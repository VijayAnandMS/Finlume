with open("ts_errors_utf8.log", "r", encoding="utf-8") as f:
    for line in f:
        if "error TS" in line and "src/" in line:
            print(line.strip())
