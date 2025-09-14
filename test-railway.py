#!/usr/bin/env python3
"""
Test script to check Railway deployment
"""
import requests
import time

def test_railway_app():
    """Test the Railway app endpoints"""
    base_url = "https://web-production-ec3e.up.railway.app"
    
    endpoints = [
        "/",
        "/health", 
        "/api/test",
        "/docs"
    ]
    
    print("🚀 Testing Railway App Deployment")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print()
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(url, timeout=10)
            print(f"✅ Status: {response.status_code}")
            if response.status_code == 200:
                if endpoint == "/docs":
                    print("📚 API Documentation available")
                else:
                    print(f"📄 Response: {response.json()}")
            print()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
            print()
    
    # Test database endpoints if available
    print("🗄️ Testing Database Endpoints")
    print("-" * 30)
    
    db_endpoints = [
        "/api/games",
        "/api/games/test-game-id"
    ]
    
    for endpoint in db_endpoints:
        url = base_url + endpoint
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            elif response.status_code == 404:
                print("ℹ️ Endpoint not found (expected for test-game-id)")
            print()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    test_railway_app()
