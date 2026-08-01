with open('clean_err.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Error" in line or "Exception" in line or "E   " in line or "SyntaxError" in line:
        start = max(0, i - 2)
        end = min(len(lines), i + 3)
        print("=========")
        print("".join(lines[start:end]))
        
# Check if there's any file listed in collection errors
for line in lines:
    if "tests/" in line or "tests\\" in line:
        if "error" in line.lower() or "failed" in line.lower():
            print(line.strip())
