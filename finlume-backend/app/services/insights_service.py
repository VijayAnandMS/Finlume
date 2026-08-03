import math
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta, date
from collections import defaultdict
from app.models.models import Transaction, UserProfile
from app.ai.llm_client import call_llm_with_tools

logger = logging.getLogger(__name__)

def calculate_monthly_summary(transactions: List[Transaction]) -> List[Dict[str, Any]]:
    """1. Monthly income vs expense summary grouped by YYYY-MM."""
    summary_map = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in transactions:
        try:
            m_str = datetime.strptime(t.transaction_date, "%Y-%m-%d").strftime("%Y-%m")
        except Exception:
            continue
        if t.transaction_type == "income":
            summary_map[m_str]["income"] += t.amount
        elif t.transaction_type == "expense":
            summary_map[m_str]["expense"] += t.amount
            
    sorted_months = sorted(summary_map.keys())
    res = []
    for m in sorted_months:
        inc = round(summary_map[m]["income"], 2)
        exp = round(summary_map[m]["expense"], 2)
        res.append({
            "month": m,
            "income": inc,
            "expense": exp,
            "net": round(inc - exp, 2)
        })
    return res

def calculate_category_spending(transactions: List[Transaction]) -> List[Dict[str, Any]]:
    """2. Spending by category for current month."""
    today = datetime.now()
    curr_month_str = today.strftime("%Y-%m")
    
    cat_map = defaultdict(float)
    total_expense = 0.0
    for t in transactions:
        try:
            t_month = datetime.strptime(t.transaction_date, "%Y-%m-%d").strftime("%Y-%m")
        except Exception:
            continue
        if t_month == curr_month_str and t.transaction_type == "expense":
            cat_map[t.category] += t.amount
            total_expense += t.amount
            
    res = []
    for cat, amt in cat_map.items():
        pct = (amt / total_expense * 100) if total_expense > 0 else 0.0
        res.append({
            "category": cat,
            "amount": round(amt, 2),
            "percentage": round(pct, 2)
        })
    return sorted(res, key=lambda x: x["amount"], reverse=True)

def get_largest_expenses(transactions: List[Transaction], limit: int = 5) -> List[Dict[str, Any]]:
    """3. Largest expenses in the current month."""
    today = datetime.now()
    curr_month_str = today.strftime("%Y-%m")
    curr_expenses = []
    for t in transactions:
        try:
            t_month = datetime.strptime(t.transaction_date, "%Y-%m-%d").strftime("%Y-%m")
        except Exception:
            continue
        if t_month == curr_month_str and t.transaction_type == "expense":
            curr_expenses.append(t)
            
    curr_expenses.sort(key=lambda x: x.amount, reverse=True)
    res = []
    for t in curr_expenses[:limit]:
        res.append({
            "id": t.id,
            "transaction_date": t.transaction_date,
            "category": t.category,
            "amount": t.amount,
            "merchant": t.merchant or t.description or "Unknown Merchant"
        })
    return res

def detect_recurring_merchants(transactions: List[Transaction]) -> List[Dict[str, Any]]:
    """4. Recurring merchant detection (appear >= 2 times with identical/close amount)."""
    merchant_txs = defaultdict(list)
    for t in transactions:
        if t.transaction_type == "expense":
            name = (t.merchant or t.description or "Unknown").strip().lower()
            if name != "unknown" and name != "":
                merchant_txs[name].append((t.transaction_date, t.amount))
                
    recurring = []
    for name, items in merchant_txs.items():
        if len(items) >= 2:
            # Group by approximate amount (+/- 5% tolerance) or exact
            amount_groups = defaultdict(list)
            for date_str, amt in items:
                # Find matching group
                matched = False
                for existing_amt in amount_groups.keys():
                    if abs(existing_amt - amt) / max(1.0, existing_amt) <= 0.05:
                        amount_groups[existing_amt].append((date_str, amt))
                        matched = True
                        break
                if not matched:
                    amount_groups[amt].append((date_str, amt))
                    
            for repr_amt, group in amount_groups.items():
                if len(group) >= 2:
                    dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in group]
                    dates.sort()
                    # Calculate average interval (days)
                    intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                    avg_days = sum(intervals) / len(intervals) if intervals else 30
                    frequency = "monthly"
                    if avg_days < 10:
                        frequency = "weekly"
                    elif avg_days > 45:
                        frequency = "quarterly"
                        
                    recurring.append({
                        "merchant": name.title(),
                        "amount": round(sum(g[1] for g in group)/len(group), 2),
                        "frequency": frequency,
                        "count": len(group)
                    })
    return recurring

