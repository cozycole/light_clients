# Simple Payment Verification and Non-Interactive Proof of Proof-of-Work Light Clients

A basic simulation of light-client and full node interactions on the blockchain in Python for CIS 433 Computer Network Security.

## Installation

## Simulation Interaction

To run the Simple Payment Verfication Simulation, enter "python3 spv.py" in the command line. 
To run the Non-interactive Proof of Proof of Work simulation, enter "python3 nipopow.py" in the command line.
The simulations allow users to generate and interact with a blockchain by performing basic verifications of
transactions.  These simulations run on the command line and take user input to perform actions.

### SPV Commands

1. ‘HELP'/'h': Brings up the help screen
2. LIST'/'l': Lists all blocks and their transaction IDs
3. 'QUIT'/'q': Closes the program
4. 'STORE'/'s': Store the blockchain in a file titled 'blockchain.txt

### NiPoPoW Commands

1. ‘HELP'/'h': Brings up the help screen
2. LIST'/'l': Lists all blocks and their transaction IDs
3. 'QUIT'/'q': Closes the program
4. 'STORE'/'s': Store the blockchain in a file titled 'blockchain.txt
5. 'HEADER'/'head': Prints stored headers within the NiPoPow Client

## Implementation

### **miner.py**

### **fullnode.py**
Full Node is a python class that takes one argument of type Blockchain.  It holds four methods:
- **get_path(tid) -> {blockid, merkle path}:**
    - The get_path method is called by the SPV module, and searches the blockchain for a transaction with ID = tid.  If the transaction is found, calls are made to the Merkle Tree Generator module to generate a tree from all of the transactions in the block containing tid.  Full node then returns a dictionary containing the Merkle Path from the transaction to the root of the block to the SPV, as well as the id of the block.

- **print_blockchain_transactions():**
    - Called by the SPV to provide information to the user.
- **store_blockchain_transactions(filename):**
	- Stores information about the blockchain in “filename”, called by the SPV.

### **merkle.py**
The Merkle Tree Generator module is a Python Class that generates a merkle tree from an array of string values.  Nodes are added through repeated calls to the add_node() method.  Nodes have left, right, and parent values, as well as attributes that keep track of their hash value and content.  
- **addnode(nodeValue -> String)**: 
    - Appends nodeValue to self.node
- **initialize():** 
    - Duplicates any remaining nodes and calls internal method _generatetree()
- **generatetree(nodeSubSection):** 
    - This is a recursive method that generates a merkle tree from the internal array of nodes.  It checks if the length of the subsection == 2.  If this is the case, we are at the leaf nodes. The contents of subsection[0] and subsection[1] are hashed together and a node with that value is returned.  If the length of the subsection is greater than 2, the current subsection is split at the index:
    - len(subsection) - (2(log2(len(subsection))//1))//2
    - This index is chosen to balance an unbalanced tree. For example, if a tree is generated from a block with 6 transactions, it is split into the highest value of 2^n possible, i.e 4.  A new node is created with left and right values equal to the node returned from calling the function recursively on the left and right sections of the current subsection split at the index:
- **set_parents(node):** 
    - Sets the parents of each node after the tree is generated.
- **get_sibling(node) -> Node:**
	- Returns the node’s sibling.
- **get_path(node) -> [String]:**
	- Returns a path from “node” to the root of the tree.

### spv.py

#### **1.SPV Class:**
The SPV Class is a Python class that represents the SPV light client.  It holds an instance of the Full Node, which in a real cryptocurrency environment would be communicated with via a network connection. It also holds an array containing all of the headers in the blockchain.  It has one method:
- **verify_transaction(tid):**
    - The verify_transaction method simulates a query to the full node ( which would usually be performed via a network connection) to verify transaction of id: tid.  The full node returns the merkle path for that node if it is found.  The SPV module then “follows” this path by taking each value in the path and hashing it together with the hashed value of the transaction id. 
    If the resulting value is the same as the value of the merkle root at headers[blockid], the transaction is verified and the method returns true, if not the method returns false.
#### **2.Simulation()**
The simulation method is called when the user runs “spv.py” and runs a command line interface that allows users to generate and interact with a simulated blockchain by verifying transactions via the SPV method. 
