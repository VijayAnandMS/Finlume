from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User, Transaction
from app.routes.chat import compute_local_summary
from app.ai.orchestrator import call_orchestrator
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from app.core.config import settings

router = APIRouter(prefix="/api/agents", tags=["Agents"])

class AdvisorRequest(BaseModel):
    question: str

class AdvisorResponse(BaseModel):
    answer: str
    agents_used: List[str]
    calculations: Dict[str, Any]
    recommendation: str
    affordability_score: Optional[str] = None
    savings_rate: Optional[str] = None
    emergency_fund_status: Optional[str] = None
    monthly_cash_flow: Optional[float] = None
    risk_level: Optional[str] = None
    explainability: Dict[str, Any] = {}

@router.post("/advisor", response_model=AdvisorResponse)
def get_advisor_recommendation(req: AdvisorRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    txs_list = [{"amount": t.amount, "type": t.type, "category": t.category, "date": str(t.date)} for t in txs]
    
    summary = compute_local_summary(current_user.id, db)
    
    anthropic_key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")
    gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    
    if anthropic_key or gemini_key:
        try:
            result = call_orchestrator(current_user.id, req.question, summary, txs_list)
            advisor_data = result.get("advisor_data") or {}
            return AdvisorResponse(
                answer=result["reply"],
                agents_used=result["agents_used"],
                calculations=advisor_data.get("calculations", {}),
                recommendation=advisor_data.get("recommendation", ""),
                affordability_score=advisor_data.get("affordability_score"),
                savings_rate=advisor_data.get("savings_rate"),
                emergency_fund_status=advisor_data.get("emergency_fund_status"),
                monthly_cash_flow=advisor_data.get("monthly_cash_flow"),
                risk_level=advisor_data.get("risk_level"),
                explainability=result.get("explainability", {})
            )
        except Exception as e:
            print(f"ADVISOR EXCEPTION: {e}")
            pass

    return AdvisorResponse(
        answer="I'm unable to process this request without an active AI agent.",
        agents_used=[],
        calculations={},
        recommendation="API Unavailable"
    )
