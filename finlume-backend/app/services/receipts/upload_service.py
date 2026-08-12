import os
import uuid
import tempfile
import shutil
from fastapi import UploadFile
from .validator import ReceiptValidator
from .image_processor import ImageProcessor
from .storage import LocalStorageProvider

class ReceiptUploadService:
    def __init__(self):
        self.storage = LocalStorageProvider()

    def process_upload(self, file: UploadFile, user_id: int) -> dict:
        filename = os.path.basename(file.filename) if file.filename else "unknown"
        ext = os.path.splitext(filename)[1].lower()
        
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
        if ext not in ALLOWED_EXTENSIONS:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Invalid file type. Allowed: jpg, jpeg, png, pdf")
            
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        
        try:
            with os.fdopen(fd, 'wb') as f:
                shutil.copyfileobj(file.file, f)
                
            ReceiptValidator.validate(temp_path)
            
            new_filename = f"{user_id}_{uuid.uuid4().hex}.jpg"
            processed_path = os.path.join(tempfile.gettempdir(), new_filename)
            ImageProcessor.process_for_storage(temp_path, processed_path)
            
            final_path = self.storage.save(processed_path, new_filename)
            
            return {
                "filename": filename,
                "storage_id": new_filename,
                "storage_url": final_path
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
