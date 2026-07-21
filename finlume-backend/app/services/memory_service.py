import os
import chromadb
from chromadb.config import Settings
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MemoryEntry(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]

class MemoryService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryService, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # We store chromadb in a local persistence directory
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "chroma_db")
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="finlume_memory")
        
    def add_memory(self, memory: MemoryEntry):
        self.collection.add(
            documents=[memory.text],
            metadatas=[memory.metadata],
            ids=[memory.id]
        )
        return True

    def query_memory(self, query: str, n_results: int = 3) -> List[MemoryEntry]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        memories = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(docs)
            ids = results["ids"][0] if "ids" in results and results["ids"] else [str(i) for i in range(len(docs))]
            
            for d, m, i in zip(docs, metas, ids):
                memories.append(MemoryEntry(id=i, text=d, metadata=m))
                
        return memories

# Global singleton
memory_service = MemoryService()
