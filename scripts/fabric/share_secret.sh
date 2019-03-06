#!/bin/bash

CMD_PRE_STMT="CORE_PEER_ADDRESS=peer1.org1.example.com:7051"
CMD_STMT="peer chaincode invoke -C mychannel -o orderer.example.com:7050 -n honeybadgerscc -c '{\"Args\":[\"hbmpc\","
END_STMT=" ,\"$2\", \"$3\"]}'"
LOCAL_CMD="python3.7 -m honeybadgermpc.secretshare_hbavsslight 4 conf/hbavss.hyper.ini $1"
CONFIG_PATH=conf/hbavss.local.ini

# Generate config file locally
set -x
tmux new-session     "${LOCAL_CMD}; sh" \; \
    splitw -h -p 50 "CORE_PEER_ADDRESS=peer0.org1.example.com:7051 ${CMD_STMT}  "\"0\""  ${END_STMT}; sh" \; \
     splitw -v -p 50 "CORE_PEER_ADDRESS=peer1.org1.example.com:7051 ${CMD_STMT}  "\"1\"" ${END_STMT}; sh" \; \
     selectp -t 0 \; \
     splitw -v -p 50 "CORE_PEER_ADDRESS=peer0.org2.example.com:7051 ${CMD_STMT} "\"2\"" ${END_STMT}  ; sh" \; \
     splitw -v -p 50 "CORE_PEER_ADDRESS=peer1.org2.example.com:7051 ${CMD_STMT}  "\"3\"" ${END_STMT}; sh"
