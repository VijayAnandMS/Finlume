from app.agents.forecast_agent import analyze_forecast
from app.agents.anomaly_agent import detect_anomalies
from app.agents.simulation_agent import execute_simulation
from app.services.memory_service import memory_service, MemoryEntry
import json

def test_forecast_agent():
    res = analyze_forecast(income=5000, expenses=3000, current_balance=1000)
    data = json.loads(res)
    assert "projected_balance_30_days" in data
    assert data["projected_balance_30_days"] == 3000

def test_anomaly_agent():
    res = detect_anomalies([{"amount": 5000, "name": "Test"}])
    data = json.loads(res)
    assert "detected_anomalies" in data

def test_simulation_agent():
    res = execute_simulation("What if I save more?", 5000, 3000)
    data = json.loads(res)
    assert "simulated_budget" in data

def test_memory_service():
    memory_service.add_memory(MemoryEntry(id="test_1", text="User saved 10k", metadata={"user": 1}))
    results = memory_service.query_memory("How much saved?")
    assert len(results) > 0
    assert results[0].text == "User saved 10k"
