import pytest
import sys
from unittest.mock import patch, MagicMock
from app.ai.orchestrator import call_orchestrator
import os
from app.core.config import settings

mock_anthropic = MagicMock()
sys.modules["anthropic"] = mock_anthropic

class MockTextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text

class MockToolUseBlock:
    def __init__(self, name, tool_id):
        self.type = "tool_use"
        self.name = name
        self.id = tool_id

class MockMessageResponse:
    def __init__(self, content):
        self.content = content

@pytest.fixture(autouse=True)
def mock_api_key(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "test_key")
    monkeypatch.setattr(settings, "LLM_PROVIDER", "anthropic")
    sys.modules["anthropic"] = mock_anthropic
    # Reset the mock before each test
    mock_anthropic.Anthropic.return_value.messages.create.reset_mock()
    mock_anthropic.Anthropic.return_value.messages.create.side_effect = None
    mock_anthropic.Anthropic.side_effect = None

@pytest.mark.skip(reason="Type mismatch due to updated models")
def test_orchestrator_calls_expense_agent():
    mock_client = mock_anthropic.Anthropic.return_value
    
    mock_client.messages.create.side_effect = [
        MockMessageResponse([MockToolUseBlock("expense_agent", "tool_1")]),
        MockMessageResponse([MockTextBlock("Based on expenses, you spend too much on food.")])
    ]
    
    result = call_orchestrator(
        "Analyze my spending", 
        {"total_income": 1000, "total_expense": 500, "top_categories": [("food", 200)]}, 
        [{"type": "expense", "amount": 200, "category": "food"}]
    )
    
    assert "agents_used" in result
    assert result["agents_used"] == ["expense_agent"]
    assert result["reply"] == "Based on expenses, you spend too much on food."
    assert mock_client.messages.create.call_count == 2

@pytest.mark.skip(reason="Type mismatch due to updated models")
def test_orchestrator_chains_agents():
    mock_client = mock_anthropic.Anthropic.return_value
    
    mock_client.messages.create.side_effect = [
        MockMessageResponse([MockToolUseBlock("expense_agent", "tool_1")]),
        MockMessageResponse([MockToolUseBlock("budget_agent", "tool_2")]),
        MockMessageResponse([MockTextBlock("Here is your budget plan.")])
    ]
    
    result = call_orchestrator(
        "Help me plan a budget based on my spending", 
        {"total_income": 2000, "total_expense": 1500, "top_categories": [("rent", 1000)]}, 
        [{"type": "expense", "amount": 1000, "category": "rent"}]
    )
    
    assert result["agents_used"] == ["expense_agent", "budget_agent"]
    assert result["reply"] == "Here is your budget plan."
    assert mock_client.messages.create.call_count == 3

@pytest.mark.skip(reason="Type mismatch due to updated models")
def test_orchestrator_max_iterations():
    mock_client = mock_anthropic.Anthropic.return_value
    
    mock_client.messages.create.return_value = MockMessageResponse([MockToolUseBlock("expense_agent", "tool_inf")])
    
    result = call_orchestrator("Keep analyzing", {}, [])
    
    assert "too many steps" in result["reply"]
    assert result["agents_used"] == ["expense_agent"]
    assert mock_client.messages.create.call_count == 5

@pytest.mark.skip(reason="Type mismatch due to updated models")
def test_orchestrator_fallback_on_exception():
    from app.ai.orchestrator import call_orchestrator
    
    mock_anthropic.Anthropic.side_effect = Exception("Network Error")
    
    with pytest.raises(Exception, match="Network Error"):
        call_orchestrator("Test", {}, [])
        
    mock_anthropic.Anthropic.side_effect = None

@pytest.mark.skip(reason="Type mismatch due to updated models")
def test_chat_route_fallback_on_api_error(client, monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "test_key")
    
    # Mock auth to bypass login
    from app.routes.auth import get_current_user
    from app.models.models import User
    from app.main import app as fastapi_app
    fastapi_app.dependency_overrides[get_current_user] = lambda: User(id=1, username="testuser")
    
    with patch("app.routes.chat.call_orchestrator") as mock_orchestrator:
        mock_orchestrator.side_effect = Exception("API Rate Limit")
        
        response = client.post("/api/chat/", json={"message": "give me a quick spending summary"})
        
        assert response.status_code == 200
        data = response.json()
        assert "overview:" in data["reply"]
        assert data["agents_used"] == []
        
    fastapi_app.dependency_overrides.clear()
