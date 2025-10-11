from sqlalchemy.orm import Session
from typing import Dict, List
from src.database.models import CryptoPrice, SupportResistanceLevel
from .base import BaseCalculator
import pandas as pd
from datetime import datetime

class SupportResistanceCalculator(BaseCalculator):
    """کلاس برای محاسبه و ذخیره سطوح حمایت و مقاومت بر اساس تکرار"""

    def calculate(self, session: Session, symbol: str, timeframe: str, num_candles: int = 100) -> Dict[str, List[float]]:
        """محاسبه سطوح بر اساس تعداد کندل‌های درخواستی"""
        records = session.query(CryptoPrice).filter(
            CryptoPrice.coin_id == symbol,
            CryptoPrice.timeframe == timeframe
        ).order_by(CryptoPrice.timestamp.desc()).limit(num_candles).all()

        if not records:
            return {"strong_levels": [], "weak_levels": []}

        df = pd.DataFrame([{
            'high': r.high,
            'low': r.low
        } for r in records])

        # جمع‌آوری همه high و low
        all_levels = pd.concat([df['high'], df['low']]).sort_values().reset_index(drop=True)

        # گروه‌بندی سطوح با تلورانس (مثلاً 0.5% از میانگین قیمت)
        tolerance = 0.005 * df['high'].mean()
        grouped = []
        current_group = [all_levels.iloc[0]]
        for level in all_levels.iloc[1:]:
            if level - current_group[-1] <= tolerance:
                current_group.append(level)
            else:
                mean_level = sum(current_group) / len(current_group)
                grouped.append((mean_level, len(current_group)))
                current_group = [level]
        if current_group:
            mean_level = sum(current_group) / len(current_group)
            grouped.append((mean_level, len(current_group)))

        # دسته‌بندی قوی و ضعیف (تکرار > 3 قوی)
        strong_levels = [level for level, count in grouped if count > 3]
        weak_levels = [level for level, count in grouped if 1 < count <= 3]

        # ذخیره سطوح
        calculated_at = datetime.now()
        for level in strong_levels:
            session.add(SupportResistanceLevel(
                symbol=symbol,
                timeframe=timeframe,
                level_type="resistance" if level in df['high'].values else "support",
                price=level,
                calculated_at=calculated_at,
                strength="strong"
            ))
        for level in weak_levels:
            session.add(SupportResistanceLevel(
                symbol=symbol,
                timeframe=timeframe,
                level_type="resistance" if level in df['high'].values else "support",
                price=level,
                calculated_at=calculated_at,
                strength="weak"
            ))
        session.commit()

        return {"strong_levels": strong_levels, "weak_levels": weak_levels}