import datetime
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session
from typing import Dict, Union, List

from src.database.models import CryptoPrice


class BasePattern(ABC):
    """کلاس پایه برای تشخیص الگوهای هارمونیک"""

    @abstractmethod
    def detect(self, session: Session, coin_id: str, num_candles: int = 100) -> List[Dict[str, Union[bool, str, Dict]]]:
        """تشخیص الگو در داده‌های کندل
        خروجی: لیست دیکشنری‌هایی با کلیدهای detected, trend_before, predicted_trend
        """
        pass

    def _get_trend(self, session: Session, coin_id: str, timeframe: str, timestamp: datetime, num_candles: int = 5,
                   is_future: bool = False) -> str:
        """محاسبه روند برای کندل‌های قبل یا بعد از زمان مشخص"""
        from src.analysis.pattern_factory import determine_trend
        if is_future:
            # برای پیش‌بینی روند بعدی (بعد از timestamp)
            records = session.query(CryptoPrice).filter(
                CryptoPrice.coin_id == coin_id,
                CryptoPrice.timeframe == timeframe,
                CryptoPrice.timestamp >= timestamp
            ).order_by(CryptoPrice.timestamp.asc()).limit(num_candles).all()
        else:
            # برای روند قبل (قبل از timestamp)
            records = session.query(CryptoPrice).filter(
                CryptoPrice.coin_id == coin_id,
                CryptoPrice.timeframe == timeframe,
                CryptoPrice.timestamp <= timestamp
            ).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()

        if len(records) < num_candles:
            return "unknown"

        closes = [r.close for r in records]
        import pandas as pd
        df = pd.DataFrame(closes, columns=['close'])
        bullish_count = sum(df['close'].diff() > 0)
        bearish_count = sum(df['close'].diff() < 0)

        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        else:
            return "neutral"