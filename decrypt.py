import base64
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import config

def get_decrypted_acc_info(file_path):

    with open(file_path, 'rb') as f:
        encrypted = f.read()

    with open(config.file_password_file_path, 'r') as f:
        line = f.readline()
        password = line.rstrip('\n')
    
    password = bytes(password, 'utf-8')

    salt = b"2023516270411815"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(password))

    F = Fernet(key)

    decrypted = F.decrypt(encrypted)

    json_data = json.loads(decrypted)

    return json_data['data']
