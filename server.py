from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.analysis.report_generator import ReportGenerator
from src.config import DATABASE_URL
from src.database.models import Base, Coin, Report, CryptoPrice
from src.api.coin_fetcher import CoinFetcher, save_coins_to_db
from src.api.factory import get_fetcher, save_candles_to_db
from src.analysis.pattern_factory import get_pattern_detector, AVAILABLE_PATTERNS, calculate_rsi, calculate_sma, \
    determine_trend
from datetime import datetime, timedelta
from typing import Optional
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


@app.post("/candles/fetch/{symbol}")
def fetch_and_save_candles(symbol: str, interval: str = "1h", limit: int = 1500):
    """Endpoint برای گرفتن و ذخیره کندل‌ها برای یک کوین خاص"""
    db = SessionLocal()
    try:
        coin = db.query(Coin).filter(Coin.symbol == symbol).first()
        if not coin:
            raise HTTPException(status_code=404, detail=f"کوین {symbol} پیدا نشد")

        fetcher = get_fetcher("kucoin")
        candles = fetcher.fetch_candles(symbol=symbol, interval=interval, limit=limit)
        saved_count = save_candles_to_db(db, candles)
        return {"status": "success", "symbol": symbol, "interval": interval, "saved_candles": saved_count}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطای غیرمنتظره: {str(e)}")
    finally:
        db.close()


@app.get("/patterns/detect/{symbol}/{interval}")
def detect_patterns(symbol: str, interval: str = "1h"):
    """Endpoint برای تشخیص الگوهای تکنیکال برای یک کوین و تایم‌فریم خاص"""
    db = SessionLocal()
    try:
        coin = db.query(Coin).filter(Coin.symbol == symbol).first()
        if not coin:
            raise HTTPException(status_code=404, detail=f"کوین {symbol} پیدا نشد")

        patterns = ["gartley", "butterfly", "head_and_shoulders", "double_top_bottom", "ascending_triangle",
                    "bullish_engulfing"]
        results = {}
        for pattern in patterns:
            detector = get_pattern_detector(pattern)
            results[pattern] = detector.detect(db, coin.base_currency, num_candles=100)

        return {"status": "success", "symbol": symbol, "interval": interval, "patterns_detected": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا: {str(e)}")
    finally:
        db.close()


@app.get("/analysis/report/{symbol}")
def get_pattern_report(symbol: str, timeframe: str = "1h", days_back: int = 7, pattern: str = "all"):
    """Endpoint برای گزارش تحلیل الگوها برای رمزارز، تایم‌فریم، بازه زمانی، و الگو"""
    db = SessionLocal()
    try:
        generator = ReportGenerator(db)
        report = generator.generate_report(symbol, timeframe, days_back, pattern)
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)