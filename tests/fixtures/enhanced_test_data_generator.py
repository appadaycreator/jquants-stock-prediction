"""
強化されたテストデータジェネレーター
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random


class EnhancedTestDataGenerator:
    """強化されたテストデータジェネレーター"""
    
    def __init__(self, seed: int = 42):
        """初期化"""
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
    
    def generate_stock_data(
        self,
        start_date: str = "2023-01-01",
        end_date: str = "2023-12-31",
        num_stocks: int = 5,
        price_range: Tuple[float, float] = (50.0, 200.0),
        volume_range: Tuple[int, int] = (100000, 10000000),
        include_weekends: bool = False,
        add_noise: bool = True,
        trend_strength: float = 0.1
    ) -> pd.DataFrame:
        """株価データを生成"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        dates = []
        current = start
        while current <= end:
            if include_weekends or current.weekday() < 5:  # 月曜日=0, 日曜日=6
                dates.append(current.strftime("%Y%m%d"))
            current += timedelta(days=1)
        
        data = []
        for stock_id in range(num_stocks):
            base_price = np.random.uniform(price_range[0], price_range[1])
            trend = np.random.uniform(-trend_strength, trend_strength)
            
            for i, date in enumerate(dates):
                # トレンドを適用
                price = base_price * (1 + trend * i / len(dates))
                
                # ノイズを追加
                if add_noise:
                    price *= np.random.uniform(0.95, 1.05)
                
                # OHLCデータを生成
                open_price = price * np.random.uniform(0.98, 1.02)
                close_price = price * np.random.uniform(0.98, 1.02)
                high_price = max(open_price, close_price) * np.random.uniform(1.0, 1.05)
                low_price = min(open_price, close_price) * np.random.uniform(0.95, 1.0)
                
                volume = np.random.randint(volume_range[0], volume_range[1])
                
                data.append({
                    "Code": f"stock_{stock_id:04d}",
                    "Date": date,
                    "Open": round(open_price, 2),
                    "High": round(high_price, 2),
                    "Low": round(low_price, 2),
                    "Close": round(close_price, 2),
                    "Volume": volume
                })
        
        return pd.DataFrame(data)
    
    def generate_corrupted_data(
        self,
        base_data: pd.DataFrame,
        corruption_types: List[str] = None
    ) -> pd.DataFrame:
        """破損データを生成"""
        if corruption_types is None:
            corruption_types = ["missing_values", "invalid_types", "outliers", "duplicates"]
        
        corrupted_data = base_data.copy()
        
        for corruption_type in corruption_types:
            if corruption_type == "missing_values":
                # ランダムに欠損値を追加
                missing_indices = np.random.choice(
                    corrupted_data.index, 
                    size=int(len(corrupted_data) * 0.1), 
                    replace=False
                )
                corrupted_data.loc[missing_indices, "Close"] = np.nan
            
            elif corruption_type == "invalid_types":
                # 数値カラムに文字列を追加
                invalid_indices = np.random.choice(
                    corrupted_data.index, 
                    size=int(len(corrupted_data) * 0.05), 
                    replace=False
                )
                corrupted_data.loc[invalid_indices, "Volume"] = "invalid_volume"
            
            elif corruption_type == "outliers":
                # 外れ値を追加
                outlier_indices = np.random.choice(
                    corrupted_data.index, 
                    size=int(len(corrupted_data) * 0.02), 
                    replace=False
                )
                corrupted_data.loc[outlier_indices, "Close"] *= 1000
            
            elif corruption_type == "duplicates":
                # 重複行を追加
                duplicate_indices = np.random.choice(
                    corrupted_data.index, 
                    size=int(len(corrupted_data) * 0.05), 
                    replace=False
                )
                duplicated_rows = corrupted_data.loc[duplicate_indices].copy()
                corrupted_data = pd.concat([corrupted_data, duplicated_rows], ignore_index=True)
        
        return corrupted_data
    
    def generate_edge_case_data(self) -> Dict[str, pd.DataFrame]:
        """エッジケースデータを生成"""
        edge_cases = {}
        
        # 最小データ
        edge_cases["minimal"] = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"],
            "Open": [100.0],
            "High": [100.0],
            "Low": [100.0],
            "Close": [100.0],
            "Volume": [1]
        })
        
        # 空のデータ
        edge_cases["empty"] = pd.DataFrame()
        
        # 極値データ
        edge_cases["extreme_values"] = pd.DataFrame({
            "Code": ["1234", "5678"],
            "Date": ["20240301", "20240302"],
            "Open": [1e-10, 1e10],
            "High": [1e-10, 1e10],
            "Low": [1e-10, 1e10],
            "Close": [1e-10, 1e10],
            "Volume": [1, 1000000000]
        })
        
        # NaN値のみ
        edge_cases["all_nan"] = pd.DataFrame({
            "Code": [np.nan, np.nan],
            "Date": [np.nan, np.nan],
            "Open": [np.nan, np.nan],
            "High": [np.nan, np.nan],
            "Low": [np.nan, np.nan],
            "Close": [np.nan, np.nan],
            "Volume": [np.nan, np.nan]
        })
        
        # 負の値
        edge_cases["negative_values"] = pd.DataFrame({
            "Code": ["1234", "5678"],
            "Date": ["20240301", "20240302"],
            "Open": [-100.0, -101.0],
            "High": [-95.0, -96.0],
            "Low": [-105.0, -106.0],
            "Close": [-102.0, -103.0],
            "Volume": [-1000000, -1100000]
        })
        
        # 無限大の値
        edge_cases["infinite_values"] = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"],
            "Open": [np.inf],
            "High": [np.inf],
            "Low": [np.inf],
            "Close": [np.inf],
            "Volume": [np.inf]
        })
        
        return edge_cases
    
    def generate_time_series_data(
        self,
        length: int = 100,
        frequency: str = "D",
        start_date: str = "2023-01-01"
    ) -> pd.DataFrame:
        """時系列データを生成"""
        dates = pd.date_range(start_date, periods=length, freq=frequency)
        
        # ランダムウォークで価格を生成
        returns = np.random.normal(0, 0.02, length)
        prices = 100 * np.exp(np.cumsum(returns))
        
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            open_price = price * np.random.uniform(0.98, 1.02)
            close_price = price * np.random.uniform(0.98, 1.02)
            high_price = max(open_price, close_price) * np.random.uniform(1.0, 1.05)
            low_price = min(open_price, close_price) * np.random.uniform(0.95, 1.0)
            
            data.append({
                "Date": date.strftime("%Y%m%d"),
                "Open": round(open_price, 2),
                "High": round(high_price, 2),
                "Low": round(low_price, 2),
                "Close": round(close_price, 2),
                "Volume": np.random.randint(100000, 1000000)
            })
        
        return pd.DataFrame(data)
    
    def generate_market_scenarios(self) -> Dict[str, pd.DataFrame]:
        """市場シナリオデータを生成"""
        scenarios = {}
        
        # 上昇トレンド
        scenarios["bull_market"] = self.generate_stock_data(
            start_date="2023-01-01",
            end_date="2023-03-31",
            num_stocks=3,
            price_range=(100.0, 150.0),
            trend_strength=0.2
        )
        
        # 下降トレンド
        scenarios["bear_market"] = self.generate_stock_data(
            start_date="2023-01-01",
            end_date="2023-03-31",
            num_stocks=3,
            price_range=(150.0, 100.0),
            trend_strength=-0.2
        )
        
        # 高ボラティリティ
        scenarios["high_volatility"] = self.generate_stock_data(
            start_date="2023-01-01",
            end_date="2023-03-31",
            num_stocks=3,
            price_range=(80.0, 120.0),
            add_noise=True
        )
        
        # 低ボラティリティ
        scenarios["low_volatility"] = self.generate_stock_data(
            start_date="2023-01-01",
            end_date="2023-03-31",
            num_stocks=3,
            price_range=(95.0, 105.0),
            add_noise=False
        )
        
        return scenarios
    
    def validate_generated_data(self, data: pd.DataFrame) -> Dict[str, bool]:
        """生成されたデータの検証"""
        validation_results = {}
        
        # 基本構造の検証
        validation_results["has_required_columns"] = all(
            col in data.columns for col in ["Code", "Date", "Open", "High", "Low", "Close", "Volume"]
        )
        
        # データ型の検証
        validation_results["correct_data_types"] = all(
            data[col].dtype in [np.float64, np.int64] for col in ["Open", "High", "Low", "Close", "Volume"]
        )
        
        # 価格一貫性の検証
        validation_results["price_consistency"] = all(
            (data["High"] >= data["Low"]) & 
            (data["High"] >= data["Open"]) & 
            (data["High"] >= data["Close"]) &
            (data["Low"] <= data["Open"]) & 
            (data["Low"] <= data["Close"])
        )
        
        # ボリュームの検証
        validation_results["positive_volume"] = all(data["Volume"] >= 0)
        
        # 欠損値の検証
        validation_results["no_missing_values"] = not data.isnull().any().any()
        
        # 日付形式の検証
        validation_results["valid_date_format"] = all(
            len(str(date)) == 8 and str(date).isdigit() for date in data["Date"]
        )
        
        return validation_results
    
    def generate_stress_test_data(self, size: int = 10000) -> pd.DataFrame:
        """ストレステスト用の大きなデータセットを生成"""
        return self.generate_stock_data(
            start_date="2020-01-01",
            end_date="2023-12-31",
            num_stocks=size // 1000,  # 適切な株式数を計算
            price_range=(1.0, 1000.0),
            volume_range=(1000, 10000000)
        )
    
    def generate_anomaly_data(self, base_data: pd.DataFrame) -> pd.DataFrame:
        """異常値データを生成"""
        anomaly_data = base_data.copy()
        
        # 価格スパイク
        spike_indices = np.random.choice(
            anomaly_data.index, 
            size=int(len(anomaly_data) * 0.01), 
            replace=False
        )
        anomaly_data.loc[spike_indices, "Close"] *= 10
        
        # ボリュームスパイク
        volume_spike_indices = np.random.choice(
            anomaly_data.index, 
            size=int(len(anomaly_data) * 0.01), 
            replace=False
        )
        anomaly_data.loc[volume_spike_indices, "Volume"] *= 100
        
        # 価格ドロップ
        drop_indices = np.random.choice(
            anomaly_data.index, 
            size=int(len(anomaly_data) * 0.01), 
            replace=False
        )
        anomaly_data.loc[drop_indices, "Close"] *= 0.1
        
        return anomaly_data
