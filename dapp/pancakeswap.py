import time
import json
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class PancakeSwap(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        super().__init__(
            name='PancakeSwap',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap,
            slippage=slippage
        )

        self.router_contract = self.get_contract(ZK_PANCAKE_CONTRACTS['router'], PANCAKE_ROUTER_ABI)
        self.quoter_contract = self.get_contract(ZK_PANCAKE_CONTRACTS['quoter'], PANCAKE_QUOTER_ABI)

    def get_pool_addr(self, from_token, to_token, fee):
        factory = self.get_contract(ZK_PANCAKE_CONTRACTS['factory'], PANCAKE_FACTORY_ABI)

        pool_addr = factory.functions.getPool(
            ZKSYNC_TOKENS[from_token],
            ZKSYNC_TOKENS[to_token],
            fee
        ).call()

        return pool_addr

    def get_min_amount_out(self, from_token, to_token, amount, exact_out=0):
        quoter_data = self.quoter_contract.functions.quoteExactInputSingle((
            ZKSYNC_TOKENS[from_token],
            ZKSYNC_TOKENS[to_token],
            amount, 
            ZK_PANCAKE_POOL_FEES[self.swap_token],
            0
        )).call()

        if exact_out:
            return int(quoter_data[0])

        min_amount_out = int(quoter_data[0] * self.mink)

        return min_amount_out

    def swap(self, from_token, to_token, amount, nonce=None):
        self.check_eth_gas()

        min_amount_out = self.get_min_amount_out(from_token, to_token, amount)

        if to_token == 'ETH' and min_amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

        deadline = int(time.time() + 280)
        multocall_data = [self.router_contract.encodeABI(
            fn_name="exactInputSingle",
            args=[(
                ZKSYNC_TOKENS[from_token],
                ZKSYNC_TOKENS[to_token],
                ZK_PANCAKE_POOL_FEES[self.swap_token],
                "0x0000000000000000000000000000000000000002" if to_token == 'ETH' else self.acc.address,
                amount,
                min_amount_out,
                0
            )]
        )]

        if to_token == 'ETH':
            unwrap_data = self.router_contract.encodeABI(
                fn_name="unwrapWETH9",
                args=[
                    min_amount_out,
                    self.acc.address
                ]
            )

            multocall_data.append(unwrap_data)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': amount if from_token == 'ETH' else 0,
            'gas': self.get_gas_for_swap(),
            'nonce': nonce
        })

        tx = self.router_contract.functions.multicall(
            deadline,
            multocall_data
        )
        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def swap_to_token(self, amount):
        status = self.swap('ETH', self.swap_token, amount)

        return status

    def swap_to_eth(self, amount):
        nonce = self.check_token_approval(ZK_PANCAKE_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, 'ETH', amount, nonce=nonce)

        return status
