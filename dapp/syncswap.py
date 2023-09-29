import time
import json
from web3 import Web3
from eth_abi import encode

from config import * 
import utils

class SyncSwap:
    name = 'SyncSwap'

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        self.swap_token = swap_token
        self.acc = acc
        self.w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))

        self.router_contract = self.get_contract(ZK_SYNCSWAP_CONTRACTS['router'], SYNCSWAP_ROUTER_ABI)
        self.pool_factory = self.get_contract(ZK_SYNCSWAP_CONTRACTS["pool_factory"], SYNCSWAP_POOL_FACTORY_ABI)
        self.token_contract = self.get_contract(ZKSYNC_TOKENS[self.swap_token], ERC20_ABI)

        self.pool_address = self.get_pool('ETH', self.swap_token)
        self.pool_contract = self.get_contract(self.pool_address, SYNCSWAP_CLASSIC_POOL_ABI)

        self.token_decimals = self.get_swap_token_decimals()

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

    def get_token_balance(self):
        balance = self.token_contract.functions.balanceOf(self.acc.address).call()

        return balance

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

        min_amount_out = int(amount_out *self.mink)

        return min_amount_out

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

    def swap(self, from_token, amount, nonce=None):
        min_amount_out = self.get_min_amount_out(ZKSYNC_TOKENS[from_token], amount)

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
