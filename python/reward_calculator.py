import json
from collections import defaultdict

def load_scored_logs(filename="scored_logs.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading scored logs: {e}")
        return []

def generate_reward_ledger(scored_logs, score_to_token_ratio=1.0):
    ledger = defaultdict(lambda: {
        "total_score": 0.0,
        "reward_tokens": 0.0,
        "entries": 0
    })

    for entry in scored_logs:
        vid = entry.get("vehicle_id")
        score = entry.get("green_score", 0.0)

        ledger[vid]["total_score"] += score
        ledger[vid]["entries"] += 1
        ledger[vid]["reward_tokens"] = round(ledger[vid]["total_score"] * score_to_token_ratio, 2)

    return dict(ledger)

def save_ledger(ledger, filename="reward_ledger.json"):
    with open(filename, "w") as f:
        json.dump(ledger, f, indent=2)
    print(f"Reward ledger saved to {filename}")

def print_summary(ledger):
    print("\nGreenChain Reward Summary:\n")
    print(f"{'Vehicle ID':<10} | {'Score':>8} | {'Tokens':>8} | {'Entries':>8}")
    print("-" * 42)
    for vid, stats in ledger.items():
        print(f"{vid:<10} | {stats['total_score']:>8.2f} | {stats['reward_tokens']:>8.2f} | {stats['entries']:>8}")

if __name__ == "__main__":
    logs = load_scored_logs()
    ledger = generate_reward_ledger(logs)
    save_ledger(ledger)
    print_summary(ledger)
