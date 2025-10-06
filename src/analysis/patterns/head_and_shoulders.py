from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict, Union
from .base import BasePattern
from src.database.models import CryptoPrice

class HeadAndShouldersPattern(BasePattern):
    """تشخیص الگوی Head and Shoulders"""

    def detect(self, session: Session, coin_id: str, num_candles: int = 100) -> List[Dict[str, Union[Dict, str]]]:
        """تشخیص الگوی Head and Shoulders در داده‌ها"""
        records = session.query(CryptoPrice).filter(
            CryptoPrice.coin_id == coin_id
        ).order_by(CryptoPrice.timestamp.asc()).limit(num_candles).all()

        if len(records) < 7:  # حداقل 7 کندل برای الگو
            return []

        df = pd.DataFrame([{
            'open': r.open,
            'close': r.close,
            'high': r.high,
            'low': r.low,
            'volume': r.volume,
            'date': r.timestamp,
            'timeframe': r.timeframe
        } for r in records])

        detections = []
        for position in range(6, len(df)):  # نیاز به حداقل 7 کندل برای الگو
            # فرض ساده برای تشخیص (باید منطق واقعی الگو رو پیاده کنی)
            left_shoulder = df.iloc[position-5:position-3]
            head = df.iloc[position-3:position-1]
            right_shoulder = df.iloc[position-1:position+1]

            # منطق ساده برای مثال
            if (
                left_shoulder['high'].max() < head['high'].max() and
                right_shoulder['high'].max() < head['high'].max() and
                abs(left_shoulder['high'].max() - right_shoulder['high'].max()) < 0.01 * head['high'].max()
            ):
                timeframe = df.iloc[position]['timeframe']
                detections.append({
                    "position": position,
                    "timestamp": df.iloc[position]['date'].isoformat(),
                    "detected": True,
                    "trend_before": self._get_trend(session, coin_id, timeframe, df.iloc[position]['date'], num_candles=5),
                    "predicted_trend": self._get_trend(session, coin_id, timeframe, df.iloc[position]['date'], num_candles=5, is_future=True)
                })

        return detections