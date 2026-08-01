import re

with open('v:/Vijay/Projects/Finlume/finlume-backend/tests/test_audit.py', 'r') as f:
    text = f.read()

# Fix all the broken strings we saw!
# headers={"Authorization": f"Bearer {variable"} or headers={"Authorization": f"Bearer {variable"}, 
# Replace with headers={"Authorization": f"Bearer {variable}"} or headers={"Authorization": f"Bearer {variable}"},

text = re.sub(r'headers=\{\"Authorization\": f\"Bearer \{([a-zA-Z0-9_]+)\"\}?,?', r'headers={"Authorization": f"Bearer {\1}"},', text)

# Remove the trailing comma if it was at the end of the line or before a parenthesis
text = text.replace('},)', '})')
text = text.replace('},\n', '}\n')

with open('v:/Vijay/Projects/Finlume/finlume-backend/tests/test_audit.py', 'w') as f:
    f.write(text)
    
print("Fixed test_audit.py completely!")
