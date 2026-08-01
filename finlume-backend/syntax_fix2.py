import glob
import re

count = 0
files_mod = []

for filepath in glob.glob("v:/Vijay/Projects/Finlume/finlume-backend/tests/*.py"):
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    
    # 1. Clean up the malformed return statement completely!
    # It might look like: return {"Authorization": f"Bearer {token_res...
    # It might span multiple lines if broken.
    
    # Replace any variant of return {"Authorization... ending with random braces/quotes
    content = re.sub(
        r'return\s*\{\"Authorization\":\s*f\"Bearer \{token_res\.json\(\)\[\'access_token\'\]\}[^}]*?\}.*?(?=\n|\Z)',
        r'return {"Authorization": f"Bearer {token_res.json()[\'access_token\']}"}',
        content
    )
    
    # Also handle the cases where I stripped it to `"}`:
    content = re.sub(
        r'return\s*\{\"Authorization\":\s*f\"Bearer \{token_res\.json\(\)\[\'access_token\'\]\}\"',
        r'return {"Authorization": f"Bearer {token_res.json()[\'access_token\']}"}',
        content
    )
    
    # Also if there are multiple closing braces left over
    content = content.replace('}"}"}', '}"}')
    content = content.replace('}"}', '}"}') # Wait, this does nothing
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        count += 1
        files_mod.append(filepath.split('/')[-1])

print(f"Fixed {count} files: {files_mod}")
