import subprocess
import os

with open("pytest_output_clean.txt", "w", encoding="utf-8") as f:
    env = os.environ.copy()
    env["PYTHONPATH"] = "c:\\Vijay\\Projects\\Finlume\\finlume-backend"
    process = subprocess.run(["python", "-m", "pytest", "-vv", "tests/test_phase6.py", "-s"], env=env, capture_output=True, text=True)
    f.write(process.stdout)
    f.write(process.stderr)
    print("Done")
