import time
import json
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class Maverick(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.5):
        super().__init__(
            name='Maverick',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap,
            slippage=slippage
        )

        self.router_contract = self.get_contract(ZK_MAVERICK_CONTRACTS['router'], MAVERICK_ROUTER_ABI)
        self.position_contract = self.get_contract(ZK_MAVERICK_CONTRACTS['pool_information'], MAVERICK_POSITION_ABI)

    def get_path(self, pool_token, from_token, to_token):
        path_data = [
            ZKSYNC_TOKENS[from_token],
            ZK_MAVERICK_POOL_ADDRESSES[pool_token],
            ZKSYNC_TOKENS[to_token],
        ]

        path = b"".join([bytes.fromhex(address[2:]) for address in path_data])

        return path

    def get_min_amount_out(self, pool_token, amount_in, from_token):
        amount_out = self.position_contract.functions.calculateSwap(
            ZK_MAVERICK_POOL_ADDRESSES[pool_token],
            amount_in, 
            True if ZK_MAVERICK_POOL_TOKEN_A[pool_token] == from_token else False,
            True,
            0
        ).call()

        amount_out = amount_out * ZK_MAVERICK_TOKEN_FACTOR[pool_token]

        min_amount_out = int(amount_out * self.mink)

        return min_amount_out

    def swap(self, from_token, to_token, amount, nonce=None):
        self.check_eth_gas()

        pool_token = to_token if from_token == 'ETH' else from_token

        min_amount_out = self.get_min_amount_out(pool_token, amount, from_token)

        if to_token == 'ETH' and min_amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

        deadline = int(time.time() + 1800)
        input_data = self.router_contract.encodeABI(
            fn_name="exactInput",
            args=[(
                self.get_path(pool_token, from_token, to_token),
                self.acc.address if from_token == 'ETH' else ZERO_ADDRESS,
                deadline,
                amount,
                min_amount_out,
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
        nonce = self.check_token_approval(ZK_MAVERICK_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, 'ETH', amount, nonce=nonce)

        return status
