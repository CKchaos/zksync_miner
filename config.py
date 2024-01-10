#General
#ETH_MAINNET_RPC = 'https://cloudflare-eth.com'
ETH_MAINNET_RPC = 'https://mainnet.infura.io/v3/32fd1d6d6c194554afaffba1f6c245b0'
ERC20_ABI = 'abi/erc20abi.json'
MAX_GWEI = 40
TARGET_GAS_PRICE = 16.5
GAS_RETRY_PENDING_TIME = 180
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ETH_OUT_MIN_LIMIT = 1200000000000000
ETH_MINIMUM_BALANCE = 1500000000000000
ETH_SWAP_MINIMUM_IN_ETHER = 0.0012
USDC_SWAP_MIN_LIMIT = 2500000
MAX_TX_CHECKING_WAIT_TIME = 20
MAX_MAINNET_TX_CHECKING_WAIT_TIME = 600

#data
ACCOUNT_INFO_FILE_PATH = './data/sgl_zksync_plan_x_py'
PASSWORD_FILE_PATH = './password'
CHANGE_OP_PROB_PATH = './data/change_op_probs.json'

#zkSync
ZKSYNC_ERA_RPC = 'https://mainnet.era.zksync.io'
ZKSYNC_CHAIN_ID = 324
ZKSYNC_BASE_FEE = 250000000
ZKSYNC_PRIORITY_FEE = 0
ZKSYNC_BRIDGE_CONTRACT = "0x32400084C286CF3E17e7B677ea9583e60a000324"
ZKSYNC_BRIDGE_ABI = "abi/txbridge/bridge.json"
ZKSYNC_BRIDGE_GAS_LIMIT = 149293

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
    'MVX': '0xC8Ac6191CDc9c7bF846AD6b52aaAA7a0757eE305',
    'OT': '0xD0eA21ba66B67bE636De1EC4bd9696EB8C61e9AA',
    'PEPE': '0xFD282F16a64c6D304aC05d1A58Da15bed0467c71',
    'PIKO': '0xf8C6dA1bbdc31Ea5F968AcE76E931685cA7F9962',
    'SIS': '0xdd9f72afED3631a6C85b5369D84875e6c42f1827',
    'SNRK': '0x533b5F887383196C6bc642f83338a69596465307',
    'SPACE': '0x47260090cE5e83454d5f05A0AbbB2C953835f777',
    'TES': '0xCab3F741Fa54e79E34753B95717b23018332b8AC',
    'USDC': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
    'USDT': '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',
    'USD+': '0x8E86e46278518EFc1C5CEd245cBA2C7e3ef11557',
    'WBTC': '0xBBeB516fb02a01611cBBE0453Fe3c580D7281011',
    'WISP': '0xc8Ec5B0627C794de0e4ea5d97AD9A556B361d243',
    'ZAT': '0x47EF4A5641992A72CFd57b9406c9D9cefEE8e0C4',
    'ZKDOGE': '0xbFB4b5616044Eded03e5b1AD75141f0D9Cb1499b',
    'ZF': '0x31C2c031fDc9d33e974f327Ab0d9883Eae06cA4A',
    'zkUSD': '0xfC7E56298657B002b3e656400E746b7212912757',
}

#WETH
WETH_ABI = 'abi/weth/abi.json'

#SyncSwap
SYNCSWAP_ROUTER_ABI = 'abi/syncswap/syncswap_router_abi.json'
SYNCSWAP_POOL_FACTORY_ABI = 'abi/syncswap/syncswap_pool_factory_abi.json'
SYNCSWAP_CLASSIC_POOL_ABI = 'abi/syncswap/SyncSwapClassicPool.json'

ZK_SYNCSWAP_CONTRACTS = {
    "router": "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295",
    "pool_factory": "0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb"
}

