import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_history_workflow.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=NullPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    import os
    if os.path.exists("test_history_workflow.db"):
        os.remove("test_history_workflow.db")

@pytest.fixture
def auth_headers():
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}
def test_history_and_audit_lifecycle(auth_headers):
    # 1. Upload Mock File
    csv_content = b"Date,Amount,Merchant\n2026-07-28,10.00,Test\n"
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    upload_res = client.post("/api/import/upload", headers=auth_headers, files=files)
    assert upload_res.status_code == 200
    session_id = upload_res.json()["session_id"]
    
    # 2. Check History list
    history_res = client.get("/api/import/history/list", headers=auth_headers)
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 1
    assert history_res.json()[0]["id"] == session_id
    
    # 3. Check specific History details
    details_res = client.get(f"/api/import/history/{session_id}", headers=auth_headers)
    assert details_res.status_code == 200
    assert details_res.json()["status"] == "MAPPED"
    
    # 4. Check Audits for Upload
    audit_res = client.get(f"/api/import/history/{session_id}/audit", headers=auth_headers)
    assert audit_res.status_code == 200
    actions = [a["action"] for a in audit_res.json()]
    assert "Upload Started" in actions
    assert "Preview Generated" in actions
    
    # 5. Patch to trigger more Audits
    preview_res = client.get(f"/api/import/{session_id}/preview", headers=auth_headers)
    rec_id = preview_res.json()[0]["id"]
    client.patch(f"/api/import/{session_id}/preview", json={
        "updates": {rec_id: {"category": "Entertainment"}}
    }, headers=auth_headers)
    
    # 6. Check Audit for Category Modification
    audit_res = client.get(f"/api/import/history/{session_id}/audit", headers=auth_headers)
    actions = [a["action"] for a in audit_res.json()]
    assert "Category Modified" in actions
    
    # 7. Confirm
    client.post(f"/api/import/{session_id}/confirm", headers=auth_headers)
    
    # 8. Check final status
    details_res = client.get(f"/api/import/history/{session_id}", headers=auth_headers)
    assert details_res.json()["status"] == "COMPLETED"
    assert details_res.json()["imported_count"] == 1
    
    # 9. Final audit check
    audit_res = client.get(f"/api/import/history/{session_id}/audit", headers=auth_headers)
    actions = [a["action"] for a in audit_res.json()]
    assert "Import Confirmed" in actions

def test_unauthorized_history(auth_headers):
    # FAKE id should yield 404 since it's filtered by user implicitly catching auth limits natively
    res = client.get("/api/import/history/FAKE_ID", headers=auth_headers)
    assert res.status_code == 404
