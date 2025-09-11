import requests
from datetime import datetime
from src.config import KUCOIN_API_URL
from .base import BaseFetcher

class KucoinFetcher(BaseFetcher):

   def __init__(self, api_url: str = KUCOIN_API_URL):
       self.api_url = api_url

   def fetch_candles(self, symbol: str, interval: str, limit: int = 100) -> list:

       interval_map = {
           "1m": "1min", "3m": "3min", "5m": "5min", "15m": "15min",
           "30m": "30min", "1h": "1hour", "2h": "2hour", "4h": "4hour",
           "6h": "6hour", "8h": "8hour", "12h": "12hour", "1d": "1day"
       }
       kucoin_interval = interval_map.get(interval, "1hour")
       endpoint = f"{self.api_url}/api/v1/market/candles"
       params = {
           "symbol": symbol.replace("/", "-"),  # مثلاً BTC/USDT -> BTC-USDT
           "type": kucoin_interval,
           "limit": limit
       }
       response = requests.get(endpoint, params=params)
       response.raise_for_status()
       data = response.json()
       if not data.get("code") == "200000":
           raise ValueError(f"خطای API KuCoin: {data.get('msg')}")
       candles = data.get("data", [])

       result = []
       for candle in candles:
           timestamp = datetime.fromtimestamp(int(candle[0]))
           open_price = float(candle[1])
           close_price = float(candle[2])
           high_price = float(candle[3])
           low_price = float(candle[4])
           volume = float(candle[6])
           currency = symbol.split("/")[1] if "/" in symbol else "USDT"
           candle_type = "bullish" if close_price > open_price else "bearish"
           upper_shadow = high_price - max(open_price, close_price)
           lower_shadow = min(open_price, close_price) - low_price

           result.append({
               "coin_id": symbol.split("/")[0],
               "open": open_price,
               "high": high_price,
               "low": low_price,
               "close": close_price,
               "currency": currency,
               "timestamp": timestamp,
               "candle_type": candle_type,
               "upper_shadow": upper_shadow,
               "lower_shadow": lower_shadow,
               "volume": volume
           })
       return result