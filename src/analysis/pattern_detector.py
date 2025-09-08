from src.storage.database import DatabaseManager
from src.analysis.indicators import calculate_shadows
import pandas as pd


class PatternDetector:
    def __init__(self):
        self.pattern_functions = {
            'bullish_engulfing': self.detect_bullish_engulfing,
            'bearish_engulfing': self.detect_bearish_engulfing,
            # بعداً الگوهای دیگه اضافه
        }

    def detect_specific_pattern(self, df, pattern_name):
        """
        تشخیص یک الگوی خاص
        """
        if pattern_name in self.pattern_functions:
            return self.pattern_functions[pattern_name](df)
        return []

    def detect_patterns(self, coin_id, start_date=None, end_date=None, patterns=None):
        """
        تشخیص همه الگوها یا الگوهای خاص
        :param patterns: لیست الگوها (مثل ['bullish_engulfing']) یا None برای همه
        """
        # ... (بقیه کد بدون تغییر)

        results = {}
        if patterns is None:
            patterns = list(self.pattern_functions.keys())

        for pattern in patterns:
            results[pattern] = self.detect_specific_pattern(df, pattern)

        # چاپ نتایج
        for pattern, indices in results.items():
            if indices:
                print(f"الگوی {pattern} در اندیس‌های زیر پیدا شد:")
                for idx in indices:
                    print(
                        f" - {df.iloc[idx]['timestamp']}: Trend={df.iloc[idx]['trend']}, Open={df.iloc[idx]['open']}, Close={df.iloc[idx]['close']}")

        return results

    def detect_trend(self, df, period=50):
        """
        تشخیص روند کلی با SMA
        :param period: تعداد کندل‌ها برای SMA
        :return: روند برای هر کندل ('up', 'down', 'neutral')
        """
        df['sma'] = talib.SMA(df['close'], timeperiod=period)
        df['trend'] = 'neutral'
        df.loc[df['close'] > df['sma'], 'trend'] = 'up'
        df.loc[df['close'] < df['sma'], 'trend'] = 'down'
        return df['trend']


    def detect_bullish_engulfing(self, df):
        """
        تشخیص الگوی Bullish Engulfing
        :param df: DataFrame با ستون‌های open, high, low, close
        :return: لیست اندیس‌هایی که الگو پیدا شده
        """
        patterns = []
        for i in range(1, len(df)):
            prev_candle = df.iloc[i - 1]
            curr_candle = df.iloc[i]

            # شرایط Bullish Engulfing
            is_prev_bearish = prev_candle['close'] < prev_candle['open']
            is_curr_bullish = curr_candle['close'] > curr_candle['open']
            is_engulfing = (
                    curr_candle['open'] <= prev_candle['close'] and
                    curr_candle['close'] >= prev_candle['open']
            )

            if is_prev_bearish and is_curr_bullish and is_engulfing:
                patterns.append(i)

        return patterns

    def detect_bearish_engulfing(self, df):
        """
        تشخیص الگوی Bearish Engulfing
        :param df: DataFrame با ستون‌های open, high, low, close
        :return: لیست اندیس‌هایی که الگو پیدا شده
        """
        patterns = []
        for i in range(1, len(df)):
            prev_candle = df.iloc[i - 1]
            curr_candle = df.iloc[i]

            # شرایط Bearish Engulfing
            is_prev_bullish = prev_candle['close'] > prev_candle['open']
            is_curr_bearish = curr_candle['close'] < curr_candle['open']
            is_engulfing = (
                    curr_candle['open'] >= prev_candle['close'] and
                    curr_candle['close'] <= prev_candle['open']
            )

            if is_prev_bullish and is_curr_bearish and is_engulfing:
                patterns.append(i)

        return patterns

    def detect_patterns(self, coin_id, start_date=None, end_date=None, patterns=None):

        """
        تشخیص همه الگوها برای یک رمزارز
        :return: دیکشنری با الگوها و اندیس‌های پیدا شده
        """
        # گرفتن داده‌ها از دیتابیس

        df = calculate_shadows(df)
        prices = self.db.get_price_data(coin_id, start_date, end_date)
        if not prices:
            print(f"هیچ داده‌ای برای {coin_id} پیدا نشد.")
            return {}

        # تبدیل به DataFrame
        df = pd.DataFrame([
            {
                'timestamp': price.timestamp,
                'open': price.open,
                'high': price.high,
                'low': price.low,
                'close': price.close,
                'candle_type': price.candle_type
            }
            for price in prices
        ])

        # تشخیص الگوها
        results = {
            'bullish_engulfing': self.detect_bullish_engulfing(df),
            'bearish_engulfing': self.detect_bearish_engulfing(df)
        }

        # تشخیص روند
        df['trend'] = self.detect_trend(df)

        # حالا الگوها رو با روند فیلتر می‌کنیم (مثلاً Bullish Engulfing تو روند down)
        results = {
            'bullish_engulfing': self.detect_bullish_engulfing(df),
            'bearish_engulfing': self.detect_bearish_engulfing(df)
        }

        # چاپ نتایج با روند
        for pattern, indices in results.items():
            if indices:
                print(f"الگوی {pattern} در اندیس‌های زیر پیدا شد:")
                for idx in indices:
                    print(
                        f" - {df.iloc[idx]['timestamp']}: Trend={df.iloc[idx]['trend']}, Open={df.iloc[idx]['open']}, Close={df.iloc[idx]['close']}")

        return results