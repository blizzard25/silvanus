import json
import random
from datetime import datetime, timedelta

def generate_ev_log(vehicle_id="EV001", start_time=None, entries=10):
    if start_time is None:
        start_time = datetime.utcnow()

    logs = []
    for i in range(entries):
        timestamp = start_time + timedelta(minutes=30 * i)
        energy_charged = round(random.uniform(5, 25), 2)
        charging_source = random.choices(["solar", "grid", "unknown"], weights=[0.5, 0.4, 0.1])[0]
        distance_driven = round(random.uniform(10, 80), 2)
        regen_braking = round(random.uniform(0.5, 3.0), 2)

        logs.append({
            "vehicle_id": vehicle_id,
            "timestamp": timestamp.isoformat() + "Z",
            "energy_charged_kwh": energy_charged,
            "charging_source": charging_source,
            "distance_driven_km": distance_driven,
            "regen_braking_kwh": regen_braking
        })

    return logs

def save_logs_to_file(logs, filename="ev_logs.json"):
    with open(filename, "w") as f:
        json.dump(logs, f, indent=2)

if __name__ == "__main__":
    ev_logs = generate_ev_log(entries=20)
    save_logs_to_file(ev_logs)
    print(f"Generated {len(ev_logs)} EV log entries in 'ev_logs.json'")
