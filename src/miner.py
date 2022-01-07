import wallet
import blockchain_structs as bs
from hashlib import sha1
import json

def send_block(block: bs.Block) -> None:
    """
    Send block to all connected peers (miners and wallets).
    """
    pass

def create_block(mempool: bs.Mempool) -> bs.Block:
    pass

def find_pow(block: bs.Block, difficulty: int) -> bs.Block:
    serial_block = block.to_json().encode()
    pow_hash = sha1(serial_block)
    while (int(pow_hash.hexdigest(), 16) > difficulty):
        print(block.nonce)
        block.set_nonce(block.nonce + 1)
        serial_block = block.to_json().encode()
        pow_hash = sha1(serial_block)
    # print(f"Solution found with nonce {block.nonce} with digest {pow_hash.hexdigest()}")
    return block

def open_peer_thread(port: int):
    """
    Create new server thread that listens for new connections from miners and wallets.
    """
    pass

def add_to_mempool(tx: bs.Transaction, mempool: bs.Mempool):
    """
    Add a tx received and validated transaction to the mempool for future blocks.
    """
    pass


# b8a0acaf4c1421a9eff8a323536991f389f0fe22
# 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF hex for 1/16 chance of finding pow solution
"""block_hash = find_pow(block.to_json().encode())
print("HASH SIZE: ",block_hash.digest_size)
print("HASH BYTES: ",block_hash.hexdigest())
"""