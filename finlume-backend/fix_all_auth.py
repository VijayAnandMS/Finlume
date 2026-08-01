import glob
import re
import os

count = 0
files_mod = []

for filepath in glob.glob("v:/Vijay/Projects/Finlume/finlume-backend/tests/*.py"):
    with open(filepath, 'r') as f:
        text = f.read()

    original = text
    
    # Safely repair headers={"Authorization": f"Bearer {variable"} or {variable"}, 
    text = re.sub(r'headers=\{\"Authorization\": f\"Bearer \{([a-zA-Z0-9_]+)\"\}?,?', r'headers={"Authorization": f"Bearer {\1}"},', text)

    # Some trailing cleanups just in case:
    text = text.replace('},)', '})')
    text = text.replace('},\n', '}\n')
    text = text.replace('}, \n', '}\n')

    if text != original:
        with open(filepath, 'w') as f:
            f.write(text)
        count += 1
        files_mod.append(os.path.basename(filepath))

print(f"Fixed {count} files: {', '.join(files_mod)}")
