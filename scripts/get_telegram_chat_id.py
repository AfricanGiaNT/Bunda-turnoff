#!/usr/bin/env python3
"""
Script to get your Telegram chat ID for bot integration.
"""

import os
import asyncio
from dotenv import load_dotenv
import telegram

# Load environment variables
load_dotenv('.env')

async def get_chat_id():
    """Get the chat ID for the bot."""
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ No TELEGRAM_TOKEN found in .env file")
        return
    
    print("🤖 Getting Telegram Chat ID")
    print("=" * 40)
    print("1. Open Telegram")
    print("2. Search for your bot (the one you created)")
    print("3. Send any message to the bot (like 'hello')")
    print("4. This script will show your chat ID")
    print("=" * 40)
    
    try:
        bot = telegram.Bot(token=token)
        
        # Get updates
        updates = await bot.get_updates()
        
        if not updates:
            print("📱 No messages found. Please send a message to your bot first.")
            print("💡 Make sure you've started a conversation with your bot in Telegram.")
            return
        
        print(f"📋 Found {len(updates)} message(s):")
        print()
        
        for i, update in enumerate(updates, 1):
            if update.message:
                chat_id = update.message.chat.id
                chat_type = update.message.chat.type
                user_name = update.message.from_user.first_name
                message_text = update.message.text
                
                print(f"Message {i}:")
                print(f"  Chat ID: {chat_id}")
                print(f"  Chat Type: {chat_type}")
                print(f"  User: {user_name}")
                print(f"  Message: {message_text}")
                print()
        
        if updates:
            latest_chat_id = updates[-1].message.chat.id
            print("✅ Add this to your .env file:")
            print(f"TELEGRAM_CHAT_ID={latest_chat_id}")
            print()
            print("🔗 Then you can send messages like:")
            print("   'Spent 5000 on lunch'")
            print("   'Hilux used 40 liters'")
            print("   'Paid 20000 for generator fuel'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your TELEGRAM_TOKEN is correct")

if __name__ == "__main__":
    asyncio.run(get_chat_id()) 