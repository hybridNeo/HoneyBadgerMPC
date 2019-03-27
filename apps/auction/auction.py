from honeybadgermpc.mpc import *
import logging
import asyncio
from honeybadgermpc.field import GF
from gmpy2 import num_digits
from honeybadgermpc.mixins import BeaverTriple, MixinOpName
from math import sqrt

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


import os
import asyncio
from honeybadgermpc.mpc import *


async def cmp_helper(network_info, N, t, node_id):
    from honeybadgermpc.ipc import ProcessProgramRunner
    print("I am here")
    program_runner = ProcessProgramRunner(network_info, N, t, node_id, {MixinOpName.MultiplyShare:BeaverTriple.multiply_shares})
    await program_runner.start()

    zeros_file_name = f"sharedata/zeros_{N}_{t}-{node_id}.share"
    rand_file_name = f"sharedata/rands_{N}_{t}-{node_id}.share"
    bits_file_name = f"sharedata/bits_{N}_{t}-{node_id}.share"
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

    pp_elements = PreProcessedLight(zeros=zeros,randoms=randoms, bits=bits)
    # print(zeros[0:10])
    print(pp_elements.get_rand())
    program_runner.add(0, cmp, node_id=node_id, ppe=pp_elements)
    # pp_elements = PreProcessedElements()
    # a = pp_elements.get_zero(context) + context.Share(233)
    # print(a)
    await asyncio.sleep(10)
    await program_runner.close()



class PreProcessedLight:
    def __init__(self, zeros, randoms, bits):
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
            z = self.zeros[0]
            self.zeros = self.zeros[1:]
            return z

    def get_bit(self):
        if len(self.bits) == 0:
            print("OUT of bits")
        else:
            b = self.bits[0]
            self.bits = self.bits[1:]
            return b

    def get_rand(self):
        if len(self.randoms) == 0:
            print("Out of randoms")
        else:
            r = self.randoms[0]
            self.randoms = self.randoms[1:]
            return r

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


if __name__ == '__main__':
    import sys
    from honeybadgermpc.config import load_config
    from honeybadgermpc.ipc import NodeDetails
    from honeybadgermpc.exceptions import ConfigurationError

    configfile = os.environ.get('HBMPC_CONFIG')
    node_id = os.environ.get('HBMPC_NODE_ID')
    runid = os.environ.get('HBMPC_RUN_ID')

    # override configfile if passed to command
    try:
        node_id = sys.argv[1]
        configfile = sys.argv[2]
        runid = sys.argv[3]
    except IndexError:
        pass

    if not node_id:
        raise ConfigurationError('Environment variable `HBMPC_NODE_ID` must be set'
                                 ' or a node id must be given as first argument.')

    if not configfile:
        raise ConfigurationError('Environment variable `HBMPC_CONFIG` must be set'
                                 ' or a config file must be given as second argument.')

    if not runid:
        raise ConfigurationError('Environment variable `HBMPC_RUN_ID` must be set'
                                 ' or a config file must be given as third argument.')

    config_dict = load_config(configfile)
    node_id = int(node_id)
    N = config_dict['N']
    t = config_dict['t']
    k = config_dict['k']
    network_info = {
        int(peerid): NodeDetails(addrinfo.split(':')[0], int(addrinfo.split(':')[1]))
        for peerid, addrinfo in config_dict['peers'].items()
    }

    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    if node_id == 0 and 1 == 2:
        pp_elements = PreProcessedElements()
        pp_elements.generate_zeros(1000, N, t)
        pp_elements.generate_rands(1000, N, t)
        pp_elements.generate_triples(1000, N, t)
        pp_elements.generate_bits(1000, N, t)
        print("Generated pre processing")

    # sys.exit()
    loop.run_until_complete(
        cmp_helper(network_info,
            N,
            t,
            node_id
        )
    )

    loop.close()
