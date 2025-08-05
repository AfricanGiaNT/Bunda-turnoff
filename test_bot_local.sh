#!/bin/bash

# Test script for the local bot
echo "🧪 Testing Local Bot"
echo "===================="

# Wait for bot to start (if not already running)
echo "⏳ Waiting for bot to be ready..."
sleep 2

# Test 1: Petty Cash Expense
echo ""
echo "💰 Test 1: Petty Cash Expense"
curl -X POST http://localhost:8000/test-message \
     -H 'Content-Type: application/json' \
     -d '{"message": "Paid 15,000 MWK for filter replacement from petty cash"}' \
     | jq '.'

# Test 2: Fuel Log
echo ""
echo "⛽ Test 2: Fuel Log"
curl -X POST http://localhost:8000/test-message \
     -H 'Content-Type: application/json' \
     -d '{"message": "Gave 40 liters diesel to Hilux, driver John, for Salima trip. Odometer start 12300 end 12420"}' \
     | jq '.'

# Test 3: Health Check
echo ""
echo "🏥 Test 3: Health Check"
curl http://localhost:8000/health | jq '.'

echo ""
echo "✅ Tests completed!" 