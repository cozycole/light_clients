import blockchain_structs
"""
a predicate (e.g. “the transaction t
is committed in the blockchain”)

Future reference:
Part 3 --> Interlink data struct, updating interlink, blockchain set notation
Part 4 --> NiPoPow proofs for k-suffix, prover and verifier algorithms,

Part 8 --> Talked about the proofs behind why they are secure (went over my head)
"""


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

    This needs to be included in blocks such that consensus can be reached. 

    There are log(n) pointers per block. The interlink data struct changes per block based
    on the previous blocks level (therefore from block to block, most superblock levels stay the same)
    
    See algorithm 1 
    """
    def __init__(self, block):
        self.genesis = block

    def update_interlink(prevBlock):
        """
        Update the interlink based on the previous blocks interlink.
        """
        pass

def verifySuffixProof(proofs):
    """
    A STEPPING STONE TO MORE ROBUST PROOFS (MAY NOT BE IMPLEMENTED SINCE INSECURE)
    Suffix is composed of the last k blocks. 

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
    """
    pass

def createSuffixProof():
    """
    Full node proof generation.

    Steps:
    -Start at genesis block
    -For each super block chain (starting highest first (most rare)) going to 0
        -remove k from end
        -take all the blocks at the given level and add it to the proof (Note for the first iteration, 
        the starting block is the genesis, however this changes with each iteration)
        -change the new starting block by  starting from the last block of this new chain go back m blocks 
        (the chosen confidence level) OR however many blocks are left in the chain.
        -start the iteration again now taking all the blocks at this level.
    """
    pass

def proofComparison(proof, proof2):
    """
    Simply the sum of 2^(superblock level) for each block. 
    """
    pass

def createInfixProof():
    proof = createSuffixProof()
    """
    for each chosen desired block (B) to be proven:
        for each block (E) in the SuffixProof():
            if depth(E) >= depth(B):
                R = followDown(E, B, depth)
                aux.append(R) # aux is the accumulation of each blocks path
            



    """
    pass

def followDown(hi, lo, height):
    """
    Algorithm that produces the necessary blocks to connect a superblock to a preceeding regular block.
    Similar to a skiplist algorithm
    hi = superblock
    lo = regular block(in which I believe you are trying to find within E)
    """

    pass

def verifyInfix():
    """
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