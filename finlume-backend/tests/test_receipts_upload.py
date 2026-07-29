import pytest
import io
import uuid
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_receipts.db"
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
    if os.path.exists("test_receipts.db"):
        os.remove("test_receipts.db")

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
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}

def generate_valid_image_bytes():
    img = Image.new('RGB', (1, 1), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_upload_valid_receipt(auth_headers):
    files = {'file': ('test.jpg', generate_valid_image_bytes(), 'image/jpeg')}
    res = client.post("/api/receipts/upload", headers=auth_headers, files=files)
    assert res.status_code == 200
    data = res.json()
    assert "receipt_session_id" in data
    
    # Test GET isolation
    rs_id = data["receipt_session_id"]
    get_res = client.get(f"/api/receipts/{rs_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["filename"] == "test.jpg"
    
    # Test DELETE
    del_res = client.delete(f"/api/receipts/{rs_id}", headers=auth_headers)
    assert del_res.status_code == 204

def test_upload_spoofed_file(auth_headers):
    # Send a text file pretending to be jpg
    files = {'file': ('hacked.jpg', b'this is not an image', 'image/jpeg')}
    res = client.post("/api/receipts/upload", headers=auth_headers, files=files)
    assert res.status_code == 400
    assert "Unsupported MIME type" in res.json()["detail"] or "Failed to decode" in res.json()["detail"]

def test_cross_tenant_isolation(auth_headers):
    # Upload from user 1
    files = {'file': ('test2.jpg', generate_valid_image_bytes(), 'image/jpeg')}
    res1 = client.post("/api/receipts/upload", headers=auth_headers, files=files)
    sid = res1.json()["receipt_session_id"]
    
    # Create user 2
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={
        "full_name": "Test User", "username": unique_user,
        "email": f"{unique_user}@test.com", "password": "password123"
    })
    token_res = client.post("/api/auth/token", data={"username": unique_user, "password": "password123"})
    auth2 = {"Authorization": f"Bearer {token_res.json()['access_token']}"}
    
    # Try fetching with user 2
    res2 = client.get(f"/api/receipts/{sid}", headers=auth2)
    assert res2.status_code == 404
