from fastapi import APIRouter, Depends, Request
from app.core.rate_limit import limiter
from app.core.config import settings
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.database import get_db
from app.models.models import User, Transaction, Goal, UserProfile
from app.routes.auth import get_current_user

from app.services.health_engine import calculate_financial_health
from app.services.insight_engine import generate_insights
from app.services.forecast_engine import predict_balances
from app.services.risk_engine import analyze_risk
from app.services.goal_engine import analyze_goals
from app.services.recommendation_engine import generate_recommendations

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

def _get_user_context(current_user: User, db: Session):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return transactions, goals, profile

@router.get("/health")
def get_health_score(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs, goals, profile = _get_user_context(current_user, db)
    return calculate_financial_health(txs, goals, profile)

@router.get("/forecast")
def get_forecast(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs, _, _ = _get_user_context(current_user, db)
    
    # Calculate simple current balance
    total_income = sum(t.amount for t in txs if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in txs if t.transaction_type == 'expense')
    current_balance = total_income - total_expense
    
    return predict_balances(txs, current_balance)

@router.get("/insights")
def get_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs, _, _ = _get_user_context(current_user, db)
    return {"insights": generate_insights(txs)}

@router.get("/recommendations")
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs, _, profile = _get_user_context(current_user, db)
    return {"recommendations": generate_recommendations(txs, profile)}

@router.get("/risk")
def get_risk(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs, _, profile = _get_user_context(current_user, db)
    return analyze_risk(txs, profile)

@router.get("/goals")
def get_goal_intelligence(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs, goals, _ = _get_user_context(current_user, db)
    return {"goal_intelligence": analyze_goals(goals, txs)}

@router.get("/dashboard")
@limiter.limit(settings.RATE_LIMIT_AI)
def get_full_intelligence_dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aggregates all intelligence engines into a single call for the primary frontend dashboard view."""
    txs, goals, profile = _get_user_context(current_user, db)
    
    total_income = sum(t.amount for t in txs if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in txs if t.transaction_type == 'expense')
    current_balance = total_income - total_expense
    
    return {
        "health": calculate_financial_health(txs, goals, profile),
        "forecast": predict_balances(txs, current_balance),
        "insights": generate_insights(txs),
        "recommendations": generate_recommendations(txs, profile),
        "risk": analyze_risk(txs, profile),
        "goals": analyze_goals(goals, txs)
    }

from app.services.insights_service import generate_financial_insights_payload

@router.get("/insights_engine")
def get_financial_insights_engine(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs, _, profile = _get_user_context(current_user, db)
    return generate_financial_insights_payload(txs, profile)

