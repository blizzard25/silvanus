# api/routes/devices.py
from fastapi import APIRouter, Depends
from api.auth import get_current_user

router = APIRouter(tags=['devices'], dependencies=[Depends(get_current_user)])

# Device route has been disabled from its previous version, however it is being maintained for future iterations on device metadata
@router.get("/devices/ping")
def ping_devices():
    return {"status": "Device route disabled"}
