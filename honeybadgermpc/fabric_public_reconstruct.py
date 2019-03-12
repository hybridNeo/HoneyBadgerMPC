import subprocess
import os
import sys



def run_cmd_remote(cmds, peers, other_tasks=[]):
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

def share_secret(peers, key, namespace):
	cmds = []
	cmd_list = ['peer','chaincode', 'query','-C' ,'mychannel' ,'-o' ,'orderer.example.com:7050', '-n' ,'honeybadgerscc' ,'-c']
	for i in range(len(peers)):
		cmd = '{"Args":["pubRecon", "' + str(i) + '","'  + key +  '"," ' + namespace +'"  ]}'
		cmd_l_i = cmd_list.copy()
		cmd_l_i.append(cmd)
		cmds.append(cmd_l_i)
	print(cmds)
	run_cmd_remote(cmds, peers)

def main():
	if(len(sys.argv) < 3):
		print("Enter key and namespace")
		os.exit(1)

	key = sys.argv[1]
	namespace = sys.argv[2]
	peers = ['peer0.org1.example.com:7051','peer1.org1.example.com:7051' ,'peer0.org2.example.com:7051','peer1.org2.example.com:7051']
	share_secret(peers, key, namespace)

if __name__ == '__main__':
	main()
