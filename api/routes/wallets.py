# api/routes/wallets.py
from fastapi import APIRouter, Depends
from api.auth import get_api_key

router = APIRouter(tags=['wallets'], dependencies=[Depends(get_api_key)])

# Wallets route has been disabled from its previous version, however it is being maintained for future iterations on device metadata
@router.get("/wallets/ping")
def ping_wallet():
    return {"status": "Wallet route disabled"}
