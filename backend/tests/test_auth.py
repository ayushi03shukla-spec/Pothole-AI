"""
tests/test_auth.py
Covers registration, login, duplicate-email rejection, bad password,
and the protected /me endpoint.
"""


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "name": "Anika",
        "email": "anika@example.com",
        "password": "secure123",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "token" in data
    assert data["user"]["email"] == "anika@example.com"


def test_register_duplicate_email(client):
    payload = {"name": "A", "email": "dup@example.com", "password": "password1"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_invalid_email(client):
    resp = client.post("/api/auth/register", json={
        "name": "A", "email": "not-an-email", "password": "password1",
    })
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post("/api/auth/register", json={
        "name": "A", "email": "shortpass@example.com", "password": "123",
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={
        "name": "B", "email": "loginuser@example.com", "password": "password1",
    })
    resp = client.post("/api/auth/login", json={
        "email": "loginuser@example.com", "password": "password1",
    })
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "name": "C", "email": "wrongpass@example.com", "password": "password1",
    })
    resp = client.post("/api/auth/login", json={
        "email": "wrongpass@example.com", "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["user"]["email"] == "test@example.com"
