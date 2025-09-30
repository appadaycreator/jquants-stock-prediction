#!/usr/bin/env python3
"""
超効率的データフレーム処理システム
データフレームコピーを最小限に抑え、インプレース操作を最大限活用
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
import weakref
from copy import deepcopy

logger = logging.getLogger(__name__)


@dataclass
class DataFrameOptimizationStats:
    """データフレーム最適化統計"""

    original_memory_mb: float
    optimized_memory_mb: float
    memory_reduction_mb: float
    memory_reduction_pct: float
    copy_operations_saved: int
    inplace_operations: int
    processing_time_saved: float
    dtype_optimizations: int


class UltraEfficientDataFrameProcessor:
    """超効率的データフレーム処理クラス"""

    def __init__(self, track_operations: bool = True):
        self.track_operations = track_operations
        self.operation_count = 0
        self.copy_operations_saved = 0
        self.inplace_operations = 0
        self.memory_saved = 0.0
        self.processing_time_saved = 0.0
        self.dtype_optimizations = 0
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

        # データフレームの参照を追跡
        self.dataframe_refs = weakref.WeakSet()

    def smart_copy(
        self, df: pd.DataFrame, operation_name: str = "", force_copy: bool = False
    ) -> pd.DataFrame:
        """必要時のみコピーを作成（超効率版）"""
        if self.track_operations:
            self.operation_count += 1

        # 強制コピーが指定されている場合
        if force_copy:
            self.logger.debug(f"📋 強制コピー作成: {operation_name}")
            return df.copy()

        # データフレームが変更される可能性を詳細チェック
        if self._will_modify_dataframe(df, operation_name):
            self.logger.debug(f"📋 コピー作成: {operation_name}")
            return df.copy()
        else:
            self.logger.debug(f"♻️ コピー回避: {operation_name}")
            self.copy_operations_saved += 1
            return df

    def _will_modify_dataframe(self, df: pd.DataFrame, operation: str) -> bool:
        """データフレームが変更されるかどうかを詳細判定"""
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
            "set_index",
            "rename",
            "reindex",
            "interpolate",
            "replace",
            "update",
            "insert",
            "append",
            "concat",
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
            "index",
            "values",
            "iloc",
            "loc",
            "at",
            "iat",
            "get",
            "isin",
            "isna",
            "notna",
            "duplicated",
            "memory_usage",
            "size",
            "ndim",
            "empty",
        ]

        # 部分的な変更操作（条件付きコピー）
        partial_modifying_operations = [
            "groupby",
            "rolling",
            "expanding",
            "ewm",
            "transform",
            "apply",
            "map",
            "applymap",
        ]

        operation_lower = operation.lower()

        if any(op in operation_lower for op in modifying_operations):
            return True
        elif any(op in operation_lower for op in non_modifying_operations):
            return False
        elif any(op in operation_lower for op in partial_modifying_operations):
            # 部分的な変更の場合は、データフレームの状態をチェック
            return self._check_dataframe_mutation_risk(df, operation)
        else:
            # 不明な場合は安全のためコピーを作成
            return True

    def _check_dataframe_mutation_risk(self, df: pd.DataFrame, operation: str) -> bool:
        """データフレームの変更リスクをチェック"""
        # データフレームが既に他の操作で変更されている場合はコピーが必要
        if id(df) in [id(ref()) for ref in self.dataframe_refs if ref() is not None]:
            return True

        # インデックスが複雑な場合はコピーが必要
        if (
            not df.index.is_monotonic_increasing
            and not df.index.is_monotonic_decreasing
        ):
            return True

        # カラム名が重複している場合はコピーが必要
        if len(df.columns) != len(set(df.columns)):
            return True

        return False

    def optimize_dtypes_ultra(self, df: pd.DataFrame) -> pd.DataFrame:
        """データ型の超効率最適化"""
        self.logger.info("🔧 データ型の超効率最適化開始")

        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        df_optimized = df.copy()

        for col in df_optimized.columns:
            col_type = df_optimized[col].dtype

            if col_type != "object":
                c_min = df_optimized[col].min()
                c_max = df_optimized[col].max()

                if str(col_type)[:3] == "int":
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df_optimized[col] = df_optimized[col].astype(np.int8)
                        self.dtype_optimizations += 1
                    elif (
                        c_min > np.iinfo(np.int16).min
                        and c_max < np.iinfo(np.int16).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.int16)
                        self.dtype_optimizations += 1
                    elif (
                        c_min > np.iinfo(np.int32).min
                        and c_max < np.iinfo(np.int32).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.int32)
                        self.dtype_optimizations += 1
                else:
                    if (
                        c_min > np.finfo(np.float16).min
                        and c_max < np.finfo(np.float16).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.float16)
                        self.dtype_optimizations += 1
                    elif (
                        c_min > np.finfo(np.float32).min
                        and c_max < np.finfo(np.float32).max
                    ):
                        df_optimized[col] = df_optimized[col].astype(np.float32)
                        self.dtype_optimizations += 1

        optimized_memory = df_optimized.memory_usage(deep=True).sum() / 1024 / 1024
        reduction = (original_memory - optimized_memory) / original_memory * 100

        self.logger.info(
            f"💾 データ型最適化完了: {original_memory:.1f}MB → {optimized_memory:.1f}MB ({reduction:.1f}%削減)"
        )

        return df_optimized

    def process_inplace(self, df: pd.DataFrame, operations: List[Dict]) -> pd.DataFrame:
        """インプレース操作でデータフレームを処理"""
        self.logger.info(f"🚀 インプレース処理開始: {len(operations)}操作")

        result_df = df

        for operation in operations:
            op_type = operation.get("type")
            op_params = operation.get("params", {})

            try:
                if op_type == "fillna":
                    result_df.fillna(**op_params, inplace=True)
                    self.inplace_operations += 1
                elif op_type == "dropna":
                    result_df.dropna(**op_params, inplace=True)
                    self.inplace_operations += 1
                elif op_type == "drop_duplicates":
                    result_df.drop_duplicates(**op_params, inplace=True)
                    self.inplace_operations += 1
                elif op_type == "sort_values":
                    result_df.sort_values(**op_params, inplace=True)
                    self.inplace_operations += 1
                elif op_type == "reset_index":
                    result_df.reset_index(**op_params, inplace=True)
                    self.inplace_operations += 1
                elif op_type == "astype":
                    for col, dtype in op_params.items():
                        result_df[col] = result_df[col].astype(dtype)
                    self.inplace_operations += 1
                elif op_type == "rename":
                    result_df.rename(**op_params, inplace=True)
                    self.inplace_operations += 1
                elif op_type == "set_index":
                    result_df.set_index(**op_params, inplace=True)
                    self.inplace_operations += 1
                else:
                    self.logger.warning(f"⚠️ 未対応のインプレース操作: {op_type}")

                self.logger.debug(f"✅ インプレース操作実行: {op_type}")

            except Exception as e:
                self.system.log_error(e, f"インプレース操作エラー ({op_type})")

        self.logger.info(f"✅ インプレース処理完了: {self.inplace_operations}操作")
        return result_df

    def chunk_processing_ultra(
        self, df: pd.DataFrame, chunk_size: int, processing_func: Callable
    ) -> pd.DataFrame:
        """超効率チャンク処理"""
        self.logger.info(f"📊 超効率チャンク処理開始: {len(df)}行, チャンクサイズ: {chunk_size}")

        if len(df) <= chunk_size:
            return processing_func(df)

        results = []
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i : i + chunk_size]

            # メモリ制限チェック
            if not self._check_memory_limit():
                self.logger.warning("⚠️ メモリ制限に達しました。ガベージコレクションを実行")
                gc.collect()

            # チャンク処理
            processed_chunk = processing_func(chunk)
            results.append(processed_chunk)

            self.logger.debug(
                f"📦 チャンク処理完了: {i//chunk_size + 1}/{(len(df)-1)//chunk_size + 1}"
            )

        # 結果を結合
        final_result = pd.concat(results, ignore_index=True)
        self.logger.info(f"✅ 超効率チャンク処理完了: {len(final_result)}行")

        return final_result

    def _check_memory_limit(self, limit_mb: int = 2048) -> bool:
        """メモリ制限をチェック"""
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        return current_memory < limit_mb

    def get_optimization_stats(self) -> DataFrameOptimizationStats:
        """最適化統計を取得"""
        return DataFrameOptimizationStats(
            original_memory_mb=0.0,  # 実際の実装では追跡
            optimized_memory_mb=0.0,
            memory_reduction_mb=self.memory_saved,
            memory_reduction_pct=0.0,
            copy_operations_saved=self.copy_operations_saved,
            inplace_operations=self.inplace_operations,
            processing_time_saved=self.processing_time_saved,
            dtype_optimizations=self.dtype_optimizations,
        )


class ViewBasedProcessor:
    """ビューベース処理クラス"""

    def __init__(self):
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

    def create_view(
        self, df: pd.DataFrame, columns: List[str] = None, rows: slice = None
    ) -> pd.DataFrame:
        """データフレームのビューを作成（コピーなし）"""
        if columns is None and rows is None:
            return df

        if columns is not None:
            df_view = df[columns]
        else:
            df_view = df

        if rows is not None:
            df_view = df_view.iloc[rows]

        self.logger.debug(f"👁️ ビュー作成: {len(df_view)}行, {len(df_view.columns)}列")
        return df_view

    def process_view(self, df: pd.DataFrame, processing_func: Callable) -> pd.DataFrame:
        """ビューでデータを処理"""
        # 元のデータフレームを直接操作
        result = processing_func(df)
        return result


class MemoryEfficientDataFrameProcessor:
    """メモリ効率データフレーム処理クラス"""

    def __init__(self, chunk_size: int = 10000, memory_limit_mb: int = 2048):
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.ultra_processor = UltraEfficientDataFrameProcessor()
        self.view_processor = ViewBasedProcessor()
        # 循環参照を回避するため、UnifiedSystemの初期化を無効化
        self.system = None
        self.logger = logging.getLogger(__name__)

    def process_dataframe_ultra_efficient(
        self, df: pd.DataFrame, operations: List[Dict]
    ) -> pd.DataFrame:
        """超効率データフレーム処理"""
        self.logger.info(f"🚀 超効率データフレーム処理開始: {len(operations)}操作")

        result_df = df

        for operation in operations:
            op_type = operation.get("type")

            if op_type == "inplace":
                result_df = self.ultra_processor.process_inplace(result_df, [operation])
            elif op_type == "dtype_optimization":
                result_df = self.ultra_processor.optimize_dtypes_ultra(result_df)
            elif op_type == "chunk_processing":
                result_df = self.ultra_processor.chunk_processing_ultra(
                    result_df,
                    operation.get("chunk_size", self.chunk_size),
                    operation.get("processing_func"),
                )
            elif op_type == "view_processing":
                result_df = self.view_processor.process_view(
                    result_df, operation.get("processing_func")
                )
            else:
                self.logger.warning(f"⚠️ 未対応の操作タイプ: {op_type}")

        # 最適化統計をログ出力
        self._log_optimization_stats()

        return result_df

    def _log_optimization_stats(self):
        """最適化統計をログ出力"""
        stats = self.ultra_processor.get_optimization_stats()

        self.logger.info("📊 超効率データフレーム処理統計:")
        self.logger.info(f"  ♻️ コピー操作削減: {stats.copy_operations_saved}回")
        self.logger.info(f"  🔧 インプレース操作: {stats.inplace_operations}回")
        self.logger.info(f"  💾 データ型最適化: {stats.dtype_optimizations}列")
        self.logger.info(f"  ⏱️ 処理時間削減: {stats.processing_time_saved:.2f}秒")


def create_ultra_efficient_processor(
    chunk_size: int = 10000, memory_limit_mb: int = 2048
) -> MemoryEfficientDataFrameProcessor:
    """超効率データフレーム処理システムを作成"""
    return MemoryEfficientDataFrameProcessor(chunk_size, memory_limit_mb)


if __name__ == "__main__":
    # テスト用のサンプルデータ
    import pandas as pd
    import numpy as np

    # サンプルデータ生成
    np.random.seed(42)
    n_rows = 10000
    n_cols = 20

    data = {f"col_{i}": np.random.randn(n_rows) for i in range(n_cols)}

    sample_df = pd.DataFrame(data)

    # 超効率データフレーム処理システムのテスト
    processor = create_ultra_efficient_processor()

    operations = [
        {"type": "dtype_optimization", "params": {}},
        {
            "type": "inplace",
            "params": {"type": "fillna", "params": {"method": "ffill"}},
        },
        {"type": "inplace", "params": {"type": "dropna", "params": {}}},
    ]

    optimized_df = processor.process_dataframe_ultra_efficient(sample_df, operations)

    print(f"📊 元データ: {sample_df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
    print(f"📈 最適化後: {optimized_df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
    print(f"✅ 処理完了: {len(optimized_df)}行, {len(optimized_df.columns)}列")
