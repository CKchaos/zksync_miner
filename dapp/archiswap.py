import time
import json
from web3 import Web3
from eth_abi import encode

from baseoperator import BaseOperator
from config import * 
import utils

class ArchiSwap(BaseOperator):

    def __init__(self, acc, gas_for_execute=0.4):
        super().__init__(
            name='ArchiSwap',
            acc=acc,
            gas_for_execute=gas_for_execute
        )

    def faucet(self):
        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': 0,
            'to': ZK_ARCHISWAP_CONTRACTS['faucet'],
            'gas': self.gas_for_execute,
            'nonce': nonce,
            'data': '0xde5f72fd'
        })

        status = self.sign_and_send_tx(tx_data)

        return status
