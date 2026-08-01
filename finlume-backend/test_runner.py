import subprocess
import os

print("Running Pytest Complete Verification...")
result = subprocess.run(['python', '-m', 'pytest', '-vv'], capture_output=True, text=True)

lines = result.stdout.split('\n')

for i, line in enumerate(lines):
    if 'failed' in line and 'passed' in line and '=' in line:
        summary_idx = i
        break
else:
    summary_idx = len(lines) - 15

print("\n--- FINAL PYTEST SUMMARY ---")
print('\n'.join(lines[-20:]))
print("----------------------------\n")

if result.returncode == 0:
    print("ALL TESTS PASSED SUCCESSFULLY! (0 failed, 0 errors)")
else:
    print(f"PYTEST RETURNED CODE: {result.returncode}")
