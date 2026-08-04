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
from app.models.models import ReceiptSession, OCRResult

from tests.conftest import TestingSessionLocal

@pytest.fixture
def auth_headers(client):
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}

def test_unified_workflow_processing(client, auth_headers):
    # Setup base requirements mocking OCR Provider output securely tracking DB contexts organically
    db = TestingSessionLocal()
    from app.models.models import User
    usr = db.query(User).order_by(User.id.desc()).first()
    
    rs = ReceiptSession(user_id=usr.id, filename="e2e_unified_test.jpg", storage_url="e2e_unified_test.jpg")
    db.add(rs)
    db.commit()
    
    mock_detected = {
        "merchant_name": "  TRGT ## ",
        "transaction_date": "10/05/2026",
        "subtotal": "$100.00",
        "tax": " 5.00 ",
        "total": "$105.00"
    }
    
    ocr = OCRResult(
        receipt_session_id=rs.id, 
        detected_fields=json.dumps(mock_detected),
        confidence_score=0.9
    )
    db.add(ocr)
    db.commit()
    rs_id = rs.id
    db.close()
    
    # 1. Process Unified Receipt End to End
    res = client.post(f"/api/receipts/{rs_id}/process", headers=auth_headers)
    assert res.status_code == 200
    
    data = res.json()
    assert "ocr_raw_data" in data
    
    parsed = json.loads(data["parsed_data"])
    assert parsed["subtotal"] == 100.0 # Validates Parsed Execution smoothly
    
    # Validates Intelligence Module
    ai = json.loads(data["ai_suggestions"])
    assert ai["corrections"]["merchant_name"] == "Target"
    
    assert data["confidence_score"] > 0
    
    # 2. Test Get Preview Logic organically functionally
    get_res = client.get(f"/api/receipts/{rs_id}/preview", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["confidence_score"] == data["confidence_score"]

def test_tenant_isolation(client, auth_headers):
    # Tests users cannot inspect isolated receipts safely smoothly cleanly
    db = TestingSessionLocal()
    from app.models.models import User
    bad_user = User(username="hacker", email="hack@hack.com", hashed_password="pw")
    db.add(bad_user)
    db.commit()
    
    rs = ReceiptSession(user_id=bad_user.id, filename="e2e_hidden.jpg", storage_url="e2e_hidden.jpg")
    db.add(rs)
    db.commit()
    
    ocr = OCRResult(receipt_session_id=rs.id, detected_fields=json.dumps({}))
    db.add(ocr)
    db.commit()
    rs_id = rs.id
    db.close()
    
    res = client.get(f"/api/receipts/{rs_id}/preview", headers=auth_headers)
    assert res.status_code == 404
