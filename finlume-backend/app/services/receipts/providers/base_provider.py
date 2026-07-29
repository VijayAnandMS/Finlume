from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseOCRProvider(ABC):
    @abstractmethod
    def extract_receipt(self, file_path: str) -> Dict[str, Any]:
        """
        Base extraction model resolving OCR targets natively.
        Must return structured dict matching Finlume's internal mapping logic.
        """
        pass
