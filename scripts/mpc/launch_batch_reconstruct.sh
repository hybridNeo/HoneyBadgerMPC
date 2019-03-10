#!/bin/bash

CMD="python -m honeybadgermpc.public_reconstruct"
CONFIG_PATH=conf/hbavss.local.ini

# Generate config file locally
set -x
tmux new-session     "${CMD} 0 ${CONFIG_PATH} 3; sh" \; \
     splitw -h -p 50 "${CMD} 1 ${CONFIG_PATH} 4; sh" \; \
     splitw -v -p 50 "${CMD} 2 ${CONFIG_PATH} 5; sh" \; \
     selectp -t 0 \; \
     splitw -v -p 50 "${CMD} 3 ${CONFIG_PATH} 6; sh" \; \
