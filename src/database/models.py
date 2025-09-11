from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint

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

    __table_args__ = (
        UniqueConstraint('coin_id', 'timestamp', name='uix_coin_timestamp'),
    )