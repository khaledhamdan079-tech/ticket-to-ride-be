#!/usr/bin/env python3
"""
Simple test script to verify the FastAPI app starts correctly
"""
import requests
import time
import sys

def test_app():
    """Test if the app is running and responding"""
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing FastAPI app startup...")
    
    # Wait a bit for the app to start
    time.sleep(2)
    
    if test_app():
        print("🎉 App is running successfully!")
        sys.exit(0)
    else:
        print("💥 App failed to start properly")
        sys.exit(1)
