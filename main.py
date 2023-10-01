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

def print_tx_staus_info(swap_status, swap_operator_name, swap_amount, unit):
    current_time = utils.get_readable_time()
    s = "[%s] Swap %.8f %s via %s " % (current_time, swap_amount, unit, swap_operator_name)
    if swap_status:
        print(s + 'done!')
    else:
        print(s + 'pending.')

if __name__ == '__main__':

    operator_name = 'SyncSwap'
    operator_name = 'PancakeSwap'
    #operator_name = 'Mute'
    operator_name = 'SpaceFi'
    operator_name = 'zkSwap'

    acc_label = 'sgl6'
    swap_token = 'ZF'
    swap_eth_to_token = 1
    swap_token_to_eth = 1

    start_pengding_time = 3

    gas_for_approve = 0.24
    gas_for_swap=0.38
    slippage=0.5

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)
    account_list = [a['label'] for a in account_info]

    assert operator_name in SWAP_TRADABLE_TOKENS
    assert swap_token in SWAP_TRADABLE_TOKENS[operator_name]
    assert acc_label in account_list

    current_time = utils.get_readable_time()
    print(f'[{current_time}] Execute swap for account **< {acc_label} >**')
    print(f'Pending for {start_pengding_time}s ...')

    time.sleep(start_pengding_time)

    mainnet_gas_price = utils.get_eth_mainnet_gas_price()
    current_time = utils.get_readable_time()
    print(f'[{current_time}] ETH gas price is {mainnet_gas_price} gwei.')
    if mainnet_gas_price > MAX_GWEI:
        print(f'ETH gas price is too high. Abort task.')
        exit()

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

    swap_operator = operator_set[operator_name](account_dict[acc_label], swap_token, gas_for_approve, gas_for_swap, slippage)

    if swap_eth_to_token:
        eth_balance = swap_operator.get_eth_balance()
        swap_amount = get_amount(eth_balance - ETH_MINIMUM_BALANCE)
        swap_status = swap_operator.swap_to_token(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / 1e18, 'ETH')
        if not swap_status:
            print("Buy swap failed, terminated!")
            exit()

    if swap_token_to_eth:
        if swap_eth_to_token:
            wash_pending_time = get_wash_pending_time()
            print(f'Pending for {wash_pending_time}s ...')
            time.sleep(wash_pending_time)

        swap_amount = swap_operator.get_token_balance()
        swap_status = swap_operator.swap_to_eth(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / (10 ** swap_operator.token_decimals), swap_operator.swap_token)
        