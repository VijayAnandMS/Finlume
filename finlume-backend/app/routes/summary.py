from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Transaction
from app.schemas.schemas import SummaryOut, CategorySummary
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/summary", tags=["summary"])

@router.get("/", response_model=SummaryOut)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    
    total_income = sum(t.amount for t in txs if t.type == "income")
    total_expense = sum(t.amount for t in txs if t.type == "expense")
    net = total_income - total_expense
    
    by_category = {}
    for t in txs:
        if t.type == "expense":
            by_category[t.category] = by_category.get(t.category, 0.0) + t.amount
            
    top_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    top_cats_out = [
        CategorySummary(category=cat, amount=amt) for cat, amt in top_categories[:3]
    ]
    
    # Sort last 10 transactions by date/id descending
    sorted_txs = sorted(txs, key=lambda x: (x.date, x.id), reverse=True)
    
    return SummaryOut(
        total_income=total_income,
        total_expense=total_expense,
        net=net,
        top_categories=top_cats_out,
        transactions=sorted_txs[:10]
    )
