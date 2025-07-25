from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from api.auth import get_current_user
from api.rate_limiting import limiter
from api.validation import BaseActivitySubmission
from api.security_logging import log_validation_attempt, log_blockchain_transaction
from api.blockchain_guard import blockchain_protected
from web3 import Web3
from dotenv import load_dotenv
import os
from typing import Dict, Any

load_dotenv()

router = APIRouter(tags=['v2-activities'])

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

class ActivitySubmission(BaseActivitySubmission):
    pass

class RewardResponse(BaseModel):
    txHash: str
    status: str

@router.post("/submit", response_model=RewardResponse)
@limiter.limit("1000/hour")
@blockchain_protected
async def submit_activity(
    request: Request,
    activity: ActivitySubmission,
    user: dict = Depends(get_current_user),
    guard=None
):
    
    try:
        log_validation_attempt("v2", activity.wallet_address, activity.value, True, activity.details)
        
        print(f"[V2 Submit] Wallet: {activity.wallet_address}")
        print(f"[V2 Submit] Activity Type: {activity.activity_type}")
        print(f"[V2 Submit] Value: {activity.value} kWh")
        print(f"[V2 Submit] Details: {activity.details}")

        guard.allow_blockchain()
        
        kwh_scaled = int(activity.value * 100)
        
        nonce = w3.eth.get_transaction_count(sender_address, 'pending')
        print(f"[V2 Submit] Nonce (pending): {nonce}")

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
        print(f"[V2 Submit] Submitted tx hash: {tx_hash.hex()}")
        log_blockchain_transaction("v2", activity.wallet_address, activity.value, tx_hash.hex(), True)

        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
            print(f"[V2 Submit] Mined in block: {receipt.blockNumber}")
            return {"txHash": tx_hash.hex(), "status": "confirmed"}
        except Exception as e:
            print(f"[V2 Submit] Tx not confirmed within timeout: {e}")
            return {"txHash": tx_hash.hex(), "status": "pending"}

    except HTTPException:
        log_validation_attempt("v2", getattr(activity, 'wallet_address', 'unknown'), getattr(activity, 'value', 0), False)
        raise
    except ValueError as e:
        print(f"[V2 Submit] Validation Error: {str(e)}")
        log_validation_attempt("v2", getattr(activity, 'wallet_address', 'unknown'), getattr(activity, 'value', 0), False)
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        print(f"[V2 Submit] Error: {str(e)}")
        log_blockchain_transaction("v2", getattr(activity, 'wallet_address', 'unknown'), getattr(activity, 'value', 0), "failed", False)
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
