from math import dist
import typing
import blockchain_structs
import copy
import miner

class Interlink:
    """
    Needs to be a new data struct included in blocks that has pointers to all level
    chains in varying level superblock chains

    id => hash of block
    id <= difficulty in order to be valid PoW
    blockchain will have n levels based on how many extra prefix zeros are in a valid id. 
    More prefix zeros == rarer hash

    We give genesis block id = 0, so has level infinity.
    Superblock chains are logarithmic in size to the level 0 chain.
    Each block needs a pointer to the last chain in every other superblock chain level (0 to n)

    There are log(n) (for a chain with n blocks) pointers per block. The interlink data struct changes per block based
    on the previous blocks level (therefore from block to block, most superblock levels stay the same)
    
    *** My implementation will simply be a list of block hashes, but it could be implemented as a merkle tree, just storing
    the merkle root, however, for the demonstration of this, storage savings is not important. The index
    of the list corresponds to the superchain level. (0 is block hash solution with at worst no extra zeros , 1 is super level 1, etc..)
    """
    def __init__(self, genesis: blockchain_structs.Block):
        self.genesis = genesis
        self.interlink = [genesis.block_hash] # will make it so genesis is last block of interlink

    def __str__(self):
        return str(self.interlink)

    def __repr__(self):
        return str(self.interlink)

    def update_interlink(self, last_block: blockchain_structs.Block, difficulty):
        """
        Update the interlink based on the previous blocks hash. Will be done each block creation.
        Copies the last block's interlink.
        """
        new_interlink = last_block.interlink.interlink.copy()
        # - 1 to exclude the genesis block at end
        num_levels = len(new_interlink) - 1 # number of superblock levels in interlink
        level = get_superblock_level(last_block, difficulty) # index of superblock
        # print(f"Num_levels:{num_levels}\nlevel index:{level}") 
        #(levels - 1) because we want the highest index not the length
        if (num_levels - 1) < level:
            new_interlink = new_interlink[:-1] # strip genesis
            # create new super_level indices 
            for i in range(level - (num_levels-1)):
                new_interlink.append(0)
            new_interlink.append(self.genesis.block_hash)
        for i in range(level + 1):
            new_interlink[i] = last_block.block_hash
        self.interlink = new_interlink
        # print(f"Block {last_block.height + 1} interlink: {self.interlink}")

def get_superblock_level(block: blockchain_structs.Block, difficulty: int):
    """ returns the difference in trailing zeros
    super block level = difference in # of trailing 0s"""
    # format 0160b keeps trailing zeros up to 160 bits
    block_hash = format(int(block.block_hash, 16), "0160b")
    difficulty = format(difficulty, "0160b")
    return (len(block_hash) - len(block_hash.lstrip('0'))) - (len(difficulty) - len(difficulty.lstrip('0')))

def output_interlinks(chain: blockchain_structs.Blockchain):
    for block in chain.chain:
        print(block.interlink)

def get_super_dist(chain: blockchain_structs.Blockchain, difficulty):
    distribution_dict = {}
    for block in chain.chain:
        level = get_superblock_level(block, difficulty)
        if level in distribution_dict:
            distribution_dict[level] += 1
        else:
            distribution_dict[level] = 1
    return distribution_dict

def verifySuffixProof(proofs):
    pass

def find_block(chain: blockchain_structs.Blockchain, hash) -> blockchain_structs.Blockchain:
    """
    I know this is not the most efficient way to do this. Indexing with a hashmap is O(1), but
    we made it a list because it facilitated proof creation. 
    """
    for block in chain.chain:
        if block.block_hash == hash:
            return block
    return False

def find_top_chain(blockchain: blockchain_structs.Blockchain, m, difficulty):
    """ Returns index of highest chain with at least m blocks"""
    assert(m >= 0)
    # get last block interlink
    block_dist = get_super_dist(blockchain, difficulty)
    last_interlink = blockchain.chain[-1].interlink
    num_sup_level = len(last_interlink.interlink) - 1
    # this works because we want to get all indices of interlink struct besides genesis
    top_chain = 0
    for i in range(num_sup_level): 
        if i in block_dist and block_dist[i] >= m:
            top_chain = i
    return top_chain

