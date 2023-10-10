import time
import json
import requests
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class XYSwap(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.5, proxies={}):
        super().__init__(
            name='XYSwap',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap * 1.5,
            slippage=slippage
        )

        self.proxies = proxies

    def quote(self, from_token, to_token, amount):
        url = "https://aggregator-api.xy.finance/v1/quote"

        params = {
            "srcChainId": ZKSYNC_CHAIN_ID,
            "srcQuoteTokenAddress": XY_E_ADDRESS if from_token == "ETH" else ZKSYNC_TOKENS[from_token],
            "srcQuoteTokenAmount": amount,
            "dstChainId": ZKSYNC_CHAIN_ID,
            "dstQuoteTokenAddress": XY_E_ADDRESS if to_token == "ETH" else ZKSYNC_TOKENS[to_token],
            "slippage": round((1 - self.mink) * 100, 2)
        }

        response = requests.get(url=url, params=params, proxies=self.proxies)
        if response.status_code == 200:
            quote_data = response.json()
            if quote_data['success']:
                return True, quote_data

        return False, 0

    def build_transaction(self, from_token, to_token, amount, swap_provider):
        url = "https://aggregator-api.xy.finance/v1/buildTx"

        params = {
            "srcChainId": ZKSYNC_CHAIN_ID,
            "srcQuoteTokenAddress": XY_E_ADDRESS if from_token == "ETH" else ZKSYNC_TOKENS[from_token],
            "srcQuoteTokenAmount": amount,
            "dstChainId": ZKSYNC_CHAIN_ID,
            "dstQuoteTokenAddress": XY_E_ADDRESS if to_token == "ETH" else ZKSYNC_TOKENS[to_token],
            "slippage": round((1 - self.mink) * 100, 2),
            "receiver": self.acc.address,
            "srcSwapProvider": swap_provider,
        }

        response = requests.get(url=url, params=params, proxies=self.proxies)
        if response.status_code == 200:
            tx_data = response.json()
            if tx_data['success']:
                return True, tx_data
        
        return False, 0

    def swap(self, from_token, to_token, amount, nonce=None):
        self.check_eth_gas()

        status, quote_data = self.quote(from_token, to_token, amount)
        if not status:
            print(f'Bad Request for XYSwap. Swap Abort!')
            return False

        status, transaction_data = self.build_transaction(
            from_token,
            to_token,
            amount,
            quote_data["routes"][0]["srcSwapDescription"]["provider"]
        )
        if not status:
            print(f'Bad Request for XYSwap. Swap Abort!')
            return False

        amount_out = int(transaction_data['route']['minReceiveAmount'])
        if to_token == 'ETH' and amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        if nonce == None:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': transaction_data['tx']['value'],
            'data': transaction_data['tx']['data'],
            'to': transaction_data['tx']['to'],
            'gas': self.get_gas_for_swap(),
            'nonce': nonce
        })

        status = self.sign_and_send_tx(tx_data)

        return status

    def swap_to_token(self, amount):
        status = self.swap('ETH', self.swap_token, amount)

        return status

    def swap_to_eth(self, amount):
        nonce = self.check_token_approval(ZK_XYSWAP_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, 'ETH', amount, nonce=nonce)

        return status
