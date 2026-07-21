from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User, Transaction
from app.routes.chat import compute_local_summary
from app.ai.orchestrator import call_orchestrator
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from app.core.config import settings

router = APIRouter(prefix="/api/agents", tags=["Agents"])

class GoalPlannerRequest(BaseModel):
    message: str

class GoalPlannerResponse(BaseModel):
    plan: str
    agents_used: List[str]
    explainability: Dict[str, Any] = {}

@router.post("/goal-planner", response_model=GoalPlannerResponse)
def generate_goal_plan(req: GoalPlannerRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    txs_list = [{"amount": t.amount, "type": t.type, "category": t.category, "date": str(t.date)} for t in txs]
    
    summary = compute_local_summary(current_user.id, db)
    
    anthropic_key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")
    gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    
    if anthropic_key or gemini_key:
        try:
            result = call_orchestrator(current_user.id, req.message, summary, txs_list)
            return GoalPlannerResponse(
                plan=result["reply"],
                agents_used=result["agents_used"],
                explainability=result.get("explainability", {})
            )
        except Exception as e:
            print(f"GOAL PLANNER EXCEPTION: {e}")
            pass

    return GoalPlannerResponse(
        plan="The AI Goal Planner is currently unavailable. Please verify API keys.",
        agents_used=[]
    )
