from enum import Enum
from pydantic import BaseModel
from typing import Optional

class DuplicateStatus(str, Enum):
    UNIQUE = "UNIQUE"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    UNKNOWN = "UNKNOWN"

class DuplicateResult(BaseModel):
    status: DuplicateStatus
    confidence: float
    matched_transaction_id: Optional[str] = None
    reason: str = ""
