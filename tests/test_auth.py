from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123",
        "organization_name": "Test Org"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["role"] == "admin"

def test_login_user():
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_login_invalid():
    response = client.post("/auth/login", data={
        "username": "wrong@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 400