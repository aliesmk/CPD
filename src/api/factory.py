from src.config import DEFAULT_EXCHANGE
from src.database.models import CryptoPrice
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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


def get_fetcher(exchange: str = DEFAULT_EXCHANGE) -> 'BaseFetcher':
    """Factory برای انتخاب فچر مناسب"""
    if exchange.lower() == "binance":
        return BinanceFetcher()
    elif exchange.lower() == "kucoin":
        return KucoinFetcher()
    else:
        raise ValueError(f"صرافی {exchange} پشتیبانی نمی‌شود")


def save_candles_to_db(session: Session, candles: list) -> int:
    """ذخیره کندل‌ها در دیتابیس با جلوگیری از تکرار و شمارش دقیق"""
    saved_count = 0
    for candle in candles:
        exists = session.query(CryptoPrice).filter(
            CryptoPrice.coin_id == candle["coin_id"],
            CryptoPrice.timestamp == candle["timestamp"],
            CryptoPrice.timeframe == candle["timeframe"]
        ).first()

        if not exists:
            record = CryptoPrice(**candle)
            session.add(record)
            saved_count += 1

    try:
        session.commit()
        return saved_count
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"خطای دیتابیس: {str(e)}")
    except Exception as e:
        session.rollback()
        raise ValueError(f"خطا در ذخیره‌سازی: {str(e)}")