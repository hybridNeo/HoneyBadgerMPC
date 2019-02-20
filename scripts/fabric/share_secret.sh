#!/bin/bash

CMD_PRE_STMT="CORE_PEER_ADDRESS=peer1.org1.example.com:7051"
CMD_STMT="peer chaincode query -C mychannel -n honeybadgerscc -c '{\"Args\":[\"hbmpc\",\"a\"]}'"
LOCAL_CMD="python3.7 -m honeybadgermpc.secretshare_hbavsslight 4 conf/hbavss.hyper.ini"
CONFIG_PATH=conf/hbavss.local.ini

# Generate config file locally
set -x
tmux new-session     "${LOCAL_CMD}; sh" \; \
    splitw -h -p 50 "CORE_PEER_ADDRESS=peer0.org1.example.com:7051 ${CMD_STMT}; sh" \; \
     splitw -v -p 50 "CORE_PEER_ADDRESS=peer1.org1.example.com:7051 ${CMD_STMT}; sh" \; \
     selectp -t 0 \; \
     splitw -v -p 50 "CORE_PEER_ADDRESS=peer0.org2.example.com:7051 ${CMD_STMT}; sh" \; \
     splitw -v -p 50 "CORE_PEER_ADDRESS=peer1.org2.example.com:7051 ${CMD_STMT}; sh"
