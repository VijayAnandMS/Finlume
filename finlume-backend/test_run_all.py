import subprocess

print("==================================================")
print("1. COMPILATION VERIFICATION")
print("==================================================")
comp = subprocess.run(['python', '-m', 'compileall', 'tests'], capture_output=True, text=True)
if comp.returncode == 0:
    print("SUCCESS: 0 syntax errors across all test files.")
else:
    print("FAILED: Syntax errors exist.")
    print(comp.stderr)

print("\n==================================================")
print("2. PYTEST COLLECTION SUMMARY")
print("==================================================")
col = subprocess.run(['python', '-m', 'pytest', '--collect-only'], capture_output=True, text=True)
for line in col.stdout.split('\n'):
    if "collected" in line or "===" in line or "Error" in line:
        print(line)

print("\n==================================================")
print("3. PYTEST FULL EXECUTION")
print("==================================================")
full = subprocess.run(['python', '-m', 'pytest', '-vv'], capture_output=True, text=True)
for line in (full.stdout + "\n" + full.stderr).split('\n')[-20:]:
    print(line)
