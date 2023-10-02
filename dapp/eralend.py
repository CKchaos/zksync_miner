import time
import json
from web3 import Web3
from eth_abi import encode

from baseoperator import BaseOperator
from config import * 
import utils

class EraLend(BaseOperator):

    def __init__(self, acc, gas_for_approve = 0.25, gas_for_execute=0.4):
        super().__init__(
            name='EraLend',
            acc=acc,
            gas_for_approve=gas_for_approve,
            gas_for_execute=gas_for_execute
        )

        self.deposit_contracts = {
            'ETH': self.get_contract(ZK_ERALEND_CONTRACTS["eETH"], ERALEND_ABI),
            'USDC': self.get_contract(ZK_ERALEND_CONTRACTS["eUSDC"], ERALEND_ABI)
        } 
        self.collateral_contract = self.get_contract(ZK_ERALEND_CONTRACTS["unitroller"], ERALEND_ABI)

        self.withdrawal_minimum = {
            'ETH': 100000000000000,
            'USDC': 300000
        }

    def get_deposit_amount(self, token):
        assert token in ['ETH', 'USDC']
        amount = self.deposit_contracts[token].functions.balanceOfUnderlying(self.acc.address).call()

        return amount

    def deposit(self, token, amount):
        assert token in ['ETH', 'USDC']

        nonce = None

        if token == 'ETH':
            data = '0x1249c58b'
        else:
            amount_str = Web3.to_hex(amount)[2:].zfill(64)
            data = '0xa0712d68' + amount_str

            nonce = self.check_token_approval(self.deposit_contracts['USDC'].address, amount, 'USDC')

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': amount if token == 'ETH' else 0,
            'to': self.deposit_contracts[token].address,
            'gas': self.gas_for_execute,
            'nonce': nonce,
            'data': data
        })

        status = self.sign_and_send_tx(tx_data)

        return status

    def withdraw(self, token):
        assert token in ['ETH', 'USDC']

        amount = self.get_deposit_amount(token)

        if amount > self.withdrawal_minimum[token]:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

            tx_data = self.get_init_tx_data()
            tx_data.update({
                'value': 0,
                'gas': self.gas_for_execute,
                'nonce': nonce
            })

            tx = self.deposit_contracts[token].functions.redeemUnderlying(amount)

            builded_tx = tx.build_transaction(tx_data)

            status = self.sign_and_send_tx(builded_tx)

            return status

    def enable_collateral(self, token):
        assert token in ['ETH', 'USDC']
        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': 0,
            'gas': self.gas_for_execute,
            'nonce': nonce
        })

        tx = self.collateral_contract.functions.enterMarkets(
            [self.deposit_contracts[token].address]
        )

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def disable_collateral(self, token):
        assert token in ['ETH', 'USDC']
        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': 0,
            'gas': self.gas_for_execute,
            'nonce': nonce
        })

        tx = self.collateral_contract.functions.exitMarket(
            self.deposit_contracts[token].address
        )

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status