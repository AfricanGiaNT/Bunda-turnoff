"""
Script to verify test records were created in Airtable.
"""

import asyncio
import os
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.airtable_client import AirtableClient
from utils.logging_config import setup_logging

# Load environment variables
load_dotenv('.env')

async def verify_records():
    """Verify that test records were created in Airtable."""
    print("🔍 Verifying Test Records in Airtable")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Initialize Airtable client
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not api_key or not base_id:
        print("❌ Missing Airtable credentials")
        return False
    
    try:
        client = AirtableClient(api_key, base_id)
        print("✅ Airtable client initialized")
        
        # Check Petty Cash records
        print("\n💰 Checking Petty Cash Records:")
        try:
            from pyairtable import Api
            api = Api(api_key)
            base = api.base(base_id)
            petty_cash_table = base.table("Petty Cash")
            
            # Get recent records (last 5)
            records = petty_cash_table.all(max_records=5)
            print(f"📋 Found {len(records)} recent petty cash records:")
            
            for i, record in enumerate(records, 1):
                fields = record['fields']
                print(f"  {i}. {fields.get('Description', 'No description')} - {fields.get('Amount', 0)} MWK")
                print(f"     Date: {fields.get('Date', 'No date')}")
                print(f"     Person: {fields.get('Person', 'No person')}")
                print(f"     Record ID: {record['id']}")
                print()
                
        except Exception as e:
            print(f"❌ Error checking petty cash records: {e}")
        
        # Check Fuel Log records
        print("\n⛽ Checking Fuel Log Records:")
        try:
            fuel_log_table = base.table("Fuel Logs")
            
            # Get recent records (last 5)
            records = fuel_log_table.all(max_records=5)
            print(f"📋 Found {len(records)} recent fuel log records:")
            
            for i, record in enumerate(records, 1):
                fields = record['fields']
                print(f"  {i}. {fields.get('Vehicle', 'No vehicle')} - {fields.get('Liters', 0)}L")
                print(f"     Driver: {fields.get('Driver', 'No driver')}")
                print(f"     Purpose: {fields.get('Purpose', 'No purpose')}")
                print(f"     Date: {fields.get('Date', 'No date')}")
                if fields.get('Odometer Start') and fields.get('Odometer End'):
                    kms = fields.get('Odometer End', 0) - fields.get('Odometer Start', 0)
                    print(f"     Distance: {kms} km")
                print(f"     Record ID: {record['id']}")
                print()
                
        except Exception as e:
            print(f"❌ Error checking fuel log records: {e}")
        
        print("=" * 50)
        print("✅ Verification completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in verification: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_records()) 