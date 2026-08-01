import subprocess

print("Running FULL PYTEST SUITE...")
full = subprocess.run(['python', '-m', 'pytest', '-vv'], capture_output=True, text=True)

with open('FINAL_SUMMARY.txt', 'w', encoding='utf-8') as f:
    f.write(full.stdout)
    f.write("\n")
    f.write(full.stderr)

print("Done.")
