from web3 import Web3
import random
import time

from config import *
import utils
from dapp.syncswap import SyncSwap
from dapp.pancakeswap import PancakeSwap
from dapp.mute import Mute
from dapp.spacefi import SpaceFi
from dapp.zkswap import zkSwap
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
    'Mute': Mute,
    'SpaceFi': SpaceFi,
    'zkSwap': zkSwap,
}

gas_for_approve = 0.24
gas_for_swap=0.38
slippage=0.5

def get_amount(max_amount):
    if max_amount < 0.0025 * 1e18:
        raise Exception(utils.get_readable_time(), 'ETH balance is not enough for swapping.')

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

def get_wash_pending_time():
    rand = random.random()
    add_time = 60 if rand < 0.1 else 0
    wash_pending_time = 5 + int(60 * random.random()) + add_time

    return wash_pending_time

def print_tx_staus_info(swap_status, swap_operator_name, swap_amount, from_token, to_token):
    current_time = utils.get_readable_time()
    s = "[%s] Swap %.8f %s for %s via %s " % (current_time, swap_amount, from_token, to_token, swap_operator_name)
    if swap_status:
        print(s + 'done!')
    else:
        print(s + 'pending.')

def get_gas_factor(gas_price):
    gas_factor = 1 if gas_price < TARGET_GAS_PRICE else gas_price / TARGET_GAS_PRICE * 0.5 + 0.5

    return gas_factor

def check_eth_gas():
    retry_pending_time = 300
    while(True):
        mainnet_gas_price = utils.get_eth_mainnet_gas_price()
        current_time = utils.get_readable_time()
        print(f'[{current_time}] ETH gas price is {mainnet_gas_price} gwei.')
        if mainnet_gas_price > MAX_GWEI:
            print(f'ETH gas price is too high.\nPending for {retry_pending_time}s ...')
            time.sleep(retry_pending_time)
        else:
            return mainnet_gas_price

def execute_task(acc_label, operator_name, swap_token, swap_eth_to_token, swap_token_to_eth, start_pengding_time):
    assert operator_name in SWAP_TRADABLE_TOKENS
    assert swap_token in SWAP_TRADABLE_TOKENS[operator_name]
    assert acc_label in account_list

    current_time = utils.get_readable_time()
    print(f'[{current_time}] Execute swap for account **< {acc_label} >**')
    print(f'Pending for {start_pengding_time}s ...')
    print(f'Estimated execution time: {utils.get_readable_time(time.time() + start_pengding_time)}')

    time.sleep(start_pengding_time)

    gas_price = check_eth_gas()

    f = get_gas_factor(gas_price)

    swap_operator = operator_set[operator_name](account_dict[acc_label], swap_token, gas_for_approve * f, gas_for_swap * f, slippage)

    if swap_eth_to_token == 0 and swap_token == 'USDC':
        balance = swap_operator.get_token_balance()
        if balance < USDC_SWAP_MIN_LIMIT:
            swap_eth_to_token = 1
            print('Buy USDC first ...')

    if swap_eth_to_token:
        eth_balance = swap_operator.get_eth_balance()
        swap_amount = get_amount(eth_balance - ETH_MINIMUM_BALANCE)
        swap_status = swap_operator.swap_to_token(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / 1e18, 'ETH', swap_operator.swap_token)
        if not swap_status:
            print("Buy swap failed, terminated!")
            return

    if swap_token_to_eth:
        if swap_eth_to_token:
            wash_pending_time = get_wash_pending_time()
            print(f'Pending for {wash_pending_time}s ...')
            time.sleep(wash_pending_time)

        swap_amount = swap_operator.get_token_balance()
        swap_status = swap_operator.swap_to_eth(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / (10 ** swap_operator.token_decimals), swap_operator.swap_token, 'ETH')

if __name__ == '__main__':

    operator_list = list(operator_set.keys())

    total_time = 14000
    task_accounts = [
        'espoo7',
        'sgl1',
        'sgl5',
        'sgl10',
        'sgl17',
        'sgl27',
        'sgl34',
        'sgl39',
        'sgl46',
        'sgl54',
        'sgl63',
        'sgl91',
    ]
    random.shuffle(task_accounts)

    task_num = len(task_accounts)

    randomlist = sorted(random.sample(range(total_time), task_num - 1))
    randomlist.append(total_time)

    pending_time_list = [randomlist[0]]

    for i in range(1, task_num):
        pending_time_list.append(randomlist[i] - randomlist[i - 1])        

    task_args = []
    for i, account in enumerate(task_accounts):
        assert account in account_list

        operator_name = random.choice(operator_list)
        swap_token = random.choice(SWAP_TRADABLE_TOKENS[operator_name])

        if random.random() < 0.5:
            swap_token = 'USDC'

        swap_mode = random.choices([(1, 0), (0, 1), (1, 1)], weights=(40, 30, 30), k=1)[0]
        
        if swap_token != 'USDC':
            swap_mode = (1, 1)

        args = {
            'acc_label': account,
            'operator_name': operator_name,
            'swap_token': swap_token,
            'swap_eth_to_token': swap_mode[0],
            'swap_token_to_eth': swap_mode[1],
            'start_pengding_time': pending_time_list[i]
        }
    
        task_args.append(args)

    for i in range(task_num):
        print(task_args[i])

    for i in range(task_num):
        execute_task(**task_args[i])
