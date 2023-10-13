from web3 import Web3
import random
import time

from logger import logging
from config import *
import utils
from decrypt import get_decrypted_acc_info
from baseoperator import BaseOperator

class ETHSender(BaseOperator):

    def __init__(self, acc, gas_for_execute=0.2):
        super().__init__(
            name='ETHSender',
            acc=acc,
            gas_for_execute=gas_for_execute
        )

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

if __name__ == '__main__':

    gas_for_execute=0.18

    params = utils.load_params('./params/send_eth.json')

    task_account = params['task_account']
    amount_in_ether = params['amount_in_ether']
    pending_time = params['pending_time']

    logging.info(f'Prepare to send {amount_in_ether} ETH to OKX for account **< {task_account} >**')
    print(f"Pending for {pending_time}s ...")
    time.sleep(pending_time)

    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))
    for a in account_info:
        if a['label'] == task_account:
            acc = w3.eth.account.from_key(a['private_key'])
            deposit_address = a['deposit_address']

    sender = ETHSender(acc, gas_for_execute)

    amount = Web3.to_wei(amount_in_ether, 'ether')
    sender.send_eth(deposit_address, amount)

    logging.info(f'{amount_in_ether} ETH sent.')