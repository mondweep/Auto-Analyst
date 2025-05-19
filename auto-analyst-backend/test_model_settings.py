import requests
import os

def test_post_model_settings():
    url = "http://localhost:8000/settings/model"
    payload = {
        "provider": "gemini",
        "model": "gemini-1.5-pro",
        "api_key": os.environ.get("GEMINI_API_KEY", "AIzaSyBdZJNOA_w8lpyX4HUQzicoVWlN9xYINQ0"),
        "max_tokens": 6000,
        "temperature": 0.7
    }
    response = requests.post(url, json=payload)
    print("Status code:", response.status_code)
    print("Response:", response.text)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

if __name__ == "__main__":
    test_post_model_settings() 