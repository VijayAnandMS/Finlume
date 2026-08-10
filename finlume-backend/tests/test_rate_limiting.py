import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rate_limiting_intelligence_dashboard():
    dyn_user = f"ratelimituser_{uuid.uuid4().hex[:6]}"
    client.post("/api/auth/register", json={"username": dyn_user, "password": "testpassword", "email": f"{dyn_user}@test.com", "full_name": "Test User"})
    login_response = client.post("/api/auth/login", data={"username": dyn_user, "password": "testpassword"})
    
    # Safely retrieve token. If missing, login failed
    assert "access_token" in login_response.json(), f"Login failed: {login_response.json()}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    responses = []
    # Fire 15 requests aggressively. The limit is 10/minute natively.
    for _ in range(15):
        res = client.get("/api/intelligence/dashboard", headers=headers)
        responses.append(res.status_code)
        
    assert 429 in responses, f"Rate limiter failed to trigger 429. Burst limit bypassed. Responses: {responses}"
