#!/usr/bin/env python3
"""
Test script to demonstrate the new structured API responses
"""

import json
import requests
import time


def test_api_responses():
    base_url = "http://localhost:8000"

    print("🔍 Testing JobSpy API Structured Responses\n")

    # Test health endpoints first
    print("1. Testing Health Endpoints:")

    try:
        # Test scraping health
        response = requests.get(f"{base_url}/health/scraping")
        if response.status_code == 200:
            data = response.json()
            print(
                f"   ✅ Scraping Health: Available={data['scraping_available']}, Proxies={data['working_proxies']}")
        else:
            print(f"   ❌ Scraping health check failed: {response.status_code}")

        # Test proxy health
        response = requests.get(f"{base_url}/health/proxies")
        if response.status_code == 200:
            data = response.json()
            print(
                f"   ✅ Proxy Health: {data['working_proxies']} working proxies, Status: {data['status']}")
        else:
            print(f"   ❌ Proxy health check failed: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running. Please start with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return

    print("\n2. Testing Job Search Responses:")

    # Test a job search
    try:
        response = requests.get(f"{base_url}/jobs", params={
            "search_term": "python developer",
            "location": "San Francisco",
            "results_wanted": 2
        })

        if response.status_code == 200:
            data = response.json()

            if data["success"]:
                print(f"   ✅ Successful Response:")
                print(f"      - Success: {data['success']}")
                print(f"      - Jobs Found: {len(data['jobs'])}")
                print(
                    f"      - Used Proxies: {data.get('metadata', {}).get('used_proxies', 'N/A')}")

                if data["jobs"]:
                    job = data["jobs"][0]
                    print(
                        f"      - Sample Job: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            else:
                print(f"   ⚠️  Error Response:")
                print(f"      - Success: {data['success']}")
                print(f"      - Error Type: {data['error']['error_type']}")
                print(f"      - Message: {data['error']['message']}")
                print(f"      - Suggested Actions:")
                # Show first 2 actions
                for action in data['error']['suggested_actions'][:2]:
                    print(f"        • {action}")
        else:
            print(f"   ❌ Request failed with status: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error testing job search: {e}")

    print("\n3. Response Structure Benefits:")
    print("   ✅ Clear success/failure indication")
    print("   ✅ Structured error information with specific error types")
    print("   ✅ Actionable suggestions for error resolution")
    print("   ✅ Metadata about proxy usage and search parameters")
    print("   ✅ Consistent JSON structure for easy client parsing")


if __name__ == "__main__":
    test_api_responses()
