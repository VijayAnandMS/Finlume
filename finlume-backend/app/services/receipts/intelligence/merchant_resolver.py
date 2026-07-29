import re

class MerchantResolver:
    # Basic dictionary mimicking common OCR hallucinations without loading heavy external LLMs for standard stores
    MERCHANT_ALIASES = {
        "W-MART": "Walmart",
        "WALMART": "Walmart",
        "TRGT": "Target",
        "STRBUCKS": "Starbucks",
        "MC DONALDS": "McDonald's",
    }
    
    @staticmethod
    def resolve_merchant(raw_merchant: str) -> dict:
        if not raw_merchant or raw_merchant == "Unknown Merchant":
            return {"suggested_name": raw_merchant, "resolution_confidence": 0.0}
            
        clean_name = str(raw_merchant).upper().strip()
        
        # Alias lookup explicitly mimicking intelligent mapping securely
        for alias, real_name in MerchantResolver.MERCHANT_ALIASES.items():
            if alias in clean_name or clean_name in alias:
                return {"suggested_name": real_name, "resolution_confidence": 0.95}
                
        # Simple Case normalization as fallback
        title_cased = raw_merchant.title()
        return {"suggested_name": title_cased, "resolution_confidence": 0.60}
