import requests
from datetime import datetime, timedelta
from src.config import KUCOIN_API_URL
from .base import BaseFetcher


class KucoinFetcher(BaseFetcher):
    def __init__(self, api_url: str = KUCOIN_API_URL):
        self.api_url = api_url

    def fetch_candles(self, symbol: str, interval: str, limit: int = 1500) -> list:
        interval_map = {
            "1m": "1min", "3m": "3min", "5m": "5min", "15m": "15min",
            "30m": "30min", "1h": "1hour", "2h": "2hour", "4h": "4hour",
            "6h": "6hour", "8h": "8hour", "12h": "12hour", "1d": "1day"
        }
        kucoin_interval = interval_map.get(interval, "1hour")

        interval_seconds = {
            "1min": 60, "3min": 180, "5min": 300, "15min": 900,
            "30min": 1800, "1hour": 3600, "2hour": 7200, "4hour": 14400,
            "6hour": 21600, "8hour": 28800, "12hour": 43200, "1day": 86400
        }.get(kucoin_interval, 3600)

        endpoint = f"{self.api_url}/api/v1/market/candles"
        result = []
        end_time = int(datetime.now().timestamp())
        candles_per_request = 500
        requests_needed = (limit + candles_per_request - 1) // candles_per_request

        print(f"شروع گرفتن {limit} کندل با {requests_needed} درخواست...")

        for req_num in range(requests_needed):
            start_time = end_time - (candles_per_request * interval_seconds)
            params = {
                "symbol": symbol.replace("/", "-"),
                "type": kucoin_interval,
                "startAt": start_time,
                "endAt": end_time
            }
            try:
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                if not data.get("code") == "200000":
                    raise ValueError(f"خطای API KuCoin: {data.get('msg')}")
                candles = data.get("data", [])
                print(f"درخواست {req_num + 1}: {len(candles)} کندل گرفته شد")
                result.extend(candles)
                end_time = start_time - 1
                if len(candles) < candles_per_request:
                    break
            except Exception as e:
                print(f"خطا در درخواست {req_num + 1}: {str(e)}")
                break

        print(f"کل کندل‌های گرفته‌شده: {len(result)}")

        formatted_candles = []
        for candle in result:
            timestamp = datetime.fromtimestamp(int(candle[0]))
            open_price = float(candle[1])
            close_price = float(candle[2])
            high_price = float(candle[3])
            low_price = float(candle[4])
            volume = float(candle[6])
            currency = symbol.split("/")[1] if "/" in symbol else "USDT"
            price_diff = abs(close_price - open_price) / open_price * 100
            candle_type = "neutral" if price_diff < 0.1 else ("bullish" if close_price > open_price else "bearish")
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price

            formatted_candles.append({
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
                "volume": volume,
                "timeframe": interval
            })

        return formatted_candles[:limit]