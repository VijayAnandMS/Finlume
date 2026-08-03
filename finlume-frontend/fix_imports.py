import glob
import re

for file in glob.glob('v:/Vijay/Projects/Finlume/finlume-frontend/src/**/*.tsx', recursive=True) + glob.glob('v:/Vijay/Projects/Finlume/finlume-frontend/src/**/*.ts', recursive=True):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(r'import api from [\'"]../services/api[\'"];', 'import { api } from "../services/api";', content)

    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
            print(f"Fixed api import in {file}")

