import json
import logging
from .merchant_resolver import MerchantResolver
from .category_predictor import CategoryPredictor
from .confidence_analyzer import ConfidenceAnalyzer

logger = logging.getLogger(__name__)

class ReceiptIntelligenceService:
    @staticmethod
    def enrich_receipt(parsed_data: dict, ocr_confidence: float, user_id: int) -> dict:
        try:
            merchant_resolution = MerchantResolver.resolve_merchant(parsed_data.get("merchant_name"))
            suggested_merchant = merchant_resolution["suggested_name"]
            
            category = CategoryPredictor.predict_category(suggested_merchant, parsed_data.get("total", 0.0), user_id)
            
            confidence_analysis = ConfidenceAnalyzer.analyze_confidence(parsed_data, ocr_confidence)
            
            field_suggestions = {}
            if suggested_merchant != parsed_data.get("merchant_name") and suggested_merchant != "Unknown Merchant":
                field_suggestions["merchant_name"] = suggested_merchant
                
            return {
                "predicted_category": category,
                "field_corrections": field_suggestions,
                "overall_confidence": confidence_analysis["overall_confidence"],
                "requires_manual_review": confidence_analysis["requires_manual_review"],
                "uncertainty_reasons": confidence_analysis["uncertainty_reasons"]
            }
        except Exception as e:
            logger.error(f"Intelligence processing failure gracefully caught: {e}")
            return {
                "predicted_category": "Uncategorized",
                "field_corrections": {},
                "overall_confidence": 0.0,
                "requires_manual_review": True,
                "uncertainty_reasons": ["AI processing fault securely suppressed"]
            }
