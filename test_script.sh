peer chaincode install -p github.com/chaincode/rockpaperscissors -n mycc2 -v 2;
peer chaincode instantiate -n mycc2 -v 2 -c '{"Args":["a","10"]}' -C mychannel;
peer chaincode invoke -n mycc2 -c '{"Args":["createGame", "test", "20", "rahul"]}' -C mychannel;
peer chaincode invoke -n mycc2 -c '{"Args":["joinGame", "test",  "jack"]}' -C mychannel;
python3.7 -m honeybadgermpc.fabric_share_secret 10 rpsrahulcell rps;
python3.7 -m honeybadgermpc.fabric_share_secret 11 rpsjackcell rps;
peer chaincode invoke -n mycc2 -c '{"Args":["endGame", "test",  "rps"]}' -C mychannel
