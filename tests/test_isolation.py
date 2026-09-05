from backend.app.models import ApiRequestLog, User


def test_tenant_isolation_between_consumers(calculator_client, consumer_client, admin_client, test_db):
    alice = test_db.query(User).filter(User.username == "alice").first()
    bob = test_db.query(User).filter(User.username == "bob").first()

    # Clear logs
    test_db.query(ApiRequestLog).delete()
    test_db.commit()

    alice_key = "ak_alice_1234567890abcdef"
    bob_key = "ak_bob_9876543210fedcba"

    # Alice makes 2 requests
    calculator_client.get("/api/calculator/add?a=1&b=2", headers={"X-API-Key": alice_key})
    calculator_client.get("/api/calculator/subtract?a=5&b=2", headers={"X-API-Key": alice_key})

    # Bob makes 1 request
    calculator_client.get("/api/calculator/multiply?a=3&b=3", headers={"X-API-Key": bob_key})

    # Login as Alice
    alice_token = consumer_client.post("/api/consumer/login", json={"username": "alice", "password": "alice123"}).json()["access_token"]
    alice_analytics = consumer_client.get("/api/consumer/analytics", headers={"Authorization": f"Bearer {alice_token}"}).json()

    assert alice_analytics["total_requests"] == 2
    assert alice_analytics["used"] == 2
    assert alice_analytics["remaining"] == 998
    for log in alice_analytics["recent_logs"]:
        assert log["user_id"] == alice.id
        assert log["username"] == "alice"

    # Login as Bob
    bob_token = consumer_client.post("/api/consumer/login", json={"username": "bob", "password": "bob123"}).json()["access_token"]
    bob_analytics = consumer_client.get("/api/consumer/analytics", headers={"Authorization": f"Bearer {bob_token}"}).json()

    assert bob_analytics["total_requests"] == 1
    assert bob_analytics["used"] == 1
    assert bob_analytics["remaining"] == 499
    for log in bob_analytics["recent_logs"]:
        assert log["user_id"] == bob.id

    # Super Admin can see both consumers in summary
    admin_token = admin_client.post("/api/admin/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]
    admin_consumers = admin_client.get("/api/admin/consumers", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert len(admin_consumers) >= 2
    consumer_map = {c["username"]: c for c in admin_consumers}
    assert consumer_map["alice"]["requests_used"] == 2
    assert consumer_map["bob"]["requests_used"] == 1

    # Super Admin can see all 3 logs
    admin_logs = admin_client.get("/api/admin/logs", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert len(admin_logs) == 3
