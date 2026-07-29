import re

class MerchantParser:
    @staticmethod
    def parse_merchant(raw_text: str) -> str:
        if not raw_text: return "Unknown Merchant"
        
        # Trim specific trailing special artifacts confidently
        clean = re.sub(r'[^A-Za-z0-9\s\&\'\-]', '', str(raw_text))
        clean = clean.strip()
        
        if not clean: return "Unknown Merchant"
        return clean
