import requests

def test_live():
    print("=================================================================")
    print("  VERIFYING LIVE ENDPOINTS ACROSS PORTS 8100, 8101, 8200")
    print("=================================================================")

    # 1. Check Swagger Docs on 8101
    r_docs = requests.get('http://localhost:8101/docs')
    print(f"[+] Calculator Swagger Docs (Port 8101): Status {r_docs.status_code}")
    assert r_docs.status_code == 200

    # 2. Admin Login on 8100
    r_admin_login = requests.post('http://localhost:8100/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
    admin_token = r_admin_login.json()['access_token']
    print(f"[+] Super Admin Login (Port 8100): Status {r_admin_login.status_code}, User: {r_admin_login.json()['username']}")
    assert r_admin_login.status_code == 200

    # 3. Consumer Login on 8200
    r_cons_login = requests.post('http://localhost:8200/api/consumer/login', json={'username': 'alice', 'password': 'alice123'})
    cons_token = r_cons_login.json()['access_token']
    print(f"[+] Consumer Login (Port 8200): Status {r_cons_login.status_code}, User: {r_cons_login.json()['username']}")
    assert r_cons_login.status_code == 200

    # 4. Fetch Alice API Key
    r_key = requests.get('http://localhost:8200/api/consumer/api-key', headers={'Authorization': f'Bearer {cons_token}'})
    api_key = r_key.json()['api_key']
    print(f"[+] Consumer Alice API Key: {api_key}")
    assert api_key.startswith("ak_alice_")

    # 5. Live Calculator Requests on Port 8101
    print('\n--- Making Real Calculator Requests to Port 8101 ---')
    # Request 1: 10 + 20
    r1 = requests.get('http://localhost:8101/api/calculator/add?a=10&b=20', headers={'X-API-Key': api_key})
    print(f"[*] Request 1 (10 + 20): Status {r1.status_code}, Response: {r1.json()}")
    assert r1.status_code == 200
    assert r1.json()['result'] == 30.0

    # Request 2: 5 * 6
    r2 = requests.get('http://localhost:8101/api/calculator/multiply?a=5&b=6', headers={'X-API-Key': api_key})
    print(f"[*] Request 2 (5 * 6): Status {r2.status_code}, Response: {r2.json()}")
    assert r2.status_code == 200
    assert r2.json()['result'] == 30.0

    # Request 3: 20 / 0 (Division by zero)
    r3 = requests.get('http://localhost:8101/api/calculator/divide?a=20&b=0', headers={'X-API-Key': api_key})
    print(f"[*] Request 3 (20 / 0): Status {r3.status_code}, Response: {r3.json()}")
    assert r3.status_code == 400

    # 6. Consumer Analytics Verification on 8200
    r_cons_analytics = requests.get('http://localhost:8200/api/consumer/analytics', headers={'Authorization': f'Bearer {cons_token}'})
    c_data = r_cons_analytics.json()
    print('\n--- Consumer Analytics Dashboard (Port 8200) ---')
    print(f"Total Requests: {c_data['total_requests']}")
    print(f"Quota: {c_data['used']} / {c_data['quota_limit']} (Remaining: {c_data['remaining']}, Usage: {c_data['usage_percentage']}%)")
    print(f"Successful: {c_data['successful_requests']}, Failed: {c_data['failed_requests']}")
    print(f"Error Rate: {c_data['error_rate']}%")
    assert c_data['total_requests'] == 3
    assert c_data['used'] == 3
    assert c_data['remaining'] == 997
    assert c_data['successful_requests'] == 2
    assert c_data['failed_requests'] == 1
    assert c_data['error_rate'] == 33.33

    # 7. Super Admin Analytics Verification on 8100
    r_admin_consumers = requests.get('http://localhost:8100/api/admin/consumers', headers={'Authorization': f'Bearer {admin_token}'})
    a_data = r_admin_consumers.json()
    print('\n--- Super Admin Dashboard View (Port 8100) ---')
    for c in a_data:
        print(f"Consumer: {c['username']} | Key: {c['api_key']} | Used: {c['requests_used']} | Remaining: {c['remaining']} | Error Rate: {c['error_rate']}%")

    r_admin_logs = requests.get('http://localhost:8100/api/admin/logs', headers={'Authorization': f'Bearer {admin_token}'})
    print(f"Total Global Logs in Admin: {len(r_admin_logs.json())}")
    assert len(r_admin_logs.json()) == 3

    print("\n[SUCCESS] ALL LIVE FLOWS AND DEMONSTRATION CRITERIA FULLY VERIFIED!")

if __name__ == "__main__":
    test_live()
