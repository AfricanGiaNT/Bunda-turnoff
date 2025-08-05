# 🚀 Render Deployment Guide

This guide will help you deploy your Telegram bot to Render for production use.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: All required API keys and tokens

## 🔧 Required Environment Variables

Make sure you have these environment variables ready:

```bash
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
TELEGRAM_CHAT_ID=your_chat_id
```

## 🚀 Deployment Steps

### Step 1: Connect to Render

1. **Login to Render**: Go to [render.com](https://render.com) and sign in
2. **New Web Service**: Click "New" → "Web Service"
3. **Connect Repository**: Connect your GitHub repository
4. **Select Repository**: Choose your bot repository

### Step 2: Configure the Service

Use these settings:

- **Name**: `service-station-ops-bot`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api.telegram_handler:app --host 0.0.0.0 --port $PORT`
- **Plan**: `Free` (for testing) or `Starter` (for production)

### Step 3: Set Environment Variables

Add these environment variables in Render:

| Key | Value | Description |
|-----|-------|-------------|
| `TELEGRAM_TOKEN` | `your_bot_token` | Your Telegram bot token |
| `OPENAI_API_KEY` | `your_openai_key` | Your OpenAI API key |
| `AIRTABLE_API_KEY` | `your_airtable_key` | Your Airtable API key |
| `AIRTABLE_BASE_ID` | `your_base_id` | Your Airtable base ID |
| `TELEGRAM_CHAT_ID` | `your_chat_id` | Your Telegram chat ID |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DAILY_SUMMARY_TIME_UTC` | `15:00` | Daily summary time |

### Step 4: Deploy

1. **Click "Create Web Service"**
2. **Wait for Build**: Render will build and deploy your service
3. **Get URL**: Note the URL (e.g., `https://your-app.onrender.com`)

## 🔗 Set Up Webhook

After deployment, you need to tell Telegram where to send messages:

### Option 1: Using the Setup Script

```bash
# Set webhook URL
python scripts/setup_webhook.py set https://your-app.onrender.com

# Check webhook status
python scripts/setup_webhook.py info

# Remove webhook (if needed)
python scripts/setup_webhook.py remove
```

### Option 2: Manual Setup

1. **Get your Render URL**: From the Render dashboard
2. **Set Webhook**: Visit this URL in your browser:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-app.onrender.com/telegram-webhook
   ```
3. **Verify**: Visit this URL to check status:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
   ```

## 🧪 Testing the Deployment

### Health Check

Visit your health check endpoint:
```
https://your-app.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "airtable_ready": true,
  "gpt_ready": true
}
```

### Test Bot Commands

1. **Start Command**: Send `/start` to your bot
2. **Help Command**: Send `/help` to your bot
3. **Test Messages**: Try these examples:
   - `"Spent 5000 on lunch"`
   - `"Hilux used 40 liters"`
   - `"Spent 5000 on lunch; Hilux used 40 liters"`

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` exists
   - Verify all dependencies are listed
   - Check Python version compatibility

2. **Environment Variables Missing**
   - Verify all required variables are set in Render
   - Check variable names match exactly
   - Ensure no extra spaces in values

3. **Webhook Not Working**
   - Verify Render URL is accessible
   - Check webhook URL format
   - Ensure HTTPS is used

4. **Bot Not Responding**
   - Check Render logs for errors
   - Verify webhook is set correctly
   - Test health check endpoint

### Checking Logs

1. **Render Dashboard**: Go to your service → "Logs"
2. **Real-time Logs**: Click "Live" to see real-time logs
3. **Error Logs**: Look for error messages in red

### Debugging Commands

```bash
# Check webhook status
python scripts/setup_webhook.py info

# Test local deployment
python run_bot_polling.py

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('TELEGRAM_TOKEN:', bool(os.getenv('TELEGRAM_TOKEN')))"
```

## 🔄 Updating the Bot

### Automatic Updates

If you connected your GitHub repository:
1. **Push Changes**: Push to your main branch
2. **Auto Deploy**: Render will automatically redeploy
3. **Verify**: Test the bot after deployment

### Manual Updates

1. **Redeploy**: Click "Manual Deploy" in Render dashboard
2. **Check Logs**: Monitor deployment logs
3. **Test**: Verify bot functionality

## 💰 Cost Considerations

### Free Plan Limitations

- **Sleep Mode**: Service sleeps after 15 minutes of inactivity
- **Cold Start**: First request after sleep takes 30-60 seconds
- **Bandwidth**: 750 hours/month included
- **Build Time**: 500 minutes/month included

### Upgrading to Paid

Consider upgrading to "Starter" plan ($7/month) for:
- **Always On**: No sleep mode
- **Faster Response**: No cold starts
- **More Resources**: Better performance
- **Custom Domains**: Use your own domain

## 🔒 Security Considerations

1. **Environment Variables**: Never commit API keys to Git
2. **Webhook Security**: Use HTTPS only
3. **Access Control**: Limit who can access your bot
4. **Rate Limiting**: Monitor API usage

## 📊 Monitoring

### Health Checks

- **Automatic**: Render checks `/health` endpoint
- **Manual**: Visit health endpoint regularly
- **Alerts**: Set up notifications for failures

### Performance Monitoring

- **Response Times**: Monitor bot response times
- **Error Rates**: Track failed requests
- **API Usage**: Monitor OpenAI and Airtable usage

## 🎯 Next Steps

After successful deployment:

1. **Test All Features**: Verify single and multiple entry logging
2. **Monitor Performance**: Check response times and reliability
3. **Set Up Monitoring**: Configure alerts and logging
4. **Document Usage**: Create user guide for your team
5. **Plan Scaling**: Consider paid plans for production use

## 📞 Support

If you encounter issues:

1. **Check Logs**: Review Render and application logs
2. **Test Locally**: Verify functionality with polling mode
3. **Documentation**: Review this guide and code comments
4. **Community**: Check Render and Telegram bot communities

---

**🎉 Congratulations!** Your Telegram bot is now deployed and ready for production use. 