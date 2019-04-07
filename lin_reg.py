import os
import sys
import subprocess
import time
import json


def all_eqexamples(chaincode):
	print('################################################################################')
	print('Showing all active eqexamples')
	print('################################################################################')
	cmd_list = ['peer','chaincode', 'query','-C' ,'mychannel' , '-n' ,chaincode ,'-c','{"Args":["getActiveeqtests"]}']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = out.decode('utf-8')
	if out_str == 'null\n':
		return
	# print(out_str)
	json_array = json.loads(out_str)
	# print(json_array)		
	print("Instance NAME\tUser 1\tUser 2")
	for i in json_array:
		print(i['name'] + '\t\t' + i['u1']+ '\t\t' + i['u2']+ '\t\t') 



def completed_eqexamples(chaincode):
	print('################################################################################')
	print('Showing all completed Insrances')
	print('################################################################################')
	cmd_list = ['peer','chaincode', 'query','-C' ,'mychannel' , '-n' ,chaincode ,'-c','{"Args":["getCompletedeqtests"]}']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = out.decode('utf-8')
	if out_str == 'null\n':
		return
	# print(out_str)
	json_array = json.loads(out_str)
	# print(json_array)		
	print("Instance NAME\tUser 1\tUser2")
	for i in json_array:
		print(i['name'] + '\t\t' + i['u1']+ '\t\t' + i['u2']+ '\n Result:' + i['result'])


def mpc(eqexample_name, chaincode):
	time.sleep(2)
	print("trying to get result")
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel', '-c','{"Args":["runMPC", "' + eqexample_name  + '","blah"]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = err.decode('utf-8')
	# print(out_str)
	res = 'None'
	try:
		arr = out_str.split('status:200 payload:')
		res = arr[1]
		res = res[1:-3] # trim quotes 
	except:
		print("Failed to get result")
		
	if res == 'None':
		print("failed to start MPC")
		# open_secrets(eqexample_name, chaincode)
	else:
		print("################# Started MPC  #################")
			


def get_result(eqexample_name, chaincode):
	time.sleep(2)
	print("trying to get result")
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel', '-c','{"Args":["endLinReg", "' + eqexample_name  + '","blah"]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = err.decode('utf-8')
	# print(out_str)
	res = 'None'
	try:
		arr = out_str.split('status:200 payload:')
		res = arr[1]
		res = res[1:-3] # trim quotes 
	except:
		print("Failed to get result")
		
	if res == 'None':
		get_result(eqexample_name, chaincode)
	else:
		print("################# MPC RESULT #################")
		try:
			a = res.split("<RESULT>")
			b = a[1].split("</RESULT>")
			print(b[0])
		except:
			print(res)	


def create_eqexample(chaincode, num_vals):
	eqexample_name = 'test'
	time_limit = num_vals
	user_name = 'user1'
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' , '-c','{"Args":["createInstance", "' + eqexample_name + '","'  + num_vals +  '","' + user_name + '"  ]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = err.decode('utf-8')
	cellname = ''
	print("###############################################################################################")
	print("Created eqexample successfully")

	print(out_str)


def join_eqexample(chaincode, x, y):
	eqexample_name = 'test'
	user_name = 'user2'
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' ,'-c','{"Args":["addData", "' + eqexample_name +  '","' + user_name + '"  ]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = err.decode('utf-8')
	cellname = ''

	try:
		arr = out_str.split('status:200 payload:')
		cellname = arr[1]
		cellname = cellname[1:-3] # trim quotes 
	except:
		print("Failed to join Instance")
		return
	print("Got cellname from chaincode  " ,cellname)
	cellnames = cellname.split(';')
	cellname_x = cellnames[0]
	cellname_y = cellnames[1]
	time.sleep(2)
	local_cmd = ['python3.7', '-m', 'honeybadgermpc.fabric_share_secret' , str(x) ,cellname_x, 'rps']
	print("Dealing Shares to endorsers.....")
	print(local_cmd)
	task = subprocess.run(local_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#print(task.stderr)
	#print(task.stdout)
	time.sleep(0)
	local_cmd = ['python3.7', '-m', 'honeybadgermpc.fabric_share_secret' , str(y) ,cellname_y, 'rps']
	print("Dealing Shares to endorsers.....")
	print(local_cmd)
	task = subprocess.run(local_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print("#######################################")
	print("Successfully shared secret")
	# print(inp)
	# time.sleep(6)
	# mpc(eqexample_name, chaincode)
	# time.sleep(15)
	# get_result(eqexample_name, chaincode)

def main():
	if(len(sys.argv) < 3):
		print("Enter the name of the chaincode as argument")
		sys.exit(0)

	chaincode_name = sys.argv[1]
	print('Linear Regression tester')
	if sys.argv[2] != 'skip':
		print('CREATING MPC INSTANCE')
		create_eqexample(chaincode_name, '7')
		time.sleep(2)
		print('AVSSing the inputs')
		Xs = [1,2,3,4,5,6,7,8]
		Ys = [2,3,4,5,6,7,8,9]
		for i in range(7):
			join_eqexample(chaincode_name, Xs[i], Ys[i])
			time.sleep(2)
	
	mpc('test',chaincode_name)
	get_result('test', chaincode_name)
	
if __name__ == '__main__':
	main()
