import csv
from typing import List, Dict, Any
from .parser_interface import DocumentParser
from .normalizer import TransactionNormalizer
from .exceptions import MissingColumnsException, CorruptedFileException

class CSVParser(DocumentParser):
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        rows = []
        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = [c.lower() for c in (reader.fieldnames or [])]
                if not any(x in fieldnames for x in ['date', 'amount', 'description', 'merchant']):
                    raise MissingColumnsException("CSV is missing required headers.")
                for row in reader:
                    rows.append(row)
        except Exception as e:
            if isinstance(e, MissingColumnsException): raise
            raise CorruptedFileException("File corrupted.")
        return TransactionNormalizer.normalize(rows)
