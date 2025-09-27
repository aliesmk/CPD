from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .base import BasePattern
import pandas as pd

class HeadAndShouldersPattern(BasePattern):
   """تشخیص الگوی Head and Shoulders"""
   def detect(self, session: Session, coin_id: str, num_candles: int = 50) -> bool:
       """تشخیص الگوی Head and Shoulders با استفاده از داده‌های کندل"""
       records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
       if len(records) < 7:  # حداقل 7 کندل برای شانه چپ، سر، شانه راست
           return False

       df = pd.DataFrame([{
           'high': r.high,
           'low': r.low,
           'close': r.close
       } for r in records]).sort_index(ascending=False)

       # ساده‌سازی: پیدا کردن پیک‌های high برای شانه چپ (left shoulder)، سر (head)، شانه راست (right shoulder)
       highs = df['high'].rolling(window=3, center=True).max()
       peaks = highs[highs == df['high']].index[:3]  # سه پیک آخر
       if len(peaks) < 3:
           return False

       left_shoulder, head, right_shoulder = df['high'].iloc[peaks]
       if head > left_shoulder and head > right_shoulder and abs(left_shoulder - right_shoulder) < 0.05 * head:  # شانه‌ها تقریباً برابر
           return True
       return False