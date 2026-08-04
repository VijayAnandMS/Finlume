import pytest
import io
import uuid
import json
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import ReceiptSession, OCRResult

from tests.conftest import TestingSessionLocal
from app.models.models import User

@pytest.fixture
def auth_headers(client):
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}

def test_parser_normalizations(client, auth_headers):
    # Setup Internal States structurally directly
    db = TestingSessionLocal()
    usr = db.query(User).order_by(User.id.desc()).first()
    
    rs = ReceiptSession(user_id=usr.id, filename="test.jpg", storage_url="test.jpg")
    db.add(rs)
    db.commit()
    
    # Intentionally messy JSON
    mock_detected = {
        "merchant_name": "  Starbucks ## ",
        "transaction_date": "10/05/2026",
        "subtotal": "$14.50",
        "tax": " 1.20 ",
        "total": "$15.70"
    }
    
    ocr = OCRResult(receipt_session_id=rs.id, detected_fields=json.dumps(mock_detected))
    db.add(ocr)
    db.commit()
    rs_id = rs.id
    db.close()
    
    res = client.post(f"/api/receipts/{rs_id}/parse", headers=auth_headers)
    assert res.status_code == 200
    
    data = res.json()
    assert data["merchant_name"] == "Starbucks" # Whitespace & hash removed
    assert data["transaction_date"] == "2026-10-05" # Dateutil parsing
    assert data["subtotal"] == 14.5 # RegEx extraction
    assert data["tax"] == 1.2
    assert data["total"] == 15.7
    assert data["currency"] == "USD"
    
def test_parser_missing_fields(client, auth_headers):
    db = TestingSessionLocal()
    usr = db.query(User).order_by(User.id.desc()).first()
    
    rs = ReceiptSession(user_id=usr.id, filename="test2.jpg", storage_url="test2.jpg")
    db.add(rs)
    db.commit()
    
    mock_detected = {
        "subtotal": "5.0",
        "tax": "0.5" # No total
    }
    ocr = OCRResult(receipt_session_id=rs.id, detected_fields=json.dumps(mock_detected))
    db.add(ocr)
    db.commit()
    rs_id = rs.id
    db.close()
    
    res = client.post(f"/api/receipts/{rs_id}/parse", headers=auth_headers)
    data = res.json()
    assert data["total"] == 5.5  # Recovered logic heuristic
    assert "Unknown Merchant" in data["merchant_name"]
    assert "Invalid or Missing" in data["warnings"]
