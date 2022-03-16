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

class SPV:
    def __init__(self, fullnode, blockheaders):
        self.fullnode = fullnode  # instance of fullnode object
        self.headers = blockheaders # all headers in the blockchain

    def verify_transaction(self, tid):
        # Calls full node to send a merkle path, and verifies the path itself
        hashed = sha1(str(tid).encode()).hexdigest()
        fullnodeinfo = self.fullnode.get_path(tid)  # returns a dictionary with a block id and all transancations
        print("\n|SPV Wallet|")
        if fullnodeinfo == None:
            # Transaction not in blockchain
            print("\tCould not find Transaction "+ str(tid) +"\n")
            return False
        print("\tRecieved path from Full Node")
        print("\tFollowing path for proof...")
        for hash in fullnodeinfo["path"]:
            # loops through all hashes in the path and hashes them together for verification
            concatenated = str(int(hashed, 16) + int(hash, 16))
            hashed = sha1(concatenated.encode()).hexdigest()
        # At this point if "hashed" == Merkle Root of a block, the transaction is verified
        if self.headers[fullnodeinfo["blockid"]]["merkle"] == hashed:
            print("\tHashed value matches stored block root,")
            print("\tTransaction {tx} verified by SPV\n".format(tx=tid))
            return True
        else:
            print("\tPath lead to incorrect root value:\n\tGiven: "+ str(hashed) + ", Actual: " + str(self.headers[fullnodeinfo["blockid"]]["merkle"]))


def simulation():
    """ The System to be run when user runs SPV.py"""
    print("\n---------------------------------------------------------------------")
    print("Simple Payment Verification Simulation")
    print("---------------------------------------------------------------------\n")
    blocklen=input("How many blocks would you like the blockchain to contain:\n$\t")
    coinbase=input("What would you like the coinbase to be:\n$\t")
    try:
        chain = generate_blockchain(int(blocklen.strip()), int(coinbase.strip()), 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    except:
        print("Could Not Read transaction")
        chain = generate_blockchain(8, 25, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    fn = FullNode(chain)
    wallet = SPV(fn, chain.headers)
    valid_transaction = chain.head.prev_block.txs[2].tx_id
    print("---------------------------------------------------------------------")
    print("Blockchain Generated,")
    print("To view a list of transactions in the blockchain, type 'l' or 'LIST'")
    print("---------------------------------------------------------------------\n")
    while(True):
        x=input('Enter Transaction to be verified by SPV, enter "HELP" for help, or "QUIT" to exit:\n$\t')
        if x == "EXIT" or x == "QUIT" or x == "q" or x == "quit":
            break
        elif x == "LIST" or x == "l":
            fn.print_blockchain_transactions()
        elif x == "STORE" or x == "s":
            fn.store_blockchain_transactions("blockchain.txt")
        elif x == "HELP" or x == "h":
            print("---------------------------------------------------------------------")
            print("\t\tSimple Payment Verification Simulation\n")
            print("This system is meant to simulate the interaction between a light client and")
            print("a full node on a client.  On startup, a blockchain is generated with your")
            print("specifications. Once the blockchain is generated, simply enter a")
            print("transaction to verify it through the SPV client.\n")
            print("To verify a transaction, enter 'l'/'LIST' and copy/paste any")
            print("transaction id")
            print("---------------------------------------------------------------------\n")
            print("Commands:")
            print("\n\t'HELP'/'h':\n\t\t- Brings up the help screen")
            print("\n\t'LIST'/'l':\n\t\t- Lists all blocks and their transaction IDs")
            print("\n\t'QUIT'/'q':\n\t\t- Closes the program")
            print("\n\t'STORE'/'s':\n\t\t-Store the blockchain in a file titled 'blockchain.txt\n'")
            print("---------------------------------------------------------------------\n")
        else:
            wallet.verify_transaction(x)
if __name__ == "__main__":
    simulation()
