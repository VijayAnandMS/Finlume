from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models.models import Transaction
from .duplicate_matcher import DuplicateMatcher
from .duplicate_models import DuplicateResult, DuplicateStatus

class DuplicateDetector:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self._existing_transactions = []
        self._preloaded = False

    def _preload_window(self, imported_transactions: List[Dict[str, Any]]):
        dates = []
        for tx in imported_transactions:
            d_str = tx.get('Date')
            if d_str:
                try:
                    dates.append(datetime.strptime(d_str, "%Y-%m-%d").date())
                except (ValueError, TypeError):
                    pass
                    
        if dates:
            min_date = min(dates) - timedelta(days=7)
            max_date = max(dates) + timedelta(days=7)
            self._existing_transactions = self.db.query(Transaction).filter(
                Transaction.user_id == self.user_id,
                Transaction.transaction_date >= min_date.strftime("%Y-%m-%d"),
                Transaction.transaction_date <= max_date.strftime("%Y-%m-%d")
            ).all()
        else:
            self._existing_transactions = self.db.query(Transaction).filter(Transaction.user_id == self.user_id).all()
        
        self._preloaded = True

    def process_batch(self, imported_transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self._preload_window(imported_transactions)
        
        results = []
        for tx in imported_transactions:
            try:
                match_res = DuplicateMatcher.match(tx, self._existing_transactions)
                tx['Duplicate Status'] = match_res.status.value
                tx['Duplicate Confidence'] = match_res.confidence
                tx['Duplicate Target'] = match_res.matched_transaction_id
                tx['Duplicate Reason'] = match_res.reason
            except Exception as e:
                 tx['Duplicate Status'] = DuplicateStatus.UNKNOWN.value
                 tx['Duplicate Reason'] = str(e)
            results.append(tx)
            
        return results
