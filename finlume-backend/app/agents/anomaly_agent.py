from pydantic import BaseModel, Field
from typing import List, Optional
import json

class RecurringItem(BaseModel):
    name: str
    recurring_amount: float
    frequency: str = Field(..., description="e.g. Monthly, Weekly")
    next_expected_date: str

class AnomalyItem(BaseModel):
    transaction_name: str
    amount: float
    reason: str = Field(..., description="Why this is flagged as an anomaly or duplicate.")
    severity: str = Field(..., description="High, Medium, Low")

class AnomalyOutput(BaseModel):
    recurring_transactions: List[RecurringItem]
    detected_anomalies: List[AnomalyItem]
    summary_notes: str

def detect_anomalies(transactions: List[dict]) -> str:
    """
    Detects recurring items and anomalies from transaction history.
    """
    # LLM execution mock for the agent layer
    output = AnomalyOutput(
        recurring_transactions=[
            RecurringItem(name="Netflix", recurring_amount=15.0, frequency="Monthly", next_expected_date="2026-08-01")
        ],
        detected_anomalies=[
            AnomalyItem(transaction_name="Unknown Wire Transfer", amount=5000.0, reason="Unusually high spending compared to baseline.", severity="High")
        ],
        summary_notes="Found 1 recurring subscription and 1 high-severity anomaly."
    )
    
    return json.dumps(output.model_dump())
