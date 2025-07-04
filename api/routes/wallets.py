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

SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
REWARD_CONTRACT = os.getenv("REWARD_CONTRACT")
TOKEN_ADDRESS = os.getenv("TOKEN_ADDRESS")

# Connect to Web3
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
sender_address = w3.eth.account.from_key(PRIVATE_KEY).address

# ABI for rewards smart contract
reward_distributor_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "reward",
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
    print(f"[Claim] Wallet: {wallet}, Score: {score}")

    if score <= 0:
        raise HTTPException(status_code=400, detail="Nothing to claim")

    try:
        # Use 'pending' to account for any in-flight transactions
        nonce = w3.eth.get_transaction_count(sender_address, 'pending')
        print(f"[Claim] Nonce (pending): {nonce}")

        txn = contract.functions.reward(wallet, int(score)).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 300000,
            'maxFeePerGas': w3.to_wei('25', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('2', 'gwei'),
            'chainId': w3.eth.chain_id
        })

        print(f"[Claim] Raw transaction: {txn}")
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)

        raw_tx = getattr(signed_txn, "rawTransaction", getattr(signed_txn, "raw_transaction", None))
        if not raw_tx:
            raise Exception("SignedTransaction has no raw transaction field")

        tx_hash = w3.eth.send_raw_transaction(raw_tx)
        print(f"[Claim] Submitted tx hash: {tx_hash.hex()}")

        # Wait for confirmation (timeout after 30s)
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
            print(f"[Claim] Mined in block: {receipt.blockNumber}")
        except Exception as e:
            print(f"[Claim] Tx not confirmed within timeout: {e}")

        wallet_scores[wallet] = 0

        return {"txHash": tx_hash.hex(), "status": "submitted"}

    except Exception as e:
        print(f"[Claim] Exception: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting transaction: {str(e)}")
