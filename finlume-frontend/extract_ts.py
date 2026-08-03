with open("ts_errors.log", "r", encoding="utf-8") as f:
    for line in f:
        if "TS2" in line or "TS1" in line or "TS7" in line:
            print(line.strip())
