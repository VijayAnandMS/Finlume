import subprocess

result = subprocess.run(['python', '-m', 'pytest', '--collect-only'], capture_output=True, text=True)

with open('clean_err.txt', 'w', encoding='utf-8') as f:
    f.write(result.stdout)
    f.write(result.stderr)
    
print("Diagnostic traced successfully.")
