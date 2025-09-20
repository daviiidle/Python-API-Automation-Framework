#!/usr/bin/env python3
"""
Quick test script to verify Wiremock error mappings are working
This tests if error scenarios return proper HTTP status codes
"""

import requests
import json

def test_wiremock_errors():
    """Test various error conditions to verify Wiremock priority fixes"""
    base_url = "http://localhost:8081"
    headers = {
        "Authorization": "Bearer banking-api-key-2024",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing Wiremock Error Mappings")
    print("=" * 50)
    
    tests = [
        {
            "name": "Missing Customer ID (should return 400)",
            "url": f"{base_url}/accounts",
            "method": "POST",
            "data": {"accountType": "SAVINGS", "currency": "AUD"},
            "expected_status": 400
        },
        {
            "name": "Invalid JSON (should return 400)", 
            "url": f"{base_url}/accounts",
            "method": "POST",
            "data": '{"invalid": json}',  # Invalid JSON
            "expected_status": 400,
            "raw_data": True
        },
        {
            "name": "Empty Customer ID (should return 400)",
            "url": f"{base_url}/accounts", 
            "method": "POST",
            "data": {"customerId": "", "accountType": "SAVINGS", "currency": "AUD"},
            "expected_status": 400
        },
        {
            "name": "Content-Length Mismatch (should return 400)",
            "url": f"{base_url}/accounts",
            "method": "POST", 
            "data": {"customerId": "CUST001", "accountType": "SAVINGS", "currency": "AUD", "initialBalance": 1000.00},
            "expected_status": 400,
            "headers": {**headers, "Content-Length": "50"}  # Wrong content length
        },
        {
            "name": "Non-existent Account (should return 404)",
            "url": f"{base_url}/accounts/NONEXISTENT",
            "method": "GET",
            "expected_status": 404
        },
        {
            "name": "No Authorization (should return 401)",
            "url": f"{base_url}/accounts",
            "method": "POST",
            "data": {"customerId": "CUST001", "accountType": "SAVINGS", "currency": "AUD"},
            "expected_status": 401,
            "headers": {"Content-Type": "application/json"}  # No auth header
        }
    ]
    
    results = []
    for test in tests:
        try:
            test_headers = test.get("headers", headers)
            
            if test["method"] == "GET":
                response = requests.get(test["url"], headers=test_headers)
            else:
                if test.get("raw_data"):
                    response = requests.post(test["url"], data=test["data"], headers=test_headers)
                else:
                    response = requests.post(test["url"], json=test["data"], headers=test_headers)
            
            expected = test["expected_status"]
            actual = response.status_code
            
            if actual == expected:
                print(f"✅ {test['name']}")
                print(f"   Expected: {expected}, Got: {actual}")
                results.append(True)
            else:
                print(f"❌ {test['name']}")
                print(f"   Expected: {expected}, Got: {actual}")
                print(f"   Response: {response.text[:100]}...")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {test['name']} - ERROR: {e}")
            results.append(False)
        
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"📊 Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All error mappings are working correctly!")
        return True
    else:
        print("⚠️  Some error mappings need adjustment")
        return False

if __name__ == "__main__":
    test_wiremock_errors()