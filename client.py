import os
import sys
import subprocess

def all_games(chaincode):
	print('Showing all active games')


def completed_games(chaincode):
	print('Showing all completed games')



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
	cmd_list = ['peer','chaincode', 'invoke','-C' ,'mychannel' , '-n' ,chaincode ,'-c','{"Args":["createGame", "' + game_name + '","'  + time_limit +  '","' + user_name + '"  ]}']
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


def main():
	if(len(sys.argv) < 2):
		print("Enter the name of the chaincode as argument")
		sys.exit(0)

	chaincode_name = sys.argv[1]
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
