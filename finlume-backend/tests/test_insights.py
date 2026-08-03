import pytest
from datetime import datetime, timedelta
from app.models.models import Transaction, UserProfile
from app.services.insights_service import (
    calculate_monthly_summary,
    calculate_category_spending,
    get_largest_expenses,
    detect_recurring_merchants,
    calculate_cash_flow_trend,
    calculate_savings_rate,
    get_monthly_comparison,
    detect_spending_anomalies,
    generate_financial_insights_payload
)

def test_calculate_monthly_summary():
    txs = [
        Transaction(amount=1000.0, transaction_type="income", category="Salary", transaction_date="2026-08-01"),
        Transaction(amount=400.0, transaction_type="expense", category="Food", transaction_date="2026-08-10"),
        Transaction(amount=2000.0, transaction_type="income", category="Salary", transaction_date="2026-07-01"),
        Transaction(amount=800.0, transaction_type="expense", category="Rent", transaction_date="2026-07-05")
    ]
    summary = calculate_monthly_summary(txs)
    # Checks
    assert len(summary) == 2
    assert summary[0]["month"] == "2026-07"
    assert summary[0]["income"] == 2000.0
    assert summary[0]["expense"] == 800.0
    assert summary[0]["net"] == 1200.0

    assert summary[1]["month"] == "2026-08"
    assert summary[1]["income"] == 1000.0
    assert summary[1]["expense"] == 400.0
    assert summary[1]["net"] == 600.0

def test_calculate_category_spending():
    today_str = datetime.now().strftime("%Y-%m-%d")
    txs = [
        Transaction(amount=100.0, transaction_type="expense", category="Food", transaction_date=today_str),
        Transaction(amount=200.0, transaction_type="expense", category="Rent", transaction_date=today_str),
        Transaction(amount=300.0, transaction_type="income", category="Salary", transaction_date=today_str),
    ]
    categories = calculate_category_spending(txs)
    assert len(categories) == 2
    assert categories[0]["category"] == "Rent"
    assert categories[0]["amount"] == 200.0
    assert categories[0]["percentage"] == 66.67
    assert categories[1]["category"] == "Food"
    assert categories[1]["amount"] == 100.0
    assert categories[1]["percentage"] == 33.33

def test_get_largest_expenses():
    today_str = datetime.now().strftime("%Y-%m-%d")
    txs = [
        Transaction(amount=50.0, transaction_type="expense", category="Food", merchant="M1", transaction_date=today_str),
        Transaction(amount=500.0, transaction_type="expense", category="Rent", merchant="M2", transaction_date=today_str),
        Transaction(amount=120.0, transaction_type="expense", category="Utilities", merchant="M3", transaction_date=today_str),
    ]
    largest = get_largest_expenses(txs, limit=2)
    assert len(largest) == 2
    assert largest[0]["merchant"] == "M2"
    assert largest[0]["amount"] == 500.0

def test_detect_recurring_merchants():
    txs = [
        Transaction(amount=15.0, transaction_type="expense", category="Entertainment", merchant="Netflix", transaction_date="2026-06-01"),
        Transaction(amount=15.0, transaction_type="expense", category="Entertainment", merchant="Netflix", transaction_date="2026-07-01"),
        Transaction(amount=15.0, transaction_type="expense", category="Entertainment", merchant="Netflix", transaction_date="2026-08-01"),
    ]
    recurring = detect_recurring_merchants(txs)
    assert len(recurring) == 1
    assert recurring[0]["merchant"] == "Netflix"
    assert recurring[0]["frequency"] == "monthly"
    assert recurring[0]["amount"] == 15.0

def test_calculate_cash_flow_trend():
    today = datetime.now().date()
    txs = [
        Transaction(amount=1000.0, transaction_type="income", category="Salary", transaction_date=(today - timedelta(days=5)).strftime("%Y-%m-%d")),
        Transaction(amount=200.0, transaction_type="expense", category="Food", transaction_date=(today - timedelta(days=2)).strftime("%Y-%m-%d")),
    ]
    trend = calculate_cash_flow_trend(txs)
    assert len(trend) == 30
    # The final balance should be 800
    assert trend[-1]["balance"] == 800.0

def test_calculate_savings_rate_value():
    assert calculate_savings_rate(1000, 200) == 80.0
    assert calculate_savings_rate(0, 200) == 0.0

def test_get_monthly_comparison():
    today = datetime.now()
    curr_month_str = today.strftime("%Y-%m-10")
    
    prev_month = 12 if today.month == 1 else today.month - 1
    prev_year = today.year - 1 if today.month == 1 else today.year
    prev_month_str = f"{prev_year}-{prev_month:02d}-10"
    
    txs = [
        Transaction(amount=150.0, transaction_type="expense", category="Food", transaction_date=curr_month_str),
        Transaction(amount=100.0, transaction_type="expense", category="Food", transaction_date=prev_month_str),
    ]
    comp = get_monthly_comparison(txs)
    assert comp["current_month_expense"] == 150.0
    assert comp["previous_month_expense"] == 100.0
    assert comp["difference_absolute"] == 50.0
    assert comp["difference_percentage"] == 50.0

def test_detect_spending_anomalies():
    today = datetime.now()
    curr_month_str = today.strftime("%Y-%m-10")
    
    # 3 trailing months
    txs = []
    y, m = today.year, today.month
    for _ in range(3):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        txs.append(Transaction(amount=100.0, transaction_type="expense", category="Food", transaction_date=f"{y}-{m:02d}-15"))
        
    # Anomaly: current month spend is 250, trailing average is 100
    txs.append(Transaction(amount=250.0, transaction_type="expense", category="Food", transaction_date=curr_month_str))
    
    anomalies = detect_spending_anomalies(txs)
    assert len(anomalies) == 1
    assert anomalies[0]["category"] == "Food"
    assert anomalies[0]["current_spending"] == 250.0
    assert anomalies[0]["trailing_average"] == 100.0
    assert anomalies[0]["increase_factor"] == 2.5

def test_insights_endpoint(client):
    # Retrieve dependency injection client standard auth headers
    # Authenticate token and test intelligence payload
    headers = {"Authorization": "Bearer test_token"} # Or bypass using a test user
    
    # Create test user
    from app.core.security import create_access_token
    from app.models.models import User
    from tests.conftest import TestingSessionLocal
    
    db = TestingSessionLocal()
    try:
        user = User(username="test_insights", email="test_insights@finlume.com", hashed_password="pw")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        token = create_access_token(subject=user.username)
        auth_headers = {"Authorization": f"Bearer {token}"}
        
        # Add dummy transactions
        tx = Transaction(user_id=user.id, amount=100.0, transaction_type="income", category="Test", transaction_date="2026-08-01", description="Test Description")
        db.add(tx)
        db.commit()
        
        res = client.get("/api/intelligence/insights_engine", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "monthly_summaries" in data
        assert "spend_by_category" in data
        assert "largest_expenses" in data
        assert "recurring_merchants" in data
        assert "cash_flow_trend" in data
        assert "savings_rate_percent" in data
        assert "monthly_comparison" in data
        assert "spending_anomalies" in data
        assert "ai_generated_summary" in data
    finally:
        db.close()

