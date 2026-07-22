import pytest
from app.core.security import verify_token
from app.core.config import settings

def test_signup_success(client):
    res = client.post("/api/auth/register", json={"username": "newuser", "password": "securepassword", "email": "newuser@test.com", "full_name": "Test User"})
    assert res.status_code == 201
    assert res.json()["username"] == "newuser"

def test_signup_duplicate(client):
    client.post("/api/auth/register", json={"username": "duplicateuser", "password": "securepassword", "email": "duplicateuser@test.com", "full_name": "Test User"})
    res = client.post("/api/auth/register", json={"username": "duplicateuser", "password": "newpassword", "email": "duplicateuser@test.com", "full_name": "Test User"})
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()

def test_login_success(client):
    client.post("/api/auth/register", json={"username": "loginuser", "password": "loginpassword", "email": "loginuser@test.com", "full_name": "Test User"})
    res = client.post("/api/auth/login", data={"username": "loginuser", "password": "loginpassword", "email": "loginuser@test.com", "full_name": "Test User"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expiration" in data
    
    # Verify JWT payload
    username = verify_token(data["access_token"])
    assert username == "loginuser"

def test_login_invalid_password(client):
    client.post("/api/auth/register", json={"username": "badpassuser", "password": "correctpassword", "email": "badpassuser@test.com", "full_name": "Test User"})
    res = client.post("/api/auth/login", data={"username": "badpassuser", "password": "wrongpassword", "email": "badpassuser@test.com", "full_name": "Test User"})
    assert res.status_code == 401
    assert "invalid credentials" in res.json()["detail"].lower()

def test_login_unknown_user(client):
    res = client.post("/api/auth/login", data={"username": "unknownuser", "password": "somepassword", "email": "unknownuser@test.com", "full_name": "Test User"})
    assert res.status_code == 401
    assert "invalid credentials" in res.json()["detail"].lower()

def test_protected_endpoint_access(client):
    # Register and login to get token
    client.post("/api/auth/register", json={"username": "protecteduser", "password": "protectedpassword", "email": "protecteduser@test.com", "full_name": "Test User"})
    login_res = client.post("/api/auth/login", data={"username": "protecteduser", "password": "protectedpassword", "email": "protecteduser@test.com", "full_name": "Test User"})
    token = login_res.json()["access_token"]
    
    # Access protected route without token
    res_no_token = client.get("/api/auth/me")
    assert res_no_token.status_code == 401
    
    # Access protected route with valid token
    headers = {"Authorization": f"Bearer {token}"}
    res_with_token = client.get("/api/auth/me", headers=headers)
    assert res_with_token.status_code == 200
    assert res_with_token.json()["username"] == "protecteduser"
