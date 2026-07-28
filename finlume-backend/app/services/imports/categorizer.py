from typing import List, Dict, Any
from app.ai.orchestrator import call_orchestrator
from .category_models import CategorizationResult, ClassificationSource
from .confidence import ConfidenceConfig
from .category_rules import CATEGORIES, KEYWORD_RULES
import json

class TransactionCategorizer:
    def __init__(self, user_id: int):
        self.user_id = user_id
        
    def _evaluate_rules(self, desc: str, amt: float) -> CategorizationResult:
        desc_lower = desc.lower()
        for category, keywords in KEYWORD_RULES.items():
            for kw in keywords:
                if kw in desc_lower:
                    return CategorizationResult(category=category, confidence=0.95, source=ClassificationSource.RULE, reason=f"Matched: {kw}")
        return None
        
    def _evaluate_ai(self, tx: Dict[str, Any]) -> CategorizationResult:
        desc = tx.get("Description", "")
        amt = tx.get("Amount", 0.0)
        prompt = (f"Categorize strictly: {json.dumps(CATEGORIES)}. Desc: {desc}, Amt: {amt}. Reply ONLY with category name.")
        try:
            res = call_orchestrator(self.user_id, prompt, summary_data={}, transactions=[])
            reply = str(res.get("reply", "")).strip()
            
            matched_cat = "Miscellaneous"
            for c in CATEGORIES:
                if c.lower() in reply.lower():
                    matched_cat = c
                    break
                    
            return CategorizationResult(
                category=matched_cat, confidence=ConfidenceConfig.AI_CONFIDENCE_DEFAULT, 
                source=ClassificationSource.AI, reason="LLM Inference"
            )
        except Exception:
            return None

    def categorize_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for tx in transactions:
            desc = str(tx.get('Description', ''))
            amt = float(tx.get('Amount', 0.0))
            
            cat_res = self._evaluate_rules(desc, amt)
            if not cat_res: cat_res = self._evaluate_ai(tx)
            if not cat_res or cat_res.confidence < ConfidenceConfig.MEDIUM_THRESHOLD:
                cat_res = CategorizationResult(category="Miscellaneous", confidence=0.0, source=ClassificationSource.MANUAL_REQUIRED, reason="Low confidence")
                
            tx['Category'] = cat_res.category
            tx['ai_category_suggestion'] = cat_res.category
            tx['category_confidence'] = cat_res.confidence
            tx['category_source'] = cat_res.source.value
            tx['category_reason'] = cat_res.reason
            results.append(tx)
        return results
