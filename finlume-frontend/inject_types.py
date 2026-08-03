import os
import re

files = {
    'v:/Vijay/Projects/Finlume/finlume-frontend/src/pages/ImportWorkflowPage.tsx': {
        'interface': """
export interface ImportRecord {
    id: string;
    raw_data: string;
    is_duplicate: boolean;
    status: string;
    parsed_date: string;
    parsed_merchant: string;
    parsed_amount: number;
    ai_category_suggestion?: string;
}
export interface SessionData {
    id: string;
    status: string;
}
""",
        'replaces': [
            (r'const \[sessionData, setSessionData\] = useState\(null\);', r'const [sessionData, setSessionData] = useState<SessionData | null>(null);'),
            (r'const \[records, setRecords\] = useState\(\[\]\);', r'const [records, setRecords] = useState<ImportRecord[]>([]);')
        ]
    },
    'v:/Vijay/Projects/Finlume/finlume-frontend/src/pages/ImportHistoryPage.tsx': {
         'interface': """
export interface ImportHistory {
    id: string;
    created_at: string;
    filename: string;
    status: string;
    imported_count: number;
    duplicates_found: number;
}
""",
         'replaces': [
             (r'const \[history, setHistory\] = useState\(\[\]\);', r'const [history, setHistory] = useState<ImportHistory[]>([]);')
         ]
    },
    'v:/Vijay/Projects/Finlume/finlume-frontend/src/pages/TransactionsPage.tsx': {
         'interface': """
export interface Transaction {
    id: string;
    transaction_date: string;
    category: string;
    transaction_type: string;
    amount: number;
    merchant?: string;
    description?: string;
}
""",
         'replaces': [
             (r'const \[transactions, setTransactions\] = useState\(\[\]\);', r'const [transactions, setTransactions] = useState<Transaction[]>([]);'),
             (r'tx: any', r'tx: Transaction')
         ]
    }
}

for path, info in files.items():
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # insert interface after imports
    if info['interface'] not in content:
        import_end = content.rfind("import ")
        line_end = content.find("\n", import_end)
        content = content[:line_end+1] + info['interface'] + content[line_end+1:]

    for src, dst in info['replaces']:
        content = re.sub(src, dst, content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Patched {os.path.basename(path)}")

