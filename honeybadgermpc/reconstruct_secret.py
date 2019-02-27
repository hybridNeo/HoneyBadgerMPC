import subprocess
import os
from honeybadgermpc.robust_reconstruction import attempt_reconstruct
from honeybadgermpc.field import GF
from honeybadgermpc.polynomial import EvalPoint

def get_shares(peers):
	env = os.environ.copy()
	
	
	cmd = '{"Args":["getKey", "0"  ]}' 
	
	shares = []
	for i in peers:
		env['CORE_PEER_ADDRESS'] = i
		res = subprocess.check_output(['peer','chaincode', 'query','-C' ,'mychannel' ,'-o' ,'orderer.example.com:7050', '-n' ,'honeybadgerscc' ,'-c', cmd ], env=env)
		res= res[:-1]
		shares.append(int(res))

	return shares






peers = ['peer0.org1.example.com:7051','peer1.org1.example.com:7051'
,'peer0.org2.example.com:7051','peer1.org2.example.com:7051']




def main():
	print('Getting shares from peers -----------------------')
	shares = get_shares(peers)
	print(shares)
	BLS12_381 = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
	field = GF.get(BLS12_381)
	fs = []
	for i in shares:
		fs.append(field(i))

	print(fs)

	point = EvalPoint(field, 4)
	print(attempt_reconstruct(fs,field,4,1,point))


main()
