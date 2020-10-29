from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import (padding, rsa, utils)
from flask import jsonify
import binascii,datetime
import pymongo
import bson
import random_generator
import pytz,hashlib

def verify(hash,sender,receiver_token):
    try:
        prehashed_msg = hashlib.sha256( str(receiver_token + sender._key_to_hash).encode('utf-8') ).digest()
        sender.public_key.verify(
            binascii.a2b_base64(hash),
            prehashed_msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )
        return True
    except InvalidSignature as _:
        return False

class DatabaseEngine:

    def __init__(self,url,database):
        self.conn = pymongo.MongoClient(url)  
        self.db = self.conn.get_database(database)
    
    def get_collection(self,collection_name):
        return self.db.get_collection(collection_name)

class Account:
    COLLECTION_NAME = 'accounts'

    def __init__(self, public_key=None, _initialAmount = 0, _token=None,key_to_hash=None):
        self.__initialAmount = _initialAmount 
        self._token = _token
        self._public_key = public_key
        self._key_to_hash = key_to_hash

    def to_dict(self):
        return {
            "token": self._token,
            "balance":self.balance,
            "key_to_hash": self._key_to_hash
        }

    @staticmethod
    def key_to_hash(db,token):
        account = Account.find_account(db, token)
        key = account._key_to_hash
        return key

    @staticmethod
    def update_key_to_hash(db,token):
        account = Account.find_account(db, token)
        account._key_to_hash = random_generator.get_random()
        db.get_collection(Account.COLLECTION_NAME).update_one({
            "_id": account.object_id,
        },
            {
            "$set": {"key_to_hash": account._key_to_hash}
        })
        return account

    @property
    def pending_transactions(self):
        return self._pending_transactions

    @pending_transactions.setter
    def pending_transactions(self,value):
        self._pending_transactions = value

    @property
    def balance(self):
        return self.__initialAmount

    @property
    def public_key(self):
        return serialization.load_der_public_key(
            binascii.a2b_base64(self._public_key),
            backend = default_backend()
        )

    @property
    def object_id(self):
        return bson.ObjectId(self._token)


    @staticmethod
    def create_account(db: DatabaseEngine, _initialAmount):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        public = public_key.public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.PKCS1)
        private = private_key.private_bytes(
            serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        
        public = binascii.b2a_base64(public).decode('utf-8')
        data = {
            "public_key": public,
            "balance": _initialAmount,
            "pending_transactions":[],
            "key_to_hash": random_generator.get_random()
        }

        collection = db.get_collection(Account.COLLECTION_NAME)
        token_ = collection.insert_one(data).inserted_id

        token = binascii.b2a_hex(token_.binary).decode('utf-8')
        
        return Account(
            _token= token,
            _initialAmount=_initialAmount,
            public_key = public,
            key_to_hash=data['key_to_hash']
        ), binascii.b2a_base64(private).decode('utf-8')

    @staticmethod
    def find_with_oid(db,oid_token):
        collection = db.get_collection(Account.COLLECTION_NAME)
        data = collection.find_one({
            "_id" : oid_token
        })
        
        token = binascii.b2a_hex(oid_token.binary).decode('utf-8')
        account = Account(_token=token)

        account._public_key = data['public_key']
        account.__initialAmount = data['balance']
        account.pending_transactions = data['pending_transactions']
        account._key_to_hash = data['key_to_hash']
        return account

    @staticmethod
    def find_account(db:DatabaseEngine,token):
        account = Account(_token=token)
        
        collection = db.get_collection(Account.COLLECTION_NAME)
        data = collection.find_one({
            "_id": account.object_id
        })
        account._public_key = data['public_key']
        account.__initialAmount = data['balance']
        account.pending_transactions = data['pending_transactions']
        account._key_to_hash = data['key_to_hash']
        return account

class Transaction:
    @staticmethod
    def do_transacion(db: DatabaseEngine, sender_token, receiver_token, hash, amount):
        try:
            sender = Account.find_account(db,sender_token)
            receiver = Account.find_account(db,receiver_token)
        except:
            return {
                "message": "unable to reach these token"
            }
        if (not sender) and (not receiver):
            return {
                "message": "unable to reach these token"
            }

        transaction = db.get_collection('transactions')
        account_ = db.get_collection('accounts')
        if verify(hash,sender,receiver_token) and (sender.balance >= amount) and (amount>0):
            #sender.public_key.verify
            _transaction = {
                "sender_token": sender.object_id,
                "receiver_token": receiver.object_id,
                "timestamp": datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                "timecommited": None,
                "amount": bson.Int64(amount),
                "status":"initial"
            }
            Account.update_key_to_hash(db,sender_token)
            _transaction_id = transaction.insert_one(_transaction).inserted_id
            account_.update_one({"_id":_transaction['sender_token']},
                {
                    "$push": {"pending_transactions": _transaction_id}
                }
            )
            account_.update_one({"_id":_transaction['receiver_token']},
                {
                    "$push": {"pending_transactions": _transaction_id}
                }
            )
            return {
                "message": "transaction begin"
            }
        return {
            "message": "invalid transaction"
        }


from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
def sign(message,data,private_key):
    return private_key.sign(b'okbonjour',padding.PKCS1v15(),hashes.MD5())
