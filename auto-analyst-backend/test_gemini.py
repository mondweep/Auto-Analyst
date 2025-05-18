import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBdZJNOA_w8lpyX4HUQzicoVWlN9xYINQ0")

# First, list available models
def list_models():
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_api_key}"
    try:
        print("Listing available Gemini models...")
        response = requests.get(list_url)
        
        if response.status_code == 200:
            models = response.json()
            print("\nAvailable models:")
            for model in models.get("models", []):
                print(f"- {model.get('name')} (supported generation methods: {model.get('supportedGenerationMethods', [])})")
            return models.get("models", [])
        else:
            print(f"Error listing models: {response.text}")
            return []
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

# Test function for Gemini API
def test_gemini(model_name):
    # Try a different version of the URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": "Hello, how are you?"}]}],
        "generationConfig": {"maxOutputTokens": 100}
    }
    
    # Make the API request
    print(f"\nSending request to Gemini API ({model_name})...")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code < 400:
            content = response.json()
            print("\nResponse from Gemini:")
            print(json.dumps(content, indent=2)[:500] + "...\n")
            
            # Extract the generated text
            if "candidates" in content and len(content["candidates"]) > 0:
                generated_text = content["candidates"][0]["content"]["parts"][0]["text"]
                print("Generated text:")
                print(generated_text)
                return True
            else:
                print("No text generated in the response")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error making API request: {e}")
        return False

# Main execution
models = list_models()

# Try these model names
model_names = [
    "gemini-pro",
    "gemini-1.0-pro",
    "gemini-1.5-pro",
    "models/gemini-pro"
]

# Add any models from the API response
for model in models:
    name = model.get('name', '')
    if 'gemini' in name.lower() and name not in model_names:
        model_names.append(name)

# Test each model
success = False
for model_name in model_names:
    success = test_gemini(model_name)
    if success:
        print(f"\n✅ Successfully used model: {model_name}")
        break

if not success:
    print("\n❌ Could not successfully use any Gemini model") 