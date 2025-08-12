# **Background Worker Deployment Guide**

## **Overview**
This guide explains how to deploy the Service Station Operations Bot as a Render Background Worker service that can still handle HTTP endpoints for Telegram webhooks.

## **Key Differences: Background Worker vs Web Service**

### **Background Worker**
- ✅ **Type**: `worker` in render.yaml
- ✅ **Port Binding**: Manual port binding (no automatic `PORT` variable)
- ✅ **HTTP Endpoints**: Supported but requires custom implementation
- ✅ **Health Checks**: Manual implementation (no automatic monitoring)
- ✅ **Cost**: More cost-effective for background processing
- ✅ **Use Case**: Perfect for bots that need both background processing AND webhook endpoints

### **Web Service**
- ⚠️ **Type**: `web` in render.yaml
- ⚠️ **Port Binding**: Automatic `PORT` environment variable
- ⚠️ **HTTP Endpoints**: Native support
- ⚠️ **Health Checks**: Automatic monitoring
- ⚠️ **Cost**: Higher cost for always-on web services

## **Configuration Files**

### **1. render.yaml**
```yaml
services:
  - type: worker                    # ← Background Worker
    name: service-station-ops-bot
    env: python
    plan: free
    buildCommand: |
      python --version
      pip --version
      pip install --upgrade pip
      pip install -r requirements.txt
      pip list
    startCommand: python app_background_worker.py  # ← Custom Background Worker app
    envVars:
      - key: TELEGRAM_TOKEN
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: AIRTABLE_API_KEY
        sync: false
      - key: AIRTABLE_BASE_ID
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
      - key: WORKER_PORT              # ← Custom port variable (not PORT)
        value: 10000
    autoDeploy: true
    pythonVersion: 3.13.0
```

### **2. app_background_worker.py**
- **Custom HTTP server** using `http.server` module
- **Manual port binding** to `WORKER_PORT` (default: 10000)
- **Threaded request handling** for concurrent webhook processing
- **Graceful error handling** with fallback to minimal mode
- **Background task support** for periodic operations

## **Port Configuration**

### **Background Worker Port Handling**
```python
# Background Workers don't get automatic PORT variable
port = int(os.environ.get('WORKER_PORT', '10000'))  # Custom variable
host = '0.0.0.0'

# Manual server binding
server_address = (host, port)
httpd = ThreadedHTTPServer(server_address, BackgroundWorkerHTTPHandler)
```

### **Environment Variables**
- ❌ `PORT` - Not available in Background Workers
- ✅ `WORKER_PORT` - Custom port variable (set to 10000)
- ✅ All other environment variables work normally

## **Deployment Steps**

### **Step 1: Delete Current Service (If Needed)**
If you have an existing service that's not working:
1. Go to Render Dashboard
2. Find your service (`srv-d28sInjuibrs73dtvp7g`)
3. Settings → Delete Service

### **Step 2: Deploy New Background Worker**
1. **Connect Repository**: Link your GitHub repo to Render
2. **Service Type**: Choose "Background Worker" (not Web Service)
3. **Configuration**: Render will use your `render.yaml` automatically
4. **Environment Variables**: Set your secrets (TELEGRAM_TOKEN, etc.)

### **Step 3: Configure Webhook URL**
Your webhook URL will be:
```
https://your-service-name.onrender.com:10000/telegram-webhook
```

**Note**: Background Workers on Render get a different URL format than Web Services.

### **Step 4: Verify Deployment**
Check the logs for:
```
🌐 HTTP Server starting on 0.0.0.0:10000
🔗 Webhook URL: http://0.0.0.0:10000/telegram-webhook
❤️ Health check: http://0.0.0.0:10000/health
🚀 Background Worker is ready!
```

## **Testing**

### **Local Testing**
```bash
# Run locally
python app_background_worker.py

# Test in another terminal
python test_background_worker.py
```

### **Production Testing**
```bash
# Test health endpoint
curl https://your-service.onrender.com:10000/health

# Test webhook endpoint
curl https://your-service.onrender.com:10000/telegram-webhook
```

## **Troubleshooting**

### **Port Issues**
- ✅ **Background Workers**: Use `WORKER_PORT=10000`
- ❌ **Don't use**: `PORT` variable (not available)

### **Health Checks**
- ✅ **Manual**: `/health` endpoint available but not monitored by Render
- ❌ **Automatic**: No `healthCheckPath` support in Background Workers

### **Logs to Check**
```
🌍 Environment PORT: Not set          # ← Expected for Background Workers
🔌 Using port: 10000 (Background Worker)  # ← Should see this
🌐 HTTP Server starting on 0.0.0.0:10000  # ← Server starting
```

### **Common Issues**
1. **"Connection refused"**: Service might not be binding to 0.0.0.0
2. **"Port already in use"**: Check if multiple instances are running
3. **"Module import errors"**: Check requirements.txt and build logs

## **Webhook Configuration**

### **Set Telegram Webhook**
```python
import requests

# Set webhook to your Background Worker
webhook_url = "https://your-service.onrender.com:10000/telegram-webhook"
telegram_token = "your_bot_token"

response = requests.post(
    f"https://api.telegram.org/bot{telegram_token}/setWebhook",
    json={"url": webhook_url}
)
```

### **Verify Webhook**
```python
response = requests.get(
    f"https://api.telegram.org/bot{telegram_token}/getWebhookInfo"
)
print(response.json())
```

## **Advantages of Background Worker Approach**

1. **Cost Effective**: Background Workers are cheaper than Web Services
2. **Background Processing**: Can run periodic tasks, cleanup, etc.
3. **Webhook Support**: Still handles HTTP endpoints for Telegram
4. **Resource Efficient**: Better resource utilization for bot workloads
5. **Flexibility**: Custom server implementation allows more control

## **Monitoring**

### **Application Logs**
- Server startup messages
- Webhook request logs
- Error handling logs
- Component initialization status

### **Health Monitoring**
```bash
# Check if service is responding
curl -f https://your-service.onrender.com:10000/health || echo "Service down"
```

### **Telegram Bot Status**
```bash
# Check webhook status
curl "https://api.telegram.org/bot$TELEGRAM_TOKEN/getWebhookInfo"
```

## **Next Steps**

1. **Deploy**: Use the Background Worker configuration
2. **Test**: Verify webhook endpoints work
3. **Monitor**: Check logs for proper initialization
4. **Configure**: Set Telegram webhook to your service URL
5. **Validate**: Send test messages to your bot

This Background Worker approach gives you the best of both worlds: cost-effective background processing with webhook endpoint support!
