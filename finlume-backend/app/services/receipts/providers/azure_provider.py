import time
import json
import logging
from typing import Dict, Any
from .base_provider import BaseOCRProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class AzureOCRProvider(BaseOCRProvider):
    # Dummy mock provider wrapping structural Azure payload requirements safely without executing external HTTP targets locally
    
    def extract_receipt(self, file_path: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info("Processing start: Azure OCR Extraction")
        
        # Simulate Network latency & Transient retries statically
        retries = 3
        for attempt in range(retries):
            try:
                # Simulating Azure "prebuilt-receipt" model
                time.sleep(1.5) 
                
                confidence_score = 0.94
                raw_text = "MOCK AZURE RECEIPT\\nTOTAL: 154.20"
                
                results = {
                    "merchant_name": "Azure Coffee Co",
                    "transaction_date": "2026-07-28",
                    "currency": "USD",
                    "subtotal": 140.00,
                    "tax": 14.20,
                    "total": 154.20,
                    "line_items": [
                        {"description": "Latte", "price": 40.00},
                        {"description": "Sandwich", "price": 100.00}
                    ]
                }
                
                duration = int((time.time() - start_time) * 1000)
                logger.info(f"Processing finish: Azure OCR Extraction in {duration}ms (Confidence: {confidence_score})")
                
                return {
                    "raw_text": raw_text,
                    "confidence": confidence_score,
                    "detected_fields": results,
                    "bounding_regions": {"merchant": [0,0, 100, 20]}, # Sample Mock Boxes
                    "processing_time_ms": duration,
                    "warnings": [],
                    "errors": []
                }
                
            except Exception as e: # Transient network loops
                if attempt == retries - 1:
                    logger.error("Failures: Azure OCR extraction failed after retries.")
                    # Sanitized error response
                    return {
                        "raw_text": "",
                        "confidence": 0.0,
                        "detected_fields": {},
                        "processing_time_ms": int((time.time() - start_time) * 1000),
                        "warnings": [],
                        "errors": ["Azure API Timeout or Network Failure"]
                    }
                time.sleep(1)
        
        return {}
