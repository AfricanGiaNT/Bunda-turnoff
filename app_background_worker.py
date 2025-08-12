#!/usr/bin/env python3
"""
Background Worker application for Render deployment.
This version is designed to run as a Background Worker service that can still handle HTTP endpoints.
"""

import os
import json
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from socketserver import ThreadingMixIn
from typing import Optional
import threading

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules for telegram bot functionality
try:
    from api.airtable_client import AirtableClient
    from api.gpt_parser import GPTParser
    from api.telegram_handler import TelegramHandler
    from utils.logging_config import setup_logging
    
    # Setup proper logging
    setup_logging()
    logger = logging.getLogger(__name__)
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some modules not available: {e}")
    MODULES_AVAILABLE = False

# Global instances
airtable_client = None
gpt_parser = None
telegram_handler = None

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    allow_reuse_address = True
    daemon_threads = True

class BackgroundWorkerHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Background Worker."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "Service Station Operations Bot - Background Worker",
                "status": "running",
                "version": "1.0.0",
                "service_type": "background_worker",
                "modules_loaded": MODULES_AVAILABLE
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "Background Worker Bot is running",
                "airtable_ready": airtable_client is not None,
                "gpt_ready": gpt_parser is not None,
                "telegram_ready": telegram_handler is not None
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/telegram-webhook":
            # Handle GET requests to the webhook endpoint for testing
            logger.info("GET request to /telegram-webhook - This is for testing only")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "Webhook endpoint is active (Background Worker)"}
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/telegram-webhook":
            # Process Telegram webhook
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                # Log the received data
                logger.info(f"Received webhook data: {post_data.decode('utf-8')}")
                
                # Parse JSON data
                update = json.loads(post_data.decode('utf-8'))
                
                # Process the update asynchronously
                if MODULES_AVAILABLE and telegram_handler:
                    asyncio.create_task(process_telegram_update(update))
                else:
                    logger.warning("Telegram handler not available, skipping message processing")
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
            
            # Always respond with 200 OK to Telegram
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "Webhook received"}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/daily-summary":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Trigger daily summary if modules are available
            if MODULES_AVAILABLE:
                try:
                    asyncio.create_task(trigger_daily_summary())
                    response = {"status": "summary_triggered", "message": "Daily summary initiated"}
                except Exception as e:
                    logger.error(f"Error triggering summary: {e}")
                    response = {"status": "error", "message": str(e)}
            else:
                response = {"status": "unavailable", "message": "Summary modules not loaded"}
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Log all requests."""
        logger.info(f"{self.address_string()} - {format % args}")

async def process_telegram_update(update: dict):
    """Process Telegram update asynchronously."""
    try:
        if telegram_handler:
            await telegram_handler.process_update(update)
        else:
            logger.warning("Telegram handler not initialized")
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}")

async def trigger_daily_summary():
    """Trigger daily summary generation."""
    try:
        from api.summary_generator import generator
        await generator.send_summary_to_configured_chat()
        logger.info("Daily summary sent successfully")
    except Exception as e:
        logger.error(f"Error sending daily summary: {e}")

def initialize_components():
    """Initialize all bot components."""
    global airtable_client, gpt_parser, telegram_handler
    
    if not MODULES_AVAILABLE:
        logger.warning("Modules not available, running in minimal mode")
        return
    
    logger.info("🔧 Initializing bot components...")
    
    try:
        # Initialize Airtable client
        api_key = os.getenv('AIRTABLE_API_KEY')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        
        if api_key and base_id:
            airtable_client = AirtableClient(api_key, base_id)
            logger.info("✅ Airtable client initialized")
        else:
            logger.warning("⚠️ Airtable credentials missing")
        
        # Initialize GPT parser
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            gpt_parser = GPTParser(openai_key)
            logger.info("✅ GPT parser initialized")
        else:
            logger.warning("⚠️ OpenAI API key missing")
        
        # Initialize Telegram handler
        telegram_token = os.getenv('TELEGRAM_TOKEN')
        if telegram_token and airtable_client and gpt_parser:
            telegram_handler = TelegramHandler(telegram_token, airtable_client, gpt_parser)
            logger.info("✅ Telegram handler initialized")
        else:
            logger.warning("⚠️ Cannot initialize Telegram handler - missing dependencies")
            
    except Exception as e:
        logger.error(f"❌ Error initializing components: {e}")

def run_http_server(host='0.0.0.0', port=10000):
    """Run the HTTP server for webhook endpoints."""
    try:
        server_address = (host, port)
        httpd = ThreadedHTTPServer(server_address, BackgroundWorkerHTTPHandler)
        
        logger.info(f"🌐 HTTP Server starting on {host}:{port}")
        logger.info(f"🔗 Webhook URL: http://{host}:{port}/telegram-webhook")
        logger.info(f"❤️ Health check: http://{host}:{port}/health")
        
        # Run server in a separate thread so it doesn't block the main process
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        
        return httpd, server_thread
        
    except Exception as e:
        logger.error(f"❌ Failed to start HTTP server: {e}")
        return None, None

async def background_tasks():
    """Run background tasks (like periodic summaries)."""
    logger.info("🔄 Background tasks loop started")
    
    while True:
        try:
            # Add any periodic background tasks here
            # For example, health checks, cleanup, etc.
            
            # Sleep for 60 seconds before next iteration
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in background tasks: {e}")
            await asyncio.sleep(60)

def main():
    """Main function to run the Background Worker."""
    logger.info("🤖 Starting Service Station Operations Bot - Background Worker")
    logger.info("=" * 60)
    
    # Log environment information
    logger.info(f"🌍 Environment PORT: {os.environ.get('PORT', 'Not set')}")
    logger.info(f"🏗️ Service Type: Background Worker")
    logger.info(f"📦 Modules Available: {MODULES_AVAILABLE}")
    
    # Initialize components
    initialize_components()
    
    # Determine port to use
    # Background Workers don't get automatic PORT variable, so we use a fixed port
    # or check for a custom environment variable
    port = int(os.environ.get('WORKER_PORT', '10000'))
    host = '0.0.0.0'
    
    logger.info(f"🔌 Using port: {port} (Background Worker)")
    
    # Start HTTP server for webhooks
    httpd, server_thread = run_http_server(host, port)
    
    if not httpd:
        logger.error("❌ Failed to start HTTP server, exiting")
        return
    
    logger.info("🚀 Background Worker is ready!")
    logger.info("📱 Webhook endpoints are active")
    logger.info("⏹️  Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    try:
        # Run background tasks
        asyncio.run(background_tasks())
        
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down Background Worker...")
        if httpd:
            httpd.shutdown()
        logger.info("✅ Background Worker stopped")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in Background Worker: {e}")
        if httpd:
            httpd.shutdown()

if __name__ == "__main__":
    main()
