# api/polling.py
from datetime import datetime
from sqlalchemy.orm import Session
import requests

from api.database import SessionLocal
from api.models.tokens import OAuthToken

ACTIVITY_SUBMIT_URL = "https://silvanus-a4nt.onrender.com/activities/submit"

def fetch_mock_solaredge_data(token: str):
    # Replace this with a real SolarEdge API call later
    return {
        "kwh": 2.5,
        "timestamp": datetime.utcnow().isoformat()
    }

def poll_all_tokens():
    db: Session = SessionLocal()
    tokens = db.query(OAuthToken).all()

    for token in tokens:
        if token.provider == "github":
            # In real use, skip GitHub or treat it as a placeholder
            print(f"Skipping GitHub token for wallet {token.wallet_address}")
            continue

        if not token.access_token:
            print(f"Missing token for wallet {token.wallet_address}")
            continue

        try:
            # Fetch data from provider
            data = fetch_mock_solaredge_data(token.access_token)

            # Submit to your backend
            response = requests.post(ACTIVITY_SUBMIT_URL, json={
                "wallet_address": token.wallet_address,
                "kwh": data["kwh"],
                "source": f"oauth:{token.provider}",
                "timestamp": data["timestamp"]
            })

            if response.status_code == 200:
                print(f"Submitted {data['kwh']} kWh for {token.wallet_address}")
            else:
                print(f"Failed to submit for {token.wallet_address}: {response.text}")

        except Exception as e:
            print(f"Polling failed for {token.wallet_address}: {e}")
    
    db.close()
