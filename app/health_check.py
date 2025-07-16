#!/usr/bin/env python3
"""
Simple health check script for the API
"""
import requests
import sys

def check_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("API is healthy")
            return 0
        else:
            print(f"API returned status code: {response.status_code}")
            return 1
    except Exception as e:
        print(f"Health check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())
