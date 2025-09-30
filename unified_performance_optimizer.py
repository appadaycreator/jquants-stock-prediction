#!/usr/bin/env python3
"""
統合パフォーマンス最適化システム
メモリ最適化、並列処理、キャッシュ機能を統合した包括的な最適化システム
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Callable
import time
import psutil
import gc
from dataclasses import dataclass
from unified_system import UnifiedSystem
from advanced_performance_optimizer import UnifiedPerformanceOptimizer
from enhanced_model_comparator import EnhancedModelComparator
from ultra_efficient_dataframe_processor import MemoryEfficientDataFrameProcessor

logger = logging.getLogger(__name__)


@dataclass
class UnifiedOptimizationMetrics:
    """統合最適化メトリクス"""

    total_processing_time: float
    memory_usage_peak: float
    memory_usage_average: float
    cache_hit_rate: float
    parallel_efficiency: float
    copy_operations_saved: int
    inplace_operations: int
    dtype_optimizations: int
    models_processed: int
    data_rows_processed: int


class UnifiedPerformanceOptimizer:
    """統合パフォーマンス最適化システム"""

    def __init__(
        self,
        memory_limit_mb: int = 2048,
        chunk_size: int = 10000,
        max_workers: int = None,
        use_cache: bool = True,
        use_parallel: bool = True,
    ):
        self.memory_limit_mb = memory_limit_mb
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.use_parallel = use_parallel

        # 各最適化システムを初期化
        self.performance_optimizer = UnifiedPerformanceOptimizer(
            memory_limit_mb, chunk_size
        )
        self.model_comparator = EnhancedModelComparator(
            max_workers, use_cache, use_parallel
        )
        self.dataframe_processor = MemoryEfficientDataFrameProcessor(
            chunk_size, memory_limit_mb
        )

        self.system = UnifiedSystem("UnifiedPerformanceOptimizer")
        self.logger = logging.getLogger(__name__)

        # 統合メトリクス
        self.metrics = UnifiedOptimizationMetrics(
            total_processing_time=0.0,
            memory_usage_peak=0.0,
            memory_usage_average=0.0,
            cache_hit_rate=0.0,
            parallel_efficiency=0.0,
            copy_operations_saved=0,
            inplace_operations=0,
            dtype_optimizations=0,
            models_processed=0,
            data_rows_processed=0,
        )

    def optimize_data_pipeline(
        self, df: pd.DataFrame, operations: List[Dict]
    ) -> pd.DataFrame:
        """データパイプラインの統合最適化"""
        self.logger.info(f"🚀 統合データパイプライン最適化開始: {len(operations)}操作")

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        try:
            # データフレーム処理の最適化
            optimized_df = self.dataframe_processor.process_dataframe_ultra_efficient(
                df, operations
            )

            # メモリ最適化
            memory_optimized_df = (
                self.performance_optimizer.memory_optimizer.optimize_dataframe_memory(
                    optimized_df
                )
            )

            # パフォーマンス監視
            with self.performance_optimizer.performance_monitor.monitor_performance(
                "data_pipeline"
            ):
                result_df = memory_optimized_df

            # メトリクス更新
            self._update_metrics(start_time, start_memory, len(df), 0)

            self.logger.info("✅ 統合データパイプライン最適化完了")
            return result_df

        except Exception as e:
            self.system.log_error(e, "統合データパイプライン最適化エラー")
            return df

    def optimize_model_comparison(
        self,
        models_config: Dict,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        feature_names: List[str] = None,
    ) -> pd.DataFrame:
        """モデル比較の統合最適化"""
        self.logger.info(f"🚀 統合モデル比較最適化開始: {len(models_config)}モデル")

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        try:
            # 強化されたモデル比較を実行
            results_df = self.model_comparator.compare_models_enhanced(
                models_config, X_train, X_test, y_train, y_test, feature_names
            )

            # メトリクス更新
            self._update_metrics(start_time, start_memory, 0, len(models_config))

            self.logger.info("✅ 統合モデル比較最適化完了")
            return results_df

        except Exception as e:
            self.system.log_error(e, "統合モデル比較最適化エラー")
            return pd.DataFrame()

    def optimize_technical_indicators(
        self, df: pd.DataFrame, config: Dict = None
    ) -> pd.DataFrame:
        """技術指標計算の統合最適化"""
        self.logger.info("🚀 統合技術指標計算最適化開始")

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        try:
            # 最適化された技術指標計算
            optimized_df = self.performance_optimizer.technical_indicators.calculate_indicators_optimized(
                df, config
            )

            # メトリクス更新
            self._update_metrics(start_time, start_memory, len(df), 0)

            self.logger.info("✅ 統合技術指標計算最適化完了")
            return optimized_df

        except Exception as e:
            self.system.log_error(e, "統合技術指標計算最適化エラー")
            return df

    def _update_metrics(
        self, start_time: float, start_memory: float, data_rows: int, models_count: int
    ):
        """メトリクスを更新"""
        processing_time = time.time() - start_time
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024

        self.metrics.total_processing_time += processing_time
        self.metrics.memory_usage_peak = max(
            self.metrics.memory_usage_peak, current_memory
        )
        self.metrics.memory_usage_average = (
            self.metrics.memory_usage_average + current_memory
        ) / 2
        self.metrics.data_rows_processed += data_rows
        self.metrics.models_processed += models_count

        # キャッシュ統計を取得
        if (
            hasattr(self.model_comparator, "cache_manager")
            and self.model_comparator.cache_manager
        ):
            cache_stats = self.model_comparator.cache_manager.get_cache_stats()
            self.metrics.cache_hit_rate = cache_stats.get("hit_rate", 0)

        # データフレーム処理統計を取得
        if hasattr(self.dataframe_processor, "ultra_processor"):
            df_stats = self.dataframe_processor.ultra_processor.get_optimization_stats()
            self.metrics.copy_operations_saved += df_stats.copy_operations_saved
            self.metrics.inplace_operations += df_stats.inplace_operations
            self.metrics.dtype_optimizations += df_stats.dtype_optimizations

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """包括的な最適化レポートを取得"""
        return {
            "performance_metrics": {
                "total_processing_time": self.metrics.total_processing_time,
                "memory_usage_peak_mb": self.metrics.memory_usage_peak,
                "memory_usage_average_mb": self.metrics.memory_usage_average,
                "cache_hit_rate_percent": self.metrics.cache_hit_rate,
                "parallel_efficiency_percent": self.metrics.parallel_efficiency,
            },
            "optimization_stats": {
                "copy_operations_saved": self.metrics.copy_operations_saved,
                "inplace_operations": self.metrics.inplace_operations,
                "dtype_optimizations": self.metrics.dtype_optimizations,
                "data_rows_processed": self.metrics.data_rows_processed,
                "models_processed": self.metrics.models_processed,
            },
            "system_config": {
                "memory_limit_mb": self.memory_limit_mb,
                "chunk_size": self.chunk_size,
                "max_workers": self.max_workers,
                "use_cache": self.use_cache,
                "use_parallel": self.use_parallel,
            },
        }

    def log_optimization_summary(self):
        """最適化サマリーをログ出力"""
        report = self.get_comprehensive_report()

        self.logger.info("📊 統合パフォーマンス最適化サマリー:")
        self.logger.info(
            f"  ⏱️ 総処理時間: {report['performance_metrics']['total_processing_time']:.2f}秒"
        )
        self.logger.info(
            f"  💾 ピークメモリ使用量: {report['performance_metrics']['memory_usage_peak_mb']:.1f}MB"
        )
        self.logger.info(
            f"  📈 キャッシュヒット率: {report['performance_metrics']['cache_hit_rate_percent']:.1f}%"
        )
        self.logger.info(
            f"  ♻️ コピー操作削減: {report['optimization_stats']['copy_operations_saved']}回"
        )
        self.logger.info(
            f"  🔧 インプレース操作: {report['optimization_stats']['inplace_operations']}回"
        )
        self.logger.info(
            f"  📊 データ行処理: {report['optimization_stats']['data_rows_processed']}行"
        )
        self.logger.info(
            f"  🤖 モデル処理: {report['optimization_stats']['models_processed']}個"
        )

    def clear_all_caches(self):
        """全てのキャッシュをクリア"""
        try:
            if hasattr(self.performance_optimizer, "cache_manager"):
                self.performance_optimizer.cache_manager.clear_cache()

            if (
                hasattr(self.model_comparator, "cache_manager")
                and self.model_comparator.cache_manager
            ):
                self.model_comparator.cache_manager.clear_cache()

            self.logger.info("🧹 全てのキャッシュをクリアしました")
        except Exception as e:
            self.logger.error(f"❌ キャッシュクリアエラー: {e}")

    def reset_metrics(self):
        """メトリクスをリセット"""
        self.metrics = UnifiedOptimizationMetrics(
            total_processing_time=0.0,
            memory_usage_peak=0.0,
            memory_usage_average=0.0,
            cache_hit_rate=0.0,
            parallel_efficiency=0.0,
            copy_operations_saved=0,
            inplace_operations=0,
            dtype_optimizations=0,
            models_processed=0,
            data_rows_processed=0,
        )
        self.logger.info("🔄 メトリクスをリセットしました")


def create_unified_performance_optimizer(
    memory_limit_mb: int = 2048,
    chunk_size: int = 10000,
    max_workers: int = None,
    use_cache: bool = True,
    use_parallel: bool = True,
) -> UnifiedPerformanceOptimizer:
    """統合パフォーマンス最適化システムを作成"""
    return UnifiedPerformanceOptimizer(
        memory_limit_mb, chunk_size, max_workers, use_cache, use_parallel
    )


if __name__ == "__main__":
    # テスト用のサンプルデータ
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split

    # サンプルデータ生成
    np.random.seed(42)
    n_samples = 5000
    n_features = 15

    X = np.random.randn(n_samples, n_features)
    y = np.random.randn(n_samples)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 統合パフォーマンス最適化システムのテスト
    optimizer = create_unified_performance_optimizer(use_cache=True, use_parallel=True)

    # データパイプライン最適化のテスト
    sample_df = pd.DataFrame({f"feature_{i}": np.random.randn(1000) for i in range(10)})

    operations = [
        {"type": "dtype_optimization", "params": {}},
        {
            "type": "inplace",
            "params": {"type": "fillna", "params": {"method": "ffill"}},
        },
    ]

    optimized_df = optimizer.optimize_data_pipeline(sample_df, operations)

    # モデル比較最適化のテスト
    models_config = {
        "random_forest": {
            "type": "random_forest",
            "params": {"n_estimators": 50, "random_state": 42},
        },
        "linear_regression": {"type": "linear_regression", "params": {}},
    }

    model_results = optimizer.optimize_model_comparison(
        models_config, X_train, X_test, y_train, y_test
    )

    # 最適化サマリーを表示
    optimizer.log_optimization_summary()

    print("📊 統合パフォーマンス最適化テスト完了")
    print(f"📈 最適化されたデータ: {len(optimized_df)}行, {len(optimized_df.columns)}列")
    print(f"🤖 モデル比較結果: {len(model_results)}モデル")
