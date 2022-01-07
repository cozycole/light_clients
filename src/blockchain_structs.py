from typing import *
from hashlib import sha1
import time


# UTXO set will be a hash map for quick retreival. (tx_id, UTXO)
class UTXO:
    # This is what will be used as the message for ECDSA signature (where self.sig == "").
    def __init__(self, value, pubkey,tx_id, index) -> None:
        self.val = value
        self.pub_key = pubkey
        self.id = (tx_id, index) # index of the vout of a tx
        self.sig = "" 

class Transaction:
    # No tx fees
    def __init__(self, vin: List[UTXO], vout: List[UTXO]) -> None:
        self.vin = vin
        self.vout = vout
        self.tx_id = None
    
class Block:
    # Creates a new block that is ready for the mining process.
    def __init__(self, prev_block, txs: List[Transaction], height) -> None:
        self.prev_block = prev_block
        self.hash = None 
        self.txs = txs
        self.height = height
        self.timestamp = int(time.time())
        self.nonce = None

    def set_nonce(self, nonce):
        self.nonce = nonce

class Mempool:
    # Mempool ordering would normally be based on tx fees but it will just be FIFO. 
    def __init__(self) -> None:
        self.pool = []
        pass

    def remove_txs(self, txs:List[Transaction]) -> None:
        """
        Removes txs from the mempool based on a block's content.
        """
        pass

    def gather_txs(self) -> List[Transaction]:
        """
        Gather valid transactions from the pool. In order for
        a collection of transactions to be valid, the same UTXO cannot
        be spent twice. This means we will need to keep account of which
        UTXOs are apart of the transaction list. After that, you can use that list
        to remove the given UTXOs from the UTXO set. 
        """
        pass

    def verify_tx(self) -> None:
        """
        Since transactions arrive in each miner's mempool
        at different times, a remove_txs could be done when certain txs
        are still arriving to that miner. This will lead to the accumlation
        of txs that are already included in a block. So you still need to check
        if the transactions are valid i.e. they aren't already in the blockchain. 
        
        The function is slightly different the the verify_tx function in miner.py since
        it this func only verifies that UTXOs are unspent. 
        """
        pass

class Blockchain:
    def __init__(self, coinbase: int, difficulty: int) -> None:
        self.coinbase = coinbase # reward transaction to miner
        self.difficulty = difficulty
        self.head = [] # List of block objects since it could be multiple blocks at one time.
        self.height = 0

    def add_block(self, block: Block):
        """
        Adds a block to the blockchain based on the given block's
        previous hash (at this point the block has been validated).
        """
        pass

    def get_long_chain(self) -> int:
        """
        This is incredibly important for block forks.
        The rule is to always build upon the longest chain,
        since it is that chain of blocks that has the most proof 
        of work on it. This method finds the hash of the the last block of
        the longest chain. This is then used by a miner to create the next block.
        """
        pass