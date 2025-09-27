"""
テスト用データジェネレーター
様々なテストシナリオに対応したサンプルデータを生成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DataGenerator:
    """テスト用データジェネレータークラス"""
    
    def __init__(self, seed: int = 42):
        """
        初期化
        
        Args:
            seed (int): 乱数シード
        """
        self.seed = seed
        np.random.seed(seed)
    
    def generate_stock_data(self, 
                          days: int = 100, 
                          start_price: float = 100.0,
                          volatility: float = 0.02,
                          trend: float = 0.001) -> pd.DataFrame:
        """
        株価データを生成
        
        Args:
            days (int): 生成する日数
            start_price (float): 開始価格
            volatility (float): ボラティリティ
            trend (float): トレンド
            
        Returns:
            pd.DataFrame: 株価データ
        """
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        # ランダムウォークで価格を生成
        returns = np.random.normal(trend, volatility, days)
        prices = start_price * np.exp(np.cumsum(returns))
        
        # OHLCデータを生成
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # 高値と安値を生成
            high_factor = 1 + abs(np.random.normal(0, 0.01))
            low_factor = 1 - abs(np.random.normal(0, 0.01))
            
            high = price * high_factor
            low = price * low_factor
            
            # 始値は前日の終値に近い値
            if i == 0:
                open_price = price
            else:
                open_price = prices[i-1] * (1 + np.random.normal(0, 0.005))
            
            # 終値は価格
            close = price
            
            # ボリュームを生成
            volume = np.random.randint(1000, 10000)
            
            data.append({
                'Date': date,
                'Open': open_price,
                'High': max(high, open_price, close),
                'Low': min(low, open_price, close),
                'Close': close,
                'Volume': volume
            })
        
        return pd.DataFrame(data)
    
    def generate_stock_data_with_patterns(self, 
                                        days: int = 100,
                                        patterns: List[str] = None) -> pd.DataFrame:
        """
        パターンを含む株価データを生成
        
        Args:
            days (int): 生成する日数
            patterns (List[str]): 含めるパターン ['trend', 'seasonal', 'volatility_cluster']
            
        Returns:
            pd.DataFrame: 株価データ
        """
        if patterns is None:
            patterns = ['trend']
        
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        prices = np.zeros(days)
        prices[0] = 100.0
        
        for i in range(1, days):
            base_return = np.random.normal(0, 0.02)
            
            # トレンドパターン
            if 'trend' in patterns:
                trend_component = 0.001 * i  # 上昇トレンド
                base_return += trend_component
            
            # 季節性パターン
            if 'seasonal' in patterns:
                seasonal_component = 0.01 * np.sin(2 * np.pi * i / 30)  # 月次周期
                base_return += seasonal_component
            
            # ボラティリティクラスタリング
            if 'volatility_cluster' in patterns:
                if i > 0 and abs(prices[i-1] - prices[i-2]) > 0.05:  # 前日が大きく変動
                    base_return *= 2  # ボラティリティを増加
            
            prices[i] = prices[i-1] * (1 + base_return)
        
        # OHLCデータを生成
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            
            if i == 0:
                open_price = price
            else:
                open_price = prices[i-1] * (1 + np.random.normal(0, 0.005))
            
            close = price
            volume = np.random.randint(1000, 10000)
            
            data.append({
                'Date': date,
                'Open': open_price,
                'High': max(high, open_price, close),
                'Low': min(low, open_price, close),
                'Close': close,
                'Volume': volume
            })
        
        return pd.DataFrame(data)
    
    def generate_missing_data(self, base_data: pd.DataFrame, 
                             missing_ratio: float = 0.1) -> pd.DataFrame:
        """
        欠損値を含むデータを生成
        
        Args:
            base_data (pd.DataFrame): ベースデータ
            missing_ratio (float): 欠損値の割合
            
        Returns:
            pd.DataFrame: 欠損値を含むデータ
        """
        data = base_data.copy()
        
        # ランダムに欠損値を導入
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in data.columns:
                missing_indices = np.random.choice(
                    data.index, 
                    size=int(len(data) * missing_ratio), 
                    replace=False
                )
                data.loc[missing_indices, col] = np.nan
        
        return data
    
    def generate_outlier_data(self, base_data: pd.DataFrame, 
                            outlier_ratio: float = 0.05) -> pd.DataFrame:
        """
        外れ値を含むデータを生成
        
        Args:
            base_data (pd.DataFrame): ベースデータ
            outlier_ratio (float): 外れ値の割合
            
        Returns:
            pd.DataFrame: 外れ値を含むデータ
        """
        data = base_data.copy()
        
        # ランダムに外れ値を導入
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in data.columns:
                outlier_indices = np.random.choice(
                    data.index, 
                    size=int(len(data) * outlier_ratio), 
                    replace=False
                )
                
                for idx in outlier_indices:
                    # 外れ値を生成（通常の3倍の変動）
                    data.loc[idx, col] *= (1 + np.random.normal(0, 0.1))
        
        return data
    
    def generate_invalid_data(self) -> pd.DataFrame:
        """
        無効なデータを生成（テスト用）
        
        Returns:
            pd.DataFrame: 無効なデータ
        """
        return pd.DataFrame({
            'Date': ['invalid_date', '2023-01-01', '2023-01-02'],
            'Open': [np.nan, 100, 101],
            'High': [95, 105, 106],  # High < Open (無効)
            'Low': [105, 95, 96],    # Low > High (無効)
            'Close': [102, 103, 104],
            'Volume': [-1000, 1000, 2000]  # 負のボリューム
        })
    
    def generate_single_row_data(self) -> pd.DataFrame:
        """
        1行のデータを生成
        
        Returns:
            pd.DataFrame: 1行のデータ
        """
        return pd.DataFrame({
            'Date': ['2023-01-01'],
            'Open': [100],
            'High': [105],
            'Low': [95],
            'Close': [102],
            'Volume': [1000]
        })
    
    def generate_empty_data(self) -> pd.DataFrame:
        """
        空のデータを生成
        
        Returns:
            pd.DataFrame: 空のデータフレーム
        """
        return pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    
    def generate_large_dataset(self, days: int = 1000) -> pd.DataFrame:
        """
        大きなデータセットを生成
        
        Args:
            days (int): 生成する日数
            
        Returns:
            pd.DataFrame: 大きなデータセット
        """
        return self.generate_stock_data(days=days)
    
    def generate_multiple_stocks(self, 
                               stock_count: int = 3,
                               days: int = 100) -> Dict[str, pd.DataFrame]:
        """
        複数の銘柄データを生成
        
        Args:
            stock_count (int): 銘柄数
            days (int): 各銘柄の日数
            
        Returns:
            Dict[str, pd.DataFrame]: 銘柄名をキーとしたデータ辞書
        """
        stocks = {}
        for i in range(stock_count):
            stock_name = f"STOCK_{i+1:03d}"
            stocks[stock_name] = self.generate_stock_data(days=days)
        
        return stocks
