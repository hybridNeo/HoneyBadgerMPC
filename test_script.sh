peer chaincode install -p github.com/chaincode/rockpaperscissors -n $1 -v 2;
peer chaincode instantiate -n $1 -v 2 -c '{"Args":["a","10"]}' -C mychannel;
