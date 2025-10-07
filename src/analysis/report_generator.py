import json
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.database.models import Coin, Report, CryptoPrice
from src.analysis.pattern_factory import get_pattern_detector, AVAILABLE_PATTERNS, calculate_rsi, calculate_sma, determine_trend
from fastapi import HTTPException
import numpy as np
import pandas as pd

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.int64, np.int32, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, float)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        return super().default(obj)

class ReportGenerator:
    """کلاس برای تولید گزارش‌های تحلیل الگوها"""

    def __init__(self, db: Session):
        self.db = db

    def _convert_numpy_types(self, obj):
        """تبدیل بازگشتی انواع numpy به انواع استاندارد پایتون"""
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj

    def generate_report(self, symbol: str, timeframe: str, days_back: int, pattern: str) -> Dict:
        """تولید گزارش برای الگوهای مشخص‌شده"""
        coin = self.db.query(Coin).filter(Coin.symbol == symbol).first()
        if not coin:
            raise HTTPException(status_code=404, detail=f"کوین {symbol} پیدا نشد")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # چک گزارش ذخیره‌شده
        report_query = self.db.query(Report).filter(
            Report.symbol == symbol,
            Report.timeframe == timeframe,
            Report.start_date == start_date,
            Report.end_date == end_date,
            Report.pattern == pattern
        ).first()

        if report_query:
            return json.loads(report_query.report_data)

        # گرفتن داده‌های کندل
        records = self.db.query(CryptoPrice).filter(
            CryptoPrice.coin_id == coin.symbol,
            CryptoPrice.timeframe == timeframe,
            CryptoPrice.timestamp >= start_date,
            CryptoPrice.timestamp <= end_date
        ).order_by(CryptoPrice.timestamp.asc()).all()

        if not records:
            raise HTTPException(status_code=404, detail="داده‌ای برای این بازه پیدا نشد")

        patterns_list = AVAILABLE_PATTERNS if pattern == "all" else [pattern]
        report = {}

        for p in patterns_list:
            detector = get_pattern_detector(p)
            detections = []
            success_count = 0

            pattern_detections = detector.detect(self.db, coin.symbol, num_candles=len(records))
            for d in pattern_detections:
                i = d["position"]
                if i >= len(records):
                    continue
                detail = self._create_detection_detail(records, i, coin.symbol, timeframe, p, d)
                if detail["success"]:
                    success_count += 1
                detections.append(detail)

            count = len(detections)
            success_rate = (success_count / count * 100) if count > 0 else 0
            failure_rate = 100 - success_rate

            # گرفتن تشخیص فعلی
            current_detection_list = detector.detect(self.db, coin.symbol, num_candles=len(records))

            # تبدیل current_detection به دیکشنری سریالایزپذیر
            current_dict = {}
            if current_detection_list and isinstance(current_detection_list, list):
                last_detection = current_detection_list[-1] if current_detection_list else {}
                pattern_type = "bullish" if last_detection.get("detected", {}).get("bullish", False) else "bearish" if last_detection.get("detected", {}).get("bearish", False) else p
                trend_before = str(last_detection.get("trend_before", "unknown"))
                current_dict = {
                    "detected": {
                        "bearish": bool(last_detection.get("detected", {}).get("bearish", False)),
                        "bullish": bool(last_detection.get("detected", {}).get("bullish", False))
                    },
                    "trend_before": trend_before,
                    "predicted_trend": str(detector._get_trend(
                        self.db, coin.symbol, timeframe, records[-1].timestamp, num_candles=5, is_future=True,
                        pattern_type=pattern_type, detections=detections
                    ))
                }
            else:
                trend_before = str(detector._get_trend(self.db, coin.symbol, timeframe, records[-1].timestamp, num_candles=5) if records else "unknown")
                current_dict = {
                    "detected": {"bearish": False, "bullish": False},
                    "trend_before": trend_before,
                    "predicted_trend": str(detector._get_trend(
                        self.db, coin.symbol, timeframe, records[-1].timestamp, num_candles=5, is_future=True,
                        pattern_type=p, detections=detections
                    )) if records else "unknown"
                }

            report[p] = {
                "count": int(count),
                "success_rate": float(success_rate),
                "failure_rate": float(failure_rate),
                "current_detection": current_dict,
                "details": detections
            }

        # تبدیل تمام انواع numpy قبل از ذخیره و بازگشت
        report_clean = self._convert_numpy_types(report)

        # ذخیره گزارش در دیتابیس
        new_report = Report(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            pattern=pattern,
            report_data=json.dumps(report_clean, cls=NumpyEncoder, ensure_ascii=False)
        )
        self.db.add(new_report)
        self.db.commit()

        return report_clean

    def _create_detection_detail(self, records: List[CryptoPrice], i: int, coin_id: str, timeframe: str, pattern: str, detection: Optional[Dict] = None) -> Dict:
        """ایجاد جزئیات برای یک تشخیص الگو"""
        rsi_value = calculate_rsi(self.db, coin_id, timeframe, records[i].timestamp)
        sma_20_value = calculate_sma(self.db, coin_id, timeframe, 20, records[i].timestamp)
        sma_50_value = calculate_sma(self.db, coin_id, timeframe, 50, records[i].timestamp)

        if detection and isinstance(detection.get("detected"), dict):
            pattern_type = "bullish" if detection["detected"].get("bullish") else "bearish"
        else:
            pattern_type = pattern

        detail = {
            "pattern": str(pattern),
            "pattern_type": str(pattern_type),
            "timestamp": records[i].timestamp.isoformat(),
            "rsi": float(rsi_value) if rsi_value is not None else 0.0,
            "sma_20": float(sma_20_value) if sma_20_value is not None else 0.0,
            "sma_50": float(sma_50_value) if sma_50_value is not None else 0.0,
            "volume": float(records[i].volume),
            "trend_before": str(detection.get("trend_before", "unknown")) if detection else "unknown",
            "trend_after": str(detection.get("predicted_trend", "unknown")) if detection else "unknown",
            "success": False
        }

        if i + 5 < len(records):
            start_close = float(records[i].close)
            end_close = float(records[i + 5].close)

            if "bullish" in pattern_type.lower():
                detail["success"] = bool(end_close > start_close)
            elif "bearish" in pattern_type.lower():
                detail["success"] = bool(end_close < start_close)
            else:
                detail["success"] = bool(end_close > start_close)

        detail["success"] = int(detail["success"])

        return detail