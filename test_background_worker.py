#!/usr/bin/env python3
"""
Test script for the Background Worker application.
This script validates that the Background Worker can handle HTTP requests properly.
"""

import requests
import json
import time
import sys

def test_endpoint(url, method='GET', data=None, expected_status=200):
    """Test an endpoint and return the result."""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"✅ {method} {url}")
        print(f"   Status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"   Response: {json.dumps(json_data, indent=2)}")
            except:
                print(f"   Response: {response.text}")
        else:
            print(f"   Response: {response.text}")
        
        if response.status_code == expected_status:
            print("   ✅ Status code matches expected")
            return True
        else:
            print(f"   ❌ Expected {expected_status}, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {url}")
        print(f"   Error: {e}")
        return False

def main():
    """Run tests against the Background Worker."""
    base_url = "http://localhost:10000"
    
    print("🧪 Testing Background Worker Application")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print()
    
    # Wait a moment for server to start
    print("⏳ Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    tests = [
        {
            "name": "Root Endpoint",
            "url": f"{base_url}/",
            "method": "GET",
            "expected": 200
        },
        {
            "name": "Health Check",
            "url": f"{base_url}/health",
            "method": "GET", 
            "expected": 200
        },
        {
            "name": "Webhook GET (Test)",
            "url": f"{base_url}/telegram-webhook",
            "method": "GET",
            "expected": 200
        },
        {
            "name": "Webhook POST (Simulation)",
            "url": f"{base_url}/telegram-webhook",
            "method": "POST",
            "data": {
                "update_id": 123,
                "message": {
                    "message_id": 456,
                    "chat": {"id": 789, "type": "private"},
                    "text": "Test message",
                    "date": 1234567890
                }
            },
            "expected": 200
        },
        {
            "name": "Daily Summary Trigger",
            "url": f"{base_url}/daily-summary",
            "method": "POST",
            "expected": 200
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        print(f"Test {i}/{total}: {test['name']}")
        print("-" * 30)
        
        success = test_endpoint(
            test['url'],
            test['method'],
            test.get('data'),
            test['expected']
        )
        
        if success:
            passed += 1
        
        print()
    
    print("=" * 50)
    print(f"🏆 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! Background Worker is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
