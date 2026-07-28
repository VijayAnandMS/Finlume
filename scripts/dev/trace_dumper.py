import subprocess, os
env = os.environ.copy()
env['PYTHONPATH']='c:\\Vijay\\Projects\\Finlume\\finlume-backend'
output = subprocess.getoutput('python -m pytest --lf')
for i, line in enumerate(output.splitlines()):
    if 'FAILURES' in line or 'ERRORS' in line or 'E   assert' in line or '===' in line or 'tests/test_routes.py' in line:
        print(line)
