from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Dict, Union, Optional
from .base import BasePattern
from src.database.models import CryptoPrice


class EngulfingPattern(BasePattern):
    """
    تشخیص دقیق الگوی Engulfing (Bullish / Bearish)
    با استفاده از بدنه، روند و حجم.
    """

    def default_predicted_trend(self, pattern_type: str, trend_before: Optional[str] = None) -> str:
        """
        پیاده‌سازی پیش‌فرض برای متد abstract موجود در BasePattern.
        اگر BasePattern signature متفاوتی خواسته باشه (مثلاً پارامترها یا نوع بازگشتی دیگر)
        باید مطابق آن امضا تغییرش بدی.
        """
        if pattern_type == "bullish" and trend_before == "bearish":
            return "bullish"
        if pattern_type == "bearish" and trend_before == "bullish":
            return "bearish"
        return "unknown"

    def detect(
        self,
        session: Session,
        coin_id: str,
        num_candles: int = 200,
        lookback: int = 8,
        min_body_pct: float = 0.002,
        engulf_threshold: float = 1.0,
        min_volume_ratio: float = 1.2,
        trend_ma_period: int = 10,
    ) -> List[Dict[str, Union[Dict, str]]]:
        """تشخیص دقیق الگوی Engulfing با فیلتر روند و حجم."""

        # دریافت داده‌ها
        records = (
            session.query(CryptoPrice)
            .filter(CryptoPrice.coin_id == coin_id)
            .order_by(CryptoPrice.timestamp.asc())
            .limit(num_candles)
            .all()
        )
        if len(records) < 2:
            return []

        # DataFrame
        df = pd.DataFrame(
            [
                {
                    "open": r.open,
                    "close": r.close,
                    "high": r.high,
                    "low": r.low,
                    "volume": r.volume,
                    "timestamp": r.timestamp,
                    "timeframe": r.timeframe,
                }
                for r in records
            ]
        )

        # محاسبه میانگین متحرک برای روند
        df["ma"] = df["close"].rolling(trend_ma_period).mean()

        # محاسبه ATR ساده برای نرمال‌سازی اندازه کندل‌ها
        df["range"] = df["high"] - df["low"]
        df["atr"] = df["range"].rolling(window=trend_ma_period).mean()

        # میانگین حجم برای فیلتر تأیید
        df["avg_volume"] = df["volume"].rolling(window=trend_ma_period).mean()

        detections = []

        for i in range(1, len(df)):
            prev = df.iloc[i - 1]
            curr = df.iloc[i]

            if pd.isna(curr["ma"]) or pd.isna(curr["atr"]) or curr["atr"] == 0:
                continue

            # محاسبه بدنه
            prev_body = abs(prev["close"] - prev["open"])
            curr_body = abs(curr["close"] - curr["open"])
            prev_body_pct = prev_body / ((prev["open"] + prev["close"]) / 2)
            curr_body_pct = curr_body / ((curr["open"] + curr["close"]) / 2)

            # حذف کندل‌های خیلی کوچک
            if curr_body_pct < min_body_pct or prev_body_pct < min_body_pct:
                continue

            # تشخیص روند قبلی دقیق‌تر
            prev_trend = self._detect_trend(df, i - 1, lookback)
            if prev_trend == "unknown":
                continue

            # نسبت حجم فعلی به میانگین حجم اخیر
            volume_ratio = (
                curr["volume"] / curr["avg_volume"] if curr["avg_volume"] > 0 else 1
            )

            # Bullish Engulfing
            if (
                prev["close"] < prev["open"]
                and curr["close"] > curr["open"]
                and curr["low"] <= prev["close"]
                and curr["high"] >= prev["open"]
                and curr_body >= prev_body * engulf_threshold
                and volume_ratio >= min_volume_ratio
                and prev_trend == "bearish"
                and curr["close"] > curr["ma"]  # تأیید تغییر روند
            ):
                detections.append(self._build_detection("bullish", i, curr, prev, volume_ratio, prev_trend))

            # Bearish Engulfing
            elif (
                prev["close"] > prev["open"]
                and curr["close"] < curr["open"]
                and curr["high"] >= prev["close"]
                and curr["low"] <= prev["open"]
                and curr_body >= prev_body * engulf_threshold
                and volume_ratio >= min_volume_ratio
                and prev_trend == "bullish"
                and curr["close"] < curr["ma"]
            ):
                detections.append(self._build_detection("bearish", i, curr, prev, volume_ratio, prev_trend))

        return detections

    def _detect_trend(self, df: pd.DataFrame, pos: int, lookback: int) -> str:
        """تشخیص روند با شیب میانگین بسته‌شدن‌ها."""
        if pos < lookback:
            return "unknown"

        subset = df.iloc[pos - lookback : pos]
        if len(subset) < 3:
            return "unknown"

        slope = subset["close"].iloc[-1] - subset["close"].iloc[0]
        if slope > 0 and subset["ma"].iloc[-1] > subset["ma"].iloc[0]:
            return "bullish"
        elif slope < 0 and subset["ma"].iloc[-1] < subset["ma"].iloc[0]:
            return "bearish"
        else:
            return "unknown"

    def _build_detection(self, pattern_type, i, curr, prev, volume_ratio, prev_trend):
        """ایجاد خروجی استاندارد الگو"""
        return {
            "position": i,
            "timestamp": curr["timestamp"].isoformat(),
            "pattern_type": pattern_type,
            "trend_before": prev_trend,
            "metrics": {
                "body_ratio": round(abs(curr["close"] - curr["open"]) / abs(prev["close"] - prev["open"]), 2),
                "volume_ratio": round(volume_ratio, 2),
                "ma": round(curr["ma"], 3),
            },
        }
