from app.services.health_engine import calculate_savings_rate, evaluate_savings_rate, calculate_financial_health
from app.services.forecast_engine import predict_balances
from app.services.risk_engine import analyze_risk
from app.services.recommendation_engine import generate_recommendations
from app.models.models import Transaction, Goal, UserProfile

def build_mock_txs():
    tx1 = Transaction(amount=5000, transaction_type="income", category="Salary", transaction_date="2026-06-01")
    tx2 = Transaction(amount=2000, transaction_type="expense", category="Rent", transaction_date="2026-06-05")
    tx3 = Transaction(amount=500, transaction_type="expense", category="Food", merchant="Whole Foods", transaction_date="2026-06-10")
    tx4 = Transaction(amount=500, transaction_type="expense", category="Food", merchant="Whole Foods", transaction_date="2026-06-12")
    return [tx1, tx2, tx3, tx4]

def build_mock_profile():
    return UserProfile(emergency_fund=12000)

def test_health_scoring_bounds():
    assert calculate_savings_rate(5000, 2000) == 60.0 # 3000 savings = 60%
    assert calculate_savings_rate(1000, 2000) == 0.0  # Cap negative savings
    assert evaluate_savings_rate(25.0) == 100
    assert evaluate_savings_rate(5.0) == 50
    
def test_full_health_integration():
    txs = build_mock_txs()
    prof = build_mock_profile()
    res = calculate_financial_health(txs, [], prof)
    assert 0 <= res["score"] <= 100
    assert res["metrics"]["savings_rate_percentage"] == 40.0 # 5000 inc, 3000 exp
    
def test_forecast_engine():
    txs = build_mock_txs()
    # 5000 income, 3000 expense, net is positive.
    res = predict_balances(txs, current_balance=2000.0)
    assert res["status"] == "success"
    assert res["7_day"]["forecast_balance"] >= 2000.0

def test_risk_engine():
    txs = build_mock_txs()
    prof = build_mock_profile()
    res = analyze_risk(txs, prof)
    # Savings are high and emergency buffer is 12000 vs 3000 monthly exp
    # Structural risk should be VERY LOW.
    assert res["risk_level"] == "LOW"
    assert res["risk_points"] < 30

def test_risk_negative_cash_flow():
    tx_bad = Transaction(amount=10000, transaction_type="expense", category="Luxury", transaction_date="2026-06-10")
    txs = build_mock_txs() + [tx_bad]
    prof = UserProfile(emergency_fund=100)
    res = analyze_risk(txs, prof)
    assert res["risk_level"] == "HIGH"
    
def test_recommendation_engine():
    txs = build_mock_txs()
    prof = build_mock_profile()
    recs = generate_recommendations(txs, prof)
    
    # Check duplicate detection for Whole Foods
    duplicate_rec = any("duplicate" in r.lower() or "recurring" in r.lower() for r in recs)
    assert duplicate_rec is True
