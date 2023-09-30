import time
import json
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class SyncSwap(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        super().__init__(
            name='SyncSwap',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap,
            slippage=slippage
        )

        self.router_contract = self.get_contract(ZK_SYNCSWAP_CONTRACTS['router'], SYNCSWAP_ROUTER_ABI)
        self.pool_factory = self.get_contract(ZK_SYNCSWAP_CONTRACTS["pool_factory"], SYNCSWAP_POOL_FACTORY_ABI)
        
        self.pool_address = self.get_pool('ETH', self.swap_token)
        self.pool_contract = self.get_contract(self.pool_address, SYNCSWAP_CLASSIC_POOL_ABI)

    def prepare_data_for_swap(self, address, token_addr):
        withdraw_mode = 1

        swap_data = encode(['address', 'address', 'uint8'], [token_addr, address, withdraw_mode])

        return swap_data

    def get_pool(self, from_token, to_token):
        pool_address = self.pool_factory.functions.getPool(
            ZKSYNC_TOKENS[from_token],
            ZKSYNC_TOKENS[to_token]
        ).call()

        return pool_address

    def get_min_amount_out(self, token_address, amount):
        amount_out = self.pool_contract.functions.getAmountOut(
            token_address,
            amount,
            self.acc.address
        ).call()

        min_amount_out = int(amount_out * self.mink)

        return min_amount_out

    def swap(self, from_token, amount, nonce=None):
        min_amount_out = self.get_min_amount_out(ZKSYNC_TOKENS[from_token], amount)

        if from_token != 'ETH' and min_amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)       

        deadline = int(time.time() + 12000)
        args = [[([(self.pool_address, self.prepare_data_for_swap(self.acc.address, ZKSYNC_TOKENS[from_token]),
                    ZERO_ADDRESS,
                    b'')],
                  ZERO_ADDRESS if from_token == 'ETH' else ZKSYNC_TOKENS[self.swap_token],
                  amount)],
                min_amount_out,
                deadline]

        tx_data = utils.get_zksync_tx_init_data()
        tx_data.update({
            'from': self.acc.address,
            'value': amount if from_token == 'ETH' else 0,
            'gas': self.gas_for_swap,
            'nonce': nonce
        })

        tx = self.router_contract.functions.swap(*args)
        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def swap_to_token(self, amount):
        status = self.swap('ETH', amount)

        return status

    def swap_to_eth(self, amount):
        nonce = self.check_token_approval(ZK_SYNCSWAP_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, amount, nonce=nonce)

        return status
