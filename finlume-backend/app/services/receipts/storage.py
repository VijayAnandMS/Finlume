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
