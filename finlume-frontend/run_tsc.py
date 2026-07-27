import subprocess

with open("err.txt", "w", encoding="utf-8") as f:
    subprocess.run("npx tsc", shell=True, stdout=f, stderr=subprocess.STDOUT, text=True)
