with open("clean_err.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "test_import_workflow.py" in line:
        print("\n".join(lines[max(0, i-5):i+20]))
        break
