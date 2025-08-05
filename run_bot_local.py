#!/usr/bin/env python3
"""
Local bot runner for testing the service station operations bot.

This script starts a FastAPI server that can handle Telegram webhook requests
and process messages through the GPT → Airtable pipeline.
"""

import os
import asyncio
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# Load environment variables
load_dotenv('.env')

# Import our modules
from api.airtable_client import AirtableClient
from api.gpt_parser import GPTParser
from api.telegram_handler import TelegramHandler
from utils.logging_config import setup_logging

# Setup logging
setup_logging()

# Initialize global instances
airtable_client = None
gpt_parser = None
telegram_handler = None

def initialize_components():
    """Initialize all bot components."""
    global airtable_client, gpt_parser, telegram_handler
    
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
    
    # Initialize Telegram handler
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    if not telegram_token:
        raise ValueError("Missing Telegram token")
    
    telegram_handler = TelegramHandler()
    print("✅ Telegram handler initialized")

# Create FastAPI app
app = FastAPI(title="Service Station Ops Bot", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    try:
        initialize_components()
        print("🚀 Bot is ready!")
    except Exception as e:
        print(f"❌ Failed to initialize bot: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Service Station Operations Bot",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "webhook": "/telegram-webhook",
            "test": "/test-message"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "components": {
        "airtable": airtable_client is not None,
        "gpt": gpt_parser is not None,
        "telegram": telegram_handler is not None
    }}

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook requests."""
    try:
        # Get the webhook data
        webhook_data = await request.json()
        
        # Extract message
        if "message" not in webhook_data:
            return JSONResponse({"status": "ok", "message": "No message in webhook"})
        
        message = webhook_data["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if not text:
            return JSONResponse({"status": "ok", "message": "No text in message"})
        
        print(f"📝 Received message from chat {chat_id}: {text}")
        
        # Process the message
        response_text = await process_message(text)
        
        # Send response back to Telegram
        if telegram_handler:
            try:
                await telegram_handler.send_message(chat_id, response_text)
                print(f"🤖 Sent to Telegram: {response_text}")
            except Exception as e:
                print(f"❌ Failed to send to Telegram: {e}")
        
        return JSONResponse({"status": "ok", "response": response_text})
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-message")
async def test_message(request: Request):
    """Test endpoint for processing messages without Telegram."""
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            return JSONResponse({"error": "No message provided"}, status_code=400)
        
        print(f"🧪 Testing message: {message}")
        response_text = await process_message(message)
        
        return JSONResponse({
            "message": message,
            "response": response_text,
            "status": "success"
        })
        
    except Exception as e:
        print(f"❌ Error testing message: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

async def process_message(message: str) -> str:
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
        
        if not record_id:
            return "❌ Failed to save to database. Please try again."
        
        # Step 4: Generate confirmation message
        confirmation = gpt_parser.generate_confirmation_message(parsed_entry)
        return f"✅ {confirmation} (Record ID: {record_id})"
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        return f"❌ Error: {str(e)}"

def main():
    """Main function to run the bot locally."""
    print("🤖 Starting Service Station Operations Bot")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['TELEGRAM_TOKEN', 'OPENAI_API_KEY', 'AIRTABLE_API_KEY', 'AIRTABLE_BASE_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please check your .env file")
        return
    
    print("✅ Environment variables loaded")
    
    # Run the server
    print("\n🌐 Starting local server...")
    print("📱 Bot will be available at: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    print("🧪 Test endpoint: POST http://localhost:8000/test-message")
    print("\n💡 To test the bot:")
    print("   curl -X POST http://localhost:8000/test-message \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"message\": \"Paid 15,000 MWK for filter replacement\"}'")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "run_bot_local:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")

if __name__ == "__main__":
    main() 