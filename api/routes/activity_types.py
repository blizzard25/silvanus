# api/routes/activity_types.py
from fastapi import APIRouter, Depends
from api.auth import get_api_key
from typing import List

#router = APIRouter()
router = APIRouter(tags=['activity-types'], dependencies=[Depends(get_api_key)])

@router.get("/activities/types", response_model=List[dict])
def get_activity_types():
    return [
        {
            "type": "ev_charging",
            "description": "Charging EV using solar or off-peak grid power",
            "expectedDetails": ["kWhUsed", "chargingDuration", "offPeak"]
        },
        {
            "type": "regen_braking",
            "description": "Energy recovered through regenerative braking",
            "expectedDetails": ["kWhRecovered"]
        },
        {
            "type": "thermostat_adjustment",
            "description": "Smart thermostat behavior changes to save energy",
            "expectedDetails": ["targetTemp", "ecoMode"]
        },
        {
            "type": "solar_export",
            "description": "Power exported to grid from solar array",
            "expectedDetails": ["kWhExported"]
        },
    ]
