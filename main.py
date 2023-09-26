from web3 import Web3
import random

import config
import utils
from dapp.syncswap import SyncSwap
from decrypt import get_decrypted_acc_info

def print_tx_staus_info(swap_status, swap_amount, unit):
    current_time = utils.get_readable_time()
    if swap_status:
        print(f"[{current_time}] Swap {swap_amount}{unit} via SyncSwap done!")
    else:
        print(f"[{current_time}] Swap {swap_amount}{unit} via SyncSwap pending.")

if __name__ == '__main__':

    acc_label = 'sgl63'
    swap_eth_to_usdc = 1
    swap_usdc_to_eth = 1
    swap_amount = 0.003

    start_pengding_time = 2200
    wash_pending_time = 32

    gas_for_approve = 0.24 + random.random() * 0.04
    gas_for_swap=0.36 + random.random() * 0.04
    slippage=0.3 +  + random.random() * 0.1
    
    current_time = utils.get_readable_time()
    print(f'[{current_time}] Execute swap for account **< {acc_label} >**')
    print(f'Pending for {start_pengding_time}s ...')

    import time
    time.sleep(start_pengding_time)

    mainnet_gas_price = utils.get_eth_mainnet_gas_price()
    current_time = utils.get_readable_time()
    print(f'[{current_time}] ETH gas price is {mainnet_gas_price} gwei.')
    if mainnet_gas_price > 24:
        print(f'ETH gas price is too high. Abort task.')
        exit()

    w3 = Web3(Web3.HTTPProvider(config.zksync_era_rpc))

    account_info = get_decrypted_acc_info(config.account_file_path)

    account_dict = {}
    for acc_info in account_info:
        account_dict[acc_info['label']] = w3.eth.account.from_key(acc_info['private_key'])

    syncswap_operator = SyncSwap(account_dict[acc_label], gas_for_approve, gas_for_swap, slippage)

    if swap_eth_to_usdc:
        unit_str = 'e'
        rand = random.random()
        digit_num = random.randint(1,4)
        swap_amount = swap_amount + round(rand, digit_num) / 1000
        swap_status = syncswap_operator.eth_to_usdc_swap(swap_amount)
        print_tx_staus_info(swap_status, swap_amount, unit_str)

    if swap_usdc_to_eth:
        time.sleep(wash_pending_time)
        swap_amount = utils.zk_usdc_balance(syncswap_operator.acc.address)
        unit_str = 'u'
        if swap_amount > 3:
            syncswap_operator.check_usdc_approval(swap_amount)
            swap_status = syncswap_operator.usdc_to_eth_swap(swap_amount)
            print_tx_staus_info(swap_status, swap_amount, unit_str)
        