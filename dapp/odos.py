import time
import json
import requests
from web3 import Web3
from eth_abi import encode

from swapoperator import SwapOperator
from config import * 
import utils

class Odos(SwapOperator):

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.5, proxies={}):
        super().__init__(
            name='Odos',
            acc=acc,
            swap_token=swap_token,
            gas_for_approve=gas_for_approve,
            gas_for_swap=gas_for_swap,
            slippage=slippage
        )

        self.proxies = proxies

    def quote(self, from_token, to_token, amount):
        url = "https://api.odos.xyz/sor/quote/v2"

        data = {
            "chainId": ZKSYNC_CHAIN_ID,
            "inputTokens": [
                {
                    "tokenAddress": ZERO_ADDRESS if from_token == 'ETH' else ZKSYNC_TOKENS[from_token],
                    "amount": f"{amount}"
                }
            ],
            "outputTokens": [
                {
                    "tokenAddress": ZERO_ADDRESS if to_token == 'ETH' else ZKSYNC_TOKENS[to_token],
                    "proportion": 1
                }
            ],
            "slippageLimitPercent": round((1 - self.mink) * 100, 2),
            "userAddr": self.acc.address,
            "referralCode": 0,
            "compact": True
        }

        response = requests.post(
            url=url,
            headers={"Content-Type": "application/json"},
            json=data,
            proxies=self.proxies
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            logger.error(f"[{self.acc.address}] Bad Odos request")
            return False, 0

    def assemble(self, path_id):
        url = "https://api.odos.xyz/sor/assemble"

        data = {
            "userAddr": self.acc.address,
            "pathId": path_id,
            "simulate": False,
        }

        response = requests.post(
            url=url,
            headers={"Content-Type": "application/json"},
            json=data,
            proxies=self.proxies
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            logger.error(f"[{self.acc.address}] Bad Odos request")
            return False, 0

    def swap(self, from_token, to_token, amount, nonce=None):
        self.check_eth_gas()

        status, quote_data = self.quote(from_token, to_token, amount)
        if not status:
            print(f'Bad Request for Odos. Swap Abort!')
            return False

        status, transaction_data = self.assemble(quote_data["pathId"])
        if not status:
            print(f'Bad Request for Odos. Swap Abort!')
            return False

        amount_out = int(transaction_data['outputTokens'][0]['amount'])
        if to_token == 'ETH' and amount_out < ETH_OUT_MIN_LIMIT:
            print(f'The balance of {from_token} is too small. Swap Abort!')

            return False

        tx = transaction_data["transaction"]
        tx['value'] = int(tx['value'])
        tx['chainId'] = ZKSYNC_CHAIN_ID

        status = self.sign_and_send_tx(tx)

        return status

    def swap_to_token(self, amount):
        status = self.swap('ETH', self.swap_token, amount)

        return status

    def swap_to_eth(self, amount):
        nonce = self.check_token_approval(ZK_ODOS_CONTRACTS['router'], amount)

        status = self.swap(self.swap_token, 'ETH', amount, nonce=nonce)

        return status
