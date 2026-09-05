def test_admin_login_success(admin_client):
    response = admin_client.post("/api/admin/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "SUPER_ADMIN"
    assert data["username"] == "admin"


def test_admin_login_invalid_password(admin_client):
    response = admin_client.post("/api/admin/login", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401


def test_consumer_login_success(consumer_client):
    response = consumer_client.post("/api/consumer/login", json={"username": "alice", "password": "alice123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "CONSUMER"
    assert data["username"] == "alice"


def test_consumer_login_invalid_user(consumer_client):
    response = consumer_client.post("/api/consumer/login", json={"username": "nonexistent", "password": "password"})
    assert response.status_code == 401


def test_admin_endpoint_requires_auth(admin_client):
    response = admin_client.get("/api/admin/consumers")
    assert response.status_code == 401
