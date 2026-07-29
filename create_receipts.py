import os

base_dir = "c:\\Vijay\\Projects\\Finlume\\finlume-backend\\app\\services\\receipts"
os.makedirs(base_dir, exist_ok=True)

files = {}

files["__init__.py"] = ""

files["exceptions.py"] = """
class InvalidMIMETypeException(Exception): pass
class FileSizeExceededException(Exception): pass
class CorruptedImageException(Exception): pass
"""

files["validator.py"] = """
import magic
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
            
        mime = magic.from_file(file_path, mime=True)
        if mime not in ReceiptValidator.ALLOWED_MIMES:
            raise InvalidMIMETypeException(f"Unsupported MIME type: {mime}")
"""

files["image_processor.py"] = """
from PIL import Image, ExifTags
import os

class ImageProcessor:
    @staticmethod
    def process_for_storage(input_path: str, output_path: str):
        try:
            with Image.open(input_path) as img:
                # Orientation correction natively wiping EXIF artifacts securely
                try:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    exif = img._getexif()
                    if exif is not None:
                        if orientation in exif:
                            if exif[orientation] == 3: img = img.rotate(180, expand=True)
                            elif exif[orientation] == 6: img = img.rotate(270, expand=True)
                            elif exif[orientation] == 8: img = img.rotate(90, expand=True)
                except Exception:
                    pass

                # Convert to RGB explicitly dropping hidden alpha telemetry matrices
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                # Re-save with stripped metadata securely
                img.save(output_path, 'JPEG', quality=85)
        except Exception as e:
            from .exceptions import CorruptedImageException
            raise CorruptedImageException("Failed to decode standard image headers natively.")
"""

files["storage.py"] = """
import os
import shutil

class LocalStorageProvider:
    def __init__(self, upload_dir: str = "receipts_storage"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def save(self, filepath: str, new_filename: str) -> str:
        dest = os.path.join(self.upload_dir, new_filename)
        shutil.move(filepath, dest)
        return dest
        
    def delete(self, new_filename: str):
        dest = os.path.join(self.upload_dir, new_filename)
        if os.path.exists(dest):
            os.remove(dest)
"""

for fname, content in files.items():
    with open(os.path.join(base_dir, fname), "w") as f:
        f.write(content.strip() + "\\n")
"""

with open("create_receipts.py", "w") as f:
    f.write(content)
print("Receipt backend templates deployed natively.")
