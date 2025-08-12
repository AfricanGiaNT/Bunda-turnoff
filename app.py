#!/usr/bin/env python3
"""
Main application entry point for Render deployment.
This file serves as the primary entry point for the service.
"""

import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from socketserver import ThreadingMixIn

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "Service Station Operations Bot API",
                "status": "running",
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "Bot is running"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/telegram-webhook":
            # Handle GET requests to the webhook endpoint for testing
            logger.info("GET request to /telegram-webhook - This is for testing only")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "Webhook endpoint is active"}
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
                
                # Extract message if available
                message = update.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                if chat_id and text:
                    logger.info(f"Received message from {chat_id}: {text}")
                    # Here you would process the message
                    # For now, just log it
                
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
            response = {"status": "summary_triggered", "message": "Daily summary endpoint"}
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

def run_server(host='0.0.0.0', port=8000):
    """Run the HTTP server."""
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, SimpleHTTPRequestHandler)
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Server running at http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()

if __name__ == "__main__":
    # Get port from environment variable or use default
    port_str = os.environ.get('PORT', '8000')
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
        logger.warning(f"Invalid PORT value '{port_str}', using default port 8000")
    
    logger.info(f"Environment PORT: {os.environ.get('PORT', 'Not set')}")
    logger.info(f"Using port: {port}")
    run_server(host='0.0.0.0', port=port)
