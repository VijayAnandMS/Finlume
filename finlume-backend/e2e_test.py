import os
import random
from fastapi.testclient import TestClient
from app.main import app

# Ensure .env variables are loaded by dotenv (which app.main does)
client = TestClient(app)

# 1. Create a unique test user
username = f"liveuser_{random.randint(1000, 9999)}"
password = "testpassword123"

print("Registering user:", username)
res = client.post("/api/auth/register", json={"username": username, "password": password})
if res.status_code != 200:
    print("Registration error:", res.json())

# 2. Login
res = client.post("/api/auth/login", json={"username": username, "password": password})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Successfully logged in.")

# 3. Add transactions
txs = [
    {"date": "2026-07-09", "category": "Salary", "type": "income", "amount": 60000.0, "description": "Paycheck"},
    {"date": "2026-07-10", "category": "Food", "type": "expense", "amount": 12000.0, "description": "Groceries & Eating Out"},
    {"date": "2026-07-11", "category": "Rent", "type": "expense", "amount": 20000.0, "description": "Monthly rent"},
    {"date": "2026-07-12", "category": "Entertainment", "type": "expense", "amount": 5000.0, "description": "Movies and subscriptions"}
]

print("Adding transactions...")
for tx in txs:
    r = client.post("/api/transactions/", json=tx, headers=headers)
    if r.status_code != 200:
        print("Error adding tx:", r.json())

import json

print("Sending chat request to Anthropic API...")
chat_res = client.post("/api/chat/", json={"message": "how much did I spend and can you suggest a budget"}, headers=headers)
with open("e2e_output.json", "w", encoding="utf-8") as f:
    json.dump(chat_res.json(), f, indent=4)
print("Response saved to e2e_output.json")
