from web3 import Web3
import random

from config import *
import utils
from dapp.syncswap import SyncSwap
from dapp.pancakeswap import PancakeSwap
from decrypt import get_decrypted_acc_info

def print_tx_staus_info(swap_status, swap_operator_name, swap_amount, unit):
    current_time = utils.get_readable_time()
    s = "[%s] Swap %.6f %s via %s " % (current_time, swap_amount, unit, swap_operator_name)
    if swap_status:
        print(s + 'done!')
    else:
        print(s + 'pending.')

if __name__ == '__main__':
    gas_price_limit = 25

    acc_label = 'sgl32'
    swap_token = 'SPACE'
    swap_eth_to_token = 1
    swap_token_to_eth = 1
    swap_amount = 0.007

    start_pengding_time = 1

    gas_for_approve = 0.24 + random.random() * 0.04
    gas_for_swap=0.38 + random.random() * 0.04
    slippage=0.3 +  + random.random() * 0.1
    
    current_time = utils.get_readable_time()
    print(f'[{current_time}] Execute swap for account **< {acc_label} >**')
    print(f'Pending for {start_pengding_time}s ...')

    import time
    time.sleep(start_pengding_time)

    mainnet_gas_price = utils.get_eth_mainnet_gas_price()
    current_time = utils.get_readable_time()
    print(f'[{current_time}] ETH gas price is {mainnet_gas_price} gwei.')
    if mainnet_gas_price > gas_price_limit:
        print(f'ETH gas price is too high. Abort task.')
        exit()

    w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    account_dict = {}
    for acc_info in account_info:
        account_dict[acc_info['label']] = w3.eth.account.from_key(acc_info['private_key'])

    #swap_operator = PancakeSwap(account_dict[acc_label], gas_for_approve, gas_for_swap, slippage)
    swap_operator = SyncSwap(account_dict[acc_label], swap_token, gas_for_approve, gas_for_swap, slippage)

    if swap_eth_to_token:
        rand = random.random()
        digit_num = random.randint(1,4)
        swap_amount = swap_amount + round(rand, digit_num) / 1000
        swap_amount = int(swap_amount * 1e18)
        swap_status = swap_operator.swap_to_token(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / 1e18, 'ETH')

    if swap_token_to_eth:
        rand = random.random()
        add_time = 60 if rand < 0.1 else 0
        wash_pending_time = 5 + int(60 * random.random()) + add_time
        print(f'Pending for {wash_pending_time}s ...')

        #time.sleep(wash_pending_time)
        swap_amount = swap_operator.get_token_balance()
        swap_status = swap_operator.swap_to_eth(swap_amount)
        print_tx_staus_info(swap_status, swap_operator.name, swap_amount / (10 ** swap_operator.token_decimals), swap_operator.swap_token)
        