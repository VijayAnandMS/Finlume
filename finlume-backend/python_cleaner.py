import glob
import os

count = 0
files_mod = []

for filepath in glob.glob("v:/Vijay/Projects/Finlume/finlume-backend/tests/*.py"):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    in_auth = False
    modified = False
    
    for line in lines:
        if line.startswith("def auth_headers():"):
            in_auth = True
            new_lines.append(line)
            new_lines.append('    import uuid\n')
            new_lines.append('    unique_user = f"user_{uuid.uuid4().hex[:8]}"\n')
            new_lines.append('    client.post("/api/auth/register", json={"full_name": "Test", "username": unique_user, "email": f"test_{unique_user}@test.com", "password": "password123"})\n')
            new_lines.append('    token_res = client.post("/api/auth/login", data={"username": unique_user, "password": "password123"})\n')
            new_lines.append('    return {"Authorization": f"Bearer {token_res.json()[\'access_token\']}"}\n')
            modified = True
            continue
            
        if in_auth:
            # We skip lines until we hit the next function or fixture
            if line.startswith("def ") or line.startswith("@") or line.startswith("class ") or line.startswith("# "):
                in_auth = False
                new_lines.append(line)
            continue
        else:
            new_lines.append(line)
            
    if modified:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        count += 1
        files_mod.append(os.path.basename(filepath))

print(f"\n===== SYNTAX FIXER EXECUTION =====")
print(f"Fixed {count} files: {', '.join(files_mod)}")
print(f"==================================\n")
