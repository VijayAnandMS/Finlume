from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from app.models.models import Transaction
from collections import defaultdict
import datetime as dt

def predict_balances(transactions: List[Transaction], current_balance: float = 0.0) -> Dict[str, Any]:
    """
    Analyzes historical transactions to predict 7-day, 30-day, and EoM balances.
    Returns confidence bounds loosely based on variance.
    """
    
    if not transactions:
        return {
            "7_day": {"forecast_balance": current_balance, "confidence": 0},
            "30_day": {"forecast_balance": current_balance, "confidence": 0},
            "end_of_month": {"forecast_balance": current_balance, "confidence": 0},
            "status": "insufficient_data"
        }

    # Extract historical velocity (net change per day) over the past 90 days.
    # Group by date strings.
    today = datetime.now()
    cutoff_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    
    net_velocity_by_day = defaultdict(float)
    overall_net = 0.0
    day_count = set()
    
    for t in transactions:
        if t.transaction_date >= cutoff_date:
            day_count.add(t.transaction_date)
            # Add or subtract depending on transaction type
            val = t.amount if t.transaction_type == "income" else -t.amount
            net_velocity_by_day[t.transaction_date] += val
            overall_net += val
            
    days_in_range = len(day_count) if len(day_count) > 0 else 1
    # Very simple average historical burn rate/growth rate per active transactional day
    # Fallback to absolute span if active days is small
    span_days = max(1, (today.date() - date.fromisoformat(min(day_count) if day_count else today.strftime("%Y-%m-%d"))).days)
    avg_net_per_day = overall_net / span_days
    
    # Simple probability math: 
    # High standard deviation/inconsistent burn lowers confidence. 
    # Fixed at 75% for basic heuristic. Increase if positive velocity is high.
    base_confidence = 75 if span_days > 15 else 40
    
    def calculate_period(days_ahead: int) -> Dict[str, Any]:
        forecasted_net = avg_net_per_day * days_ahead
        confidence = base_confidence + min(20, int(days_ahead / 30 * 10)) # Very crude confidence modifier
        if days_ahead > 30: confidence -= 10 # Loses confidence further out
        return {
            "forecast_balance": round(current_balance + forecasted_net, 2),
            "confidence": min(98, max(10, confidence))
        }

    # Calculate days left in the month
    next_month = today.month % 12 + 1
    next_month_year = today.year + (today.month // 12)
    first_day_next_month = datetime(next_month_year, next_month, 1)
    days_to_eom = (first_day_next_month - today).days

    return {
        "7_day": calculate_period(7),
        "30_day": calculate_period(30),
        "end_of_month": calculate_period(max(0, days_to_eom)),
        "status": "success",
        "burn_rate_daily": round(-avg_net_per_day, 2) if avg_net_per_day < 0 else 0.0
    }
