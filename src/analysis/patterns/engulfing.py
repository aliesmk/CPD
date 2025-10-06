from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict
from .base import BasePattern
from src.database.models import CryptoPrice

class EngulfingPattern(BasePattern):
    """تشخیص الگوی Engulfing (هم Bullish و هم Bearish)"""

    def detect(self, session: Session, coin_id: str, num_candles: int = 100) -> List[Dict[str, any]]:
        """تشخیص الگوی Engulfing در تمام موقعیت‌های داده‌ها"""
        records = session.query(CryptoPrice).filter(
            CryptoPrice.coin_id == coin_id
        ).order_by(
            CryptoPrice.timestamp.asc()  # به ترتیب زمانی برای اسکن از قدیمی به جدید
        ).limit(num_candles).all()

        if len(records) < 6:  # حداقل 6 کندل برای بررسی روند
            return []

        df = pd.DataFrame([{
            'open': r.open,
            'close': r.close,
            'volume': r.volume,
            'id': r.id,
            'date': r.timestamp
        } for r in records])

        detections = []
        for position in range(1, len(df)):  # از 1 شروع کن تا قبلی وجود داشته باشه
            prev_row = df.iloc[position - 1]
            curr_row = df.iloc[position]

            prev_open, prev_close, prev_volume = prev_row['open'], prev_row['close'], prev_row['volume']
            curr_open, curr_close, curr_volume = curr_row['open'], curr_row['close'], curr_row['volume']

            prev_trend = self._check_prev_trend(df, position)

            prev_body_size = abs(prev_close - prev_open) / prev_open
            curr_body_size = abs(curr_close - curr_open) / curr_open
            min_body_size = 0.001

            bullish = (
                prev_close < prev_open and
                curr_close > curr_open and
                curr_open < prev_close and
                curr_close > prev_open and
                curr_volume > prev_volume * 0.8 and
                prev_trend == "bearish" and
                prev_body_size > min_body_size and
                curr_body_size > min_body_size
            )

            bearish = (
                prev_close > prev_open and
                curr_close < curr_open and
                curr_open > prev_close and
                curr_close < prev_open and
                curr_volume > prev_volume * 0.8 and
                prev_trend == "bullish" and
                prev_body_size > min_body_size and
                curr_body_size > min_body_size
            )

            if bullish or bearish:
                detections.append({
                    "position": position,
                    "timestamp": curr_row['date'].isoformat(),
                    "bullish": bullish,
                    "bearish": bearish
                })

        return detections

    def _check_prev_trend(self, df: pd.DataFrame, position: int, lookback: int = 5) -> str:
        """بررسی روند کندل‌های قبلی"""
        start_idx = position - lookback
        end_idx = position - 1

        if start_idx < 0:
            return "unknown"

        prev_candles = df.iloc[start_idx:end_idx]
        bearish_count = sum(prev_candles['close'] < prev_candles['open'])
        bullish_count = len(prev_candles) - bearish_count

        if bearish_count > bullish_count:
            return "bearish"
        else:
            return "bullish"