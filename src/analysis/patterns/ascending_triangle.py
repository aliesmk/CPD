from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .base import BasePattern
import pandas as pd
from scipy.stats import linregress

class AscendingTrianglePattern(BasePattern):
   """تشخیص الگوی Ascending Triangle"""
   def detect(self, session: Session, coin_id: str, num_candles: int = 50) -> bool:
       """تشخیص الگوی Ascending Triangle با استفاده از داده‌های کندل"""
       records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
       if len(records) < 10:  # حداقل 10 کندل برای مثلث
           return False

       df = pd.DataFrame([{
           'high': r.high,
           'low': r.low,
           'close': r.close
       } for r in records]).sort_index(ascending=False)

       # ساده‌سازی: چک کردن خط مقاومت افقی (highها ثابت) و خط حمایت صعودی (lowها افزایشی)
       high_std = df['high'].std()  # واریانس highها کم باشه (افقی)
       low_slope = linregress(range(len(df)), df['low']).slope  # شیب lowها مثبت

       if high_std < 0.02 * df['high'].mean() and low_slope > 0:  # آستانه تقریبی
           return True
       return False