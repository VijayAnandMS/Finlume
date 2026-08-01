import glob
import re

for f in glob.glob("v:/Vijay/Projects/Finlume/finlume-backend/tests/*.py"):
    with open(f, "r") as file:
        content = file.read()
    
    # Fix NullPool
    if "create_engine(" in content and "NullPool" not in content:
        content = content.replace(
            "from sqlalchemy import create_engine", 
            "from sqlalchemy import create_engine\nfrom sqlalchemy.pool import NullPool"
        )
        content = re.sub(
            r'engine = create_engine\(([^)]*)\)',
            r'engine = create_engine(\1, poolclass=NullPool)',
            content
        )
        
    # Fix auth_headers
    if "def auth_headers():" in content:
        auth_block = """def auth_headers():
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})
    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})
    return {"Authorization": f"Bearer {token_res.json()['access_token']}"}"""
        
        content = re.sub(
            r'def auth_headers\(\):.*?return.*?\}',
            auth_block,
            content,
            flags=re.DOTALL
        )
    
    # Fix double fixture
    content = content.replace("@pytest.fixture\n@pytest.fixture", "@pytest.fixture")

    with open(f, "w") as file:
        file.write(content)

print("Applied globally cleanly!")
