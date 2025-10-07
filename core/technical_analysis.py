"""
テクニカル分析ライブラリ（pandas-ta代替）
Python 3.11対応の自作実装
"""

import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalAnalysis:
    """テクニカル分析クラス"""

    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """単純移動平均（Simple Moving Average）"""
        return data.rolling(window=window).mean()

    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """指数移動平均（Exponential Moving Average）"""
        return data.ewm(span=window).mean()

    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """RSI（Relative Strength Index）"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(
        data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD（Moving Average Convergence Divergence）"""
        ema_fast = TechnicalAnalysis.ema(data, fast)
        ema_slow = TechnicalAnalysis.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalAnalysis.ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(
        data: pd.Series, window: int = 20, std_dev: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """ボリンジャーバンド"""
        sma = TechnicalAnalysis.sma(data, window)
        std = data.rolling(window=window).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    @staticmethod
    def stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_window: int = 14,
        d_window: int = 3,
    ) -> Tuple[pd.Series, pd.Series]:
        """ストキャスティクス"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        return k_percent, d_percent

    @staticmethod
    def atr(
        high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
    ) -> pd.Series:
        """ATR（Average True Range）"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return true_range.rolling(window=window).mean()

    @staticmethod
    def williams_r(
        high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
    ) -> pd.Series:
        """Williams %R"""
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()
        return -100 * ((highest_high - close) / (highest_high - lowest_low))

    @staticmethod
    def cci(
        high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20
    ) -> pd.Series:
        """CCI（Commodity Channel Index）"""
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=window).mean()
        mean_deviation = typical_price.rolling(window=window).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        )
        return (typical_price - sma_tp) / (0.015 * mean_deviation)

    @staticmethod
    def adx(
        high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
    ) -> pd.Series:
        """ADX（Average Directional Index）"""
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement
        dm_plus = high.diff()
        dm_minus = -low.diff()

        dm_plus = dm_plus.where((dm_plus > dm_minus) & (dm_plus > 0), 0)
        dm_minus = dm_minus.where((dm_minus > dm_plus) & (dm_minus > 0), 0)

        # Smoothed values
        atr = tr.rolling(window=window).mean()
        di_plus = 100 * (dm_plus.rolling(window=window).mean() / atr)
        di_minus = 100 * (dm_minus.rolling(window=window).mean() / atr)

        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        return dx.rolling(window=window).mean()

    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """OBV（On-Balance Volume）"""
        if len(close) == 0 or len(volume) == 0:
            return pd.Series(dtype=float)

        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    @staticmethod
    def vwap(
        high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
    ) -> pd.Series:
        """VWAP（Volume Weighted Average Price）"""
        typical_price = (high + low + close) / 3
        return (typical_price * volume).cumsum() / volume.cumsum()

    @staticmethod
    def ichimoku(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        conversion_period: int = 9,
        base_period: int = 26,
        leading_span_b_period: int = 52,
    ) -> dict:
        """一目均衡表"""
        conversion_line = (
            high.rolling(window=conversion_period).max()
            + low.rolling(window=conversion_period).min()
        ) / 2
        base_line = (
            high.rolling(window=base_period).max()
            + low.rolling(window=base_period).min()
        ) / 2

        leading_span_a = (conversion_line + base_line) / 2
        leading_span_b = (
            high.rolling(window=leading_span_b_period).max()
            + low.rolling(window=leading_span_b_period).min()
        ) / 2

        return {
            "conversion_line": conversion_line,
            "base_line": base_line,
            "leading_span_a": leading_span_a,
            "leading_span_b": leading_span_b,
        }

    @staticmethod
    def support_resistance(
        data: pd.Series, window: int = 20, threshold: float = 0.02
    ) -> dict:
        """サポート・レジスタンスライン"""
        rolling_max = data.rolling(window=window).max()
        rolling_min = data.rolling(window=window).min()

        resistance = rolling_max[rolling_max == data]
        support = rolling_min[rolling_min == data]

        return {"resistance": resistance.dropna(), "support": support.dropna()}


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """データフレームにテクニカル指標を追加"""
    result = df.copy()

    if "close" in df.columns:
        # 移動平均
        result["sma_5"] = TechnicalAnalysis.sma(df["close"], 5)
        result["sma_10"] = TechnicalAnalysis.sma(df["close"], 10)
        result["sma_20"] = TechnicalAnalysis.sma(df["close"], 20)
        result["sma_50"] = TechnicalAnalysis.sma(df["close"], 50)

        # RSI
        result["rsi"] = TechnicalAnalysis.rsi(df["close"])

        # MACD
        macd, signal, histogram = TechnicalAnalysis.macd(df["close"])
        result["macd"] = macd
        result["macd_signal"] = signal
        result["macd_histogram"] = histogram

    if all(col in df.columns for col in ["high", "low", "close"]):
        # ボリンジャーバンド
        bb_upper, bb_middle, bb_lower = TechnicalAnalysis.bollinger_bands(df["close"])
        result["bb_upper"] = bb_upper
        result["bb_middle"] = bb_middle
        result["bb_lower"] = bb_lower

        # ストキャスティクス
        if "high" in df.columns and "low" in df.columns:
            k_percent, d_percent = TechnicalAnalysis.stochastic(
                df["high"], df["low"], df["close"]
            )
            result["stoch_k"] = k_percent
            result["stoch_d"] = d_percent

    if all(col in df.columns for col in ["high", "low", "close", "volume"]):
        # OBV
        result["obv"] = TechnicalAnalysis.obv(df["close"], df["volume"])

        # VWAP
        result["vwap"] = TechnicalAnalysis.vwap(
            df["high"], df["low"], df["close"], df["volume"]
        )

    return result
