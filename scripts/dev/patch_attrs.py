import os
import glob

files = glob.glob('c:/Vijay/Projects/Finlume/finlume-backend/app/routes/*.py')
for f in files:
    with open(f, 'r') as file:
        content = file.read()
        
    new_content = content.replace('t.type', 't.transaction_type').replace('t.date', 't.transaction_date')
    
    if new_content != content:
        with open(f, 'w') as file:
            file.write(new_content)
        print(f"Patched {f}")
