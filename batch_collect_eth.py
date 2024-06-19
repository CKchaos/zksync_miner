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
            gas_for_execute=0.1
        )

        self.w3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC))

    def sign_and_send_tx(self, builded_tx):
        signed_tx = self.w3.eth.account.sign_transaction(builded_tx, self.acc.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

        time.sleep(3)

        return tx_hash

    def send_eth(self, deposit_address, balance):
        self.check_eth_gas(7)
        assert deposit_address != ZERO_ADDRESS

        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        gas_price = int(self.w3.eth.gas_price * 1.05)

        print("gas price:", Web3.from_wei(gas_price, 'gwei'))
        gas = gas_price * 21000
        print("gas:", Web3.from_wei(gas, 'ether'))

        sent_amount = balance - gas

        if sent_amount <= 0:
            return  None, 0

        tx_data = self.get_init_tx_data()
        tx_data = {
            "chainId": self.w3.eth.chain_id,
            "from": self.acc.address,
            'value': sent_amount,
            'to': Web3.to_checksum_address(deposit_address),
            'gas': 21000,
            "gasPrice": gas_price,
            'nonce': nonce
        }

        tx_hash = self.sign_and_send_tx(tx_data)
        #tx_hash = 0

        return tx_hash, sent_amount

def execute_send_eth(acc, task_account, deposit_address):
    sender = ETHSender(acc)

    eth_balance = sender.get_eth_balance()
    tx_hash, sent_amount = sender.send_eth(deposit_address, eth_balance)

    sent_amount = Web3.from_wei(sent_amount, 'ether')

    logging.info(f'{task_account}: {sent_amount} ETH sent via tx({tx_hash})')

    return sent_amount

if __name__ == '__main__':

    filter_list = []
    with open("./data/collect_eth_filter_out") as f:
        lines = f.readlines()
        for line in lines:
            filter_list.append(line.strip())

    collect_list = []
    with open("./data/collect_eth_list") as f:
        lines = f.readlines()
        for line in lines:
            acc = line.strip()
            if acc not in filter_list:
                collect_list.append(acc)

    #collect_list = collect_list[31:]

    to_address = '0x8880b5c6f3a3867f28f200d0e8df452ccc3f6a4f'

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    w3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC))
    
    acc_list = {}
    for a in account_info:
        if a['label'] in collect_list:
            acc = w3.eth.account.from_key(a['private_key'])
            acc_list[a['label']] = acc

    collected_eth = 0
    for task_account in collect_list:
        sent_amount = execute_send_eth(acc_list[task_account], task_account, to_address)
        collected_eth += sent_amount

    print("total collected eth：", collected_eth)