class BaseFetcher:
    def fetch_candles(self, symbol: str, interval: str, limit: int = 100) -> list:
        raise NotImplementedError("این متد باید در زیرکلاس‌ها پیاده‌سازی شود")