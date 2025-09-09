import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DEFAULT_EXCHANGE = os.getenv("DEFAULT_EXCHANGE", "kucoin")
KUCOIN_API_URL = os.getenv("KUCOIN_API_URL", "https://api.kucoin.com")
BINANCE_API_URL = os.getenv("BINANCE_API_URL", "https://api.binance.com")