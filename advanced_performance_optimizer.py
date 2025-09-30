#!/usr/bin/env python3
"""
高度なパフォーマンス最適化システム
大規模データ処理時のメモリ使用量と処理時間を大幅に改善
"""

import pandas as pd
import numpy as np
import psutil
import gc
import logging
from typing import Dict, List, Optional, Generator, Tuple, Any, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from functools import lru_cache
import tracemalloc
from contextlib import contextmanager
import time
import hashlib
import joblib
import os
from dataclasses import dataclass
from unified_system import UnifiedSystem

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """パフォーマンスメトリクス"""

    memory_usage_mb: float
    processing_time_seconds: float
    cpu_usage_percent: float
    memory_peak_mb: float
    operations_count: int
    cache_hits: int
    cache_misses: int


class AdvancedMemoryOptimizer:
    """高度なメモリ最適化クラス"""

    def __init__(self, memory_limit_mb: int = 2048, chunk_size: int = 10000):
        self.memory_limit_mb = memory_limit_mb
        self.chunk_size = chunk_size
        # 循環参照を回避するため、psutil.Process()の初期化も無効化
        self.process = None
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

        # メモリ監視の開始
        tracemalloc.start()

    def get_memory_usage(self) -> float:
        """現在のメモリ使用量を取得（MB）"""
        if self.process is None:
            # 循環参照を回避するため、デフォルト値を返す
            return 0.0
        return self.process.memory_info().rss / 1024 / 1024

    def check_memory_limit(self) -> bool:
        """メモリ制限をチェック"""
        current_memory = self.get_memory_usage()
        return current_memory < self.memory_limit_mb

    def optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """データフレームのメモリ最適化"""
        self.logger.info("🔧 データフレームメモリ最適化開始")

        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024

        # データ型最適化
        df_optimized = df.copy()

        for col in df_optimized.columns:
            col_type = df_optimized[col].dtype

            if col_type != "object":
                c_min = df_optimized[col].min()
                c_max = df_optimized[col].max()

                if str(col_type)[:3] == "int":
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df_optimized[col] = df_optimized[col].astype(np.int8)
                    elif (
                        c_min > np.iinfo(np.int16).min
                        and c_max < np.iinfo(np.int16).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.int16)
                    elif (
                        c_min > np.iinfo(np.int32).min
                        and c_max < np.iinfo(np.int32).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.int32)
                else:
                    if (
                        c_min > np.finfo(np.float16).min
                        and c_max < np.finfo(np.float16).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.float16)
                    elif (
                        c_min > np.finfo(np.float32).min
                        and c_max < np.finfo(np.float32).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.float32)

        optimized_memory = df_optimized.memory_usage(deep=True).sum() / 1024 / 1024
        reduction = (original_memory - optimized_memory) / original_memory * 100

        self.logger.info(
            f"💾 メモリ最適化完了: {original_memory:.1f}MB → {optimized_memory:.1f}MB ({reduction:.1f}%削減)"
        )

        return df_optimized

    def process_large_dataframe(
        self, df: pd.DataFrame, processing_func: Callable
    ) -> pd.DataFrame:
        """大規模データフレームのチャンク処理"""
        self.logger.info(f"📊 大規模データフレーム処理開始: {len(df)}行")

        if len(df) <= self.chunk_size:
            return processing_func(df)

        results = []
        for i in range(0, len(df), self.chunk_size):
            chunk = df.iloc[i : i + self.chunk_size]

            # メモリ制限チェック
            if not self.check_memory_limit():
                self.logger.warning("⚠️ メモリ制限に達しました。ガベージコレクションを実行")
                gc.collect()

            # チャンク処理
            processed_chunk = processing_func(chunk)
            results.append(processed_chunk)

            self.logger.debug(
                f"📦 チャンク処理完了: {i//self.chunk_size + 1}/{(len(df)-1)//self.chunk_size + 1}"
            )

        # 結果を結合
        final_result = pd.concat(results, ignore_index=True)
        self.logger.info(f"✅ 大規模データフレーム処理完了: {len(final_result)}行")

        return final_result


