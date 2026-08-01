with open("FINAL_SUMMARY.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
for line in lines[-20:]:
    print(line.strip())
