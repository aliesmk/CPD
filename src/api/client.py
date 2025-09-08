import requests
import pandas as pd
from datetime import datetime, timedelta
from src.storage.database import DatabaseManager


class CoinGeckoClient:
    def __init__(self, base_url="https://api.coingecko.com/api/v3"):
        self.base_url = base_url
        self.db = DatabaseManager()

    def get_ohlc_data(self, coin_id='bitcoin', vs_currency='usd', days=30):
        url = f"{self.base_url}/coins/{coin_id}/ohlc?vs_currency={vs_currency}&days={days}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            prices_data = [
                {
                    'coin_id': coin_id,
                    'open': price_entry[1],
                    'high': price_entry[2],
                    'low': price_entry[3],
                    'close': price_entry[4],
                    'currency': vs_currency,
                    'timestamp': pd.to_datetime(price_entry[0], unit='ms')
                }
                for price_entry in data
            ]

            saved_count = self.db.save_price_data_bulk(prices_data)

            df = pd.DataFrame(
                data,
                columns=['timestamp', 'open', 'high', 'low', 'close']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['candle_type'] = df.apply(
                lambda row: 'bullish' if row['close'] > row['open']
                else 'bearish' if row['close'] < row['open'] else 'doji',
                axis=1
            )
            return df

        except requests.exceptions.RequestException as e:
            print(f"خطا در گرفتن داده‌ها: {e}")
            return None