import os
from app.services.imports.exceptions import UnsupportedFileException

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.pdf'}
MAX_FILE_SIZE_MB = 10

class FileValidator:
    @staticmethod
    def validate(file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileException(f"Unsupported file type: {ext}")
        
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise UnsupportedFileException(f"File exceeds max size of {MAX_FILE_SIZE_MB}MB")
