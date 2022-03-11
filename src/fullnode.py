"""
Quinn Fetrow
02/10/2022

Limited functionality full node, to be communicated with by the 
light client (wallet.py)

Holds the current blockchain as well as a method to verify transactions

"""
import blockchain_structs as bs
from merkle import MerkleTree


class FullNode:
    def __init__(self, blockchain: bs.Blockchain) -> None:
        self.blockchain = blockchain
    
    def get_path(self, transaction: bs.Transaction):
        # Returns a dictionary with key pairs,
        # "blockid" : blockid
        # "path" : [List of hashes to hash together for verification]
        curblock = self.blockchain.head
        while curblock != None:
            # Moving backwards through the blockchain
            if transaction in curblock.txs:
                mtree = MerkleTree()
                for tx in curblock.txs:
                    mtree.addNode(tx)  # Fill the merkle tree
                mtree.initialize()
                return {
                        "blockid": curblock.height,
                        "path" : mtree.get_path(transaction)
                        }
            curblock = curblock.prev_block

    def get_nipopow_proof():
        pass