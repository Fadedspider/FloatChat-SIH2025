import requests
import json

# Test all endpoints
BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing ARGO Ocean Data API...")
    
    # Test root
    response = requests.get(f"{BASE_URL}/")
    print(f"Root: {response.json()}")
    
    # Test health check
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.json()}")
    
    # Test daily averages
    response = requests.get(f"{BASE_URL}/daily-avg?var=temperature")
    print(f"Daily temp (first 3): {response.json()['data'][:3]}")

if __name__ == "__main__":
    test_endpoints()
