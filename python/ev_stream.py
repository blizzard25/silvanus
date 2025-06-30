import time
import random
import os
from web3 import Web3
from dotenv import load_dotenv
from eth_utils import to_wei

# Load .env file
load_dotenv()
wallets = [addr.strip() for addr in os.getenv("WALLET_ADDRESSES", "").split(",") if addr.strip()]
print("Loaded wallets:", wallets)

if not wallets:
    print("🚫 No wallet addresses found in .env. Exiting.")
    exit()

print("Starting reward loop... polling every 15 seconds")

# Setup Web3 connection
w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
REWARD_CONTRACT = "0x3f7789C9e2DAa66d864bEB3Bf52B1F96B391cc60"

# Load multiple wallet addresses (comma-separated in .env)
wallets = [addr.strip() for addr in os.getenv("WALLET_ADDRESSES", "").split(",") if addr.strip()]

# Connect to reward distributor contract
ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "reward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=REWARD_CONTRACT, abi=ABI)
account = w3.eth.account.from_key(PRIVATE_KEY)

# Green activity types and scores
ACTIVITIES = [
    {"type": "EV miles driven", "min": 5, "max": 25, "score_per_unit": 1},
    {"type": "Public transit rides", "min": 0, "max": 2, "score_per_unit": 10},
    {"type": "Bike rides", "min": 0, "max": 3, "score_per_unit": 15},
    {"type": "Solar charging sessions", "min": 0, "max": 1, "score_per_unit": 50}
]

def simulate_green_activity(user):
    activity_data = []
    total_score = 0

    for act in ACTIVITIES:
        count = random.randint(act["min"], act["max"])
        score = count * act["score_per_unit"]
        total_score += score
        activity_data.append((act["type"], count, score))

    return {
        "user": user,
        "score": total_score,
        "activities": activity_data,
        "timestamp": int(time.time())
    }

def reward_user(user, amount):
    try:
        nonce = w3.eth.get_transaction_count(account.address, 'pending')
        txn = contract.functions.reward(user, amount).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"✅ Rewarded {amount} tokens to {user} — TX: {tx_hash.hex()}")
    except Exception as e:
        print(f"❌ Error rewarding {user}: {e}")

# Main simulation loop
while True:
    for wallet in wallets:
        data = simulate_green_activity(wallet)
        print(f"\n📡 Green Activity Report for {wallet} at {data['timestamp']}:")
        for typ, count, score in data["activities"]:
            print(f"   - {typ}: {count} (Score: {score})")
        if data["score"] > 0:
            reward_user(wallet, to_wei(data["score"], 'ether'))
        else:
            print("🚫 No qualifying green activity — no reward.")
    time.sleep(3)
