from web3 import Web3
import random
import requests
import time
import numpy as np
from datetime import datetime

from logger import logging
from config import *
import utils
from decrypt import get_decrypted_acc_info

from dapp.archiswap import ArchiSwap
from dapp.eralend import EraLend
from dapp.izumi import iZumi
from dapp.maverick import Maverick
from dapp.mute import Mute
from dapp.odos import Odos
from dapp.pancakeswap import PancakeSwap
from dapp.reactor import Reactor
from dapp.spacefi import SpaceFi
from dapp.syncswap import SyncSwap
from dapp.tevaera import Tevaera
from dapp.weth import WETH
from dapp.woofi import WooFi
from dapp.xyswap import XYSwap
from dapp.zkswap import zkSwap
from dapp.zns import ZNS

def get_operator_sets():
    swap_operator_set = {
        'iZumi': iZumi,
        'Maverick': Maverick,
        #'Mute': Mute,
        'Odos': Odos,
        'PancakeSwap': PancakeSwap,
        'SpaceFi': SpaceFi,
        'SyncSwap': SyncSwap,
        'WooFi': WooFi,
        'XYSwap': XYSwap,
        'zkSwap': zkSwap,
    }

    side_operator_set = {
        'ArchiSwap': ArchiSwap,
        'EraLend': EraLend,
        'Reactor': Reactor,
        'Tevaera': Tevaera,
        'WETH': WETH,
        'ZNS': ZNS,
    }
    
    return swap_operator_set, side_operator_set

