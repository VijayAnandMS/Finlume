with open("ts.log", "r", encoding="utf-16") as f:
    text = f.read()

count = 0
for line in text.split("\n"):
    if "error TS" in line or "src/" in line:
        print(line.strip())
        count += 1
        if count >= 30:
            break
