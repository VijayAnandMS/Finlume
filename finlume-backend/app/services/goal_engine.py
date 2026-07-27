from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from app.models.models import Goal, Transaction

def analyze_goals(goals: List[Goal], transactions: List[Transaction]) -> List[Dict[str, Any]]:
    """
    Analyzes all active goals and constructs intelligence maps for each, calculating
    probabilities of success based on current savings rate velocities.
    """
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_savings = max(0.0, total_income - total_expense)
    
    # Estimate standard monthly savings generated organically from transactions (crude heuristic based on active span)
    span_months = 1 # fallback
    if transactions:
        tx_dates = [datetime.strptime(t.transaction_date, "%Y-%m-%d") for t in transactions]
        min_date = min(tx_dates)
        max_date = max(tx_dates)
        delta_days = (max_date - min_date).days
        span_months = max(1.0, delta_days / 30.0)
    
    monthly_organic_savings = net_savings / span_months

    insights = []
    
    for goal in goals:
        if goal.status != "active":
            continue
            
        remaining = max(0.0, goal.target_amount - goal.current_amount)
        progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 100.0
        
        # Calculate time remaining mathematically
        months_remaining = -1
        deadline_str = "No deadline set"
        if goal.deadline:
            try:
                deadline_dt = datetime.strptime(goal.deadline, "%Y-%m-%d")
                months_remaining = max(0, (deadline_dt - datetime.now()).days // 30)
                deadline_str = goal.deadline
            except ValueError:
                pass
                
        # Calculations
        req_monthly = remaining / months_remaining if months_remaining > 0 else 0
        probability = 100
        
        recommendation = "You are fully on track to achieve this goal."
        
        if months_remaining > 0:
            if monthly_organic_savings >= req_monthly:
                probability = min(98, 70 + int((monthly_organic_savings / (req_monthly + 1))*10))
                recommendation = f"You organically save ${round(monthly_organic_savings)}/mo which securely covers your required ${round(req_monthly)}/mo for this goal."
            elif req_monthly > 0:
                probability = int((monthly_organic_savings / req_monthly) * 100)
                probability = min(60, max(5, probability))
                recommendation = f"You are falling slightly short. You need to save ${round(req_monthly)}/mo, but available monthly surplus is tracking at ${round(monthly_organic_savings)}/mo. Try cutting discretionary expenses."

        estimated_completion = "Achieved" if remaining == 0 else "Unknown"
        if remaining > 0 and monthly_organic_savings > 0:
            months = remaining / monthly_organic_savings
            dt = datetime.now() + timedelta(days=int(months*30))
            estimated_completion = dt.strftime("%Y-%m-%d")
            
        insights.append({
            "goal_id": goal.id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "progress_percent": round(progress, 1),
            "remaining_amount": round(remaining, 2),
            "estimated_completion": estimated_completion,
            "required_monthly_savings": round(req_monthly, 2) if req_monthly > 0 else None,
            "probability_of_success_percent": min(100, max(0, probability)),
            "ai_recommendation": recommendation
        })
        
    return insights
