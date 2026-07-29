import filetype
import os
from .exceptions import InvalidMIMETypeException, FileSizeExceededException

class ReceiptValidator:
    ALLOWED_MIMES = {'image/jpeg', 'image/png', 'image/webp'}
    MAX_SIZE_MB = 10

    @staticmethod
    def validate(file_path: str):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > ReceiptValidator.MAX_SIZE_MB:
            raise FileSizeExceededException(f"Image exceeds {ReceiptValidator.MAX_SIZE_MB}MB limit.")
            
        mime = filetype.guess(file_path)
        if mime is None or mime.mime not in ReceiptValidator.ALLOWED_MIMES:
            raise InvalidMIMETypeException(f"Unsupported MIME type.")
