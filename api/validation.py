from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from web3 import Web3
import re
from typing import Dict, Any

VALID_ACTIVITY_TYPES = {
    "solar_export", "ev_charging", "energy_saving", "carbon_offset", 
    "renewable_energy", "green_transport", "waste_reduction"
}

class BaseActivitySubmission(BaseModel):
    wallet_address: str = Field(..., description="Ethereum wallet address")
    activity_type: str = Field(..., description="Type of green activity")
    value: float = Field(..., ge=0.0, le=10000.0, description="Activity value in kWh (0-10000)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional activity details")
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not v:
            raise ValueError('Wallet address is required')
        
        address = v.lower()
        if address.startswith('0x'):
            address = address[2:]
        
        if not re.match(r'^[0-9a-f]{40}$', address):
            raise ValueError('Invalid Ethereum wallet address format')
        
        normalized_address = '0x' + address if not v.startswith('0x') else v.lower()
        return Web3.to_checksum_address(normalized_address)
    
    @validator('activity_type')
    def validate_activity_type(cls, v):
        if v not in VALID_ACTIVITY_TYPES:
            raise ValueError(f'Invalid activity type. Must be one of: {", ".join(VALID_ACTIVITY_TYPES)}')
        return v
    
    @validator('value')
    def validate_value(cls, v):
        if v < 0:
            raise ValueError('Activity value must be non-negative')
        if v > 10000:
            raise ValueError('Activity value cannot exceed 10000 kWh')
        
        return round(float(v), 2)

def validate_activity_before_blockchain(activity: BaseActivitySubmission, endpoint_name: str):
    """Explicit validation before blockchain interaction"""
    if activity.value > 10000:
        print(f"[{endpoint_name}] VALIDATION FAILED: Value {activity.value} exceeds 10000 kWh limit")
        raise HTTPException(status_code=422, detail="Activity value cannot exceed 10000 kWh")
    
    if activity.value < 0:
        print(f"[{endpoint_name}] VALIDATION FAILED: Value {activity.value} is negative")
        raise HTTPException(status_code=422, detail="Activity value must be non-negative")
        
    print(f"[{endpoint_name}] VALIDATION PASSED: Value {activity.value} kWh is within limits")
