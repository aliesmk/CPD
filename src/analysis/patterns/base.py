from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from src.database.models import CryptoPrice

class BasePattern(ABC):
   """کلاس پایه برای تشخیص الگوهای هارمونیک"""
   @abstractmethod
   def detect(self, session: Session, coin_id: str, num_candles: int = 100) -> bool:
       """تشخیص الگو در داده‌های کندل"""
       pass