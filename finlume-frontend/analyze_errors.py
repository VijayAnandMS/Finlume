import collections

with open("ts_errors_utf8.log", "r", encoding="utf-8") as f:
    text = f.read()

errors = collections.defaultdict(list)
for line in text.split("\n"):
    if "error TS" in line and "(" in line and ")" in line:
        parts = line.split("error TS")
        filename = parts[0].strip()
        issue = parts[1].strip()
        errors[filename].append(issue)

for f, issues in errors.items():
    print(f"--- {f} ---")
    for iss in issues[:5]:
        print(f"  TS{iss}")
    if len(issues) > 5:
        print(f"  ... and {len(issues) - 5} more")

if not errors:
    print("NO TS ERRORS FOUND IN LOG HEADER!")
