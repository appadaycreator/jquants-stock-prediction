#!/usr/bin/env python3
"""
データフレーム最適化システム
不要なコピーを排除し、インプレース操作を活用した効率的なデータ処理
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Callable, Any, Tuple
from contextlib import contextmanager
import gc
import psutil
from functools import wraps
import time
from dataclasses import dataclass
from unified_system import UnifiedSystem

logger = logging.getLogger(__name__)


@dataclass
class OptimizationStats:
    """最適化統計情報"""

    original_memory_mb: float
    optimized_memory_mb: float
    memory_reduction_mb: float
    memory_reduction_pct: float
    copy_operations_saved: int
    processing_time_saved: float


class DataFrameOptimizer:
    """データフレーム最適化クラス"""

    def __init__(self, track_operations: bool = True):
        self.track_operations = track_operations
        self.operation_count = 0
        self.copy_operations_saved = 0
        self.memory_saved = 0.0
        self.system = UnifiedSystem("DataFrameOptimizer")
        self.logger = logging.getLogger(__name__)

    def optimize_inplace(
        self, df: pd.DataFrame, operation: str, *args, **kwargs
    ) -> pd.DataFrame:
        """インプレース操作の最適化"""
        if self.track_operations:
            self.operation_count += 1

        try:
            # インプレース操作を実行
            if operation == "fillna":
                df.fillna(*args, inplace=True, **kwargs)
            elif operation == "dropna":
                df.dropna(*args, inplace=True, **kwargs)
            elif operation == "drop_duplicates":
                df.drop_duplicates(*args, inplace=True, **kwargs)
            elif operation == "sort_values":
                df.sort_values(*args, inplace=True, **kwargs)
            elif operation == "reset_index":
                df.reset_index(*args, inplace=True, **kwargs)
            elif operation == "astype":
                for col, dtype in args[0].items():
                    df[col] = df[col].astype(dtype)
            else:
                self.logger.warning(f"⚠️ 未対応のインプレース操作: {operation}")
                return df

            if self.track_operations:
                self.copy_operations_saved += 1
                self.logger.debug(f"✅ インプレース操作実行: {operation}")

            return df

        except Exception as e:
            self.system.log_error(e, f"インプレース操作エラー ({operation})")
            self.logger.error(f"❌ インプレース操作エラー: {e}")
            return df

    def smart_copy(self, df: pd.DataFrame, operation_name: str = "") -> pd.DataFrame:
        """必要時のみコピーを作成"""
        # データフレームが変更される可能性をチェック
        if self._will_modify_dataframe(df, operation_name):
            self.logger.debug(f"📋 コピー作成: {operation_name}")
            return df.copy()
        else:
            self.logger.debug(f"♻️ コピー回避: {operation_name}")
            self.copy_operations_saved += 1
            return df

    def _will_modify_dataframe(self, df: pd.DataFrame, operation: str) -> bool:
        """データフレームが変更されるかどうかを判定"""
        # 変更される可能性が高い操作
        modifying_operations = [
            "fillna",
            "dropna",
            "drop_duplicates",
            "sort_values",
            "reset_index",
            "astype",
            "assign",
            "eval",
            "query",
        ]

        # 変更されない可能性が高い操作
        non_modifying_operations = [
            "head",
            "tail",
            "sample",
            "nlargest",
            "nsmallest",
            "describe",
            "info",
            "shape",
            "dtypes",
            "columns",
        ]

        if any(op in operation.lower() for op in modifying_operations):
            return True
        elif any(op in operation.lower() for op in non_modifying_operations):
            return False
        else:
            # 不明な場合は安全のためコピーを作成
            return True


class InPlaceProcessor:
    """インプレース処理クラス"""

    def __init__(self, optimizer: DataFrameOptimizer):
        self.optimizer = optimizer
        self.logger = logging.getLogger(__name__)

    def process_dataframe_inplace(
        self, df: pd.DataFrame, operations: List[Dict]
    ) -> pd.DataFrame:
        """データフレームをインプレースで処理"""
        self.logger.info(f"🔧 インプレース処理開始: {len(operations)}操作")

        for i, operation in enumerate(operations):
            try:
                op_name = operation.get("operation")
                args = operation.get("args", [])
                kwargs = operation.get("kwargs", {})

                self.logger.debug(f"  {i+1}. {op_name}")

                # インプレース操作を実行
                df = self.optimizer.optimize_inplace(df, op_name, *args, **kwargs)

            except Exception as e:
                self.logger.error(f"❌ 操作 {i+1} でエラー: {e}")
                continue

        self.logger.info(f"✅ インプレース処理完了: {len(operations)}操作")
        return df

    def add_column_inplace(
        self,
        df: pd.DataFrame,
        column_name: str,
        values: Union[pd.Series, np.ndarray, List],
    ) -> pd.DataFrame:
        """カラムをインプレースで追加"""
        try:
            df[column_name] = values
            self.logger.debug(f"✅ カラム追加: {column_name}")
            return df
        except Exception as e:
            self.logger.error(f"❌ カラム追加エラー: {e}")
            return df

    def modify_column_inplace(
        self, df: pd.DataFrame, column_name: str, operation: str, *args, **kwargs
    ) -> pd.DataFrame:
        """カラムをインプレースで変更"""
        try:
            if operation == "fillna":
                df[column_name].fillna(*args, inplace=True, **kwargs)
            elif operation == "astype":
                df[column_name] = df[column_name].astype(*args, **kwargs)
            elif operation == "clip":
                df[column_name] = df[column_name].clip(*args, **kwargs)
            elif operation == "replace":
                df[column_name].replace(*args, inplace=True, **kwargs)
            else:
                self.logger.warning(f"⚠️ 未対応のカラム操作: {operation}")

            self.logger.debug(f"✅ カラム変更: {column_name} ({operation})")
            return df

        except Exception as e:
            self.logger.error(f"❌ カラム変更エラー: {e}")
            return df


class MemoryEfficientProcessor:
    """メモリ効率的なプロセッサー"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.process = psutil.Process()

    def process_with_memory_monitoring(
        self, df: pd.DataFrame, processing_func: Callable, *args, **kwargs
    ) -> pd.DataFrame:
        """メモリ監視付き処理"""
        initial_memory = self._get_memory_usage()
        self.logger.info(f"🔧 処理開始 (メモリ: {initial_memory:.1f}MB)")

        try:
            result = processing_func(df, *args, **kwargs)

            final_memory = self._get_memory_usage()
            memory_increase = final_memory - initial_memory

            self.logger.info(f"✅ 処理完了 (メモリ増加: {memory_increase:.1f}MB)")

            # メモリ使用量が大きい場合はガベージコレクション
            if memory_increase > 100:  # 100MB以上増加
                self.logger.info("🧹 ガベージコレクション実行")
                gc.collect()

            return result

        except Exception as e:
            self.logger.error(f"❌ 処理エラー: {e}")
            raise

    def _get_memory_usage(self) -> float:
        """現在のメモリ使用量を取得（MB）"""
        return self.process.memory_info().rss / 1024 / 1024

    def chunk_processing(
        self, df: pd.DataFrame, chunk_size: int, processing_func: Callable
    ) -> pd.DataFrame:
        """チャンク処理による大規模データ処理"""
        self.logger.info(f"📊 チャンク処理開始 (チャンクサイズ: {chunk_size})")

        results = []
        total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size > 0 else 0)

        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i : i + chunk_size]
            processed_chunk = processing_func(chunk)
            results.append(processed_chunk)

            # メモリ監視
            current_memory = self._get_memory_usage()
            if current_memory > 2048:  # 2GB以上
                self.logger.warning(
                    "⚠️ メモリ使用量が高いため、ガベージコレクションを実行"
                )
                gc.collect()

            self.logger.debug(f"  チャンク {i//chunk_size + 1}/{total_chunks} 完了")

        # 結果を結合
        final_result = pd.concat(results, ignore_index=True)
        self.logger.info(f"✅ チャンク処理完了: {len(final_result)}行")

        return final_result


