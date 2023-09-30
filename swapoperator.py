import time
import json
import random
from web3 import Web3
from eth_abi import encode

from config import * 
import utils

class SwapOperator():

    def __init__(self, name, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        self.name = name
        self.acc = acc
        self.swap_token = swap_token
        
        self.w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))

        self.token_contract = self.get_contract(ZKSYNC_TOKENS[self.swap_token], ERC20_ABI)
        self.token_decimals = self.get_swap_token_decimals()

        gas_for_approve *= 1 + random.random() * 0.2
        gas_for_swap *= 1 + random.random() * 0.12
        slippage *= 1 + random.random() * 0.5

        eth_market_price = utils.crypto_to_usd('ETH')
        self.gas_for_approve = utils.usd_to_zk_gas(gas_for_approve, eth_market_price)
        self.gas_for_swap = utils.usd_to_zk_gas(gas_for_swap, eth_market_price)
        self.mink = (100 - slippage) * 0.01

    def get_contract(self, contract_addr, abi_path):
        abi = utils.load_abi(abi_path)
        contract = self.w3.eth.contract(contract_addr, abi=abi)

        return contract

    def get_swap_token_decimals(self):
        decimals = self.token_contract.functions.decimals().call()

        return decimals

    def get_eth_balance(self):
        balance = self.w3.eth.get_balance(self.acc.address)

        return balance

    def get_token_balance(self):
        balance = self.token_contract.functions.balanceOf(self.acc.address).call()

        return balance

    def check_token_approval(self, address_to_approve, ammount_in_wei):
        print("Checking allowance ...")
        allowance_args = [self.acc.address, address_to_approve]
        allowance_in_wei = self.token_contract.functions.allowance(*allowance_args).call()

        if allowance_in_wei < ammount_in_wei:
            print("Perform allowance first ...")
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

            tx_data = utils.get_zksync_tx_init_data()
            tx_data.update({
                'from': self.acc.address,
                'value': 0,
                'gas': self.gas_for_approve,
                'nonce': nonce
            })

            approve_args = [address_to_approve, 2 ** 256 - 1]

            approve_tx = self.token_contract.functions.approve(*approve_args)
            builded_approve = approve_tx.build_transaction(tx_data)

            status = self.sign_and_send_tx(builded_approve)

            return nonce + 1
        
        print("Allowance confrimed!")

        return None

    def sign_and_send_tx(self, builded_tx):
        signed_tx = self.w3.eth.account.sign_transaction(builded_tx, self.acc.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

        time.sleep(8)

        tx_status = utils.check_tx_status(tx_hash)
        return tx_status

    def swap_to_token(self, amount):
        pass

    def swap_to_eth(self, amount):
        pass
