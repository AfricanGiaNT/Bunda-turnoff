"""
Test script for real implementation with sample messages.
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

async def test_real_implementation():
    """Test the real implementation with sample messages."""
    print("🧪 Testing Real Implementation")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Initialize components
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not all([api_key, base_id, openai_key]):
        print("❌ Missing required API keys")
        return False
    
    try:
        airtable_client = AirtableClient(api_key, base_id)
        gpt_parser = GPTParser(openai_key)
        print("✅ Components initialized")
        
        # Test messages
        test_messages = [
            "Paid 15,000 MWK for filter replacement from petty cash",
            "Gave 40 liters diesel to Hilux, driver John, for Salima trip. Odometer start 12300 end 12420"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Test {i}: {message}")
            print("-" * 40)
            
            try:
                # Step 1: Parse with GPT
                parsed_entry = await gpt_parser.parse_message(message)
                if not parsed_entry:
                    print("❌ Failed to parse message")
                    continue
                
                print(f"✅ Parsed: {parsed_entry.type.value}")
                print(f"   Data: {parsed_entry}")
                
                # Step 2: Validate
                if not gpt_parser.validate_parsed_entry(parsed_entry):
                    print("❌ Validation failed")
                    continue
                
                print("✅ Validation passed")
                
                # Step 3: Store in Airtable
                record_id = None
                if parsed_entry.type.value == "expense":
                    data = {
                        "date": parsed_entry.date,
                        "amount": parsed_entry.amount,
                        "description": parsed_entry.description,
                        "person": parsed_entry.person or "Me"
                    }
                    record_id = await airtable_client.create_expense(data)
                    
                elif parsed_entry.type.value == "fuel":
                    data = {
                        "date": parsed_entry.date,
                        "vehicle": parsed_entry.vehicle,
                        "driver": parsed_entry.driver,
                        "liters": parsed_entry.liters,
                        "purpose": parsed_entry.purpose or ""
                    }
                    if parsed_entry.odometer_start:
                        data["odometer_start"] = parsed_entry.odometer_start
                    if parsed_entry.odometer_end:
                        data["odometer_end"] = parsed_entry.odometer_end
                    
                    record_id = await airtable_client.create_fuel_log(data)
                
                if record_id:
                    print(f"✅ Stored in Airtable: {record_id}")
                    
                    # Step 4: Generate confirmation
                    confirmation = gpt_parser.generate_confirmation_message(parsed_entry)
                    print(f"✅ Confirmation: {confirmation}")
                else:
                    print("❌ Failed to store in Airtable")
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Real implementation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_real_implementation()) 