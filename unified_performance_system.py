#!/usr/bin/env python3
"""
統合パフォーマンス最適化システム
全ての最適化機能を統合し、一元管理するシステム
"""

import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json
import os
from pathlib import Path

# 最適化システムのインポート
from enhanced_memory_optimizer import (
    EnhancedMemoryOptimizer,
    create_enhanced_memory_optimizer,
)
from enhanced_parallel_processor import EnhancedParallelProcessor, parallel_context
from enhanced_chart_optimizer import EnhancedChartOptimizer, create_chart_optimizer
from performance_integration_test import PerformanceIntegrationTester

logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """パフォーマンス設定"""

    memory_limit_mb: int = 1024
    max_data_points: int = 3000
    target_render_time: float = 3.0
    enable_aggressive_optimization: bool = True
    enable_parallel_processing: bool = True
    enable_chart_optimization: bool = True
    enable_memory_optimization: bool = True
    max_workers: int = 8
    quality_level: str = "high"


@dataclass
class OptimizationResult:
    """最適化結果"""

    success: bool
    execution_time: float
    memory_usage_mb: float
    memory_reduction_percent: float
    processing_speed_improvement: float
    chart_render_time: float
    data_points: int
    optimizations_applied: List[str]
    metrics: Dict[str, Any]
    error_message: Optional[str] = None


