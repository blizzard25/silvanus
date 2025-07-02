import time
import random
import os
import threading
from web3 import Web3
from dotenv import load_dotenv
from eth_utils import to_wei

# Load environment variables
load_dotenv()
wallets = [addr.strip() for addr in os.getenv("WALLET_ADDRESSES", "").split(",") if addr.strip()]
print("Loaded wallets:", wallets)

if not wallets:
    print("🚫 No wallet addresses found in .env. Exiting.")
    exit()

print("Starting reward loop... parallelized across all wallets every 3 seconds")

# Setup Web3
w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
REWARD_CONTRACT = os.getenv("REWARD_CONTRACT")

# Smart contract ABI
ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "uint256", "name": "score", "type": "uint256"}
        ],
        "name": "reward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Contract and account setup
contract = w3.eth.contract(address=REWARD_CONTRACT, abi=ABI)
account = w3.eth.account.from_key(PRIVATE_KEY)

# Activity scoring system
ACTIVITIES = [
    {"type": "EV miles driven", "min": 5, "max": 25, "score_per_unit": 1},
    {"type": "Public transit rides", "min": 0, "max": 2, "score_per_unit": 10},
    {"type": "Bike rides", "min": 0, "max": 3, "score_per_unit": 15},
    {"type": "Solar charging sessions", "min": 0, "max": 1, "score_per_unit": 50}
]

# Nonce management for parallelism
nonce_lock = threading.Lock()
current_nonce = w3.eth.get_transaction_count(account.address, 'pending')

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

def reward_user(user, score):
    global current_nonce
    try:
        with nonce_lock:
            nonce = current_nonce
            current_nonce += 1

        txn = contract.functions.reward(user, score).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"✅ TX succeeded: {tx_hash.hex()} | Score: {score}")
        else:
            print(f"❌ TX failed: {tx_hash.hex()}")

    except Exception as e:
        print(f"❌ Error rewarding {user}: {e}")

def process_wallet(wallet):
    data = simulate_green_activity(wallet)
    print(f"\n📡 Green Activity Report for {wallet} at {data['timestamp']}:")
    for typ, count, score in data["activities"]:
        print(f"   - {typ}: {count} (Score: {score})")

    if data["score"] > 0:
        reward_user(wallet, data["score"])
    else:
        print("🚫 No qualifying green activity — no reward.")

# Main loop
while True:
    threads = []
    for wallet in wallets:
        t = threading.Thread(target=process_wallet, args=(wallet,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    time.sleep(3)
