from src.config import DEFAULT_EXCHANGE
from src.database.models import CryptoPrice
from sqlalchemy.orm import Session
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
    for candle in candles:
        exists = session.query(CryptoPrice).filter(
            CryptoPrice.coin_id == candle["coin_id"],
            CryptoPrice.timestamp == candle["timestamp"]
        ).first()

        if not exists:
            record = CryptoPrice(**candle)
            session.add(record)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"خطا در ذخیره‌سازی: {e}")