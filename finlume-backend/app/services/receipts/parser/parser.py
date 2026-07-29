import json
from .merchant_parser import MerchantParser
from .amount_parser import AmountParser
from .date_parser import DateParser

class ReceiptParser:
    @staticmethod
    def parse_ocr_result(detected_fields: dict) -> dict:
        """
        Takes raw Key-Values detected by Azure Provider 
        and extracts strict structured metadata cleanly.
        """
        merchant = MerchantParser.parse_merchant(detected_fields.get("merchant_name"))
        date = DateParser.parse_date(detected_fields.get("transaction_date"))
        
        subtotal = AmountParser.parse_amount(detected_fields.get("subtotal"))
        tax = AmountParser.parse_amount(detected_fields.get("tax"))
        total = AmountParser.parse_amount(detected_fields.get("total"))
        
        # Validation numeric heuristic explicitly tracing logic safely
        warnings = []
        if total == 0.0 and (subtotal > 0.0 or tax > 0.0):
            total = subtotal + tax
            warnings.append("Total reconstructed from subtotal and tax.")
            
        if abs((subtotal + tax) - total) > 0.1 and total > 0.0 and subtotal > 0.0:
            warnings.append("Numeric inconsistency: Subtotal + Tax does not match Total.")
            
        if not merchant or merchant == "Unknown Merchant":
            warnings.append("Missing or ambiguous Merchant Name.")
            
        if not date:
            warnings.append("Invalid or Missing Transaction Date.")
            
        return {
            "merchant_name": merchant,
            "transaction_date": date,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "currency": detected_fields.get("currency", "USD") or "USD",
            "warnings": warnings
        }
