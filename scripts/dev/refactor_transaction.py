import os
import re

for root, _, files in os.walk('c:/Vijay/Projects/Finlume/finlume-backend/app/routes'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            # Careful regex for kwarg assignments
            content = re.sub(r'\btype\s*=\s*', 'transaction_type=', content)
            content = re.sub(r'\bdate\s*=\s*', 'transaction_date=', content)
            content = content.replace('Transaction.date', 'Transaction.transaction_date')
            content = content.replace('Transaction.type', 'Transaction.transaction_type')
            content = content.replace('"date"', '"transaction_date"').replace("'date'", "'transaction_date'")
            content = content.replace('"type"', '"transaction_type"').replace("'type'", "'transaction_type'")
            
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
print("done")
