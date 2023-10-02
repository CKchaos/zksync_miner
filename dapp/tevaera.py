import time
import json
import random
from web3 import Web3
from eth_abi import encode

from baseoperator import BaseOperator
from config import * 
import utils

class Tevaera(BaseOperator):

    def __init__(self, acc, gas_for_execute=0.55):
        super().__init__(
            name='Tevaera',
            acc=acc,
            gas_for_execute=gas_for_execute
        )

        self.gas_for_mint_nft = int(self.gas_for_execute * (0.99 + random.random() * 0.02))

        self.id_contract = self.get_contract(ZK_TEVAERA_CONTRACTs["id"], TEVAERA_ID_ABI)
        self.nft_contract = self.get_contract(ZK_TEVAERA_CONTRACTs["nft"], TEVAERA_NFT_ABI)

    def mint_id(self):
        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': Web3.to_wei(0.0003, "ether"),
            'gas': self.gas_for_execute,
            'nonce': nonce
        })

        tx = self.id_contract.functions.mintCitizenId()

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def mint_nft(self):
        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': 0,
            'gas': self.gas_for_mint_nft,
            'nonce': nonce
        })

        tx = self.nft_contract.functions.mint()

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status
