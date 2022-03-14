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
    
    def get_path(self, tid: str):
        # Returns a dictionary with key pairs,
        # "blockid" : blockid
        # "path" : [List of hashes to hash together for verification]
        curblock = self.blockchain.head
        while curblock != None:
            # Moving backwards through the blockchain
            for block_transaction in curblock.txs:
                if block_transaction.tx_id == tid:
                    print("\n|Full Node|\n\tTransaction {t} found in block {b}".format(t=tid, b = curblock.height))
                    mtree = MerkleTree()
                    for tx in curblock.txs:
                        mtree.addNode(tx.tx_id)  # Fill the merkle tree
                    print("\n|Full Node|")
                    mtree.initialize()
                    mpath = mtree.get_path(tid)
                    print("\tSending merkle path: {p}".format(p=mpath))
                    return {
                            "blockid": curblock.height,
                            "path" : mpath
                            }
            curblock = curblock.prev_block

    def get_nipopow_proof():
        pass
    
    def print_blockchain_transactions(self):
        # Prints the current block chain, for use in testing systems
        curblock = self.blockchain.head
        while curblock != None:
            print("Block "+str(curblock.height)+":")
            print("\t{")
            for tx in curblock.txs:
                print("\t"+str(tx.tx_id))
            print("\t\t\t\t\t\t}")
            curblock = curblock.prev_block

    def store_blockchain_transactions(self, filename: str):
        # Writes blockchain to file at "Filename"
        curblock = self.blockchain.head
        fp = open(filename, "w")
        if not fp:
            print("Could not write to file")
            return None
        while curblock != None:
            fp.write("\nBlock "+str(curblock.height)+":\n")
            fp.write("\tTimestamp: {ts}\n".format(ts=curblock.header['timestamp']))
            fp.write("\tNonce: {nn}\n".format(nn=curblock.nonce))
            fp.write("\tMerkle Root: {mr}\n".format(mr=curblock.header['merkle']))
            fp.write("\tTransactions \n\t{\n")
            for tx in curblock.txs:
                fp.write("\t"+str(tx.tx_id)+"\n")
            fp.write("\t}\n\n")
            curblock = curblock.prev_block

