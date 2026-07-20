from typing import Dict, Any, List
from app.agents.expense_agent import analyze_expenses
from app.agents.budget_agent import plan_budget
from app.agents.advisor_agent import analyze_financial_decision

def plan_goal(user_id: int, goal_name: str, target_amount: float, deadline: str, summary: Dict[str, Any], transactions: List[Dict[str, Any]]) -> str:
    # 1. Analyze Expenses
    expense_analysis = analyze_expenses(transactions)
    
    # 2. Plan Budget
    total_income = summary.get('total_income', 0.0)
    total_expense = summary.get('total_expense', 0.0)
    top_categories = [{"category": c[0], "amount": c[1]} for c in summary.get("top_categories", [])]
    budget_analysis = plan_budget(total_income, total_expense, top_categories)
    
    # 3. Analyze Financial Decision via Advisor
    question = f"Is it feasible to start saving for {goal_name} (Target: {target_amount}) by {deadline}?"
    context = {
        "total_income": total_income,
        "total_expense": total_expense
    }
    advisor_analysis = analyze_financial_decision(user_id, question, context)
    
    risk = advisor_analysis.get('risk_level', 'Unknown')
    affordability = advisor_analysis.get('affordability_score', 'Unknown')
    rec = advisor_analysis.get('recommendation', '')
    
    lines = [
        f"**Goal Strategy: {goal_name}**",
        f"- Target: ₹{target_amount:.2f}",
        f"- Deadline: {deadline}",
        "",
        "**1. Advisor Risk Assessment**",
        f"Analysis: {rec}",
        f"Risk Level: {risk} | Affordability Score: {affordability}",
        "",
        "**2. Expense Optimization**",
        expense_analysis,
        "Consider reducing top spending categories to free up monthly savings.",
        "",
        "**3. Budget Alignment**",
        budget_analysis,
    ]
    
    return "\n".join(lines)
