import time
import json
from web3 import Web3
from eth_abi import encode

import config
import utils

class PancakeSwap:

    def __init__(self, acc, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        self.router_abi = utils.load_abi('PancakeSwap_router', config.PANCAKE_ROUTER_ABI)
        self.w3 = Web3(Web3.HTTPProvider(config.zksync_era_rpc))
        self.acc = acc

        eth_market_price = utils.crypto_to_usd('ETH')
        self.gas_for_approve = utils.usd_to_zk_gas(gas_for_approve, eth_market_price)
        self.gas_for_swap = utils.usd_to_zk_gas(gas_for_swap, eth_market_price)
        self.mink = (100 - slippage) * 0.01

    def get_pool_addr(self, from_token, to_token):
        factory_abi = utils.load_abi('PancakeSwap_factory', config.PANCAKE_FACTORY_ABI)
        factory = self.w3.eth.contract(address=config.ZK_PANCAKE_CONTRACTS['factory'], abi=factory_abi)

        pool_addr = factory.functions.getPool(
            Web3.to_checksum_address(config.ZKSYNC_TOKENS[from_token]),
            Web3.to_checksum_address(config.ZKSYNC_TOKENS[to_token]),
            100
        ).call()

        return pool_addr

    def get_min_amount_out(self, from_token, to_token, amount):
        quoter_abi = utils.load_abi('PancakeSwap_quoter', config.PANCAKE_QUOTER_ABI)
        quoter = self.w3.eth.contract(address=config.ZK_PANCAKE_CONTRACTS['quoter'], abi=quoter_abi)

        quoter_data = quoter.functions.quoteExactInputSingle((
            Web3.to_checksum_address(config.ZKSYNC_TOKENS[from_token]),
            Web3.to_checksum_address(config.ZKSYNC_TOKENS[to_token]),
            amount,
            100,
            0
        )).call()

        return int(quoter_data[0] * self.mink)

    def check_token_approval(self, ammount_in_token):
        approve_abi = utils.load_abi('USDC', config.erc20_abi)
        contract_approve = self.w3.eth.contract(config.zk_usdc_addr, abi=approve_abi)

        allowance_args = [Web3.to_checksum_address(self.acc.address), Web3.to_checksum_address(config.ZK_PANCAKE_CONTRACTS['router'])]
        allowance_in_wei = contract_approve.functions.allowance(*allowance_args).call()

        amount = int(ammount_in_usdc * 1e6)
        if allowance_in_wei < amount:
            nonce = self.w3.eth.get_transaction_count(self.acc.address)

            approve_args = [Web3.to_checksum_address(config.ZK_PANCAKE_CONTRACTS['router']), 2 ** 256 - 1]

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
        min_amount_received = self.get_min_amount_out('ETH', 'USDC', amount)
        nonce = self.w3.eth.get_transaction_count(self.acc.address)
        contract = self.w3.eth.contract(config.ZK_PANCAKE_CONTRACTS['router'], abi=self.router_abi)

        deadline = int(time.time() + 280)
        transaction_data = contract.encodeABI(
            fn_name="exactInputSingle",
            args=[(
                Web3.to_checksum_address(config.ZKSYNC_TOKENS['ETH']),
                Web3.to_checksum_address(config.ZKSYNC_TOKENS['USDC']),
                100,
                self.acc.address,
                amount,
                min_amount_received,
                0
            )]
        )

        tx = contract.functions.multicall(
            deadline,
            [transaction_data]
        )

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
        min_amount_received = self.get_min_amount_out('USDC', 'ETH', amount)
        nonce = self.w3.eth.get_transaction_count(self.acc.address)
        contract = self.w3.eth.contract(config.ZK_PANCAKE_CONTRACTS['router'], abi=self.router_abi)
        
        deadline = int(time.time() + 280)
        transaction_data = contract.encodeABI(
            fn_name="exactInputSingle",
            args=[(
                Web3.to_checksum_address(config.ZKSYNC_TOKENS['USDC']),
                Web3.to_checksum_address(config.ZKSYNC_TOKENS['ETH']),
                100,
                "0x0000000000000000000000000000000000000002",
                amount,
                min_amount_received,
                0
            )]
        )

        unwrap_data = contract.encodeABI(
            fn_name="unwrapWETH9",
            args=[
                min_amount_received,
                self.acc.address
            ]
        )

        tx = contract.functions.multicall(
            deadline,
            [transaction_data, unwrap_data]
        )

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
