import requests
import json
import os
from datetime import datetime
import time

def test_endpoint(endpoint_path, value, description):
    print(f"\n=== Testing {description} ===")
    response = requests.post(
        f'https://silvanus-a4nt.onrender.com{endpoint_path}',
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': '12062569evan1206'
        },
        json={
            'wallet_address': os.getenv('RECIPIENT_WALLET_ADDRESS'),
            'activity_type': 'solar_export',
            'value': value,
            'details': {'note': f'Debug test - {description}', 'timestamp': datetime.now().isoformat()}
        }
    )
    
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
    return response.status_code

test_endpoint('/v2/activities/submit', 15000.0, 'V2 endpoint with 15000.0 kWh')
test_endpoint('/v1/activities/submit', 15000.0, 'V1 endpoint with 15000.0 kWh') 
test_endpoint('/activities/submit', 15000.0, 'Legacy endpoint with 15000.0 kWh')

print("\nCheck Transaction Explorer at https://silvanusproject.com for any new token distributions")
