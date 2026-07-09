from typing import List, Dict, Any

def plan_budget(total_income: float, total_expense: float, top_categories: List[Dict[str, Any]]) -> str:
    """
    Creates a basic budget plan based on income, expense, and top spending categories.
    
    Args:
        total_income: The user's total income.
        total_expense: The user's total expenses.
        top_categories: A list of dictionaries representing top expense categories.
                        Each dict should have 'category' and 'amount' keys.
                        
    Returns:
        A string summarizing the budget plan.
    """
    if total_income <= 0:
        return "You need to have a recorded income to create a meaningful budget plan."
        
    net_surplus = total_income - total_expense
    
    plan_parts = []
    
    if net_surplus <= 0:
        plan_parts.append(f"Your expenses (₹{total_expense:.2f}) currently exceed or match your income (₹{total_income:.2f}). "
                          "You should immediately look to reduce non-essential spending.")
    else:
        suggested_savings = net_surplus * 0.5
        plan_parts.append(f"You have a net surplus of ₹{net_surplus:.2f}. "
                          f"A good rule of thumb is to save at least 50% of your surplus, which is ₹{suggested_savings:.2f}.")
                          
    if top_categories:
        top_cat = top_categories[0]
        cat_name = top_cat.get('category', 'Unknown')
        cat_amt = top_cat.get('amount', 0.0)
        
        if cat_amt > (total_income * 0.3):
            plan_parts.append(f"Warning: Your top expense '{cat_name}' (₹{cat_amt:.2f}) takes up more than 30% of your income. "
                              "Consider finding ways to reduce this specific cost.")
        else:
            plan_parts.append(f"Your top expense is '{cat_name}' at ₹{cat_amt:.2f}. Keep monitoring this to ensure it stays within reasonable limits.")
            
    return " ".join(plan_parts)
