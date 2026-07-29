from dateutil import parser
from datetime import datetime

class DateParser:
    @staticmethod
    def parse_date(raw_value: str) -> str:
        if not raw_value: return ""
        try:
            # Flexible date bounding natively identifying YYYY-MM-DD vs MM/DD/YYYY gracefully 
            dt = parser.parse(str(raw_value), fuzzy=True)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return ""
