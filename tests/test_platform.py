from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    # Register
    client.post("/auth/register", json={
        "name": "Platform Test",
        "email": "platform@test.com",
        "password": "testpass123",
        "organization_name": "Platform Test Org"
    })
    # Login
    response = client.post("/auth/login", data={
        "username": "platform@test.com",
        "password": "testpass123"
    })
    return response.json()["access_token"]

def test_platform_summary():
    token = get_token()
    response = client.get("/platform/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "organization" in response.json()
    assert "plan" in response.json()

def test_platform_health():
    token = get_token()
    response = client.get("/platform/health",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_notifications():
    token = get_token()
    response = client.get("/notifications/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_billing_info():
    token = get_token()
    response = client.get("/billing/info",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "plan" in response.json()
    assert "publishable_key" in response.json()