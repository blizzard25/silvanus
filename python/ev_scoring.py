from ev_data_ingest import load_ev_logs, parse_ev_entry

def compute_green_score(entry):
    score = 0.0
    explanation = {}

    # Base score
    score += 5.0
    explanation["base_score"] = 5.0

    # Charging source bonus
    source_bonus = {"solar": 2.0, "grid": 0.5, "unknown": 0.0}
    charging_bonus = source_bonus.get(entry["charging_source"], 0.0)
    score += charging_bonus
    explanation["charging_bonus"] = charging_bonus

    # Efficiency bonus (km per kWh)
    try:
        efficiency = entry["distance_driven_km"] / entry["energy_charged_kwh"]
    except ZeroDivisionError:
        efficiency = 0

    if efficiency > 4.0:
        eff_bonus = 1.0
    elif efficiency >= 2.0:
        eff_bonus = 0.5
    else:
        eff_bonus = 0.0

    score += eff_bonus
    explanation["efficiency_bonus"] = eff_bonus

    # Regenerative braking bonus (relative to energy charged)
    regen_ratio = entry["regen_braking_kwh"] / max(entry["energy_charged_kwh"], 0.01)
    regen_bonus = min(regen_ratio * 5.0, 1.0)
    score += regen_bonus
    explanation["regen_bonus"] = round(regen_bonus, 2)

    # Final score and breakdown
    return round(score, 2), explanation

def score_all_entries(entries):
    results = []
    for entry in entries:
        parsed = parse_ev_entry(entry)
        if parsed:
            score, details = compute_green_score(parsed)
            results.append({
                "vehicle_id": parsed["vehicle_id"],
                "timestamp": parsed["timestamp"].isoformat() + "Z",
                "green_score": score,
                "explanation": details
            })
    return results

def print_sample_output(scored):
    for item in scored[:3]:
        print(json.dumps(item, indent=2))
    print(f"\n...Total entries scored: {len(scored)}")

if __name__ == "__main__":
    import json
    raw_logs = load_ev_logs()
    scored_logs = score_all_entries(raw_logs)
    print_sample_output(scored_logs)

    # Optionally save to file
    with open("scored_logs.json", "w") as f:
        json.dump(scored_logs, f, indent=2)
