"""
Simplified FastAPI application entry point for the Service Station Operations Bot.
This version removes the startup event to avoid potential compatibility issues.
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Service Station Operations Bot",
    description="Telegram bot for managing service station operations",
    version="1.0.0"
)

class TelegramUpdate(BaseModel):
    """Telegram webhook update structure."""
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

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
        "message": "Bot is running"
    }

@app.post("/telegram-webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle incoming Telegram webhook updates."""
    try:
        # Simple response for now
        return {"status": "ok", "message": "Webhook received"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/daily-summary")
async def trigger_daily_summary():
    """Manually trigger daily summary generation."""
    return {"status": "summary_triggered", "message": "Daily summary endpoint"}

if __name__ == "__main__":
    import os
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
    logger.info(f"Starting simplified FastAPI server on 0.0.0.0:{port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