class TaskDeployer():

    def __init__(self, epoch_time, epoch_percentage, swap_prob, usdc_prob):
        self.w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))

        account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)
        self.account_list = [a['label'] for a in account_info]
        self.account_dict = {}
        for acc_info in account_info:
            self.account_dict[acc_info['label']] = self.w3.eth.account.from_key(acc_info['private_key'])

        self.gas_for_approve = 0.24
        self.gas_for_swap=0.38
        self.slippage=0.5

        self.swap_operator_set, self.side_operator_set = get_operator_sets()
        self.swap_operator_list = list(self.swap_operator_set.keys())
        self.side_operator_list = list(self.side_operator_set.keys())

        self.swap_prob = swap_prob
        self.usdc_prob = usdc_prob

        self.change_op_probs = utils.load_json(CHANGE_OP_PROB_PATH)

        self.epoch_time = epoch_time
        self.epoch_percentage = epoch_percentage

    def get_amount(self, max_amount):
        if max_amount < ETH_SWAP_MINIMUM_IN_ETHER * 1e18:
            return 0

        swap_amount = ETH_SWAP_MINIMUM_IN_ETHER + 0.0021 * random.random()

        digit_list = [4, 5, 6, 7, 8]
        digit_num = random.choices(digit_list, weights=(4, 16, 36, 32, 12), k=1)[0]
        swap_amount = round(swap_amount, digit_num)
        swap_amount = Web3.to_wei(swap_amount, 'ether')

        if swap_amount > max_amount:
            p = 0.95 + random.random() * 0.03
            swap_amount = max_amount * p

        swap_amount = int(swap_amount)

        return swap_amount

    def get_task_candidates(self):
        candidates = []
        for acc_label in self.account_list:
            balance = self.w3.eth.get_balance(self.account_dict[acc_label].address)
            if balance > 0:
                candidates.append(acc_label)
            
        return candidates
    
    def get_candidate_nonces(self, candidates):
        nonces = []
        for label in candidates:
            nonce = self.w3.eth.get_transaction_count(self.account_dict[label].address)
            nonces.append(nonce)

        return nonces

    def get_non_active_time(self, address):
        try:
            url = f"https://block-explorer-api.mainnet.zksync.io/transactions?address={address}&limit=1&page=1"

            response = requests.get(url=url)
            if response.status_code == 200:
                data = response.json()
                timestr = data['items'][0]['receivedAt']
                last_active_time = datetime.strptime(timestr[:-5], "%Y-%m-%dT%H:%M:%S")
                delta = datetime.utcnow() - last_active_time
                non_active_time = int(delta.total_seconds())
            else:
                non_active_time = 1

            return non_active_time
        except:
            return 0

    def get_non_active_times(self, candidates):
        non_active_times = np.zeros(len(candidates))
        for i, acc_label in enumerate(candidates):
            non_active_time = self.get_non_active_time(self.account_dict[acc_label].address)
            non_active_times[i] = non_active_time

        return non_active_times
    
    def sample_task_account_idx(self, candidates, nonces, non_active_times, sample_num):
        nonces = np.array(nonces)
        acc_num = len(candidates)

        prob = np.ones(acc_num) * 2
        prob[nonces >= 100] = 0
        #prob[non_active_times > 86400 * 0.5] = 2
        prob[non_active_times > 86400 * 2] = 10
        
        non_zero_prob = np.sum(prob > 0)
        print("non_zero_prob:", non_zero_prob)

        rand_ = int(non_zero_prob * (random.random() * 0.9 + 0.1))
        if rand_ < sample_num:
            sample_num = rand_

        if sample_num == 0:
            return []

        prob = prob / np.sum(prob)

        indices = list(range(acc_num))
        task_accounts_idx = np.random.choice(indices, size=sample_num, replace=False, p=prob)

        return list(task_accounts_idx)

    def get_pending_time_list(self, epoch_time, epoch_task_num):
        total_time = int(epoch_time * (0.9 + 0.2 * random.random()))
        unit_time = int(total_time / epoch_task_num)
        rand = np.random.rand(epoch_task_num)
        
        randomlist = np.zeros(epoch_task_num)
        for i in range(epoch_task_num - 1):
            randomlist[i] = 1 - rand[i] + rand[i + 1]
        randomlist[-1] = 1 - rand[-1] + rand[0]
        
        max_idx = np.argmax(randomlist)
        min_idx = np.argmin(randomlist)
        
        randomlist[max_idx] = randomlist[max_idx] * 1.2
        randomlist[min_idx] = randomlist[min_idx] * 0.8
        
        randomlist = np.array(randomlist * unit_time, dtype='int64')

        return list(randomlist)

    def sample_operator_list(self, task_num):
        operator_list = []
        for i in range(task_num):
            if random.random() < self.swap_prob:
                operator_name = random.choice(self.swap_operator_list)
            else:
                operator_name = random.choice(self.side_operator_list)

            operator_list.append(operator_name)

        return operator_list

    def get_task_args(self, task_candidates, task_account_indices, pending_time_list, operator_list):
        task_args = []
        for i in range(len(task_account_indices)):
            args = {
                'acc_label': task_candidates[task_account_indices[i]],
                'operator_name': operator_list[i],
                'start_pengding_time': pending_time_list[i]
            }

            task_args.append(args)

        return task_args

    def get_last_tx_time(self, seconds):
        if seconds == 0:
            return 'NaN'

        day = int(seconds // 86400)
        seconds = seconds % 86400
        ds = '' if day == 0 else f'{day}d '
        s = datetime.utcfromtimestamp(seconds).strftime("%Hh %Mm")

        return ds + s

    def get_wash_pending_time(self):
        rand = random.random()
        add_time = 60 if rand < 0.1 else 0
        wash_pending_time = 5 + int(60 * random.random()) + add_time

        return wash_pending_time
    
    def print_tx_staus_info(self, acc_label, swap_status, swap_operator_name, swap_amount, from_token, to_token):
        s = "Swap %.8f %s for %s via %s " % (swap_amount, from_token, to_token, swap_operator_name)
        if swap_status:
            s = s + 'done!'
            logging.info(s)

        else:
            s = s + 'failed!'
            logging.info(s)

            logging.error(f'account **< {acc_label} >** may have got a failed transanction.')

    def deploy_side_task(self, acc_label, operator_name, start_pengding_time):
        pass

    def deploy_swap_task(self, acc_label, operator_name, start_pengding_time):
        assert operator_name in SWAP_TRADABLE_TOKENS

        swap_token = random.choice(SWAP_TRADABLE_TOKENS[operator_name])

        if random.random() < self.usdc_prob:
            swap_token = 'USDC'

        swap_mode = random.choices([(1, 0), (0, 1), (1, 1)], weights=(30, 10, 40), k=1)[0]
        
        if swap_token != 'USDC':
            swap_mode = (1, 1)

        logging.info(f'Execute {swap_token} swap via {operator_name} for account **< {acc_label} >**')
        print(f'Pending for {start_pengding_time}s ...')
        print(f'Estimated execution time: {utils.get_readable_time(time.time() + start_pengding_time)}')

        time.sleep(start_pengding_time)

        swap_operator = self.swap_operator_set[operator_name](self.account_dict[acc_label], swap_token, self.gas_for_approve, self.gas_for_swap, self.slippage)

        if swap_token == 'USDC':
            balance = swap_operator.get_token_balance()
            if balance > USDC_SWAP_MIN_LIMIT:
                swap_mode = (0, 1)
                print('Sell USDC this time ...')
            elif swap_mode[0] == 0:
                #print('No USDC, Skip.')
                #return

                swap_mode = (1, 0)
                print('Buy USDC this time ...')

        if swap_mode[0]:
            eth_balance = swap_operator.get_eth_balance()
            swap_amount = self.get_amount(eth_balance - ETH_MINIMUM_BALANCE)

            if swap_amount < Web3.to_wei(ETH_SWAP_MINIMUM_IN_ETHER, 'ether'):
                print("ETH balance is not enough to perform swap, aborted!")
                return

            swap_status = swap_operator.swap_to_token(swap_amount)
            self.print_tx_staus_info(acc_label, swap_status, swap_operator.name, swap_amount / 1e18, 'ETH', swap_operator.swap_token)
            if not swap_status:
                print("Buy swap failed, terminated!")
                return

        if swap_mode[1]:
            if swap_mode[0]:
                rand = random.random()
                print("sample_operator_rand:", rand)
                print("change_op_prob:", self.change_op_probs[acc_label])
                if rand < self.change_op_probs[acc_label]: 
                    op_name = random.choice(SWAP_TOKEN_PATHS[swap_token])
                    print('Sampled an operator:', op_name)
                    if op_name != operator_name:
                        swap_operator = self.swap_operator_set[op_name](self.account_dict[acc_label], swap_token, self.gas_for_approve, self.gas_for_swap, self.slippage)
                    
                wash_pending_time = self.get_wash_pending_time()
                print(f'Pending for {wash_pending_time}s ...')
                time.sleep(wash_pending_time)

            swap_amount = swap_operator.get_token_balance()
            swap_status = swap_operator.swap_to_eth(swap_amount)
            self.print_tx_staus_info(acc_label, swap_status, swap_operator.name, swap_amount / (10 ** swap_operator.token_decimals), swap_operator.swap_token, 'ETH')

    def deploy_task(self, acc_label, operator_name, start_pengding_time):
        if operator_name in self.swap_operator_list:
            self.deploy_swap_task(acc_label, operator_name, start_pengding_time)
        else:
            self.deploy_side_task(acc_label, operator_name, start_pengding_time)

    def run(self):
        while True:
            logging.info('New epoch!')

            logging.info('Getting task candidates ...')
            task_candidates = self.get_task_candidates()
            logging.info('Number of candidates: %d' % len(task_candidates))

            logging.info('Getting candidate nonces ...')
            nonces = self.get_candidate_nonces(task_candidates)
            nonces_np = np.array(nonces)
            logging.info('Number of all transactions: %d' % sum(nonces_np))
            logging.info('Number of accounts with >100 transactions: %d' % sum(nonces_np >= 100))

            logging.info('Getting non-active times ...')
            non_active_times = self.get_non_active_times(task_candidates)

            logging.info('Sampling task accounts and timetable ...')
            task_num = round(len(task_candidates) * self.epoch_percentage)
            task_account_indices = self.sample_task_account_idx(task_candidates, nonces, non_active_times, task_num)

            if len(task_account_indices) == 0:
                logging.info('No accounts need to assign tasks.')
                logging.info('Waiting for next epoch...')
                print(f'Pending for {self.epoch_time}s ...')
                time.sleep(self.epoch_time)
                continue
                

            task_num = len(task_account_indices)

            pending_time_list = self.get_pending_time_list(self.epoch_time, task_num)

            assert len(task_account_indices) == len(pending_time_list)
            
            logging.info('Epoch time: %s' % datetime.utcfromtimestamp(int(sum(pending_time_list))).strftime("%Hh %Mm %Ss"))
            logging.info('Epoch tasks: %d' % task_num)

            operator_list = self.sample_operator_list(task_num)

            task_args = self.get_task_args(task_candidates, task_account_indices, pending_time_list, operator_list)

            print("Task overview:")
            for i in range(task_num):
                acc_label = task_args[i]['acc_label']
                last_tx_time = self.get_last_tx_time(non_active_times[task_account_indices[i]])
                print(f"acc:{acc_label:6.6}  last_tx:{last_tx_time:10.10}  operator:{operator_list[i]:11.11}  pending_time:{pending_time_list[i]}s")

            for i in range(task_num):
                print()
                logging.info(f'Task {i + 1}/{task_num}:')
                try:
                    self.deploy_task(**task_args[i])
                except Exception as error:
                    logging.error("An error occurred:", error)
