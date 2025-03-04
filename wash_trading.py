from web3 import Web3
import random
import time

from logger import logging
from config import *
import utils
from decrypt import get_decrypted_acc_info
from dapp.pancakeswap import PancakeSwap
from dapp.maverick import Maverick

account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)
account_list = [a['label'] for a in account_info]

w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))

account_dict = {}
for acc_info in account_info:
    account_dict[acc_info['label']] = w3.eth.account.from_key(acc_info['private_key'])

gas_for_approve = 0.24
gas_for_swap=0.38
slippage=0.5

operator_set = {
    'PancakeSwap': PancakeSwap,
    'Maverick': Maverick,
}

def get_amount(max_amount):
    p = 0.95 + random.random() * 0.05

    swap_amount = int(max_amount * p)

    swap_amount = Web3.from_wei(swap_amount, 'ether')

    digit_list = [2, 3, 4, 5, 6]
    digit_num = random.choices(digit_list, weights=(4, 23, 34, 23, 16), k=1)[0]
    swap_amount = round(swap_amount, digit_num)
    swap_amount = Web3.to_wei(swap_amount, 'ether')

    return swap_amount

def print_tx_staus_info(swap_status, swap_operator_name, swap_amount, from_token, to_token):
    s = "Swap %.8f %s for %s via %s " % (swap_amount, from_token, to_token, swap_operator_name)
    if swap_status:
        s = s + 'done!'
    else:
        s = s + 'pending.'
    
    logging.info(s)

def execute_task(acc_label, operator_name, swap_token, start_pengding_time):
    assert operator_name in SWAP_TRADABLE_TOKENS
    assert acc_label in account_list

    logging.info(f'Execute swap for account **< {acc_label} >**')
    print(f'Pending for {start_pengding_time}s ...')
    print(f'Estimated execution time: {utils.get_readable_time(time.time() + start_pengding_time)}')

    time.sleep(start_pengding_time)

    swap_operator = operator_set[operator_name](account_dict[acc_label], swap_token, gas_for_approve, gas_for_swap, slippage)

    eth_balance = swap_operator.get_eth_balance()
    swap_amount = get_amount(eth_balance - ETH_MINIMUM_BALANCE)
    swap_status = swap_operator.swap_to_token(swap_amount)
    print_tx_staus_info(swap_status, swap_operator.name, swap_amount / 1e18, 'ETH', swap_operator.swap_token)
    if not swap_status:
        print("Buy swap failed, terminated!")
        return

    swap_amount = swap_operator.get_token_balance()
    swap_status = swap_operator.swap_to_eth(swap_amount)
    print_tx_staus_info(swap_status, swap_operator.name, swap_amount / (10 ** swap_operator.token_decimals), swap_operator.swap_token, 'ETH')

if __name__ == '__main__':
    operator_list = list(operator_set.keys())

    params = utils.load_json('./params/wash_trading.json')

    task_account = params['task_account']
    wash_times = params['wash_times']
    max_gap_pending_time = params['max_gap_pending_time']
    
    for i in range(wash_times):
        print(f'\nTask: {i + 1}/{wash_times}')
        operator_name = random.choice(operator_list)

        args = {
            'acc_label': task_account,
            'operator_name': operator_name,
            'swap_token': 'USDC',
            'start_pengding_time': int(max_gap_pending_time * random.random())
        }
    
        execute_task(**args)