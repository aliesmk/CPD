import requests
from datetime import datetime
from src.config import BINANCE_API_URL
from .base import BaseFetcher

class BinanceFetcher(BaseFetcher):
   def __init__(self, api_url: str = BINANCE_API_URL):
       self.api_url = api_url

   def fetch_candles(self, symbol: str, interval: str, limit: int = 100) -> list:
       endpoint = f"{self.api_url}/api/v3/klines"
       params = {
           "symbol": symbol.replace("/", ""),  # مثلاً BTC/USDT -> BTCUSDT
           "interval": interval,  # مثل 1h, 4h, 1d
           "limit": limit
       }
       response = requests.get(endpoint, params=params)
       response.raise_for_status()
       candles = response.json()

       result = []
       for candle in candles:
           timestamp = datetime.fromtimestamp(candle[0] / 1000)
           open_price = float(candle[1])
           high_price = float(candle[2])
           low_price = float(candle[3])
           close_price = float(candle[4])
           volume = float(candle[5])
           currency = symbol.split("/")[1] if "/" in symbol else "USDT"
           price_diff = abs(close_price - open_price) / open_price * 100
           if price_diff < 0.1:
               candle_type = "neutral"
           else:
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