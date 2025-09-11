from src.config import DEFAULT_EXCHANGE
from src.database.models import CryptoPrice
from sqlalchemy.orm import Session

from .fetchers.base import BaseFetcher
from .fetchers.binance import BinanceFetcher
from .fetchers.kucoin import KucoinFetcher

def get_fetcher(exchange: str = DEFAULT_EXCHANGE) -> 'BaseFetcher':
    """Factory برای انتخاب فچر مناسب"""
    if exchange.lower() == "binance":
        return BinanceFetcher()
    elif exchange.lower() == "kucoin":
        return KucoinFetcher()
    else:
        raise ValueError(f"صرافی {exchange} پشتیبانی نمی‌شود")

def save_candles_to_db(session: Session, candles: list):
    """ذخیره کندل‌ها در دیتابیس"""
    for candle in candles:
        record = CryptoPrice(**candle)
        session.add(record)
    session.commit()