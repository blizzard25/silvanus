# api/routes/wallets.py
from fastapi import APIRouter, HTTPException, Depends
from api.auth import get_api_key
from typing import List
from pydantic import BaseModel
from datetime import datetime
from web3 import Web3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(tags=['wallets'], dependencies=[Depends(get_api_key)])

# In-memory store
wallet_scores = {}
wallet_events = {}

# Load blockchain config
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
REWARD_CONTRACT = os.getenv("REWARD_CONTRACT")
TOKEN_ADDRESS = os.getenv("TOKEN_ADDRESS")

# Connect to Web3
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
sender_address = w3.eth.account.from_key(PRIVATE_KEY).address

# ABI from ev_stream.py
reward_distributor_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "distributeReward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Load contract
contract = w3.eth.contract(address=REWARD_CONTRACT, abi=reward_distributor_abi)

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
    score = wallet_scores.get(wallet, 0)

    if score <= 0:
        raise HTTPException(status_code=400, detail="Nothing to claim")

    try:
        nonce = w3.eth.get_transaction_count(sender_address)

        txn = contract.functions.distributeReward(wallet, int(score)).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.to_wei('10', 'gwei')
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Reset the score after successful submission
        wallet_scores[wallet] = 0

        return {"txHash": tx_hash.hex(), "status": "submitted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting transaction: {str(e)}")
