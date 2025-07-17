# api/routes/wallets.py
from fastapi import APIRouter, Depends
from api.auth import get_current_user

router = APIRouter(tags=['wallets'], dependencies=[Depends(get_current_user)])

# Wallets route has been disabled from its previous version, however it is being maintained for future iterations on device metadata
@router.get("/wallets/ping")
def ping_wallet():
    return {"status": "Wallet route disabled"}
