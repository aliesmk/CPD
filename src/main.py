from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.api.factory import get_fetcher, save_candles_to_db
from src.analysis.pattern_factory import get_pattern_detector, calculate_rsi, calculate_fibonacci_levels

# اتصال به دیتابیس
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# گرفتن داده‌ها از KuCoin
fetcher = get_fetcher("kucoin")
candles = fetcher.fetch_candles(symbol="BTC/USDT", interval="1h", limit=50)

# ذخیره در دیتابیس
save_candles_to_db(session, candles)

# چاپ رکوردها برای تست
from src.database.models import CryptoPrice
records = session.query(CryptoPrice).all()
for record in records:
    print(record.coin_id, record.timestamp, record.candle_type, record.open, record.close, record.volume)

# محاسبه RSI
rsi = calculate_rsi(session, "BTC")
print(f"RSI فعلی برای BTC: {rsi}")

# محاسبه سطوح فیبوناچی
fib_levels = calculate_fibonacci_levels(session, "BTC")
print("سطوح فیبوناچی برای BTC:")
for level, price in fib_levels.items():
    print(f"{level}: {price}")

# تست الگوهای هارمونیک
gartley_detector = get_pattern_detector("gartley")
butterfly_detector = get_pattern_detector("butterfly")

if gartley_detector.detect(session, "BTC"):
    print("الگوی Gartley شناسایی شد!")
else:
    print("الگوی Gartley پیدا نشد.")

if butterfly_detector.detect(session, "BTC"):
    print("الگوی Butterfly شناسایی شد!")
else:
    print("الگوی Butterfly پیدا نشد.")

session.close()

#  add RSI and Fibonacci
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.config import DATABASE_URL
# from src.api.factory import get_fetcher, save_candles_to_db
# from src.analysis.patterns import calculate_rsi, calculate_fibonacci_levels
#
# # اتصال به دیتابیس
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()
#
# # گرفتن داده‌ها از KuCoin
# fetcher = get_fetcher("kucoin")
# candles = fetcher.fetch_candles(symbol="BTC/USDT", interval="1h", limit=10)
#
# # ذخیره در دیتابیس
# save_candles_to_db(session, candles)
#
# # چاپ رکوردها برای تست
# from src.database.models import CryptoPrice
# records = session.query(CryptoPrice).all()
# for record in records:
#     print(record.coin_id, record.timestamp, record.candle_type, record.open, record.close, record.volume)
#
# # محاسبه RSI
# rsi = calculate_rsi(session, "BTC")
# print(f"RSI فعلی برای BTC: {rsi}")
#
# # محاسبه سطوح فیبوناچی
# fib_levels = calculate_fibonacci_levels(session, "BTC")
# print("سطوح فیبوناچی برای BTC:")
# for level, price in fib_levels.items():
#     print(f"{level}: {price}")
#
# session.close()

# #  GET KUKOIN DATA
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.config import DATABASE_URL
# from src.api.factory import get_fetcher, save_candles_to_db
#
# # اتصال به دیتابیس
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()
#
# # گرفتن داده‌ها از KuCoin
# fetcher = get_fetcher("kucoin")
# candles = fetcher.fetch_candles(symbol="BTC/USDT", interval="1h", limit=10)
#
# # ذخیره در دیتابیس
# save_candles_to_db(session, candles)
#
# # چاپ رکوردها برای تست
# from src.database.models import CryptoPrice
# records = session.query(CryptoPrice).all()
# for record in records:
#     print(record.coin_id, record.timestamp, record.candle_type, record.open, record.close)
#
# session.close()



# GET DATA FROM BINANCE
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.config import DATABASE_URL
# from src.api.fetchers import get_fetcher, save_candles_to_db
#
# # اتصال به دیتابیس
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()
#
# # گرفتن داده‌ها از Binance
# fetcher = get_fetcher("binance")
# candles = fetcher.fetch_candles(symbol="BTC/USDT", interval="1h", limit=10)
#
# # ذخیره در دیتابیس
# save_candles_to_db(session, candles)
#
# # چاپ رکوردها برای تست
# from src.database.models import CryptoPrice
# records = session.query(CryptoPrice).all()
# for record in records:
#     print(record.coin_id, record.timestamp, record.candle_type, record.open, record.close)
#
# session.close()


# get first data
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.config import DATABASE_URL
# from src.database.models import Base, CryptoPrice
# from datetime import datetime
#
# engine = create_engine(DATABASE_URL)
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()
#
# # اضافه کردن رکورد تست
# test_record = CryptoPrice(
#    coin_id="BTC",
#    open=50000.0,
#    high=51000.0,
#    low=49000.0,
#    close=50500.0,
#    currency="USDT",
#    timestamp=datetime.now(),
#    candle_type="bullish",
#    upper_shadow=1000.0,
#    lower_shadow=500.0
# )
# session.add(test_record)
# session.commit()
#
# # چاپ رکوردها
# records = session.query(CryptoPrice).all()
# for record in records:
#    print(record.coin_id, record.timestamp, record.candle_type)
#
# session.close()