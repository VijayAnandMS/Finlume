import pdfplumber
import re
from typing import List, Dict, Any
from .parser_interface import DocumentParser
from .normalizer import TransactionNormalizer
from .exceptions import CorruptedFileException

class PDFParser(DocumentParser):
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        rows = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text: continue
                    for line in text.split('\n'):
                        match = re.match(r'^(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})\s+(.+?)\s+(-?\$?\d+,?\d*\.\d{2})$', line)
                        if match:
                            date, desc, amt = match.groups()
                            rows.append({'Date': date, 'Description': desc, 'Amount': amt})
        except Exception as e:
            raise CorruptedFileException(str(e))
        return TransactionNormalizer.normalize(rows)
