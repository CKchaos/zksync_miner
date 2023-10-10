import time
import json
import random
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class iZumi(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.5):
        super().__init__(
            name='iZumi',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap,
            slippage=0.8
        )

        self.router_contract = self.get_contract(ZK_IZUMI_CONTRACTS['router'], IZUMI_ROUTER_ABI)

    def get_min_amount_out(self, amount_in, from_token):
        eth_market_price = utils.crypto_to_usd('ETH')

        if from_token == 'ETH':
            amount_out = eth_market_price * amount_in / 1e12
        else:
            amount_out = amount_in / eth_market_price * 1e12

        min_amount_out = int(amount_out * self.mink)

        return min_amount_out

    def swap(self, from_token, to_token, amount, nonce=None):
        self.check_eth_gas()

        min_amount_out = self.get_min_amount_out(amount, from_token)

        if to_token == 'ETH' and min_amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

        fee = random.choice(['000190', '0007D0'])

        path = ZKSYNC_TOKENS[from_token] + fee + ZKSYNC_TOKENS[to_token][2:]

        deadline = int(time.time() + 600)
        input_data = self.router_contract.encodeABI(
            fn_name="swapAmount",
            args=[(
                path,
                self.acc.address if from_token == 'ETH' else ZERO_ADDRESS,
                amount,
                min_amount_out,
                deadline
            )]
        )

        if from_token == 'ETH':
            append_data = self.router_contract.encodeABI(
                fn_name="refundETH",
            )
        else:
            append_data = self.router_contract.encodeABI(
                fn_name="unwrapWETH9",
                args=[
                    0,
                    self.acc.address
                ]
            )

        multicall_data = [input_data, append_data]

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': amount if from_token == 'ETH' else 0,
            'gas': self.get_gas_for_swap(),
            'nonce': nonce
        })

        tx = self.router_contract.functions.multicall(
            multicall_data
        )
        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def swap_to_token(self, amount):
        status = self.swap('ETH', self.swap_token, amount)

        return status

    def swap_to_eth(self, amount):
        nonce = self.check_token_approval(ZK_IZUMI_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, 'ETH', amount, nonce=nonce)

        return status
