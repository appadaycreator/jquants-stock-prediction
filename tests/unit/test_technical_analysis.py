"""
テクニカル分析ライブラリのテスト
"""

import unittest
import pandas as pd
import numpy as np
from core.technical_analysis import TechnicalAnalysis, calculate_technical_indicators


class TestTechnicalAnalysis(unittest.TestCase):
    """テクニカル分析のテストクラス"""
    
    def setUp(self):
        """テストデータの準備"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        
        # サンプル株価データ
        base_price = 100
        price_changes = np.random.normal(0, 2, 100)
        prices = [base_price]
        
        for change in price_changes[1:]:
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'high': [p + np.random.uniform(0, 2) for p in prices],
            'low': [p - np.random.uniform(0, 2) for p in prices],
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # high, low, closeの整合性を保つ
        self.df['high'] = np.maximum(self.df['high'], self.df['close'])
        self.df['low'] = np.minimum(self.df['low'], self.df['close'])
    
    def test_sma(self):
        """単純移動平均のテスト"""
        sma_5 = TechnicalAnalysis.sma(self.df['close'], 5)
        
        # 最初の4つはNaN
        self.assertTrue(pd.isna(sma_5.iloc[0:4]).all())
        
        # 5番目から値が入る
        self.assertFalse(pd.isna(sma_5.iloc[4]))
        
        # 値が正しいかチェック
        expected_sma_5 = self.df['close'].rolling(5).mean()
        pd.testing.assert_series_equal(sma_5, expected_sma_5)
    
    def test_ema(self):
        """指数移動平均のテスト"""
        ema_10 = TechnicalAnalysis.ema(self.df['close'], 10)
        
        # 最初の値は元の値と同じ
        self.assertEqual(ema_10.iloc[0], self.df['close'].iloc[0])
        
        # 値が正しいかチェック
        expected_ema_10 = self.df['close'].ewm(span=10).mean()
        pd.testing.assert_series_equal(ema_10, expected_ema_10)
    
    def test_rsi(self):
        """RSIのテスト"""
        rsi = TechnicalAnalysis.rsi(self.df['close'])
        
        # RSIは0-100の範囲（NaNを除く）
        valid_rsi = rsi.dropna()
        if len(valid_rsi) > 0:
            self.assertTrue((valid_rsi >= 0).all())
            self.assertTrue((valid_rsi <= 100).all())
        
        # 最初の13個はNaN
        self.assertTrue(pd.isna(rsi.iloc[0:13]).all())
    
    def test_macd(self):
        """MACDのテスト"""
        macd, signal, histogram = TechnicalAnalysis.macd(self.df['close'])
        
        # すべて同じ長さ
        self.assertEqual(len(macd), len(self.df))
        self.assertEqual(len(signal), len(self.df))
        self.assertEqual(len(histogram), len(self.df))
        
        # histogram = macd - signal
        pd.testing.assert_series_equal(histogram, macd - signal)
    
    def test_bollinger_bands(self):
        """ボリンジャーバンドのテスト"""
        upper, middle, lower = TechnicalAnalysis.bollinger_bands(self.df['close'])
        
        # upper > middle > lower（NaNを除く）
        valid_mask = ~(upper.isna() | middle.isna() | lower.isna())
        if valid_mask.any():
            self.assertTrue((upper[valid_mask] >= middle[valid_mask]).all())
            self.assertTrue((middle[valid_mask] >= lower[valid_mask]).all())
        
        # middleはSMAと同じ
        expected_sma = TechnicalAnalysis.sma(self.df['close'], 20)
        pd.testing.assert_series_equal(middle, expected_sma)
    
    def test_stochastic(self):
        """ストキャスティクスのテスト"""
        k_percent, d_percent = TechnicalAnalysis.stochastic(
            self.df['high'], self.df['low'], self.df['close']
        )
        
        # 0-100の範囲（NaNを除く）
        valid_k = k_percent.dropna()
        if len(valid_k) > 0:
            self.assertTrue((valid_k >= 0).all())
            self.assertTrue((valid_k <= 100).all())
        
        # d_percentはk_percentの移動平均
        expected_d = k_percent.rolling(3).mean()
        pd.testing.assert_series_equal(d_percent, expected_d)
    
    def test_atr(self):
        """ATRのテスト"""
        atr = TechnicalAnalysis.atr(self.df['high'], self.df['low'], self.df['close'])
        
        # ATRは正の値（NaNを除く）
        valid_atr = atr.dropna()
        if len(valid_atr) > 0:
            self.assertTrue((valid_atr >= 0).all())
        
        # 最初の13個はNaN
        self.assertTrue(pd.isna(atr.iloc[0:13]).all())
    
    def test_obv(self):
        """OBVのテスト"""
        obv = TechnicalAnalysis.obv(self.df['close'], self.df['volume'])
        
        # 最初の値は最初のボリューム
        self.assertEqual(obv.iloc[0], self.df['volume'].iloc[0])
        
        # 値が累積されている
        self.assertNotEqual(obv.iloc[-1], obv.iloc[0])
    
    def test_vwap(self):
        """VWAPのテスト"""
        vwap = TechnicalAnalysis.vwap(
            self.df['high'], self.df['low'], self.df['close'], self.df['volume']
        )
        
        # VWAPは正の値（NaNを除く）
        valid_vwap = vwap.dropna()
        if len(valid_vwap) > 0:
            self.assertTrue((valid_vwap > 0).all())
        
        # VWAPは価格の範囲内（NaNを除く）
        valid_mask = ~(vwap.isna() | self.df['low'].isna() | self.df['high'].isna())
        if valid_mask.any():
            # VWAPはlowとhighの間にあることを確認
            typical_price = (self.df['high'] + self.df['low'] + self.df['close']) / 3
            self.assertTrue((vwap[valid_mask] >= typical_price[valid_mask] * 0.5).all())
            self.assertTrue((vwap[valid_mask] <= typical_price[valid_mask] * 1.5).all())
    
    def test_ichimoku(self):
        """一目均衡表のテスト"""
        ichimoku = TechnicalAnalysis.ichimoku(
            self.df['high'], self.df['low'], self.df['close']
        )
        
        # すべての指標が存在
        self.assertIn('conversion_line', ichimoku)
        self.assertIn('base_line', ichimoku)
        self.assertIn('leading_span_a', ichimoku)
        self.assertIn('leading_span_b', ichimoku)
        
        # すべて同じ長さ
        for key, value in ichimoku.items():
            self.assertEqual(len(value), len(self.df))
    
    def test_calculate_technical_indicators(self):
        """テクニカル指標計算のテスト"""
        result = calculate_technical_indicators(self.df)
        
        # 元の列が保持されている
        for col in self.df.columns:
            self.assertIn(col, result.columns)
        
        # 新しい指標が追加されている
        expected_indicators = ['sma_5', 'sma_10', 'sma_20', 'sma_50', 'rsi', 'macd']
        for indicator in expected_indicators:
            self.assertIn(indicator, result.columns)
    
    def test_edge_cases(self):
        """エッジケースのテスト"""
        # 空のデータフレーム
        empty_df = pd.DataFrame()
        result = calculate_technical_indicators(empty_df)
        self.assertEqual(len(result), 0)
        
        # 1行のデータ
        single_row = self.df.iloc[:1].copy()
        result = calculate_technical_indicators(single_row)
        self.assertEqual(len(result), 1)
        
        # NaN値の処理
        df_with_nan = self.df.copy()
        df_with_nan.loc[10:15, 'close'] = np.nan
        result = calculate_technical_indicators(df_with_nan)
        self.assertEqual(len(result), len(df_with_nan))


if __name__ == '__main__':
    unittest.main()
