import openpyxl
from typing import List, Dict, Any
from .parser_interface import DocumentParser
from .normalizer import TransactionNormalizer
from .exceptions import MissingColumnsException, CorruptedFileException

class ExcelParser(DocumentParser):
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        rows = []
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            ws = wb.active
            data = list(ws.values)
            if not data: return []
            headers = [str(x) for x in data[0]]
            for row in data[1:]:
                if any(row):
                    rows.append(dict(zip(headers, row)))
        except Exception:
            raise CorruptedFileException("Cannot read Excel structure.")
        return TransactionNormalizer.normalize(rows)
