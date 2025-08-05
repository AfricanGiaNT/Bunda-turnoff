#!/usr/bin/env python3
"""
Analyze Tasks and Issues tables in Airtable base.
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv('.env')

def analyze_tasks_issues():
    """Analyze the Tasks and Issues tables structure."""
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not api_key or not base_id:
        print("❌ Missing Airtable credentials")
        return
    
    api = Api(api_key)
    base = api.base(base_id)
    
    print("🔍 Analyzing Tasks and Issues Tables")
    print("=" * 50)
    
    # Analyze Tasks table
    print("\n📋 TASKS TABLE ANALYSIS:")
    print("-" * 30)
    try:
        tasks_table = base.table("Tasks")
        tasks_schema = tasks_table.schema()
        
        print(f"Table Name: {tasks_schema.name}")
        print(f"Table ID: {tasks_schema.id}")
        print(f"Number of fields: {len(tasks_schema.fields)}")
        
        print("\nFields:")
        for i, field in enumerate(tasks_schema.fields, 1):
            print(f"  {i}. {field.name} ({field.type})")
            if field.type == 'singleSelect' and field.options and field.options.choices:
                choices = [choice.name for choice in field.options.choices]
                print(f"     Choices: {', '.join(choices)}")
            elif field.type == 'multipleSelects' and field.options and field.options.choices:
                choices = [choice.name for choice in field.options.choices]
                print(f"     Choices: {', '.join(choices)}")
        
        # Get some sample records
        print(f"\nSample Records (first 3):")
        records = tasks_table.all(max_records=3)
        for i, record in enumerate(records, 1):
            print(f"  Record {i}: {record['fields']}")
            
    except Exception as e:
        print(f"❌ Error analyzing Tasks table: {e}")
    
    # Analyze Issues table
    print("\n\n🚨 ISSUES TABLE ANALYSIS:")
    print("-" * 30)
    try:
        issues_table = base.table("Issues")
        issues_schema = issues_table.schema()
        
        print(f"Table Name: {issues_schema.name}")
        print(f"Table ID: {issues_schema.id}")
        print(f"Number of fields: {len(issues_schema.fields)}")
        
        print("\nFields:")
        for i, field in enumerate(issues_schema.fields, 1):
            print(f"  {i}. {field.name} ({field.type})")
            if field.type == 'singleSelect' and field.options and field.options.choices:
                choices = [choice.name for choice in field.options.choices]
                print(f"     Choices: {', '.join(choices)}")
            elif field.type == 'multipleSelects' and field.options and field.options.choices:
                choices = [choice.name for choice in field.options.choices]
                print(f"     Choices: {', '.join(choices)}")
        
        # Get some sample records
        print(f"\nSample Records (first 3):")
        records = issues_table.all(max_records=3)
        for i, record in enumerate(records, 1):
            print(f"  Record {i}: {record['fields']}")
            
    except Exception as e:
        print(f"❌ Error analyzing Issues table: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Analysis completed!")

if __name__ == "__main__":
    analyze_tasks_issues() 