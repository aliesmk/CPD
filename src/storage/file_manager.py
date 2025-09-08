# src/storage/file_manager.py
import pandas as pd
import os

class FileManager:
    def __init__(self, data_dir="../data/raw"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def save_to_csv(self, df, filename):
        """
        ذخیره DataFrame به فایل CSV
        :param df: DataFrame داده‌ها
        :param filename: نام فایل (مثل bitcoin_prices.csv)
        """
        file_path = os.path.join(self.data_dir, filename)
        df.to_csv(file_path, index=False)
        print(f"داده‌ها در {file_path} ذخیره شد")