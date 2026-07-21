import json
from app.ai.llm_factory import LLMFactory
from app.agents.expense_agent import analyze_expenses
from app.agents.budget_agent import plan_budget
from app.agents.advisor_agent import analyze_financial_decision

def plan_investment(
    user_id: int,
    question: str,
    income: float,
    expenses: float,
    savings: float,
    risk: str,
    horizon: str,
    existing: str,
    summary: dict,
    transactions: list
) -> str:
    # 1. Expense Analysis
    expense_analysis = analyze_expenses(transactions) if transactions else "No transactions available."
    
    # 2. Budget Analysis
    budget_analysis = plan_budget(income, expenses, [])
    
    # 3. Advisor Check
    context = {
        "total_income": income,
        "total_expense": expenses,
        "current_savings": savings
    }
    advisor_question = f"Is the user in a healthy position to invest given their {savings} monthly savings?"
    advisor_analysis = analyze_financial_decision(user_id, advisor_question, context)
    
    prompt = f"""
    You are an expert Investment Intelligence Agent.
    The user asked: {question}
    
    Financial Context:
    Income: {income}
    Expenses: {expenses}
    Savings: {savings}
    Risk Preference: {risk}
    Investment Horizon: {horizon}
    Existing Investments: {existing}
    
    Other Agents Analysis:
    Expense Agent: {str(expense_analysis)[:300]}...
    Budget Agent: {str(budget_analysis)[:300]}...
    Advisor Agent says: {advisor_analysis.get('recommendation', '')}
    
    Provide your recommendations as a strictly valid JSON object adhering EXACTLY to this schema. Do NOT provide financial guarantees. Make recommendations educational.
    {{
      "investment_score": <int 0-100 indicating readiness>,
      "risk_level": "{risk}",
      "recommended_monthly_investment": <float estimated from savings>,
      "recommended_asset_allocation": {{
         "Emergency Fund": <int percentage>,
         "FD": <int percentage>,
         "Bonds": <int percentage>,
         "Index Funds": <int percentage>,
         "Mutual Funds": <int percentage>,
         "ETF": <int percentage>,
         "Stocks": <int percentage>,
         "Gold": <int percentage>,
         "REIT": <int percentage>,
         "Cash": <int percentage>
         // Ensure percentages sum to EXACTLY 100
      }},
      "emergency_fund_check": "<string brief analysis on emergency fund status>",
      "goal_alignment": "<string brief analysis on how this aligns with typical goals>",
      "advisor_notes": "<string brief educational notes (no guarantees)>",
      "investment_plan": "<string clear 2-paragraph actionable strategy>"
    }}
    
    Output ONLY raw JSON. No markdown backticks.
    """
    
    llm = LLMFactory.get_llm()
    result = llm.generate_response(prompt)
    
    if result.startswith("```json"):
        result = result.replace("```json\n", "")
    if result.endswith("```"):
        result = result[:-3]
    
    return result.strip()
