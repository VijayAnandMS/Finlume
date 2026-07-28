import os
from .csv_parser import CSVParser
from .excel_parser import ExcelParser
from .pdf_parser import PDFParser
from .validator import ALLOWED_EXTENSIONS

class ParserFactory:
    @staticmethod
    def get_parser(file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv': return CSVParser()
        elif ext == '.xlsx': return ExcelParser()
        elif ext == '.pdf': return PDFParser()
        raise ValueError(f"No parser bound for {ext}")
