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
		open_secrets(eqexample_name, chaincode)
	else:
		print("################# Started MPC  #################")
			


def get_result(eqexample_name, chaincode):
	time.sleep(2)
	print("trying to get result")
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel', '-c','{"Args":["endeqtest", "' + eqexample_name  + '","blah"]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
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
		print(res)	


def create_eqexample(chaincode):
	print('Enter name of the MPC Instance to create')
	eqexample_name = input()
	time_limit = '10'
	print("Enter your username")
	user_name = input()
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' , '-c','{"Args":["createeqtest", "' + eqexample_name + '","'  + time_limit +  '","' + user_name + '"  ]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = err.decode('utf-8')
	cellname = ''
	print("###############################################################################################")
	print("Created eqexample successfully")

	try:
		arr = out_str.split('status:200 payload:')
		cellname = arr[1]
		cellname = cellname[1:-3] # trim quotes 
	except:
		print("Failed to create eqexample")
		return
	print("Got cellname from chaincode  " ,cellname)
	print("Enter your input.")
	inp = (input())
	local_cmd = ['python3.7', '-m', 'honeybadgermpc.fabric_share_secret' , inp ,cellname, 'rps']
	print("Dealing Shares to endorsers.....")
	print(local_cmd)
	task = subprocess.run(local_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	# print(task.stderr)
	# print(task.stdout)
	print("#######################################")
	print("Successfully shared secret")
	print("Now wait for the other player to make a move")
	# print(inp)

def join_eqexample(chaincode):
	print("Enter the name of the Instance")
	eqexample_name = input()
	print("Enter your username")
	user_name = input()
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' ,'-c','{"Args":["joineqtest", "' + eqexample_name +  '","' + user_name + '"  ]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
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
	print("Enter your input")
	inp = (input())
	local_cmd = ['python3.7', '-m', 'honeybadgermpc.fabric_share_secret' , inp ,cellname, 'rps']
	print("Dealing Shares to endorsers.....")
	print(local_cmd)
	task = subprocess.run(local_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	# print(task.stderr)
	# print(task.stdout)
	print("#######################################")
	print("Successfully shared secret")
	print("Now wait for the timeout to view the result")
	# print(inp)
	time.sleep(6)
	mpc(eqexample_name, chaincode)
	time.sleep(15)
	get_result(eqexample_name, chaincode)

def main():
	if(len(sys.argv) < 2):
		print("Enter the name of the chaincode as argument")
		sys.exit(0)

	chaincode_name = sys.argv[1]
	# get_result('test',chaincode_name)
	# sys.exit(0)
	print('###################################')
	print('# MPC Example 		###')
	
	while(1):
		print("#############################################")
		print("1. Press 1 to View all active MPC sessions ")
		print("2. Press 2 to View all completed MPC session ")
		print("3. Press 3 to create an MPC session ")
		print("4. Press 4 to enter input to an MPC session ")
		print("5. Press 5 to exit ")
		inp = input()
		if inp == '1':
			all_eqexamples(chaincode_name)
		elif inp == '2':
			completed_eqexamples(chaincode_name)
		elif inp == '3':
			create_eqexample(chaincode_name)
		elif inp == '4':
			join_eqexample(chaincode_name)
		elif inp == '5':
			sys.exit(0)	

if __name__ == '__main__':
	main()
