import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
                  os.path.dirname(__file__), 
                  os.pardir)
)
print(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT)

import unittest
from src.nipopow import *

class TestGoodVerification(unittest.TestCase):
    """
    Test a valid proof creation from a randomly generated blockchain
    """
    def __init__(self):
        self.difficulty = 0x5FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        num_blocks = 30
        self.chain = miner.generate_blockchain(num_blocks, 25, self.difficulty)
        # security parameters
        self.k = 2
        self.m = 3
        self.stored_chain = get_superchain(chain.chain, find_top_chain(chain, 3, difficulty, k), difficulty, k)
        output_blockhashes(chain, difficulty)
        print("Super Block Distribution:", get_super_dist(chain, difficulty, k))

    def test_suffix_verification(self):
        print("Super Block Distribution:", get_super_dist(chain, difficulty, k))
        proof = suffix_proof(self.chain, self.k, self.m, difficulty)
        self.assertTrue(verify_suffix(proof, self.stored_chain, self.k, self.chain.chain[0]))

    def test_infix_verification(self):
        """
        Checks whether it is a valid chain after blocks are added
        with the follow down function.
        """
        txn_hash = self.chain.chain[20].txs[0].tx_id
        proof = infix_proof(self.chain, self.k, self.m, self.difficulty, txn_hash)
        self.assertTrue(verify_infix(proof, self.stored_chain, self.k, self.chain.chain[0], self.m))
