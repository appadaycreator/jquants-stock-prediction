#!/usr/bin/env python3
"""
テクニカル分析の拡張テスト
カバレッジ向上のための追加テスト
"""

import pytest
import pandas as pd
import numpy as np
from core.technical_analysis import TechnicalAnalysis, calculate_technical_indicators


class TestTechnicalAnalysisEnhanced:
    """テクニカル分析の拡張テストクラス"""

    def setup_method(self):
        """テストデータの準備"""
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        np.random.seed(42)

        # サンプルデータの生成
        close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        high_prices = close_prices + np.random.rand(100) * 2
        low_prices = close_prices - np.random.rand(100) * 2
        volume = np.random.randint(1000, 10000, 100)

        self.df = pd.DataFrame(
            {
                "date": dates,
                "close": close_prices,
                "high": high_prices,
                "low": low_prices,
                "volume": volume,
            }
        )

        self.close_series = self.df["close"]
        self.high_series = self.df["high"]
        self.low_series = self.df["low"]
        self.volume_series = self.df["volume"]

    def test_sma_edge_cases(self):
        """SMAのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.sma(empty_series, 5)
        assert len(result) == 0

        # 単一値
        single_value = pd.Series([100])
        result = TechnicalAnalysis.sma(single_value, 5)
        assert len(result) == 1
        assert pd.isna(result.iloc[0])

        # ウィンドウサイズがデータより大きい
        short_series = pd.Series([100, 101, 102])
        result = TechnicalAnalysis.sma(short_series, 10)
        assert len(result) == 3
        assert all(pd.isna(result))

    def test_ema_edge_cases(self):
        """EMAのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.ema(empty_series, 5)
        assert len(result) == 0

        # 単一値
        single_value = pd.Series([100])
        result = TechnicalAnalysis.ema(single_value, 5)
        assert len(result) == 1
        assert result.iloc[0] == 100

    def test_rsi_edge_cases(self):
        """RSIのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.rsi(empty_series, 14)
        assert len(result) == 0

        # 単一値
        single_value = pd.Series([100])
        result = TechnicalAnalysis.rsi(single_value, 14)
        assert len(result) == 1
        assert pd.isna(result.iloc[0])

        # 全て同じ値
        constant_series = pd.Series([100] * 20)
        result = TechnicalAnalysis.rsi(constant_series, 14)
        assert len(result) == 20
        # 全て同じ値の場合、RSIは50になるはず
        assert all(result.dropna() == 50)

    def test_macd_edge_cases(self):
        """MACDのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        macd, signal, histogram = TechnicalAnalysis.macd(empty_series)
        assert len(macd) == 0
        assert len(signal) == 0
        assert len(histogram) == 0

        # 短いシリーズ
        short_series = pd.Series([100, 101, 102])
        macd, signal, histogram = TechnicalAnalysis.macd(short_series, 12, 26, 9)
        assert len(macd) == 3
        assert len(signal) == 3
        assert len(histogram) == 3

    def test_bollinger_bands_edge_cases(self):
        """ボリンジャーバンドのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        upper, middle, lower = TechnicalAnalysis.bollinger_bands(empty_series)
        assert len(upper) == 0
        assert len(middle) == 0
        assert len(lower) == 0

        # 単一値
        single_value = pd.Series([100])
        upper, middle, lower = TechnicalAnalysis.bollinger_bands(single_value, 20, 2)
        assert len(upper) == 1
        assert pd.isna(upper.iloc[0])
        assert pd.isna(middle.iloc[0])
        assert pd.isna(lower.iloc[0])

    def test_stochastic_edge_cases(self):
        """ストキャスティクスのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        k, d = TechnicalAnalysis.stochastic(empty_series, empty_series, empty_series)
        assert len(k) == 0
        assert len(d) == 0

        # 単一値
        single_high = pd.Series([100])
        single_low = pd.Series([99])
        single_close = pd.Series([99.5])
        k, d = TechnicalAnalysis.stochastic(single_high, single_low, single_close)
        assert len(k) == 1
        assert len(d) == 1

    def test_atr_edge_cases(self):
        """ATRのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.atr(empty_series, empty_series, empty_series)
        assert len(result) == 0

        # 単一値
        single_high = pd.Series([100])
        single_low = pd.Series([99])
        single_close = pd.Series([99.5])
        result = TechnicalAnalysis.atr(single_high, single_low, single_close)
        assert len(result) == 1

    def test_williams_r_edge_cases(self):
        """Williams %Rのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.williams_r(empty_series, empty_series, empty_series)
        assert len(result) == 0

        # 単一値
        single_high = pd.Series([100])
        single_low = pd.Series([99])
        single_close = pd.Series([99.5])
        result = TechnicalAnalysis.williams_r(single_high, single_low, single_close)
        assert len(result) == 1

    def test_cci_edge_cases(self):
        """CCIのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.cci(empty_series, empty_series, empty_series)
        assert len(result) == 0

        # 単一値
        single_high = pd.Series([100])
        single_low = pd.Series([99])
        single_close = pd.Series([99.5])
        result = TechnicalAnalysis.cci(single_high, single_low, single_close)
        assert len(result) == 1

    def test_adx_edge_cases(self):
        """ADXのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.adx(empty_series, empty_series, empty_series)
        assert len(result) == 0

        # 単一値
        single_high = pd.Series([100])
        single_low = pd.Series([99])
        single_close = pd.Series([99.5])
        result = TechnicalAnalysis.adx(single_high, single_low, single_close)
        assert len(result) == 1

    def test_obv_edge_cases(self):
        """OBVのエッジケーステスト"""
        # 空のシリーズ
        empty_close = pd.Series([], dtype=float)
        empty_volume = pd.Series([], dtype=float)
        result = TechnicalAnalysis.obv(empty_close, empty_volume)
        assert len(result) == 0

        # 単一値
        single_close = pd.Series([100])
        single_volume = pd.Series([1000])
        result = TechnicalAnalysis.obv(single_close, single_volume)
        assert len(result) == 1
        assert result.iloc[0] == 1000

    def test_vwap_edge_cases(self):
        """VWAPのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.vwap(
            empty_series, empty_series, empty_series, empty_series
        )
        assert len(result) == 0

        # 単一値
        single_high = pd.Series([100])
        single_low = pd.Series([99])
        single_close = pd.Series([99.5])
        single_volume = pd.Series([1000])
        result = TechnicalAnalysis.vwap(
            single_high, single_low, single_close, single_volume
        )
        assert len(result) == 1
        assert result.iloc[0] == 99.5

    def test_ichimoku_edge_cases(self):
        """一目均衡表のエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.ichimoku(empty_series, empty_series, empty_series)
        assert len(result["conversion_line"]) == 0
        assert len(result["base_line"]) == 0
        assert len(result["leading_span_a"]) == 0
        assert len(result["leading_span_b"]) == 0

        # 短いシリーズ
        short_high = pd.Series([100, 101, 102])
        short_low = pd.Series([99, 100, 101])
        short_close = pd.Series([99.5, 100.5, 101.5])
        result = TechnicalAnalysis.ichimoku(short_high, short_low, short_close)
        assert len(result["conversion_line"]) == 3
        assert len(result["base_line"]) == 3

    def test_support_resistance_edge_cases(self):
        """サポート・レジスタンスのエッジケーステスト"""
        # 空のシリーズ
        empty_series = pd.Series([], dtype=float)
        result = TechnicalAnalysis.support_resistance(empty_series)
        assert len(result["resistance"]) == 0
        assert len(result["support"]) == 0

        # 単一値
        single_value = pd.Series([100])
        result = TechnicalAnalysis.support_resistance(single_value)
        assert len(result["resistance"]) == 0
        assert len(result["support"]) == 0

    def test_calculate_technical_indicators_edge_cases(self):
        """テクニカル指標計算のエッジケーステスト"""
        # 空のデータフレーム
        empty_df = pd.DataFrame()
        result = calculate_technical_indicators(empty_df)
        assert len(result) == 0

        # 必要な列がない場合
        incomplete_df = pd.DataFrame(
            {"date": pd.date_range("2024-01-01", periods=10), "close": range(100, 110)}
        )
        result = calculate_technical_indicators(incomplete_df)
        assert "sma_5" in result.columns
        assert "rsi" in result.columns

        # 部分的な列がある場合
        partial_df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=10),
                "close": range(100, 110),
                "high": range(101, 111),
                "low": range(99, 109),
            }
        )
        result = calculate_technical_indicators(partial_df)
        assert "bb_upper" in result.columns
        assert "stoch_k" in result.columns

    def test_technical_indicators_with_nan_values(self):
        """NaN値を含むデータでのテスト"""
        # NaN値を含むデータ
        data_with_nan = self.df.copy()
        data_with_nan.loc[10:15, "close"] = np.nan

        # テクニカル指標の計算
        result = calculate_technical_indicators(data_with_nan)

        # NaN値が適切に処理されることを確認
        assert not result["sma_5"].isna().all()
        assert not result["rsi"].isna().all()

    def test_technical_indicators_with_inf_values(self):
        """無限値を含むデータでのテスト"""
        # 無限値を含むデータ
        data_with_inf = self.df.copy()
        data_with_inf.loc[10, "close"] = np.inf
        data_with_inf.loc[11, "close"] = -np.inf

        # テクニカル指標の計算
        result = calculate_technical_indicators(data_with_inf)

        # 無限値が適切に処理されることを確認
        assert not result["sma_5"].isna().all()
        assert not result["rsi"].isna().all()

    def test_technical_indicators_with_zero_values(self):
        """ゼロ値を含むデータでのテスト"""
        # ゼロ値を含むデータ
        data_with_zero = self.df.copy()
        data_with_zero.loc[10:15, "close"] = 0

        # テクニカル指標の計算
        result = calculate_technical_indicators(data_with_zero)

        # ゼロ値が適切に処理されることを確認
        assert not result["sma_5"].isna().all()
        assert not result["rsi"].isna().all()

    def test_technical_indicators_with_negative_values(self):
        """負の値を含むデータでのテスト"""
        # 負の値を含むデータ
        data_with_negative = self.df.copy()
        data_with_negative["close"] = data_with_negative["close"] - 200

        # テクニカル指標の計算
        result = calculate_technical_indicators(data_with_negative)

        # 負の値が適切に処理されることを確認
        assert not result["sma_5"].isna().all()
        assert not result["rsi"].isna().all()

    def test_technical_indicators_performance(self):
        """パフォーマンステスト"""
        # 大きなデータセットでのテスト
        large_dates = pd.date_range("2020-01-01", periods=1000, freq="D")
        large_close = 100 + np.cumsum(np.random.randn(1000) * 0.5)

        large_df = pd.DataFrame(
            {
                "date": large_dates,
                "close": large_close,
                "high": large_close + np.random.rand(1000) * 2,
                "low": large_close - np.random.rand(1000) * 2,
                "volume": np.random.randint(1000, 10000, 1000),
            }
        )

        # テクニカル指標の計算（時間測定）
        import time

        start_time = time.time()
        result = calculate_technical_indicators(large_df)
        end_time = time.time()

        # 計算時間が妥当であることを確認（5秒以内）
        assert end_time - start_time < 5.0
        assert len(result) == 1000
