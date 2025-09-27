from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .base import BasePattern
import pandas as pd

class BullishEngulfingPattern(BasePattern):
   """تشخیص الگوی Bullish Engulfing"""
   def detect(self, session: Session, coin_id: str, num_candles: int = 50) -> bool:
       """تشخیص الگوی Bullish Engulfing با استفاده از داده‌های کندل"""
       records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
       if len(records) < 2:  # حداقل 2 کندل
           return False

       df = pd.DataFrame([{
           'open': r.open,
           'close': r.close
       } for r in records]).sort_index(ascending=False)

       # چک کردن دو کندل آخر
       prev_open, prev_close = df.iloc[1]['open'], df.iloc[1]['close']
       curr_open, curr_close = df.iloc[0]['open'], df.iloc[0]['close']

       # شرایط Bullish Engulfing: کندل قبلی نزولی، کندل فعلی صعودی و بدنه‌ش بزرگ‌تر و پوشش‌دهنده
       if prev_close < prev_open and curr_close > curr_open and curr_open < prev_close and curr_close > prev_open:
           return True
       return False