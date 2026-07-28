from enum import Enum
from pydantic import BaseModel

class ClassificationSource(str, Enum):
    RULE = "RULE"
    AI = "AI"
    MANUAL_REQUIRED = "MANUAL_REQUIRED"

class CategorizationResult(BaseModel):
    category: str
    confidence: float
    source: ClassificationSource
    reason: str
