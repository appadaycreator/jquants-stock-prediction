"""
技術指標モジュールのユニットテスト
"""
import pytest
import pandas as pd
import numpy as np
from technical_indicators import TechnicalIndicators

class TestTechnicalIndicators:
    """TechnicalIndicatorsクラスのテスト"""
    
    def test_init(self):
        """初期化テスト"""
        ti = TechnicalIndicators()
        assert ti is not None
        assert hasattr(ti, 'logger')
    
    def test_calculate_all_indicators_basic(self, sample_stock_data):
        """基本的な技術指標計算テスト"""
        ti = TechnicalIndicators()
        result = ti.calculate_all_indicators(sample_stock_data)
        
        # 元のデータフレームより多くのカラムがあることを確認
        assert len(result.columns) > len(sample_stock_data.columns)
        assert len(result) == len(sample_stock_data)
        
        # 元のデータが保持されていることを確認
        for col in sample_stock_data.columns:
            assert col in result.columns
    
    def test_calculate_all_indicators_missing_columns(self):
        """必要なカラムが不足している場合のテスト"""
        ti = TechnicalIndicators()
        incomplete_data = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=10),
            'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        })
        
        with pytest.raises(ValueError, match="必要なカラムが不足しています"):
            ti.calculate_all_indicators(incomplete_data)
    
    def test_calculate_all_indicators_with_config(self, sample_stock_data):
        """カスタム設定での技術指標計算テスト"""
        ti = TechnicalIndicators()
        config = {
            'sma_windows': [5, 10],
            'rsi_period': 7,
            'macd_fast': 5,
            'macd_slow': 10
        }
        
        result = ti.calculate_all_indicators(sample_stock_data, config)
        assert len(result.columns) > len(sample_stock_data.columns)
    
    def test_sma_calculation(self, sample_stock_data):
        """移動平均の計算テスト"""
        ti = TechnicalIndicators()
        result = ti._calculate_moving_averages(sample_stock_data, [5, 10])
        
        # SMA_5とSMA_10が追加されていることを確認
        assert 'SMA_5' in result.columns
        assert 'SMA_10' in result.columns
        
        # 最初の数行はNaNであることを確認（期間が足りないため）
        assert pd.isna(result['SMA_5'].iloc[0])
        assert pd.isna(result['SMA_10'].iloc[0])
        
        # 十分な期間がある行では値が計算されていることを確認
        assert not pd.isna(result['SMA_5'].iloc[10])
        assert not pd.isna(result['SMA_10'].iloc[15])
    
    def test_rsi_calculation(self, sample_stock_data):
        """RSIの計算テスト"""
        ti = TechnicalIndicators()
        result = ti._calculate_rsi(sample_stock_data, 14)
        
        assert 'RSI' in result.columns
        
        # RSIは0-100の範囲であることを確認
        rsi_values = result['RSI'].dropna()
        assert all(0 <= val <= 100 for val in rsi_values)
    
    def test_macd_calculation(self, sample_stock_data):
        """MACDの計算テスト"""
        ti = TechnicalIndicators()
        result = ti._calculate_macd(sample_stock_data, 12, 26, 9)
        
        assert 'MACD' in result.columns
        assert 'MACD_Signal' in result.columns
        assert 'MACD_Histogram' in result.columns
    
    def test_bollinger_bands_calculation(self, sample_stock_data):
        """ボリンジャーバンドの計算テスト"""
        ti = TechnicalIndicators()
        result = ti._calculate_bollinger_bands(sample_stock_data, 20, 2)
        
        assert 'BB_Upper' in result.columns
        assert 'BB_Middle' in result.columns
        assert 'BB_Lower' in result.columns
        assert 'BB_Width' in result.columns
        assert 'BB_Percent' in result.columns
        
        # ボリンジャーバンドの関係性を確認
        bb_data = result[['BB_Upper', 'BB_Middle', 'BB_Lower']].dropna()
        assert all(bb_data['BB_Upper'] >= bb_data['BB_Middle'])
        assert all(bb_data['BB_Middle'] >= bb_data['BB_Lower'])
    
    def test_atr_calculation(self, sample_stock_data):
        """ATRの計算テスト"""
        ti = TechnicalIndicators()
        result = ti._calculate_atr(sample_stock_data, 14)
        
        assert 'ATR' in result.columns
        
        # ATRは正の値であることを確認
        atr_values = result['ATR'].dropna()
        assert all(val >= 0 for val in atr_values)
    
    def test_volume_indicators(self, sample_stock_data):
        """ボリューム指標の計算テスト"""
        ti = TechnicalIndicators()
        result = ti._calculate_volume_indicators(sample_stock_data, 20)
        
        assert 'Volume_SMA' in result.columns
        assert 'Volume_Rate' in result.columns
    
    def test_price_changes_calculation(self, sample_stock_data):
        """価格変動率の計算テスト"""
        ti = TechnicalIndicators()
        result = ti._calculate_price_changes(sample_stock_data, [1, 3, 5])
        
        assert 'Price_Change_1d' in result.columns
        assert 'Price_Change_3d' in result.columns
        assert 'Price_Change_5d' in result.columns
        
        # 価格変動率の計算を確認
        price_change_1d = result['Price_Change_1d'].dropna()
        assert len(price_change_1d) > 0
    
    def test_empty_dataframe(self):
        """空のデータフレームでのテスト"""
        ti = TechnicalIndicators()
        empty_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        
        # 空のデータフレームでもエラーが発生しないことを確認
        result = ti.calculate_all_indicators(empty_df)
        assert result.empty
    
    def test_single_row_dataframe(self):
        """1行のデータフレームでのテスト"""
        ti = TechnicalIndicators()
        single_row_df = pd.DataFrame({
            'Open': [100],
            'High': [105],
            'Low': [95],
            'Close': [102],
            'Volume': [1000]
        })
        
        result = ti.calculate_all_indicators(single_row_df)
        assert len(result) == 1
        # 多くの指標はNaNになるが、エラーは発生しないことを確認
        assert not result.empty
    
    def test_nan_handling(self):
        """NaN値の処理テスト"""
        ti = TechnicalIndicators()
        data_with_nan = pd.DataFrame({
            'Open': [100, 101, np.nan, 103, 104],
            'High': [105, 106, 107, 108, 109],
            'Low': [95, 96, 97, 98, 99],
            'Close': [102, 103, 104, 105, 106],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # NaN値があってもエラーが発生しないことを確認
        result = ti.calculate_all_indicators(data_with_nan)
        assert len(result) == 5
    
    def test_default_config(self):
        """デフォルト設定のテスト"""
        ti = TechnicalIndicators()
        config = ti._get_default_config()
        
        assert isinstance(config, dict)
        assert 'sma_windows' in config
        assert 'rsi_period' in config
        assert 'macd_fast' in config
        assert isinstance(config['sma_windows'], list)
        assert isinstance(config['rsi_period'], int)
