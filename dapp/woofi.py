import time
import json
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class WooFi(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.5):
        super().__init__(
            name='WooFi',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap,
            slippage=slippage
        )

        self.router_contract = self.get_contract(ZK_WOOFI_CONTRACTS['router'], WOOFI_ROUTER_ABI)

    def get_min_amount_out(self, from_token, to_token, amount):
        amount_out = self.router_contract.functions.querySwap(
            WOO_E_ADDRESS if from_token == 'ETH' else ZKSYNC_TOKENS[from_token],
            WOO_E_ADDRESS if to_token == 'ETH' else ZKSYNC_TOKENS[to_token],
            amount
        ).call()

        min_amount_out = int(amount_out * self.mink)

        return min_amount_out

    def swap(self, from_token, to_token, amount, nonce=None):
        self.check_eth_gas()

        min_amount_out = self.get_min_amount_out(from_token, to_token, amount)

        if from_token != 'ETH' and min_amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': amount if from_token == 'ETH' else 0,
            'gas': self.get_gas_for_swap(),
            'nonce': nonce
        })

        tx = self.router_contract.functions.swap(
            WOO_E_ADDRESS if from_token == 'ETH' else ZKSYNC_TOKENS[from_token],
            WOO_E_ADDRESS if to_token == 'ETH' else ZKSYNC_TOKENS[to_token],
            amount,
            min_amount_out,
            self.acc.address,
            self.acc.address
        )

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def swap_to_token(self, amount):
        status = self.swap('ETH', self.swap_token, amount)

        return status

    def swap_to_eth(self, amount):
        nonce = self.check_token_approval(ZK_WOOFI_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, 'ETH', amount, nonce=nonce)

        return status
