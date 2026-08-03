with open("tsc_full.log", "r", encoding="utf-16") as f:
    text = f.read()

for i, line in enumerate(text.split("\n")[:100]):
    if "error TS" in line or "src/" in line:
        print(line.strip())
