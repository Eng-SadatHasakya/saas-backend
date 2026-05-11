from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

# Shared test credentials
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_ORG = f"Test Org {uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "testpass123"

def test_register_user():
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "organization_name": TEST_ORG
    })
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

def test_login_user():
    response = client.post("/auth/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
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