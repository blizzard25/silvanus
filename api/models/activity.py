from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GreenActivity(BaseModel):
    device_id: str
    activity_type: str  # e.g., "ev_miles", "solar_charge", "regen_braking"
    value: float        # miles driven, kWh, # of events
    timestamp: Optional[datetime] = None
