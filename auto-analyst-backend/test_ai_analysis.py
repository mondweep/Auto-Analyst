import requests
import json
import time
import os

def test_file_server_health():
    """Test if the file server is running"""
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print("✅ File server is running")
            return True
        else:
            print(f"❌ File server returned error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to file server: {str(e)}")
        return False

def test_app_server_health():
    """Test if the main app server is running"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ App server is running")
            return True
        else:
            print(f"❌ App server returned error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to app server: {str(e)}")
        return False

def test_file_datasets():
    """Test if we can get the list of available datasets"""
    try:
        response = requests.get("http://localhost:8000/api/file-server/datasets")
        if response.status_code == 200:
            data = response.json()
            if "files" in data and len(data["files"]) > 0:
                print(f"✅ Found {len(data['files'])} datasets: {', '.join(data['files'])}")
                return data["files"]
            else:
                print("❌ No datasets found")
                return []
        else:
            print(f"❌ Error getting datasets: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting datasets: {str(e)}")
        return []

def test_analyze_file(filename=None):
    """Test the analyze-file endpoint"""
    try:
        # If no filename provided, get the first available dataset
        if not filename:
            datasets = test_file_datasets()
            if not datasets:
                print("❌ No datasets available for analysis")
                return False
            filename = datasets[0]
        
        # Make the request
        payload = {
            "query": "Give me a summary of the data",
            "filename": filename
        }
        
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/analyze-file",
            json=payload
        )
        
        # Check if successful
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"✅ Successfully analyzed {filename} in {processing_time:.2f} seconds")
                result_length = len(data.get("response", ""))
                print(f"  Response length: {result_length} characters")
                return True
            else:
                print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Error analyzing file: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in test_analyze_file: {str(e)}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    try:
        payload = {
            "query": "What insights can you provide about the data?"
        }
        
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/chat",
            json=payload
        )
        
        # Check if successful
        if response.status_code == 200:
            data = response.json()
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"✅ Chat response successful in {processing_time:.2f} seconds")
            result_length = len(data.get("response", ""))
            print(f"  Response length: {result_length} characters")
            return True
        else:
            print(f"❌ Error with chat: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in test_chat_endpoint: {str(e)}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n===== Testing AI Analysis Capabilities =====\n")
    
    # First check if servers are running
    if not test_file_server_health():
        print("❌ File server is not running, skipping further tests")
        return False
    
    if not test_app_server_health():
        print("❌ App server is not running, skipping further tests")
        return False
    
    # Test data analysis capabilities
    print("\n----- Testing Data Analysis -----")
    datasets = test_file_datasets()
    
    if datasets:
        # Test with the first dataset
        test_analyze_file(datasets[0])
    
    # Test chat capabilities
    print("\n----- Testing Chat Interface -----")
    test_chat_endpoint()
    
    print("\n===== Tests Completed =====\n")
    return True

if __name__ == "__main__":
    run_all_tests() 