import time
import json
from web3 import Web3
from eth_abi import encode

import config
import utils

class SyncSwap:

    def __init__(self, acc, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        self.router_abi = utils.load_abi('Syncswap', config.syncswap_router_abi)
        self.w3 = Web3(Web3.HTTPProvider(config.zksync_era_rpc))
        self.acc = acc

        eth_market_price = utils.crypto_to_usd('ETH')
        self.gas_for_approve = utils.usd_to_zk_gas(gas_for_approve, eth_market_price)
        self.gas_for_swap = utils.usd_to_zk_gas(gas_for_swap, eth_market_price)
        self.mink = (100 - slippage) * 0.01

    def prepare_data_for_swap(self, address, token_addr):
        token_in_addr = config.zk_weth_addr
        withdraw_mode = 1

        swap_data = encode(['address', 'address', 'uint8'], [token_addr, address, withdraw_mode])

        return swap_data

    def get_pool_eth_price(self):
        pool_abi = utils.load_abi('USDC_WETH_POOL', config.syncswap_classic_pool_abi)
        pool = self.w3.eth.contract(address=config.zk_weth_usdc_pool_addr, abi=pool_abi)
        reserves = pool.functions.getReserves().call()
        pool_fee = pool.functions.getProtocolFee().call()

        [reserves_usdc, reserves_eth] = reserves

        reserves_usdc /= 1e6 
        reserves_eth /= 1e18
        pool_fee /= 1e7 

        eth_price_swap_to_usdc = reserves_usdc / reserves_eth * (1 - pool_fee)
        eth_price_swap_to_eth = reserves_usdc / reserves_eth * (1 + pool_fee)

        return (eth_price_swap_to_usdc, eth_price_swap_to_eth)

    def check_usdc_approval(self, ammount_in_usdc):
        approve_abi = utils.load_abi('USDC', config.erc20_abi)
        contract_approve = self.w3.eth.contract(config.zk_usdc_addr, abi=approve_abi)

        allowance_args = [Web3.to_checksum_address(self.acc.address), config.zk_syncswap_router_addr]
        allowance_in_wei = contract_approve.functions.allowance(*allowance_args).call()

        amount = int(ammount_in_usdc * 1e6)
        if allowance_in_wei < amount:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

            approve_args = [Web3.to_checksum_address(config.zk_syncswap_router_addr), 2 ** 256 - 1]

            approve_tx = contract_approve.functions.approve(*approve_args)
            builded_approve = approve_tx.build_transaction({
                'chainId': config.zksync_chain_id,
                'from': Web3.to_checksum_address(self.acc.address),
                'value': 0,
                'gas': self.gas_for_approve,
                'nonce': nonce,
                'maxFeePerGas': config.zksync_base_fee,
                'maxPriorityFeePerGas': config.zksync_priority_fee
            })

            signed_approve = self.w3.eth.account.sign_transaction(builded_approve, self.acc.key)
            approve_hash = self.w3.eth.send_raw_transaction(signed_approve.rawTransaction).hex()

            time.sleep(6)

            approve_status = utils.check_tx_status(approve_hash)
        
            return approve_status

    def eth_to_usdc_swap(self, amount_in_ether):
        time.sleep(1)
        amount = Web3.to_wei(amount_in_ether, 'ether')
        pool_eth_price, _ = self.get_pool_eth_price()
        min_amount_received = int(self.mink * pool_eth_price * amount_in_ether * 1e6)
        nonce = self.w3.eth.get_transaction_count(self.acc.address)
        contract = self.w3.eth.contract(config.zk_syncswap_router_addr, abi=self.router_abi)

        deadline = int(time.time() + 1800)
        args = [[([(config.zk_weth_usdc_pool_addr, self.prepare_data_for_swap(self.acc.address, config.zk_weth_addr),
                    '0x0000000000000000000000000000000000000000',
                    b'')],
                  '0x0000000000000000000000000000000000000000',
                  amount)],
                min_amount_received,
                deadline]

        tx = contract.functions.swap(*args)
        builded_tx = tx.build_transaction({
            'chainId': config.zksync_chain_id,
            'from': Web3.to_checksum_address(self.acc.address),
            'value': amount,
            'gas': self.gas_for_swap,
            'nonce': nonce,
            'maxFeePerGas': config.zksync_base_fee,
            'maxPriorityFeePerGas': config.zksync_priority_fee
        })

        signed_tx = self.w3.eth.account.sign_transaction(builded_tx, self.acc.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

        time.sleep(10)

        tx_status = utils.check_tx_status(tx_hash)
        return tx_status

    def usdc_to_eth_swap(self, ammount_in_usdc):
        time.sleep(1)
        amount = int(ammount_in_usdc * 1e6)
        _, pool_eth_price = self.get_pool_eth_price()
        min_amount_received = int(self.mink * ammount_in_usdc / pool_eth_price * 1e18)
        nonce = self.w3.eth.get_transaction_count(self.acc.address)
        contract = self.w3.eth.contract(config.zk_syncswap_router_addr, abi=self.router_abi)
        
        deadline = int(time.time() + 1800)
        args = [[([(config.zk_weth_usdc_pool_addr, self.prepare_data_for_swap(self.acc.address, config.zk_usdc_addr),
                    '0x0000000000000000000000000000000000000000',
                    b'')],
                  config.zk_usdc_addr,
                  amount)],
                min_amount_received,
                deadline]

        tx = contract.functions.swap(*args)
        builded_tx = tx.build_transaction({
            'chainId': config.zksync_chain_id,
            'from': Web3.to_checksum_address(self.acc.address),
            'value': 0,
            'gas': self.gas_for_swap,
            'nonce': nonce,
            'maxFeePerGas': config.zksync_base_fee,
            'maxPriorityFeePerGas': config.zksync_priority_fee
        })

        signed_tx = self.w3.eth.account.sign_transaction(builded_tx, self.acc.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

        time.sleep(10)

        tx_status = utils.check_tx_status(tx_hash)
        
        return tx_status
