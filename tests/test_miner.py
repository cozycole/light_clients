import unittest
import time
import sys
sys.path.insert(1, "/Users/colet/pyth_blockchain/src")
import miner
import blockchain_structs as bs
from hashlib import sha1
"""
This file tests functions of a miner.
This includes finding block solutions and verifying/routing blocks and txs.

### Change the sys.path to wherever the src directoy is stored on your system ###

Run: python -m unittest tests/test_miner.py
"""

class TestBlockMine(unittest.TestCase):
    # creates empty block and finds pow 
    def create_mine(difficulty):
        mine_block = bs.Block(None, [], 0)
        start = time.time()
        solution = miner.find_pow(mine_block, difficulty)
        end = time.time()
        print(f"Solution found in {end - start}s")
        return solution
    # find and validate a proof of work
    def test_mine_valid_block(self):
        solution = TestBlockMine.create_mine(0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        self.assertGreater(0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, int(sha1(solution.to_json().encode()).hexdigest(), 16))
    
    # check an invalid pow of work (lower difficulty)
    def test_mine_invalid_block(self):
        solution = TestBlockMine.create_mine(0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        self.assertGreater(int(sha1(solution.to_json().encode()).hexdigest(), 16), 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)


if __name__ == "__main__":
    unittest.main()