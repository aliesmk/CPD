import datetime
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Dict, Union, List
from src.database.models import CryptoPrice
import pandas as pd


class BasePattern(ABC):
    """کلاس پایه برای تشخیص الگوهای هارمونیک"""

    @abstractmethod
    def detect(self, session: Session, coin_id: str, num_candles: int = 100) -> List[Dict[str, Union[Dict, str]]]:
        """تشخیص الگو در داده‌های کندل"""
        pass

    @abstractmethod
    def default_predicted_trend(self, pattern_type: str, trend_before: str = None) -> str:
        """روند پیش‌فرض بر اساس تعریف الگو و روند قبلی"""
        pass

    def _get_trend(self, session: Session, coin_id: str, timeframe: str, timestamp: datetime, num_candles: int = 5,
                   is_future: bool = False, pattern_type: str = None, detections: List[Dict] = None) -> str:
        """محاسبه روند برای کندل‌های قبل یا بعد از زمان مشخص"""
        if is_future:
            # برای پیش‌بینی روند بعدی (بعد از timestamp)
            records = session.query(CryptoPrice).filter(
                CryptoPrice.coin_id == coin_id,
                CryptoPrice.timeframe == timeframe,
                CryptoPrice.timestamp >= timestamp
            ).order_by(CryptoPrice.timestamp.asc()).limit(num_candles).all()

            if len(records) < num_candles:
                # اگر داده آینده کافی نیست، از تاریخچه یا تعریف الگو استفاده کن
                if detections and pattern_type:
                    trend_before = self._get_trend(session, coin_id, timeframe, timestamp, num_candles=5,
                                                   is_future=False)
                    history_pred = self._predict_from_history(detections, pattern_type)
                    if history_pred != "unknown":
                        return history_pred
                    return self.default_predicted_trend(pattern_type, trend_before)
                return self.default_predicted_trend(pattern_type, None) if pattern_type else "unknown"

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
        df = pd.DataFrame(closes, columns=['close'])
        bullish_count = sum(df['close'].diff() > 0)
        bearish_count = sum(df['close'].diff() < 0)

        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        else:
            return "neutral"

    def _predict_from_history(self, detections: List[Dict], pattern_type: str) -> str:
        """پیش‌بینی روند بعدی بر اساس تاریخچه الگوها"""
        if not detections:
            return "unknown"

        trends = [d["trend_after"] for d in detections if d["pattern_type"].lower() == pattern_type.lower()]
        if not trends:
            return "unknown"

        bullish_count = trends.count("bullish")
        bearish_count = trends.count("bearish")
        neutral_count = trends.count("neutral")

        total = len(trends)
        if bullish_count / total > 0.5:
            return "bullish"
        elif bearish_count / total > 0.5:
            return "bearish"
        else:
            return "neutral"