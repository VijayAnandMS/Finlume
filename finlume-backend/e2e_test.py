import os
import sys
import uuid
import json
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from app.main import app
from app.database import SessionLocal
from app.models.models import User

client = TestClient(app)

def test_full_system():
    print("--- STARTING E2E VALIDATION ---")
    
    # 1. Registration
    username = f"e2e_user_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    print(f"Registering {username}...")
    res = client.post("/api/auth/register", json={
        "full_name": "E2E Tester",
        "username": username,
        "email": email,
        "password": "SecurePassword123!"
    })
    
    # Check registration
    if res.status_code not in (200, 201, 202):
        print(f"Registration failed: {res.text}")
        return False
        
    print("Registration OK.")
    
    # Auto-verify email
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_email_verified = True
        user.is_active = True
        db.commit()
    db.close()
    print("User verified.")
    
    # 2. Login
    print("Logging in...")
    res = client.post("/api/auth/login", data={
        "username": username,
        "password": "SecurePassword123!"
    })
    
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return False
        
    token = res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK. JWT Acquired.")
    
    # 3. Create 30 Transactions
    print("Generating 10 Income and 20 Expense Transactions...")
    
    incomes = [
        {"transaction_date": "2026-07-01", "category": "Salary", "transaction_type": "income", "amount": 5000.0, "merchant": "TechCorp"},
        {"transaction_date": "2026-07-02", "category": "Freelance", "transaction_type": "income", "amount": 1000.0, "merchant": "Upwork"},
        {"transaction_date": "2026-07-03", "category": "Investments", "transaction_type": "income", "amount": 250.0, "merchant": "Vanguard"},
        {"transaction_date": "2026-07-04", "category": "Gift", "transaction_type": "income", "amount": 100.0, "merchant": "Family"},
        {"transaction_date": "2026-07-05", "category": "Refund", "transaction_type": "income", "amount": 50.0, "merchant": "Amazon"},
        {"transaction_date": "2026-07-06", "category": "Bonus", "transaction_type": "income", "amount": 500.0, "merchant": "TechCorp"},
        {"transaction_date": "2026-07-07", "category": "Side Hustle", "transaction_type": "income", "amount": 200.0, "merchant": "Etsy"},
        {"transaction_date": "2026-07-08", "category": "Dividend", "transaction_type": "income", "amount": 75.0, "merchant": "Fidelity"},
        {"transaction_date": "2026-07-09", "category": "Salary", "transaction_type": "income", "amount": 5000.0, "merchant": "TechCorp"},
        {"transaction_date": "2026-07-10", "category": "Rebate", "transaction_type": "income", "amount": 25.0, "merchant": "Costco"},
    ]
    
    expenses = [
        {"transaction_date": f"2026-07-{i+1:02d}", "category": "Food", "transaction_type": "expense", "amount": 20.0 + i, "merchant": "Restaurant"} for i in range(10)
    ] + [
        {"transaction_date": f"2026-07-{i+11:02d}", "category": "Rent", "transaction_type": "expense", "amount": 1000.0, "merchant": "Landlord"} for i in range(5)
    ] + [
        {"transaction_date": f"2026-07-{i+16:02d}", "category": "Utilities", "transaction_type": "expense", "amount": 100.0, "merchant": "PowerCo"} for i in range(5)
    ]
    
    transactions_created = []
    
    for tx in incomes + expenses:
        res = client.post("/api/transactions/", json=tx, headers=headers)
        if res.status_code not in (200, 201):
            print(f"Failed to create transaction: {tx} | Error: {res.text}")
            return False
        transactions_created.append(res.json())
        
    print(f"Created {len(transactions_created)} transactions successfully.")
    
    # 4. Filter / Pagination Check
    print("Testing Filters and Pagination...")
    res = client.get("/api/transactions/?type=expense&limit=5", headers=headers)
    if res.status_code != 200 or len(res.json()) != 5:
        print("Filtering/Pagination Failed.")
        return False
    print("Pagination OK.")
    
    # 5. Dashboard Summary
    print("Testing Dashboard Sync...")
    res = client.get("/api/summary/", headers=headers)
    if res.status_code != 200:
        print("Summary GET failed.")
        return False
        
    summary_data = res.json()
    if summary_data.get("total_income", 0) <= 0 or summary_data.get("total_expense", 0) <= 0:
        print("Summary values are flat! Integration failed.")
        return False
        
    print(f"Dashboard Sync OK. Income: {summary_data['total_income']}, Expense: {summary_data['total_expense']}")
    
    # 6. AI Agent Validation
    print("Testing AI Agent logic...")
    res = client.post("/api/chat/", json={"message": "What is my monthly savings?"}, headers=headers)
    if res.status_code != 200:
        print(f"AI Call failed: {res.text}")
    else:
        print(f"AI Response Captured: {res.json().get('reply')[:100]}...")
        
    print("--- E2E VALIDATION PASS ---")
    return True

if __name__ == "__main__":
    if test_full_system():
        print("SUCCESS")
        sys.exit(0)
    else:
        print("FAILED")
        sys.exit(1)
