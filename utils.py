from web3 import Web3
import json
import time
from config import *
import requests

def get_readable_time(t=None):
    if t == None:
        t = time.time()
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

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

def get_eth_mainnet_gas_price():
    attempt = 0

    while attempt < 3:
        try:
            w3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC))
            gas_price = w3.eth.gas_price
            gas_price_in_gwei = w3.from_wei(gas_price, 'gwei')

            return float(gas_price_in_gwei)

        except:
            time.sleep(3)
            attempt += 1
  
    raise Exception('Getting ETH mainnet gas price error')
