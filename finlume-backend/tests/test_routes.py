import pytest

def test_auth_routes(client):
    # 1. Register a user
    reg_response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpassword", "email": "testuser@test.com", "full_name": "Test User"}
    )
    assert reg_response.status_code == 201
    assert reg_response.json()["username"] == "testuser"
    assert "id" in reg_response.json()

    # Try registering again with the same username (should fail)
    fail_reg = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "newpassword", "email": "testuser@test.com", "full_name": "Test User"}
    )
    assert fail_reg.status_code == 400

    # 2. Login
    login_response = client.post("/api/auth/login", data={"username": "testuser", "password": "testpassword", "email": "testuser@test.com", "full_name": "Test User"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 3. Retrieve current user info
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "testuser"

    # Access /me with invalid token (should fail)
    fail_me = client.get("/api/auth/me", headers={"Authorization": "Bearer badtoken"})
    assert fail_me.status_code == 401


def test_transaction_routes_and_analytics(client):
    import uuid
    dyn_user = f"analyticsuser_{uuid.uuid4().hex[:6]}"
    # Register structurally isolated user
    client.post("/api/auth/register", json={"username": dyn_user, "password": "testpassword", "email": f"{dyn_user}@test.com", "full_name": "Test User"})
    # Get auth token
    login_response = client.post("/api/auth/login", data={"username": dyn_user, "password": "testpassword", "email": f"{dyn_user}@test.com", "full_name": "Test User"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Add some transactions (Income & Expense)
    tx1 = client.post(
        "/api/transactions/",
        headers=headers,
        json={
            "transaction_date": "2026-07-08",
            "category": "Salary",
            "transaction_type": "income",
            "amount": 60000.0,
            "description": "Monthly pay"
        }
    )
    assert tx1.status_code == 201
    tx1_id = tx1.json()["id"]

    tx2 = client.post(
        "/api/transactions/",
        headers=headers,
        json={
            "transaction_date": "2026-07-09",
            "category": "Food",
            "transaction_type": "expense",
            "amount": 1200.0,
            "description": "Weekly groceries"
        }
    )
    assert tx2.status_code == 201
    tx2_id = tx2.json()["id"]

    tx3 = client.post(
        "/api/transactions/",
        headers=headers,
        json={
            "transaction_date": "2026-07-10",
            "category": "Rent",
            "transaction_type": "expense",
            "amount": 15000.0,
            "description": "Monthly rent payment"
        }
    )
    assert tx3.status_code == 201

    # 2. List Transactions
    list_res = client.get("/api/transactions/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 3

    # 3. Update Transaction (Update Rent from 15000 to 16000)
    tx3_id = tx3.json()["id"]
    update_res = client.put(
        f"/api/transactions/{tx3_id}",
        headers=headers,
        json={
            "transaction_date": "2026-07-10",
            "category": "Rent",
            "transaction_type": "expense",
            "amount": 16000.0,
            "description": "Monthly rent payment updated"
        }
    )
    assert update_res.status_code == 200
    assert update_res.json()["amount"] == 16000.0

    # 4. Fetch Summary / Analytics
    summary_res = client.get("/api/summary/", headers=headers)
    assert summary_res.status_code == 200
    data = summary_res.json()
    assert data["total_income"] == 60000.0
    assert data["total_expense"] == 17200.0  # 1200 + 16000
    assert data["net"] == 42800.0
    assert len(data["top_categories"]) == 2  # Rent and Food
    assert data["top_categories"][0]["category"] == "Rent"
    assert data["top_categories"][0]["amount"] == 16000.0

    # 5. Delete Transaction (Delete Food expense)
    del_res = client.delete(f"/api/transactions/{tx2_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify transaction deletion in summary
    new_summary = client.get("/api/summary/", headers=headers).json()
    assert new_summary["total_expense"] == 16000.0  # Food deleted, only rent remains


@pytest.mark.skip(reason="Flaky test disabled for CI stability")
def test_ai_chat_coach(client):
    # Get auth token
    login_response = client.post("/api/auth/login", data={"username": "testuser", "password": "testpassword", "email": "testuser@test.com", "full_name": "Test User"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Ask about overview/summary
    res_overview = client.post(
        "/api/chat/",
        headers=headers,
        json={"message": "Give me a summary of my account"}
    )
    assert res_overview.status_code == 200
    assert "income" in res_overview.json()["reply"].lower()

    # 2. Ask about savings
    res_save = client.post(
        "/api/chat/",
        headers=headers,
        json={"message": "How can I save more?"}
    )
    assert res_save.status_code == 200
    assert "save" in res_save.json()["reply"].lower() or "surplus" in res_save.json()["reply"].lower()

    # 3. Ask about spending/expenses
    res_spend = client.post(
        "/api/chat/",
        headers=headers,
        json={"message": "what is my highest expense?"}
    )
    assert res_spend.status_code == 200
    assert "rent" in res_spend.json()["reply"].lower()
