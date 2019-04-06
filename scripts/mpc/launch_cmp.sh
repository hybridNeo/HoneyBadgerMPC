#!/bin/bash
# Assume hosts are as follows:
"""
 127.0.0.1   hbmpc_0
 127.0.0.1   hbmpc_1
 127.0.0.1   hbmpc_2
 127.0.0.1   hbmpc_3
"""

CMD="python -m honeybadgermpc.fabric_mpc_runner"
CONFIG_PATH=conf/ipc.network.local/hbmpc.ini
set -x
rm -rf sharedata/READY # NOTE: see preprocessing.py wait_for_preprocessing
tmux new-session     "${CMD} 0 ${CONFIG_PATH} cmp_field 3 3; sh" \; \
     splitw -h -p 50 "${CMD} 1 ${CONFIG_PATH} cmp_field 4 4; sh" \; \
     splitw -v -p 50 "${CMD} 2 ${CONFIG_PATH} cmp_field 5 5; sh" \; \
     selectp -t 0 \; \
     splitw -v -p 50 "${CMD} 3 ${CONFIG_PATH} cmp_field 6 6; sh"
