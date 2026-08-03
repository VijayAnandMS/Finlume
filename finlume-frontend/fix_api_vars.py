import os, re
for root, dirs, files in os.walk('v:/Vijay/Projects/Finlume/finlume-frontend/src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Change api import to lib if using HTTP methods
            if 'api.get(' in content or 'api.post(' in content or 'api.put(' in content or 'api.delete(' in content:
                content = re.sub(r'import\s+\{\s*api\s*\}\s+from\s+[\'"]../services/api[\'"];', 'import api from "../lib/api";', content)
                content = re.sub(r'import\s+api\s+from\s+[\'"]../services/api[\'"];', 'import api from "../lib/api";', content)
            
            # Remove unused sessionData
            content = content.replace("const [sessionData, setSessionData] = useState<SessionData | null>(null);", "")
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
