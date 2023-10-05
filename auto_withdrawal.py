import os
import time
import random
from web3 import Web3
import numpy as np

import okx.Funding as Funding

import utils
from config import * 
from decrypt import get_decrypted_acc_info
from logger import logging

def get_account_list(start_idx):
    account_info = get_decrypted_acc_info(ACCOUNT_INFO_FILE_PATH)

    account_list = []
    for acc_info in account_info:
        label = acc_info['label']
        if label[:3] == 'sgl' and int(label[3:]) >= start_idx:
            account_list.append(
                {
                    'label': label,
                    'address': Web3.to_checksum_address(acc_info['address'])
                }
            )
    
    return account_list

def get_funding_api():
    OKX_API_PATH = 'data/okx_api_x_py'

    okx_api = get_decrypted_acc_info(OKX_API_PATH)

    api_key = okx_api["API_KEY"]
    secret_key = okx_api["API_SECRET"]
    passphrase = okx_api["API_PARAPHRASE"]

    flag = "0"

    funding_api = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)

    return funding_api

def get_pending_time_list(epoch_time, epoch_task_num):
    total_time = int(epoch_time + 18000 * random.random())
    unit_time = int(total_time / epoch_task_num)
    rand = np.random.rand(epoch_task_num)
    
    randomlist = np.zeros(epoch_task_num)
    for i in range(epoch_task_num - 1):
        randomlist[i] = 1 - rand[i] + rand[i + 1]
    randomlist[-1] = 1 - rand[-1] + rand[0]
    
    max_idx = np.argmax(randomlist)
    min_idx = np.argmin(randomlist)
    
    randomlist[max_idx] = randomlist[max_idx] * 1.1
    randomlist[min_idx] = randomlist[min_idx] * 0.85
    
    randomlist = np.array(randomlist * unit_time, dtype='int64')

    return list(randomlist)

def get_empty_accounts(account_list):
    empty_accounts = []
    w3 = Web3(Web3.HTTPProvider(ZKSYNC_ERA_RPC))
    for acc in account_list:
        lable = acc['label']
        balance = w3.eth.get_balance(acc['address'])
        if balance == 0:
            empty_accounts.append(acc)

    return empty_accounts

def get_task_accounts(empty_accounts, epoch_task_num):
    acc_num = len(empty_accounts)
    prob = np.ones(acc_num)
    half = int(acc_num / 2)
    prob[:half] *= 2
    prob = prob / np.sum(prob)
    task_accounts = np.random.choice(empty_accounts, size=epoch_task_num, replace=False, p=prob)

    return list(task_accounts)

def get_amount():
    amount = 0.008 + 0.009 * random.random()

    digit_list = [4, 5, 6, 7, 8]
    digit_num = random.choices(digit_list, weights=(10, 25, 25, 25, 15), k=1)[0]
    amount = round(amount, digit_num)

    return str(amount)

def withdrawal(funding_api, to_addr, amount):
    attempt = 0
    while attempt < 3:
        try:
            result = funding_api.get_currencies('ETH')

            withdrawal_fee = '0.001'
            for d in result['data']:
                if d['chain'] == 'ETH-zkSync Era':
                    withdrawal_fee = d['minFee']
                    break

            assert float(withdrawal_fee) < 0.0009, 'withdrawal_fee(%s) is higher than expected.' % withdrawal_fee
            print('Current withdrawal fee: ', withdrawal_fee)

            print('\nSending withdrawal request ...\n')
            rst = funding_api.withdrawal(
                ccy="ETH",
                toAddr=to_addr,
                amt=amount,
                fee=withdrawal_fee,
                dest="4",
                chain='ETH-zkSync Era'
            )

            logging.info('Withdrawal request sent.')
            print("result:", rst)

            return

        except Exception as error:
            current_time = utils.get_readable_time()
            print(f"[{current_time}] An exception occurred:", error)

            time.sleep(5)
            attempt += 1
    


if __name__ == '__main__':

    epoch_time = 76000
    epoch_task_num = 6

    start_idx = 57
    account_list = get_account_list(start_idx)

    funding_api = get_funding_api()

    while(True):
        pending_time_list = get_pending_time_list(epoch_time, epoch_task_num)

        logging.info("Getting empty accounts ...")
        empty_accounts = get_empty_accounts(account_list)
        
        empty_num = len(empty_accounts)
        logging.info(f"empty accounts: {empty_num}")

        if len(empty_accounts) < epoch_task_num:
            logging.info("Deposit task finished!")
            exit()

        task_accounts = get_task_accounts(empty_accounts, epoch_task_num)

        for i, acc in enumerate(task_accounts):
            label = acc['label']
            logging.info(f'Execute deposit for account **< {label} >**')

            amount = get_amount()

            withdrawal(funding_api, acc['address'], amount)

            print(f'\nPending for {pending_time_list[i]}s ...')
            print(f'Estimated time for next execution: {utils.get_readable_time(time.time() + pending_time_list[i])}')
            time.sleep(pending_time_list[i])





    

    

