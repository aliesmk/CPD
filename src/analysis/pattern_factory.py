import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from src.database.models import CryptoPrice
from .patterns.base import BasePattern
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

def calculate_rsi(db: Session, coin_id: str, timeframe: str, timestamp: datetime, periods: int = 14) -> float:
    """محاسبه RSI برای یک کوین در زمان مشخص"""
    records = db.query(CryptoPrice).filter(
        CryptoPrice.coin_id == coin_id,
        CryptoPrice.timeframe == timeframe,
        CryptoPrice.timestamp <= timestamp
    ).order_by(CryptoPrice.timestamp.desc()).limit(periods + 1).all()

    if len(records) < periods + 1:
        return 0.0

    prices = [r.close for r in records]
    df = pd.DataFrame(prices, columns=['close'])
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=periods).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=periods).mean()
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if rs != 0 else 0
    return round(rsi, 2)

def calculate_sma(db: Session, coin_id: str, timeframe: str, periods: int, timestamp: datetime) -> float:
    """محاسبه میانگین متحرک ساده (SMA)"""
    records = db.query(CryptoPrice).filter(
        CryptoPrice.coin_id == coin_id,
        CryptoPrice.timeframe == timeframe,
        CryptoPrice.timestamp <= timestamp
    ).order_by(CryptoPrice.timestamp.desc()).limit(periods).all()

    if len(records) < periods:
        return 0.0

    prices = [r.close for r in records]
    return round(sum(prices) / len(prices), 2)

def determine_trend(db: Session, coin_id: str, timeframe: str, timestamp: datetime, num_candles: int = 5) -> str:
    """تعیین روند (صعودی، نزولی یا خنثی)"""
    records = db.query(CryptoPrice).filter(
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