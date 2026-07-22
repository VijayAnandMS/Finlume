import pytest
from app.agents.advisor_agent import analyze_financial_decision
from app.ai.orchestrator import ADVISOR_TOOL_SCHEMA, call_orchestrator
from unittest.mock import patch, MagicMock

def test_advisor_positive_cash_flow():
    context = {"total_income": 100000, "total_expense": 40000}
    result = analyze_financial_decision(1, "Can I buy a laptop for 90000?", context)
    assert result["monthly_cash_flow"] == 60000
    assert result["affordability_score"] in ["Good", "Excellent"]
    assert result["risk_level"] in ["Low Risk", "Moderate"]
    assert "financially reasonable" in result["recommendation"] or "exercise caution" in result["recommendation"]

def test_advisor_negative_cash_flow():
    context = {"total_income": 50000, "total_expense": 60000}
    result = analyze_financial_decision(1, "Can I buy a bike?", context)
    assert result["monthly_cash_flow"] == -10000
    assert result["affordability_score"] == "Poor"
    assert result["risk_level"] == "Very High Risk"
    assert "not advisable" in result["recommendation"]

def test_advisor_no_history():
    context = {"total_income": 0, "total_expense": 0}
    result = analyze_financial_decision(1, "Can I afford this?", context)
    assert result["monthly_cash_flow"] == 0
    assert result["affordability_score"] == "Poor"
    assert result["risk_level"] == "Very High Risk"
    assert "not advisable" in result["recommendation"]

def test_advisor_high_expenses():
    context = {"total_income": 100000, "total_expense": 95000}
    result = analyze_financial_decision(1, "Can I buy a watch?", context)
    assert result["monthly_cash_flow"] == 5000
    assert "High Risk" in result["risk_level"]

def test_advisor_emergency_fund():
    context = {"total_income": 100000, "total_expense": 20000}
    # Remaining: 80k. Emergency fund: 80k * 3 / 20k = 12 months > 3
    result = analyze_financial_decision(1, "Can I afford a holiday?", context)
    assert "12.0" in result["emergency_fund_status"]
    assert result["affordability_score"] == "Excellent"

def test_tool_registration():
    assert ADVISOR_TOOL_SCHEMA["name"] == "advisor_agent"
    assert "user_id" in ADVISOR_TOOL_SCHEMA["input_schema"]["properties"]

def test_orchestrator_invocation():
    # Verify the orchestrator schema list includes the advisor
    from app.ai.orchestrator import EXPENSE_TOOL_SCHEMA, BUDGET_TOOL_SCHEMA
    tools = [EXPENSE_TOOL_SCHEMA, BUDGET_TOOL_SCHEMA, ADVISOR_TOOL_SCHEMA]
    assert len(tools) == 3
    assert ADVISOR_TOOL_SCHEMA in tools

def test_api_endpoint(client):
    # Register and login to get auth token
    client.post(
        "/api/auth/register",
        json={"username": "advisortest", "password": "password", "email": "advisortest@test.com", "full_name": "Test User"}
    )
    login_response = client.post("/api/auth/login", data={"username": "advisortest", "password": "password", "email": "advisortest@test.com", "full_name": "Test User"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with patch("app.routes.advisor.call_orchestrator") as mock_orchestrator:
        mock_orchestrator.return_value = {
            "reply": "Here is your advice.",
            "agents_used": ["advisor_agent"],
            "advisor_data": {
                "recommendation": "Go for it",
                "calculations": {"remaining": 500},
                "affordability_score": "Good",
                "risk_level": "Low"
            }
        }
        
        with patch("app.routes.advisor.settings.ANTHROPIC_API_KEY", "mock-key"):
            response = client.post(
                "/api/agents/advisor",
                json={"question": "Can I afford this?"},
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "advisor_agent" in data["agents_used"]
            assert data["recommendation"] == "Go for it"
            assert data["affordability_score"] == "Good"
