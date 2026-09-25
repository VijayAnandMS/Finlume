from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL

if not db_url:
    if settings.ENVIRONMENT.lower() in ("production", "render", "staging"):
        raise RuntimeError(
            "CRITICAL: DATABASE_URL environment variable is not set. "
            "It is required in production/staging environments. "
            "Set DATABASE_URL to your Supabase/PostgreSQL connection string."
        )
    # Local development fallback to SQLite
    db_url = "sqlite:///./finlume_test.db"
    print("INFO: DATABASE_URL not set — using local SQLite for development.")

# Handle Supabase/Render legacy postgres:// scheme
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Configure engine with appropriate args per dialect
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(db_url, connect_args=connect_args)

# Log dialect only, never the full URL (contains credentials)
print(f"INFO: Database engine active — dialect: {engine.dialect.name}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()