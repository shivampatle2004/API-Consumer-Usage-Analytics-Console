ALICE_KEY = "ak_alice_1234567890abcdef"


def test_addition(calculator_client):
    response = calculator_client.get(
        "/api/calculator/add?a=10&b=20",
        headers={"X-API-Key": ALICE_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "addition"
    assert data["a"] == 10.0
    assert data["b"] == 20.0
    assert data["result"] == 30.0


def test_subtraction(calculator_client):
    response = calculator_client.get(
        "/api/calculator/subtract?a=20&b=10",
        headers={"X-API-Key": ALICE_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "subtraction"
    assert data["result"] == 10.0


def test_multiplication(calculator_client):
    response = calculator_client.get(
        "/api/calculator/multiply?a=5&b=6",
        headers={"X-API-Key": ALICE_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "multiplication"
    assert data["result"] == 30.0


def test_division(calculator_client):
    response = calculator_client.get(
        "/api/calculator/divide?a=20&b=4",
        headers={"X-API-Key": ALICE_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "division"
    assert data["result"] == 5.0


def test_divide_by_zero(calculator_client):
    response = calculator_client.get(
        "/api/calculator/divide?a=20&b=0",
        headers={"X-API-Key": ALICE_KEY}
    )
    assert response.status_code == 400
    assert "Division by zero" in response.json()["detail"]


def test_missing_api_key(calculator_client):
    response = calculator_client.get("/api/calculator/add?a=10&b=20")
    assert response.status_code == 401


def test_invalid_api_key(calculator_client):
    response = calculator_client.get(
        "/api/calculator/add?a=10&b=20",
        headers={"X-API-Key": "ak_invalid_key_12345"}
    )
    assert response.status_code == 401
