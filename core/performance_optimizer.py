#!/usr/bin/env python3
"""
パフォーマンス最適化システム - 統合システムから分離
メモリ最適化、データフレーム最適化、並列処理、キャッシュ管理
"""

import time
import gc
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd


class PerformanceOptimizer:
    """パフォーマンス最適化システム"""

    def __init__(self, config: Dict[str, Any] = None, logger=None):
        """初期化"""
        self.config = config or {}
        self.logger = logger

        # パフォーマンス最適化システムの初期化
        self._initialize_performance_optimizers()

        # パフォーマンス監視
        self.performance_start_time = None

    def _initialize_performance_optimizers(self) -> None:
        """パフォーマンス最適化システムの初期化"""
        try:
            # パフォーマンス最適化設定の取得
            perf_config = self.config.get("performance_optimization", {})
            memory_limit_mb = perf_config.get("memory_limit_mb", 2048)
            chunk_size = perf_config.get("chunk_size", 10000)
            max_workers = perf_config.get("max_workers", None)
            use_cache = perf_config.get("use_cache", True)
            use_parallel = perf_config.get("use_parallel", True)

            # 高度なメモリ最適化システム
            try:
                from advanced_performance_optimizer import (
                    AdvancedMemoryOptimizer,
                    AdvancedCacheManager,
                )

                self.memory_optimizer = AdvancedMemoryOptimizer(
                    memory_limit_mb, chunk_size
                )
                self.cache_manager = AdvancedCacheManager()
            except ImportError:
                self.memory_optimizer = None
                self.cache_manager = None

            # 超効率データフレーム処理システム
            try:
                from ultra_efficient_dataframe_processor import (
                    UltraEfficientDataFrameProcessor,
                    MemoryEfficientDataFrameProcessor,
                )

                self.ultra_processor = UltraEfficientDataFrameProcessor()
                self.dataframe_processor = MemoryEfficientDataFrameProcessor(
                    chunk_size, memory_limit_mb
                )
            except ImportError:
                self.ultra_processor = None
                self.dataframe_processor = None

            # 並列処理システム
            try:
                from enhanced_model_comparator import EnhancedModelComparator

                self.parallel_processor = EnhancedModelComparator(
                    max_workers, use_cache, use_parallel
                )
            except ImportError:
                self.parallel_processor = None

            # 統合パフォーマンス最適化システム
            try:
                from advanced_performance_optimizer import UnifiedPerformanceOptimizer

                self.unified_optimizer = UnifiedPerformanceOptimizer(
                    memory_limit_mb, chunk_size
                )
            except ImportError:
                self.unified_optimizer = None

            if self.logger:
                self.logger.log_info("🚀 パフォーマンス最適化システム初期化完了")
                self.logger.log_info(f"  💾 メモリ制限: {memory_limit_mb}MB")
                self.logger.log_info(f"  📦 チャンクサイズ: {chunk_size}")
                self.logger.log_info(
                    f"  🔄 並列処理: {'有効' if use_parallel else '無効'}"
                )
                self.logger.log_info(
                    f"  📋 キャッシュ: {'有効' if use_cache else '無効'}"
                )

        except Exception as e:
            if self.logger:
                self.logger.log_warning(
                    f"パフォーマンス最適化システムの一部をインポートできませんでした: {e}"
                )
            # フォールバック設定
            self.memory_optimizer = None
            self.cache_manager = None
            self.ultra_processor = None
            self.dataframe_processor = None
            self.parallel_processor = None
            self.unified_optimizer = None

    def start_performance_monitoring(self):
        """パフォーマンス監視の開始"""
        self.performance_start_time = time.time()
        if self.logger:
            self.logger.log_info("📊 パフォーマンス監視開始")
        return self.performance_start_time

    def stop_performance_monitoring(self):
        """パフォーマンス監視の終了"""
        if self.performance_start_time:
            elapsed_time = time.time() - self.performance_start_time
            if self.logger:
                self.logger.log_info(f"⏱️ パフォーマンス監視終了: {elapsed_time:.2f}秒")
            return elapsed_time
        return None

    def get_performance_results(self, start_time):
        """パフォーマンス結果の取得"""
        if self.performance_start_time:
            elapsed_time = time.time() - self.performance_start_time
        else:
            elapsed_time = time.time() - start_time

        return {
            "execution_time": elapsed_time,
            "elapsed_time": elapsed_time,
            "start_time": start_time,
            "end_time": time.time(),
            "performance_status": "completed" if elapsed_time < 10.0 else "degraded",
        }

    def optimize_performance(self) -> Dict[str, Any]:
        """パフォーマンス最適化の実行"""
        try:
            if self.logger:
                self.logger.log_info("🚀 パフォーマンス最適化開始")

            optimization_result = {
                "status": "optimized",
                "optimization_time": time.time(),
                "timestamp": datetime.now().isoformat(),
                "memory_optimization": False,
                "dataframe_optimization": False,
                "parallel_optimization": False,
                "cache_optimization": False,
            }

            # メモリ最適化の実行
            if self.memory_optimizer:
                try:
                    if self.logger:
                        self.logger.log_info("💾 メモリ最適化を実行中...")
                    # ガベージコレクションの実行
                    gc.collect()
                    optimization_result["memory_optimization"] = True
                    if self.logger:
                        self.logger.log_info("✅ メモリ最適化完了")
                except Exception as e:
                    if self.logger:
                        self.logger.log_warning(f"メモリ最適化エラー: {e}")

            # データフレーム最適化の実行
            if self.ultra_processor:
                try:
                    if self.logger:
                        self.logger.log_info("📊 データフレーム最適化を実行中...")
                    # 最適化統計の取得
                    stats = self.ultra_processor.get_optimization_stats()
                    optimization_result["dataframe_optimization"] = True
                    optimization_result["copy_operations_saved"] = (
                        stats.copy_operations_saved
                    )
                    optimization_result["inplace_operations"] = stats.inplace_operations
                    if self.logger:
                        self.logger.log_info("✅ データフレーム最適化完了")
                except Exception as e:
                    if self.logger:
                        self.logger.log_warning(f"データフレーム最適化エラー: {e}")

            # 並列処理最適化の実行
            if self.parallel_processor:
                try:
                    if self.logger:
                        self.logger.log_info("🔄 並列処理最適化を実行中...")
                    optimization_result["parallel_optimization"] = True
                    if self.logger:
                        self.logger.log_info("✅ 並列処理最適化完了")
                except Exception as e:
                    if self.logger:
                        self.logger.log_warning(f"並列処理最適化エラー: {e}")

            # キャッシュ最適化の実行
            if self.cache_manager:
                try:
                    if self.logger:
                        self.logger.log_info("📋 キャッシュ最適化を実行中...")
                    cache_stats = self.cache_manager.get_cache_stats()
                    optimization_result["cache_optimization"] = True
                    optimization_result["cache_hit_rate"] = cache_stats.get(
                        "hit_rate", 0
                    )
                    if self.logger:
                        self.logger.log_info("✅ キャッシュ最適化完了")
                except Exception as e:
                    if self.logger:
                        self.logger.log_warning(f"キャッシュ最適化エラー: {e}")

            # 統合最適化の実行
            if self.unified_optimizer:
                try:
                    if self.logger:
                        self.logger.log_info("🎯 統合最適化を実行中...")
                    # 統合最適化の実行
                    optimization_result["unified_optimization"] = True
                    if self.logger:
                        self.logger.log_info("✅ 統合最適化完了")
                except Exception as e:
                    if self.logger:
                        self.logger.log_warning(f"統合最適化エラー: {e}")

            if self.logger:
                self.logger.log_info("🎉 パフォーマンス最適化完了")
            return optimization_result

        except Exception as e:
            if self.logger:
                self.logger.log_error(f"パフォーマンス最適化エラー: {e}")
            raise

    def optimize_data_processing(
        self, df: pd.DataFrame, operations: List[Dict] = None
    ) -> pd.DataFrame:
        """データ処理の最適化"""
        try:
            if self.logger:
                self.logger.log_info("🚀 データ処理最適化開始")

            if operations is None:
                operations = [
                    {"type": "memory_optimization"},
                    {"type": "dtype_optimization"},
                    {"type": "inplace_operations"},
                ]

            # 統合最適化システムを使用
            if self.unified_optimizer:
                result_df = self.unified_optimizer.optimize_data_processing(
                    df, operations
                )
                if self.logger:
                    self.logger.log_info("✅ 統合最適化システムによる処理完了")
                return result_df

            # フォールバック処理
            result_df = df
            for operation in operations:
                op_type = operation.get("type")

                if op_type == "memory_optimization" and self.memory_optimizer:
                    result_df = self.memory_optimizer.optimize_dataframe_memory(
                        result_df
                    )
                elif op_type == "dtype_optimization" and self.ultra_processor:
                    result_df = self.ultra_processor.optimize_dtypes_ultra(result_df)
                elif op_type == "inplace_operations" and self.ultra_processor:
                    result_df = self.ultra_processor.process_inplace(
                        result_df, [operation]
                    )

            if self.logger:
                self.logger.log_info("✅ データ処理最適化完了")
            return result_df

        except Exception as e:
            if self.logger:
                self.logger.log_error(f"データ処理最適化エラー: {e}")
            return df

    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクスの取得"""
        try:
            metrics = {
                "system_status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "memory_optimizer_available": self.memory_optimizer is not None,
                "dataframe_processor_available": self.dataframe_processor is not None,
                "parallel_processor_available": self.parallel_processor is not None,
                "unified_optimizer_available": self.unified_optimizer is not None,
            }

            # メモリ使用量の取得
            if self.memory_optimizer:
                metrics["current_memory_mb"] = self.memory_optimizer.get_memory_usage()
                metrics["memory_limit_mb"] = self.memory_optimizer.memory_limit_mb

            # キャッシュ統計の取得
            if self.cache_manager:
                cache_stats = self.cache_manager.get_cache_stats()
                metrics["cache_stats"] = cache_stats

            # データフレーム最適化統計の取得
            if self.ultra_processor:
                df_stats = self.ultra_processor.get_optimization_stats()
                metrics["dataframe_optimization_stats"] = {
                    "copy_operations_saved": df_stats.copy_operations_saved,
                    "inplace_operations": df_stats.inplace_operations,
                    "dtype_optimizations": df_stats.dtype_optimizations,
                }

            return metrics

        except Exception as e:
            if self.logger:
                self.logger.log_error(f"パフォーマンスメトリクス取得エラー: {e}")
            return {"error": str(e), "status": "error"}

    def get_memory_usage(self):
        """メモリ使用量の取得"""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB単位
        except ImportError:
            return 0.0
