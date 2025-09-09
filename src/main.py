from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.database.models import Base, CryptoPrice
from datetime import datetime

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# اضافه کردن رکورد تست
test_record = CryptoPrice(
   coin_id="BTC",
   open=50000.0,
   high=51000.0,
   low=49000.0,
   close=50500.0,
   currency="USDT",
   timestamp=datetime.now(),
   candle_type="bullish",
   upper_shadow=1000.0,
   lower_shadow=500.0
)
session.add(test_record)
session.commit()

# چاپ رکوردها
records = session.query(CryptoPrice).all()
for record in records:
   print(record.coin_id, record.timestamp, record.candle_type)

session.close()