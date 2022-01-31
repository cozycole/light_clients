from typing import *
from hashlib import sha1
from ecdsa import SigningKey, VerifyingKey, NIST192p
import time
import json


# UTXO set will be a hash map for quick retreival. (tx_id, UTXO)
class UTXO:
    # This is what will be used as the message for ECDSA signature (where self.sig == "").
    def __init__(self, value, pubkey) -> None:
        self.val = value
        self.pub_key = pubkey
        self.id = None # set after the initial hash of tx
        self.sig = ""

    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)

    def set_sig(self, sig):
        self.sig = sig

    def set_tx_id(self, tx_hash, index):
        self.id = (tx_hash, index)

    def sign_utxo(self, priv_key):
        """ priv_key must be a SigningKey object"""
        if type(priv_key) == str:
            priv_key = SigningKey.from_string(bytearray.fromhex(priv_key))
        message = self.to_json().encode()
        sig = priv_key.sign(message)
        self.sig = sig.hex()

    def get_message(self):
        """ Returns the same UTXO where self.sig is "" in order to get the message data. The message 
        is what is used to generate the signature in which a user is trying to verify."""
        return UTXO(self.val, self.pub_key, self.id)
        

class Transaction:
    # No tx fees
    def __init__(self, vin: List[UTXO], vout: List[UTXO]) -> None:
        self.tx_id = None
        self.vin = vin
        self.vout = vout
    
    def set_tx_id(self):
        self.tx_id = sha1(json.dumps(self, indent = 4, default=lambda o: o.__dict__).encode()).hexdigest()
        return self


class Block:
    # Creates a new block that is ready for the mining process.
    def __init__(self, prev_block, txs: List[Transaction], height) -> None:
        self.block_hash = None
        self.prev_block = prev_block 
        self.txs = txs
        self.height = height
        self.timestamp = int(time.time())
        self.nonce = 0
    
    def set_block_hash(self, prev_hash):
        self.block_hash = prev_hash

    def set_nonce(self, nonce):
        self.nonce = nonce

    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)


class Blockchain:
    def __init__(self, coinbase: int, difficulty: int) -> None:
        self.coinbase = coinbase # reward transaction to miner
        self.difficulty = difficulty
        self.chain = [] # a list of json objects (strings)
        self.height = 0 #height discounts the genesis block
        self.head = None

    def add_block(self, block: Block):
        """
        Adds a block to the blockchain based on the given block's
        previous hash (at this point the block has been validated).
        """
        set_utxo_txid(block.txs)
        self.chain.append(block.to_json())
        if block.prev_block is not None:
            self.height += 1
        self.head = block

def set_utxo_txid(tx_list: List[Transaction]):
    # updates each utxo with the tx_id and index
    for tx in tx_list:
        for i in range(len(tx.vout)):
            tx.vout[i].set_tx_id(tx.tx_id, i)

