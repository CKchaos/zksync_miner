#General
ETH_MAINNET_RPC = 'https://cloudflare-eth.com'
ERC20_ABI = 'abi/erc20abi.json'
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ETH_OUT_MIN_LIMIT = 1800000000000000
ETH_MINIMUM_BALANCE = 1000000000000000

#data
ACCOUNT_INFO_FILE_PATH = './data/sgl_zksync_plan_x_py'
PASSWORD_FILE_PATH = './password'

#zkSync
ZKSYNC_ERA_RPC = 'https://mainnet.era.zksync.io'
ZKSYNC_CHAIN_ID = 324
ZKSYNC_BASE_FEE = 250000000
ZKSYNC_PRIORITY_FEE = 0

ZKSYNC_TOKENS = {
    'ETH': '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91',
    'WETH': '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91',
    'BUSD': '0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181',
    'CAKE': '0x3A287a06c66f9E95a56327185cA2BDF5f031cEcD',
    'Cheems': '0xd599dA85F8Fc4877e61f547dFAcffe1238A7149E',
    'DOGERA': '0xA59af353E423F54D47F2Ce5F85e3e265d95282Cd',
    'DVF': '0xBbD1bA24d589C319C86519646817F2F153c9B716',
    'ERA': '0xeCD9f240ED3895c77dB676004328Dd1d246f33C9',
    'GOVI': '0xD63eF5e9C628c8a0E8984CDfb7444AEE44B09044',
    'iZi': '0x16A9494e257703797D747540f01683952547EE5b',
    'LUSD': '0x503234F203fC7Eb888EEC8513210612a43Cf6115',
    'MATIC': '0x28a487240e4D45CfF4A2980D334CC933B7483842',
    'MAV': '0x787c09494Ec8Bcb24DcAf8659E7d5D69979eE508',
    'MUTE': '0x0e97C7a0F8B2C9885C8ac9fC6136e829CbC21d42',
    'OT': '0xD0eA21ba66B67bE636De1EC4bd9696EB8C61e9AA',
    'PEPE': '0xFD282F16a64c6D304aC05d1A58Da15bed0467c71',
    'PIKO': '0xf8C6dA1bbdc31Ea5F968AcE76E931685cA7F9962',
    'rETH': '0x32Fd44bB869620C0EF993754c8a00Be67C464806',
    'SIS': '0xdd9f72afED3631a6C85b5369D84875e6c42f1827',
    'SNRK': '0x533b5F887383196C6bc642f83338a69596465307',
    'SPACE': '0x47260090cE5e83454d5f05A0AbbB2C953835f777',
    'TES': '0xCab3F741Fa54e79E34753B95717b23018332b8AC',
    'USDC': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
    'USDT': '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',
    'USD+': '0x8E86e46278518EFc1C5CEd245cBA2C7e3ef11557',
    'WBTC': '0xBBeB516fb02a01611cBBE0453Fe3c580D7281011',
    'ZAT': '0x47EF4A5641992A72CFd57b9406c9D9cefEE8e0C4',
    'ZKDOGE': '0xbFB4b5616044Eded03e5b1AD75141f0D9Cb1499b',
    'zkUSD': '0xfC7E56298657B002b3e656400E746b7212912757',
}

#SyncSwap
SYNCSWAP_ROUTER_ABI = 'abi/syncswap/syncswap_router_abi.json'
SYNCSWAP_POOL_FACTORY_ABI = 'abi/syncswap/syncswap_pool_factory_abi.json'
SYNCSWAP_CLASSIC_POOL_ABI = 'abi/syncswap/SyncSwapClassicPool.json'

ZK_SYNCSWAP_CONTRACTS = {
    "router": "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295",
    "pool_factory": "0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb"
}

ZK_SYNCSWAP_TOKENS = ['BUSD', 'Cheems', 'DOGERA', 'DVF', 'ERA', 'GOVI', 'iZi', 'LUSD', 
                    'MATIC', 'MAV', 'MUTE', 'OT', 'PEPE', 'PIKO', 'rETH', 'SIS',
                    'SNRK', 'SPACE', 'USDC', 'USDT', 'USD+', 'WBTC', 'ZAT', 'ZKDOGE', 'zkUSD']

#PancakeSwap
PANCAKE_FACTORY_ABI = 'abi/pancake/factory.json'
PANCAKE_POOL_ABI = 'abi/pancake/pool.json'
PANCAKE_QUOTER_ABI = 'abi/pancake/quoter.json'
PANCAKE_ROUTER_ABI = 'abi/pancake/router.json'

ZK_PANCAKE_CONTRACTS = {
    "router": "0xf8b59f3c3Ab33200ec80a8A58b2aA5F5D2a8944C",
    "factory": "0x1BB72E0CbbEA93c08f535fc7856E0338D7F7a8aB",
    "quoter": "0x3d146FcE6c1006857750cBe8aF44f76a28041CCc",
}

ZK_PANCAKE_TOKENS = ['BUSD', 'CAKE', 'TES', 'USDC', 'USDT', 'WBTC']

ZK_PANCAKE_POOL_FEES = {
    'BUSD': 500,
    'CAKE': 2500,
    'TES': 10000,
    'USDC': 100,
    'USDT': 500,
    'WBTC': 500,
}

#Maverick
MAVERICK_FACTORY_ABI = 'abi/maverick/maverick_pool.json'
MAVERICK_ROUTER_ABI = ''

ZK_MAVERICK_CONTRACTS = {
    "router": "0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4",
    "factory": "0x2C1a605f843A2E18b7d7772f0Ce23c236acCF7f5"
}


#integration
SWAP_TRADABLE_TOKENS = {
    'SyncSwap': ZK_SYNCSWAP_TOKENS,
    'PancakeSwap': ZK_PANCAKE_TOKENS,
}

