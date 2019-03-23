import os
import sys
import subprocess
import time
import json

def int_to_inp(inp):
	if inp == '10':
		return "rock"
	if inp == "11":
		return "paper"
	if inp == "12":
		return "scissors"
	return "NA"

def all_games(chaincode):
	print('################################################################################')
	print('Showing all active games')
	print('################################################################################')
	cmd_list = ['peer','chaincode', 'query','-C' ,'mychannel' , '-n' ,chaincode ,'-c','{"Args":["getActiveGames"]}']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = out.decode('utf-8')
	if out_str == 'null\n':
		return
	# print(out_str)
	json_array = json.loads(out_str)
	# print(json_array)		
	print("GAME NAME\tPlayer 1\tPlayer 2")
	for i in json_array:
		print(i['name'] + '\t\t' + i['u1']+ '\t\t' + i['u2']+ '\t\t') 



def completed_games(chaincode):
	print('################################################################################')
	print('Showing all completed games')
	print('################################################################################')
	cmd_list = ['peer','chaincode', 'query','-C' ,'mychannel' , '-n' ,chaincode ,'-c','{"Args":["getCompletedGames"]}']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = out.decode('utf-8')
	if out_str == 'null\n':
		return
	# print(out_str)
	json_array = json.loads(out_str)
	# print(json_array)		
	print("GAME NAME\tPlayer 1\tPlayer 2\tMove 1\tMove 2\tResult")
	for i in json_array:
		print(i['name'] + '\t\t' + i['u1']+ '\t\t' + i['u2']+ '\t\t' + int_to_inp(i['m1'])+ '\t' + int_to_inp(i['m2']) + '\t' + i['result'])


def get_result(game_name, chaincode):
	time.sleep(2)
	print("trying to get result")
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' , '-n' ,chaincode ,'-c','{"Args":["endGame", "' + game_name  + '","blah"]}']
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
		get_result(game_name, chaincode)
	else:
		print("################# RESULT/WINNER #################")
		print(res)	

def inp_to_int(inp):
	inp = inp.lower()
	if inp == 'rock':
		return "10"
	if inp == "paper":
		return "11"
	if inp == "scissors":
		return "12"
	return "13"

def create_game(chaincode):
	''' 
		peer chaincode invoke -n mycc2 -c '{"Args":["createGame", "test", "20", "rahul"]}' -C mychannel; 
	'''	
	print('Enter name of the game to create')
	game_name = input()
	print("Enter time limit in seconds")
	time_limit = input()
	print("Enter your username for the game")
	user_name = input()
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' , '-c','{"Args":["createGame", "' + game_name + '","'  + time_limit +  '","' + user_name + '"  ]}','-n' ,chaincode ,'--peerAddresses', 'peer0.org1.example.com:7051', '--peerAddresses', 'peer1.org1.example.com:7051', '--peerAddresses','peer0.org2.example.com:7051','--peerAddresses', 'peer1.org2.example.com:7051']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = err.decode('utf-8')
	print(out,err)
	cellname = ''
	print("###############################################################################################")
	print("Created game successfully")

	try:
		arr = out_str.split('status:200 payload:')
		cellname = arr[1]
		cellname = cellname[1:-3] # trim quotes 
	except:
		print("Failed to create game")
		return
	print("Got cellname from chaincode  " ,cellname)
	print("Enter your move. (rock/paper/scissors)")
	inp = inp_to_int(input())
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

def join_game(chaincode):
	print("Enter the name of the game to join")
	game_name = input()
	print("Enter your username for the game")
	user_name = input()
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' , '-n' ,chaincode ,'-c','{"Args":["joinGame", "' + game_name +  '","' + user_name + '"  ]}']
	task = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = task.stdout
	err = task.stderr	
	out_str = err.decode('utf-8')
	cellname = ''
	print("###############################################################################################")
	print("Created game successfully")

	try:
		arr = out_str.split('status:200 payload:')
		cellname = arr[1]
		cellname = cellname[1:-3] # trim quotes 
	except:
		print("Failed to create game")
		return
	print("Got cellname from chaincode  " ,cellname)
	print("Enter your move. (rock/paper/scissors)")
	inp = inp_to_int(input())
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
	get_result(game_name, chaincode)

def main():
	if(len(sys.argv) < 2):
		print("Enter the name of the chaincode as argument")
		sys.exit(0)

	chaincode_name = sys.argv[1]
	# get_result('test',chaincode_name)
	# sys.exit(0)
	print('###################################')
	print('# ROCK PAPER SCISSORS 		###')
	
	while(1):
		print("#############################################")
		print("1. Press 1 to View all active games ")
		print("2. Press 2 to View all completed games ")
		print("3. Press 3 to create game ")
		print("4. Press 4 to join a game ")
		print("5. Press 5 to exit ")
		inp = input()
		if inp == '1':
			all_games(chaincode_name)
		elif inp == '2':
			completed_games(chaincode_name)
		elif inp == '3':
			create_game(chaincode_name)
		elif inp == '4':
			join_game(chaincode_name)
		elif inp == '5':
			sys.exit(0)	

if __name__ == '__main__':
	main()
