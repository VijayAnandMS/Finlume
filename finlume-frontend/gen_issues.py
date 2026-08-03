import re

with open("tsc_final.log", "r", encoding="utf-16") as f:
    text = f.read()

issues = []
current_file = None
for line in text.split("\n"):
    m_file = re.search(r'^(src/[^\(]+)\(', line)
    if m_file:
        current_file = m_file.group(1)
    
    m_error = re.search(r"TS\d+: (.*)", line)
    if m_error and current_file:
        issues.append(f"{current_file}: {m_error.group(0)}")

with open("issues.txt", "w", encoding="utf-8") as f:
    for iss in set(issues):
        f.write(iss + "\n")
