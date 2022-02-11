"""
Quinn Fetrow
02/10/2022

Limited functionality light client. Communicates with full node to verify transactions.

Ideally, the wallet would communicate with the full node remotely, but for the sake of complexity
it will hold an instance of the full node that it communicates with.

"""
from miner import *
from hashlib import sha1
from fullnode import *

class Wallet:
    def __init__(self, fullnode, blockheaders):
        self.fullnode = fullnode  # instance of fullnode object
        self.headers = blockheaders # all headers in the blockchain

    def verify_transaction(self, transaction):
        # Calls full node to send a merkle path, and verifies the path itself
        hashed = sha1(str(transaction).encode()).hexdigest()
        fullnodeinfo = self.fullnode.get_path(transaction)  # returns a dictionary with a block id and all transancations
        if fullnodeinfo == None:
            # Transaction not in blockchain
            print("Could not find Transaction "+ str(transaction) )
            return False
        for hash in fullnodeinfo["path"]:
            # loops through all hashes in the path and hashes them together for verification
            concatenated = str(int(hashed, 16) | int(hash, 16))
            hashed = sha1(concatenated.encode()).hexdigest()
        # At this point if "hashed" == Merkle Root of a block, the transaction is verified
        if self.headers[fullnodeinfo["blockid"]]["merkle"] == hashed:
            return True
        else:
            print("Given: "+ str(hashed) + ", Actual: " + str(self.headers[fullnodeinfo["blockid"]]["merkle"]))

if __name__ == "__main__":
    """ Simple Test implementation of the System"""
    chain = generate_blockchain(8, 25, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    fn = FullNode(chain)
    wallet = Wallet(fn, chain.headers)
    if wallet.verify_transaction("<FAKE TRANSACTION>"): # wallet finds an invalid transaction
        print("Full node is lying!")
    valid_transaction = chain.head.prev_block.txs[0]
    if wallet.verify_transaction(valid_transaction): # wallet finds a valid transaction
        print("Valid transaction: "+str(valid_transaction))

