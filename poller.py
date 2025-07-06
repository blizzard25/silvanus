import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session
import requests

# Ensure api/ is importable
sys.path.append(os.path.join(os.path.dirname(__file__), "api"))

from database import SessionLocal
from models.tokens import OAuthToken

ACTIVITY_SUBMIT_URL = "https://silvanus-a4nt.onrender.com/activities/submit"

def fetch_mock_solaredge_data(token: str):
    # Placeholder for a real SolarEdge API call
    return {
        "kwh": 2.5,
        "timestamp": datetime.utcnow().isoformat()
    }

def poll_all_tokens():
    db: Session = SessionLocal()
    tokens = db.query(OAuthToken).all()

    for token in tokens:
        if token.provider == "github":
            print(f"Skipping GitHub token for wallet {token.wallet_address}")
            continue

        if not token.access_token:
            print(f"Missing token for wallet {token.wallet_address}")
            continue

        try:
            # Simulate fetching energy data
            data = fetch_mock_solaredge_data(token.access_token)

            # Submit activity to API
            response = requests.post(ACTIVITY_SUBMIT_URL, json={
                "wallet_address": token.wallet_address,
                "kwh": data["kwh"],
                "source": f"oauth:{token.provider}",
                "timestamp": data["timestamp"]
            })

            if response.status_code == 200:
                print(f"✅ Submitted {data['kwh']} kWh for {token.wallet_address}")
            else:
                print(f"❌ Failed to submit for {token.wallet_address}: {response.text}")

        except Exception as e:
            print(f"⚠️ Polling error for {token.wallet_address}: {e}")

    db.close()

if __name__ == "__main__":
    poll_all_tokens()
