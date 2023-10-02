import time
import json
import random
from web3 import Web3
from eth_abi import encode

from baseoperator import BaseOperator
from config import * 
import utils

class ZNS(BaseOperator):

    def __init__(self, acc, gas_for_execute=0.4):
        super().__init__(
            name='ZNS',
            acc=acc,
            gas_for_execute=gas_for_execute
        )

        self.gas_for_set_domain = int(self.gas_for_execute * (0.5 + 0.15 * random.random()))

        self.register_contract = self.get_contract(ZK_ZNS_CONTRACTs["register"], ZNS_REGISTER_ABI)
        self.manager_contract = self.get_contract(ZK_ZNS_CONTRACTs["manager"], ZNS_MANAGER_ABI)

        self.vocab = self.get_vocab()

        self.compound_attempt_times = 10

    def get_vocab(self):
        with open(ZNS_VOCAB_PATH, 'r') as f:
            lines = f.readlines()

        vocab = {}
        v_lens = (3, 8)
        for i in range(v_lens[0], v_lens[1] + 1):
            vocab[i] = []

        for l in lines:
            w = l.strip('\n').lower() 
            w_len = len(w)
            if w_len in vocab:
                vocab[w_len].append(w)

        return vocab

    def get_random_name(self):
        while(True):
            domain_name = "".join(random.sample([chr(i) for i in range(97, 123)], random.randint(7, 10))) + str(random.randint(0,1000))

            check_name = self.register_contract.functions.available(domain_name).call()

            if check_name:
                return domain_name

    def get_compound_name(self):
        for i in range(self.compound_attempt_times):
            length = random.randint(8, 11)
            first = random.randint(3, int(length / 2))
            second = length - first

            domain_name = random.choice(self.vocab[first]) + random.choice(self.vocab[second])
            digit_num = random.randint(0, 3)
            digit = '' if digit_num == 0 else str(random.randint(1, 10 ** digit_num - 1))

            domain_name = domain_name + digit

            check_name = self.register_contract.functions.available(domain_name).call()

            if check_name:
                return domain_name

        self.get_random_name()

    def get_primary_domain_id(self):
        domain_id = self.manager_contract.functions.getPrimaryDomainId(self.acc.address).call()

        return domain_id

    def get_owned_domains(self):
        output = self.manager_contract.functions.getOwnedDomains(self.acc.address).call()

        return output[0]

    def mint(self):
        domain_name = self.get_compound_name()

        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': 0,
            'gas': self.gas_for_execute,
            'nonce': nonce
        })

        print(f"Sending transaction to mint {domain_name}.zks ...")
        tx = self.register_contract.functions.register(domain_name, self.acc.address, 1)

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

    def set_new_primary_domain(self):
        domains = self.get_owned_domains()
        primary = self.get_primary_domain_id()

        new_primary = None
        for domain_id in domains:
            if primary != domain_id:
                new_primary = domain_id
        
        if new_primary == None:
            print("This account does not have an available domain to be a new primary domain.")
            return

        nonce = self.w3.eth.get_transaction_count(self.acc.address)

        tx_data = self.get_init_tx_data()
        tx_data.update({
            'value': 0,
            'gas': self.gas_for_set_domain,
            'nonce': nonce
        })

        tx = self.manager_contract.functions.setPrimaryDomain(new_primary)

        builded_tx = tx.build_transaction(tx_data)

        status = self.sign_and_send_tx(builded_tx)

        return status

