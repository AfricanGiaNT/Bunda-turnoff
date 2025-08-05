#!/usr/bin/env python3
"""
Test script to verify webhook functionality locally.
"""

import asyncio
import uvicorn
from api.telegram_handler import app
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_health_endpoint():
    """Test the health endpoint."""
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    print("🏥 Health Check Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Health check passed!")
        return True
    else:
        print("❌ Health check failed!")
        return False

async def test_webhook_endpoint():
    """Test the webhook endpoint with sample data."""
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Sample Telegram update
    sample_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 123456789,
                "type": "private"
            },
            "date": 1234567890,
            "text": "Spent 5000 on lunch"
        }
    }
    
    print("🔗 Webhook Test:")
    response = client.post("/telegram-webhook", json=sample_update)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Webhook endpoint working!")
        return True
    else:
        print("❌ Webhook endpoint failed!")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Webhook Functionality")
    print("=" * 40)
    
    # Run tests
    health_ok = asyncio.run(test_health_endpoint())
    webhook_ok = asyncio.run(test_webhook_endpoint())
    
    print("\n📊 Test Results:")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Webhook Endpoint: {'✅ PASS' if webhook_ok else '❌ FAIL'}")
    
    if health_ok and webhook_ok:
        print("\n🎉 All tests passed! Ready for deployment.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main() 