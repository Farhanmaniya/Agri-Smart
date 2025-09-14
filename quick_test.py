#!/usr/bin/env python3
"""Quick test script for AgriSmart API endpoints."""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
# You'll need to get a real token from /api/auth/login
TOKEN = "YOUR_TOKEN_HERE"  # Replace with actual token

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def test_rainfall():
    """Test rainfall prediction."""
    url = f"{BASE_URL}/api/predictions/rainfall"
    data = {
        "temperature": 25.0,
        "humidity": 60.0,
        "pressure": 1013.0,
        "wind_speed": 10.0,
        "month": 6,
        "day_of_year": 150
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Rainfall Prediction: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_soil():
    """Test soil type prediction."""
    url = f"{BASE_URL}/api/predictions/soil-type"
    data = {
        "ph": 6.5,
        "nitrogen": 40.0,
        "phosphorus": 30.0,
        "potassium": 35.0,
        "organic_matter": 2.5,
        "moisture": 25.0,
        "temperature": 25.0
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Soil Prediction: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_models():
    """Test models listing."""
    url = f"{BASE_URL}/api/predictions/models"
    response = requests.get(url, headers=headers)
    print(f"Models List: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing AgriSmart API...")
    test_rainfall()
    print("\n" + "="*50 + "\n")
    test_soil()
    print("\n" + "="*50 + "\n")
    test_models()
