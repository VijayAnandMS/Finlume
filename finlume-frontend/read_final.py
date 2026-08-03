import re
with open("tsc_final.log", "r", encoding="utf-16") as f:
    text = f.read()

for line in text.split("\n"):
    if "error TS" in line or "src/" in line:
        print(line.strip())
