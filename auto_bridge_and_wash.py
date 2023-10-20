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
from auto_washer import execute_auto_wash
from send_eth import execute_send_eth

def execute_bridge_to_zksync(acc, task_account):
    bridge_operator = txBridge(acc)
    status, amount_in_ether = bridge_operator.bridge_to_zksync()

    if status:
        logging.info(f'Successfully bridge {amount_in_ether} ETH to zkSync!')
    else:
        logging.info('Bridging ETH to zkSync failed!')
        exit()

if __name__ == "__main__":
    params = utils.load_json('./params/auto_bridge_and_wash.json')

    task_account = params['task_account']
    pending_time = params['pending_time']
    max_gap_pending_time = params['max_gap_pending_time']
    target_wash_amount = params['target_wash_amount']

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    w3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC))
    for a in account_info:
        if a['label'] == task_account:
            acc = w3.eth.account.from_key(a['private_key'])
            deposit_address = a['deposit_address']
            break

    logging.info(f'Execute bridge ETH to zkSync for account **< {task_account} >**')
    print(f'Pending for {pending_time}s ...')
    print(f'Estimated execution time: {utils.get_readable_time(time.time() + pending_time)}')

    time.sleep(pending_time)

    execute_bridge_to_zksync(acc, task_account)
    print()

    pending_time = int(1800 + 900 * random.random())
    logging.info(f'Prepare to execute washing swap for account **< {task_account} >**')
    print(f'Pending for {pending_time}s ...')
    print(f'Estimated execution time: {utils.get_readable_time(time.time() + pending_time)}')

    time.sleep(pending_time)

    logging.info("Start performing washing swap ...")
    execute_auto_wash(acc, task_account, max_gap_pending_time, target_wash_amount)
    print()

    pending_time = int(600 + 600 * random.random())
    logging.info(f'Prepare to send ETH back to OKX for account **< {task_account} >**')
    print(f'Pending for {pending_time}s ...')
    print(f'Estimated execution time: {utils.get_readable_time(time.time() + pending_time)}')

    time.sleep(pending_time)

    execute_send_eth(acc, task_account, deposit_address)

    logging.info("All tasks finished.")
