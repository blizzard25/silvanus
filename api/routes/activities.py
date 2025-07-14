from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, validator, Field
from api.auth import get_api_key_with_tier, APIKeyTier
from api.main import limiter, get_rate_limit_for_request
from web3 import Web3
from dotenv import load_dotenv
import os
import re
from typing import Dict, Any
from decimal import Decimal

load_dotenv()

router = APIRouter(tags=['activities'])

# Load environment
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
REWARD_CONTRACT = os.getenv("REWARD_CONTRACT")

# Connect to Web3
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
sender_address = w3.eth.account.from_key(PRIVATE_KEY).address

# Contract ABI
reward_distributor_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "uint256", "name": "score", "type": "uint256"}
        ],
        "name": "reward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=REWARD_CONTRACT, abi=reward_distributor_abi)

VALID_ACTIVITY_TYPES = {
    "solar_export", "ev_charging", "energy_saving", "carbon_offset", 
    "renewable_energy", "green_transport", "waste_reduction"
}

class ActivitySubmission(BaseModel):
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
        
        return '0x' + address if not v.startswith('0x') else v.lower()
    
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
    
    @validator('details')
    def validate_details(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Details must be a dictionary')
        
        if len(str(v)) > 1000:
            raise ValueError('Details field is too large (max 1000 characters)')
        
        return v

class RewardResponse(BaseModel):
    txHash: str
    status: str

@router.post("/submit", response_model=RewardResponse)
async def submit_activity(
    request: Request,
    activity: ActivitySubmission,
    auth_info: dict = Depends(get_api_key_with_tier)
):
    rate_limit = get_rate_limit_for_request(request)
    await limiter.limit(rate_limit)(request)
    
    try:
        print(f"[Submit] API Tier: {auth_info['tier'].value}")
        print(f"[Submit] Wallet: {activity.wallet_address}")
        print(f"[Submit] Activity Type: {activity.activity_type}")
        print(f"[Submit] Value: {activity.value} kWh")
        print(f"[Submit] Details: {activity.details}")

        kwh_scaled = int(activity.value * 100)
        
        if auth_info['tier'] == APIKeyTier.BASIC and activity.value > 100:
            raise HTTPException(
                status_code=403, 
                detail="Basic tier limited to 100 kWh per submission"
            )
        
        nonce = w3.eth.get_transaction_count(sender_address, 'pending')
        print(f"[Submit] Nonce (pending): {nonce}")

        txn = contract.functions.reward(activity.wallet_address, kwh_scaled).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 300000,
            'maxFeePerGas': w3.to_wei('25', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('2', 'gwei'),
            'chainId': w3.eth.chain_id
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        raw_tx = getattr(signed_txn, "rawTransaction", getattr(signed_txn, "raw_transaction", None))
        if not raw_tx:
            raise Exception("SignedTransaction has no raw transaction field")

        tx_hash = w3.eth.send_raw_transaction(raw_tx)
        print(f"[Submit] Submitted tx hash: {tx_hash.hex()}")

        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
            print(f"[Submit] Mined in block: {receipt.blockNumber}")
            return {"txHash": tx_hash.hex(), "status": "confirmed"}
        except Exception as e:
            print(f"[Submit] Tx not confirmed within timeout: {e}")
            return {"txHash": tx_hash.hex(), "status": "pending"}

    except HTTPException:
        raise
    except ValueError as e:
        print(f"[Submit] Validation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        print(f"[Submit] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
