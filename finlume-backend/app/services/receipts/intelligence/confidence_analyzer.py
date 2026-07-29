class ConfidenceAnalyzer:
    @staticmethod
    def analyze_confidence(parsed_data: dict, ocr_confidence: float) -> dict:
        flags = []
        overall = ocr_confidence
        
        # Penalize confidence on missing Merchant
        if parsed_data.get("merchant_name") == "Unknown Merchant":
            overall *= 0.8
            flags.append("Merchant missing or illegible")
            
        # Penalize on invalid date defaults
        if not parsed_data.get("transaction_date"):
            overall *= 0.9
            flags.append("Date format illegible")
            
        # Missing total triggers flag
        if parsed_data.get("total", 0.0) <= 0.0:
            overall *= 0.5
            flags.append("Warning: Zero Total or missing numerical boundaries")
            
        return {
            "overall_confidence": round(overall, 2),
            "requires_manual_review": overall < 0.75,
            "uncertainty_reasons": flags
        }
