import logging
from typing import List, Dict, Any
from datetime import datetime, date
from collections import defaultdict
from app.models.models import Transaction

logger = logging.getLogger(__name__)

def analyze_category_growth(current_month_txs: List[Transaction], last_month_txs: List[Transaction]) -> List[str]:
    curr_cat = defaultdict(float)
    last_cat = defaultdict(float)
    
    for t in current_month_txs:
        if t.transaction_type == "expense":
            curr_cat[t.category] += t.amount
            
    for t in last_month_txs:
        if t.transaction_type == "expense":
            last_cat[t.category] += t.amount
            
    insights = []
    for cat, curr_amount in curr_cat.items():
        if cat in last_cat and last_cat[cat] > 0:
            last_amount = last_cat[cat]
            diff = curr_amount - last_amount
            if diff > 0:
                pct = (diff / last_amount) * 100
                if pct > 15:  # Significant growth
                    insights.append(f"Your {cat.lower()} spending increased {round(pct)}% compared with last month.")
        elif curr_amount > 50:
            insights.append(f"You spent ${curr_amount} on {cat.lower()} this month, which wasn't an expense last month.")
            
    return insights

def analyze_largest_expenses(transactions: List[Transaction]) -> List[str]:
    if not transactions:
        return []
    total_spend = sum(t.amount for t in transactions if t.transaction_type == "expense")
    if total_spend == 0:
        return []
        
    cat_spend = defaultdict(float)
    for t in transactions:
        if t.transaction_type == "expense":
            cat_spend[t.category] += t.amount
            
    sorted_cats = sorted(cat_spend.items(), key=lambda x: x[1], reverse=True)
    if not sorted_cats:
        return []
        
    top_cat, top_amount = sorted_cats[0]
    pct = (top_amount / total_spend) * 100
    
    return [f"{top_cat} accounts for {round(pct)}% of your total expenses."]

def generate_insights(transactions: List[Transaction]) -> List[str]:
    """Generates a dynamic list of insights analyzing the user's spending trends."""
    if not transactions:
        return ["You don't have enough transactions to generate deep insights yet. Start tracking your spending!"]

    # Basic split by dates (Assuming ISO string formats YY-MM-DD)
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    curr_month_txs = []
    last_month_txs = []
    
    for t in transactions:
        try:
            d = datetime.strptime(t.transaction_date, "%Y-%m-%d")
            if d.year == current_year and d.month == current_month:
                curr_month_txs.append(t)
            elif (d.year == current_year and d.month == current_month - 1) or \
                 (d.year == current_year - 1 and current_month == 1 and d.month == 12):
                last_month_txs.append(t)
        except ValueError:
            pass
            
    insights = []
    
    # 1. Category Growth Analysis
    insights.extend(analyze_category_growth(curr_month_txs, last_month_txs))
    
    # 2. Largest Expenses Analysis
    insights.extend(analyze_largest_expenses(curr_month_txs))
    
    if not insights:
        insights.append("Your spending is stable across all categories with no major spikes.")
        
    return insights
