import subprocess
import os
import sys



def run_cmd_remote(cmds, peers, other_tasks=None):
	env = os.environ.copy()
	tasks = []
	for i in other_tasks:
		tasks.append(i)

	for i in range(len(peers)):
		env['CORE_PEER_ADDRESS'] = peers[i]
		task = subprocess.Popen(cmds[i], env=env)
		tasks.append(task)

	for i in tasks:
		i.wait()


def run_cmd_local(cmd):
	task = subprocess.Popen(cmd)
	return task	

def share_secret(peers, key, value, namespace):
	cmds = []
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' ,'-o' ,'orderer.example.com:7050', '-n' ,'honeybadgerscc' ,'-c']
	for i in range(len(peers)):
		cmd = '{"Args":["hbmpc", "' + str(i) + '","'  + key +  '"," ' + namespace +'"  ]}'
		cmd_l_i = cmd_list.copy()
		cmd_l_i.append(cmd)
		cmds.append(cmd_l_i)
	print(cmds)
	local_cmd = ['python3.7', '-m', 'honeybadgermpc.secretshare_hbavsslight' , str(len(peers)) ,'/usr/src/HoneyBadgerMPC/conf/hbavss.hyper.ini', value]
	print(local_cmd)
	local_tid = run_cmd_local(local_cmd)
	run_cmd_remote(cmds, peers, [local_tid])

def main():
	if(len(sys.argv) < 4):
		print("Enter key, value and namespace")
		os.exit(1)

	value = sys.argv[1]
	key = sys.argv[2]
	namespace = sys.argv[3]
	peers = ['peer0.org1.example.com:7051','peer1.org1.example.com:7051' ,'peer0.org2.example.com:7051','peer1.org2.example.com:7051']
	share_secret(peers, key, value, namespace)

if __name__ == '__main__':
	main()
