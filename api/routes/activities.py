from fastapi import APIRouter, HTTPException, Depends
from api.models.activity import GreenActivity
from api.auth import get_api_key
from typing import List
from datetime import datetime
from api.routes.wallets import wallet_scores, wallet_events
from api.routes.devices import registered_devices  # assumes device_id → {owner, type}

router = APIRouter(tags=['activities'], dependencies=[Depends(get_api_key)])
activity_log = []

# Scoring weights per activity type (adjustable)
activity_weights = {
    "solar_export": 1.5,
    "ev_charging": 1.2,
    "regen_braking": 1.0,
    "thermostat_adjustment": 0.8
}

@router.post("/", response_model=GreenActivity)
def submit_activity(activity: GreenActivity):
    if not activity.device_id:
        raise HTTPException(status_code=400, detail="Missing device ID")

    # Verify device is registered
    device = registered_devices.get(activity.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not registered")

    # Lookup wallet and assign score
    wallet = device["owner"]
    multiplier = activity_weights.get(activity.activity_type, 1.0)
    points = activity.value * multiplier
    wallet_scores[wallet] = wallet_scores.get(wallet, 0) + points

    # Log the event
    event = {
        "activity": activity.activity_type,
        "value": activity.value,
        "timestamp": datetime.utcnow(),
        "details": activity.details
    }
    wallet_events.setdefault(wallet, []).append(event)
    activity_log.append(activity)

    return activity

@router.get("/", response_model=List[GreenActivity])
def get_all_activities():
    return activity_log
