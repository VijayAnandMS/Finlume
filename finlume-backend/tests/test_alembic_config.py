import os

def test_alembic_env_config():
    # Get path to alembic/env.py relative to the test file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, "alembic", "env.py")
    
    assert os.path.exists(env_path), "alembic/env.py file does not exist"
    
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Assert it does NOT contain a hardcoded postgresql:// connection string
    assert "postgresql://" not in content, "Found hardcoded postgresql:// connection string in alembic/env.py"
    
    # 2. Assert it imports/reads the DB URL from settings.DATABASE_URL
    assert "app.core.config" in content or "app.database" in content, "alembic/env.py must import app configuration"
    assert "settings.DATABASE_URL" in content or "db_url" in content, "alembic/env.py must use settings.DATABASE_URL or db_url to configure migrations"

