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

def record_sending(acc_label, amount):
    t = time.time()
    time_str = datetime.fromtimestamp(t, tz=timezone('Asia/Shanghai')).strftime("%m-%d %H:%M")
    s = f"{acc_label:6.6}  {time_str:11.11}  {amount}\n"

    with open('data/send_eth_record', 'a') as f:
        f.write(s)

class ETHSender(BaseOperator):

    def __init__(self, acc, gas_for_execute=0.2):
        super().__init__(
            name='ETHSender',
            acc=acc,
            gas_for_execute=gas_for_execute
        )

    def get_amount(self, balance):
        rand = random.random()
        add_mount = 0.005 * random.random() if rand < 0.3 else 0
        net_amount_in_ether = 0.0105 + 0.0065 * random.random() + add_mount
        net_amount = Web3.to_wei(net_amount_in_ether, 'ether')

        amount = balance - net_amount
        amount_in_ether = Web3.from_wei(amount, 'ether')

        digit_list = [3, 4, 5, 6, 7]
        digit_num = random.choices(digit_list, weights=(14, 18, 28, 26, 14), k=1)[0]
        amount_in_ether = round(amount_in_ether, digit_num)

        return amount_in_ether

    def send_eth(self, deposit_address, amount):
        self.check_eth_gas()

        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': amount,
            'to': Web3.to_checksum_address(deposit_address),
            'gas': self.get_gas_for_execute(),
            'nonce': nonce
        })

        status = self.sign_and_send_tx(tx_data)

        return status

def execute_send_eth(acc, task_account, deposit_address):
    gas_for_execute=0.18
    sender = ETHSender(acc, gas_for_execute)

    eth_balance = sender.get_eth_balance()
    amount_in_ether = sender.get_amount(eth_balance)

    amount = Web3.to_wei(amount_in_ether, 'ether')
    sender.send_eth(deposit_address, amount)

    record_sending(task_account, amount_in_ether)
    logging.info(f'{amount_in_ether} ETH sent.')

if __name__ == '__main__':
    params = utils.load_json('./params/send_eth.json')

    task_account = params['task_account']
    pending_time = params['pending_time']

    logging.info(f'Prepare to send ETH to OKX for account **< {task_account} >**')
    print(f"Pending for {pending_time}s ...")
    time.sleep(pending_time)

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))
    for a in account_info:
        if a['label'] == task_account:
            acc = w3.eth.account.from_key(a['private_key'])
            deposit_address = a['deposit_address']
            break

    execute_send_eth(acc, task_account, deposit_address)