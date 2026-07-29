from app.services.imports.categorizer import TransactionCategorizer

class CategoryPredictor:
    @staticmethod
    def predict_category(merchant_name: str, total_amount: float, user_id: int) -> str:
        # Reuses Phase 16 AI Categorizer engine
        categorizer = TransactionCategorizer(user_id=user_id)
        mock_tx = [{"Description": merchant_name, "Amount": total_amount}]
        result = categorizer.categorize_batch(mock_tx)
        if result and len(result) > 0:
            return result[0].get("Category", "Miscellaneous")
        return "Miscellaneous"
