from web3 import Web3
import json
import time
from config import *
import requests


def get_readable_time():
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    return time_str


def crypto_to_usd(asset = 'ETH'):
    attempt = 0
    while attempt < 3:
        try:
            url = f'https://min-api.cryptocompare.com/data/price?fsym={asset}&tsyms=USDT'
            response = requests.get(url)
            result = [response.json()]
            price = float(result[0]['USDT'])
            
            return price
            
        except:
            time.sleep(5)
            attempt += 1
        
    raise Exception(get_readable_time(), 'Getiing %s market data error.' % asset)


def check_crypto_price_range(asset, price, expected_price_range):
    price_range = expected_price_range[asset]

    if price < price_range[0] or price > price_range[1]:
        raise Exception(get_readable_time(), '%s market price (%.2f) is out of expected range.' % (asset, price))


def usd_to_zk_gas(usd, eth_market_price):
    gas_unit = int(Web3.to_wei(usd / eth_market_price, 'ether') / ZKSYNC_BASE_FEE)

    return gas_unit

def load_abi(abi_file_path):
    with open(abi_file_path) as f:
        abi = json.load(f)
        return abi

def check_tx_status(tx_hash, rpc="https://mainnet.era.zksync.io"):
    attempt = 0
    while attempt < 3:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc))
            tx = w3.eth.get_transaction_receipt(tx_hash)
            status = tx['status']
            if status == 1:
                return True
            else:
                return False
        except:
            time.sleep(3)
            attempt += 1
    
    raise Exception(get_readable_time(), 'Checking transaction status error.')


def zk_token_balance(address, rpc='https://mainnet.era.zksync.io', token_address='0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', ABI = None):
    address = Web3.to_checksum_address(address)
    token_address = Web3.to_checksum_address(token_address)

    attempt = 0
    while attempt < 3:
        try:
            if ABI == None:
                with open(ERC20_ABI) as jsonabi:
                    ABI = json.load(jsonabi)

            w3 = Web3(Web3.HTTPProvider(rpc))
            token = w3.eth.contract(address=token_address, abi=ABI)
            token_balance = token.functions.balanceOf(address).call()

            return token_balance

        except:
            time.sleep(5)
            attempt += 1

    raise Exception(get_readable_time(), 'ERC20 token (%s) balance error.' % token_address)


def zk_eth_balance(address):
    address = Web3.to_checksum_address(address)
    attempt = 0

    while attempt < 3:
        try:
            w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))
            balance = w3.eth.get_balance(address)
            return balance

        except:
            time.sleep(5)
            attempt += 1
  
    raise Exception('ZkSync Eth Balance Error')

def get_zksync_tx_init_data():
    init_tx = {
        'chainId': ZKSYNC_CHAIN_ID,
        'maxFeePerGas': ZKSYNC_BASE_FEE,
        'maxPriorityFeePerGas': ZKSYNC_PRIORITY_FEE
    }

    return init_tx

def zk_usdc_balance(address):
    address = Web3.to_checksum_address(address)
    attempt = 0

    while attempt < 3:
        try:
            w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))
            erc20_abi = load_abi(ERC20_ABI)
            contract_usdc = w3.eth.contract(ZKSYNC_TOKENS['USDC'], abi=erc20_abi)

            blance_in_wei = contract_usdc.functions.balanceOf(address).call()

            balance = blance_in_wei / 1e6

            return balance

        except:
            time.sleep(3)
            attempt += 1
  
    raise Exception('ZkSync USDC Balance Error')


def get_eth_mainnet_gas_price():
    attempt = 0

    while attempt < 3:
        try:
            w3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC))
            gas_price = w3.eth.gas_price
            gas_price_in_gwei = w3.from_wei(gas_price, 'gwei')

            return gas_price_in_gwei

        except:
            time.sleep(3)
            attempt += 1
  
    raise Exception('Getting ETH mainnet gas price error')