def calculate_cash_flow_trend(transactions: List[Transaction]) -> List[Dict[str, Any]]:
    """5. Cash flow trend daily for the past 30 days."""
    today = datetime.now().date()
    start_date = today - timedelta(days=29)
    date_list = [start_date + timedelta(days=i) for i in range(30)]
    
    # Calculate historical net before start date to establish initial balance
    history_net = 0.0
    for t in transactions:
        try:
            t_date = datetime.strptime(t.transaction_date, "%Y-%m-%d").date()
        except Exception:
            continue
        if t_date < start_date:
            val = t.amount if t.transaction_type == "income" else -t.amount
            history_net += val
            
    # Calculate day-by-day delta
    daily_delta = defaultdict(float)
    for t in transactions:
        try:
            t_date = datetime.strptime(t.transaction_date, "%Y-%m-%d").date()
        except Exception:
            continue
        if start_date <= t_date <= today:
            val = t.amount if t.transaction_type == "income" else -t.amount
            daily_delta[t_date] += val
            
    trend = []
    running_balance = history_net
    for d in date_list:
        running_balance += daily_delta[d]
        trend.append({
            "date": d.strftime("%Y-%m-%d"),
            "balance": round(running_balance, 2)
        })
    return trend

def calculate_savings_rate(total_income: float, total_expense: float) -> float:
    """6. Savings rate calculation."""
    if total_income <= 0:
        return 0.0
    savings = total_income - total_expense
    return max(0.0, round((savings / total_income) * 100, 2))

def get_monthly_comparison(transactions: List[Transaction]) -> Dict[str, Any]:
    """7. Monthly comparison of current vs last month expense."""
    today = datetime.now()
    curr_month = today.month
    curr_year = today.year
    
    prev_month = 12 if curr_month == 1 else curr_month - 1
    prev_year = curr_year - 1 if curr_month == 1 else curr_year
    
    curr_total = 0.0
    prev_total = 0.0
    
    for t in transactions:
        try:
            d = datetime.strptime(t.transaction_date, "%Y-%m-%d")
        except Exception:
            continue
        if d.year == curr_year and d.month == curr_month and t.transaction_type == "expense":
            curr_total += t.amount
        elif d.year == prev_year and d.month == prev_month and t.transaction_type == "expense":
            prev_total += t.amount
            
    diff_abs = curr_total - prev_total
    diff_pct = (diff_abs / prev_total * 100) if prev_total > 0 else 0.0
    
    return {
        "current_month_expense": round(curr_total, 2),
        "previous_month_expense": round(prev_total, 2),
        "difference_absolute": round(diff_abs, 2),
        "difference_percentage": round(diff_pct, 2)
    }

