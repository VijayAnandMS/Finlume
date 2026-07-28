from difflib import SequenceMatcher

class DuplicateRulesConfig:
    DATE_TOLERANCE_DAYS = 3
    DESCRIPTION_SIMILARITY_THRESHOLD = 0.70
    AMOUNT_TOLERANCE = 0.0

def calculate_similarity(a: str, b: str) -> float:
    if not a or not b: return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
