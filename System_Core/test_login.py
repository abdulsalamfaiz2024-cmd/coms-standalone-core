
import requests
import json
import hashlib

# Config
URL = "http://localhost:8000/api/login"
USERNAME = "admin"
PASSWORD = "admin123"

def test_login():
    print(f"Testing Login against {URL}...")
    headers = {'Content-Type': 'application/json'}
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Login working via API.")
        else:
            print("FAILURE: Login denied.")
            
    except Exception as e:
        print(f"CRITICAL ERROR: Could not connect to server. Is it running? {e}")

if __name__ == "__main__":
    test_login()