ZK_SYNCSWAP_TOKENS = ['BUSD', 'Cheems', 'DOGERA', 'DVF', 'ERA', 'GOVI', 'iZi', 'LUSD', 
                    'MATIC', 'MAV', 'MUTE', 'OT', 'PEPE', 'PIKO', 'SIS',
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

#Mute
MUTE_ROUTER_ABI = 'abi/mute/router.json'

ZK_MUTE_CONTRACTS = {
    "router": "0x8B791913eB07C32779a16750e3868aA8495F5964",
}

ZK_MUTE_TOKENS = ['MUTE', 'MVX', 'USDC', 'WBTC', 'WISP', 'ZKDOGE']

#SpaceFi
SPACEFI_ROUTER_ABI = 'abi/spacefi/router.json'

ZK_SPACEFI_CONTRACTS = {
    "router": "0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d"
}

ZK_SPACEFI_TOKENS = ['BUSD', 'SPACE', 'USDC', 'USDT', 'WBTC']

#zkSwap
ZKSWAP_ROUTER_ABI = 'abi/zkswap/router.json'

ZK_ZKSWAP_CONTRACTS = {
    "router": "0x18381c0f738146Fb694DE18D1106BdE2BE040Fa4"
}

ZK_ZKSWAP_TOKENS = ['BUSD', 'USDC', 'USDT', 'WBTC', 'ZF']

#iZumi
IZUMI_ROUTER_ABI = 'abi/izumi/router.json'

ZK_IZUMI_CONTRACTS = {
    "router": "0x943ac2310D9BC703d6AB5e5e76876e212100f894"
}

ZK_IZUMI_TOKENS = ['USDC']

#Maverick
MAVERICK_POSITION_ABI = 'abi/maverick/position.json'
MAVERICK_ROUTER_ABI = 'abi/maverick/router.json'

ZK_MAVERICK_CONTRACTS = {
    "router": "0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4",
    "pool_information": "0x57D47F505EdaA8Ae1eFD807A860A79A28bE06449",
}

ZK_MAVERICK_TOKENS = ['USDC', 'BUSD', 'LUSD', 'MAV']

ZK_MAVERICK_POOL_ADDRESSES = {
    'USDC': "0x41C8cf74c27554A8972d3bf3D2BD4a14D8B604AB",
    'BUSD': "0x3Ae63FB198652E294B8DE4C2EF659D95D5ff28BE",
    'LUSD': "0xB1338207DE233aE6a9A6D63309221b577F8Cd6E8",
    'MAV': "0x4D47167e66e86d1a1083f52136832d4f1eF5809A"
}

ZK_MAVERICK_POOL_TOKEN_A = {
    'USDC': 'ETH',
    'BUSD': 'ETH',
    'LUSD': 'ETH',
    'MAV': 'MAV'
}

ZK_MAVERICK_TOKEN_FACTOR = {
    'USDC': 0.9996,
    'BUSD': 0.997,
    'LUSD': 0.999,
    'MAV':  0.992
}

#Odos
ZK_ODOS_CONTRACTS = {
    "router": "0x4bBa932E9792A2b917D47830C93a9BC79320E4f7",
}

ZK_ODOS_TOKENS = ['USDC']

#XYSwap
XY_E_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

ZK_XYSWAP_CONTRACTS = {
    "router": "0x30E63157bD0bA74C814B786F6eA2ed9549507b46",
}

ZK_XYSWAP_TOKENS = ['USDC', 'USDT', 'BUSD']

#WooFi
WOOFI_ROUTER_ABI = 'abi/woofi/router.json'

ZK_WOOFI_CONTRACTS = {
    "router": "0xfd505702b37Ae9b626952Eb2DD736d9045876417"
}

WOO_E_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

ZK_WOOFI_TOKENS = ['USDC']

#Eralend
ERALEND_ABI = 'abi/eralend/abi.json'

ZK_ERALEND_CONTRACTS = {
    "eETH": "0x22D8b71599e14F20a49a397b88c1C878c86F5579",
    "eUSDC": "0x90973213E2a230227BD7CCAfB30391F4a52439ee",
    "unitroller": '0xC955d5fa053d88E7338317cc6589635cD5B2cf09'
}

#Reactor
REACTOR_ABI = 'abi/reactor/abi.json'

ZK_REACTOR_CONTRACTS = {
    "rfETH": "0xC5db68F30D21cBe0C9Eac7BE5eA83468d69297e6",
    "rfUSDC": "0x04e9Db37d8EA0760072e1aCE3F2A219988Fdac29",
    "collateral": "0x23848c28Af1C3AA7B999fA57e6b6E8599C17F3f2",
}

#ArchiSwap
ZK_ARCHISWAP_CONTRACTS = {
    "faucet": "0x4E8a60Eade9e6967d2ee5bF6aa46eEce10E9809e"
}

#ZNS
ZNS_REGISTER_ABI = 'abi/zns/register.json'
ZNS_MANAGER_ABI = 'abi/zns/manager.json'

ZK_ZNS_CONTRACTs = {
    "register": "0xCBE2093030F485adAaf5b61deb4D9cA8ADEAE509",
    "manager": "0xCc788c0495894C01F01cD328CF637c7C441Ee69E"
}

ZNS_VOCAB_PATH = "data/zns_vocab"

#Tevaera
TEVAERA_ID_ABI = 'abi/tevaera/id.json'
TEVAERA_NFT_ABI = 'abi/tevaera/nft.json'

ZK_TEVAERA_CONTRACTs = {
    "id": "0xd29Aa7bdD3cbb32557973daD995A3219D307721f",
    "nft": "0x50B2b7092bCC15fbB8ac74fE9796Cf24602897Ad"
}

#integration
SWAP_TRADABLE_TOKENS = {
    'SyncSwap': ZK_SYNCSWAP_TOKENS,
    'PancakeSwap': ZK_PANCAKE_TOKENS,
    #'Mute': ZK_MUTE_TOKENS,
    'SpaceFi': ZK_SPACEFI_TOKENS,
    'zkSwap': ZK_ZKSWAP_TOKENS,
    'iZumi': ZK_IZUMI_TOKENS,
    'Maverick': ZK_MAVERICK_TOKENS,
    'Odos': ZK_ODOS_TOKENS,
    #'XYSwap': ZK_XYSWAP_TOKENS,
    'WooFi': ZK_WOOFI_TOKENS,
}

SWAP_TOKEN_PATHS = {}
for op, tokens in SWAP_TRADABLE_TOKENS.items():
    for token in tokens:
        if token in SWAP_TOKEN_PATHS:
            SWAP_TOKEN_PATHS[token].append(op)
        else:
            SWAP_TOKEN_PATHS[token] = [op]
            
