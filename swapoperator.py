import time
import json
import random
from web3 import Web3
from eth_abi import encode

from baseoperator import BaseOperator
from config import * 
import utils

class SwapOperator(BaseOperator):

    def __init__(self, name, acc, swap_token, gas_for_approve=0.25, gas_for_swap=0.4, slippage=0.3):
        super().__init__(
            name=name,
            acc=acc,
            gas_for_approve=gas_for_approve
        )

        self.swap_token = swap_token
        
        self.token_contract = self.get_contract(ZKSYNC_TOKENS[self.swap_token], ERC20_ABI)
        self.token_decimals = self.get_swap_token_decimals()

        gas_for_swap *= 1 + random.random() * 0.12
        slippage *= 1 + random.random() * 0.5

        self.gas_for_swap = utils.usd_to_zk_gas(gas_for_swap, self.eth_market_price)
        self.mink = (100 - slippage) * 0.01

    def get_swap_token_decimals(self):
        decimals = self.token_contract.functions.decimals().call()

        return decimals

    def get_eth_balance(self):
        balance = self.w3.eth.get_balance(self.acc.address)

        return balance

    def get_token_balance(self):
        balance = self.token_contract.functions.balanceOf(self.acc.address).call()

        return balance

    def get_gas_for_swap(self):
        gas = int(self.gas_for_swap * self.gas_factor)

        return gas

    def swap_to_token(self, amount):
        pass

    def swap_to_eth(self, amount):
        pass
