import time
import json
import random
from web3 import Web3

from baseoperator import BaseOperator
from config import * 
import utils

class txBridge(BaseOperator):

    def __init__(self, acc, gas_for_execute=0.2):
        super().__init__(
            name='txBridge',
            acc=acc,
            gas_for_execute=gas_for_execute
        )
        
        self.w3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC))
        self.contract = self.get_contract(ZKSYNC_BRIDGE_CONTRACT, ZKSYNC_BRIDGE_ABI)

        self.mainnet_flag = True

    def get_tx_data(self):
        tx_data = {
            "chainId": self.w3.eth.chain_id,
            "from": self.acc.address,
            "gasPrice": self.w3.eth.gas_price,
            "gas": ZKSYNC_BRIDGE_GAS_LIMIT
        }

        return tx_data

    def bridge_to_zksync(self):
        self.check_eth_gas(12)

        balance = self.get_eth_balance()
        amount = balance - int(Web3.to_wei(15 * ZKSYNC_BRIDGE_GAS_LIMIT, 'gwei') * (1 + 0.5 * random.random()))

        zk_gas_limit = random.randint(700000, 900000)
        base_cost = self.contract.functions.l2TransactionBaseCost(self.w3.eth.gas_price, zk_gas_limit, 800).call()

        bridge_amount = amount - base_cost
        bridge_amount_in_ether = Web3.from_wei(bridge_amount, 'ether')

        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx = self.contract.functions.requestL2Transaction(
            self.acc.address,
            bridge_amount,
            "0x",
            zk_gas_limit,
            800,
            [],
            self.acc.address
        )

        tx_data = self.get_tx_data()
        tx_data.update({
            "value": amount,
            "nonce": nonce
        })

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status, bridge_amount_in_ether
