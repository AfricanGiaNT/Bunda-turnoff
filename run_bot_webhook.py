#!/usr/bin/env python3
"""
Telegram bot with webhook for local development.
This version uses a local webhook instead of polling.
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging

# Load environment variables
load_dotenv('.env')

# Import our modules
from api.airtable_client import AirtableClient
from api.gpt_parser import GPTParser
from utils.logging_config import setup_logging

# Setup logging
setup_logging()

# Initialize global instances
airtable_client = None
gpt_parser = None

def initialize_components():
    """Initialize all bot components."""
    global airtable_client, gpt_parser
    
    print("🔧 Initializing bot components...")
    
    # Initialize Airtable client
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    
    if not api_key or not base_id:
        raise ValueError("Missing Airtable credentials")
    
    airtable_client = AirtableClient(api_key, base_id)
    print("✅ Airtable client initialized")
    
    # Initialize GPT parser
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        raise ValueError("Missing OpenAI API key")
    
    gpt_parser = GPTParser(openai_key)
    print("✅ GPT parser initialized")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming Telegram message."""
    try:
        message = update.message
        chat_id = message.chat.id
        text = message.text
        
        print(f"📝 Received message from {chat_id}: {text}")
        
        # Process the message through our pipeline
        response_text = await process_message_pipeline(text)
        
        # Send response back to user
        await message.reply_text(response_text)
        print(f"🤖 Sent response: {response_text}")
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        await message.reply_text("❌ Sorry, there was an error processing your message. Please try again.")

async def process_message_pipeline(message: str) -> str:
    """Process a message through the full pipeline."""
    try:
        print(f"📝 Processing message: {message}")
        
        # Step 1: Parse with GPT
        parsed_entry = await gpt_parser.parse_message(message)
        if not parsed_entry:
            return "❌ Failed to parse message. Please try again with clearer wording."
        
        print(f"✅ Parsed entry: {parsed_entry}")
        
        # Step 2: Validate the parsed entry
        if not gpt_parser.validate_parsed_entry(parsed_entry):
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
        
        elif parsed_entry.type.value == "task":
            data = {
                "date": parsed_entry.date,
                "task_title": parsed_entry.task_title,
                "details": parsed_entry.details or "",
                "status": parsed_entry.status or "To Do",
                "assigned_to": parsed_entry.assigned_to or "Nthambi"
            }
            if parsed_entry.deadline:
                data["deadline"] = parsed_entry.deadline
            
            record_id = await airtable_client.create_task(data)
        
        elif parsed_entry.type.value == "issue":
            # Use description if available, otherwise use task_title (for misclassified entries)
            description = parsed_entry.description or parsed_entry.task_title or "No description provided"
            
            # Fix status mapping for Issues table (only "Open" or "Resolved" allowed)
            issue_status = "Open"  # Default for new issues
            if parsed_entry.status and parsed_entry.status in ["Open", "Resolved"]:
                issue_status = parsed_entry.status
            
            data = {
                "date": parsed_entry.date,
                "description": description,
                "category": parsed_entry.category or "Other",
                "severity": parsed_entry.severity or "Low",
                "status": issue_status,
                "reported_by": parsed_entry.reported_by or "Nthambi"
            }
            
            record_id = await airtable_client.create_issue(data)
        
        if not record_id:
            return "❌ Failed to save to database. Please try again."
        
        # Step 4: Generate confirmation message
        confirmation = gpt_parser.generate_confirmation_message(parsed_entry)
        return f"✅ {confirmation} (Record ID: {record_id})"
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        return f"❌ Error: {str(e)}"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_message = """
🤖 **Service Station Operations Bot**

I can help you log:
• **Petty Cash Expenses** - "Spent 5000 on lunch"
• **Fuel Logs** - "Hilux used 40 liters"
• **Tasks** - "Assign John to safety inspection"
• **Issues** - "Urgent: Air compressor broken"

Just send me a message and I'll process it automatically!

Examples:
• "Paid 15,000 for generator fuel"
• "Prado used 60 liters for site visit"
• "Assign Sarah to prepare monthly report"
• "Urgent: Fuel supply running low"
"""
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_message = """
📋 **How to use this bot:**

**Petty Cash Expenses:**
• "Spent 5000 on lunch"
• "Paid 20000 for generator fuel"
• "Emergency repairs cost 15000"

**Fuel Logs:**
• "Hilux used 40 liters"
• "Prado fueled 60 liters for site visit"
• "Gave John 50 liters for delivery"

**Tasks:**
• "Assign John to safety inspection by Friday"
• "Prepare client presentation by next week"
• "Inspect site equipment"
• "Review project timeline"

**Issues:**
• "Urgent: Air compressor malfunctioning"
• "Fuel supply running low"
• "Customer complaint about service"
• "Equipment fault in generator"

**With more details:**
• "Hilux used 45 liters, odometer 12300 to 12420, driver Peter"
• "Paid 12000 for tools, receipt at https://example.com/receipt.jpg"
• "Assign Sarah to prepare monthly report by Monday"

Just type naturally and I'll understand!
"""
    await update.message.reply_text(help_message)

def main():
    """Main function to run the bot with webhook."""
    print("🤖 Starting Service Station Operations Bot (Webhook)")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['TELEGRAM_TOKEN', 'OPENAI_API_KEY', 'AIRTABLE_API_KEY', 'AIRTABLE_BASE_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please check your .env file")
        return
    
    print("✅ Environment variables loaded")
    
    # Initialize components
    try:
        initialize_components()
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        return
    
    # Get bot token
    token = os.getenv('TELEGRAM_TOKEN')
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(MessageHandler(filters.COMMAND, start_command))
    application.add_handler(MessageHandler(filters.Regex(r'^/help'), help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))
    
    print("🚀 Bot is ready!")
    print("📱 Send messages to your bot in Telegram")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    # For now, just use polling but with better error handling
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            timeout=60,
            read_timeout=60,
            write_timeout=60,
            connect_timeout=60,
            pool_timeout=60
        )
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 This might be a network issue. Please check your internet connection.")

if __name__ == "__main__":
    main() 