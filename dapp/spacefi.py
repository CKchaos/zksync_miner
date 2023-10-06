import time
import json
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class SpaceFi(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        super().__init__(
            name='SpaceFi',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap,
            slippage=slippage
        )

        self.router_contract = self.get_contract(ZK_SPACEFI_CONTRACTS['router'], SPACEFI_ROUTER_ABI)

    def get_min_amount_out(self, from_token, to_token, amount):
        amount_out = self.router_contract.functions.getAmountsOut(
            amount,
            [ZKSYNC_TOKENS[from_token], ZKSYNC_TOKENS[to_token]]
        ).call()

        min_amount_out = int(amount_out[1] * self.mink)

        return min_amount_out

    def swap(self, from_token, to_token, amount, nonce=None):
        self.check_eth_gas()

        min_amount_out = self.get_min_amount_out(from_token, to_token, amount)

        if to_token == 'ETH' and min_amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

        deadline = int(time.time() + 1200)

        args = [] if from_token == 'ETH' else [amount]
        args += [
            min_amount_out,
            [ZKSYNC_TOKENS[from_token], ZKSYNC_TOKENS[to_token]],
            self.acc.address,
            deadline
        ]

        if from_token == 'ETH':
            tx = self.router_contract.functions.swapExactETHForTokens(*args)
        else:
            tx = self.router_contract.functions.swapExactTokensForETH(*args)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': amount if from_token == 'ETH' else 0,
            'gas': self.get_gas_for_swap(),
            'nonce': nonce
        })

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def swap_to_token(self, amount):
        status = self.swap('ETH', self.swap_token, amount)

        return status

    def swap_to_eth(self, amount):
        nonce = self.check_token_approval(ZK_SPACEFI_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, 'ETH', amount, nonce=nonce)

        return status
