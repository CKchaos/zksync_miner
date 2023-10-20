from web3 import Web3
import random
import time
from datetime import datetime
from pytz import timezone

from logger import logging
from config import *
import utils
from decrypt import get_decrypted_acc_info
from dapp.txbridge import txBridge

if __name__ == "__main__":
    params = utils.load_json('./params/auto_bridge_and_wash.json')

    task_account = params['task_account']
    pending_time = params['pending_time']

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    w3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC))
    for a in account_info:
        if a['label'] == task_account:
            acc = w3.eth.account.from_key(a['private_key'])
            break

    bridge_operator = txBridge(acc)

    logging.info(f'Execute bridge ETH to zkSync for account **< {task_account} >**')
    print(f'Pending for {pending_time}s ...')
    print(f'Estimated execution time: {utils.get_readable_time(time.time() + pending_time)}')

    time.sleep(pending_time)
    status, amount_in_ether = bridge_operator.bridge_to_zksync()

    if status:
        logging.info(f'Successfully bridge {amount_in_ether} ETH to zkSync!')
    else:
        logging.info('Bridging ETH to zkSync failed!')
