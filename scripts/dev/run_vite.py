import subprocess

with open("err2.txt", "w", encoding="utf-8") as f:
    subprocess.run("npx vite build", shell=True, stdout=f, stderr=subprocess.STDOUT, text=True)
