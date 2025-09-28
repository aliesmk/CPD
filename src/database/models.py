from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint, Index

Base = declarative_base()

class CryptoPrice(Base):
    __tablename__ = 'crypto_prices'

    id = Column(Integer, primary_key=True)
    coin_id = Column(String, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    candle_type = Column(String, nullable=False)
    upper_shadow = Column(Float, nullable=False, server_default='0.0')
    lower_shadow = Column(Float, nullable=False, server_default='0.0')
    volume = Column(Float, nullable=False, server_default='0.0')
    timeframe = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('coin_id', 'timestamp', 'timeframe', name='uix_coin_timestamp_timeframe'),
        Index('idx_coin_timeframe', 'coin_id', 'timeframe'),
    )


class Coin(Base):
    __tablename__ = 'coins'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    base_currency = Column(String, nullable=False)
    quote_currency = Column(String, nullable=False)
    status = Column(String, default='tradable')

    __table_args__ = (
        UniqueConstraint('symbol', name='uix_symbol'),
    )