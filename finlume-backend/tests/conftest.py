import os
os.environ["DATABASE_URL"] = "sqlite:///./finlume_test.db"
os.environ["TEST_DATABASE_URL"] = "sqlite:///./finlume_test.db"
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.database import Base, get_db
import app.models


import os

# Configure pytest to run against the PostgreSQL test database
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", 
    "postgresql://finlume:finlume@localhost:5432/finlume_test"
)

try:
    engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
    with engine.connect() as conn:
        pass
    print("conftest: Connected to PostgreSQL test DB.")
except Exception:
    TEST_DATABASE_URL = "sqlite:///./finlume_test.db"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=NullPool)
    print("conftest: PostgreSQL unreachable. Falling back to SQLite.")

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create the database schema
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()

