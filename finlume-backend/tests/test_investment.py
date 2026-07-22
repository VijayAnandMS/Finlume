import pytest
import json

@pytest.fixture(scope="module")
def token_headers(client):
    client.post("/api/auth/register", json={"username": "invest_user", "password": "password", "email": "invest_user@test.com", "full_name": "Test User"})
    res = client.post("/api/auth/login", data={"username": "invest_user", "password": "password", "email": "invest_user@test.com", "full_name": "Test User"})
    token = res.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

def test_investment_plan(client, token_headers):
    payload = {
        "message": "I make ₹1,00,000 monthly and have ₹20,000 in savings to invest. How should I allocate it for long term?",
        "income": 100000,
        "expenses": 60000,
        "savings": 20000,
        "risk": "High",
        "horizon": "Long Term",
        "existing": "None"
    }
    response = client.post("/api/agents/investment", json=payload, headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "investment_score" in data
    assert "recommended_asset_allocation" in data
    assert "risk_level" in data
    assert "advisor_notes" in data
