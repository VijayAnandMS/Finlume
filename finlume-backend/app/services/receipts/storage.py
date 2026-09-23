import os
import shutil
import tempfile
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class StorageProvider:
    def save(self, filepath: str, new_filename: str) -> str:
        raise NotImplementedError
        
    def delete(self, new_filename: str):
        raise NotImplementedError
        
    def get_signed_url(self, new_filename: str) -> str:
        raise NotImplementedError
        
    def download(self, new_filename: str, dest_path: str):
        raise NotImplementedError

class LocalStorageProvider(StorageProvider):
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

    def get_signed_url(self, new_filename: str) -> str:
        return os.path.join(self.upload_dir, new_filename)

    def download(self, new_filename: str, dest_path: str):
        src = os.path.join(self.upload_dir, new_filename)
        if os.path.exists(src):
            shutil.copy(src, dest_path)

class SupabaseStorageProvider(StorageProvider):
    def __init__(self):
        from supabase import create_client, Client
        self.bucket = settings.SUPABASE_RECEIPTS_BUCKET
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("Supabase credentials not configured in settings")
        
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
    def _get_path(self, new_filename: str) -> str:
        try:
            parts = new_filename.split("_")
            user_id = parts[0]
            # format: user/{user_id}/receipts/{new_filename}
            return f"user/{user_id}/receipts/{new_filename}"
        except Exception:
            return f"user/unknown/receipts/{new_filename}"

    def save(self, filepath: str, new_filename: str) -> str:
        object_path = self._get_path(new_filename)
        with open(filepath, 'rb') as f:
            self.client.storage.from_(self.bucket).upload(path=object_path, file=f, file_options={"content-type": "image/jpeg"})
        return object_path

    def delete(self, new_filename: str):
        object_path = self._get_path(new_filename)
        self.client.storage.from_(self.bucket).remove([object_path])

    def get_signed_url(self, new_filename: str) -> str:
        object_path = self._get_path(new_filename)
        res = self.client.storage.from_(self.bucket).create_signed_url(object_path, 3600)
        # Handle dict or string based on supabase-py versions
        if isinstance(res, dict):
            return res.get("signedURL", "")
        return str(res)

    def download(self, new_filename: str, dest_path: str):
        object_path = self._get_path(new_filename)
        res = self.client.storage.from_(self.bucket).download(object_path)
        with open(dest_path, "wb") as f:
            f.write(res)

def get_storage_provider() -> StorageProvider:
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
        try:
            return SupabaseStorageProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase, falling back to local storage: {e}")
            return LocalStorageProvider()
    return LocalStorageProvider()

