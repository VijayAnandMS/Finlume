from datetime import datetime
from typing import Dict, Any, List
from .duplicate_rules import DuplicateRulesConfig, calculate_similarity
from .duplicate_models import DuplicateResult, DuplicateStatus

class DuplicateMatcher:
    @staticmethod
    def match(imported_tx: Dict[str, Any], existing_txs: List[Any]) -> DuplicateResult:
        imp_amt = float(imported_tx.get('Amount', 0.0))
        imp_desc = str(imported_tx.get('Description', '')).strip()
        imp_date_str = imported_tx.get('Date', '')
        
        try:
            imp_date = datetime.strptime(imp_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            imp_date = None
            
        best_match = DuplicateResult(status=DuplicateStatus.UNIQUE, confidence=0.0)
        
        for ext_tx in existing_txs:
            ext_amt = float(ext_tx.amount)
            if abs(imp_amt - ext_amt) > DuplicateRulesConfig.AMOUNT_TOLERANCE:
                continue 
                
            ext_date_str = ext_tx.transaction_date
            ext_date = None
            try:
                if ext_date_str:
                    ext_date = datetime.strptime(ext_date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
                
            desc_sim = calculate_similarity(imp_desc, str(ext_tx.description or '') + " " + str(ext_tx.merchant or ''))
                
            date_match = (imp_date_str == ext_date_str)
            desc_exact = (imp_desc.lower() == str(ext_tx.description or '').lower() or imp_desc.lower() == str(ext_tx.merchant or '').lower())
            
            if date_match and desc_exact:
                return DuplicateResult(
                    status=DuplicateStatus.EXACT_DUPLICATE, 
                    confidence=1.0, 
                    matched_transaction_id=str(ext_tx.id), 
                    reason="Exact Date, Amount and Description match."
                )
                
            if imp_date and ext_date:
                date_diff = abs((imp_date - ext_date).days)
                if date_diff <= DuplicateRulesConfig.DATE_TOLERANCE_DAYS:
                    if desc_sim >= DuplicateRulesConfig.DESCRIPTION_SIMILARITY_THRESHOLD:
                        if desc_sim > best_match.confidence:
                            best_match = DuplicateResult(
                                status=DuplicateStatus.POSSIBLE_DUPLICATE,
                                confidence=desc_sim,
                                matched_transaction_id=str(ext_tx.id),
                                reason=f"Fuzzy Match: Amount locked, Date offset {date_diff}d, Text similarity {desc_sim:.2f}."
                            )
                            
        return best_match
