from math import dist
from typing import *
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

    def update_interlink(self, last_block: blockchain_structs.Block, difficulty: int):
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
    block_num = 0
    for block in chain.chain:
        print(f"Block {block_num} interlink:",block.interlink)
        block_num += 1

def get_super_dist(chain: blockchain_structs.Blockchain, difficulty: int, k: int):
    """
    Returns a dictionary representing the distribution of blocks at varying
    superblock levels. It discounts the last k blocks since the history of these
    blocks remain to be solidified.
    """
    distribution_dict = {}
    for block in chain.chain[:-k]:
        level = get_superblock_level(block, difficulty)
        if level in distribution_dict:
            distribution_dict[level] += 1
        else:
            distribution_dict[level] = 1
    return distribution_dict

def find_block(chain: blockchain_structs.Blockchain, hash: str) -> blockchain_structs.Blockchain:
    """
    I know this is not the most efficient way to do this. Indexing with a hashmap is O(1), but
    we made it a list because it facilitated proof creation. 
    """
    for block in chain.chain:
        if block.block_hash == hash:
            return block
    return False

def find_txn_block(blockchain: blockchain_structs.Blockchain, txn_hash: str):
    for block in blockchain.chain:
        for txn in block.txs:
            if txn.tx_id == txn_hash:
                return block
    return False

def find_top_chain(blockchain: blockchain_structs.Blockchain, m: int, difficulty: int, k: int):
    """ Returns index of highest level superchain with at least m blocks"""
    assert(m >= 0)
    # get last block interlink
    # get a dictionary representing the distribution of superblock levels within a chain
    block_dist = get_super_dist(blockchain, difficulty, k)
    last_interlink = blockchain.chain[-1].interlink
    num_sup_level = len(last_interlink.interlink) - 1
    # this works because we want to get all indices of interlink struct besides genesis
    top_chain = 0
    for i in range(num_sup_level): 
        if i in block_dist and block_dist[i] >= m:
            top_chain = i
    return top_chain

def get_superchain(blockchain: List[blockchain_structs.Block], sb_index: int, difficulty: int, k: int):
    chain = []
    # -k is done to prevent adding any super blocks of the chain that are within the 
    # untouched suffix
    for block in blockchain[:-k]:
        if get_superblock_level(block, difficulty) == sb_index:
            chain.append(block)
    return chain

def get_extra_sblocks(blockchain: List[blockchain_structs.Block], m: int, k: int, difficulty: int):
    """
    accumulates all blocks higher than the main superblock chain
    these are needed in order to make a valid chain for a proof
    """
    blocks = []
    extra_levels = []
    distribution = get_super_dist(blockchain, difficulty, k)
    for key, value in distribution.items():
        if (value < m) and (key > find_top_chain(blockchain, m, difficulty, k)):
            extra_levels.append(key)
    for block in blockchain.chain[:-k]:
        if get_superblock_level(block, difficulty) in extra_levels:
            blocks.append(block)
    return blocks

def suffix_proof(blockchain: blockchain_structs.Blockchain, k: int, m: int, difficulty: int):
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
    top_chain_index = find_top_chain(blockchain, m, difficulty, k)
    if isinstance(top_chain_index, str):
        print("ERROR", top_chain_index)
        return
    chain = get_superchain(blockchain.chain, top_chain_index, difficulty, k)
    prefix = []
    prefix.append(chain)
    print("PREFIX SUPERCHAIN:", prefix)
    # now get last m blocks (or less than m blocks exist in that super chain) from each lower level. 
    for i in range(top_chain_index - 1, -1, -1):
        sub_chain = get_superchain(blockchain.chain, i, difficulty, k)
        if sub_chain is None:
            prefix.append([])
            # print(f"PREFIX LEVEL {i}:", sub_chain)
        elif len(sub_chain) >= m:
            prefix.append(sub_chain[-m:])
            # print(f"PREFIX LEVEL {i}:", sub_chain[-m:])
        else:
            prefix.append(sub_chain)
            # print(f"PREFIX LEVEL {i}:", sub_chain)
    # simply return the last k blocks as these are waiting to be confirmed (for BTC k = 6)
    suffix = blockchain.chain[-k:]
    # print("PREFIX:",prefix)
    # print("SUFFIX",suffix)
    prefix.append(suffix)
    return [prefix, get_extra_sblocks(blockchain, m, k, difficulty)]

def infix_proof(blockchain: blockchain_structs.Blockchain, k: int, m: int, difficulty: int, txn_hash: str):
    # find block with transaction
    predicate_block = find_txn_block(blockchain, txn_hash)
    if predicate_block:
        # print("BLOCK FOUND:", predicate_block)
        # find suffix proof which gives the scaffolding for the proof 
        proof_blocks = suffix_proof(blockchain, k, m, difficulty)
        chain = proof_blocks[0]
        if proof_blocks[1]:
            chain.append(proof_blocks[1])
        chain = chain_from_proof(chain)
        # print("PRE FOLLOW DOWN:", [block.height for block in chain])
        if predicate_block not in chain:
            index = 0
            for block in chain:
                if block.height > predicate_block.height:
                    chain = follow_down(blockchain, chain, predicate_block, block.height)
                    break
                index += 1
            # print("INFIX CHAIN:",chain)
            proof_blocks.append(chain)
        return proof_blocks
    else:
        print(f"No block in chain contains transaction with hash {txn_hash}")
        return False

