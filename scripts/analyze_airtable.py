"""
Script to analyze Airtable base structure for Petty Cash and Fuel Log tables.
"""

import os
import asyncio
from dotenv import load_dotenv
from pyairtable import Api, Base, Table

# Load environment variables
load_dotenv('.env')

async def analyze_airtable_structure():
    """Analyze the Airtable base structure."""
    
    # Get credentials from environment
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not api_key or not base_id:
        print("❌ Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID in environment")
        return
    
    try:
        # Initialize Airtable API
        api = Api(api_key)
        base = api.base(base_id)
        
        print("🔍 Analyzing Airtable Base Structure...")
        print(f"Base ID: {base_id}")
        print()
        
        # Get all tables in the base
        tables = base.tables()
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table.name} (ID: {table.id})")
        print()
        
        # Analyze Petty Cash table
        print("💰 PETTY CASH TABLE ANALYSIS:")
        try:
            petty_cash_table = base.table('Petty Cash')
            petty_cash_schema = petty_cash_table.schema()
            
            print(f"  Table Name: {petty_cash_table.name}")
            print(f"  Table ID: {petty_cash_table.id}")
            print("  Fields:")
            for field in petty_cash_schema.fields:
                field_type = field.type
                field_name = field.name
                field_id = field.id
                print(f"    - {field_name} ({field_type}) [ID: {field_id}]")
                
                # Show options for select fields
                if hasattr(field, 'options') and field.options:
                    if hasattr(field.options, 'choices'):
                        print(f"      Options: {[opt.name for opt in field.options.choices]}")
            
            # Get sample records
            records = petty_cash_table.all(max_records=3)
            print(f"  Sample Records: {len(records)} found")
            if records:
                print("  First record fields:")
                for key, value in records[0]['fields'].items():
                    print(f"    {key}: {value}")
            
        except Exception as e:
            print(f"  ❌ Error analyzing Petty Cash table: {e}")
        
        print()
        
        # Analyze Fuel Log table
        print("⛽ FUEL LOG TABLE ANALYSIS:")
        try:
            fuel_log_table = base.table('Fuel Logs')
            fuel_log_schema = fuel_log_table.schema()
            
            print(f"  Table Name: {fuel_log_table.name}")
            print(f"  Table ID: {fuel_log_table.id}")
            print("  Fields:")
            for field in fuel_log_schema.fields:
                field_type = field.type
                field_name = field.name
                field_id = field.id
                print(f"    - {field_name} ({field_type}) [ID: {field_id}]")
                
                # Show options for select fields
                if hasattr(field, 'options') and field.options:
                    if hasattr(field.options, 'choices'):
                        print(f"      Options: {[opt.name for opt in field.options.choices]}")
            
            # Get sample records
            records = fuel_log_table.all(max_records=3)
            print(f"  Sample Records: {len(records)} found")
            if records:
                print("  First record fields:")
                for key, value in records[0]['fields'].items():
                    print(f"    {key}: {value}")
                    
        except Exception as e:
            print(f"  ❌ Error analyzing Fuel Log table: {e}")
        
        print()
        
        # Check for other tables
        print("📊 OTHER TABLES:")
        for table in tables:
            if table.name not in ['Petty Cash', 'Fuel Logs']:
                try:
                    schema = table.schema()
                    print(f"  {table.name}: {len(schema.fields)} fields")
                except Exception as e:
                    print(f"  {table.name}: Error reading schema - {e}")
        
    except Exception as e:
        print(f"❌ Error connecting to Airtable: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_airtable_structure()) 