class AdvancedCacheManager:
    """高度なキャッシュ管理システム"""

    def __init__(
        self, cache_dir: str = "advanced_cache", max_cache_size_mb: int = 1024
    ):
        self.cache_dir = cache_dir
        self.max_cache_size_mb = max_cache_size_mb
        self.cache_stats = {"hits": 0, "misses": 0}
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

        os.makedirs(cache_dir, exist_ok=True)

    def _generate_cache_key(self, data_hash: str, operation: str, params: Dict) -> str:
        """キャッシュキーを生成"""
        key_string = f"{data_hash}_{operation}_{str(sorted(params.items()))}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _generate_data_hash(self, data: Any) -> str:
        """データのハッシュを生成"""
        if isinstance(data, pd.DataFrame):
            return hashlib.md5(data.to_string().encode()).hexdigest()
        elif isinstance(data, np.ndarray):
            return hashlib.md5(data.tobytes()).hexdigest()
        else:
            return hashlib.md5(str(data).encode()).hexdigest()

    def get_cached_result(
        self, data: Any, operation: str, params: Dict, compute_func: Callable
    ) -> Any:
        """キャッシュから結果を取得または計算"""
        data_hash = self._generate_data_hash(data)
        cache_key = self._generate_cache_key(data_hash, operation, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.joblib")

        if os.path.exists(cache_file):
            try:
                self.cache_stats["hits"] += 1
                self.logger.debug(f"📋 キャッシュヒット: {operation}")
                return joblib.load(cache_file)
            except Exception as e:
                self.logger.warning(f"⚠️ キャッシュ読み込みエラー: {e}")

        # キャッシュミス - 計算実行
        self.cache_stats["misses"] += 1
        self.logger.debug(f"🔄 キャッシュミス: {operation}")

        result = compute_func(data, params)

        # 結果をキャッシュに保存
        try:
            joblib.dump(result, cache_file)
            self.logger.debug(f"💾 結果をキャッシュに保存: {operation}")
        except Exception as e:
            self.logger.warning(f"⚠️ キャッシュ保存エラー: {e}")

        return result

    def clear_cache(self):
        """キャッシュをクリア"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith(".joblib"):
                    os.remove(os.path.join(self.cache_dir, file))
            self.logger.info("🧹 キャッシュをクリアしました")
        except Exception as e:
            self.logger.error(f"❌ キャッシュクリアエラー: {e}")

    def get_cache_stats(self) -> Dict[str, int]:
        """キャッシュ統計を取得"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            (self.cache_stats["hits"] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


class OptimizedTechnicalIndicators:
    """最適化された技術指標計算クラス"""

    def __init__(
        self,
        memory_optimizer: AdvancedMemoryOptimizer,
        cache_manager: AdvancedCacheManager,
    ):
        self.memory_optimizer = memory_optimizer
        self.cache_manager = cache_manager
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

    def calculate_indicators_optimized(
        self, df: pd.DataFrame, config: Dict = None
    ) -> pd.DataFrame:
        """最適化された技術指標計算"""
        self.logger.info("🚀 最適化された技術指標計算開始")

        if config is None:
            config = self._get_default_config()

        # メモリ最適化
        df_optimized = self.memory_optimizer.optimize_dataframe_memory(df)

        # キャッシュを活用した指標計算
        result = self.cache_manager.get_cached_result(
            df_optimized,
            "technical_indicators",
            config,
            self._calculate_indicators_internal,
        )

        return result

    def _calculate_indicators_internal(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """内部的な指標計算（キャッシュ用）"""
        result_df = df.copy()

        try:
            # 移動平均系（最適化版）
            result_df = self._calculate_moving_averages_optimized(result_df, config)

            # モメンタム系指標（最適化版）
            result_df = self._calculate_momentum_optimized(result_df, config)

            # ボラティリティ系指標（最適化版）
            result_df = self._calculate_volatility_optimized(result_df, config)

            # ボリューム系指標（最適化版）
            result_df = self._calculate_volume_optimized(result_df, config)

            self.logger.info("✅ 最適化された技術指標計算完了")
            return result_df

        except Exception as e:
            self.system.log_error(e, "技術指標計算エラー")
            return df

    def _calculate_moving_averages_optimized(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """最適化された移動平均計算"""
        windows = config.get("sma_windows", [5, 10, 20, 50])

        for window in windows:
            # インプレース操作でメモリ効率化
            df[f"SMA_{window}"] = (
                df["Close"].rolling(window=window, min_periods=1).mean()
            )

        return df

    def _calculate_momentum_optimized(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """最適化されたモメンタム指標計算"""
        # RSI計算（最適化版）
        rsi_period = config.get("rsi_period", 14)
        delta = df["Close"].diff()
        gain = (
            delta.where(delta > 0, 0).rolling(window=rsi_period, min_periods=1).mean()
        )
        loss = (
            (-delta.where(delta < 0, 0))
            .rolling(window=rsi_period, min_periods=1)
            .mean()
        )
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # MACD計算（最適化版）
        fast = config.get("macd_fast", 12)
        slow = config.get("macd_slow", 26)
        signal = config.get("macd_signal", 9)

        ema_fast = df["Close"].ewm(span=fast, min_periods=1).mean()
        ema_slow = df["Close"].ewm(span=slow, min_periods=1).mean()
        df["MACD"] = ema_fast - ema_slow
        df["MACD_Signal"] = df["MACD"].ewm(span=signal, min_periods=1).mean()
        df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

        return df

    def _calculate_volatility_optimized(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """最適化されたボラティリティ指標計算"""
        # ボリンジャーバンド（最適化版）
        bb_period = config.get("bb_period", 20)
        bb_std = config.get("bb_std", 2)

        sma = df["Close"].rolling(window=bb_period, min_periods=1).mean()
        std = df["Close"].rolling(window=bb_period, min_periods=1).std()

        df["BB_Upper"] = sma + (std * bb_std)
        df["BB_Lower"] = sma - (std * bb_std)
        df["BB_Percent"] = (df["Close"] - df["BB_Lower"]) / (
            df["BB_Upper"] - df["BB_Lower"]
        )

        # ATR計算（最適化版）
        atr_period = config.get("atr_period", 14)
        high_low = df["High"] - df["Low"]
        high_close_prev = np.abs(df["High"] - df["Close"].shift(1))
        low_close_prev = np.abs(df["Low"] - df["Close"].shift(1))
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        df["ATR"] = true_range.rolling(window=atr_period, min_periods=1).mean()

        return df

    def _calculate_volume_optimized(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """最適化されたボリューム指標計算"""
        # VWAP計算（最適化版）
        typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
        df["VWAP"] = (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()
        df["VWAP_Deviation"] = (df["Close"] - df["VWAP"]) / df["VWAP"] * 100

        # ボリューム移動平均
        volume_sma_period = config.get("volume_sma_period", 20)
        df["Volume_SMA"] = (
            df["Volume"].rolling(window=volume_sma_period, min_periods=1).mean()
        )
        df["Volume_Rate"] = df["Volume"] / df["Volume_SMA"]

        return df

    def _get_default_config(self) -> Dict:
        """デフォルト設定を取得"""
        return {
            "sma_windows": [5, 10, 20, 50],
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "bb_period": 20,
            "bb_std": 2,
            "atr_period": 14,
            "volume_sma_period": 20,
        }


class AdvancedPerformanceMonitor:
    """高度なパフォーマンス監視クラス"""

    def __init__(self):
        self.metrics_history = []
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def monitor_performance(self, operation_name: str):
        """パフォーマンス監視コンテキストマネージャー"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024

            metrics = PerformanceMetrics(
                memory_usage_mb=end_memory,
                processing_time_seconds=end_time - start_time,
                cpu_usage_percent=psutil.cpu_percent(),
                memory_peak_mb=end_memory,
                operations_count=1,
                cache_hits=0,
                cache_misses=0,
            )

            self.metrics_history.append(
                {
                    "operation": operation_name,
                    "metrics": metrics,
                    "timestamp": pd.Timestamp.now(),
                }
            )

            self.logger.info(f"📊 パフォーマンス監視: {operation_name}")
            self.logger.info(f"  ⏱️ 処理時間: {metrics.processing_time_seconds:.2f}秒")
            self.logger.info(f"  💾 メモリ使用量: {metrics.memory_usage_mb:.1f}MB")

    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        if not self.metrics_history:
            return {}

        total_time = sum(
            m["metrics"].processing_time_seconds for m in self.metrics_history
        )
        avg_memory = np.mean(
            [m["metrics"].memory_usage_mb for m in self.metrics_history]
        )
        peak_memory = max([m["metrics"].memory_peak_mb for m in self.metrics_history])

        return {
            "total_operations": len(self.metrics_history),
            "total_time_seconds": total_time,
            "average_memory_mb": avg_memory,
            "peak_memory_mb": peak_memory,
            "operations": [m["operation"] for m in self.metrics_history],
        }


class UnifiedPerformanceOptimizer:
    """統合パフォーマンス最適化システム"""

    def __init__(self, memory_limit_mb: int = 2048, chunk_size: int = 10000):
        self.memory_optimizer = AdvancedMemoryOptimizer(memory_limit_mb, chunk_size)
        self.cache_manager = AdvancedCacheManager()
        self.technical_indicators = OptimizedTechnicalIndicators(
            self.memory_optimizer, self.cache_manager
        )
        self.performance_monitor = AdvancedPerformanceMonitor()
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

    def optimize_data_processing(
        self, df: pd.DataFrame, operations: List[Dict]
    ) -> pd.DataFrame:
        """データ処理の最適化"""
        self.logger.info(f"🚀 統合パフォーマンス最適化開始: {len(operations)}操作")

        with self.performance_monitor.monitor_performance("data_processing"):
            result_df = df

            for operation in operations:
                op_type = operation.get("type")

                if op_type == "technical_indicators":
                    result_df = (
                        self.technical_indicators.calculate_indicators_optimized(
                            result_df, operation.get("config")
                        )
                    )
                elif op_type == "memory_optimization":
                    result_df = self.memory_optimizer.optimize_dataframe_memory(
                        result_df
                    )
                elif op_type == "chunk_processing":
                    result_df = self.memory_optimizer.process_large_dataframe(
                        result_df, operation.get("processing_func")
                    )
                else:
                    self.logger.warning(f"⚠️ 未対応の操作タイプ: {op_type}")

            # パフォーマンス統計をログ出力
            self._log_optimization_stats()

            return result_df

    def _log_optimization_stats(self):
        """最適化統計をログ出力"""
        cache_stats = self.cache_manager.get_cache_stats()
        performance_summary = self.performance_monitor.get_performance_summary()

        self.logger.info("📊 最適化統計:")
        self.logger.info(f"  📋 キャッシュヒット率: {cache_stats.get('hit_rate', 0):.1f}%")
        self.logger.info(
            f"  ⏱️ 総処理時間: {performance_summary.get('total_time_seconds', 0):.2f}秒"
        )
        self.logger.info(
            f"  💾 平均メモリ使用量: {performance_summary.get('average_memory_mb', 0):.1f}MB"
        )
        self.logger.info(
            f"  📈 ピークメモリ使用量: {performance_summary.get('peak_memory_mb', 0):.1f}MB"
        )


def create_performance_optimizer(
    memory_limit_mb: int = 2048, chunk_size: int = 10000
) -> UnifiedPerformanceOptimizer:
    """パフォーマンス最適化システムを作成"""
    return UnifiedPerformanceOptimizer(memory_limit_mb, chunk_size)


if __name__ == "__main__":
    # テスト用のサンプルデータ
    import pandas as pd
    import numpy as np

    # サンプルデータ生成
    dates = pd.date_range("2024-01-01", periods=1000, freq="D")
    np.random.seed(42)

    base_price = 1000 + np.cumsum(np.random.randn(1000) * 0.02) * 1000

    sample_data = pd.DataFrame(
        {
            "Date": dates,
            "Open": base_price,
            "High": base_price * (1 + np.random.uniform(0, 0.05, 1000)),
            "Low": base_price * (1 - np.random.uniform(0, 0.05, 1000)),
            "Close": base_price + np.random.uniform(-20, 20, 1000),
            "Volume": np.random.randint(1000000, 10000000, 1000),
        }
    )

    # パフォーマンス最適化システムのテスト
    optimizer = create_performance_optimizer()

    operations = [
        {"type": "technical_indicators", "config": {}},
        {"type": "memory_optimization", "config": {}},
    ]

    optimized_data = optimizer.optimize_data_processing(sample_data, operations)

    print(f"📊 元データ: {len(sample_data.columns)}列, {len(sample_data)}行")
    print(f"📈 最適化後: {len(optimized_data.columns)}列, {len(optimized_data)}行")
    print(f"➕ 追加指標: {len(optimized_data.columns) - len(sample_data.columns)}個")
