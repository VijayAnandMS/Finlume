import re

with open("tsc_final.log", "r", encoding="utf-16") as f:
    text = f.read()

issues = []
current_file = None
for line in text.split("\n"):
    m_file = re.search(r'^(src/[^\(]+)\(', line)
    if m_file:
        current_file = m_file.group(1)
    
    m_error = re.search(r"TS6133: '([^']+)' is declared but its value is never read", line)
    if m_error and current_file:
        issues.append(f"{current_file}: {m_error.group(1)}")

    m_error2 = re.search(r"TS2[0-9]+: (.*)", line)
    if m_error2 and 'TS6133' not in line and current_file:
        issues.append(f"{current_file}: {m_error2.group(0)}")

for iss in set(issues):
    print(iss)

