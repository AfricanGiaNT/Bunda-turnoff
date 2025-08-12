#!/bin/bash
# Script to set up the webhook for your Render deployment

# Check if the URL was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <render_url>"
  echo "Example: $0 https://service-station-ops-bot.onrender.com"
  exit 1
fi

RENDER_URL=$1

# Run the setup_webhook.py script
echo "Setting up webhook for $RENDER_URL..."
python scripts/setup_webhook.py set $RENDER_URL

# Check the result
if [ $? -eq 0 ]; then
  echo "Webhook setup successful!"
  echo "Your bot should now receive messages from Telegram."
  echo "To test, send a message to your bot in Telegram."
else
  echo "Webhook setup failed. Check the error message above."
fi
