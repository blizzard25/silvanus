# api/routes/wallets.py
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# In-memory store
wallet_scores = {}
wallet_events = {}

class GreenEvent(BaseModel):
    activity: str
    value: float
    timestamp: datetime
    details: dict

class WalletScore(BaseModel):
    wallet: str
    score: float

class ClaimResponse(BaseModel):
    txHash: str
    status: str

@router.get("/wallets/{wallet}/score", response_model=WalletScore)
def get_wallet_score(wallet: str):
    score = wallet_scores.get(wallet, 0)
    return {"wallet": wallet, "score": score}

@router.get("/wallets/{wallet}/events", response_model=List[GreenEvent])
def get_wallet_events(wallet: str):
    return wallet_events.get(wallet, [])

@router.post("/wallets/{wallet}/claim", response_model=ClaimResponse)
def claim_rewards(wallet: str):
    # Dummy on-chain call simulation
    tx_hash = f"0x{uuid.uuid4().hex}"
    return {"txHash": tx_hash, "status": "submitted"}
