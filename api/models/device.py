from pydantic import BaseModel

class Device(BaseModel):
    device_id: str
    device_type: str  # e.g., EV, solar, thermostat
    owner: str