def get_superchain(blockchain: blockchain_structs.Blockchain, sb_index, difficulty):
    chain = []
    for block in blockchain.chain:
        if get_superblock_level(block, difficulty) == sb_index:
            chain.append(block)
    return chain

def suffix_proof(blockchain: blockchain_structs.Blockchain, k, m, difficulty):
    """
    Full node proof generation.
    Steps:
    -Start at genesis block
    -For each super block chain (starting highest first (most rare)) going to 0
    -remove k from end
    -take all the blocks at highest level in which m blocks exist and add to the proof (Note for the first iteration, 
        the starting block is the genesis, however this changes with each iteration)
        -change the new starting block by  starting from the last block of this new chain go back m blocks 
        (the chosen confidence level) OR however many blocks are left in the chain.
        -start the iteration again now taking all the blocks at this level.
    """
    top_chain_index = find_top_chain(blockchain, m, difficulty)
    if isinstance(top_chain_index, str):
        print("ERROR", top_chain_index)
        return
    chain = get_superchain(blockchain, top_chain_index, difficulty)
    prefix = []
    prefix.append(chain)
    print("PREFIX SUPERCHAIN:", prefix)
    # now get last m blocks (or less than m blocks exist in that super chain) from each lower level. 
    for i in range(top_chain_index - 1, -1, -1):
        sub_chain = get_superchain(blockchain, i, difficulty)
        if sub_chain is None:
            prefix.append(sub_chain)
            print(f"PREFIX LEVEL {i}:", sub_chain)
        elif len(sub_chain) >= m:
            prefix.append(sub_chain[-m:])
            print(f"PREFIX LEVEL {i}:", sub_chain[-m])
        else:
            prefix.append(sub_chain)
            print(f"PREFIX LEVEL {i}:", sub_chain)
    # simply return the last k blocks as these are waiting to be confirmed (for BTC k = 6)
    suffix = blockchain.chain[-k:]
    print("PREFIX:",prefix)
    print("SUFFIX",suffix)
    return prefix + suffix

def infix_proof():
    proof = suffix_proof() # pi and chi
    """
    for each chosen desired block (B) to be proven:
        for each block (E) in the SuffixProof():
            if depth(E) >= depth(B):
                R = followDown(E, B, depth)
                aux.append(R) # aux is the accumulation of each blocks path
    """
    pass

def follow_down(hi, lo, height):
    """
    Algorithm that produces the necessary blocks to connect a superblock to a preceeding regular block.
    Similar to a skiplist algorithm
    hi = superblock
    lo = regular block(in which I believe you are trying to find within E)
    """

    pass

def verify_infix():
    """
    Verifier demands an m-level for a proof (higher m, higher confidence, higher proof size (still log)) 
    that means that each superblock level must have at least m blocks in the chain (this prevents a bad actor
    from creating a bad proof if they get lucky and create a very rare super block)
    
    Each node sends a nipopow proof to the light client
    A proof is a chain ( a subchain of a nodes chain).
    Verification steps:
    -Check if it is a valid chain (anchored to the genesis block)
    -Check if the size of the suffix is k.
    -Compare the proof value to the previous proof (see if it has a higher proof score)
    -If all pass, this proof (chain) becomes the one you accept.
    Returns the predicate of the suffix. 

    See algo 2 in paper
    Implemented in algorithm 7 and 8 (8 incorporates goodness with m and delta)
    """
    pass

"""
GENESIS is always included in a proof.
Infix proofs are proofs that can appear anywhere iwthin the chain (except the k suffix for stability)
Ex proof: prove a tx id occured.
An infix proof is valid if:
    - it is a set of blocks in the chain that are not in the k suffix


No financial incentive for an adversary to attack the construction of these proofs. 
The only thing they could do is make the proof be more bytes (taking more of the verifiers time)
"""

if __name__ == "__main__":
    # testing
    chain = miner.generate_blockchain(20, 25, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    # output_chain(chain)
    # output_blockhashes(chain)
    output_interlinks(chain)
    print(find_top_chain(chain, 3, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF))
    print("Super Block Distribution:", get_super_dist(chain, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF))
    suffix_proof(chain, 3, 3, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)