from fastapi import APIRouter, HTTPException
from api.models.device import Device
from typing import List

router = APIRouter()
devices_db = {}  # Replace with real DB later

@router.post("/", response_model=Device)
def register_device(device: Device):
    if device.device_id in devices_db:
        raise HTTPException(status_code=400, detail="Device already registered")
    devices_db[device.device_id] = device
    return device

@router.get("/", response_model=List[Device])
def list_devices():
    return list(devices_db.values())
