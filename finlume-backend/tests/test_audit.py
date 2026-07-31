import pytest
import sys
from datetime import timedelta
from unittest.mock import MagicMock, patch
from jose import jwt
from app.core.config import settings
from app.core.security import create_access_token

# Mock Anthropic in sys.modules so the test runs cleanly without installing dependencies
mock_anthropic_module = MagicMock()
# Configure Claude Mock responses
class MockTextBlock:
    def __init__(self, text):
        self.transaction_type="text"
        self.text = text

class MockMessageResponse:
    def __init__(self, content):
        self.content = content


def test_auth_wrong_password(client):
    # Register test user
    client.post(
        "/api/auth/register",
        json={"username": "audituser", "password": "securepassword", "email": "audituser@test.com", "full_name": "Test User"}
    )

    # Login with wrong password (should fail 401)
    login_fail = client.post("/api/auth/login", data={"username": "audituser", "password": "wrongpassword", "email": "audituser@test.com", "full_name": "Test User"}
    )
    assert login_fail.status_code == 401
    assert login_fail.json()["detail"] == "Invalid credentials"


def test_auth_missing_or_expired_jwt(client):
    # 1. Missing Token (401)
    res_missing = client.get("/api/auth/me")
    assert res_missing.status_code == 401

    # 2. Expired Token
    expired_token = create_access_token(
        subject="audituser",
        expires_delta=timedelta(minutes=-10)
    )
    res_expired = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert res_expired.status_code == 401
    assert "validate credentials" in res_expired.json()["detail"].lower()

    # 3. Tampered/Bad Secret Token
    bad_secret_token = jwt.encode(
        {"exp": 9999999999, "sub": "audituser"},
        "wrongsecretkey",
        algorithm="HS256"
    )
    res_tampered = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {bad_secret_token}"}
    )
    assert res_tampered.status_code == 401
    assert "validate credentials" in res_tampered.json()["detail"].lower()


