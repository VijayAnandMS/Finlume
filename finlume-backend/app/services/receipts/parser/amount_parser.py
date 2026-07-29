import re

class AmountParser:
    @staticmethod
    def parse_amount(raw_value) -> float:
        if not raw_value: return 0.0
        
        # Remove currency symbols and formatting artifacts safely capturing pure boundaries
        cleaned = re.sub(r'[^0-9\.]', '', str(raw_value).replace(',', '.'))
        try:
            # Handle corner cases where multiple decimals extract cleanly
            parts = cleaned.split('.')
            if len(parts) > 2:
                cleaned = "".join(parts[:-1]) + "." + parts[-1]
            return float(cleaned)
        except ValueError:
            return 0.0
