from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .base import BasePattern
import pandas as pd

class ButterflyPattern(BasePattern):
   """تشخیص الگوی هارمونیک Butterfly"""
   def detect(self, session: Session, coin_id: str, num_candles: int = 100) -> bool:
       """تشخیص الگوی Butterfly با استفاده از داده‌های کندل"""
       records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
       if len(records) < 5:  # حداقل 5 کندل برای نقاط XA, AB, BC, CD
           return False

       df = pd.DataFrame([{
           'high': r.high,
           'low': r.low,
           'close': r.close
       } for r in records]).sort_index(ascending=False)

       # ساده‌سازی: چک کردن نسبت‌های فیبوناچی تقریبی برای نقاط XA, AB, BC, CD
       X, A, B, C, D = df.iloc[:5][['high', 'low']].values
       AB = abs(A[0] - B[1]) / abs(X[0] - A[1])
       BC = abs(B[1] - C[0]) / abs(A[0] - B[1])
       CD = abs(C[0] - D[1]) / abs(B[1] - C[0])

       # نسبت‌های تقریبی Butterfly
       if (0.7 < AB < 0.9 and 0.3 < BC < 0.5 and 1.2 < CD < 1.6):
           return True
       return False