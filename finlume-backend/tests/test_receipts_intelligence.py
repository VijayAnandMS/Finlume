import pytest
import io
import uuid
import json
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from app.models.models import ReceiptSession, OCRResult, ParsedReceipt, ReceiptIntelligence

from tests.conftest import TestingSessionLocal

@pytest.fixture
def auth_headers(client):
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}

def test_intelligence_mapping(client, auth_headers):
    db = TestingSessionLocal()
    from app.models.models import User
    usr = db.query(User).order_by(User.id.desc()).first()
    
    rs = ReceiptSession(user_id=usr.id, filename="ai_test.jpg", storage_url="ai_test.jpg")
    db.add(rs)
    db.commit()
    
    ocr = OCRResult(receipt_session_id=rs.id, confidence_score=0.9)
    db.add(ocr)
    
    # Store explicit target values testing normalization
    pr = ParsedReceipt(
        receipt_session_id=rs.id, 
        merchant_name="mc donalds", 
        transaction_date="2026-05-15", 
        total=15.50
    )
    db.add(pr)
    db.commit()
    rs_id = rs.id
    db.close()
    
    res = client.post(f"/api/receipts/{rs_id}/intelligence", headers=auth_headers)
    assert res.status_code == 200
    
    data = res.json()
    assert data["predicted_category"] != "Uncategorized"  # Should map to 'Food'
    
    corrections = json.loads(data["field_corrections"])
    assert corrections["merchant_name"] == "McDonald's" # Normalization alias tracking correctly
    
    assert data["overall_confidence"] > 0
    assert data["requires_manual_review"] is False
    
def test_intelligence_failure_safeguards(client, auth_headers):
    # Test attempting intelligence parsing without Prerequisite schemas safely bounds 400 limitations organically
    db = TestingSessionLocal()
    from app.models.models import User
    usr = db.query(User).order_by(User.id.desc()).first()
    
    rs = ReceiptSession(user_id=usr.id, filename="fail_test.jpg", storage_url="fail_test.jpg")
    db.add(rs)
    db.commit()
    rs_id = rs.id
    db.close()
    
    res = client.post(f"/api/receipts/{rs_id}/intelligence", headers=auth_headers)
    assert res.status_code == 400
    assert "Cannot apply Intelligence without Parsed Data" in res.json()["detail"]
