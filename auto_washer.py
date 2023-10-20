from web3 import Web3
import random
import time
from datetime import datetime
from pytz import timezone

from logger import logging
from config import *
import utils
from decrypt import get_decrypted_acc_info
from baseoperator import BaseOperator
from dapp.pancakeswap import PancakeSwap
from dapp.maverick import Maverick

class AutoWasher(BaseOperator):

    def __init__(self, acc, acc_label, gas_for_execute=0.2, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        super().__init__(
            name='AutoWasher',
            acc=acc,
            gas_for_execute=gas_for_execute
        )
        
        self.acc_label = acc_label

        self.pancake_operator = PancakeSwap(acc, 'USDC', gas_for_approve, gas_for_swap, slippage)
        self.maverick_operator = Maverick(acc, 'USDC', gas_for_approve, gas_for_swap, slippage)

    def get_amount(self, max_amount):
        p = 0.95 + random.random() * 0.05

        swap_amount = int(max_amount * p)

        swap_amount = Web3.from_wei(swap_amount, 'ether')

        digit_list = [2, 3, 4, 5, 6]
        digit_num = random.choices(digit_list, weights=(4, 23, 34, 23, 16), k=1)[0]
        swap_amount = round(swap_amount, digit_num)
        swap_amount = Web3.to_wei(swap_amount, 'ether')

        return swap_amount

    def print_tx_staus_info(self, swap_status, swap_operator_name, swap_amount, from_token, to_token):
        s = "Swap %.8f %s for %s via %s " % (swap_amount, from_token, to_token, swap_operator_name)
        if swap_status:
            s = s + 'done!'
            logging.info(s)

        else:
            s = s + 'failed!'
            logging.info(s)

            logging.error(f'account **< {self.acc_label} >** may have got a failed transanction. Stop washing')
            exit()

    def perform_single_wash_round(self):
        eth_balance = self.pancake_operator.get_eth_balance()
        swap_amount = self.get_amount(eth_balance - ETH_MINIMUM_BALANCE)

        print("Request estimated ETH -> USDC output ...")
        pancake_out = self.pancake_operator.get_min_amount_out('ETH', 'USDC', swap_amount, exact_out=1)
        maverick_out = self.maverick_operator.get_min_amount_out('USDC', swap_amount, 'ETH', exact_out=1)
        print("PancakeSwap: %.6f" % (pancake_out / 1e6))
        print("Maverick: %.6f" % (maverick_out / 1e6))

        swap_operator = self.pancake_operator if pancake_out > maverick_out else self.maverick_operator

        swap_status = swap_operator.swap_to_token(swap_amount)
        self.print_tx_staus_info(swap_status, swap_operator.name, swap_amount / 1e18, 'ETH', swap_operator.swap_token)
        if not swap_status:
            print("Buy swap failed, terminated!")
            return

        time.sleep(5 + random.random() * 5)

        swap_amount = self.pancake_operator.get_token_balance()

        print("Request estimated USDC -> ETH output ...")
        pancake_out = self.pancake_operator.get_min_amount_out('USDC', 'ETH', swap_amount, exact_out=1)
        maverick_out = self.maverick_operator.get_min_amount_out('USDC', swap_amount, 'USDC', exact_out=1)
        print("PancakeSwap: %.6f" % (pancake_out / 1e18))
        print("Maverick: %.6f" % (maverick_out / 1e18))

        swap_operator = self.pancake_operator if pancake_out > maverick_out else self.maverick_operator

        swap_status = swap_operator.swap_to_eth(swap_amount)

        wash_amount = swap_amount / (10 ** swap_operator.token_decimals)

        self.print_tx_staus_info(swap_status, swap_operator.name, wash_amount, swap_operator.swap_token, 'ETH')

        wash_amount *= 2

        return wash_amount

def execute_auto_wash(acc, task_account, max_gap_pending_time, target_wash_amount):
    gas_for_approve = 0.24
    gas_for_swap=0.38
    slippage=0.5

    washer = AutoWasher(acc, task_account, 0.2, gas_for_approve, gas_for_swap, slippage)

    start_balance = washer.get_eth_balance()

    total_wash_amount = 0
    while total_wash_amount < target_wash_amount:
        start_pengding_time = int(random.random() * max_gap_pending_time)
        logging.info(f'Execute washing swap for account **< {task_account} >**')
        print(f'Pending for {start_pengding_time}s ...')
        print(f'Estimated execution time: {utils.get_readable_time(time.time() + start_pengding_time)}')

        time.sleep(start_pengding_time)

        wash_amount = washer.perform_single_wash_round()

        total_wash_amount += wash_amount

        logging.info(f"Executed wash: {total_wash_amount} / {target_wash_amount}")
        print()

    eth_wash_cost = (start_balance - washer.get_eth_balance()) / 1e18
    wash_cost_in_usd = eth_wash_cost * utils.crypto_to_usd('ETH')

    logging.info("Wash trading finished!")
    logging.info(f"Total washing amount: {total_wash_amount}")
    logging.info("Washing cost in ETH: %.8f" % (eth_wash_cost))
    logging.info("Washing cost in USD: %.8f" % (wash_cost_in_usd))

if __name__ == '__main__':
    params = utils.load_json('./params/auto_washer.json')

    task_account = params['task_account']
    max_gap_pending_time = params['max_gap_pending_time']
    target_wash_amount = params['target_wash_amount']

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))
    for a in account_info:
        if a['label'] == task_account:
            acc = w3.eth.account.from_key(a['private_key'])
            break

    execute_auto_wash(acc, task_account, max_gap_pending_time, target_wash_amount)
    