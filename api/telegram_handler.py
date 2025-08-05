"""
Telegram webhook/polling entrypoints for the service station operations bot.

Handles incoming messages from Telegram, processes them through GPT parsing,
and stores results in Airtable.
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Import our modules
from .airtable_client import AirtableClient
from .gpt_parser import GPTParser
from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class TelegramUpdate(BaseModel):
    """Telegram webhook update structure."""
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

class TelegramHandler:
    """Handles Telegram bot interactions."""
    
    def __init__(self):
        self.app = FastAPI(title="Service Station Ops Bot")
        self.airtable_client = None
        self.gpt_parser = None
        self.setup_routes()
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize bot components."""
        try:
            # Initialize Airtable client
            api_key = os.getenv('AIRTABLE_API_KEY')
            base_id = os.getenv('AIRTABLE_BASE_ID')
            
            if not api_key or not base_id:
                logger.error("Missing Airtable credentials")
                return
            
            self.airtable_client = AirtableClient(api_key, base_id)
            logger.info("✅ Airtable client initialized")
            
            # Initialize GPT parser
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                logger.error("Missing OpenAI API key")
                return
            
            self.gpt_parser = GPTParser(openai_key)
            logger.info("✅ GPT parser initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
    
    def setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.post("/telegram-webhook")
        async def telegram_webhook(update: TelegramUpdate):
            """Handle incoming Telegram webhook updates."""
            try:
                if update.message:
                    await self.process_message(update.message)
                elif update.callback_query:
                    await self.process_callback(update.callback_query)
                return {"status": "ok"}
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "airtable_ready": self.airtable_client is not None,
                "gpt_ready": self.gpt_parser is not None
            }
        
        @self.app.post("/daily-summary")
        async def trigger_daily_summary():
            """Manually trigger daily summary generation."""
            # TODO: Implement daily summary generation
            return {"status": "summary_triggered"}
    
    async def process_message(self, message: Dict[str, Any]):
        """Process incoming Telegram message."""
        try:
            # Extract message details
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            
            if not chat_id or not text:
                logger.warning("Invalid message format")
                return
            
            logger.info(f"📝 Received message from {chat_id}: {text}")
            
            # Handle commands
            if text.startswith('/'):
                await self.handle_command(chat_id, text)
                return
            
            # Process regular message
            response_text = await self.process_message_pipeline(text)
            await self.send_message(chat_id, response_text)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_message(chat_id, "❌ Sorry, there was an error processing your message. Please try again.")
    
    async def handle_command(self, chat_id: int, text: str):
        """Handle bot commands."""
        if text.startswith('/start'):
            welcome_message = """
🤖 **Service Station Operations Bot**

I can help you log:
• **Petty Cash Expenses** - "Spent 5000 on lunch"
• **Fuel Logs** - "Hilux used 40 liters"
• **Tasks** - "Assign John to safety inspection"
• **Issues** - "Urgent: Air compressor broken"

**NEW: Multiple Entries**
Separate multiple entries with semicolons (;):
"Spent 5000 on lunch; Hilux used 40 liters; Assign John to safety inspection"

Just send me a message and I'll process it automatically!
"""
            await self.send_message(chat_id, welcome_message)
        
        elif text.startswith('/help'):
            help_message = """
📋 **How to use this bot:**

**Single Entries:**
Just send a natural message and I'll understand!

**Multiple Entries (NEW!):**
Separate multiple entries with semicolons (;):

**Examples:**
• "Spent 5000 on lunch; Paid 20000 for generator fuel"
• "Hilux used 40 liters; Prado fueled 60 liters"
• "Assign John to safety inspection; Prepare client presentation"
• "Spent 5000 on lunch; Hilux used 40 liters; Assign John to safety inspection"

Just type naturally and I'll understand!
"""
            await self.send_message(chat_id, help_message)
    
    async def process_message_pipeline(self, message: str) -> str:
        """Process a message through the full pipeline."""
        try:
            if not self.gpt_parser or not self.airtable_client:
                return "❌ Bot is not properly initialized. Please try again later."
            
            # Check if message contains multiple entries separated by semicolons
            if ';' in message:
                return await self.process_multiple_entries_pipeline(message)
            else:
                return await self.process_single_entry_pipeline(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"❌ Error: {str(e)}"
    
    async def process_single_entry_pipeline(self, message: str) -> str:
        """Process a single entry through the pipeline."""
        try:
            # Step 1: Parse with GPT
            parsed_entry = await self.gpt_parser.parse_message(message)
            if not parsed_entry:
                return "❌ Failed to parse message. Please try again with clearer wording."
            
            # Step 2: Validate the parsed entry
            if not self.gpt_parser.validate_parsed_entry(parsed_entry):
                return "❌ Missing required fields. Please provide more details."
            
            # Step 3: Store in Airtable
            record_id = await self.store_entry_in_airtable(parsed_entry)
            if not record_id:
                return "❌ Failed to save to database. Please try again."
            
            # Step 4: Generate confirmation message
            confirmation = self.gpt_parser.generate_confirmation_message(parsed_entry)
            return f"✅ {confirmation} (Record ID: {record_id})"
            
        except Exception as e:
            logger.error(f"Error processing single entry: {e}")
            return f"❌ Error: {str(e)}"
    
    async def process_multiple_entries_pipeline(self, message: str) -> str:
        """Process multiple entries separated by semicolons."""
        try:
            # Step 1: Parse multiple entries with GPT
            parsed_entries = await self.gpt_parser.parse_multiple_entries(message)
            if not parsed_entries:
                return "❌ Failed to parse any entries. Please check your format and try again."
            
            # Step 2: Validate and store each entry
            successful_entries = []
            record_ids = []
            
            for i, entry in enumerate(parsed_entries, 1):
                # Validate the entry
                if not self.gpt_parser.validate_parsed_entry(entry):
                    logger.warning(f"Entry {i} failed validation: {entry}")
                    continue
                
                # Store in Airtable
                record_id = await self.store_entry_in_airtable(entry)
                if record_id:
                    successful_entries.append(entry)
                    record_ids.append(record_id)
                else:
                    logger.error(f"Entry {i} failed to store: {entry}")
            
            if not successful_entries:
                return "❌ No entries were successfully processed. Please check your format and try again."
            
            # Step 3: Generate confirmation message
            return self.gpt_parser.generate_multiple_confirmation_message(successful_entries, record_ids)
            
        except Exception as e:
            logger.error(f"Error processing multiple entries: {e}")
            return f"❌ Error: {str(e)}"
    
    async def store_entry_in_airtable(self, parsed_entry) -> Optional[str]:
        """Store a parsed entry in Airtable and return the record ID."""
        try:
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
                
                record_id = await self.airtable_client.create_task(data)
            
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
                
                record_id = await self.airtable_client.create_issue(data)
            
            return record_id
            
        except Exception as e:
            logger.error(f"Error storing entry in Airtable: {e}")
            return None
    
    async def process_callback(self, callback_query: Dict[str, Any]):
        """Process callback queries (for buttons, etc.)."""
        # TODO: Implement callback processing
        pass
    
    async def send_message(self, chat_id: int, text: str) -> bool:
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

# Global handler instance
handler = TelegramHandler()
app = handler.app 