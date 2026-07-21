from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User, UserProfile
from app.schemas.schemas import UserProfileData

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile:
        return {"status": "empty"}
    return current_user.profile

@router.put("/")
def update_profile(data: UserProfileData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        # flush to assign ID or construct safely
    else:
        profile = current_user.profile
        
    profile.income = data.income
    profile.currency = data.currency
    profile.salary_frequency = data.salary_frequency
    profile.monthly_expenses = data.monthly_expenses
    profile.financial_goals = data.financial_goals
    profile.risk_level = data.risk_level
    profile.investment_experience = data.investment_experience
    profile.emergency_fund = data.emergency_fund
    profile.existing_investments = data.existing_investments
    profile.loan_amount = data.loan_amount
    
    if not current_user.profile_completed:
        current_user.profile_completed = True
        
    db.commit()
    
    return {"status": "success", "message": "Profile updated."}
