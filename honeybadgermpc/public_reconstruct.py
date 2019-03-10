import sys
from .config import load_config
from .ipc import NodeDetails, ProcessProgramRunner
import os
import asyncio


async def _prog(context, **kwargs):
    share = kwargs["share"]
    s = context.Share((share))
    print("Share: ", s)
    a = await (s.open())
    print('Reconstructed Value:',int(a))


async def run_batch_reconstruct(config, n, t, id, share):
    print("In batch reconstruct ")
    program_runner = ProcessProgramRunner(config, n, t, id)
    await program_runner.start()
    program_runner.add(0, _prog, share=share)
    await asyncio.sleep(1)
    await program_runner.close()

if __name__ == "__main__":
    configfile = os.environ.get('HBMPC_CONFIG')
    nodeid = os.environ.get('HBMPC_NODE_ID')
    share = 42 # if value to be shared in not passed via arguments.
    # override configfile if passed to command
    try:
        nodeid = sys.argv[1]
        configfile = sys.argv[2]
        share = int(sys.argv[3])
    except IndexError:
        pass

    if not nodeid:
        raise ConfigurationError('Environment variable `HBMPC_NODE_ID` must be set'
                                 ' or a node id must be given as first argument.')

    if not configfile:
        raise ConfigurationError('Environment variable `HBMPC_CONFIG` must be set'
                                 ' or a config file must be given as first argument.')

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
        loop.run_until_complete(run_batch_reconstruct(network_info, N, t, nodeid, share))
    finally:
        loop.close()

