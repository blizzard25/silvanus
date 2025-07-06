import requests
from datetime import datetime, timezone
import platform
import socket
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://silvanus-a4nt.onrender.com"
API_KEY = "12062569evan1206"
HEADERS = {"X-API-Key": API_KEY}

owner_wallet = os.getenv("RECIPIENT_WALLET_ADDRESS")

# Submit a solar_export event with diagnostics
activity_payload = {
    "wallet_address": owner_wallet,
    "activity_type": "solar_export",
    "value": 5.0,  # kWh
    "details": {
        "note": "Automated test via /activities/submit",
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
}

response = requests.post(f"{BASE_URL}/activities/submit", json=activity_payload, headers=HEADERS)
print("→ Submit Activity:", response.status_code, response.text)
