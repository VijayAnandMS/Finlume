from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json

class ForecastOutput(BaseModel):
    projected_balance_30_days: float = Field(..., description="Estimated bank balance after 30 days based on recurring logic.")
    projected_balance_90_days: float
    projected_balance_180_days: float
    projected_balance_365_days: float
    savings_projection: float = Field(..., description="Estimated total savings accumulated over 12 months.")
    cash_flow_graph: List[Dict[str, float]] = Field(..., description="List of dictionaries map of month to expected cash flow.")
    confidence_score: float = Field(..., description="Score 0-1 on prediction validity")
    advisor_notes: str = Field(..., description="Explanatory notes of the forecast logic")

def analyze_forecast(income: float, expenses: float, current_balance: float = 0, current_savings: float = 0) -> str:
    """
    Executes the forecast logic. In a real environment, this invokes the LLM with `ForecastOutput` schema.
    For integration testing, we provide a deterministic simulated LLM structure.
    """
    monthly_net = income - expenses
    
    output = ForecastOutput(
        projected_balance_30_days=current_balance + monthly_net,
        projected_balance_90_days=current_balance + (monthly_net * 3),
        projected_balance_180_days=current_balance + (monthly_net * 6),
        projected_balance_365_days=current_balance + (monthly_net * 12),
        savings_projection=current_savings + (monthly_net * 0.2 * 12), # assumption 20% to savings
        cash_flow_graph=[
            {"month_1": monthly_net},
            {"month_2": monthly_net},
            {"month_3": monthly_net}
        ],
        confidence_score=0.85,
        advisor_notes="Forecast generated based on static income vs expenses projection."
    )
    
    return json.dumps(output.model_dump())
