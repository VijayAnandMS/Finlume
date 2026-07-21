import os
import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User, Transaction
from app.core.config import settings
from app.routes.chat import compute_local_summary
from app.ai.orchestrator import call_orchestrator

router = APIRouter(prefix="/api/agents", tags=["Agents"])

class InvestmentRequest(BaseModel):
    message: str
    income: float = 0
    expenses: float = 0
    savings: float = 0
    risk: str = "Medium"
    horizon: str = "Medium Term"
    existing: str = ""

class InvestmentResponse(BaseModel):
    investment_score: int
    risk_level: str
    recommended_monthly_investment: float
    recommended_asset_allocation: Dict[str, float]
    emergency_fund_check: str
    goal_alignment: str
    advisor_notes: str
    investment_plan: str
    explainability: Dict[str, Any] = {}

@router.post("/investment", response_model=InvestmentResponse)
def generate_investment_plan(req: InvestmentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    txs_list = [{"amount": t.amount, "type": t.type, "category": t.category, "date": str(t.date)} for t in txs]
    
    summary = compute_local_summary(current_user.id, db)
    
    anthropic_key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")
    gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    
    if anthropic_key or gemini_key:
        try:
            # We construct a formatted message so orchestrator recognizes the exact params
            full_msg = f'''Question: {req.message}
Income: {req.income}
Expenses: {req.expenses}
Savings: {req.savings}
Risk: {req.risk}
Horizon: {req.horizon}
Existing: {req.existing}
'''
            result = call_orchestrator(current_user.id, full_msg, summary, txs_list)
            # The orchestrator reply should contain the raw JSON from the agent because the agent returns JSON. But orchestrator tries to format it via LLM. 
            # Wait, `call_orchestrator`'s final step uses an LLM to generate a reply based on the tool results. If it does that, it might NOT output perfect JSON.
            # INSTEAD, let's catch the payload directly from the tool call inside the backend or just parse it!
            
            # Since orchestrator returns `{"reply": "...", "agents_used": ...}`, we'll attempt to parse the reply as JSON.
            text = result["reply"]
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.replace("```", "").strip()
                
            parsed = json.loads(text)
            if "explainability" in result:
                parsed["explainability"] = result["explainability"]
            return InvestmentResponse(**parsed)
        except Exception as e:
            print(f"INVESTMENT PLANNER EXCEPTION: {e}")
            pass
            
    # Fallback response
    return InvestmentResponse(
        investment_score=0,
        risk_level=req.risk,
        recommended_monthly_investment=0.0,
        recommended_asset_allocation={},
        emergency_fund_check="Agent unavailable.",
        goal_alignment="Agent unavailable.",
        advisor_notes="Please check API Keys.",
        investment_plan="The AI agent is completely offline."
    )
