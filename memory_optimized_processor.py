#!/usr/bin/env python3
"""
メモリ効率化プロセッサー
大規模データ処理時のメモリ使用量と処理時間を最適化
"""

import pandas as pd
import numpy as np
import psutil
import gc
import logging
from typing import Dict, List, Optional, Generator, Tuple, Any
from unified_parallel_processing_system import (
    execute_parallel, 
    get_parallel_config, 
    set_parallel_config
)
from unified_system import get_unified_system
import multiprocessing as mp
from functools import lru_cache
import tracemalloc
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """メモリ使用量監視クラス"""

    def __init__(self):
        self.peak_memory = 0
        self.memory_history = []
        self.process = psutil.Process()
        self.initial_memory = self.get_current_memory()

    def get_current_memory(self) -> int:
        """現在のメモリ使用量を取得（MB）"""
        return self.process.memory_info().rss / 1024 / 1024

    def track_memory(self, operation_name: str = ""):
        """メモリ使用量を追跡"""
        current_memory = self.get_current_memory()
        self.memory_history.append(
            {
                "operation": operation_name,
                "memory_mb": current_memory,
                "timestamp": pd.Timestamp.now(),
            }
        )

        if current_memory > self.peak_memory:
            self.peak_memory = current_memory

        logger.debug(f"メモリ使用量: {current_memory:.1f}MB ({operation_name})")
        return current_memory

    def get_memory_stats(self) -> Dict[str, Any]:
        """メモリ統計を取得"""
        current_memory = self.get_current_memory()
        return {
            "current_mb": current_memory,
            "peak_mb": self.peak_memory,
            "increase_mb": current_memory - self.initial_memory,
            "history_count": len(self.memory_history),
        }


class MemoryOptimizedProcessor:
    """メモリ効率化プロセッサー"""

    def __init__(self, chunk_size: int = 10000, memory_limit_mb: int = 2048):
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.monitor = MemoryMonitor()
        self.logger = logging.getLogger(__name__)

    def process_large_data(
        self, data_source: str, processing_func, **kwargs
    ) -> Generator[pd.DataFrame, None, None]:
        """チャンク処理による大規模データ処理"""
        self.logger.info(f"📊 大規模データ処理開始 (チャンクサイズ: {self.chunk_size})")

        try:
            for chunk in pd.read_csv(data_source, chunksize=self.chunk_size):
                # メモリ使用量をチェック
                if self.monitor.get_current_memory() > self.memory_limit_mb:
                    self.logger.warning(
                        "⚠️ メモリ制限に達しました。ガベージコレクションを実行します。"
                    )
                    gc.collect()

                # チャンク処理
                processed_chunk = self._process_chunk(chunk, processing_func, **kwargs)
                yield processed_chunk

                # メモリ追跡
                self.monitor.track_memory("chunk_processing")

        except Exception as e:
            self.logger.error(f"❌ 大規模データ処理エラー: {e}")
            raise

    def _process_chunk(
        self, chunk: pd.DataFrame, processing_func, **kwargs
    ) -> pd.DataFrame:
        """チャンクの処理"""
        try:
            return processing_func(chunk, **kwargs)
        except Exception as e:
            self.logger.error(f"❌ チャンク処理エラー: {e}")
            raise

    @contextmanager
    def memory_context(self, operation_name: str):
        """メモリコンテキストマネージャー"""
        initial_memory = self.monitor.get_current_memory()
        self.logger.info(f"🔧 {operation_name} 開始 (メモリ: {initial_memory:.1f}MB)")

        try:
            yield
        finally:
            final_memory = self.monitor.get_current_memory()
            memory_increase = final_memory - initial_memory
            self.logger.info(
                f"✅ {operation_name} 完了 (メモリ増加: {memory_increase:.1f}MB)"
            )

            # メモリ使用量が大きい場合はガベージコレクション
            if memory_increase > 100:  # 100MB以上増加した場合
                self.logger.info("🧹 ガベージコレクションを実行")
                gc.collect()


