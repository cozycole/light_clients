from typing import *
import blockchain_structs as bs
from hashlib import sha1
from ecdsa import SigningKey, VerifyingKey, NIST192p
import random
import json

# pre-generated addresses
# (priv, pub)
MINER = ('c652028637a25b2c980b3babaac89a42e63b1227cb1946b7', 
'2c574d39a8f7e532bb269e449d5cd28b3db7e79a7917db0fd449ddacbac9663c131f8e93367e008ae1e0ce108f2e5ffb')

ADDRESSES = [('765353b3e107ad026219295db145cf93fc7462879b745988',
            'dcbf440d344f3df542b4e7dc4c92e1b4f34b6edfbd4eff75094204b2232c6f7ca2f861c0f51dd7e65cae0411a0484a43'), 
            ('894c48d2137182d16e112a3120682f69b7f0335d837dc159',
            '36f6feb41708f38c9fc7a65775e5aeec3d3028491fae2d2af542deb1f6a3556a4a2a9e236126b48c697b51693f7d091b'),
            ('d6b2189fd24fc1e19f32c2741738bb0834ac919c6ded34d7',
            '3e246fd658bb0a5feaee64f4c69adeb5d537be6b5083f20de2c06e1914ef3b09d12bca3081f02d7a69c1ca5af5892e67')]

def verify_UTXO(utxo: bs.UTXO, utxo_set: List[bs.UTXO]) -> bool:
    """
    Checks that both the the UTXO signature is valid, and that the UTXO resides
    in the UTXO set.
    """
    # First check the utxo resides in the set
    if utxo not in utxo_set:
        return False
    # Second, verify if the signature is valid
    prove_message = utxo.get_message().to_json().encode()
    verif_key = VerifyingKey.from_string(bytearray.fromhex(utxo.pub_key), curve=NIST192p)
    decoded_sig = bytes.fromhex(utxo.sig)
    try:
        return verif_key.verify(decoded_sig, prove_message)
    except:
        return False

def find_pow(block: bs.Block, difficulty: int) -> bs.Block:
    serial_block = block.to_json().encode()
    pow_hash = sha1(serial_block)
    while (int(pow_hash.hexdigest(), 16) > difficulty):
        block.set_nonce(block.nonce + 1)
        serial_block = block.to_json().encode()
        pow_hash = sha1(serial_block)
    block.set_block_hash(pow_hash.hexdigest())
    print("\n|Miner|")
    print(f"\tSolution found with nonce {block.nonce} with digest {pow_hash.hexdigest()}\n")
    return block

def get_tx_hash(tx: bs.Transaction):
    return sha1(json.dumps(tx, indent = 4, default=lambda o: o.__dict__)).hexdigest()

def get_block_hash(block: bs.Block):
    return sha1(json.dumps(block, indent = 4, default=lambda o: o.__dict__).encode()).hexdigest()

def create_coinbase_tx(pubkey, value):
    coinbase = bs.UTXO(value, pubkey)
    return bs.Transaction([], [coinbase]).set_tx_id()

def disperse_coinbase(addresses: List[Tuple], utxo: bs.UTXO):
    """ Distributes previous block's coinbase transaction to addresses in the address book
    creates one.
    """
    utxo.sign_utxo(MINER[0])
    vin = [utxo]
    vout = []
    ds_amount = utxo.val // len(addresses)
    for i in range(len(addresses)):
        vout.append(bs.UTXO(ds_amount, addresses[i][1]))
    return bs.Transaction(vin, vout).set_tx_id()

def create_txs(block: bs.Block, rounds):
    """ 
    Takes in previous block and number of transactions desired to create.
    This function creates a list of new transactions between senders
    in the address book. I don't really want to create functions that keep
    track of the UTXO set so every transactions deals with vouts from the previous block.
    """
    tx_list = []
    for i in range(len(ADDRESSES)):
        priv_key = ADDRESSES[i][0]
        pub_key = ADDRESSES[i][1]
        add_list = [key for key in ADDRESSES if key != ADDRESSES[i]]
        utxos = []
        # find utxos for given address
        for tx in block.txs:
            for utxo in tx.vout:
                if utxo.pub_key == pub_key:
                    utxos.append(utxo)
        # rounds is the number of times each address creates tx to other addresses
        for i in range(rounds):
            # if utxo list is empty stop making txs from curr address
            if not utxos:
                break
            curr_utxo = random.choice(utxos)
            curr_utxo.sign_utxo(priv_key)
            send_utxo = bs.UTXO(random.randint(1, curr_utxo.val), random.choice(add_list)[1])
            vin = [curr_utxo]
            vout = [send_utxo]
            tx_list.append(bs.Transaction(vin, vout).set_tx_id())
            utxos.remove(curr_utxo)
    return tx_list

def output_blockchain(blockchain):
    for block in blockchain.chain:
        print(block)

def generate_blockchain(block_num, coinbase, difficulty):
    block_chain = bs.Blockchain(coinbase, difficulty)
    # create and add genesis block
    genesis = bs.Block(None, [], 0)
    block_hash = get_block_hash(genesis)
    genesis.set_block_hash(block_hash)
    block_chain.add_block(genesis)
    
    miner_pub_key = MINER[1]
    address_book = ADDRESSES # list of all the addresses
    # creates the first block (when no UTXOs exist yet)
    first_coinbase = create_coinbase_tx(miner_pub_key, coinbase)
    disperse_cb = disperse_coinbase(address_book, first_coinbase.vout[0])
    first_tx_list = [first_coinbase, disperse_cb]
    premine_block = bs.Block(block_chain.head, first_tx_list, block_chain.height+1)
    first_block = find_pow(premine_block, difficulty)
    block_chain.add_block(first_block)
    # subsequent blocks will be creating txs among addresses
    for i in range(block_num):
        tx_list = []
        tx_list.append(create_coinbase_tx(miner_pub_key, coinbase))
        tx_list.append(disperse_coinbase(address_book, block_chain.head.txs[0].vout[0]))
        tx_list = tx_list + create_txs(block_chain.head, 18) # unpacks list returned from create_txs
        new_block = bs.Block(block_chain.head, tx_list , block_chain.height+1)
        find_pow(new_block, difficulty)
        block_chain.add_block(new_block)
    return block_chain

if __name__ == "__main__":
    # generate chain with 5 blocks, block rewards of 25 and given pow difficulty
    # 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF hex for 1/16^4 chance of finding pow solution
    chain = generate_blockchain(1, 25, 0x0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    output_blockchain(chain)