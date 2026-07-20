import json
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

results = {}

username = f"user_{int(time.time())}"
res_reg = client.post("/api/auth/register", json={"username": username, "password": "password"})
results["register_status"] = res_reg.status_code

res_login = client.post("/api/auth/login", json={"username": username, "password": "password"})
token = res_login.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# 1. POST
payload = {
    "name": "Buy a car",
    "target_amount": 500000,
    "current_amount": 10000,
    "deadline": "2028-01-01",
    "status": "active",
    "monthly_target": 20000,
    "priority": "high"
}
res = client.post("/api/goals/", json=payload, headers=headers)
results["post_status"] = res.status_code
results["post_res"] = res.json()
goal_id = res.json().get("id")

# 2. GET
res2 = client.get("/api/goals/", headers=headers)
results["get_status"] = res2.status_code
results["get_res"] = res2.json()

# 3. PUT
if goal_id:
    put_payload = {
        "name": "Buy a car (Updated)",
        "target_amount": 500000,
        "current_amount": 30000,
        "deadline": "2028-01-01",
        "status": "active",
        "monthly_target": 25000,
        "priority": "high"
    }
    res3 = client.put(f"/api/goals/{goal_id}", json=put_payload, headers=headers)
    results["put_status"] = res3.status_code
    results["put_res"] = res3.json()

# 4. AI Planner
ai_payload = {"message": "Plan a goal to Buy a car for 500000"}
res4 = client.post("/api/agents/goal-planner", json=ai_payload, headers=headers)
results["ai_status"] = res4.status_code
results["ai_res"] = res4.json()

# 5. DELETE
if goal_id:
    res5 = client.delete(f"/api/goals/{goal_id}", headers=headers)
    results["delete_status"] = res5.status_code

with open("verify_out.json", "w") as f:
    json.dump(results, f, indent=2)