class DataTypeOptimizer:
    """データ型最適化クラス"""

    @staticmethod
    def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """データ型を最適化してメモリ使用量を削減"""
        logger.info("🔧 データ型最適化を開始")

        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024

        for col in df.columns:
            if df[col].dtype == "object":
                # 文字列カラムの最適化
                if df[col].nunique() / len(df) < 0.5:  # カーディナリティが低い場合
                    df[col] = df[col].astype("category")
            elif df[col].dtype == "int64":
                # 整数型の最適化
                if df[col].min() >= 0:
                    if df[col].max() < 255:
                        df[col] = df[col].astype("uint8")
                    elif df[col].max() < 65535:
                        df[col] = df[col].astype("uint16")
                    elif df[col].max() < 4294967295:
                        df[col] = df[col].astype("uint32")
                else:
                    if df[col].min() > -128 and df[col].max() < 127:
                        df[col] = df[col].astype("int8")
                    elif df[col].min() > -32768 and df[col].max() < 32767:
                        df[col] = df[col].astype("int16")
                    elif df[col].min() > -2147483648 and df[col].max() < 2147483647:
                        df[col] = df[col].astype("int32")
            elif df[col].dtype == "float64":
                # 浮動小数点型の最適化
                if df[col].min() >= 0:
                    df[col] = pd.to_numeric(df[col], downcast="float")
                else:
                    df[col] = pd.to_numeric(df[col], downcast="float")

        optimized_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        reduction = original_memory - optimized_memory
        reduction_pct = (reduction / original_memory) * 100

        logger.info(
            f"✅ データ型最適化完了: {original_memory:.1f}MB → {optimized_memory:.1f}MB ({reduction_pct:.1f}%削減)"
        )

        return df


class ParallelProcessor:
    """並列処理クラス"""

    def __init__(self, max_workers: int = None):
        # 設定ファイルからmax_workersを読み込み
        try:
            import yaml

            with open("config_final.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self.max_workers = max_workers or config.get("performance", {}).get(
                "max_workers", 4
            )
        except Exception:
            self.max_workers = max_workers or min(4, mp.cpu_count())
        self.logger = logging.getLogger(__name__)

    def process_indicators_parallel(
        self, df: pd.DataFrame, indicator_funcs: List[callable]
    ) -> pd.DataFrame:
        """技術指標を並列処理で計算"""
        self.logger.info(f"🚀 並列処理開始 (ワーカー数: {self.max_workers})")

        # データを分割
        chunk_size = len(df) // self.max_workers
        chunks = [df.iloc[i : i + chunk_size] for i in range(0, len(df), chunk_size)]

        results = []
        with get_unified_system().execute_parallel(self.max_workers) as executor:
            # 各チャンクに対して並列処理
            futures = []
            for i, chunk in enumerate(chunks):
                future = executor.submit(
                    self._process_chunk_indicators, chunk, indicator_funcs
                )
                futures.append((i, future))

            # 結果を収集
            for i, future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"❌ チャンク {i} の処理エラー: {e}")
                    results.append(chunk)  # エラー時は元のチャンクを返す

        # 結果を結合
        final_result = pd.concat(results, ignore_index=True)
        self.logger.info(f"✅ 並列処理完了: {len(final_result)}行")

        return final_result

    def _process_chunk_indicators(
        self, chunk: pd.DataFrame, indicator_funcs: List[callable]
    ) -> pd.DataFrame:
        """チャンクの技術指標計算"""
        result = chunk.copy()

        for func in indicator_funcs:
            try:
                result = func(result)
            except Exception as e:
                self.logger.warning(f"⚠️ 指標計算エラー: {e}")
                continue

        return result


