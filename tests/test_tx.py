import unittest
import time
import sys
import copy
from ecdsa import SigningKey, VerifyingKey, NIST192p

sys.path.insert(1, "/Users/colet/pyth_blockchain/src")
import miner
import blockchain_structs as bs
from hashlib import sha1

"""
This file tests functions regarding transactions. This means all methods/functions involving
both UTXO objects and Transaction objects
This includes finding block solutions and verifying/routing blocks and txs. 
Signatures use the NIST192p curve by default (no reason to change the curve).

### Change the sys.path to wherever the src directoy is stored on your system ###

Run: python -m unittest tests/test_tx.py

I think the best way to have the UTXO set is for it to be a dict with key: pub_key value: List[dicts representing a UTXO]
or I could implement an equality
"""

class TestUTXO(unittest.TestCase):
    chain = bs.Blockchain(25, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    # address of each wallet to send crypto to
    def initialize_utxo_set(self):
        for i in range(2):
            pass
    
    def test_signature_valid(self):
        sk = SigningKey.generate() # private key
        vk = sk.verifying_key # public key
        pub_add = vk.to_string().hex()
        message = bs.UTXO(25, pub_add, 0, 0).to_json().encode()
        signature = sk.sign(message)
        self.assertEqual(True, vk.verify(signature, message))

    def test_sig_from_UTXO(self):
        # The logic for this test will be used for verify_UTXO()
        priv_key = SigningKey.generate() # private key
        pub_key= priv_key.verifying_key # public key
        pub_str = pub_key.to_string().hex() # now in a format we can input into a UTXO object and serialize it
        a_UTXO = bs.UTXO(25, pub_str, 0, 0)
        # assuring that we have successfully decoded the key from the UTXO
        self.assertEqual(VerifyingKey.from_string(bytearray.fromhex(a_UTXO.pub_key), curve=NIST192p), pub_key)
        
        message = a_UTXO.to_json().encode()
        signature = priv_key.sign(message)
        print(bytes.hex(signature))
        a_UTXO.set_sig(bytes.hex(signature)) # This is the type of UTXO we would see in a transaction (one with a signature)
        # Now we need to verify that this UTXO can be spent (has a valid signature from the public key attributed to it)
        prove_message = a_UTXO.get_message().to_json().encode()
        verif_key = VerifyingKey.from_string(bytearray.fromhex(a_UTXO.pub_key), curve=NIST192p)
        decoded_sig = bytes.fromhex(a_UTXO.sig)
        self.assertTrue(verif_key.verify(decoded_sig, prove_message))

    def test_utxo_in_set(self):
        # this test checks if the first part of verify_UTXO works
        utxo_set = [] # Still deciding whether we should use a list, dict or database
        priv_key = SigningKey.generate() # private key
        pub_key= priv_key.verifying_key # public key
        pub_str = pub_key.to_string().hex()
        a_UTXO = bs.UTXO(25, pub_str, 0, 0)
        utxo_set.append(a_UTXO.__dict__) # THIS IS THE UTXO WE WOULD HAVE IN THE SET BEFORE SEEING A TX
        signed_UTXO = copy.copy(a_UTXO)
        message = a_UTXO.to_json().encode()
        signature = priv_key.sign(message)
        print(bytes.hex(signature))
        signed_UTXO.set_sig(bytes.hex(signature)) # THIS IS THE SIGNED UTXO WE NEED TO VERIFY IS IN THE UTXO SET (HAS A SIGNATURE THO)
        check_UTXO = signed_UTXO.get_message()
        print(f"CHECK_UTXO:{check_UTXO.__dict__} SET_UTXO:{a_UTXO.__dict__}") 
        self.assertTrue(check_UTXO.__dict__ in utxo_set) # I think problem here is that my test is editing the UTXO in the set

