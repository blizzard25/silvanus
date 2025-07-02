import httpx
import requests
from datetime import datetime, timezone
import uuid

BASE_URL = "http://localhost:8000"

def test_register_device():
    payload = {
        "device_id": "EV Tracker #1",
        "device_type": "ev",
        "owner": "0x1234567890abcdef1234567890abcdef12345678"
    }

    response = requests.post(f"{BASE_URL}/devices/", json=payload)
    print("Status code:", response.status_code)
    print("Response body:", response.text)  # added line
    assert response.status_code == 200
    data = response.json()
    print("✅ Registered Device:", data)
    return data["device_id"]


def test_submit_activity(device_id):
    payload = {
        "device_id": device_id,
        "wallet": "0x1234567890abcdef1234567890abcdef12345678",
        "activity_type": "ev_miles",
        "value": 12,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {
            "regenBraking": 1.8,
            "offPeak": True
        }
    }

    response = requests.post(f"{BASE_URL}/activities/", json=payload)
    print("Status code:", response.status_code)
    print("Response body:", response.text)
    assert response.status_code == 200

    data = response.json()
    print("✅ Submitted Activity:", data)

def test_get_score(wallet):
    print("→ Testing GET /wallets/{wallet}/score")
    response = requests.get(f"{BASE_URL}/wallets/{wallet}/score")
    print("Status code:", response.status_code)
    print("Response body:", response.text)
    assert response.status_code == 200
    data = response.json()
    print("✅ Retrieved Score:", data)


def test_get_events(wallet):
    print("→ Testing GET /wallets/{wallet}/events")
    response = requests.get(f"{BASE_URL}/wallets/{wallet}/events")
    print("Status code:", response.status_code)
    print("Response body:", response.text)
    assert response.status_code == 200
    data = response.json()
    print("✅ Retrieved Events:", data)


def test_trigger_claim(wallet):
    print("→ Testing POST /wallets/{wallet}/claim")
    response = requests.post(f"{BASE_URL}/wallets/{wallet}/claim")
    print("Status code:", response.status_code)
    print("Response body:", response.text)
    assert response.status_code == 200
    data = response.json()
    print("✅ Triggered Claim:", data)


def test_get_activity_types():
    response = requests.get(f"{BASE_URL}/activities/types/")
    assert response.status_code == 200
    data = response.json()
    print("✅ Activity Types:", data)

if __name__ == "__main__":
    print("Running GreenChain API Tests...\n")
    wallet = "0x123ABC456DEF"
    device_id = test_register_device()
    test_submit_activity(device_id)
    test_get_score(wallet)
    test_get_events(wallet)
    test_trigger_claim(wallet)
    test_get_activity_types()
