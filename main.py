from web3 import Web3

import config
import utils
from dapp.syncswap import SyncSwap
from decrypt import get_decrypted_acc_info

if __name__ == '__main__':

    w3 = Web3(Web3.HTTPProvider(config.zksync_era_rpc))

    account_info = get_decrypted_acc_info(config.account_file_path)

    account_dict = {}
    for acc_info in account_info:
        account_dict[acc_info['label']] = w3.eth.account.from_key(acc_info['private_key'])
    
    gas_for_approve = 0.26256
    gas_for_swap=0.36857
    slippage=0.45
    syncswap_operator = SyncSwap(account_dict['espoo3'], gas_for_approve, gas_for_swap, slippage)

    swap_amount = 0.008
    swap_status = syncswap_operator.eth_to_usdc_swap(swap_amount)

    current_time = utils.get_readable_time()
    if swap_status:
        print(f"[{current_time}] Swap {swap_amount}e via SyncSwap done!")
    else:
        print(f"[{current_time}] Swap {swap_amount}e via SyncSwap pending.")