#!/usr/bin/env python3
"""
Reset WireMock scenario states to ensure clean test runs.
"""

import requests
import sys

def reset_wiremock_scenarios(wiremock_url="http://localhost:8081"):
    """Reset all WireMock scenario states to 'Started'."""
    
    print(f"Resetting WireMock scenarios at {wiremock_url}")
    
    try:
        # Reset all scenarios to Started state
        reset_url = f"{wiremock_url}/__admin/scenarios/reset"
        response = requests.post(reset_url)
        
        if response.status_code == 200:
            print("✅ Successfully reset all WireMock scenarios")
            return True
        else:
            print(f"❌ Failed to reset scenarios. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to WireMock. Make sure it's running on port 8081")
        return False
    except Exception as e:
        print(f"❌ Error resetting scenarios: {e}")
        return False

def main():
    """Main execution."""
    wiremock_url = "http://localhost:8081"
    
    if len(sys.argv) > 1:
        wiremock_url = sys.argv[1]
    
    success = reset_wiremock_scenarios(wiremock_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()