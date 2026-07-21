def calculate_financial_health(summary_data: dict, goals: list, transactions: list) -> dict:
    """
    Computes financial health on a scale of 0-100 across 4 dimensions: Savings, Debt, Cash Flow, and Goals.
    """
    total_income = summary_data.get("total_income", 0.0)
    total_expense = summary_data.get("total_expense", 0.0)
    net_surplus = total_income - total_expense
    
    # Simple heuristic calculations for mock evaluation
    
    # 1. Savings Score (Scale to 100 based on saving 20% of income)
    target_savings = total_income * 0.2
    savings_score = min(100, int((net_surplus / target_savings) * 100)) if target_savings > 0 else 50
    if net_surplus < 0: savings_score = 0
        
    # 2. Cash Flow Score (Expense vs Income ratio)
    ratio = total_expense / total_income if total_income > 0 else 1.0
    cash_flow_score = max(0, 100 - int(ratio * 100))
    
    # 3. Debt Score (Mock logic as Debt isn't directly tracked yet outside expenses)
    debt_score = 85
    
    # 4. Goal Progress Score
    goal_score = 100
    if goals:
        funded = sum(g.current_amount for g in goals)
        target = sum(g.target_amount for g in goals)
        goal_score = int((funded / target) * 100) if target > 0 else 50
        
    overall = int((savings_score + cash_flow_score + debt_score + goal_score) / 4)
    
    classification = "Poor"
    if overall >= 85: classification = "Excellent"
    elif overall >= 70: classification = "Good"
    elif overall >= 50: classification = "Fair"
        
    return {
        "overall_score": overall,
        "classification": classification,
        "savings_score": savings_score,
        "cash_flow_score": cash_flow_score,
        "debt_score": debt_score,
        "goal_score": goal_score
    }