def follow_down(blockchain: blockchain_structs.Blockchain, proof_blocks: List[blockchain_structs.Block], predicate_block: blockchain_structs.Block, index: int):
    """
    Algorithm that produces the necessary blocks to connect a superblock to a preceeding block of interest.
    """
    while True:
        if predicate_block.block_hash in blockchain.chain[index].interlink.interlink:
            break
        else:
            # find the highest next block in the interlink structure such that 
            # the block to be added doesn't go past the predicate_block
            interlink = blockchain.chain[index].interlink.interlink
            for i in range(len(interlink) - 1, -1, -1):
                block = find_block(blockchain, interlink[i])
                if block.height > predicate_block.height:
                    if block not in proof_blocks:
                        proof_blocks.append(block)
                        # print("BLOCK ADDED:", block)
                    index = block.height
                    break
    proof_blocks.append(predicate_block)
    proof_blocks.sort(key=lambda x: x.height, reverse=True)
    # print("FINAL CHAIN:",[block.height for block in proof_blocks])
    return proof_blocks

def verify_suffix(proof_blocks: List[blockchain_structs.Block], stored_superchain, k: int, genesis: blockchain_structs.Block, m: int):
    """
    Checks:
        1) Valid chain such that genesis is the same and the suffix connects to the prefix.
        2) Checks that each block within each superblock subchain of the proof connects to the stored superchain
        3) The suffix is equal to k blocks where k is a security parameter that gives enough 
        confidence againt blockchain forks. For example, for Bitcoin, k would be 6. It takes
        6 blocks chained upon a block in order for an entity (such as an exchange) to trust a transaction.
    """
    proof = proof_blocks[0]
    suffix_proof = proof[-1]
    if len(suffix_proof) < k:
        print("Verification Error: Suffix is not k blocks")
        return False
    # the first element of the list is the desired superchain
    # checks to see if their stored superchain is apart of the proof
    if proof[0] != stored_superchain:
        print("Verification Error: Discrepcancy between stored superchain and proof")
        print(f"Stored Superchain:{stored_superchain}")
        print(f"Proof top superchain:{proof[0]}")
        return False
    
    chain = proof_blocks[0]
    if proof_blocks[1]:
        chain.append(proof_blocks[1])
    chain = chain_from_proof(chain)
    return validate_chain(chain, genesis)

def validate_chain(chain: List[blockchain_structs.Block], genesis: blockchain_structs.Block):
    if chain[-1] != genesis:
        chain.append(genesis)
    print("VALIDATING CHAIN:", [block.height for block in chain])
    for i in range(len(chain)):
        # the next block in the list must be connected on some level within a given blocks interlink
        if chain[i+1].block_hash not in chain[i].interlink.interlink:
            print(f"Verification Error: Not a valid chain! interlink of block {chain[i]} has no record of block {chain[i+1]}")
            print(f"{chain[i]} interlink: {chain[i].interlink.interlink}")
            return False
        # if the blocks have a different genesis block
        if chain[i].interlink.interlink[-1] != genesis.block_hash:
            print(f"Verification Error: Block with hash {chain[i]} is not chained to genesis")
            return False
        # if at end of the list
        if chain[i+1] == genesis:
            break
    print("VALID CHAIN")
    return True

def chain_from_proof(proof: List[List[blockchain_structs.Block]]) -> List[blockchain_structs.Block]:
    """
    This function correctly orders the blocks of the prefix and suffix of a suffix proof based on block height
    Proof is of the format: 
    [[Superblocks of level n], [last m blocks of Superblock level n-1], ... [last m of Superblock level 0], [Suffix]]
    where suffix is the last k blocks, k being specified by the verifier.
    Ordering the chain makes it more straightforward for a verifier to see if it is an anchored chain or not. 
    
    Returns a list of the blocks in the prefix and suffix sorted by block height in descending order
    """
    ordered_chain = [block for subchain in proof for block in subchain]
    ordered_chain = list(set(ordered_chain)) # remove any duplicates
    ordered_chain.sort(key=lambda x: x.height, reverse=True)
    # print([block.height for block in ordered_chain])
    return ordered_chain

def verify_infix(proof: List[List[blockchain_structs.Block]], stored_superchain, k: int, genesis: blockchain_structs.Block, m: int):
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
    """
    if verify_suffix(proof[:-1], stored_superchain, k, genesis, m):
        print("Valid suffix proof")
        print("Verifying infix proof")
        if validate_chain(proof[-1], genesis):
            print("Valid Infix Proof")
            return True
        else:
            print("Verification Error: Invalid infix proof")
    return False


def output_blockhashes(blockchain, difficulty):
    for block in blockchain.chain:
        print(f"Block {block.height}: {block.block_hash} || Level {get_superblock_level(block, difficulty)}")

if __name__ == "__main__":
    # testing
    difficulty = 0x5FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    chain = miner.generate_blockchain(100, 25, difficulty)
    k = 2
    m = 3
    txn_hash = chain.chain[20].txs[0].tx_id
    output_blockhashes(chain, difficulty)
    # output_interlinks(chain)
    stored_chain = get_superchain(chain.chain, find_top_chain(chain, 3, difficulty, k), difficulty, k)
    print("Super Block Distribution:", get_super_dist(chain, difficulty, k))
    proof = infix_proof(chain, k, m, difficulty, txn_hash)
    # verify_suffix(proof, stored_chain, k, chain.chain[0])
    if verify_infix(proof, stored_chain, k, chain.chain[0], m):
        print(f"VALID PROOF. TXN {txn_hash} exists!")