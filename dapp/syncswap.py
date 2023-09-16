import config
import utils

import time
import json
from web3 import Web3
from eth_abi import encode

class SyncSwap:

    def __init__(self, acc, gas_for_approve = 0.25, gas_for_swap=0.4, slippage=0.3):
        self.load_abi()
        self.initWeb3()
        self.acc = acc
        self.gas_for_approve = utils.usd_to_zk_gas(gas_for_approve)
        self.gas_for_swap = utils.usd_to_zk_gas(gas_for_swap)
        self.mink = (100 - slippage) * 0.01

    def initWeb3(self):
        self.w3 = Web3(Web3.HTTPProvider(config.zksync_era_rpc))

    def load_abi(self):
        try:
            with open(config.syncswap_router_abi) as f:
                self.router_abi = json.load(f)
        except:
            print(utils.get_readable_time() + ': SyncSwap load abi Error.')
            return 'ERROR'

    def prepare_data_for_eth_to_usdc(self, address):
        token_in_addr = config.zk_weth_addr
        withdraw_mode = 1

        swap_data = encode(['address', 'address', 'uint8'], [token_in_addr, address, withdraw_mode])

        return swap_data

    def prepare_bytes_for_sync_usdc_to_eth(self,address):

        addressb = bytes.fromhex(address[2:])
        s = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003U\xdfmL\x9c05rO\xd0\xe3\x91M\xe9jZ\x83\xaa\xf4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        e = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
        con = s + addressb + e
        return con

    def approve_zk_usdc(self, acc, address):
        try:
            Aprove_abi = ''
            with open(erc20abi) as file:
                Aprove_abi = json.load(file)
            w3 = Web3(Web3.HTTPProvider("https://mainnet.era.zksync.io"))
            contract_approve = w3.eth.contract('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', abi=Aprove_abi)
            approve_args = [Web3.to_checksum_address(address),2**256-1]
            # check_token_balance(Web3.to_checksum_address(acc.address), "https://mainnet.era.zksync.io",
            #                                                 '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4')
            approve_txn = contract_approve.functions.approve(*approve_args)
            builded_approve = approve_txn.build_transaction({
                'chainId': 324,
                'from': Web3.to_checksum_address(acc.address),
                'value': Web3.to_wei(0,'ether'),
                'gas': self.gasForApprove,
                'nonce': w3.eth.get_transaction_count(acc.address),
                'maxFeePerGas': 250000000,
                'maxPriorityFeePerGas': 250000000
            })
            signed_approve = w3.eth.account.sign_transaction(builded_approve, acc.key)
            txn_hash_approve = w3.eth.send_raw_transaction(signed_approve.rawTransaction)
            txn_approve_text = txn_hash_approve.hex()
            return txn_approve_text
        except:
            print("\033[31m{}".format('Core -> Utils -> Balance -> approve_zk_usdc(asset) ERROR'))
            print("\033[0m{}".format(' '))
            return 'ERROR'

    def eth_to_usdc_swap(self, amount_in_ether):
        time.sleep(1)
        amount = Web3.to_wei(amount_in_ether, 'ether')
        min_amount_received = int(self.mink * utils.crypto_to_usd() * amount_in_ether * 1e6)
        nonce = self.w3.eth.get_transaction_count(self.acc.address)
        contract = self.w3.eth.contract(config.zk_syncswap_router_addr, abi=self.router_abi)

        deadline = int(time.time() + 1800)
        args = [[([(config.zk_weth_usdc_pool_addr, self.prepare_data_for_eth_to_usdc(self.acc.address),
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
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_text = tx_hash.hex()

        time.sleep(10)

        tx_status = utils.check_tx_status(tx_text)
        
        return tx_status

    def usdc_to_eth_swap(self,ammount_in_usdc_wei,needApprove = True):
        value = ammount_in_usdc_wei
        time.sleep(1)
        valueReceive = int(self.mink*(ammount_in_usdc_wei/crypto_to_usd())*10**12)
        # nonce = self.w3.eth.get_transaction_count(self.acc.address)
        contract = self.w3.eth.contract(self.swap_contract,abi=self.abi)

        dead_line = int(time.time() + 3600 * 3)
        args = [[([('0x80115c708E12eDd42E504c1cD52Aea96C547c05c', self.prepare_bytes_for_sync_usdc_to_eth(self.acc.address),
                    '0x0000000000000000000000000000000000000000',
                    b'')],
                  '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
                  value)],
                valueReceive,
                dead_line]
        txn = contract.functions.swap(*args)


        if needApprove:
            print(self.approve_zk_usdc(self.acc,self.swap_contract))
            time.sleep(60)

        builded_txn = txn.build_transaction({
            'chainId': 324,
            'from': Web3.to_checksum_address(self.acc.address),
            'value': Web3.to_wei(0,'ether'),
            'gas': self.gasForSwap,
            'nonce': self.w3.eth.get_transaction_count(self.acc.address),
            'maxFeePerGas': 250000000,
            'maxPriorityFeePerGas': 250000000
        })

        signed_txn = self.w3.eth.account.sign_transaction(builded_txn, self.acc.key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_text = txn_hash.hex()

        time.sleep(10)
        return check_tx_sucs(txn_text)