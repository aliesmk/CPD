from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .base import BasePattern
import pandas as pd

class DoubleTopBottomPattern(BasePattern):
   """تشخیص الگوی Double Top/Bottom"""
   def detect(self, session: Session, coin_id: str, num_candles: int = 50) -> bool:
       """تشخیص الگوی Double Top/Bottom با استفاده از داده‌های کندل"""
       records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
       if len(records) < 5:  # حداقل 5 کندل برای دو قله/کف
           return False

       df = pd.DataFrame([{
           'high': r.high,
           'low': r.low,
           'close': r.close
       } for r in records]).sort_index(ascending=False)

       # ساده‌سازی: چک کردن دو پیک high مشابه برای Double Top
       highs = df['high'].rolling(window=3, center=True).max()
       peaks = highs[highs == df['high']].index[:2]  # دو پیک آخر
       if len(peaks) < 2:
           return False

       top1, top2 = df['high'].iloc[peaks]
       if abs(top1 - top2) < 0.05 * top1:  # دو قله تقریباً برابر
           return True  # Double Top (برای Bottom می‌تونیم low رو چک کنیم)

       return False