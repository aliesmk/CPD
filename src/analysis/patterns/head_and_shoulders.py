from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .base import BasePattern
import pandas as pd

class HeadAndShouldersPattern(BasePattern):
   """تشخیص الگوی Head and Shoulders"""
   def detect(self, session: Session, coin_id: str, position: int = -1, num_candles: int = 50) -> bool:
       """تشخیص الگوی Head and Shoulders در موقعیت خاص"""
       records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
       if len(records) < 7:
           return False

       df = pd.DataFrame([{
           'high': r.high,
           'low': r.low,
           'close': r.close
       } for r in records]).sort_index(ascending=False)

       # موقعیت را تنظیم کن
       if position == -1:
           position = len(df) - 1

       # گرفتن داده‌های قبل از position
       df_slice = df.iloc[:position + 1]

       if len(df_slice) < 7:
           return False

       highs = df_slice['high'].rolling(window=3, center=True).max()
       peaks = highs[highs == df_slice['high']].index[:3]  # سه پیک آخر
       if len(peaks) < 3:
           return False

       left_shoulder, head, right_shoulder = df_slice['high'].iloc[peaks]
       if head > left_shoulder and head > right_shoulder and abs(left_shoulder - right_shoulder) < 0.05 * head:
           neckline_lows = df_slice['low'].iloc[peaks[1]:peaks[0]].min()
           if df_slice['low'].iloc[-1] < neckline_lows:
               return True
       return False