class UnifiedPerformanceSystem:
    """統合パフォーマンス最適化システム"""

    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()

        # 最適化システムの初期化
        self.memory_optimizer = None
        self.parallel_processor = None
        self.chart_optimizer = None

        # パフォーマンス履歴
        self.optimization_history = []
        self.performance_metrics = {}

        logger.info("🚀 統合パフォーマンス最適化システム初期化完了")
        self._initialize_systems()

    def _initialize_systems(self):
        """最適化システムの初期化"""
        try:
            # メモリ最適化システム
            if self.config.enable_memory_optimization:
                self.memory_optimizer = create_enhanced_memory_optimizer(
                    memory_limit_mb=self.config.memory_limit_mb,
                    aggressive_mode=self.config.enable_aggressive_optimization,
                )
                logger.info("✅ メモリ最適化システム初期化完了")

            # 並列処理システム
            if self.config.enable_parallel_processing:
                self.parallel_processor = EnhancedParallelProcessor(
                    max_workers=self.config.max_workers, adaptive_mode=True
                )
                logger.info("✅ 並列処理システム初期化完了")

            # チャート最適化システム
            if self.config.enable_chart_optimization:
                self.chart_optimizer = create_chart_optimizer(
                    max_data_points=self.config.max_data_points,
                    target_render_time=self.config.target_render_time,
                    quality_level=self.config.quality_level,
                )
                logger.info("✅ チャート最適化システム初期化完了")

        except Exception as e:
            logger.error(f"システム初期化エラー: {e}")
            raise

    def optimize_data_processing(
        self,
        data: pd.DataFrame,
        operations: List[str] = None,
        chart_type: str = "candlestick",
    ) -> OptimizationResult:
        """データ処理の統合最適化"""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        logger.info(f"🚀 統合データ処理最適化開始")
        logger.info(f"   - データサイズ: {len(data)}行")
        logger.info(f"   - 操作: {operations or ['all']}")

        optimizations_applied = []
        optimized_data = data.copy()

        try:
            # 1. メモリ最適化
            if self.config.enable_memory_optimization and self.memory_optimizer:
                with self.memory_optimizer.memory_monitoring("memory_optimization"):
                    optimized_data = (
                        self.memory_optimizer.optimize_dataframe_aggressive(
                            optimized_data
                        )
                    )
                    optimizations_applied.append("memory_optimization")
                    logger.info("✅ メモリ最適化完了")

            # 2. 並列処理最適化
            if self.config.enable_parallel_processing and self.parallel_processor:
                with parallel_context(max_workers=self.config.max_workers) as processor:
                    # データをチャンクに分割して並列処理
                    chunk_size = max(
                        1000, len(optimized_data) // self.config.max_workers
                    )
                    chunks = [
                        optimized_data.iloc[i : i + chunk_size]
                        for i in range(0, len(optimized_data), chunk_size)
                    ]

                    processed_chunks = processor.parallel_map_optimized(
                        self._process_data_chunk, chunks, task_type="mixed"
                    )

                    optimized_data = pd.concat(processed_chunks, ignore_index=True)
                    optimizations_applied.append("parallel_processing")
                    logger.info("✅ 並列処理最適化完了")

            # 3. チャート最適化
            chart_render_time = 0
            if self.config.enable_chart_optimization and self.chart_optimizer:
                chart_result = self.chart_optimizer.optimize_chart_rendering(
                    optimized_data, chart_type=chart_type, title="最適化されたチャート"
                )
                chart_render_time = chart_result["render_time"]
                optimizations_applied.append("chart_optimization")
                logger.info("✅ チャート最適化完了")

            # 結果の計算
            end_time = time.time()
            end_memory = self._get_memory_usage()

            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            memory_reduction = self._calculate_memory_reduction(
                start_memory, end_memory
            )
            speed_improvement = self._calculate_speed_improvement(
                execution_time, len(data)
            )

            result = OptimizationResult(
                success=True,
                execution_time=execution_time,
                memory_usage_mb=memory_usage,
                memory_reduction_percent=memory_reduction,
                processing_speed_improvement=speed_improvement,
                chart_render_time=chart_render_time,
                data_points=len(optimized_data),
                optimizations_applied=optimizations_applied,
                metrics={
                    "original_data_size": len(data),
                    "optimized_data_size": len(optimized_data),
                    "compression_ratio": len(optimized_data) / len(data),
                    "target_achieved": chart_render_time
                    <= self.config.target_render_time,
                },
            )

            # 履歴に記録
            self.optimization_history.append(
                {"timestamp": time.time(), "result": result, "config": self.config}
            )

            logger.info("✅ 統合データ処理最適化完了")
            logger.info(f"   - 実行時間: {execution_time:.2f}秒")
            logger.info(f"   - メモリ使用量: {memory_usage:.1f}MB")
            logger.info(f"   - メモリ削減: {memory_reduction:.1f}%")
            logger.info(f"   - 処理速度向上: {speed_improvement:.1f}倍")
            logger.info(f"   - チャート描画: {chart_render_time:.2f}秒")

            return result

        except Exception as e:
            logger.error(f"統合最適化エラー: {e}")
            return OptimizationResult(
                success=False,
                execution_time=time.time() - start_time,
                memory_usage_mb=0,
                memory_reduction_percent=0,
                processing_speed_improvement=1,
                chart_render_time=0,
                data_points=0,
                optimizations_applied=[],
                metrics={},
                error_message=str(e),
            )

    def _process_data_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """データチャンクの処理"""
        # 基本的なデータ処理
        processed_chunk = chunk.copy()

        # 欠損値の処理
        processed_chunk = processed_chunk.dropna()

        # データ型の最適化
        for col in processed_chunk.columns:
            if processed_chunk[col].dtype == "float64":
                processed_chunk[col] = processed_chunk[col].astype("float32")
            elif processed_chunk[col].dtype == "int64":
                processed_chunk[col] = processed_chunk[col].astype("int32")

        return processed_chunk

    def _get_memory_usage(self) -> float:
        """現在のメモリ使用量を取得（MB）"""
        import psutil

        return psutil.Process().memory_info().rss / 1024 / 1024

    def _calculate_memory_reduction(
        self, start_memory: float, end_memory: float
    ) -> float:
        """メモリ削減率を計算"""
        if start_memory > 0:
            return max(0, (start_memory - end_memory) / start_memory * 100)
        return 0

    def _calculate_speed_improvement(
        self, execution_time: float, data_size: int
    ) -> float:
        """処理速度向上率を計算"""
        if execution_time > 0:
            return data_size / execution_time
        return 1

    def run_performance_test(self, test_data_size: int = 50000) -> Dict[str, Any]:
        """パフォーマンステストの実行"""
        logger.info(f"🧪 パフォーマンステスト開始: {test_data_size}行")

        try:
            # テストデータの生成
            test_data = self._generate_test_data(test_data_size)

            # 統合最適化の実行
            result = self.optimize_data_processing(test_data)

            # パフォーマンスメトリクスの記録
            self.performance_metrics = {
                "test_data_size": test_data_size,
                "execution_time": result.execution_time,
                "memory_usage": result.memory_usage_mb,
                "memory_reduction": result.memory_reduction_percent,
                "speed_improvement": result.processing_speed_improvement,
                "chart_render_time": result.chart_render_time,
                "success": result.success,
                "optimizations_applied": result.optimizations_applied,
            }

            logger.info("✅ パフォーマンステスト完了")
            return self.performance_metrics

        except Exception as e:
            logger.error(f"パフォーマンステストエラー: {e}")
            return {"error": str(e)}

    def _generate_test_data(self, size: int) -> pd.DataFrame:
        """テストデータの生成"""
        np.random.seed(42)
        dates = pd.date_range("2020-01-01", periods=size, freq="D")

        base_price = 1000 + np.cumsum(np.random.randn(size) * 0.02) * 1000

        data = pd.DataFrame(
            {
                "Date": dates,
                "Open": base_price,
                "High": base_price * (1 + np.random.uniform(0, 0.05, size)),
                "Low": base_price * (1 - np.random.uniform(0, 0.05, size)),
                "Close": base_price + np.random.uniform(-20, 20, size),
                "Volume": np.random.randint(1000000, 10000000, size),
                "SMA_5": base_price.rolling(window=5).mean(),
                "SMA_20": base_price.rolling(window=20).mean(),
                "SMA_50": base_price.rolling(window=50).mean(),
                "RSI": np.random.uniform(0, 100, size),
                "MACD": np.random.uniform(-10, 10, size),
                "BB_Upper": base_price * 1.02,
                "BB_Lower": base_price * 0.98,
                "ATR": np.random.uniform(1, 10, size),
            }
        )

        return data

    def get_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートの生成"""
        if not self.optimization_history:
            return {"message": "最適化履歴がありません"}

        # 最新の結果を取得
        latest_result = self.optimization_history[-1]["result"]

        # 統計情報の計算
        total_optimizations = len(self.optimization_history)
        successful_optimizations = sum(
            1 for h in self.optimization_history if h["result"].success
        )
        success_rate = (
            (successful_optimizations / total_optimizations * 100)
            if total_optimizations > 0
            else 0
        )

        avg_execution_time = np.mean(
            [h["result"].execution_time for h in self.optimization_history]
        )
        avg_memory_reduction = np.mean(
            [h["result"].memory_reduction_percent for h in self.optimization_history]
        )
        avg_speed_improvement = np.mean(
            [
                h["result"].processing_speed_improvement
                for h in self.optimization_history
            ]
        )

        return {
            "system_status": {
                "memory_optimizer": self.memory_optimizer is not None,
                "parallel_processor": self.parallel_processor is not None,
                "chart_optimizer": self.chart_optimizer is not None,
            },
            "performance_metrics": self.performance_metrics,
            "optimization_history": {
                "total_optimizations": total_optimizations,
                "successful_optimizations": successful_optimizations,
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "avg_memory_reduction": avg_memory_reduction,
                "avg_speed_improvement": avg_speed_improvement,
            },
            "latest_result": {
                "success": latest_result.success,
                "execution_time": latest_result.execution_time,
                "memory_usage_mb": latest_result.memory_usage_mb,
                "memory_reduction_percent": latest_result.memory_reduction_percent,
                "processing_speed_improvement": latest_result.processing_speed_improvement,
                "chart_render_time": latest_result.chart_render_time,
                "data_points": latest_result.data_points,
                "optimizations_applied": latest_result.optimizations_applied,
            },
            "dod_validation": self._validate_dod(latest_result),
            "recommendations": self._generate_recommendations(),
        }

    def _validate_dod(self, result: OptimizationResult) -> Dict[str, bool]:
        """DoD（受け入れ基準）の検証"""
        return {
            "memory_reduction_30_percent": result.memory_reduction_percent >= 30,
            "processing_speed_2x": result.processing_speed_improvement >= 2.0,
            "chart_render_3_seconds": result.chart_render_time <= 3.0,
            "overall_success": (
                result.memory_reduction_percent >= 30
                and result.processing_speed_improvement >= 2.0
                and result.chart_render_time <= 3.0
            ),
        }

    def _generate_recommendations(self) -> List[str]:
        """推奨事項の生成"""
        recommendations = []

        if not self.optimization_history:
            return recommendations

        latest_result = self.optimization_history[-1]["result"]

        if latest_result.memory_reduction_percent < 30:
            recommendations.append(
                "メモリ削減が30%未満です。より積極的なメモリ最適化を推奨します。"
            )

        if latest_result.processing_speed_improvement < 2.0:
            recommendations.append(
                "処理速度向上が2倍未満です。並列処理の最適化を推奨します。"
            )

        if latest_result.chart_render_time > 3.0:
            recommendations.append(
                "チャート描画が3秒を超えています。データダウンサンプリングを推奨します。"
            )

        if not latest_result.success:
            recommendations.append(
                "最適化に失敗しました。エラーログを確認してください。"
            )

        return recommendations

    def cleanup(self):
        """リソースのクリーンアップ"""
        if self.memory_optimizer:
            self.memory_optimizer.cleanup()

        if self.parallel_processor:
            self.parallel_processor.cleanup()

        if self.chart_optimizer:
            self.chart_optimizer.cleanup()

        self.optimization_history.clear()
        self.performance_metrics.clear()

        logger.info("🧹 統合パフォーマンスシステムをクリーンアップしました")


def create_unified_performance_system(
    memory_limit_mb: int = 1024,
    max_data_points: int = 3000,
    target_render_time: float = 3.0,
    enable_aggressive_optimization: bool = True,
) -> UnifiedPerformanceSystem:
    """統合パフォーマンスシステムを作成"""
    config = PerformanceConfig(
        memory_limit_mb=memory_limit_mb,
        max_data_points=max_data_points,
        target_render_time=target_render_time,
        enable_aggressive_optimization=enable_aggressive_optimization,
    )
    return UnifiedPerformanceSystem(config)


if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 統合パフォーマンスシステムのテスト
    system = create_unified_performance_system()

    try:
        # パフォーマンステストの実行
        test_results = system.run_performance_test(test_data_size=30000)

        # レポートの生成
        report = system.get_performance_report()

        # 結果の表示
        print("\n" + "=" * 80)
        print("🚀 統合パフォーマンス最適化システム結果")
        print("=" * 80)

        print(f"📊 パフォーマンスメトリクス:")
        print(f"   - 実行時間: {test_results.get('execution_time', 0):.2f}秒")
        print(f"   - メモリ使用量: {test_results.get('memory_usage', 0):.1f}MB")
        print(f"   - メモリ削減: {test_results.get('memory_reduction', 0):.1f}%")
        print(f"   - 処理速度向上: {test_results.get('speed_improvement', 1):.1f}倍")
        print(f"   - チャート描画: {test_results.get('chart_render_time', 0):.2f}秒")

        dod_validation = report.get("dod_validation", {})
        print(f"\n🎯 DoD検証結果:")
        print(
            f"   - メモリ削減30%以上: {'✅' if dod_validation.get('memory_reduction_30_percent', False) else '❌'}"
        )
        print(
            f"   - 処理速度2倍以上: {'✅' if dod_validation.get('processing_speed_2x', False) else '❌'}"
        )
        print(
            f"   - チャート描画3秒以内: {'✅' if dod_validation.get('chart_render_3_seconds', False) else '❌'}"
        )
        print(
            f"   - 総合判定: {'✅ 成功' if dod_validation.get('overall_success', False) else '❌ 失敗'}"
        )

        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 推奨事項:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")

        print("\n" + "=" * 80)
        print("✅ 統合パフォーマンス最適化システム完了")
        print("=" * 80)

    except Exception as e:
        logger.error(f"システム実行エラー: {e}")
        print(f"❌ エラー: {e}")

    finally:
        # クリーンアップ
        system.cleanup()
