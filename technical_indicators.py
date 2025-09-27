#!/usr/bin/env python3
"""
技術指標計算モジュール
株価データに対する高度な技術指標を計算する機能を提供
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """技術指標計算クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_all_indicators(self, df: pd.DataFrame, config: Dict = None) -> pd.DataFrame:
        """
        全ての技術指標を計算
        
        Args:
            df (pd.DataFrame): OHLCV データ
            config (Dict): 設定辞書
            
        Returns:
            pd.DataFrame: 技術指標が追加されたデータフレーム
        """
        result_df = df.copy()
        
        # デフォルト設定
        if config is None:
            config = self._get_default_config()
        
        self.logger.info("📊 技術指標の計算を開始...")
        
        # 必要なカラムの存在確認
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"必要なカラムが不足しています: {missing_columns}")
        
        try:
            # 1. 移動平均系
            result_df = self._calculate_moving_averages(result_df, config.get('sma_windows', [5, 10, 25, 50]))
            result_df = self._calculate_ema(result_df, config.get('ema_windows', [12, 26]))
            
            # 2. モメンタム系指標
            result_df = self._calculate_rsi(result_df, config.get('rsi_period', 14))
            result_df = self._calculate_macd(result_df, config.get('macd_fast', 12), 
                                           config.get('macd_slow', 26), config.get('macd_signal', 9))
            result_df = self._calculate_stochastic(result_df, config.get('stoch_k', 14), config.get('stoch_d', 3))
            
            # 3. ボラティリティ系指標
            result_df = self._calculate_bollinger_bands(result_df, config.get('bb_period', 20), config.get('bb_std', 2))
            result_df = self._calculate_atr(result_df, config.get('atr_period', 14))
            
            # 4. ボリューム系指標
            result_df = self._calculate_volume_indicators(result_df, config.get('volume_sma_period', 20))
            result_df = self._calculate_vwap(result_df)
            result_df = self._calculate_obv(result_df)
            
            # 5. トレンド系指標
            result_df = self._calculate_adx(result_df, config.get('adx_period', 14))
            result_df = self._calculate_cci(result_df, config.get('cci_period', 20))
            
            # 6. 価格変動率
            result_df = self._calculate_price_changes(result_df, config.get('price_change_periods', [1, 3, 5, 10]))
            
            # 7. 価格位置指標
            result_df = self._calculate_price_position(result_df, config.get('price_position_periods', [20, 50]))
            
            self.logger.info(f"✅ 技術指標計算完了: {len(result_df.columns) - len(df.columns)}個の新指標を追加")
            
        except Exception as e:
            self.logger.error(f"❌ 技術指標計算中にエラー: {e}")
            raise
        
        return result_df
    
    def _get_default_config(self) -> Dict:
        """デフォルト設定を取得"""
        return {
            'sma_windows': [5, 10, 20, 25, 50],
            'ema_windows': [12, 26],
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26, 
            'macd_signal': 9,
            'stoch_k': 14,
            'stoch_d': 3,
            'bb_period': 20,
            'bb_std': 2,
            'atr_period': 14,
            'volume_sma_period': 20,
            'adx_period': 14,
            'cci_period': 20,
            'price_change_periods': [1, 3, 5, 10],
            'price_position_periods': [20, 50]
        }
    
    def _calculate_moving_averages(self, df: pd.DataFrame, windows: List[int]) -> pd.DataFrame:
        """単純移動平均を計算"""
        result_df = df.copy()
        for window in windows:
            result_df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
        return result_df
    
    def _calculate_ema(self, df: pd.DataFrame, windows: List[int]) -> pd.DataFrame:
        """指数移動平均を計算"""
        result_df = df.copy()
        for window in windows:
            result_df[f'EMA_{window}'] = df['Close'].ewm(span=window).mean()
        return result_df
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """RSI（相対力指数）を計算"""
        result_df = df.copy()
        
        # 価格変動を計算
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # RSI計算
        rs = gain / loss
        result_df['RSI'] = 100 - (100 / (1 + rs))
        
        return result_df
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD（移動平均収束拡散）を計算"""
        result_df = df.copy()
        
        # EMAを計算
        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        
        # MACD Line
        result_df['MACD'] = ema_fast - ema_slow
        
        # Signal Line  
        result_df['MACD_Signal'] = result_df['MACD'].ewm(span=signal).mean()
        
        # MACD Histogram
        result_df['MACD_Histogram'] = result_df['MACD'] - result_df['MACD_Signal']
        
        return result_df
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """ストキャスティクスを計算"""
        result_df = df.copy()
        
        # %K計算
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        result_df['Stoch_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
        
        # %D計算（%Kの移動平均）
        result_df['Stoch_D'] = result_df['Stoch_K'].rolling(window=d_period).mean()
        
        return result_df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """ボリンジャーバンドを計算"""
        result_df = df.copy()
        
        # 中央線（移動平均）
        sma = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        
        result_df['BB_Middle'] = sma
        result_df['BB_Upper'] = sma + (std * std_dev)
        result_df['BB_Lower'] = sma - (std * std_dev)
        
        # %B（ボリンジャーバンド内の位置）
        result_df['BB_Percent'] = (df['Close'] - result_df['BB_Lower']) / (result_df['BB_Upper'] - result_df['BB_Lower'])
        
        # バンド幅
        result_df['BB_Width'] = (result_df['BB_Upper'] - result_df['BB_Lower']) / result_df['BB_Middle']
        
        return result_df
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """ATR（真の値幅）を計算"""
        result_df = df.copy()
        
        # True Range計算
        high_low = df['High'] - df['Low']
        high_close_prev = np.abs(df['High'] - df['Close'].shift(1))
        low_close_prev = np.abs(df['Low'] - df['Close'].shift(1))
        
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        
        # ATR（True Rangeの移動平均）
        result_df['ATR'] = true_range.rolling(window=period).mean()
        
        # ATR Percentage（終値に対する相対ATR）
        result_df['ATR_Percent'] = result_df['ATR'] / df['Close'] * 100
        
        return result_df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame, sma_period: int = 20) -> pd.DataFrame:
        """ボリューム系指標を計算"""
        result_df = df.copy()
        
        # ボリューム移動平均
        result_df['Volume_SMA'] = df['Volume'].rolling(window=sma_period).mean()
        
        # ボリュームレート（平均との比率）
        result_df['Volume_Rate'] = df['Volume'] / result_df['Volume_SMA']
        
        # 価格ボリューム趨勢（PVT）
        result_df['PVT'] = ((df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1) * df['Volume']).cumsum()
        
        return result_df
    
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """VWAP（ボリューム加重平均価格）を計算"""
        result_df = df.copy()
        
        # 典型価格
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        
        # VWAP計算
        result_df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        # VWAP乖離率
        result_df['VWAP_Deviation'] = (df['Close'] - result_df['VWAP']) / result_df['VWAP'] * 100
        
        return result_df
    
    def _calculate_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        """OBV（オンバランスボリューム）を計算"""
        result_df = df.copy()
        
        # 価格変動の方向を判定
        price_change = df['Close'].diff()
        obv_change = np.where(price_change > 0, df['Volume'], 
                             np.where(price_change < 0, -df['Volume'], 0))
        
        # OBV累積
        result_df['OBV'] = obv_change.cumsum()
        
        # OBV移動平均
        result_df['OBV_SMA'] = result_df['OBV'].rolling(window=20).mean()
        
        return result_df
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """ADX（平均方向性指数）を計算"""
        result_df = df.copy()
        
        # True Range
        high_low = df['High'] - df['Low']
        high_close_prev = np.abs(df['High'] - df['Close'].shift(1))
        low_close_prev = np.abs(df['Low'] - df['Close'].shift(1))
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        
        # Directional Movement
        plus_dm = pd.Series(np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
                                    np.maximum(df['High'] - df['High'].shift(1), 0), 0), index=df.index)
        minus_dm = pd.Series(np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
                                     np.maximum(df['Low'].shift(1) - df['Low'], 0), 0), index=df.index)
        
        # Smoothed values
        atr = pd.Series(true_range, index=df.index).rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        result_df['ADX'] = dx.rolling(window=period).mean()
        result_df['Plus_DI'] = plus_di
        result_df['Minus_DI'] = minus_di
        
        return result_df
    
    def _calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """CCI（商品チャネル指数）を計算"""
        result_df = df.copy()
        
        # 典型価格
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        
        # CCI計算
        sma_tp = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        
        result_df['CCI'] = (typical_price - sma_tp) / (0.015 * mad)
        
        return result_df
    
    def _calculate_price_changes(self, df: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
        """価格変動率を計算"""
        result_df = df.copy()
        
        for period in periods:
            # 絶対変化
            result_df[f'Price_Change_{period}d'] = df['Close'].diff(period)
            
            # 相対変化（％）
            result_df[f'Price_Change_Pct_{period}d'] = df['Close'].pct_change(period) * 100
            
            # ログリターン
            result_df[f'Log_Return_{period}d'] = np.log(df['Close'] / df['Close'].shift(period))
        
        return result_df
    
    def _calculate_price_position(self, df: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
        """価格位置指標を計算"""
        result_df = df.copy()
        
        for period in periods:
            # 最高値・最安値からの位置
            high_max = df['High'].rolling(window=period).max()
            low_min = df['Low'].rolling(window=period).min()
            
            result_df[f'Price_Position_{period}d'] = (df['Close'] - low_min) / (high_max - low_min) * 100
            
            # 移動平均からの乖離
            sma = df['Close'].rolling(window=period).mean()
            result_df[f'SMA_Deviation_{period}d'] = (df['Close'] - sma) / sma * 100
        
        return result_df

def get_enhanced_features_list() -> List[str]:
    """拡張された特徴量リストを取得"""
    return [
        # 既存のSMA
        'SMA_5', 'SMA_10', 'SMA_20', 'SMA_25', 'SMA_50',
        
        # EMA
        'EMA_12', 'EMA_26',
        
        # モメンタム系
        'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
        'Stoch_K', 'Stoch_D',
        
        # ボラティリティ系
        'BB_Upper', 'BB_Lower', 'BB_Percent', 'BB_Width',
        'ATR', 'ATR_Percent',
        
        # ボリューム系
        'Volume_SMA', 'Volume_Rate', 'VWAP', 'VWAP_Deviation', 
        'OBV', 'OBV_SMA', 'PVT',
        
        # トレンド系
        'ADX', 'Plus_DI', 'Minus_DI', 'CCI',
        
        # 価格変動
        'Price_Change_1d', 'Price_Change_3d', 'Price_Change_5d', 'Price_Change_10d',
        'Price_Change_Pct_1d', 'Price_Change_Pct_3d', 'Price_Change_Pct_5d', 'Price_Change_Pct_10d',
        'Log_Return_1d', 'Log_Return_3d', 'Log_Return_5d', 'Log_Return_10d',
        
        # 価格位置
        'Price_Position_20d', 'Price_Position_50d',
        'SMA_Deviation_20d', 'SMA_Deviation_50d',
        
        # ラグ特徴量（既存）
        'Close_lag_1', 'Close_lag_3', 'Close_lag_5',
        
        # ボリューム
        'Volume'
    ]

if __name__ == "__main__":
    # テスト用のサンプルデータ
    import pandas as pd
    
    # サンプルデータ生成
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # ベース価格生成
    base_price = 1000 + np.cumsum(np.random.randn(100) * 0.02) * 1000
    
    sample_data = pd.DataFrame({
        'Date': dates,
        'Open': base_price,
        'High': base_price * (1 + np.random.uniform(0, 0.05, 100)),
        'Low': base_price * (1 - np.random.uniform(0, 0.05, 100)),
        'Close': base_price + np.random.uniform(-20, 20, 100),
        'Volume': np.random.randint(1000000, 10000000, 100)
    })
    
    # 技術指標計算
    calculator = TechnicalIndicators()
    enhanced_data = calculator.calculate_all_indicators(sample_data)
    
    print(f"📊 元データ: {len(sample_data.columns)}列")
    print(f"📈 拡張後: {len(enhanced_data.columns)}列")
    print(f"➕ 追加指標: {len(enhanced_data.columns) - len(sample_data.columns)}個")
    
    # 追加された指標を表示
    new_columns = [col for col in enhanced_data.columns if col not in sample_data.columns]
    print("\n🔧 追加された技術指標:")
    for i, col in enumerate(new_columns, 1):
        print(f"  {i:2d}. {col}")
