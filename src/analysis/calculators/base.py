from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Dict

class BaseCalculator(ABC):
    """کلاس پایه برای محاسبات تحلیل تکنیکال"""

    @abstractmethod
    def calculate(self, session: Session, symbol: str, timeframe: str, num_candles: int = 100) -> Dict[str, List[float]]:
        """محاسبه و بازگشت سطوح"""
        pass