from typing import List, Dict, Any
import abc

class DocumentParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        pass
