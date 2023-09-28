#General
eth_mainnet_rpc = 'https://cloudflare-eth.com'
erc20_abi = 'abi/erc20abi.json'
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

#zkSync
zksync_era_rpc = 'https://mainnet.era.zksync.io'
zksync_chain_id = 324
zksync_base_fee = 250000000
zksync_priority_fee = 0

zk_weth_addr = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'
zk_usdc_addr = '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'

ZKSYNC_TOKENS = {
    "ETH": "0x5aea5775959fbc2557cc8789bc1bf90a239d9a91",
    "WETH": "0x5aea5775959fbc2557cc8789bc1bf90a239d9a91",
    "USDC": "0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4",
    "USDT": "0x493257fd37edb34451f62edf8d2a0c418852ba4c",
    "BUSD": "0x2039bb4116b4efc145ec4f0e2ea75012d6c0f181",
    "MATIC": "0x28a487240e4d45cff4a2980d334cc933b7483842",
    "OT": "0xd0ea21ba66b67be636de1ec4bd9696eb8c61e9aa",
    "MAV": "0x787c09494ec8bcb24dcaf8659e7d5d69979ee508",
    "WBTC": "0xbbeb516fb02a01611cbbe0453fe3c580d7281011",
}

#data
account_file_path = './data/sgl_zksync_plan_x_py'
file_password_file_path = './password'

#SyncSwap
syncswap_router_abi = 'abi/syncswap/syncswap_router_abi.json'
syncswap_classic_pool_abi = 'abi/syncswap/SyncSwapClassicPool.json'
zk_syncswap_weth_usdc_pool_addr = '0x80115c708E12eDd42E504c1cD52Aea96C547c05c'
zk_syncswap_router_addr = '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295'

#PancakeSwap
PANCAKE_FACTORY_ABI = 'abi/pancake/factory.json'
PANCAKE_POOL_ABI = 'abi/pancake/pool.json'
PANCAKE_QUOTER_ABI = 'abi/pancake/quoter.json'
PANCAKE_ROUTER_ABI = 'abi/pancake/router.json'

ZK_PANCAKE_CONTRACTS = {
    "router": "0xf8b59f3c3Ab33200ec80a8A58b2aA5F5D2a8944C",
    "factory": "0x1BB72E0CbbEA93c08f535fc7856E0338D7F7a8aB",
    "quoter": "0x3d146FcE6c1006857750cBe8aF44f76a28041CCc"
}



#Maverick
maverick_pool_abi = 'abi/maverick/maverick_pool.json'
zk_maverick_router_addr = '0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4'


