from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL

# Fallback logic: if it is postgres but not reachable, fallback to SQLite for local development
if db_url.startswith("postgresql"):
    try:
        temp_engine = create_engine(db_url, connect_args={"connect_timeout": 2})
        conn = temp_engine.connect()
        conn.close()
        engine = temp_engine
    except Exception:
        print("WARNING: PostgreSQL not reachable. Falling back to local SQLite (finlume.db).")
        db_url = "sqlite:///./finlume.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url)

print(f"INFO: Database engine active: {db_url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()