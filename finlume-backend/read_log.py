with open("test_final_qa.txt", "rb") as f:
    text = f.read().decode("utf-16le", errors="ignore")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "FAILURES" in line or "= FAILURES =" in line or "FAILED tests" in line:
            print("\n".join(lines[max(0, i-5):i+50]))
            break
