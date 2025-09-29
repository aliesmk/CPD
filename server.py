from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
    db = SessionLocal()
    try:
        coin = db.query(Coin).filter(Coin.symbol == symbol).first()
        if not coin:
            raise HTTPException(status_code=404, detail=f"کوین {symbol} پیدا نشد")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        report_query = db.query(Report).filter(
            Report.symbol == symbol,
            Report.timeframe == timeframe,
            Report.start_date == start_date,
            Report.end_date == end_date,
            Report.pattern == pattern
        ).first()

        if report_query:
            return report_query.report_data

        records = db.query(CryptoPrice).filter(
            CryptoPrice.coin_id == coin.base_currency,
            CryptoPrice.timeframe == timeframe,
            CryptoPrice.timestamp >= start_date,
            CryptoPrice.timestamp <= end_date
        ).order_by(CryptoPrice.timestamp).all()

        if not records:
            raise HTTPException(status_code=404, detail="داده‌ای برای این بازه پیدا نشد")

        patterns_list = AVAILABLE_PATTERNS if pattern == "all" else [pattern]
        report = {}
        for p in patterns_list:
            detector = get_pattern_detector(p)
            detections = []
            for i in range(1, len(records)):
                # گرفتن num_candles تا موقعیت i
                result = detector.detect(db, coin.base_currency, num_candles=i + 1)
                pattern_type = None
                if isinstance(result, dict):
                    if result["bullish"]:
                        pattern_type = "bullish"
                    elif result["bearish"]:
                        pattern_type = "bearish"
                elif result:
                    pattern_type = p

                if pattern_type:
                    detail = {
                        "timestamp": records[i].timestamp.isoformat(),
                        "rsi": calculate_rsi(db, coin.base_currency, timeframe=timeframe, timestamp=records[i].timestamp),
                        "sma_20": calculate_sma(db, coin.base_currency, timeframe, 20, records[i].timestamp),
                        "sma_50": calculate_sma(db, coin.base_currency, timeframe, 50, records[i].timestamp),
                        "volume": records[i].volume,
                        "trend_before": determine_trend(db, coin.base_currency, timeframe, records[i].timestamp, num_candles=5),
                        "trend_after": determine_trend(db, coin.base_currency, timeframe, records[i].timestamp + timedelta(hours=1), num_candles=5),
                        "success": False,
                        "pattern_type": pattern_type
                    }
                    if i + 5 < len(records):
                        start_close = records[i].close
                        end_close = records[i + 5].close
                        detail["success"] = (
                            (end_close > start_close and ("bullish" in pattern_type or "head_and_shoulders" not in pattern_type)) or
                            (end_close < start_close and ("bearish" in pattern_type or "head_and_shoulders" in pattern_type))
                        )
                    detections.append(detail)

            count = len(detections)
            success_count = sum(1 for d in detections if d["success"])
            success_rate = (success_count / count * 100) if count > 0 else 0
            failure_rate = 100 - success_rate
            current_detection = detector.detect(db, coin.base_currency, num_candles=len(records))

            report[p] = {
                "count": count,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
                "current_detection": current_detection if isinstance(current_detection, bool) else current_detection,
                "details": detections
            }

        new_report = Report(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            pattern=pattern,
            report_data=report
        )
        db.add(new_report)
        db.commit()

        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا: {str(e)}")
    finally:
        db.close()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)