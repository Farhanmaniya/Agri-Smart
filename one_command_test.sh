#!/bin/bash
# One-command test script for AgriSmart API

echo "🚀 Testing AgriSmart API..."

# Test health check
echo "1. Testing health check..."
curl -s http://localhost:8000/api/health | jq .

echo -e "\n2. Testing rainfall prediction..."
curl -s -X POST "http://localhost:8000/api/predictions/rainfall" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"temperature": 25.0, "humidity": 60.0, "pressure": 1013.0, "wind_speed": 10.0, "month": 6, "day_of_year": 150}' | jq .

echo -e "\n3. Testing soil prediction..."
curl -s -X POST "http://localhost:8000/api/predictions/soil-type" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"ph": 6.5, "nitrogen": 40.0, "phosphorus": 30.0, "potassium": 35.0, "organic_matter": 2.5, "moisture": 25.0, "temperature": 25.0}' | jq .

echo -e "\n4. Testing models list..."
curl -s -X GET "http://localhost:8000/api/predictions/models" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq .

echo -e "\n✅ Test completed!"
