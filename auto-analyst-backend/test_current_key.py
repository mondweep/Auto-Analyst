#!/usr/bin/env python3

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Test the API key from .env
api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing API key: {api_key[:20]}...")

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}'
headers = {'Content-Type': 'application/json'}
data = {
    'contents': [{'role': 'user', 'parts': [{'text': 'Hello'}]}],
    'generationConfig': {'maxOutputTokens': 100, 'temperature': 0.7}
}

try:
    print("Making API request...")
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text[:500]}')
    
    if response.status_code == 200:
        print("✅ API key is VALID")
    elif response.status_code == 400:
        print("❌ API key is INVALID or request malformed")
    elif response.status_code == 403:
        print("❌ API key is FORBIDDEN")
    else:
        print(f"❌ API key test failed with status {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ API request timed out - possible network issue")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - check internet connection")
except Exception as e:
    print(f"❌ Error testing API key: {e}")

# Also test a simple HTTP request to verify internet connectivity
try:
    print("\nTesting basic internet connectivity...")
    response = requests.get("https://httpbin.org/get", timeout=10)
    if response.status_code == 200:
        print("✅ Internet connection is working")
    else:
        print("❌ Internet connection issues")
except Exception as e:
    print(f"❌ Internet connectivity test failed: {e}") 