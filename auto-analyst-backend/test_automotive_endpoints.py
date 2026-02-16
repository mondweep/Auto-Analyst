import requests

def test_vehicles():
    url = "http://localhost:8000/api/vehicles"
    response = requests.get(url)
    print("/api/vehicles status:", response.status_code)
    print("/api/vehicles response:", response.text)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers["Content-Type"].startswith("application/json"), "Expected JSON response"

def test_statistics():
    url = "http://localhost:8000/api/statistics"
    response = requests.get(url)
    print("/api/statistics status:", response.status_code)
    print("/api/statistics response:", response.text)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers["Content-Type"].startswith("application/json"), "Expected JSON response"

if __name__ == "__main__":
    test_vehicles()
    test_statistics() 