def detect_spending_anomalies(transactions: List[Transaction]) -> List[Dict[str, Any]]:
    """8. Spending anomaly detection against 3-month trailing average.
       Threshold: current month > 1.5x of trailing avg.
    """
    today = datetime.now()
    curr_month = today.month
    curr_year = today.year
    
    # Months to analyze
    trailing_months = []
    y, m = curr_year, curr_month
    for _ in range(3):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        trailing_months.append((y, m))
        
    curr_cat = defaultdict(float)
    trail_cat = defaultdict(list)
    
    for t in transactions:
        try:
            d = datetime.strptime(t.transaction_date, "%Y-%m-%d")
        except Exception:
            continue
        if d.year == curr_year and d.month == curr_month:
            if t.transaction_type == "expense":
                curr_cat[t.category] += t.amount
        else:
            for idx, (ty, tm) in enumerate(trailing_months):
                if d.year == ty and d.month == tm and t.transaction_type == "expense":
                    # Initialize list of size 3
                    if t.category not in trail_cat:
                        trail_cat[t.category] = [0.0, 0.0, 0.0]
                    trail_cat[t.category][idx] += t.amount
                    
    anomalies = []
    for cat, curr_spend in curr_cat.items():
        if cat in trail_cat:
            history = trail_cat[cat]
            avg_history = sum(history) / len(history)
            if avg_history > 50 and curr_spend > 1.5 * avg_history:
                anomalies.append({
                    "category": cat,
                    "current_spending": round(curr_spend, 2),
                    "trailing_average": round(avg_history, 2),
                    "increase_factor": round(curr_spend / avg_history, 2)
                })
    return anomalies

def generate_ai_financial_summary(transactions: List[Transaction], profile: UserProfile) -> str:
    """9. AI-generated financial summary using the LLM backend orchestrator client."""
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    savings = total_income - total_expense
    savings_rate = calculate_savings_rate(total_income, total_expense)
    
    # Get top spending categories
    cat_sums = defaultdict(float)
    for t in transactions:
        if t.transaction_type == "expense":
            cat_sums[t.category] += t.amount
    sorted_cats = sorted(cat_sums.items(), key=lambda x: x[1], reverse=True)
    top_cat = sorted_cats[0][0] if sorted_cats else "None"
    
    prompt = f"""
You are the AI Financial Coach. Review the following aggregated metrics and generate 3 concise, highly actionable recommendation bullet points for the user. Do not output conversational filler. Avoid markdown bold headers. Just output 3 bullet points.

MONTHLY SUMMARY:
Total Income analyzed: ₹{total_income}
Total Expense analyzed: ₹{total_expense}
Surplus: ₹{savings}
Savings Rate: {savings_rate}%
Top Category: {top_cat}
"""
    try:
        response = call_llm_with_tools(
            system_prompt="You are a precise financial intelligence assistant, generating dry, brief bullet-point advice.",
            messages=[{"role": "user", "content": prompt}],
            tools=[],
            max_tokens=250
        )
        final_text = "".join(c.text for c in response.content if c.type == "text")
        if final_text.strip():
            return final_text.strip()
    except Exception as e:
        logger.error(f"Error calling LLM for summary: {e}")
        
    # Heuristic fallback structure if AI layer has credential issues (stable fallback)
    fallback = (
        f"- Your current savings rate is {savings_rate}%. Try keeping this above 20% by setting structured auto-invest goals.\n"
        f"- Your primary expense driver this month is {top_cat}. Focus on trimming optional item purchases in this list.\n"
        f"- Ensure you have saved at least 3 months of core runway (₹{round(total_expense * 3)}) in a highly liquid emergency fund."
    )
    return fallback

def generate_financial_insights_payload(transactions: List[Transaction], profile: UserProfile) -> Dict[str, Any]:
    """10. Combine all components into the full insights dashboard payload structure."""
    txs = transactions
    total_income = sum(t.amount for t in txs if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in txs if t.transaction_type == 'expense')
    
    return {
        "monthly_summaries": calculate_monthly_summary(txs),
        "spend_by_category": calculate_category_spending(txs),
        "largest_expenses": get_largest_expenses(txs),
        "recurring_merchants": detect_recurring_merchants(txs),
        "cash_flow_trend": calculate_cash_flow_trend(txs),
        "savings_rate_percent": calculate_savings_rate(total_income, total_expense),
        "monthly_comparison": get_monthly_comparison(txs),
        "spending_anomalies": detect_spending_anomalies(txs),
        "ai_generated_summary": generate_ai_financial_summary(txs, profile)
    }
