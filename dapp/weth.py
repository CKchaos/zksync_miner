import time
import json
from web3 import Web3
from eth_abi import encode

from baseoperator import BaseOperator
from config import * 
import utils

class WETH(BaseOperator):

    def __init__(self, acc, gas_for_execute=0.3):
        super().__init__(
            name='WETH',
            acc=acc,
            gas_for_execute=gas_for_execute
        )

        self.contract = self.get_contract(ZKSYNC_TOKENS['WETH'], WETH_ABI)

        self.withdrawal_minimum = 1000000000000000

    def get_deposit_amount(self):
        amount = self.contract.functions.balanceOf(self.acc.address).call()

        return amount

    def wrap(self, amount):
        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': amount,
            'gas': self.gas_for_execute,
            'nonce': nonce,
        })

        tx = self.contract.functions.deposit()

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def unwrap(self):
        amount = self.get_deposit_amount()

        if amount > self.withdrawal_minimum:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

            tx_data = self.get_init_tx_data()
            tx_data.update({
                'value': 0,
                'gas': self.gas_for_execute,
                'nonce': nonce
            })

            tx = self.contract.functions.withdraw(amount)

            builded_tx = tx.build_transaction(tx_data)

            status = self.sign_and_send_tx(builded_tx)

            return status

