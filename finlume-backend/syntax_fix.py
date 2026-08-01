import glob
import os

count = 0
files_mod = []

for filepath in glob.glob("v:/Vijay/Projects/Finlume/finlume-backend/tests/*.py"):
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    
    # Target multiple types of trailing bracing
    content = content.replace('}"}', '"}')
    content = content.replace('""}', '"}')
    content = content.replace('"}"""', '"}')
    
    # Just in case there's another variant:
    content = content.replace("}'}", "'}")
    content = content.replace("]\"}", "]\"}")

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        count += 1
        files_mod.append(os.path.basename(filepath))

print(f"Fixed {count} files: {files_mod}")