class CacheManager:
    """計算結果キャッシュ管理"""

    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
        self.logger = logging.getLogger(__name__)

    def get_cached_result(self, key: str, compute_func: callable, *args, **kwargs):
        """キャッシュから結果を取得、なければ計算"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            self.logger.debug(f"📋 キャッシュヒット: {key}")
            return self.cache[key]

        # キャッシュサイズ制限
        if len(self.cache) >= self.max_size:
            self._evict_least_used()

        # 計算実行
        result = compute_func(*args, **kwargs)
        self.cache[key] = result
        self.access_count[key] = 1

        self.logger.debug(f"💾 キャッシュに保存: {key}")
        return result

    def _evict_least_used(self):
        """最も使用頻度の低いキャッシュを削除"""
        if not self.cache:
            return

        least_used_key = min(
            self.access_count.keys(), key=lambda k: self.access_count[k]
        )
        del self.cache[least_used_key]
        del self.access_count[least_used_key]

        self.logger.debug(f"🗑️ キャッシュ削除: {least_used_key}")

    def clear_cache(self):
        """キャッシュをクリア"""
        self.cache.clear()
        self.access_count.clear()
        self.logger.info("🧹 キャッシュをクリアしました")


class OptimizedTechnicalIndicators:
    """最適化された技術指標計算クラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_processor = MemoryOptimizedProcessor()
        self.cache_manager = CacheManager()
        self.parallel_processor = ParallelProcessor()
        self.dtype_optimizer = DataTypeOptimizer()

    def calculate_indicators_optimized(
        self, df: pd.DataFrame, config: Dict = None
    ) -> pd.DataFrame:
        """最適化された技術指標計算"""
        self.logger.info("🚀 最適化された技術指標計算を開始")

        with self.memory_processor.memory_context("技術指標計算"):
            # データ型最適化
            df = self.dtype_optimizer.optimize_dtypes(df)

            # キャッシュキーを生成
            cache_key = f"indicators_{hash(str(df.shape))}"

            # キャッシュから結果を取得または計算
            result = self.cache_manager.get_cached_result(
                cache_key, self._calculate_indicators_internal, df, config
            )

            return result

    def _calculate_indicators_internal(
        self, df: pd.DataFrame, config: Dict = None
    ) -> pd.DataFrame:
        """内部的な指標計算"""
        result_df = df.copy()

        # 並列処理可能な指標計算関数のリスト
        indicator_funcs = [
            self._calculate_moving_averages_optimized,
            self._calculate_rsi_optimized,
            self._calculate_macd_optimized,
            self._calculate_bollinger_bands_optimized,
        ]

        # 並列処理で指標計算
        result_df = self.parallel_processor.process_indicators_parallel(
            result_df, indicator_funcs
        )

        return result_df

    def _calculate_moving_averages_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """最適化された移動平均計算"""
        result_df = df.copy()

        # 必要なカラムのみを処理
        if "Close" in df.columns:
            windows = [5, 10, 20, 50]
            for window in windows:
                if len(df) >= window:
                    result_df[f"SMA_{window}"] = (
                        df["Close"].rolling(window=window, min_periods=1).mean()
                    )

        return result_df

    def _calculate_rsi_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """最適化されたRSI計算"""
        result_df = df.copy()

        if "Close" in df.columns and len(df) >= 14:
            # ベクトル化されたRSI計算
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            # 指数移動平均を使用してより効率的に計算
            avg_gain = gain.ewm(span=14, min_periods=1).mean()
            avg_loss = loss.ewm(span=14, min_periods=1).mean()

            rs = avg_gain / avg_loss
            result_df["RSI"] = 100 - (100 / (1 + rs))

        return result_df

    def _calculate_macd_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """最適化されたMACD計算"""
        result_df = df.copy()

        if "Close" in df.columns and len(df) >= 26:
            # 指数移動平均を効率的に計算
            ema_12 = df["Close"].ewm(span=12, min_periods=1).mean()
            ema_26 = df["Close"].ewm(span=26, min_periods=1).mean()

            result_df["MACD"] = ema_12 - ema_26
            result_df["MACD_Signal"] = (
                result_df["MACD"].ewm(span=9, min_periods=1).mean()
            )
            result_df["MACD_Histogram"] = result_df["MACD"] - result_df["MACD_Signal"]

        return result_df

    def _calculate_bollinger_bands_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """最適化されたボリンジャーバンド計算"""
        result_df = df.copy()

        if "Close" in df.columns and len(df) >= 20:
            # 移動平均と標準偏差を一度に計算
            sma = df["Close"].rolling(window=20, min_periods=1).mean()
            std = df["Close"].rolling(window=20, min_periods=1).std()

            result_df["BB_Middle"] = sma
            result_df["BB_Upper"] = sma + (std * 2)
            result_df["BB_Lower"] = sma - (std * 2)
            result_df["BB_Width"] = (
                result_df["BB_Upper"] - result_df["BB_Lower"]
            ) / result_df["BB_Middle"]

        return result_df


def create_optimized_processor(
    chunk_size: int = 10000, memory_limit_mb: int = 2048
) -> MemoryOptimizedProcessor:
    """最適化されたプロセッサーを作成"""
    return MemoryOptimizedProcessor(
        chunk_size=chunk_size, memory_limit_mb=memory_limit_mb
    )


def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrameのメモリ使用量を最適化"""
    optimizer = DataTypeOptimizer()
    return optimizer.optimize_dtypes(df)


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)

    # サンプルデータ生成
    dates = pd.date_range("2020-01-01", periods=10000, freq="D")
    np.random.seed(42)

    sample_data = pd.DataFrame(
        {
            "Date": dates,
            "Open": np.random.uniform(100, 200, 10000),
            "High": np.random.uniform(100, 200, 10000),
            "Low": np.random.uniform(100, 200, 10000),
            "Close": np.random.uniform(100, 200, 10000),
            "Volume": np.random.randint(1000000, 10000000, 10000),
        }
    )

    # メモリ最適化テスト
    processor = create_optimized_processor()
    monitor = MemoryMonitor()

    print("📊 メモリ最適化テスト開始")
    print(f"初期メモリ: {monitor.get_current_memory():.1f}MB")

    # データ型最適化
    optimized_data = optimize_dataframe_memory(sample_data)
    print(f"最適化後メモリ: {monitor.get_current_memory():.1f}MB")

    # 技術指標計算
    calculator = OptimizedTechnicalIndicators()
    result = calculator.calculate_indicators_optimized(optimized_data)

    print(f"最終メモリ: {monitor.get_current_memory():.1f}MB")
    print(f"メモリ統計: {monitor.get_memory_stats()}")
    print(f"結果データ形状: {result.shape}")
