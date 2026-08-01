import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
import uuid

# Fast testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_import_api.db"
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
    if os.path.exists("test_import_api.db"):
        os.remove("test_import_api.db")

@pytest.fixture
def auth_headers():
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}
def test_missing_jwt():
    res = client.post("/api/import/upload")
    assert res.status_code == 401

def test_upload_invalid_extension(auth_headers):
    files = {'file': ('test.txt', b'some random text', 'text/plain')}
    res = client.post("/api/import/upload", headers=auth_headers, files=files)
    assert res.status_code == 415

def test_valid_csv_upload(auth_headers):
    # Testing Valid CSV upload seamlessly
    csv_content = b"Date,Amount,Merchant\n2026-07-28,10.00,Test\n"
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    res = client.post("/api/import/upload", headers=auth_headers, files=files)
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert data["total_parsed"] == 1
    
    session_id = data["session_id"]
    
    # Test Preview GET Request
    preview_res = client.get(f"/api/import/{session_id}/preview", headers=auth_headers)
    assert preview_res.status_code == 200
    assert len(preview_res.json()) == 1
    
    # Test Session Get Request
    sess_res = client.get(f"/api/import/{session_id}", headers=auth_headers)
    assert sess_res.status_code == 200
    assert sess_res.json()["status"] == "MAPPED"
    
    # Test Delete Request
    del_res = client.delete(f"/api/import/{session_id}", headers=auth_headers)
    assert del_res.status_code == 204
    
    # Verify cleanup natively
    assert client.get(f"/api/import/{session_id}", headers=auth_headers).status_code == 404

def test_malformed_csv_upload(auth_headers):
    files = {'file': ('bad.csv', b'Random,Data\n1,2', 'text/csv')}
    res = client.post("/api/import/upload", headers=auth_headers, files=files)
    assert res.status_code == 422 # Missing columns catch

def test_large_file_rejection(auth_headers, monkeypatch):
    from app.services.imports import validator
    def mock_getsize(*args):
        return 15 * 1024 * 1024 # Fake 15MB
        
    monkeypatch.setattr("os.path.getsize", mock_getsize)
    files = {'file': ('big.csv', b'a', 'text/csv')}
    res = client.post("/api/import/upload", headers=auth_headers, files=files)
    assert res.status_code == 415
    assert "exceeds" in res.json()['detail']
