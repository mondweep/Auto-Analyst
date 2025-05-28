import requests

def test_market_data():
    url = "http://localhost:8000/api/market-data"
    response = requests.get(url)
    print("/api/market-data status:", response.status_code)
    print("/api/market-data response:", response.text)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers["Content-Type"].startswith("application/json"), "Expected JSON response"
    assert "market_data" in response.text or "[]" in response.text, "Expected market_data in response"

def test_opportunities():
    url = "http://localhost:8000/api/opportunities"
    response = requests.get(url)
    print("/api/opportunities status:", response.status_code)
    print("/api/opportunities response:", response.text)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers["Content-Type"].startswith("application/json"), "Expected JSON response"
    assert "opportunities" in response.text or "[]" in response.text, "Expected opportunities in response"

if __name__ == "__main__":
    test_market_data()
    test_opportunities() 