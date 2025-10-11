from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
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


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    pattern = Column(String, nullable=False)
    report_data = Column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'start_date', 'end_date', 'pattern', name='uix_report_key'),
    )

class SupportResistanceLevel(Base):
    __tablename__ = 'support_resistance_levels'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    level_type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    calculated_at = Column(DateTime, nullable=False)
    strength = Column(String, nullable=False, default='weak')

    # __table_args__ = (
    #     UniqueConstraint('symbol', 'timeframe', 'level_type', 'calculated_at', name='uix_sr_level'),
    #     Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
    # )