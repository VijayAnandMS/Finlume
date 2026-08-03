with open("ts_errors.log", "r", encoding="utf-8") as f:
    lines = f.readlines()
for line in lines:
    if "error TS" in line:
        print(line.strip())
