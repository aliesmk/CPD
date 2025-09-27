import requests
from src.config import KUCOIN_API_URL
from src.database.models import Coin
from sqlalchemy.orm import Session


class CoinFetcher:
    """فچر برای گرفتن لیست کوین‌ها از KuCoin"""

    def __init__(self, api_url: str = KUCOIN_API_URL):
        self.api_url = api_url

    def fetch_all_coins(self) -> list:
        """گرفتن لیست همه کوین‌ها از KuCoin"""
        endpoint = f"{self.api_url}/api/v1/symbols"
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        if not data.get("code") == "200000":
            raise ValueError(f"خطای API KuCoin: {data.get('msg')}")

        coins = data.get("data", [])
        result = []
        for coin in coins:
            if coin.get("isOpen", True):  # فقط کوین‌های فعال
                result.append({
                    "symbol": coin["symbol"],  # مثل BTC-USDT
                    "name": coin["name"],  # مثل BTC-USDT
                    "base_currency": coin["baseCurrency"],  # BTC
                    "quote_currency": coin["quoteCurrency"],  # USDT
                    "status": coin["enableTrading"] and "tradable" or "suspended"
                })
        return result


def save_coins_to_db(session: Session, coins: list):
    """ذخیره کوین‌ها در دیتابیس با جلوگیری از تکرار"""
    for coin in coins:
        # چک کردن وجود رکورد با symbol
        exists = session.query(Coin).filter(Coin.symbol == coin["symbol"]).first()

        if not exists:
            record = Coin(**coin)
            session.add(record)
        # اگه وجود داره، skip می‌کنیم (یا آپدیت کن اگه لازم)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"خطا در ذخیره‌سازی کوین‌ها: {e}")