import json
from datetime import datetime

def load_ev_logs(filename="ev_logs.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

def parse_ev_entry(entry):
    try:
        # Validate required keys
        required_keys = ["vehicle_id", "timestamp", "energy_charged_kwh", "charging_source", "distance_driven_km", "regen_braking_kwh"]
        for key in required_keys:
            if key not in entry:
                raise KeyError(f"Missing field: {key}")

        # Type and range checks
        energy = float(entry["energy_charged_kwh"])
        if not (0 <= energy <= 100):
            raise ValueError(f"Unreasonable charge value: {energy}")

        distance = float(entry["distance_driven_km"])
        if not (0 <= distance <= 1000):
            raise ValueError(f"Unreasonable distance: {distance}")

        regen = float(entry["regen_braking_kwh"])
        if not (0 <= regen <= 10):
            raise ValueError(f"Unreasonable regen: {regen}")

        if entry["charging_source"] not in ["solar", "grid", "unknown"]:
            raise ValueError(f"Invalid charging source: {entry['charging_source']}")

        return {
            "vehicle_id": entry["vehicle_id"],
            "timestamp": datetime.fromisoformat(entry["timestamp"].replace("Z", "")),
            "energy_charged_kwh": energy,
            "charging_source": entry["charging_source"],
            "distance_driven_km": distance,
            "regen_braking_kwh": regen
        }
    except (KeyError, ValueError) as e:
        print(f"Invalid entry: {e}")
        return None


def print_summary(logs):
    print(f"\nLoaded {len(logs)} EV entries.")
    sources = {}
    for log in logs:
        src = log["charging_source"]
        sources[src] = sources.get(src, 0) + 1
    print(f"Charging source breakdown: {sources}")

if __name__ == "__main__":
    raw_logs = load_ev_logs()
    parsed_logs = [parse_ev_entry(e) for e in raw_logs if parse_ev_entry(e)]
    print_summary(parsed_logs)
