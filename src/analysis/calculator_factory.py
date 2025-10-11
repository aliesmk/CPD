from .calculators.support_resistance_calculator import SupportResistanceCalculator

AVAILABLE_CALCULATORS = {
    "support_resistance": SupportResistanceCalculator()
}

def get_calculator(calculator_name: str):
    """Factory برای انتخاب کلاس محاسبات"""
    if calculator_name in AVAILABLE_CALCULATORS:
        return AVAILABLE_CALCULATORS[calculator_name]
    raise ValueError(f"محاسبات {calculator_name} پشتیبانی نمی‌شود")