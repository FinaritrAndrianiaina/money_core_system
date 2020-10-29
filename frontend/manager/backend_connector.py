import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import (padding, rsa, utils)
from json import loads,dumps

import binascii
import hashlib

BACKEND_LINK = 'http://localhost:5000'


def create_new_adress():
    try:
        response = requests.api.get(BACKEND_LINK+'/new/account')
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None
def get_address(token):
    response = requests.api.get(BACKEND_LINK+'/get/account',params={'token':token})
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_key(token):
    response = requests.api.get(BACKEND_LINK+'/get_key/',params={"token":token})
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_list(token):
    response = requests.api.get(
        BACKEND_LINK+'/transactions/list', params={"token": token})
    if response.status_code == 200:
        return response.json()
    else:
        return None


def new_transaction(token,receiver_token,amount,priv_key):
    key = get_key(token)['message']
    prehashed_msg = hashlib.sha256(str(receiver_token + key).encode('utf-8')).digest()
    private_key = serialization.load_der_private_key(
        binascii.a2b_base64(priv_key),
        password=None,
        backend=default_backend()
    )
    signature = private_key.sign(
        prehashed_msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        utils.Prehashed(hashes.SHA256()),
    )
    transaction = {
        "signature": binascii.b2a_base64(signature).decode('utf-8'),
        "receiver_token": receiver_token,
        "sender_token": token,
        "amount": amount
    }
    response = requests.api.post(BACKEND_LINK+'/new/transaction',data=dumps(transaction))
    return response.json()  
