from backend.app.models import ApiRequestLog, User


def test_consumer_analytics_calculation(calculator_client, consumer_client, test_db):
    alice = test_db.query(User).filter(User.username == "alice").first()
    assert alice is not None

    # Clear logs
    test_db.query(ApiRequestLog).filter(ApiRequestLog.user_id == alice.id).delete()
    test_db.commit()

    # Log in as Alice
    login_res = consumer_client.post("/api/consumer/login", json={"username": "alice", "password": "alice123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Initial state (0 requests)
    res_initial = consumer_client.get("/api/consumer/analytics", headers=auth_headers)
    assert res_initial.status_code == 200
    data0 = res_initial.json()
    assert data0["total_requests"] == 0
    assert data0["used"] == 0
    assert data0["remaining"] == 1000
    assert data0["error_rate"] == 0.0
    assert data0["successful_requests"] == 0
    assert data0["failed_requests"] == 0

    # Step 2: Make 1 successful request
    alice_key = "ak_alice_1234567890abcdef"
    r1 = calculator_client.get("/api/calculator/add?a=10&b=20", headers={"X-API-Key": alice_key})
    assert r1.status_code == 200

    data1 = consumer_client.get("/api/consumer/analytics", headers=auth_headers).json()
    assert data1["total_requests"] == 1
    assert data1["used"] == 1
    assert data1["remaining"] == 999
    assert data1["error_rate"] == 0.0
    assert data1["successful_requests"] == 1
    assert data1["failed_requests"] == 0

    # Step 3: Make second successful request
    r2 = calculator_client.get("/api/calculator/multiply?a=5&b=6", headers={"X-API-Key": alice_key})
    assert r2.status_code == 200

    # Step 4: Make 1 failed request (divide by zero)
    r3 = calculator_client.get("/api/calculator/divide?a=20&b=0", headers={"X-API-Key": alice_key})
    assert r3.status_code == 400

    # Step 5: Check analytics metrics: 3 total, 2 success, 1 failed, 33.33% error rate
    data3 = consumer_client.get("/api/consumer/analytics", headers=auth_headers).json()
    assert data3["total_requests"] == 3
    assert data3["used"] == 3
    assert data3["remaining"] == 997
    assert data3["successful_requests"] == 2
    assert data3["failed_requests"] == 1
    assert round(data3["error_rate"], 2) == 33.33
    assert len(data3["recent_logs"]) == 3
