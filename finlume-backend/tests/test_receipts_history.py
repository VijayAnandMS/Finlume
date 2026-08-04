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
from app.models.models import ReceiptSession, ReceiptAudit

from tests.conftest import TestingSessionLocal

@pytest.fixture
def auth_headers(client):
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}

def test_history_audit_retrieval(client, auth_headers):
    # Retrieve user cleanly
    db = TestingSessionLocal()
    from app.models.models import User
    usr = db.query(User).order_by(User.id.desc()).first()
    
    # Generate Mock session history cleanly
    rs = ReceiptSession(user_id=usr.id, filename="hist1.jpg", storage_url="hist1.jpg")
    db.add(rs)
    db.commit()
    
    audit = ReceiptAudit(
        receipt_session_id=rs.id,
        user_id=usr.id,
        processing_status="PREVIEW_READY",
        confidence_summary=0.98,
        validation_warnings=json.dumps([]),
        manual_review_flags=json.dumps(["Date missing"])
    )
    db.add(audit)
    db.commit()
    rs_id = rs.id
    db.close()
    
    # 1. Fetch History Array
    res = client.get("/api/receipts/history", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1
    
    # 2. Fetch Detailed Audit
    res_detail = client.get(f"/api/receipts/history/{rs_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    assert res_detail.json()["processing_status"] == "PREVIEW_READY"
    assert res_detail.json()["confidence_summary"] == 0.98
    
    # 3. Test Isolation / Delete
    res_del = client.delete(f"/api/receipts/history/{rs_id}", headers=auth_headers)
    assert res_del.status_code == 200

    # Ensure Gone
    assert client.get(f"/api/receipts/history/{rs_id}", headers=auth_headers).status_code == 404
