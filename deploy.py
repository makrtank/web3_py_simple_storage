from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# alternatively can deploy to real blockchain via Infura to get http link
# update chain_id to publically available info per chain
# get chain specific address and private key
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = os.getenv("PRIVATE_KEY")

# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get latest transaction
nonce = w3.eth.getTransactionCount(my_address)
print(nonce)

# Build a TX
# Sign it
# Send it
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("sending transaction...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("waiting for receipt...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed.")
# working with Contract you need:
# Contract ABI
# Contract Address

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> simulate making the call and getting a return value
# Transact -> Actually make a state change

# initial value of favorite number
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
        "gasPrice": w3.eth.gas_price,
    }
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
print("sending tx...")
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("waiting for receipt...")
tx_reciept = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("tx sent, new #:")
print(simple_storage.functions.retrieve().call())
