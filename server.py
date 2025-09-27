from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.database.models import Base, Coin
from src.api.coin_fetcher import CoinFetcher, save_coins_to_db

app = FastAPI(title="Crypto Pattern Detector API", version="1.0.0")

# اتصال به دیتابیس
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # ایجاد جدول‌ها اگر وجود ندارن
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/")
def read_root():
    return {"message": "Crypto Pattern Detector API - آماده برای تحلیل!"}

@app.post("/coins/fetch")
def fetch_and_save_coins():
    """Endpoint برای گرفتن و ذخیره لیست همه کوین‌ها از KuCoin"""
    db = SessionLocal()
    try:
        fetcher = CoinFetcher()
        coins = fetcher.fetch_all_coins()
        save_coins_to_db(db, coins)
        return {"status": "success", "saved_coins": len(coins), "total_unique": len(coins)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.get("/coins")
def get_all_coins():
    """Endpoint برای گرفتن لیست کوین‌های ذخیره‌شده"""
    db = SessionLocal()
    try:
        coins = db.query(Coin).all()
        return [{"symbol": c.symbol, "name": c.name, "base_currency": c.base_currency, "quote_currency": c.quote_currency, "status": c.status} for c in coins]
    finally:
        db.close()

@app.get("/algorithms")
def get_algorithms():
    """Endpoint برای گرفتن لیست الگوریتم‌های معمول رمزارزها"""
    algorithms = [
        {"name": "SHA-256", "description": "الگوریتم هشینگ مورد استفاده در بیتکوین و بسیاری رمزارزهای دیگر برای امنیت و ماینینگ.", "used_in": "Bitcoin, Bitcoin Cash"},
        {"name": "Scrypt", "description": "الگوریتم مقاوم در برابر ASIC برای ماینینگ سبک‌تر.", "used_in": "Litecoin, Dogecoin"},
        {"name": "Ethash", "description": "الگوریتم اثبات کار برای اتریوم (قبل از انتقال به PoS).", "used_in": "Ethereum (قدیمی), Ethereum Classic"},
        {"name": "CryptoNight", "description": "الگوریتم خصوصی برای رمزارزهای حریم خصوصی.", "used_in": "Monero, Bytecoin"},
        {"name": "X11", "description": "الگوریتم ترکیبی از 11 هش برای امنیت بیشتر.", "used_in": "Dash, PIVX"},
        {"name": "Proof of Work (PoW)", "description": "الگوریتم اجماع عمومی برای ماینینگ.", "used_in": "Bitcoin, Ethereum (قدیمی)"},
        {"name": "Proof of Stake (PoS)", "description": "الگوریتم اجماع انرژی‌کارآمد.", "used_in": "Ethereum (جدید), Cardano"}
    ]
    return {"algorithms": algorithms}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)