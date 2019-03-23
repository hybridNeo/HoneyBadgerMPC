CORE_PEER_ADDRESS=peer0.org1.example.com:7051 peer chaincode install -p github.com/chaincode/rockpaperscissors -n $1 -v 2;
CORE_PEER_ADDRESS=peer1.org1.example.com:7051 peer chaincode install -p github.com/chaincode/rockpaperscissors -n $1 -v 2;
CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/users/Admin\@org2.example.com/msp/ CORE_PEER_LOCALMSPID=Org2MSP CORE_PEER_ADDRESS=peer0.org2.example.com:7051 peer chaincode install -o orderer.example.com:7050 -p github.com/chaincode/rockpaperscissors -n $1 -v 2;
CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/users/Admin\@org2.example.com/msp/ CORE_PEER_LOCALMSPID=Org2MSP CORE_PEER_ADDRESS=peer1.org2.example.com:7051 peer chaincode install -o orderer.example.com:7050 -p github.com/chaincode/rockpaperscissors -n $1 -v 2;


peer chaincode instantiate -n $1 -v 2 -c '{"Args":["a","10"]}' -P "OutOf (3, 'Org1MSP.member', 'Org1MSP.member', 'Org2MSP.member', 'Org2MSP.member')" -C mychannel;
