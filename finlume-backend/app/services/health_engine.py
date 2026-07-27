from typing import Dict, Any, List
from app.models.models import Transaction, Goal, UserProfile

def calculate_savings_rate(total_income: float, total_expense: float) -> float:
    if total_income <= 0:
        return 0.0
    savings = total_income - total_expense
    return max(0.0, (savings / total_income) * 100)

def evaluate_savings_rate(savings_rate: float) -> int:
    if savings_rate >= 20:
        return 100
    if savings_rate >= 10:
        return 75
    if savings_rate > 0:
        return 50
    return 0

def evaluate_emergency_fund(profile: UserProfile, total_expense: float) -> int:
    if not profile or not profile.emergency_fund or total_expense <= 0:
        return 0
    # Aim for 3-6 months of expenses
    monthly_estimate = total_expense  # simplified assuming 1 month window
    months_covered = profile.emergency_fund / monthly_estimate
    
    if months_covered >= 6:
        return 100
    if months_covered >= 3:
        return 75
    if months_covered >= 1:
        return 40
    return 10

def evaluate_expense_to_income(total_income: float, total_expense: float) -> int:
    if total_income <= 0:
        return 0
    ratio = total_expense / total_income
    if ratio <= 0.5:
        return 100
    if ratio <= 0.7:
        return 80
    if ratio <= 0.9:
        return 50
    return 20

def evaluate_goal_progress(goals: List[Goal]) -> int:
    if not goals:
        return 50 # Neutral if no goals set yet
    
    total_target = sum(g.target_amount for g in goals if g.target_amount > 0)
    total_saved = sum(g.current_amount for g in goals)
    
    if total_target == 0:
        return 50
        
    progress = total_saved / total_target
    if progress >= 1.0:
        return 100
    if progress >= 0.5:
        return 75
    if progress >= 0.1:
        return 40
    return 10

def get_grade(score: int) -> str:
    if score >= 85: return "Excellent"
    if score >= 70: return "Good"
    if score >= 50: return "Fair"
    return "Needs Attention"

def get_summary(score: int) -> str:
    if score >= 85: 
        return "Your financial health is outstanding. Keep maintaining your savings and budget."
    if score >= 70: 
        return "You are on track. Consider optimizing your savings rate to reach 'Excellent' status."
    if score >= 50: 
        return "You are doing okay, but closely monitoring your discretionary expenses could boost your score."
    return "Your financial health requires immediate attention. Focus on reducing core expenses and building an emergency fund."

def calculate_financial_health(
    transactions: List[Transaction], 
    goals: List[Goal], 
    profile: UserProfile
) -> Dict[str, Any]:
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    
    savings_rate = calculate_savings_rate(total_income, total_expense)
    
    # 1. Savings Rate Score (Weight 30%)
    score_savings = evaluate_savings_rate(savings_rate)
    
    # 2. Emergency Fund Score (Weight 30%)
    score_emergency = evaluate_emergency_fund(profile, total_expense)
    
    # 3. Expense to Income Ratio (Weight 20%)
    score_expense_ratio = evaluate_expense_to_income(total_income, total_expense)
    
    # 4. Goals Progress (Weight 20%)
    score_goals = evaluate_goal_progress(goals)
    
    # Final Score Calculation
    final_score = int(
        (score_savings * 0.3) +
        (score_emergency * 0.3) +
        (score_expense_ratio * 0.2) +
        (score_goals * 0.2)
    )
    
    return {
        "score": final_score,
        "grade": get_grade(final_score),
        "summary": get_summary(final_score),
        "metrics": {
            "savings_rate_percentage": round(savings_rate, 2),
            "emergency_fund_score": score_emergency,
            "expense_ratio_score": score_expense_ratio,
            "goals_progress_score": score_goals,
            "total_income_analyzed": total_income,
            "total_expense_analyzed": total_expense
        }
    }
