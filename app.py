from src.api.client import CoinGeckoClient
from src.storage.file_manager import FileManager
from src.storage.database import DatabaseManager


def main():
    client = CoinGeckoClient()
    data = client.get_ohlc_data(coin_id='bitcoin', vs_currency='usd', days=365)

    if data is not None:
        file_manager = FileManager()
        file_manager.save_to_csv(data, 'bitcoin_ohlc.csv')

        db = DatabaseManager()
        prices = db.get_price_data(coin_id='bitcoin')
        print(f"تعداد رکوردها در دیتابیس: {len(prices)}")
        for price in prices[:5]:
            print(
                f"{price.timestamp}: Open={price.open}, High={price.high}, Low={price.low}, Close={price.close}, Type={price.candle_type}")


if __name__ == "__main__":
    main()