"""
Script to update .env file with template values.
"""

import os

def update_env_file():
    """Update .env file with template values."""
    
    env_content = """# Service Station Operations Bot - Environment Variables Template
# Copy this file to .env and fill in your actual values

# Telegram Bot Configuration
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Airtable Configuration
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here

# Application Configuration
DAILY_SUMMARY_TIME_UTC=15:00
STARTING_PETTY_CASH=100000
LOG_LEVEL=INFO
EXPORT_DIR=/tmp/exports

# Optional: Webhook URL for Telegram (if using webhooks instead of polling)
# TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram-webhook

# Optional: Database/Storage Configuration
# DATABASE_URL=sqlite:///./service_station.db

# Optional: Monitoring/Health Check
# HEALTH_CHECK_ENABLED=true
# HEALTH_CHECK_INTERVAL=300
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Updated .env file with template values")
    print("⚠️  IMPORTANT: You need to replace the placeholder values with your actual API keys and tokens")
    print("📝 Edit the .env file and replace:")
    print("   - your_telegram_bot_token_here")
    print("   - your_chat_id_here") 
    print("   - your_openai_api_key_here")
    print("   - your_airtable_api_key_here")
    print("   - your_airtable_base_id_here")

if __name__ == "__main__":
    update_env_file() 