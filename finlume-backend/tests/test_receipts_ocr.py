import pytest
import io
import uuid
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ocr_bounds.db"
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
    if os.path.exists("test_ocr_bounds.db"):
        os.remove("test_ocr_bounds.db")

@pytest.fixture
def auth_headers():
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}"}

def generate_valid_image_bytes():
    img = Image.new('RGB', (1, 1), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_ocr_extraction_integration(auth_headers):
    # 1. Upload mock receipt
    files = {'file': ('test.jpg', generate_valid_image_bytes(), 'image/jpeg')}
    res = client.post("/api/receipts/upload", headers=auth_headers, files=files)
    assert res.status_code == 200
    sid = res.json()["receipt_session_id"]
    
    # 2. Trigger OCR Processing Endpoint
    ocr_res = client.post(f"/api/receipts/{sid}/ocr", headers=auth_headers)
    assert ocr_res.status_code == 200
    
    data = ocr_res.json()
    assert data["confidence_score"] > 0
    assert "detected_fields" in data
    assert "bounding_regions" in data
    assert data["processing_time_ms"] > 0
    
    # Verify exact dummy data mapped successfully safely without external API costs
    import json
    fields = json.loads(data["detected_fields"])
    assert fields["merchant_name"] == "Azure Coffee Co"
    
    # 3. Trigger GET endpoint manually
    get_res = client.get(f"/api/receipts/{sid}/ocr", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["raw_text"] == "MOCK AZURE RECEIPT\\nTOTAL: 154.20"
    
def test_ocr_concurrent_guard(auth_headers):
    # 1. Upload mock receipt
    files = {'file': ('test2.jpg', generate_valid_image_bytes(), 'image/jpeg')}
    res = client.post("/api/receipts/upload", headers=auth_headers, files=files)
    sid = res.json()["receipt_session_id"]
    
    # Intentionally manipulate DB natively mapping concurrency faults
    db = TestingSessionLocal()
    from app.models.models import ReceiptSession
    db_sess = db.query(ReceiptSession).filter(ReceiptSession.id == sid).first()
    db_sess.status = "OCR_PROCESSING"
    db.commit()
    db.close()
    
    ocr_res = client.post(f"/api/receipts/{sid}/ocr", headers=auth_headers)
    assert ocr_res.status_code == 409
    assert ocr_res.json()["detail"] == "Receipt is already processing"
