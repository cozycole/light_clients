import nipopow
from miner import generate_blockchain
from fullnode import FullNode

class NiPoPow_Client:
    def __init__(self, fullnode: FullNode):
        self.superchain = None
        self.genesis = None
        self.fullnode = fullnode
        self.m = 3
        self.k = 3

    def print_superchain(self):
        print("Stored headers:",self.superchain)

    def set_superchain(self, superchain):
        self.superchain = superchain

    def set_genesis(self, genesis):
        self.genesis = genesis
    
    def verify_transaction(self, txn: str):
        proof = self.fullnode.get_nipopow_proof(self.k, self.m, txn)
        if not proof:
            return False
        nipopow.verify_infix(proof, self.superchain, self.k, self.genesis, txn)

if __name__ == '__main__':
    """ Simple Test implementation of the System"""
    print("\n---------------------------------------------------------------------")
    print("Non Interactive Proof of Proof of Work Client Simulation")
    print("---------------------------------------------------------------------\n")
    blocklen=input("How many blocks would you like the blockchain to contain:\n$\t")
    difficulty = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    try:
        chain = generate_blockchain(int(blocklen.strip()), 25, difficulty)
    except:
        print("Could not read block number... generating chain of 25 blocks")
        chain = generate_blockchain(25, 25, difficulty)
    fn = FullNode(chain)
    fn.set_difficulty(difficulty)
    wallet = NiPoPow_Client(fn)
    super_chain = fn.get_top_chain(wallet.m, wallet.k, difficulty)
    wallet.set_superchain(super_chain)
    wallet.set_genesis(chain.chain[0])
    print("---------------------------------------------------------------------")
    print("Blockchain Generated,")
    print("To view a list of transactions in the blockchain, type 'l' or 'LIST'")
    print("---------------------------------------------------------------------\n")
    print("NIPOPOW STORED SUPERCHAIN:", super_chain)
    print("---------------------------------------------------------------------\n")
    while(True):
        x=input('Enter Transaction to be verified by NiPoPow client, enter "HELP" for help, or "QUIT" to exit:\n$\t')
        if x == "EXIT" or x == "QUIT" or x == "q" or x == "quit":
            break
        elif x == "LIST" or x == "l":
            fn.print_blockchain_transactions()
        elif x == "STORE" or x == "s":
            fn.store_blockchain_transactions("blockchain.txt")
        elif x == "HEADER" or x == "HEADERS" or x == "HEAD":
            wallet.print_superchain()
        elif x == "HELP" or x == "h":
            print("---------------------------------------------------------------------")
            print("\t\tNiPoPow Verification Simulation\n")
            print("This system is meant to simulate the interaction between a light client and")
            print("a full node on a client.  On startup, a blockchain is generated with your")
            print("specifications. Once the blockchain is generated, simply enter a")
            print("transaction to verify it through the NiPoPow client.\n")
            print("To verify a transaction, enter 'l'/'LIST' and copy/paste any")
            print("transaction id")
            print("---------------------------------------------------------------------\n")
            print("Commands:")
            print("\n\t'HELP'/'h':\n\t\t- Brings up the help screen")
            print("\n\t'LIST'/'l':\n\t\t- Lists all blocks and their transaction IDs")
            print("\n\t'QUIT'/'q':\n\t\t- Closes the program")
            print("\n\t'STORE'/'s':\n\t\t-Store the blockchain in a file titled 'blockchain.txt\n'")
            print("\n\t'HEADER'/'head':\n\t\t- Prints stored headers within the NiPoPow Client")
            print("---------------------------------------------------------------------\n")
        else:
            wallet.verify_transaction(x.strip())