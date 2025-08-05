"""
Test script for Telegram bot functionality with real message processing.
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

class TelegramBotTester:
    """Test class for Telegram bot functionality."""
    
    def __init__(self):
        self.airtable_client = None
        self.gpt_parser = None
        
    async def initialize(self):
        """Initialize the bot components."""
        print("🔧 Initializing bot components...")
        
        # Initialize Airtable client
        api_key = os.getenv('AIRTABLE_API_KEY')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        
        if not api_key or not base_id:
            print("❌ Missing Airtable credentials")
            return False
        
        self.airtable_client = AirtableClient(api_key, base_id)
        print("✅ Airtable client initialized")
        
        # Initialize GPT parser
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("❌ Missing OpenAI API key")
            return False
        
        self.gpt_parser = GPTParser(openai_key)
        print("✅ GPT parser initialized")
        
        return True
    
    async def process_message(self, message: str) -> str:
        """Process a message through the full pipeline."""
        try:
            print(f"\n📝 Processing message: {message}")
            
            # Step 1: Parse with GPT
            parsed_entry = await self.gpt_parser.parse_message(message)
            if not parsed_entry:
                return "❌ Failed to parse message. Please try again with clearer wording."
            
            print(f"✅ Parsed entry: {parsed_entry}")
            
            # Step 2: Validate the parsed entry
            if not self.gpt_parser.validate_parsed_entry(parsed_entry):
                return "❌ Missing required fields. Please provide more details."
            
            # Step 3: Store in Airtable
            record_id = None
            if parsed_entry.type.value == "expense":
                data = {
                    "date": parsed_entry.date,
                    "amount": parsed_entry.amount,
                    "description": parsed_entry.description,
                    "person": parsed_entry.person or "Me"
                }
                if parsed_entry.receipt_url:
                    data["receipt_url"] = parsed_entry.receipt_url
                
                record_id = await self.airtable_client.create_expense(data)
                
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
                
                record_id = await self.airtable_client.create_fuel_log(data)
            
            if not record_id:
                return "❌ Failed to save to database. Please try again."
            
            # Step 4: Generate confirmation message
            confirmation = self.gpt_parser.generate_confirmation_message(parsed_entry)
            return f"✅ {confirmation} (Record ID: {record_id})"
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return f"❌ Error: {str(e)}"
    
    async def run_interactive_test(self):
        """Run an interactive test session."""
        print("\n🤖 Starting Interactive Test Session")
        print("=" * 50)
        print("Type messages to test the bot. Type 'quit' to exit.")
        print("Example messages:")
        print("- Paid 15,000 MWK for filter replacement from petty cash")
        print("- Gave 40 liters diesel to Hilux, driver John, for Salima trip")
        print("- Spent 25,000 on generator fuel, receipt attached")
        print("=" * 50)
        
        while True:
            try:
                message = input("\n💬 Enter message: ").strip()
                
                if message.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not message:
                    continue
                
                response = await self.process_message(message)
                print(f"🤖 Bot: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function."""
    print("🧪 Telegram Bot Tester")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Initialize tester
    tester = TelegramBotTester()
    if not await tester.initialize():
        print("❌ Failed to initialize bot components")
        return
    
    # Run interactive test
    await tester.run_interactive_test()

if __name__ == "__main__":
    asyncio.run(main()) 