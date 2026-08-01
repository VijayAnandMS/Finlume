with open('clean_err.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "ERROR tests/test_routes.py" in line or "ERROR tests/test_audit.py" in line:
        print("=========")
        print("".join(lines[i:i+30]))
