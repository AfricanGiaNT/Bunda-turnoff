#!/usr/bin/env python3
"""
Script to set up Telegram webhook URL after deploying to Render.
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv('.env')

async def setup_webhook(render_url: str):
    """Set up webhook URL for Telegram bot."""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            print("❌ TELEGRAM_TOKEN not found in environment variables")
            return False
        
        bot = Bot(token=token)
        
        # Set webhook URL
        webhook_url = f"{render_url}/telegram-webhook"
        print(f"🔗 Setting webhook URL: {webhook_url}")
        
        success = await bot.set_webhook(url=webhook_url)
        
        if success:
            print("✅ Webhook set successfully!")
            
            # Get webhook info
            webhook_info = await bot.get_webhook_info()
            print(f"📊 Webhook Info:")
            print(f"   URL: {webhook_info.url}")
            print(f"   Has custom certificate: {webhook_info.has_custom_certificate}")
            print(f"   Pending update count: {webhook_info.pending_update_count}")
            print(f"   Last error date: {webhook_info.last_error_date}")
            print(f"   Last error message: {webhook_info.last_error_message}")
            
            return True
        else:
            print("❌ Failed to set webhook")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

async def remove_webhook():
    """Remove webhook and switch to polling."""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            print("❌ TELEGRAM_TOKEN not found in environment variables")
            return False
        
        bot = Bot(token=token)
        
        print("🔄 Removing webhook...")
        success = await bot.delete_webhook()
        
        if success:
            print("✅ Webhook removed successfully!")
            return True
        else:
            print("❌ Failed to remove webhook")
            return False
            
    except Exception as e:
        print(f"❌ Error removing webhook: {e}")
        return False

async def get_webhook_info():
    """Get current webhook information."""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            print("❌ TELEGRAM_TOKEN not found in environment variables")
            return False
        
        bot = Bot(token=token)
        
        webhook_info = await bot.get_webhook_info()
        print(f"📊 Current Webhook Info:")
        print(f"   URL: {webhook_info.url}")
        print(f"   Has custom certificate: {webhook_info.has_custom_certificate}")
        print(f"   Pending update count: {webhook_info.pending_update_count}")
        print(f"   Last error date: {webhook_info.last_error_date}")
        print(f"   Last error message: {webhook_info.last_error_message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
        return False

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/setup_webhook.py set <render_url>")
        print("  python scripts/setup_webhook.py remove")
        print("  python scripts/setup_webhook.py info")
        print("\nExamples:")
        print("  python scripts/setup_webhook.py set https://your-app.onrender.com")
        print("  python scripts/setup_webhook.py remove")
        print("  python scripts/setup_webhook.py info")
        return
    
    command = sys.argv[1]
    
    if command == "set":
        if len(sys.argv) < 3:
            print("❌ Please provide the Render URL")
            print("Example: python scripts/setup_webhook.py set https://your-app.onrender.com")
            return
        
        render_url = sys.argv[2]
        if not render_url.startswith("https://"):
            print("❌ Render URL must start with https://")
            return
        
        asyncio.run(setup_webhook(render_url))
    
    elif command == "remove":
        asyncio.run(remove_webhook())
    
    elif command == "info":
        asyncio.run(get_webhook_info())
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: set, remove, info")

if __name__ == "__main__":
    main() 