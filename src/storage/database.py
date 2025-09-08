from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.storage.models.crypto_price import CryptoPrice
from sqlalchemy.dialects.postgresql import insert
import os
from dotenv import load_dotenv

load_dotenv()


def get_candle_type(open_price, close_price, threshold=0.0001):
    if abs(close_price - open_price) / open_price < threshold:
        return 'doji'
    return 'bullish' if close_price > open_price else 'bearish'


class DatabaseManager:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = os.getenv('DB_URL',)
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def save_price_data_bulk(self, prices_data):
        session = self.Session()
        try:
            for data in prices_data:
                data['candle_type'] = get_candle_type(data['open'], data['close'])

            stmt = insert(CryptoPrice).values(prices_data).on_conflict_do_nothing(
                index_elements=['coin_id', 'timestamp']
            )
            result = session.execute(stmt)
            session.commit()
            saved_count = result.rowcount
            print(f"{saved_count} رکورد جدید ذخیره شد.")
            return saved_count
        except Exception as e:
            session.rollback()
            print(f"خطا در ذخیره داده‌ها: {e}")
            return 0
        finally:
            session.close()

    def get_price_data(self, coin_id, start_date=None, end_date=None):
        session = self.Session()
        try:
            query = session.query(CryptoPrice).filter(CryptoPrice.coin_id == coin_id)
            if start_date:
                query = query.filter(CryptoPrice.timestamp >= start_date)
            if end_date:
                query = query.filter(CryptoPrice.timestamp <= end_date)
            return query.all()
        finally:
            session.close()