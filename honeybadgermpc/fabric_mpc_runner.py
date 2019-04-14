import asyncio
import sys
from .public_reconstruct import _prog
from honeybadgermpc.ipc import ProcessProgramRunner
from honeybadgermpc.config import load_config
from honeybadgermpc.ipc import NodeDetails
from honeybadgermpc.exceptions import ConfigurationError
from honeybadgermpc.mpc import *
import logging
from honeybadgermpc.field import GF
from gmpy2 import num_digits
from honeybadgermpc.mixins import BeaverTriple, MixinOpName
from math import sqrt
from honeybadgermpc.fixed_point import FixedPoint, ppe, linear_regression_mpc

async def cmp(context, **kwargs):
    pp_elements = kwargs['ppe']
    # print("here")
    a = context.Share((int(pp_elements.get_zero())))  + context.Share(2)
    b = context.Share((int(pp_elements.get_zero())))  + context.Share(23)

    r = pp_elements.get_rand()
    print(r)
    result = await comparison(context, a, b, pp_elements)

    if result:
        print("Comparison result: a > b")
    else:
        print("Comparison result: a <= b")


async def comparison(context, a_share, b_share, pp_elements):
    """MULTIPARTY COMPARISON - An Improved Multiparty Protocol for
    Comparison of Secret-shared Values by Tord Ingolf Reistad (2007)
    This method `greater_than_equal` method which can compare
    Zp field elements and gives a secret result shared over Zp.
    greater_than_equal` method which can compare Zp field
    """

    modulus = Subgroup.BLS12_381
    Field = GF.get(modulus)
    l = num_digits(modulus, 2)
    k = security_parameter = 32

    async def get_random_bit():
        r = context.Share(int(pp_elements.get_rand()))
        r_square = await (r*r)
        r_sq = await r_square.open()

        if pow(r_sq, (modulus-1)//2) != Field(1) or r_sq ==0:
            return await get_random_bit()

            root = r_sq.sqrt()
            return (~Field(2)) * ((~root)*r + Field(1))

    # assert 2 * a_share + 1 < modulus, "[a] < (p-1)/2 must hold"
    # assert 2 * b_share + 1 < modulus, "[b] < (p-1)/2 must hold"

    # ############# PART 1 ###############
    # First Transformation
    r_bits = [context.Share(int(pp_elements.get_bit())) for _ in range(l)]
    r_B = Field(0)
    for i, b in enumerate(r_bits):
        r_B = r_B + (2**i) * b

    z = a_share - b_share
    c = await (2 * z + r_B).open()
    c_bits = [Field(int(x)) for x in list('{0:0255b}'.format(c.value))]
    c_bits.reverse()

    r_0 = r_bits[0]         # [r0]
    c0 = c_bits[0]

    # ############# PART 2 ###############
    # Compute X
    X = Field(0)
    for i in range(l-1):
        cr = Field(0)
        for j in range(i+1, l):
            print(i, j)
            # print(i, j, "r_bits[j] ", await r_bits[j].open(), "c_bits[j] ", c_bits[j])
            c_xor_r = r_bits[j] + c_bits[j] - Field(2)*c_bits[j]*r_bits[j]
            # print("c_xor_r: ", await c_xor_r.open())
            cr = cr + c_xor_r
        cr_open = await cr.open()
        # print("cr: ", cr_open)
        pp = pow(2, int(cr_open))
        # print("pp: ", pp)
        X = X + (Field(1) - c_bits[i]) * pp * r_bits[i]

    # ############# PART 3 ###############
    # Extracting LSB
    # TODO
    # assert X.v.value < sqrt(4 * modulus)

    s_bits = [context.Share(int(pp_elements.get_bit())) for _ in range(l)]

    s_0 = s_bits[0]
    s1 = s_bits[-1]         # [s_{l-1}]
    s2 = s_bits[-2]         # [s_{l-2}]
    s1s2 = await (s1*s2)

    s_B = Field(0)
    for i, b in enumerate(s_bits):
        s_B = s_B + (2**i) * b

    D = s_B + X
    d = await D.open()
    d0 = int(d) & 1

    # TODO
    # assert d > sqrt(4 * modulus)

    dxor1 = d0 ^ (d.value < 2**(l-1))       # d0 ^ (d < 2**{l-1})
    dxor2 = d0 ^ (d.value < 2**(l-2))        # d0 ^ (d < 2**{l-1})
    dxor12 = d0 ^ (d.value < (2**(l-1) + 2**(l-2)))                 # d0 ^ (d < (2**{l-2} + 2**{l-1}))

    #[d_0]
    d_0 = d0 * (Field(1) + s1s2 - s1 - s2) \
        + dxor2 * (s2 - s1s2) \
        + dxor1 * (s1 - s1s2) \
        + dxor12 * s1s2

    x_0 = s_0 + d_0 - 2 * (await (s_0 * d_0))       # [x0] = [s0] ^ [d0], equal to [r]B > c
    c0_xor_r0 = c0 + r_0 - 2*c0*r_0 #c0 ^ r_0
    return  c0_xor_r0 + x_0- 2*(await (c0_xor_r0*x_0)) #c0 ^ r_0 ^ x_0



class PreProcessedLight:
    def __init__(self, zeros, randoms, bits):
        self.num_randoms = 0
        self.num_bits = 0
        self.num_rand_bits = 0
        if len(zeros) > 4:
            self.zeros = zeros[4:]
        if len(randoms) > 4:
            self.randoms = randoms[4:]
        if len(bits) > 4:
            self.bits = bits[4:]

    def get_zero(self):
        if len(self.zeros) == 0:
            print("OUT of zeroes")
        else:
            z = self.zeros[-1]
            if len(self.bits) > 1:
                self.zeros.pop()
            return z

    def get_bit(self):
        self.num_bits += 1
        if len(self.bits) == 0:
            print("OUT of bits")
        else:
            b = self.bits[-1]
            if len(self.bits) > 1:
                self.bits.pop()
            return b

    def get_random_bit(self):
        self.num_rand_bits += 1
        if len(self.bits) == 0:
            print("OUT of bits")
        else:
            b = self.bits[-1]
            if len(self.bits) > 1:
                self.bits.pop()
            #self.bits = self.bits[1:]
            return b

    def get_rand(self):
        self.num_randoms += 1
        if len(self.randoms) == 0:
            print("Out of randoms")
        else:
            r = self.randoms[-1]
            if len(self.bits) > 1:
                self.randoms.pop()
            return r

    def print_stats(self):
        print(f'Number of bits used {self.num_bits}')
        print(f'Number of random bits used {self.num_rand_bits}')
        print(f'Number of randoms used {self.num_randoms}')

# TODO replace with active preprocessing engine
def get_preprocessing(N, t, node_id):
    zeros_file_name = f"sharedata/zeros_{N}_{t}-{node_id}.share"
    rand_file_name = f"sharedata/rands_{N}_{t}-{node_id}.share"
    bits_file_name = f"sharedata/random_bit_{N}_{t}-{node_id}.share"
    # print(zeros_file_name)
    zeros = []
    randoms = []
    bits = []
    with open(zeros_file_name, "r") as f:
        zeros = f.readlines()

    zeros = [x.strip() for x in zeros]
    with open(rand_file_name, "r") as f:
        randoms = f.readlines()
    randoms = [x.strip() for x in randoms]

    with open(bits_file_name, "r") as f:
        bits = f.readlines()
    bits = [x.strip() for x in bits]


    # hack to increase the size of zeroes, randoms and bits
    zeros *= 100
    randoms *= 100
    bits *= 100
    pp_elements = PreProcessedLight(zeros=zeros,randoms=randoms, bits=bits)
    return pp_elements


async def equality(context, p_share, q_share, pp_elements):


    def legendre_mod_p(a):
        """Return the legendre symbol ``legendre(a, p)`` where *p* is the
        order of the field of *a*.
        """
        assert a.modulus % 2 == 1
        b = (a ** ((a.modulus - 1)//2))
        if b == 1:
            return 1
        elif b == a.modulus-1:
            return -1
        return 0

    diff_a = p_share - q_share
    k = security_parameter = 32
    Field = GF.get(Subgroup.BLS12_381)

    async def _gen_test_bit():

        # b \in {0, 1}
        # _b \in {5, 1}, for p = 1 mod 8, s.t. (5/p) = -1
        # so _b = -4 * b + 5
        _b = (-4) * context.Share(int(pp_elements.get_bit())) + context.Share(5)
        _r = context.Share(int(pp_elements.get_rand()))
        _rp = context.Share(int(pp_elements.get_rand()))

        # c = a * r + b * rp * rp
        # If b_i == 1 c_i will always be a square modulo p if a is
        # zero and with probability 1/2 otherwise (except if rp == 0).
        # If b_i == -1 it will be non-square.
        _c = await (diff_a * _r) + await (_b * (await (_rp*_rp)))
        c = await _c.open()

        return c, _b

    async def gen_test_bit():
        cj, bj = await _gen_test_bit()
        while cj == 0:
            cj, bj = await _gen_test_bit()
        # bj.open() \in {5, 1}

        legendre = legendre_mod_p(cj)

        if legendre == 1:
            xj = (1 / Field(2)) * (bj + context.Share(1))
        elif legendre == -1:
            xj = (-1) * (1 / Field(2)) * (bj - context.Share(1))
        else:
            gen_test_bit()

        return xj

    x = [await gen_test_bit() for _ in range(k)]

    # Take the product (this is here the same as the "and") of all
    # the x'es
    while len(x) > 1:
        x.append(await (x.pop(0) * x.pop(0)))

    return await x[0].open()

async def equality_wrapper(context, **kwargs):
    pp_elements = kwargs['ppe']
    p = (context.Share(int(kwargs['shares'][0])))
    q = context.Share(int(kwargs['shares'][1]))

    print(p,q)
    # result, count_comm = await equality(context, p, q)
    result = await equality(context, p, q, pp_elements)
    # result = 0
    if result == 0:
        print("The two numbers are different! (with high probability)")
    else:
        print("The two numbers are equal!")

    # print("The number of communication count_complexity is: ", count_comm)


async def auction(context, **kwargs):
    import time
    pp_elements = kwargs['ppe']
    global ppe
    ppe = pp_elements
    time1 = time.time()
    bids = [ FixedPoint(context, context.Share(int(i)), pp=pp_elements) for i in kwargs['shares'] ]
    winning_bid = await auction_mpc(context, pp_elements, bids)
    winning_bid_r = await winning_bid.open()
    print("<RESULT>"  + str(winning_bid_r) +  "</RESULT>")

async def linear_regression_wrapper(context, **kwargs):
    import time
    pp_elements = kwargs['ppe']
    global ppe
    ppe = pp_elements
    x = FixedPoint(context, 59.0, pp=pp_elements)
    y = FixedPoint(context, 58.6, pp=pp_elements)
    t = await x.mul(y)
    print(t)
    print(await t.open())
    ctx= context
    time1 = time.time()
    learning_rate = kwargs['learning_rate']
    epochs = kwargs['epochs']
    X_l = int(len(kwargs['shares'])/2)
    X_s = kwargs['shares'][0:X_l]
    Y_s = kwargs['shares'][X_l:]
    X = [ FixedPoint(ctx, context.Share(int(i)), pp=pp_elements) for i in X_s ]
    Y = [ FixedPoint(ctx, context.Share(int(i)), pp=pp_elements) for i in Y_s ]
    m, b = await linear_regression_mpc(context, pp_elements,
                                    X,
				    Y,
				    learning_rate=learning_rate,
                                    epochs=epochs)
    # await test_multiplication(ctx)
    m_r = await m.open()
    b_r = await b.open()
    print(f'<RESULT>{m_r};{b_r}</RESULT>')
    print(f'The time taken is { time.time() - time1}')


async def auction_mpc(context, pp_elements, bids):
    max_bid = bids[0]

    for i in range(1, len(bids)):
        t = await max_bid.lt(bids[i])
        v = (await (t.open())).value
        if v == 1:
            max_bid = bids[i]

    return max_bid



async def cmp_f_wrapper(context, **kwargs):
    import time
    print("In the wrapper")
    pp_elements = kwargs['ppe']
    global ppe
    ppe = pp_elements
    print(kwargs['shares'])
    x = FixedPoint(context, context.Share(int(kwargs['shares'][0])), pp=pp_elements)
    y = FixedPoint(context, context.Share(int(kwargs['shares'][1])), pp=pp_elements)
    t = await x.lt(y)
    print(await (t.open()))

async def run_mpc_loader(app_name, config, n, t, id, shares):
    program_runner = ProcessProgramRunner(config, n, t, id,
            {MixinOpName.MultiplyShare:BeaverTriple.multiply_shares})
    await program_runner.start()
    import time
    begin_time = time.time()
    # logic to load the appropriate program
    if app_name == 'cmp':
        pp_elements = get_preprocessing(N, t, id)
        program_runner.add(0, cmp, node_id=id, ppe=pp_elements)
        await program_runner.join()
        await program_runner.close()
        pp_elements.print_stats()
    elif app_name == 'equals':
        pp_elements = get_preprocessing(N, t, id)
        # print(shares)
        program_runner.add(0, equality_wrapper, ppe=pp_elements, shares=shares)
        await program_runner.join()
        await program_runner.close()
        pp_elements.print_stats()
    elif app_name == 'cmp_field':
        print(f'CMP FIELD {id}')
        pp_elements = get_preprocessing(N, t, id)
        program_runner.add(0, cmp_f_wrapper, ppe=pp_elements, shares=shares)
        await program_runner.join()
        await program_runner.close()
        pp_elements.print_stats()
    elif app_name == 'linear_regression_mpc':
        pp_elements = get_preprocessing(N, t, id)

        program_runner.add(0, linear_regression_wrapper, ppe=pp_elements, shares=shares,
                learning_rate=0.05, epochs=100)
        await program_runner.join()
        await program_runner.close()
        pp_elements.print_stats()
    elif app_name == 'auction':
        pp_elements = get_preprocessing(N, t, id)
        program_runner.add(0, auction, ppe=pp_elements, shares=shares)
        await program_runner.join()
        await program_runner.close()
        pp_elements.print_stats()
    print(f'Time taken for MPC operation is {time.time() - begin_time}')

'''
    arg1  nodeid
    arg2  configfile
    arg3  app name
    args4 to argsn shares

'''
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Wrong number of arguments")
        sys.exit(1)

    nodeid = sys.argv[1]
    configfile = sys.argv[2]
    app_name = sys.argv[3]
    shares = sys.argv[4:]

    config_dict = load_config(configfile)
    N = config_dict['N']
    t = config_dict['t']
    nodeid = int(nodeid)
    network_info = {
        int(peerid): NodeDetails(addrinfo.split(':')[0], int(addrinfo.split(':')[1]))
        for peerid, addrinfo in config_dict['peers'].items()
    }

    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try:
        loop.run_until_complete(run_mpc_loader(app_name, network_info, N, t, nodeid, shares))
    finally:
        loop.close()



