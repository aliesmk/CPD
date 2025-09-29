from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    """کلاس پایه برای فچرهای صرافی"""
    @abstractmethod
    def fetch_candles(self, symbol: str, interval: str, limit: int) -> list:
        """گرفتن کندل‌ها از صرافی"""
        pass