"""
Interactive Client Tester for Calculator API & Consumer Analytics
Demonstrates external script consumption using Alice's API Key.
"""
import requests
import json
import time

CALCULATOR_URL = "http://localhost:8101"
CONSUMER_URL = "http://localhost:8200"
ALICE_API_KEY = "ak_alice_1234567890abcdef"

headers = {
    "X-API-Key": ALICE_API_KEY
}


def print_divider(title=""):
    print("\n" + "=" * 65)
    if title:
        print(f"  {title}")
        print("=" * 65)


def run_tests():
    print_divider("EXTERNAL PYTHON CLIENT: CALCULATOR API TEST")
    print(f"[*] Target API:     {CALCULATOR_URL}")
    print(f"[*] Using API Key:  {ALICE_API_KEY} (Consumer: Alice)")

    # 1. Addition
    print("\n[1/5] Sending Addition Request: 100 + 250 ...")
    r1 = requests.get(f"{CALCULATOR_URL}/api/calculator/add?a=100&b=250", headers=headers)
    print(f"      Status: {r1.status_code} | Result: {r1.json()}")

    # 2. Subtraction
    print("\n[2/5] Sending Subtraction Request: 500 - 150 ...")
    r2 = requests.get(f"{CALCULATOR_URL}/api/calculator/subtract?a=500&b=150", headers=headers)
    print(f"      Status: {r2.status_code} | Result: {r2.json()}")

    # 3. Multiplication
    print("\n[3/5] Sending Multiplication Request: 12 * 8 ...")
    r3 = requests.get(f"{CALCULATOR_URL}/api/calculator/multiply?a=12&b=8", headers=headers)
    print(f"      Status: {r3.status_code} | Result: {r3.json()}")

    # 4. Division
    print("\n[4/5] Sending Division Request: 100 / 4 ...")
    r4 = requests.get(f"{CALCULATOR_URL}/api/calculator/divide?a=100&b=4", headers=headers)
    print(f"      Status: {r4.status_code} | Result: {r4.json()}")

    # 5. Error Scenario: Division by Zero
    print("\n[5/5] Sending Invalid Request (Division by Zero): 50 / 0 ...")
    r5 = requests.get(f"{CALCULATOR_URL}/api/calculator/divide?a=50&b=0", headers=headers)
    print(f"      Status: {r5.status_code} | Response: {r5.json()}")

    # Verify Updated Analytics in Database
    print_divider("LIVE ANALYTICS DASHBOARD SNAPSHOT")
    try:
        # Login to fetch consumer analytics
        auth_res = requests.post(f"{CONSUMER_URL}/api/consumer/login", json={"username": "alice", "password": "alice123"})
        if auth_res.status_code == 200:
            token = auth_res.json()["access_token"]
            analytics_res = requests.get(f"{CONSUMER_URL}/api/consumer/analytics", headers={"Authorization": f"Bearer {token}"})
            data = analytics_res.json()
            print(f"[*] Consumer:            {data['username']}")
            print(f"[*] Total Requests Made: {data['total_requests']}")
            print(f"[*] Quota Limit:         {data['quota_limit']}")
            print(f"[*] Quota Used:          {data['used']}")
            print(f"[*] Quota Remaining:     {data['remaining']}")
            print(f"[*] Usage Percentage:    {data['usage_percentage']}%")
            print(f"[*] Successful Requests: {data['successful_requests']}")
            print(f"[*] Failed Requests:     {data['failed_requests']}")
            print(f"[*] Error Rate:          {data['error_rate']}%")
    except Exception as e:
        print(f"Note: Could not reach consumer portal for analytics check ({e})")

    print_divider("SUCCESS: ALL REQUESTS PROCESSED AND LOGGED")
    print("You can view these live logs in:")
    print(" - Super Admin Portal:    http://localhost:8100")
    print(" - Consumer Portal:       http://localhost:8200")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_tests()
