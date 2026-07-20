import pytest
from app.models.models import Goal

@pytest.fixture(scope="module")
def token_headers(client):
    client.post("/api/auth/register", json={"username": "goaltester", "password": "password"})
    res = client.post("/api/auth/login", data={"username": "goaltester", "password": "password"})
    token = res.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}


def test_create_goal(client, token_headers):
    response = client.post("/api/goals/", json={
        "name": "Emergency Fund",
        "target_amount": 5000,
        "current_amount": 100,
        "deadline": "2026-12-31",
        "monthly_target": 500,
        "priority": "high"
    }, headers=token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Emergency Fund"
    assert data["target_amount"] == 5000
    assert data["monthly_target"] == 500
    assert "id" in data

def test_get_goals(client, token_headers):
    response = client.get("/api/goals/", headers=token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_goal(client, token_headers):
    # First create
    post_res = client.post("/api/goals/", json={
        "name": "Vacation",
        "target_amount": 2000,
        "current_amount": 0
    }, headers=token_headers)
    goal_id = post_res.json()["id"]

    # Then update
    put_res = client.put(f"/api/goals/{goal_id}", json={
        "name": "Vacation Fund",
        "target_amount": 2500,
        "current_amount": 500
    }, headers=token_headers)
    
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["name"] == "Vacation Fund"
    assert data["current_amount"] == 500

def test_delete_goal(client, token_headers):
    # First create
    post_res = client.post("/api/goals/", json={
        "name": "Test Delete",
        "target_amount": 1000,
        "current_amount": 0
    }, headers=token_headers)
    goal_id = post_res.json()["id"]
    
    # Then delete
    del_res = client.delete(f"/api/goals/{goal_id}", headers=token_headers)
    assert del_res.status_code == 204
    
    # Verify deleted
    get_res = client.get("/api/goals/", headers=token_headers)
    goals = get_res.json()
    assert not any(g["id"] == goal_id for g in goals)
