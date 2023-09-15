from web3 import Web3
import json
import time
import config


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


def usd_to_zk_gas(usd=0.3):
    eth_price = crypto_to_usd('ETH')
    gas_unit = int(Web3.to_wei(usd / eth_price, 'ether') / config.zksync_base_fee)

    return gas_unit


def check_tx_status(tx, rpc="https://mainnet.era.zksync.io"):
    attempt = 0
    while attempt < 3:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc))
            txn = w3.eth.get_transaction_receipt(tx)
            status = txn['status']
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
                with open(config.erc20_abi) as jsonabi:
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
            w3 = Web3(Web3.HTTPProvider(config.zksync_era_rpc))
            balance = w3.eth.get_balance(address)
            return balance

        except:
            time.sleep(5)
            attempt += 1
  
    raise Exception('ZkSync Eth Balance Error')