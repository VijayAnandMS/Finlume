import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_import_workflow.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
    import os
    if os.path.exists("test_import_workflow.db"):
        os.remove("test_import_workflow.db")

@pytest.fixture
def auth_headers():
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={
        "full_name": "Test User",
        "username": unique_user,
        "email": f"{unique_user}@test.com",
        "password": "password123"
    })
    token_res = client.post("/api/auth/token", data={
        "username": unique_user,
        "password": "password123"
    })
    token = token_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_workflow_lifecycle(auth_headers):
    # 1. Upload Mock File
    csv_content = b"Date,Amount,Merchant\n2026-07-28,10.00,Test\n2026-07-28,20.00,Test2\n"
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    upload_res = client.post("/api/import/upload", headers=auth_headers, files=files)
    assert upload_res.status_code == 200
    session_id = upload_res.json()["session_id"]
    
    # 2. Get Preview
    preview_res = client.get(f"/api/import/{session_id}/preview", headers=auth_headers)
    assert preview_res.status_code == 200
    records = preview_res.json()
    assert len(records) == 2
    assert records[0]["status"] == "STAGED"
    
    # 3. Patch specific record (Exclude & Category Update)
    rec_id_1 = records[0]["id"]
    rec_id_2 = records[1]["id"]
    
    patch_payload = {
        "updates": {
            rec_id_1: {"status": "DISCARDED", "category": "Food"},
            rec_id_2: {"category": "Entertainment"}
        }
    }
    
    patch_res = client.patch(f"/api/import/{session_id}/preview", json=patch_payload, headers=auth_headers)
    assert patch_res.status_code == 200
    
    # 4. Verify Patch
    preview2 = client.get(f"/api/import/{session_id}/preview", headers=auth_headers).json()
    for r in preview2:
        if r["id"] == rec_id_1:
            assert r["status"] == "DISCARDED"
            assert r["ai_category_suggestion"] == "Food"
        elif r["id"] == rec_id_2:
            assert r["status"] == "STAGED"
            assert r["ai_category_suggestion"] == "Entertainment"
            
    # 5. Confirm Workflow
    confirm_res = client.post(f"/api/import/{session_id}/confirm", headers=auth_headers)
    assert confirm_res.status_code == 200
    assert confirm_res.json()["imported"] == 1 # Only one remained STAGED
    
    # 6. Session should be Completed
    sess_res = client.get(f"/api/import/{session_id}", headers=auth_headers)
    assert sess_res.json()["status"] == "COMPLETED"

def test_unauthorized_access(auth_headers):
    # Trigger 401 Missing Token
    res = client.get("/api/import/FAKE/preview")
    assert res.status_code == 401
