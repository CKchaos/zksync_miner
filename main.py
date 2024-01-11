from web3 import Web3
import random
import time
import numpy as np

from logger import logging
from config import *
import utils
from dapp.syncswap import SyncSwap
from dapp.pancakeswap import PancakeSwap
from dapp.mute import Mute
from dapp.spacefi import SpaceFi
from dapp.zkswap import zkSwap
from dapp.maverick import Maverick
from dapp.izumi import iZumi
from decrypt import get_decrypted_acc_info

account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)
account_list = [a['label'] for a in account_info]

w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))

account_dict = {}
for acc_info in account_info:
    account_dict[acc_info['label']] = w3.eth.account.from_key(acc_info['private_key'])

operator_set = {
    'SyncSwap': SyncSwap,
    'PancakeSwap': PancakeSwap,
    #'Mute': Mute,
    'SpaceFi': SpaceFi,
    'zkSwap': zkSwap,
    'Maverick': Maverick,
    'iZumi': iZumi,
}

gas_for_approve = 0.24
gas_for_swap=0.38
slippage=0.5

def get_amount(max_amount):
    if max_amount < 0.0025 * 1e18:
        return 0

    swap_amount = 0.0025 + 0.005 * random.random()

    digit_list = [4, 5, 6, 7, 8]
    digit_num = random.choices(digit_list, weights=(4, 16, 36, 32, 12), k=1)[0]
    swap_amount = round(swap_amount, digit_num)
    swap_amount = Web3.to_wei(swap_amount, 'ether')

    if swap_amount > max_amount:
        p = 0.95 + random.random() * 0.03
        swap_amount = max_amount * p

    swap_amount = int(swap_amount)

    return swap_amount

def get_pending_time_list(epoch_time, epoch_task_num):
    total_time = int(epoch_time * (0.9 + 0.2 * random.random()))
    unit_time = int(total_time / epoch_task_num)
    rand = np.random.rand(epoch_task_num)
    
    randomlist = np.zeros(epoch_task_num)
    for i in range(epoch_task_num - 1):
        randomlist[i] = 1 - rand[i] + rand[i + 1]
    randomlist[-1] = 1 - rand[-1] + rand[0]
    
    max_idx = np.argmax(randomlist)
    min_idx = np.argmin(randomlist)
    
    randomlist[max_idx] = randomlist[max_idx] * 1.2
    randomlist[min_idx] = randomlist[min_idx] * 0.8
    
    randomlist = np.array(randomlist * unit_time, dtype='int64')

    return list(randomlist)

def get_wash_pending_time():
    rand = random.random()
    add_time = 60 if rand < 0.1 else 0
    wash_pending_time = 5 + int(60 * random.random()) + add_time

    return wash_pending_time

def print_tx_staus_info(swap_status, swap_operator_name, swap_amount, from_token, to_token):
    s = "Swap %.8f %s for %s via %s " % (swap_amount, from_token, to_token, swap_operator_name)
    if swap_status:
        s = s + 'done!'
    else:
        s = s + 'pending.'
    
    logging.info(s)

def execute_task(acc_label, operator_name, swap_token, swap_mode, start_pengding_time):
    assert operator_name in SWAP_TRADABLE_TOKENS
    assert swap_token in SWAP_TRADABLE_TOKENS[operator_name]
    assert acc_label in account_list

    logging.info(f'Execute swap for account **< {acc_label} >**')
    print(f'Pending for {start_pengding_time}s ...')
    print(f'Estimated execution time: {utils.get_readable_time(time.time() + start_pengding_time)}')

    time.sleep(start_pengding_time)

    swap_operator = operator_set[operator_name](account_dict[acc_label], swap_token, gas_for_approve, gas_for_swap, slippage)

    if swap_token == 'USDC':
        balance = swap_operator.get_token_balance()
        if balance > USDC_SWAP_MIN_LIMIT:
            swap_mode = (0, 1)
            print('Sell USDC this time ...')
        elif swap_mode[0] == 0:
            swap_mode = (1, 1)
            print('Buy USDC first ...')

    if swap_mode[0]:
        eth_balance = swap_operator.get_eth_balance()
        swap_amount = get_amount(eth_balance - ETH_MINIMUM_BALANCE)
        if swap_amount == 0:
            logging.info('ETH balance is not enough for swapping.')
            return
        swap_status = swap_operator.swap_to_token(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / 1e18, 'ETH', swap_operator.swap_token)
        if not swap_status:
            print("Buy swap failed, terminated!")
            return

    if swap_mode[1]:
        if swap_mode[0]:
            wash_pending_time = get_wash_pending_time()
            print(f'Pending for {wash_pending_time}s ...')
            time.sleep(wash_pending_time)

        swap_amount = swap_operator.get_token_balance()
        swap_status = swap_operator.swap_to_eth(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / (10 ** swap_operator.token_decimals), swap_operator.swap_token, 'ETH')

if __name__ == '__main__':

    operator_list = list(operator_set.keys())

    total_time = 84000
    task_accounts = [
            'sgl8',
    'sgl9',
    'sgl21',
    'sgl27',
    'sgl32',
    'sgl33',
    'sgl35',
    'sgl48',
    'sgl49',
    'sgl57',
    'sgl60',
    'sgl64',
    'sgl65',
    'sgl66',
    'sgl68',
    'sgl69',
    'sgl71',
    'sgl74',
    'sgl77',
    'sgl78',
    'sgl79',
    'sgl80',
    'sgl81',
    'sgl82',
    'sgl84',
    'sgl85',
    'sgl86',
    'sgl88',
    'sgl89',
    'sgl90',
    'sgl92',
    'sgl94',
    'sgl95',
    'sgl96',
    'sgl97',
    'sgl98',
    'sgl99',
    'sgl100',
    'sgl101',
    'sgl104',
    'sgl105',
    'sgl106',
    'sgl109',
    'sgl110',
    'sgl111',
    'sgl113',
    'sgl116',
    'sgl117',
    'sgl118',
    'sgl119',
    'sgl120',
    'sgl121',
    'sgl123',
    'sgl124',
    'sgl126',
    'sgl129',
    'sgl131',
    'sgl133',
    'sgl134',
    'sgl135',
    'sgl137',
    'sgl138',
    'sgl141',
    'sgl142',
    'sgl143'
    ]
    account_list1 = task_accounts[::2]
    account_list2 = task_accounts[1::2]

    random.shuffle(account_list1)
    random.shuffle(account_list2)

    task_accounts = account_list1 + account_list2

    task_num = len(task_accounts)
    print('Tasks:', task_num)

    pending_time_list = get_pending_time_list(total_time, task_num)
    pending_time_list[0] = 1

    task_args = []
    for i, account in enumerate(task_accounts):
        assert account in account_list

        operator_name = random.choice(operator_list)
        swap_token = random.choice(SWAP_TRADABLE_TOKENS[operator_name])

        if random.random() < 0.5:
            swap_token = 'USDC'
        
        swap_token = 'USDC'

        swap_mode = random.choices([(1, 0), (0, 1), (1, 1)], weights=(40, 40, 20), k=1)[0]
        swap_mode = (1, 0)

        if swap_token != 'USDC':
            swap_mode = (1, 1)

        args = {
            'acc_label': account,
            'operator_name': operator_name,
            'swap_token': swap_token,
            'swap_mode': swap_mode,
            'start_pengding_time': pending_time_list[i]
        }
    
        task_args.append(args)

    for i in range(task_num):
        print(task_args[i])

    for i in range(task_num):
        print(f'\nTask {i + 1}/{task_num}:')
        execute_task(**task_args[i])

    logging.info('All tasks finished!')
