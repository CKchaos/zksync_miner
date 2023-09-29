import time
import json
from web3 import Web3
from eth_abi import encode

from config import * 
import utils

class SyncSwap:
    name = 'SyncSwap'

    def __init__(self, acc, swap_token, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        self.router_abi = utils.load_abi(SYNCSWAP_ROUTER_ABI)
        self.w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))
        self.acc = acc

        self.swap_token = swap_token
        token_abi = utils.load_abi(ERC20_ABI)
        self.token_contract = self.w3.eth.contract(ZKSYNC_TOKENS[self.swap_token], abi=token_abi)

        eth_market_price = utils.crypto_to_usd('ETH')
        self.gas_for_approve = utils.usd_to_zk_gas(gas_for_approve, eth_market_price)
        self.gas_for_swap = utils.usd_to_zk_gas(gas_for_swap, eth_market_price)
        self.mink = (100 - slippage) * 0.01

    def prepare_data_for_swap(self, address, token_addr):
        withdraw_mode = 1

        swap_data = encode(['address', 'address', 'uint8'], [token_addr, address, withdraw_mode])

        return swap_data

    # TODO: modify for any token
    def get_pool_eth_price(self):
        pool_abi = utils.load_abi(SYNCSWAP_POOL_ABI)
        pool = self.w3.eth.contract(address=ZK_SYNCSWAP_WETH_USDC_POOL_ADDR, abi=pool_abi)
        reserves = pool.functions.getReserves().call()
        pool_fee = pool.functions.getProtocolFee().call()

        [reserves_usdc, reserves_eth] = reserves

        reserves_usdc /= 1e6 
        reserves_eth /= 1e18
        pool_fee /= 1e7 

        eth_price_swap_to_usdc = reserves_usdc / reserves_eth * (1 - pool_fee)
        eth_price_swap_to_eth = reserves_usdc / reserves_eth * (1 + pool_fee)

        return (eth_price_swap_to_usdc, eth_price_swap_to_eth)

    def check_token_approval(self, address_to_approve, ammount_in_wei):
        allowance_args = [self.acc.address, address_to_approve]
        allowance_in_wei = self.token_contract.functions.allowance(*allowance_args).call()

        if allowance_in_wei < ammount_in_wei:
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

            return status

    def sign_and_send_tx(self, builded_tx):
        signed_tx = self.w3.eth.account.sign_transaction(builded_tx, self.acc.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

        time.sleep(6)

        tx_status = utils.check_tx_status(tx_hash)
        return tx_status

    # TODO: modify decimals for any token
    def swap_to_token(self, amount_in_ether):
        amount = Web3.to_wei(amount_in_ether, 'ether')
        pool_eth_price, _ = self.get_pool_eth_price()
        min_amount_received = int(self.mink * pool_eth_price * amount_in_ether * 1e6)
        nonce = self.w3.eth.get_transaction_count(self.acc.address)
        router = self.w3.eth.contract(ZK_SYNCSWAP_CONTRACTS['router'], abi=self.router_abi)

        deadline = int(time.time() + 12000)
        args = [[([(ZK_SYNCSWAP_WETH_USDC_POOL_ADDR, self.prepare_data_for_swap(self.acc.address, ZKSYNC_TOKENS['ETH']),
                    ZERO_ADDRESS,
                    b'')],
                  ZERO_ADDRESS,
                  amount)],
                min_amount_received,
                deadline]

        tx_data = utils.get_zksync_tx_init_data()
        tx_data.update({
            'from': self.acc.address,
            'value': amount,
            'gas': self.gas_for_swap,
            'nonce': nonce
        })

        tx = router.functions.swap(*args)
        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    # TODO: modify decimals for any token
    def swap_to_eth(self, ammount_in_token):
        amount = int(ammount_in_token * 1e6)
        _, pool_eth_price = self.get_pool_eth_price()
        min_amount_received = int(self.mink * ammount_in_token / pool_eth_price * 1e18)
        nonce = self.w3.eth.get_transaction_count(self.acc.address)
        router = self.w3.eth.contract(ZK_SYNCSWAP_CONTRACTS['router'], abi=self.router_abi)
        
        self.check_token_approval(ZK_SYNCSWAP_CONTRACTS['router'], amount)

        deadline = int(time.time() + 12000)
        args = [[([(ZK_SYNCSWAP_WETH_USDC_POOL_ADDR, self.prepare_data_for_swap(self.acc.address, ZKSYNC_TOKENS['USDC']),
                    ZERO_ADDRESS,
                    b'')],
                  ZKSYNC_TOKENS['USDC'],
                  amount)],
                min_amount_received,
                deadline]

        tx_data = utils.get_zksync_tx_init_data()
        tx_data.update({
            'from': self.acc.address,
            'value': 0,
            'gas': self.gas_for_swap,
            'nonce': nonce
        })

        tx = router.functions.swap(*args)
        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status
