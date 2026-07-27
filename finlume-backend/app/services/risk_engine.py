from typing import Dict, Any, List
from app.models.models import Transaction, UserProfile

def analyze_risk(transactions: List[Transaction], profile: UserProfile) -> Dict[str, Any]:
    """
    Evaluates current financial trajectories to determine the risk level.
    """
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    
    warnings = []
    points = 0
    
    # 1. Negative Cash Flow
    if total_expense > total_income:
        points += 50
        warnings.append("Critical Negative Cash Flow: Your expenses currently exceed your income, immediately depleting savings.")
    
    # 2. Overspending Risk (Expense Ratio)
    if total_income > 0:
        ratio = total_expense / total_income
        if ratio > 0.8:
            points += 30
            warnings.append(f"High Expenditure Ratio: You are spending {round(ratio*100)}% of your income.")
        elif ratio > 0.6:
            points += 15
            warnings.append(f"Moderate Expenditure Ratio: Spending consumes {round(ratio*100)}% of income leaving minimal buffer.")
            
    # 3. Low Savings/Emergency warning
    if profile:
        monthly_expense_est = total_expense if total_expense > 0 else 1000
        emergency_months = (profile.emergency_fund or 0) / monthly_expense_est
        if emergency_months < 1:
            points += 40
            warnings.append("Severe Emergency Risk: Your emergency fund cannot comfortably cover even 1 month of standard baseline expenses.")
        elif emergency_months < 3:
            points += 20
            warnings.append("Low Emergency Buffer: Experts recommend holding at least 3 months of core expenses in savings.")
    else:
        points += 30
        warnings.append("Unknown Emergency Baseline: Ensure you have an emergency fund configured.")

    # Convert points into severity tiers
    risk_level = "LOW"
    
    if points >= 70:
        risk_level = "HIGH"
    elif points >= 30:
        risk_level = "MEDIUM"
        
    if not warnings:
        warnings = ["Your financial trajectory is stable with no immediate structural risks detected."]
        
    return {
        "risk_level": risk_level,
        "risk_points": min(100, points),
        "explanations": warnings
    }
