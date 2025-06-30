# mint_rewards.py
import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

# Load ENV vars
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SENDER_ADDRESS = os.getenv("WALLET_ADDRESS")

# Load contract ABI and address
CONTRACT_ADDRESS = "0x3E80B5768D2a48Da2f5C235f6a0d601a769A9Ca7"
with open("artifacts/contracts/SilvanusToken.sol/SilvanusToken.json") as f:
    contract_artifact = json.load(f)
abi = contract_artifact["abi"]

# Setup Web3
w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Load wallets
with open("python/wallets.json") as f:
    wallets = json.load(f)

for vehicle_id, data in wallets.items():
    wallet_address = data.get("wallet_address")
    unclaimed = data.get("unclaimed_tokens", 0)

    if not wallet_address or unclaimed <= 0:
        continue

    amount_wei = w3.to_wei(unclaimed, 'ether')
    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)

    tx = contract.functions.transfer(wallet_address, amount_wei).build_transaction({
        'chainId': 11155111,  # Sepolia chain ID
        'gas': 100000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': nonce,
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"Minted {unclaimed} SVN to {wallet_address} for {vehicle_id} (TX: {tx_hash.hex()})")

    # Update ledger
    data["claimed_tokens"] += unclaimed
    data["unclaimed_tokens"] = 0

# Save updated wallets
with open("wallets.json", "w") as f:
    json.dump(wallets, f, indent=2)
