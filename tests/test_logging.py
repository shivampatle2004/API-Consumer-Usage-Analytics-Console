from backend.app.models import ApiRequestLog, User


def test_logging_success_and_failure(calculator_client, test_db):
    alice = test_db.query(User).filter(User.username == "alice").first()
    assert alice is not None

    # Clear logs for deterministic test
    test_db.query(ApiRequestLog).filter(ApiRequestLog.user_id == alice.id).delete()
    test_db.commit()

    alice_key = "ak_alice_1234567890abcdef"

    # 1. Successful request
    res1 = calculator_client.get("/api/calculator/add?a=10&b=20", headers={"X-API-Key": alice_key})
    assert res1.status_code == 200

    logs = test_db.query(ApiRequestLog).filter(ApiRequestLog.user_id == alice.id).all()
    assert len(logs) == 1
    assert logs[0].endpoint == "/api/calculator/add"
    assert logs[0].method == "GET"
    assert logs[0].status_code == 200

    # 2. Failed request (divide by zero)
    res2 = calculator_client.get("/api/calculator/divide?a=20&b=0", headers={"X-API-Key": alice_key})
    assert res2.status_code == 400

    logs_after = test_db.query(ApiRequestLog).filter(ApiRequestLog.user_id == alice.id).order_by(ApiRequestLog.id).all()
    assert len(logs_after) == 2
    assert logs_after[1].endpoint == "/api/calculator/divide"
    assert logs_after[1].status_code == 400
