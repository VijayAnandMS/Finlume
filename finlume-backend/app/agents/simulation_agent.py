from pydantic import BaseModel, Field
from typing import List, Dict
import json

class SimulationOutput(BaseModel):
    simulated_budget: Dict[str, float] = Field(..., description="New adjusted budget allocations")
    simulated_goals_impact: str = Field(..., description="How this impacts existing goals")
    simulated_investments: float = Field(..., description="Adjusted net investment portfolio")
    simulated_forecast: Dict[str, float] = Field(..., description="Adjusted future timeline")
    explanation: str

def execute_simulation(scenario: str, current_income: float, current_expenses: float) -> str:
    """
    Processes What-If scenarios.
    """
    output = SimulationOutput(
        simulated_budget={"Housing": current_expenses * 0.4, "Savings": current_income * 0.3},
        simulated_goals_impact="Achieving emergency fund 2 months faster under this scenario.",
        simulated_investments=10000.0,
        simulated_forecast={"30_days": current_income - current_expenses + 500},
        explanation=f"Simulating scenario: {scenario}"
    )
    return json.dumps(output.model_dump())
