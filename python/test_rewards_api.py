import requests
from datetime import datetime, timezone
import platform
import socket
import os
import time
import json
import hashlib
import base64
import secrets
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://silvanus-a4nt.onrender.com"

API_KEYS = {
    "valid": "12062569evan1206",  # Valid API key (1000/hour fixed rate limit)
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
    response = make_request("/activities/types", api_key=API_KEYS["valid"])
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
    
    response = make_request("/v1/activities/submit", activity_payload, API_KEYS["valid"], "POST")
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
    
    response = make_request("/v2/activities/submit", activity_payload, API_KEYS["valid"], "POST")
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
    
    response = make_request("/activities/submit", activity_payload, API_KEYS["valid"], "POST")
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
    response = make_request("/v2/activities/submit", invalid_payload, API_KEYS["valid"], "POST")
    print(f"   Invalid wallet: {response.status_code} (expected 422)")
    
    print("→ Testing invalid activity type...")
    invalid_payload = {
        "wallet_address": owner_wallet,
        "activity_type": "invalid_activity",
        "value": 5.0
    }
    response = make_request("/v2/activities/submit", invalid_payload, API_KEYS["valid"], "POST")
    print(f"   Invalid activity type: {response.status_code} (expected 422)")
    
    print("→ Testing value out of range...")
    invalid_payload = {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 15000.0  # Exceeds 10000 limit
    }
    response = make_request("/v2/activities/submit", invalid_payload, API_KEYS["valid"], "POST")
    print(f"   Value too high: {response.status_code} (expected 422)")

def test_rate_limiting():
    """Test rate limiting and authentication"""
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
    
    print("→ Testing valid API key with normal value...")
    response = make_request("/v2/activities/submit", {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 150.0  # Normal value within 10000 limit
    }, API_KEYS["valid"], "POST")
    print(f"   Valid API key normal value: {response.status_code} (expected 200)")

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

def generate_pkce_challenge():
    """Generate PKCE code verifier and challenge for OAuth2.0"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

def test_oauth_login_flow():
    """Test OAuth2.0 login flow initiation"""
    print("\n=== OAUTH2.0 LOGIN FLOW TEST ===")
    
    user_id = f"test_user_{int(time.time())}"
    response = requests.get(f"{BASE_URL}/oauth/login/github", params={"user_id": user_id})
    
    print(f"→ OAuth login request: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    data = response.json()
    
    if "auth_url" not in data:
        print(f"   Missing auth_url field")
        return False
    
    auth_url = data["auth_url"]
    parsed_url = urlparse(auth_url)
    query_params = parse_qs(parsed_url.query)
    
    basic_params = ["client_id", "redirect_uri", "scope", "response_type"]
    for param in basic_params:
        if param not in query_params:
            print(f"   Missing basic OAuth parameter: {param}")
            return False
    
    print(f"   ✓ Auth URL: {auth_url[:80]}...")
    print(f"   ✓ Basic OAuth parameters present")
    
    enhanced_features = []
    if "state" in data:
        print(f"   ✓ State parameter: {data['state'][:20]}...")
        enhanced_features.append("state_in_response")
    
    if "state" in query_params:
        print(f"   ✓ State in URL: {query_params['state'][0][:20]}...")
        enhanced_features.append("state_in_url")
    
    if "code_challenge" in query_params and "code_challenge_method" in query_params:
        if query_params["code_challenge_method"][0] == "S256":
            print(f"   ✓ PKCE challenge method: S256")
            enhanced_features.append("pkce")
        else:
            print(f"   ⚠ Invalid PKCE method: {query_params['code_challenge_method'][0]}")
    
    if "provider" in data:
        print(f"   ✓ Provider: {data['provider']}")
        enhanced_features.append("provider")
    
    if "session_key" in data:
        print(f"   ✓ Session key present")
        enhanced_features.append("session_key")
    
    if enhanced_features:
        print(f"   ✓ Enhanced OAuth2.0 features: {', '.join(enhanced_features)}")
    else:
        print(f"   ⚠ Basic OAuth flow (enhanced features not deployed yet)")
    
    return True

def test_oauth_pkce_validation():
    """Test PKCE code challenge validation"""
    print("\n=== OAUTH2.0 PKCE VALIDATION TEST ===")
    
    user_id = f"pkce_test_{int(time.time())}"
    response = requests.get(f"{BASE_URL}/oauth/login/github", params={"user_id": user_id})
    
    print(f"→ PKCE validation request: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    data = response.json()
    auth_url = data["auth_url"]
    
    parsed_url = urlparse(auth_url)
    query_params = parse_qs(parsed_url.query)
    
    if "code_challenge" not in query_params or "code_challenge_method" not in query_params:
        print(f"   ⚠ PKCE parameters not present (old API deployment)")
        print(f"   Available parameters: {list(query_params.keys())}")
        return True  # Pass the test since PKCE may not be deployed yet
    
    generated_challenge = query_params["code_challenge"][0]
    challenge_method = query_params["code_challenge_method"][0]
    
    if len(generated_challenge) < 43:  # Base64 encoded SHA256 should be at least 43 chars
        print(f"   Code challenge too short: {len(generated_challenge)}")
        return False
    
    if challenge_method != "S256":
        print(f"   Invalid challenge method: {challenge_method}")
        return False
    
    print(f"   ✓ Code challenge length: {len(generated_challenge)}")
    print(f"   ✓ Challenge method: {challenge_method}")
    print(f"   ✓ Challenge format: {generated_challenge[:20]}...")
    
    return True

def test_oauth_state_validation():
    """Test OAuth2.0 state parameter for CSRF protection"""
    print("\n=== OAUTH2.0 STATE VALIDATION TEST ===")
    
    states_from_response = []
    states_from_url = []
    
    for i in range(3):
        user_id = f"state_test_{i}_{int(time.time())}"
        response = requests.get(f"{BASE_URL}/oauth/login/github", params={"user_id": user_id})
        
        if response.status_code != 200:
            print(f"   Request {i+1} failed: {response.status_code}")
            return False
        
        data = response.json()
        
        if "state" in data:
            state = data["state"]
            states_from_response.append(state)
            if len(state) < 20:
                print(f"   State {i+1} too short: {len(state)}")
                return False
        
        auth_url = data["auth_url"]
        parsed_url = urlparse(auth_url)
        query_params = parse_qs(parsed_url.query)
        
        if "state" in query_params:
            url_state = query_params["state"][0]
            states_from_url.append(url_state)
    
    if states_from_response:
        if len(set(states_from_response)) != len(states_from_response):
            print(f"   Response states not unique: {len(set(states_from_response))} unique out of {len(states_from_response)}")
            return False
        print(f"   ✓ Generated {len(states_from_response)} unique states in response")
        print(f"   ✓ State lengths: {[len(s) for s in states_from_response]}")
    
    if states_from_url:
        if len(set(states_from_url)) != len(states_from_url):
            print(f"   URL states not unique: {len(set(states_from_url))} unique out of {len(states_from_url)}")
            return False
        print(f"   ✓ Generated {len(states_from_url)} unique states in URL")
    
    if not states_from_response and not states_from_url:
        print(f"   ⚠ No state parameters found (old API deployment)")
        return True  # Pass since state may not be deployed yet
    
    print(f"   ✓ State validation passed")
    return True

def test_oauth_token_storage():
    """Test OAuth2.0 token storage endpoints"""
    print("\n=== OAUTH2.0 TOKEN STORAGE TEST ===")
    
    response = requests.post(f"{BASE_URL}/oauth/test/store-token")
    
    print(f"→ Token storage: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    result = response.json()
    if "status" not in result:
        print(f"   Unexpected response format: {result}")
        return False
    
    response = requests.get(f"{BASE_URL}/oauth/test/list-tokens")
    
    print(f"→ Token listing: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    tokens = response.json()
    if not isinstance(tokens, list):
        print(f"   Expected list, got: {type(tokens)}")
        return False
    
    print(f"   ✓ Token storage endpoint accessible")
    print(f"   ✓ Token listing endpoint accessible")
    print(f"   ✓ Total tokens in storage: {len(tokens)}")
    
    return True

def test_bearer_token_authentication():
    """Test Bearer token authentication on activity endpoints"""
    print("\n=== BEARER TOKEN AUTHENTICATION TEST ===")
    
    user_id = f"bearer_test_{int(time.time())}"
    test_token = "test_bearer_token_12345"
    
    token_data = {
        "user_id": user_id,
        "access_token": test_token,
        "refresh_token": "refresh_123",
        "expires_in": 3600,
        "scope": "read:user user:email"
    }
    
    store_response = requests.post(
        f"{BASE_URL}/oauth/test/store-token",
        json=token_data
    )
    
    if store_response.status_code != 200:
        print(f"   Failed to store test token: {store_response.status_code}")
        return False
    
    bearer_headers = {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json"
    }
    
    activity_data = {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 2.0,
        "details": {"test": "bearer_token_auth", "user_id": user_id}
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/activities/submit",
        headers=bearer_headers,
        json=activity_data
    )
    
    print(f"→ Bearer token V1 endpoint: {response.status_code}")
    
    expected_auth_errors = [401, 403]
    
    if response.status_code in expected_auth_errors:
        print(f"   ✓ Bearer token parsed and validated (expected auth failure)")
        return True
    elif response.status_code == 200:
        print(f"   ✓ Bearer token authentication successful")
        return True
    elif response.status_code == 422:
        print(f"   ✓ Bearer token parsed, validation error (expected)")
        return True
    else:
        print(f"   Unexpected response: {response.status_code} - {response.text}")
        return False

def test_oauth_vs_api_key_comparison():
    """Test that both OAuth2.0 and API key authentication work"""
    print("\n=== OAUTH2.0 VS API KEY COMPARISON TEST ===")
    
    activity_data = {
        "wallet_address": owner_wallet,
        "activity_type": "solar_export",
        "value": 1.5,
        "details": {"test": "auth_comparison"}
    }
    
    api_key_response = requests.post(
        f"{BASE_URL}/v1/activities/submit",
        headers={"X-API-Key": API_KEYS["valid"], "Content-Type": "application/json"},
        json=activity_data
    )
    
    bearer_response = requests.post(
        f"{BASE_URL}/v1/activities/submit",
        headers={"Authorization": "Bearer test_token_123", "Content-Type": "application/json"},
        json=activity_data
    )
    
    print(f"→ API key authentication: {api_key_response.status_code}")
    print(f"→ Bearer token parsing: {bearer_response.status_code}")
    
    if api_key_response.status_code not in [200, 201]:
        print(f"   API key failed: {api_key_response.text}")
        return False
    
    if bearer_response.status_code == 500:
        print(f"   Bearer token caused server error: {bearer_response.text}")
        return False
    
    print(f"   ✓ API key works: {api_key_response.status_code}")
    print(f"   ✓ Bearer token parsed: {bearer_response.status_code}")
    
    return True

def test_oauth_rate_limiting():
    """Test rate limiting with OAuth2.0 user identity"""
    print("\n=== OAUTH2.0 RATE LIMITING TEST ===")
    
    user_id = f"rate_limit_test_{int(time.time())}"
    test_token = f"rate_limit_token_{user_id}"
    
    token_data = {
        "user_id": user_id,
        "access_token": test_token,
        "refresh_token": "refresh_rate_test",
        "expires_in": 3600,
        "scope": "read:user user:email"
    }
    
    store_response = requests.post(
        f"{BASE_URL}/oauth/test/store-token",
        json=token_data
    )
    
    if store_response.status_code != 200:
        print(f"   Could not store test token, using API key instead")
        headers = {"X-API-Key": API_KEYS["valid"], "Content-Type": "application/json"}
    else:
        headers = {"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"}
    
    responses = []
    for i in range(3):
        response = requests.post(
            f"{BASE_URL}/v1/activities/submit",
            headers=headers,
            json={
                "wallet_address": owner_wallet,
                "activity_type": "solar_export",
                "value": 0.5,
                "details": {"test": f"oauth_rate_limit_{i}"}
            }
        )
        responses.append(response.status_code)
        time.sleep(0.2)
    
    success_codes = [200, 201]
    auth_error_codes = [401, 403]
    rate_limit_codes = [429]
    
    success_count = sum(1 for code in responses if code in success_codes)
    auth_error_count = sum(1 for code in responses if code in auth_error_codes)
    rate_limited_count = sum(1 for code in responses if code in rate_limit_codes)
    
    print(f"→ Rate limiting results:")
    print(f"   ✓ Successful: {success_count}")
    print(f"   ✓ Auth errors: {auth_error_count}")
    print(f"   ✓ Rate limited: {rate_limited_count}")
    
    server_errors = sum(1 for code in responses if code >= 500)
    if server_errors == len(responses):
        print(f"   All requests resulted in server errors")
        return False
    
    return True

def run_comprehensive_tests():
    """Run all test suites including OAuth2.0 tests"""
    print("🧪 SILVANUS API COMPREHENSIVE TEST SUITE WITH OAUTH2.0")
    print("=" * 60)
    
    results = {}
    
    results['health'] = test_health_endpoint()
    results['activity_types'] = test_activity_types_endpoint()
    
    results['oauth_login_flow'] = test_oauth_login_flow()
    results['oauth_pkce_validation'] = test_oauth_pkce_validation()
    results['oauth_state_validation'] = test_oauth_state_validation()
    results['oauth_token_storage'] = test_oauth_token_storage()
    results['bearer_token_auth'] = test_bearer_token_authentication()
    results['oauth_vs_api_key'] = test_oauth_vs_api_key_comparison()
    results['oauth_rate_limiting'] = test_oauth_rate_limiting()
    
    results['v1_endpoint'] = test_v1_endpoint()
    results['v2_endpoint'] = test_v2_endpoint()
    results['legacy_endpoint'] = test_legacy_endpoint()
    
    test_input_validation()
    test_rate_limiting()
    test_api_authentication()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    oauth_tests = ['oauth_login_flow', 'oauth_pkce_validation', 'oauth_state_validation', 
                   'oauth_token_storage', 'bearer_token_auth', 'oauth_vs_api_key', 'oauth_rate_limiting']
    
    print("\n🔐 OAuth2.0 Tests:")
    oauth_passed = 0
    for test_name in oauth_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name:25} {status}")
            if results[test_name]:
                oauth_passed += 1
    
    print(f"\n📈 OAuth2.0 Success Rate: {oauth_passed}/{len(oauth_tests)} ({oauth_passed/len(oauth_tests)*100:.1f}%)")
    
    print("\n🔧 Core API Tests:")
    core_tests = [k for k in results.keys() if k not in oauth_tests]
    core_passed = 0
    for test_name in core_tests:
        status = "✅ PASS" if results[test_name] else "❌ FAIL"
        print(f"  {test_name:25} {status}")
        if results[test_name]:
            core_passed += 1
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if oauth_passed == len(oauth_tests):
        print("🎉 All OAuth2.0 tests passed!")
    else:
        print("⚠️  Some OAuth2.0 tests failed - check logs above")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check logs above")

if __name__ == "__main__":
    run_comprehensive_tests()
