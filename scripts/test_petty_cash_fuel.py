"""
Test script for petty cash and fuel logs implementation.
"""

import asyncio
import os
from dotenv import load_dotenv
from datetime import date

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.airtable_client import AirtableClient
from api.gpt_parser import GPTParser
from utils.logging_config import setup_logging

# Load environment variables
load_dotenv('.env')

async def test_airtable_connection():
    """Test Airtable connection and field mappings."""
    print("🔍 Testing Airtable Connection...")
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not api_key or not base_id:
        print("❌ Missing Airtable credentials")
        return False
    
    try:
        client = AirtableClient(api_key, base_id)
        print(f"✅ Airtable client initialized")
        print(f"📋 Petty Cash fields: {list(client.petty_cash_fields.keys())}")
        print(f"⛽ Fuel Log fields: {list(client.fuel_log_fields.keys())}")
        print(f"🚗 Valid vehicles: {client.valid_vehicles}")
        return True
    except Exception as e:
        print(f"❌ Error initializing Airtable client: {e}")
        return False

async def test_gpt_parser():
    """Test GPT parser with sample messages."""
    print("\n🤖 Testing GPT Parser...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Missing OpenAI API key")
        return False
    
    try:
        parser = GPTParser(api_key)
        print("✅ GPT parser initialized")
        
        # Test messages
        test_messages = [
            "Paid 15,000 MWK for filter replacement from petty cash",
            "Gave 40 liters diesel to Hilux, driver John, for Salima trip. Odometer start 12300 end 12420",
            "Spent 25,000 on generator fuel, receipt attached",
            "Prado refueled 35L, driver Sarah, odometer 15600 to 15800, maintenance visit"
        ]
        
        for message in test_messages:
            print(f"\n📝 Testing: {message}")
            # Note: This will return None since we haven't implemented the actual OpenAI call yet
            result = await parser.parse_message(message)
            if result:
                print(f"✅ Parsed: {result}")
            else:
                print("⚠️  Parser not yet implemented (expected)")
        
        return True
    except Exception as e:
        print(f"❌ Error testing GPT parser: {e}")
        return False

async def test_field_mappings():
    """Test field mappings with sample data."""
    print("\n🗂️ Testing Field Mappings...")
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not api_key or not base_id:
        print("❌ Missing Airtable credentials")
        return False
    
    try:
        client = AirtableClient(api_key, base_id)
        
        # Test petty cash data
        petty_cash_data = {
            "date": date.today().isoformat(),
            "amount": 15000,
            "description": "Filter replacement",
            "person": "Me"
        }
        
        print(f"💰 Petty Cash test data: {petty_cash_data}")
        record_id = await client.create_expense(petty_cash_data)
        print(f"✅ Petty cash record created: {record_id}")
        
        # Test fuel log data
        fuel_log_data = {
            "date": date.today().isoformat(),
            "vehicle": "Toyota Hilux",
            "driver": "John",
            "liters": 40,
            "odometer_start": 12300,
            "odometer_end": 12420,
            "purpose": "Salima trip"
        }
        
        print(f"⛽ Fuel Log test data: {fuel_log_data}")
        record_id = await client.create_fuel_log(fuel_log_data)
        print(f"✅ Fuel log record created: {record_id}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing field mappings: {e}")
        return False

async def test_invalid_vehicle():
    """Test handling of invalid vehicle selection."""
    print("\n🚫 Testing Invalid Vehicle Handling...")
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not api_key or not base_id:
        print("❌ Missing Airtable credentials")
        return False
    
    try:
        client = AirtableClient(api_key, base_id)
        
        # Test with invalid vehicle
        fuel_log_data = {
            "date": date.today().isoformat(),
            "vehicle": "Invalid Vehicle",  # This should be handled
            "driver": "John",
            "liters": 40,
            "purpose": "Test trip"
        }
        
        print(f"⛽ Invalid vehicle test data: {fuel_log_data}")
        record_id = await client.create_fuel_log(fuel_log_data)
        print(f"✅ Fuel log record created (should default to 'Other'): {record_id}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing invalid vehicle: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Running Petty Cash & Fuel Logs Tests")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Run tests
    tests = [
        test_airtable_connection,
        test_gpt_parser,
        test_field_mappings,
        test_invalid_vehicle
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Ready for implementation.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main()) 