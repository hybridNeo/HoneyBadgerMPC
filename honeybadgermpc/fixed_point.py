import logging
import asyncio
import traceback
import time
from honeybadgermpc.mpc import PreProcessedElements, TaskProgramRunner
from honeybadgermpc.mixins import BeaverTriple, MixinOpName
from honeybadgermpc.elliptic_curve import Subgroup
from honeybadgermpc.field import GF, GFElement
import random

ppe = None

F = 32
KAPPA = 32
K = 64
p = modulus = Subgroup.BLS12_381
Field = GF.get(p)
USE_RANDOM_BIT_PPE = True


async def random_bit_share(ctx):
    if USE_RANDOM_BIT_PPE:
        return ctx.Share(Field(int(ppe.get_random_bit())))
    else:
        r = ppe.get_rand()
        r_square = await (r * r)
        r_sq = await r_square.open()

        if pow(r_sq, (modulus - 1) // 2) != Field(1) or r_sq == 0:
            return await random_bit_share(ctx)

        root = r_sq.sqrt()
        return (~Field(2)) * ((~root) * r + Field(1))


async def random2m(ctx, m):
    result = ctx.Share(0)
    bits = []
    for i in range(m):
        bits.append(await random_bit_share(ctx))
        result = result + Field(2) ** i * bits[-1]

    return result, bits


async def trunc_pr(ctx, x, k, m):
    """
    k: Maximum number of bits
    m: Truncation bits
    """
    assert k > m
    start_time = time.time()
    r1, _ = await random2m(ctx, m)
    r2, _ = await random2m(ctx, k + KAPPA - m)
    end_time = time.time()
    r2 = ctx.Share(r2.v * Field(2) ** m)
    start_time = time.time()
    c = await (x + Field(2 ** (k - 1)) + r1.v + r2.v).open()
    end_time = time.time()
    c2 = c.value % (2 ** m)
    d = ctx.Share((x.v - Field(c2) + r1.v) * ~(Field(2) ** m))
    return d


def to_bits(x, k):
    """
    Convert x to a k-bit representation
    Least significant bit first
    """
    res = []
    for i in range(k):
        res.append(x % 2)
        x //= 2
    return res


async def get_carry_bit(ctx, a_bits, b_bits, low_carry_bit=1):
    a_bits.reverse()
    b_bits.reverse()

    async def _bit_ltl_reduce(x):
        if len(x) == 1:
            return x[0]
        carry1, all_one1 = await _bit_ltl_reduce(x[:len(x) // 2])
        carry2, all_one2 = await _bit_ltl_reduce(x[len(x) // 2:])
        return carry1 + (await (all_one1 * carry2)), (await (all_one1 * all_one2))

    carry_bits = [(await (ai * bi)) for ai, bi in zip(a_bits, b_bits)]
    all_one_bits = [ctx.Share(ai.v + bi.v - 2 * carryi.v) for ai, bi, carryi in
                    zip(a_bits, b_bits, carry_bits)]
    carry_bits.append(ctx.Share(low_carry_bit))
    all_one_bits.append(ctx.Share(0))
    return (await _bit_ltl_reduce(list(zip(carry_bits, all_one_bits))))[0]


async def bit_ltl(ctx, a, b_bits):
    """
    a: Public
    b: List of private bit shares. Least significant digit first
    """
    print("d1")
    b_bits = [ctx.Share(Field(1) - bi.v) for bi in b_bits]
    print("d2")
    a_bits = [ctx.Share(ai) for ai in to_bits(int(a), len(b_bits))]
    print("d3")
    # a_bits_opened = [(await a_bit.open()) for a_bit in a_bits]
    print("d4")
    # print("a: ", a_bits_opened)
    print("d5")
    # b_bits_opened = [(await b_bit.open()) for b_bit in b_bits]
    # print("b: ", b_bits_opened)
    print("d6")
    carry = await get_carry_bit(ctx, a_bits, b_bits)
    print("d7")
    return ctx.Share(Field(1) - carry.v)


async def mod2m(ctx, x, k, m):
    r1, r1_bits = await random2m(ctx, m)
    r2, _ = await random2m(ctx, k + KAPPA - m)
    r2 = ctx.Share(r2.v * Field(2) ** m)
    print("here")
    c = await (x + r2 + r1 + Field(2) ** (k - 1)).open()
    print("here2")
    c2 = int(c) % (2 ** m)
    u = await bit_ltl(ctx, c2, r1_bits)
    print("here3")
    a2 = ctx.Share(Field(c2) - r1.v + (2 ** m) * u.v)
    return a2


async def trunc(ctx, x, k, m):
    a2 = await mod2m(ctx, x, k, m)
    print("A2 done")
    d = ctx.Share((x.v - a2.v) / (Field(2)) ** m)
    return d


class FixedPoint(object):
    def __init__(self, ctx, x, pp = None):
        self.ctx = ctx
        global ppe
        if pp == None:
            print("Heisenbug")
        self.ppe =pp

        if type(x) in [int, float]:
            ppe = pp
            print(ppe.get_zero())
            self.share = ctx.Share(Field(int(ppe.get_zero())) + (Field(int(x * 2 ** F))))
            print(self.share)
        elif type(x) is ctx.Share:
            ppe = pp
            self.share = x
        else:
            raise NotImplementedError

    def add(self, x):
        if type(x) is FixedPoint:
            return FixedPoint(self.ctx, self.share + x.share, pp=self.ppe)

    def sub(self, x):
        if type(x) is FixedPoint:
            return FixedPoint(self.ctx, self.share - x.share, pp=self.ppe)
        raise NotImplementedError

    async def mul(self, x):
        if type(x) is FixedPoint:
            start_time = time.time()
            res_share = await (self.share * x.share)
            end_time = time.time()
            print("Multiplication time: ", end_time - start_time)
            start_time = time.time()
            res_share = await trunc_pr(self.ctx, res_share, 2 * K, F)
            end_time = time.time()
            print("Trunc time: ", end_time - start_time)
            return FixedPoint(self.ctx, res_share, pp=self.ppe)
        raise NotImplementedError

    async def open(self):
        x = (await self.share.open()).value
        if x >= 2 ** (K - 1):
            x = -(p - x)
        return float(x) / 2 ** F

    def neg(self):
        return FixedPoint(self.ctx, Field(-1) * self.share, pp=self.ppe)

    async def ltz(self):
        t = await trunc(self.ctx, self.share, K, K - 1)
        return self.ctx.Share(-t.v)

    async def lt(self, x):
        return await self.sub(x).ltz()

    async def gt(self, x):
        return await x.sub(self).ltz()

    async def div(self, x):
        if type(x) in [float, int]:
            if (self.ppe == None ):
                print("PPE is NONE")
            return await self.mul(FixedPoint(self.ctx, 1. / x, pp=self.ppe))
        raise NotImplementedError


async def linear_regression_mpc(ctx, ppe, X, y, m_current=0, b_current=0, epochs=1,
                                learning_rate=0.01):
    N = len(X)
    m_current = FixedPoint(ctx, m_current, pp=ppe)
    b_current = FixedPoint(ctx, b_current, pp=ppe)
    learning_rate = FixedPoint(ctx, learning_rate, pp=ppe)
    for i in range(epochs):
        y_current = [((await m_current.mul(X[i]))).add(b_current) for i in range(N)]
        m_gradient = FixedPoint(ctx, 0, pp=ppe)
        for i in range(N):
            m_gradient = m_gradient.sub(await y[i].sub(y_current[i]).mul(X[i]))
        m_gradient = await m_gradient.div(N)
        print("m_gradient: ", await m_gradient.open())
        b_gradient = FixedPoint(ctx, 0, pp=ppe)
        for i in range(N):
            b_gradient = b_gradient.add(y[i].sub(y_current[i]))
        b_gradient = (await b_gradient.div(N)).neg()
        print("b_gradient: ", await b_gradient.open())
        m_current = m_current.sub(await (learning_rate.mul(m_gradient)))
        b_current = b_current.sub(await (learning_rate.mul(b_gradient)))
        print("m_current: ", await m_current.open(), "b_current: ",
              await b_current.open())
    return m_current, b_current


async def test_multiplication(ctx):
    for i in range(100):
        random.seed(i)
        print("Multiplication ", i)
        x = (random.random() - 0.5) * 100
        y = (random.random() - 0.5) * 100
        z = x * y
        print(x, y, z)
        z2 = await (await FixedPoint(ctx, x).mul(FixedPoint(ctx, y))).open()
        print(abs(z - z2))
        assert abs(z - z2) < 1e-6


async def _prog(ctx):
    x = FixedPoint(ctx, 59.0)
    y = FixedPoint(ctx, 58.6)
    start_time = time.time()
    t = await x.mul(y)
    end_time = time.time()
    print("Multiplication time: ", end_time - start_time)
    print(await t.open())
    m, b = await linear_regression_mpc(ctx,
                                    [FixedPoint(ctx, 1), FixedPoint(ctx, 2),
                                        FixedPoint(ctx, 3), FixedPoint(ctx, 4),
                                        FixedPoint(ctx, 5), FixedPoint(ctx, 6),
                                        FixedPoint(ctx, 7)],
                                    [FixedPoint(ctx, 2), FixedPoint(ctx, 3),
                                        FixedPoint(ctx, 4), FixedPoint(ctx, 5),
                                        FixedPoint(ctx, 6), FixedPoint(ctx, 7),
                                        FixedPoint(ctx, 8)],
                                    learning_rate=0.05,
                                    epochs=100)
    await test_multiplication(ctx)
    print(await m.open(), await b.open())


if __name__ == "__main__":
    n = 4
    t = 1

    ppe = PreProcessedElements()
    logging.info("Generating zeros in sharedata/")
    ppe.generate_zeros(1000, n, t)
    logging.info("Generating random shares of bits in sharedata/")
    ppe.generate_random_bits(10000, n, t)
    logging.info('Generating random shares in sharedata/')
    ppe.generate_rands(10000, n, t)
    logging.info('Generating random shares of triples in sharedata/')
    ppe.generate_triples(10000, n, t)

    # logging.info('Generating random shares of bits in sharedata/')
    # ppe.generate_bits(1000, n, t)

    start_time = time.time()
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    try:
        # programRunner = TaskProgramRunner(n, t, {
        #     MixinOpName.MultiplyShare: BeaverTriple.multiply_shares})
        program_runner = TaskProgramRunner(n, t, {
            MixinOpName.MultiplyShare: BeaverTriple.multiply_shares})
        program_runner.add(_prog)
        loop.run_until_complete(program_runner.join())
    finally:
        loop.close()

    end_time = time.time()
    print(end_time - start_time)
