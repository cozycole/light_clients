from typing import *
import blockchain_structs as bs


def create_tx(wallet_key: int, recipients) -> object:
    pass

def send_tx(tx: bs.Transaction) -> str:
    pass

def verify_tx(tx: bs.Transaction) -> bool:
    pass

def sign_UTXO(priv_key: int, utxo: bs.UTXO) -> bs.UTXO:
    """
    
    """
    pass

def find_UTXOs(pub_key: int) -> List[bs.UTXO]:
    """
    Finds the UTXOs of a the UTXO set for a given wallet.
    """
    pass


def verify_block(block: bs.Block) -> bool:
    """
    Block Standards:
    - Block must have all valid transactions.
    - Block must have a valid coinbase transaction.
    - Is BlockHash < Difficulty
    - 
    """
    pass

def find_miner(ports: List[int]) -> None:
    """
    Connect to a miner's serving thread through TCP. 
    """
    pass
