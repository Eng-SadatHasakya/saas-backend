from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_register_user():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": unique_email,
        "password": "testpass123",
        "organization_name": f"Test Org {uuid.uuid4().hex[:8]}"
    })
    assert response.status_code == 200
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