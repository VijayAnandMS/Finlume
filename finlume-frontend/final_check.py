import subprocess
print("Compiling...")
res = subprocess.run(['npx', 'tsc', '-b', '--force'], capture_output=True, text=True, shell=True)
output = res.stdout + "\n" + res.stderr
lines = output.split('\n')
for line in lines[-20:]:
    print(line)
