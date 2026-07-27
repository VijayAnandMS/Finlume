from typing import List, Dict, Any
from collections import defaultdict
from app.models.models import Transaction, UserProfile

def generate_recommendations(transactions: List[Transaction], profile: UserProfile) -> List[str]:
    """
    Generates actionable financial recommendations dynamically extracted from 
    live transaction context and current profile bounds.
    """
    recs = []
    if not transactions:
        recs.append("Start tracking your transactions to unlock personalized insights.")
        return recs

    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    
    # Analyze emergency structure
    if profile:
        monthly_expense_est = total_expense if total_expense > 0 else 1000
        emergency_months = (profile.emergency_fund or 0) / monthly_expense_est
        if emergency_months < 3:
            recs.append(f"Increase emergency savings. You currently only have {(profile.emergency_fund or 0)} which covers less than {round(emergency_months, 1)} months of your standard runway.")
            
    # Analyze categories for optimization
    cat_spend = defaultdict(float)
    merchants = defaultdict(list)
    
    for t in transactions:
        if t.transaction_type == "expense":
            cat_spend[t.category] += t.amount
            if t.merchant:
                merchants[t.merchant.lower().strip()].append(t)
    
    # 1. Discretionary Spending Reductions
    if "restaurant" in cat_spend or "food" in cat_spend:
        rest_spend = cat_spend.get("restaurant", 0) + cat_spend.get("food", 0)
        if total_expense > 0 and rest_spend / total_expense > 0.25:
            recs.append(f"Consider reducing restaurant and food spending. At ${rest_spend}, it represents a huge {round((rest_spend/total_expense)*100)}% of your expenses.")
            
    if "entertainment" in cat_spend:
        ent_spend = cat_spend["entertainment"]
        if ent_spend > 500:
            recs.append("Delay discretionary purchases. Your entertainment spending is exceptionally high right now.")

    # 2. Duplicate subscriptions logic (Crude: hitting same merchant same month)
    # Detect recurring identical amounts across same merchants
    duplicates = 0
    for merchant, txs in merchants.items():
        if len(txs) >= 2:
            # check if amounts match exactly
            amts = [tx.amount for tx in txs]
            if len(set(amts)) == 1 and len(amts) > 1:
                duplicates += 1
                if duplicates == 1:
                    recs.append(f"Review recurring charges to '{merchant.title()}'. Double check you don't have duplicate or unneeded subscriptions.")

    # 3. Income to Expense mapping and Investment
    savings = total_income - total_expense
    if savings > 1000 and profile and (profile.existing_investments or 0) < 5000:
        recs.append(f"Increase investment allocation. You frequently maintain strong cash surplus (${round(savings)}/mo) but have low market investments mapped.")
        
    if not recs:
        recs.append("Your financial habits appear highly optimized against our standard heuristic tracks.")
        
    return recs[:5] # Top 5 recommendations limit
