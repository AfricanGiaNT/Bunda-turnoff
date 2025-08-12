"""
Main FastAPI application entry point for the Service Station Operations Bot.
This file serves as the entry point for uvicorn deployment.
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from api.airtable_client import AirtableClient
from api.gpt_parser import GPTParser
from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Service Station Operations Bot",
    description="Telegram bot for managing service station operations, fuel logs, petty cash, and tasks/issues",
    version="1.0.0"
)

# Global variables for components
airtable_client = None
gpt_parser = None

class TelegramUpdate(BaseModel):
    """Telegram webhook update structure."""
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global airtable_client, gpt_parser
    
    try:
        # Initialize Airtable client
        api_key = os.getenv('AIRTABLE_API_KEY')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        
        if not api_key or not base_id:
            logger.error("Missing Airtable credentials")
            return
        
        airtable_client = AirtableClient(api_key, base_id)
        logger.info("✅ Airtable client initialized")
        
        # Initialize GPT parser
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.error("Missing OpenAI API key")
            return
        
        gpt_parser = GPTParser(openai_key)
        logger.info("✅ GPT parser initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Service Station Operations Bot API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "airtable_ready": airtable_client is not None,
        "gpt_ready": gpt_parser is not None
    }

@app.post("/telegram-webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle incoming Telegram webhook updates."""
    try:
        if update.message:
            await process_message(update.message)
        elif update.callback_query:
            await process_callback(update.callback_query)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/daily-summary")
async def trigger_daily_summary():
    """Manually trigger daily summary generation."""
    try:
        from api.summary_generator import generator
        await generator.send_summary_to_configured_chat()
        return {"status": "summary_triggered"}
    except Exception as e:
        logger.error(f"Error triggering daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_message(message: Dict[str, Any]):
    """Process incoming Telegram message."""
    try:
        if not gpt_parser:
            logger.error("GPT parser not initialized")
            return
        
        # Extract text from message
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        
        if not text:
            return
        
        logger.info(f"Processing message: {text[:100]}...")
        
        # Parse with GPT
        parsed_entry = await gpt_parser.parse_message(text)
        
        if parsed_entry:
            # Store in Airtable
            record_id = await store_entry_in_airtable(parsed_entry)
            
            if record_id:
                response = f"✅ Entry recorded successfully! Record ID: {record_id}"
            else:
                response = "❌ Failed to store entry in database"
        else:
            response = "❌ Could not parse message. Please try again with clearer information."
        
        # Send response back to user
        if chat_id:
            await send_message(chat_id, response)
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")

async def store_entry_in_airtable(parsed_entry) -> Optional[str]:
    """Store a parsed entry in Airtable and return the record ID."""
    try:
        if not airtable_client:
            logger.error("Airtable client not initialized")
            return None
            
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
            description = parsed_entry.description or parsed_entry.task_title or "No description provided"
            issue_status = "Open"
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
        
        return record_id
        
    except Exception as e:
        logger.error(f"Error storing entry in Airtable: {e}")
        return None

async def process_callback(callback_query: Dict[str, Any]):
    """Process callback queries (for buttons, etc.)."""
    # TODO: Implement callback processing
    pass

async def send_message(chat_id: int, text: str) -> bool:
    """Send message back to Telegram user."""
    try:
        from telegram import Bot
        
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            logger.error("No TELEGRAM_TOKEN found")
            return False
        
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Sent message to {chat_id}: {text}")
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable with validation
    port_str = os.environ.get('PORT', '8000')
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
        logger.warning(f"Invalid PORT value '{port_str}', using default port 8000")
    
    logger.info(f"Environment PORT: {os.environ.get('PORT', 'Not set')}")
    logger.info(f"Using port: {port}")
    logger.info(f"Starting FastAPI server on 0.0.0.0:{port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
