from typing import Dict, Any

def analyze_financial_decision(user_id: int, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes a financial decision based on the user's income, expenses, and goals.
    
    Args:
        user_id: The ID of the user.
        question: The financial question or decision to analyze (e.g., "Can I buy a laptop?").
        context: Additional financial context including 'total_income' and 'total_expense'.
    
    Returns:
        A dictionary containing the recommendation, affordability score, and risk calculations.
    """
    total_income = context.get('total_income', 0.0)
    total_expense = context.get('total_expense', 0.0)
    
    remaining_cash = total_income - total_expense
    savings_percentage = 0
    if total_income > 0:
        savings_percentage = (remaining_cash / total_income) * 100
        
    # Mocking emergency fund since it's not directly in the standard transactions schema
    # We estimate based on a generic multiplier of remaining cash for the sake of the heuristic.
    emergency_fund_months = remaining_cash * 3 / total_expense if total_expense > 0 else 0
    
    # Determine Affordability Score and Risk Level
    if remaining_cash <= 0:
        risk_level = "Very High Risk"
        affordability_score = "Poor"
    elif savings_percentage < 10:
        risk_level = "High Risk"
        affordability_score = "Moderate"
    elif savings_percentage <= 20:
        risk_level = "Moderate"
        affordability_score = "Good"
    else:
        risk_level = "Low Risk"
        affordability_score = "Excellent"
        
    if emergency_fund_months >= 3 and affordability_score != "Poor":
        affordability_score = "Excellent" # Bonus score
        
    # Generate reasoning
    reasoning = (
        f"Your current monthly income is ₹{total_income:.2f} with expenses around ₹{total_expense:.2f}. "
        f"This leaves you with a cash flow of ₹{remaining_cash:.2f} (Savings rate: {savings_percentage:.1f}%). "
    )
    
    if "Poor" in affordability_score or "High Risk" in risk_level:
        recommendation = "It is not advisable to make large financial commitments right now."
        reasoning += "Your current cash flow is tight. Focus on increasing your savings rate before considering this."
    elif "Moderate" in affordability_score:
        recommendation = "You can proceed, but exercise caution."
        reasoning += "You have some breathing room, but a large purchase could deplete your safety net. Consider saving specifically for this."
    else:
        recommendation = "This appears financially reasonable."
        reasoning += "You have a healthy savings rate and sufficient cash flow to accommodate this."

    return {
        "summary": "Financial analysis complete.",
        "recommendation": recommendation,
        "affordability_score": affordability_score,
        "savings_rate": f"{savings_percentage:.1f}%",
        "emergency_fund_status": f"{emergency_fund_months:.1f} months",
        "monthly_cash_flow": remaining_cash,
        "risk_level": risk_level,
        "reasoning": reasoning,
        "calculations": {
            "income": total_income,
            "expenses": total_expense,
            "remaining": remaining_cash
        }
    }
