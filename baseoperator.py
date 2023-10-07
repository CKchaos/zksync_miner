import time
import json
import random
from web3 import Web3
from eth_abi import encode

from config import * 
import utils

class BaseOperator():

    def __init__(self, name, acc, gas_for_approve = 0.25, gas_for_execute=0.35):
        self.name = name
        self.acc = acc
        
        self.w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))

        self.token_contract = None

        gas_for_approve *= 1 + random.random() * 0.2
        gas_for_execute *= 1 + random.random() * 0.1

        self.eth_market_price = utils.crypto_to_usd('ETH')
        self.gas_for_approve = utils.usd_to_zk_gas(gas_for_approve, self.eth_market_price)
        self.gas_for_execute = utils.usd_to_zk_gas(gas_for_execute, self.eth_market_price)

        self.gas_factor = 1

    def get_init_tx_data(self):
        init_tx_data = {
            'from': self.acc.address,
            'chainId': ZKSYNC_CHAIN_ID,
            'maxFeePerGas': ZKSYNC_BASE_FEE,
            'maxPriorityFeePerGas': ZKSYNC_PRIORITY_FEE
        }

        return init_tx_data

    def get_contract(self, contract_addr, abi_path):
        abi = utils.load_abi(abi_path)
        contract = self.w3.eth.contract(contract_addr, abi=abi)

        return contract

    def check_eth_gas(self):
        #print("Checking ETH mainnet gas price ...")
        while(True):
            mainnet_gas_price = utils.get_eth_mainnet_gas_price()
            #print(f'ETH gas price is {mainnet_gas_price} gwei.')
            if mainnet_gas_price > MAX_GWEI:
                print(f'ETH gas price is too high.\nPending for {GAS_RETRY_PENDING_TIME}s ...')
                time.sleep(GAS_RETRY_PENDING_TIME)
            else:
                self.gas_factor = 1 if mainnet_gas_price < TARGET_GAS_PRICE else mainnet_gas_price / TARGET_GAS_PRICE * 0.5 + 0.5

                return

    def check_token_approval(self, address_to_approve, ammount_in_wei, token='USDC'):
        print("Checking allowance ...")

        if self.token_contract == None:
            token_contract = self.get_contract(ZKSYNC_TOKENS[token], ERC20_ABI)
        else:
            token_contract = self.token_contract

        allowance_args = [self.acc.address, address_to_approve]
        allowance_in_wei = token_contract.functions.allowance(*allowance_args).call()

        if allowance_in_wei < ammount_in_wei:
            print("Perform allowance first ...")
            self.check_eth_gas()

            nonce = self.w3.eth.get_transaction_count(self.acc.address)

            tx_data = self.get_init_tx_data()
            tx_data.update({
                'value': 0,
                'gas': int(self.gas_for_approve * self.gas_factor),
                'nonce': nonce
            })

            approve_args = [address_to_approve, 2 ** 256 - 1]

            approve_tx = token_contract.functions.approve(*approve_args)
            builded_approve = approve_tx.build_transaction(tx_data)

            status = self.sign_and_send_tx(builded_approve)

            print("Allowance granted!")

            return nonce + 1
        
        print("Allowance confirmed!")

        return None

    def sign_and_send_tx(self, builded_tx):
        signed_tx = self.w3.eth.account.sign_transaction(builded_tx, self.acc.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

        time.sleep(8)

        tx_status = utils.check_tx_status(tx_hash)
        return tx_status
