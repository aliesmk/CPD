from sqlalchemy.orm import Session
from typing import Dict, List
from src.database.models import CryptoPrice, SupportResistanceLevel
from .base import BaseCalculator
import pandas as pd
from datetime import datetime, timedelta

class SupportResistanceCalculator(BaseCalculator):
    """کلاس برای محاسبه و ذخیره سطوح حمایت و مقاومت بر اساس داده‌های واقعی"""

    def calculate(self, session: Session, symbol: str, timeframe: str, num_candles: int = 100) -> Dict[str, List[float]]:
        """محاسبه سطوح بر اساس تعداد کندل‌های واقعی با فیلتر حجم و تکرار"""

        # دریافت داده‌ها بدون split یا فیلتر تاریخ
        records = session.query(CryptoPrice).filter(
            CryptoPrice.coin_id == symbol,
            CryptoPrice.timeframe == timeframe
        ).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()

        if not records or len(records) < 2:
            return {"strong_levels": [], "weak_levels": []}

        df = pd.DataFrame([{
            'high': r.high,
            'low': r.low,
            'volume': r.volume,
            'timestamp': r.timestamp
        } for r in records])

        # فقط مرتب‌سازی بر اساس زمان (بدون فیلتر تاریخ)
        df = df.sort_values(by="timestamp").reset_index(drop=True)

        # جمع‌آوری همه high و low
        all_levels = pd.concat([df['high'], df['low']]).sort_values().reset_index(drop=True)

        # گروه‌بندی سطوح با تلورانس کوچک‌تر (0.2% از میانگین قیمت)
        tolerance = 0.002 * df['high'].mean()
        grouped = []
        current_group = [all_levels.iloc[0]]

        for level in all_levels.iloc[1:]:
            if abs(level - current_group[-1]) <= tolerance:
                current_group.append(level)
            else:
                mean_level = sum(current_group) / len(current_group)
                grouped.append((mean_level, len(current_group)))
                current_group = [level]

        if current_group:
            mean_level = sum(current_group) / len(current_group)
            grouped.append((mean_level, len(current_group)))

        # فیلتر حجم (فقط سطوحی که حجم بالای میانگین دارن)
        df['volume_avg'] = df['volume'].rolling(window=15, min_periods=1).mean()
        valid_indices = df.index[df['volume'] > df['volume_avg']].tolist()
        filtered_grouped = [
            (level, count)
            for level, count in grouped
            if any(
                abs(level - df.loc[i, 'high']) < tolerance or abs(level - df.loc[i, 'low']) < tolerance
                for i in valid_indices
            )
        ]

        # دسته‌بندی قوی و ضعیف
        strong_levels = [level for level, count in filtered_grouped if count >= 4]  # حداقل 4 تکرار برای قوی
        weak_levels = [level for level, count in filtered_grouped if 2 <= count < 4]  # 2-3 تکرار برای ضعیف

        # محدود کردن تعداد (حداکثر 20 تا)
        strong_levels = sorted(strong_levels)[:50]
        weak_levels = sorted(weak_levels)[:50]

        # ذخیره سطوح
        calculated_at = datetime.now()
        for i, level in enumerate(strong_levels + weak_levels):
            micro_offset = timedelta(microseconds=i * 100)
            level_type = "resistance" if any(abs(level - h) < tolerance for h in df['high']) else "support"
            session.add(SupportResistanceLevel(
                symbol=symbol,
                timeframe=timeframe,
                level_type=level_type,
                price=float(level),
                calculated_at=calculated_at + micro_offset,
                strength="strong" if level in strong_levels else "weak"
            ))

        session.commit()

        return {"strong_levels": strong_levels, "weak_levels": weak_levels}
