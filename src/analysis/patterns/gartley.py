from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .base import BasePattern
import pandas as pd

class GartleyPattern(BasePattern):
   """تشخیص الگوی هارمونیک Gartley"""
   def detect(self, session: Session, coin_id: str, num_candles: int = 100) -> bool:
       """تشخیص الگوی Gartley با استفاده از داده‌های کندل"""
       records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
       if len(records) < 5:  # حداقل 5 کندل برای نقاط XA, AB, BC, CD
           return False

       df = pd.DataFrame([{
           'high': r.high,
           'low': r.low,
           'close': r.close
       } for r in records]).sort_index(ascending=False)

       # ساده‌سازی: چک کردن نسبت‌های فیبوناچی تقریبی برای نقاط XA, AB, BC, CD
       # فرض می‌کنیم 5 کندل آخر نقاط D, C, B, A, X رو تشکیل می‌دن
       X, A, B, C, D = df.iloc[:5][['high', 'low']].values
       # محاسبه نسبت‌های فیبوناچی (برای Gartley صعودی)
       AB = abs(A[0] - B[1]) / abs(X[0] - A[1])
       BC = abs(B[1] - C[0]) / abs(A[0] - B[1])
       CD = abs(C[0] - D[1]) / abs(B[1] - C[0])

       # نسبت‌های تقریبی Gartley
       if (0.6 < AB < 0.7 and 0.6 < BC < 0.7 and 0.7 < CD < 0.9):
           return True
       return False