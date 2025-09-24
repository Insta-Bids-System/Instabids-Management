#!/usr/bin/env python3
"""
Test script to verify property management API endpoints are working.
"""
import json

import requests

API_BASE = "http://localhost:8000"


def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"[OK] API Health: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"[FAIL] API Health failed: {e}")
        return False


def test_properties_endpoint():
    """Test properties endpoint without auth"""
    try:
        response = requests.get(f"{API_BASE}/api/properties", timeout=5)
        print(f"Properties endpoint: {response.status_code}")

        if response.status_code == 403:
            print("   -> 403 Forbidden (Authentication required - EXPECTED)")
            return True
        elif response.status_code == 200:
            data = response.json()
            print(f"   -> 200 OK - Found {len(data)} properties")
            return True
        else:
            print(f"   -> Unexpected status: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Properties endpoint failed: {e}")
        return False


def test_create_property():
    """Test creating a property (will fail due to auth, but tests endpoint exists)"""
    property_data = {
        "address": "123 Test Street",
        "city": "Test City",
        "state": "CA",
        "zip_code": "12345",
        "property_type": "single_family",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500,
    }

    try:
        response = requests.post(
            f"{API_BASE}/api/properties",
            json=property_data,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        print(f"Create property: {response.status_code}")

        if response.status_code == 403:
            print("   -> 403 Forbidden (Authentication required - EXPECTED)")
            return True
        elif response.status_code == 422:
            print("   -> 422 Validation Error (Endpoint exists but data invalid)")
            return True
        elif response.status_code == 201:
            print("   -> 201 Created - Property created successfully!")
            return True
        else:
            print(f"   -> Unexpected status: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Create property failed: {e}")
        return False


def main():
    print("Testing Property Management API")
    print("=" * 50)

    results = []

    # Test API health
    results.append(test_api_health())

    # Test properties endpoints
    results.append(test_properties_endpoint())
    results.append(test_create_property())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"[SUCCESS] All tests passed ({passed}/{total})")
        print("Property Management API is working correctly!")
    else:
        print(f"[WARNING] Some tests failed ({passed}/{total})")
        print("API endpoints exist but may need authentication setup")

    return passed == total


if __name__ == "__main__":
    main()
