from typing import List, Dict, Any
from datetime import datetime

class TransactionNormalizer:
    @staticmethod
    def normalize(raw_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for row in raw_rows:
            date_str = str(row.get('date', row.get('Date', ''))).strip()
            amt_str = str(row.get('amount', row.get('Amount', ''))).replace(',','').replace('$','').strip()
            desc_str = str(row.get('description', row.get('Description', row.get('merchant', '')))).strip()
            
            try:
                amt = float(amt_str)
            except ValueError:
                amt = 0.0
                
            fmt_date = None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"):
                try:
                    fmt_date = datetime.strptime(date_str[:10], fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
                    
            normalized.append({"Date": fmt_date or date_str, "Amount": amt, "Description": desc_str})
        return normalized