def test_transaction_cross_user_isolation(client):
    # Register & Login User A
    client.post(
        "/api/auth/register",
        json={"username": "usera", "password": "passworda", "email": "usera@test.com", "full_name": "Test User"}
    )
    token_a = client.post("/api/auth/login", data={"username": "usera", "password": "passworda", "email": "usera@test.com", "full_name": "Test User"}
    ).json()["access_token"]

    # Register & Login User B
    client.post(
        "/api/auth/register",
        json={"username": "userb", "password": "passwordb", "email": "userb@test.com", "full_name": "Test User"}
    )
    token_b = client.post("/api/auth/login", data={"username": "userb", "password": "passwordb", "email": "userb@test.com", "full_name": "Test User"}
    ).json()["access_token"]

    # User A creates a transaction
    tx_a = client.post(
        "/api/transactions/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "transaction_date": "2026-07-08",
            "category": "Salary",
            "transaction_type": "income",
            "amount": 50000.0,
            "description": "User A pay"
        }
    ).json()
    tx_a_id = tx_a["id"]

    # User B tries to read User A's transaction (should fail 404)
    res_read = client.get(
        f"/api/transactions/",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert res_read.status_code == 200
    # User B should not see User A's transaction in their list
    user_b_txs = res_read.json()
    assert all(tx["id"] != tx_a_id for tx in user_b_txs)

    # User B tries to update User A's transaction (should fail 404)
    res_update = client.put(
        f"/api/transactions/{tx_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "transaction_date": "2026-07-08",
            "category": "Salary",
            "transaction_type": "income",
            "amount": 99999.0,
            "description": "User B hack attempt"
        }
    )
    assert res_update.status_code == 404

    # User B tries to delete User A's transaction (should fail 404)
    res_delete = client.delete(
        f"/api/transactions/{tx_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert res_delete.status_code == 404


def test_analytics_exact_math(client):
    # Register & Login User C
    client.post(
        "/api/auth/register",
        json={"username": "userc", "password": "passwordc", "email": "userc@test.com", "full_name": "Test User"}
    )
    token_c = client.post("/api/auth/login", data={"username": "userc", "password": "passwordc", "email": "userc@test.com", "full_name": "Test User"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token_c}"}

    # Add controlled cashflows
    # Income: 20000
    client.post("/api/transactions/", headers=headers, json={"transaction_date": "2026-07-08", "category": "Salary", "transaction_type": "income", "amount": 20000.0, "description": "Pay"})
    # Expenses: Food 500, Shopping 1500, Food 250
    client.post("/api/transactions/", headers=headers, json={"transaction_date": "2026-07-08", "category": "Food", "transaction_type": "expense", "amount": 500.0})
    client.post("/api/transactions/", headers=headers, json={"transaction_date": "2026-07-09", "category": "Shopping", "transaction_type": "expense", "amount": 1500.0})
    client.post("/api/transactions/", headers=headers, json={"transaction_date": "2026-07-09", "category": "Food", "transaction_type": "expense", "amount": 250.0})

    # Fetch summary and assert math values
    summary_res = client.get("/api/summary/", headers=headers)
    assert summary_res.status_code == 200
    data = summary_res.json()
    assert data["total_income"] == 20000.0
    assert data["total_expense"] == 2250.0
    assert data["net"] == 17750.0

    # Assert categories aggregated and sorted
    assert len(data["top_categories"]) == 2
    assert data["top_categories"][0]["category"] == "Shopping"
    assert data["top_categories"][0]["amount"] == 1500.0
    assert data["top_categories"][1]["category"] == "Food"
    assert data["top_categories"][1]["amount"] == 750.0


def test_ai_coach_claude_response(client):
    client.post(
        "/api/auth/register",
        json={"username": "agentuser", "password": "passworda", "email": "agentuser@test.com", "full_name": "Test User"}
    )
    # Get auth token
    login_response = client.post("/api/auth/login", data={"username": "agentuser", "password": "passworda", "email": "agentuser@test.com", "full_name": "Test User"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sys.modules["anthropic"] = mock_anthropic_module
    
    # Set mock API key and provider
    with patch("app.core.config.settings.ANTHROPIC_API_KEY", "mock-api-key"), \
         patch("app.core.config.settings.LLM_PROVIDER", "anthropic"):
        # Configure mock response for this test
        mock_message = MockMessageResponse([MockTextBlock("Hello, this is a mocked financial coach response from Claude.")])
        mock_anthropic_module.Anthropic.return_value.messages.create.return_value = mock_message
        mock_anthropic_module.Anthropic.return_value.messages.create.side_effect = None
        
        res = client.post(
            "/api/chat/",
            headers=headers,
            json={"message": "Suggest a savings plan for me."}
        )
        assert res.status_code == 200
        data = res.json()
        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 10


def test_ai_coach_failing_api_fallback(client):
    client.post(
        "/api/auth/register",
        json={"username": "fallbackuser", "password": "passwordb", "email": "fallbackuser@test.com", "full_name": "Test User"}
    )
    login_response = client.post("/api/auth/login", data={"username": "fallbackuser", "password": "passwordb", "email": "fallbackuser@test.com", "full_name": "Test User"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sys.modules["anthropic"] = mock_anthropic_module
    
    # Simulate Claude API throwing an exception
    mock_anthropic_module.Anthropic.return_value.messages.create.side_effect = Exception("Anthropic API rate limit exceeded")
    
    with patch("app.core.config.settings.ANTHROPIC_API_KEY", "mock-api-key"), \
         patch("app.core.config.settings.LLM_PROVIDER", "anthropic"):
        res = client.post(
            "/api/chat/",
            headers=headers,
            json={"message": "Give me a summary of my account"}
        )
        assert res.status_code == 200
        reply = res.json()["reply"]
        assert "reply" in res.json()
        # Should gracefully fall back to heuristics
        assert "expenses" in reply.lower() or "income" in reply.lower()
        assert len(reply) > 20

    # Reset side effect
    mock_anthropic_module.Anthropic.return_value.messages.create.side_effect = None


def test_ai_coach_malformed_transactions(client):
    # Register & Login User D
    client.post(
        "/api/auth/register",
        json={"username": "userd", "password": "passwordd", "email": "userd@test.com", "full_name": "Test User"}
    )
    token_d = client.post("/api/auth/login", data={"username": "userd", "password": "passwordd", "email": "userd@test.com", "full_name": "Test User"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token_d}"}

    # Add transaction with zero amount and empty details
    client.post(
        "/api/transactions/",
        headers=headers,
        json={
            "transaction_date": "2026-07-08",
            "category": "Other",
            "transaction_type": "expense",
            "amount": 0.0,
            "description": ""
        }
    )

    # Trigger chat summary request, ensure no zero-division or crash happens
    res = client.post(
        "/api/chat/",
        headers=headers,
        json={"message": "Give me a summary"}
    )
    assert res.status_code == 200
    assert "income is ₹0.00" in res.json()["reply"].lower()
