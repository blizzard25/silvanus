from fastapi import APIRouter, HTTPException, Depends
from api.models.activity import GreenActivity
from api.auth import get_api_key
from typing import List

router = APIRouter(tags=['activities'], dependencies=[Depends(get_api_key)])
activity_log = []

@router.post("/", response_model=GreenActivity)
def submit_activity(activity: GreenActivity):
    if not activity.device_id:
        raise HTTPException(status_code=400, detail="Missing device ID")
    activity_log.append(activity)
    return activity

@router.get("/", response_model=List[GreenActivity])
def get_all_activities():
    return activity_log
