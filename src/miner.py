import wallet
import blockchain_structs as bs

def send_block(block: bs.Block) -> None:
    """
    Send block to all connected peers (miners and wallets).
    """
    pass

def create_block(mempool: bs.Mempool) -> bs.Block:
    pass

def find_pow(block: bs.Block) -> bs.Block:
    pass

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

