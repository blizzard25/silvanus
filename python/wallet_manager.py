import json
import os

LEDGER_FILE = "reward_ledger.json"
WALLET_FILE = "wallets.json"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def initialize_wallets(ledger):
    wallets = {}
    for vid, stats in ledger.items():
        wallets[vid] = {
            "claimed_tokens": 0.0,
            "unclaimed_tokens": stats["reward_tokens"]
        }
    return wallets

def claim_tokens(wallets, vehicle_id, amount):
    wallet = wallets.get(vehicle_id)
    if not wallet:
        print(f"Vehicle ID '{vehicle_id}' not found.")
        return

    claimable = wallet["unclaimed_tokens"]
    if amount > claimable:
        print(f"Insufficient unclaimed tokens: Requested {amount}, Available {claimable}")
        return

    wallet["unclaimed_tokens"] -= amount
    wallet["claimed_tokens"] += amount
    print(f"{vehicle_id} successfully claimed {amount} PoG tokens.")

def show_balances(wallets):
    print("\nWallet Balances:\n")
    print(f"{'Vehicle ID':<10} | {'Claimed':>8} | {'Unclaimed':>10}")
    print("-" * 34)
    for vid, w in wallets.items():
        print(f"{vid:<10} | {w['claimed_tokens']:>8.2f} | {w['unclaimed_tokens']:>10.2f}")

if __name__ == "__main__":
    ledger = load_json(LEDGER_FILE)
    wallets = load_json(WALLET_FILE)

    if not wallets:
        wallets = initialize_wallets(ledger)
        save_json(WALLET_FILE, wallets)
        print("Wallets initialized from reward ledger.")

    show_balances(wallets)

    # Example: simulate a claim
    vehicle_id = input("\nEnter vehicle ID to claim tokens from: ")
    amount = float(input("Enter amount of tokens to claim: "))
    claim_tokens(wallets, vehicle_id, amount)

    save_json(WALLET_FILE, wallets)
