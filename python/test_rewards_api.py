import requests
from datetime import datetime, timezone
import platform
import socket
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://silvanus-a4nt.onrender.com"

API_KEYS = {
    "basic": "12062569evan1206",  # Basic tier (1000/hour)
    "premium": "premium_key_test",  # Premium tier (5000/hour) - placeholder
    "admin": "admin_key_test",  # Admin tier (10000/hour) - placeholder
    "invalid": "invalid_key_123"  # Invalid key for testing
}

owner_wallet = os.getenv("RECIPIENT_WALLET_ADDRESS")

def make_request(endpoint, payload=None, api_key=None, method="GET"):
    """Make HTTP request with optional API key"""
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    url = f"{BASE_URL}{endpoint}"
    
    if method == "POST":
        response = requests.post(url, json=payload, headers=headers)
    else:
        response = requests.get(url, headers=headers)
    
    return response

def test_health_endpoint():
    """Test health check endpoint"""
    print("\n=== HEALTH CHECK TEST ===")
    response = make_request("/healthz")
    print(f"→ Health Check: {response.status_code} {response.text}")
    return response.status_code == 200

def test_activity_types_endpoint():
    """Test activity types endpoint"""
    print("\n=== ACTIVITY TYPES TEST ===")
    response = make_request("/activities/types", api_key=API_KEYS["basic"])
    print(f"→ Activity Types: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   Available types: {data}")
        except:
            print(f"   Response: {response.text}")
    return response.status_code == 200

def test_v1_endpoint():
    """Test V1 activities endpoint (legacy behavior)"""
    print("\n=== V1 ENDPOINT TEST ===")
    
    activity_payload = {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 5.0,  # kWh
        "details": {
            "note": "V1 endpoint test",
            "host": socket.gethostname(),
            "platform": platform.platform(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    
    response = make_request("/v1/activities/submit", activity_payload, API_KEYS["basic"], "POST")
    print(f"→ V1 Submit Activity: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    else:
        try:
            data = response.json()
            print(f"   Success: {data}")
        except:
            print(f"   Response: {response.text}")
    
    return response.status_code == 200

def test_v2_endpoint():
    """Test V2 activities endpoint (enhanced validation)"""
    print("\n=== V2 ENDPOINT TEST ===")
    
    activity_payload = {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 7.5,  # kWh
        "details": {
            "note": "V2 endpoint test with enhanced validation",
            "host": socket.gethostname(),
            "platform": platform.platform(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_version": "v2"
        }
    }
    
    response = make_request("/v2/activities/submit", activity_payload, API_KEYS["basic"], "POST")
    print(f"→ V2 Submit Activity: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    else:
        try:
            data = response.json()
            print(f"   Success: {data}")
        except:
            print(f"   Response: {response.text}")
    
    return response.status_code == 200

def test_legacy_endpoint():
    """Test legacy activities endpoint (backward compatibility)"""
    print("\n=== LEGACY ENDPOINT TEST ===")
    
    activity_payload = {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 3.0,  # kWh
        "details": {
            "note": "Legacy endpoint test",
            "host": socket.gethostname(),
            "platform": platform.platform(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    
    response = make_request("/activities/submit", activity_payload, API_KEYS["basic"], "POST")
    print(f"→ Legacy Submit Activity: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    else:
        try:
            data = response.json()
            print(f"   Success: {data}")
        except:
            print(f"   Response: {response.text}")
    
    return response.status_code == 200

def test_input_validation():
    """Test enhanced input validation in V2"""
    print("\n=== INPUT VALIDATION TESTS ===")
    
    print("→ Testing invalid wallet address...")
    invalid_payload = {
        "wallet_address": "invalid_address",
        "activity_type": "solar_export",
        "value": 5.0
    }
    response = make_request("/v2/activities/submit", invalid_payload, API_KEYS["basic"], "POST")
    print(f"   Invalid wallet: {response.status_code} (expected 422)")
    
    print("→ Testing invalid activity type...")
    invalid_payload = {
        "wallet_address": owner_wallet,
        "activity_type": "invalid_activity",
        "value": 5.0
    }
    response = make_request("/v2/activities/submit", invalid_payload, API_KEYS["basic"], "POST")
    print(f"   Invalid activity type: {response.status_code} (expected 422)")
    
    print("→ Testing value out of range...")
    invalid_payload = {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 15000.0  # Exceeds 10000 limit
    }
    response = make_request("/v2/activities/submit", invalid_payload, API_KEYS["basic"], "POST")
    print(f"   Value too high: {response.status_code} (expected 422)")

def test_rate_limiting():
    """Test rate limiting with different API key tiers"""
    print("\n=== RATE LIMITING TESTS ===")
    
    print("→ Testing no API key rate limit...")
    response = make_request("/v2/activities/submit", {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 1.0
    }, None, "POST")
    print(f"   No API key: {response.status_code}")
    
    print("→ Testing invalid API key...")
    response = make_request("/v2/activities/submit", {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 1.0
    }, API_KEYS["invalid"], "POST")
    print(f"   Invalid API key: {response.status_code}")
    
    print("→ Testing basic tier value limit...")
    response = make_request("/v2/activities/submit", {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 150.0  # Exceeds basic tier 100 kWh limit
    }, API_KEYS["basic"], "POST")
    print(f"   Basic tier large value: {response.status_code} (expected 403)")

def test_api_authentication():
    """Test API authentication scenarios"""
    print("\n=== AUTHENTICATION TESTS ===")
    
    print("→ Testing endpoint without API key...")
    response = make_request("/v1/activities/submit", {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 1.0
    }, None, "POST")
    print(f"   No auth: {response.status_code} (expected 403)")
    
    print("→ Testing with invalid API key...")
    response = make_request("/v1/activities/submit", {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 1.0
    }, "totally_invalid_key", "POST")
    print(f"   Invalid auth: {response.status_code} (expected 403)")

def run_comprehensive_tests():
    """Run all test suites"""
    print("🧪 SILVANUS API COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    
    results = {}
    
    results['health'] = test_health_endpoint()
    results['activity_types'] = test_activity_types_endpoint()
    
    results['v1_endpoint'] = test_v1_endpoint()
    results['v2_endpoint'] = test_v2_endpoint()
    results['legacy_endpoint'] = test_legacy_endpoint()
    
    test_input_validation()
    test_rate_limiting()
    test_api_authentication()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All core functionality tests passed!")
    else:
        print("⚠️  Some tests failed - check logs above")

if __name__ == "__main__":
    run_comprehensive_tests()
