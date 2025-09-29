import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .patterns.engulfing import EngulfingPattern
from .patterns.gartley import GartleyPattern
from .patterns.butterfly import ButterflyPattern
from .patterns.head_and_shoulders import HeadAndShouldersPattern
from .patterns.double_top_bottom import DoubleTopBottomPattern
from .patterns.ascending_triangle import AscendingTrianglePattern
from .patterns.bullish_engulfing import BullishEngulfingPattern
from datetime import datetime, timedelta

AVAILABLE_PATTERNS = [
    "head_and_shoulders",
    "double_top_bottom",
    "bullish_engulfing",
    "gartley",
    "butterfly",
    "ascending_triangle",
    "engulfing"
]


def get_pattern_detector(pattern_name: str) -> 'BasePattern':
    """Factory برای انتخاب الگوی تحلیل تکنیکال"""
    if pattern_name.lower() == "gartley":
        return GartleyPattern()
    elif pattern_name.lower() == "butterfly":
        return ButterflyPattern()
    elif pattern_name.lower() == "head_and_shoulders":
        return HeadAndShouldersPattern()
    elif pattern_name.lower() == "double_top_bottom":
        return DoubleTopBottomPattern()
    elif pattern_name.lower() == "ascending_triangle":
        return AscendingTrianglePattern()
    elif pattern_name.lower() == "bullish_engulfing":
        return BullishEngulfingPattern()
    elif pattern_name.lower() == "engulfing":
        return EngulfingPattern()
    else:
        raise ValueError(f"الگوی {pattern_name} پشتیبانی نمی‌شود")

def calculate_rsi(session: Session, coin_id: str, period: int = 14) -> float:
   """محاسبه RSI برای کوین خاص (آخرین مقدار)"""
   records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(200).all()
   if len(records) < period + 1:
       return None

   df = pd.DataFrame([{
       'timestamp': r.timestamp,
       'close': r.close
   } for r in records]).sort_values('timestamp')

   delta = df['close'].diff()
   gain = delta.where(delta > 0, 0)
   loss = -delta.where(delta < 0, 0)

   avg_gain = gain.rolling(window=period, min_periods=1).mean()
   avg_loss = loss.rolling(window=period, min_periods=1).mean()

   rs = avg_gain / avg_loss.replace(0, np.nan)
   rsi = 100 - (100 / (1 + rs))

   return rsi.iloc[-1]

def calculate_sma(session: Session, coin_id: str, timeframe: str, period: int, timestamp: datetime) -> float:
    """محاسبه Simple Moving Average در زمان خاص"""
    records = session.query(CryptoPrice).filter(
        CryptoPrice.coin_id == coin_id,
        CryptoPrice.timeframe == timeframe,
        CryptoPrice.timestamp <= timestamp
    ).order_by(CryptoPrice.timestamp.desc()).limit(period).all()
    if len(records) < period:
        return None
    closes = [r.close for r in records]
    return sum(closes) / len(closes)

def determine_trend(session: Session, coin_id: str, timeframe: str, timestamp: datetime, num_candles: int = 5) -> str:
    """تشخیص روند (bullish/bearish/neutral) قبل یا بعد از زمان خاص"""
    records = session.query(CryptoPrice).filter(
        CryptoPrice.coin_id == coin_id,
        CryptoPrice.timeframe == timeframe,
        CryptoPrice.timestamp <= timestamp
    ).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
    if len(records) < num_candles:
        return "insufficient_data"
    ups = sum(1 for r in records if r.close > r.open)
    downs = sum(1 for r in records if r.close < r.open)
    if ups > downs:
        return "bullish"
    elif downs > ups:
        return "bearish"
    return "neutral"


def calculate_fibonacci_levels(session: Session, coin_id: str, num_candles: int = 100) -> dict:
   """محاسبه سطوح فیبوناچی بر اساس high/low اخیر"""
   records = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()
   if not records:
       return {}

   highs = [r.high for r in records]
   lows = [r.low for r in records]
   max_high = max(highs)
   min_low = min(lows)
   diff = max_high - min_low

   levels = {
       '0.0%': min_low,
       '23.6%': min_low + 0.236 * diff,
       '38.2%': min_low + 0.382 * diff,
       '50.0%': min_low + 0.5 * diff,
       '61.8%': min_low + 0.618 * diff,
       '100.0%': max_high
   }
   return levels