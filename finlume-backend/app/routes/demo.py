from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User, Transaction, Goal
import datetime
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/mock", tags=["Demo Sandbox"])

@router.post("/populate", summary="Initialize Sandbox")
def populate_demo_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Wipes current user data and injects rich, realistic transaction and goal data spanning 90 days suitable for portfolio visualizations."""
    
    # 1. Clean existing state conditionally
    db.query(Transaction).filter(Transaction.user_id == current_user.id).delete()
    db.query(Goal).filter(Goal.user_id == current_user.id).delete()
    
    # 2. Add Goals
    goals = [
        Goal(user_id=current_user.id, name="Emergency Fund", target_amount=200000, current_amount=50000, deadline=datetime.date(2027, 1, 1)),
        Goal(user_id=current_user.id, name="Stock Portfolio Growth", target_amount=500000, current_amount=320000, deadline=datetime.date(2028, 6, 1)),
    ]
    db.add_all(goals)
    
    # 3. Add Realistic Transactions
    today = datetime.date.today()
    txs = []
    
    # Salary injects
    for i in range(3):
        txs.append(Transaction(user_id=current_user.id, amount=120000, transaction_type="income", category="Salary", transaction_date=today - datetime.timedelta(days=i*30)))
        
    # High frequency expenses
    expenses = [
        (450, "Food"), (1200, "Food"), (20000, "Rent"), (8000, "Shopping"),
        (2500, "Utilities"), (999, "Entertainment"), (5000, "Travel")
    ]
    
    for i in range(60):
        amount, category = expenses[i % len(expenses)]
        offset = today - datetime.timedelta(days=i)
        txs.append(Transaction(user_id=current_user.id, amount=amount, transaction_type="expense", category=category, transaction_date=offset))
    
    db.add_all(txs)
    db.commit()
    
    return JSONResponse(status_code=201, content={"status": "success", "message": "Demo Sandbox initialized successfully."})
