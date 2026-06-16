def test_register(client):
    res = client.post("/api/v1/auth/register", json={
        "phone": "+254700000001",
        "email": "test@ecoflow.com",
        "name": "Test User",
        "password": "secret123",
        "role": "seller"
    })
    assert res.status_code == 201


def test_login(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "test@ecoflow.com",
        "password": "secret123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "test@ecoflow.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401