class OptimizedTechnicalIndicators:
    """最適化された技術指標計算（コピー最小化版）"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimizer = DataFrameOptimizer()
        self.inplace_processor = InPlaceProcessor(self.optimizer)

    def calculate_indicators_optimized(
        self, df: pd.DataFrame, config: Dict = None
    ) -> pd.DataFrame:
        """コピーを最小化した技術指標計算"""
        self.logger.info("🚀 最適化された技術指標計算開始")

        # 元のデータフレームを直接操作（必要最小限のコピー）
        result_df = self.optimizer.smart_copy(df, "technical_indicators")

        try:
            # 移動平均系（インプレース）
            result_df = self._calculate_moving_averages_inplace(result_df, config)

            # モメンタム系指標（インプレース）
            result_df = self._calculate_momentum_indicators_inplace(result_df, config)

            # ボラティリティ系指標（インプレース）
            result_df = self._calculate_volatility_indicators_inplace(result_df, config)

            # ボリューム系指標（インプレース）
            result_df = self._calculate_volume_indicators_inplace(result_df, config)

            self.logger.info("✅ 最適化された技術指標計算完了")
            return result_df

        except Exception as e:
            self.logger.error(f"❌ 技術指標計算エラー: {e}")
            return df

    def _calculate_moving_averages_inplace(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """移動平均をインプレースで計算"""
        windows = (
            config.get("sma_windows", [5, 10, 20, 50]) if config else [5, 10, 20, 50]
        )

        for window in windows:
            if len(df) >= window:
                df[f"SMA_{window}"] = (
                    df["Close"].rolling(window=window, min_periods=1).mean()
                )

        return df

    def _calculate_momentum_indicators_inplace(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """モメンタム指標をインプレースで計算"""
        # RSI
        if len(df) >= 14:
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.ewm(span=14, min_periods=1).mean()
            avg_loss = loss.ewm(span=14, min_periods=1).mean()

            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        if len(df) >= 26:
            ema_12 = df["Close"].ewm(span=12, min_periods=1).mean()
            ema_26 = df["Close"].ewm(span=26, min_periods=1).mean()

            df["MACD"] = ema_12 - ema_26
            df["MACD_Signal"] = df["MACD"].ewm(span=9, min_periods=1).mean()
            df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

        return df

    def _calculate_volatility_indicators_inplace(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """ボラティリティ指標をインプレースで計算"""
        # ボリンジャーバンド
        if len(df) >= 20:
            sma = df["Close"].rolling(window=20, min_periods=1).mean()
            std = df["Close"].rolling(window=20, min_periods=1).std()

            df["BB_Middle"] = sma
            df["BB_Upper"] = sma + (std * 2)
            df["BB_Lower"] = sma - (std * 2)
            df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Middle"]

        # ATR
        if len(df) >= 14:
            high_low = df["High"] - df["Low"]
            high_close_prev = np.abs(df["High"] - df["Close"].shift(1))
            low_close_prev = np.abs(df["Low"] - df["Close"].shift(1))

            true_range = np.maximum(
                high_low, np.maximum(high_close_prev, low_close_prev)
            )
            df["ATR"] = true_range.rolling(window=14, min_periods=1).mean()
            df["ATR_Percent"] = df["ATR"] / df["Close"] * 100

        return df

    def _calculate_volume_indicators_inplace(
        self, df: pd.DataFrame, config: Dict
    ) -> pd.DataFrame:
        """ボリューム指標をインプレースで計算"""
        # ボリューム移動平均
        df["Volume_SMA"] = df["Volume"].rolling(window=20, min_periods=1).mean()
        df["Volume_Rate"] = df["Volume"] / df["Volume_SMA"]

        # VWAP
        typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
        df["VWAP"] = (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()
        df["VWAP_Deviation"] = (df["Close"] - df["VWAP"]) / df["VWAP"] * 100

        return df


class OptimizedDataProcessor:
    """最適化されたデータプロセッサー（統合版）"""

    def __init__(self, chunk_size: int = 10000, memory_limit_mb: int = 2048):
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.optimizer = DataFrameOptimizer()
        self.inplace_processor = InPlaceProcessor(self.optimizer)
        self.memory_processor = MemoryEfficientProcessor()
        self.technical_indicators = OptimizedTechnicalIndicators()
        self.logger = logging.getLogger(__name__)

    def process_data_optimized(
        self, df: pd.DataFrame, operations: List[Dict]
    ) -> pd.DataFrame:
        """最適化されたデータ処理"""
        self.logger.info(f"🚀 最適化データ処理開始: {len(operations)}操作")

        # メモリ監視付き処理
        result = self.memory_processor.process_with_memory_monitoring(
            df, self._execute_operations, operations
        )

        # 最適化統計をログ出力
        self._log_optimization_stats()

        return result

    def _execute_operations(
        self, df: pd.DataFrame, operations: List[Dict]
    ) -> pd.DataFrame:
        """操作を実行"""
        result_df = df

        for operation in operations:
            op_type = operation.get("type")

            if op_type == "inplace":
                result_df = self.inplace_processor.process_dataframe_inplace(
                    result_df, [operation]
                )
            elif op_type == "technical_indicators":
                result_df = self.technical_indicators.calculate_indicators_optimized(
                    result_df, operation.get("config")
                )
            elif op_type == "chunk_processing":
                result_df = self.memory_processor.chunk_processing(
                    result_df,
                    operation.get("chunk_size", self.chunk_size),
                    operation.get("processing_func"),
                )
            else:
                self.logger.warning(f"⚠️ 未対応の操作タイプ: {op_type}")

        return result_df

    def _log_optimization_stats(self):
        """最適化統計をログ出力"""
        stats = OptimizationStats(
            original_memory_mb=0.0,  # 実際の実装では追跡
            optimized_memory_mb=0.0,
            memory_reduction_mb=0.0,
            memory_reduction_pct=0.0,
            copy_operations_saved=self.optimizer.copy_operations_saved,
            processing_time_saved=0.0,
        )

        self.logger.info(f"📊 最適化統計:")
        self.logger.info(f"  ♻️ コピー操作削減: {stats.copy_operations_saved}回")
        self.logger.info(f"  💾 メモリ削減: {stats.memory_reduction_pct:.1f}%")


def create_optimized_processor(
    chunk_size: int = 10000, memory_limit_mb: int = 2048
) -> OptimizedDataProcessor:
    """最適化されたデータプロセッサーを作成"""
    return OptimizedDataProcessor(
        chunk_size=chunk_size, memory_limit_mb=memory_limit_mb
    )


def optimize_dataframe_operations(
    df: pd.DataFrame, operations: List[Dict]
) -> pd.DataFrame:
    """データフレーム操作を最適化"""
    processor = create_optimized_processor()
    return processor.process_data_optimized(df, operations)


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)

    # サンプルデータ生成
    dates = pd.date_range("2020-01-01", periods=1000, freq="D")
    np.random.seed(42)

    sample_data = pd.DataFrame(
        {
            "Date": dates,
            "Open": np.random.uniform(100, 200, 1000),
            "High": np.random.uniform(100, 200, 1000),
            "Low": np.random.uniform(100, 200, 1000),
            "Close": np.random.uniform(100, 200, 1000),
            "Volume": np.random.randint(1000000, 10000000, 1000),
        }
    )

    # 最適化された処理
    processor = create_optimized_processor()

    operations = [
        {"type": "technical_indicators", "config": {"sma_windows": [5, 10, 20]}},
        {
            "type": "inplace",
            "operation": "fillna",
            "args": [],
            "kwargs": {"method": "ffill"},
        },
    ]

    result = processor.process_data_optimized(sample_data, operations)

    print(f"📊 処理結果: {result.shape}")
    print(f"♻️ コピー操作削減: {processor.optimizer.copy_operations_saved}回")
