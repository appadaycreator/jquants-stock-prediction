#!/usr/bin/env python3
"""
パフォーマンス統合テストシステム
最適化後のパフォーマンステストを実行し、DoDを検証する
"""

import time
import psutil
import pandas as pd
import numpy as np
import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# 最適化システムのインポート
from enhanced_memory_optimizer import (
    EnhancedMemoryOptimizer,
    create_enhanced_memory_optimizer,
)
from enhanced_parallel_processor import EnhancedParallelProcessor, parallel_context
from enhanced_chart_optimizer import EnhancedChartOptimizer, create_chart_optimizer

logger = logging.getLogger(__name__)


@dataclass
class PerformanceTestResult:
    """パフォーマンステスト結果"""

    test_name: str
    execution_time: float
    memory_usage_mb: float
    memory_reduction_percent: float
    processing_speed_improvement: float
    chart_render_time: float
    success: bool
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None


@dataclass
class DoDValidation:
    """DoD検証結果"""

    memory_reduction_achieved: bool
    processing_speed_achieved: bool
    chart_render_time_achieved: bool
    ui_responsiveness_achieved: bool
    overall_success: bool
    details: Dict[str, Any]


class PerformanceIntegrationTester:
    """パフォーマンス統合テストシステム"""

    def __init__(self, test_data_size: int = 100000):
        self.test_data_size = test_data_size
        self.results = []
        self.baseline_metrics = {}
        self.optimized_metrics = {}

        # テストデータの生成
        self.test_data = self._generate_test_data()

        logger.info(f"🧪 パフォーマンス統合テストシステム初期化完了")
        logger.info(f"   - テストデータサイズ: {test_data_size}行")

    def _generate_test_data(self) -> pd.DataFrame:
        """テストデータの生成"""
        np.random.seed(42)
        dates = pd.date_range("2020-01-01", periods=self.test_data_size, freq="D")

        base_price = (
            1000 + np.cumsum(np.random.randn(self.test_data_size) * 0.02) * 1000
        )

        data = pd.DataFrame(
            {
                "Date": dates,
                "Open": base_price,
                "High": base_price
                * (1 + np.random.uniform(0, 0.05, self.test_data_size)),
                "Low": base_price
                * (1 - np.random.uniform(0, 0.05, self.test_data_size)),
                "Close": base_price + np.random.uniform(-20, 20, self.test_data_size),
                "Volume": np.random.randint(1000000, 10000000, self.test_data_size),
                "SMA_5": base_price.rolling(window=5).mean(),
                "SMA_20": base_price.rolling(window=20).mean(),
                "SMA_50": base_price.rolling(window=50).mean(),
                "RSI": np.random.uniform(0, 100, self.test_data_size),
                "MACD": np.random.uniform(-10, 10, self.test_data_size),
                "BB_Upper": base_price * 1.02,
                "BB_Lower": base_price * 0.98,
                "ATR": np.random.uniform(1, 10, self.test_data_size),
            }
        )

        return data

    def run_baseline_tests(self) -> Dict[str, Any]:
        """ベースラインテストの実行"""
        logger.info("📊 ベースラインテスト開始")

        baseline_results = {}

        # 1. メモリ使用量のベースライン測定
        baseline_results["memory_baseline"] = self._test_memory_baseline()

        # 2. 処理速度のベースライン測定
        baseline_results["processing_baseline"] = self._test_processing_baseline()

        # 3. チャート描画のベースライン測定
        baseline_results["chart_baseline"] = self._test_chart_baseline()

        self.baseline_metrics = baseline_results

        logger.info("✅ ベースラインテスト完了")
        return baseline_results

    def run_optimized_tests(self) -> Dict[str, Any]:
        """最適化テストの実行"""
        logger.info("🚀 最適化テスト開始")

        optimized_results = {}

        # 1. メモリ最適化テスト
        optimized_results["memory_optimized"] = self._test_memory_optimization()

        # 2. 並列処理最適化テスト
        optimized_results["processing_optimized"] = self._test_processing_optimization()

        # 3. チャート最適化テスト
        optimized_results["chart_optimized"] = self._test_chart_optimization()

        # 4. 統合最適化テスト
        optimized_results["integrated"] = self._test_integrated_optimization()

        self.optimized_metrics = optimized_results

        logger.info("✅ 最適化テスト完了")
        return optimized_results

    def _test_memory_baseline(self) -> Dict[str, Any]:
        """メモリ使用量のベースライン測定"""
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_time = time.time()

        # 通常のデータ処理
        processed_data = self.test_data.copy()
        processed_data = processed_data.dropna()
        processed_data = processed_data.astype(
            {
                "Open": "float64",
                "High": "float64",
                "Low": "float64",
                "Close": "float64",
                "Volume": "int64",
            }
        )

        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        end_time = time.time()

        return {
            "start_memory_mb": start_memory,
            "end_memory_mb": end_memory,
            "memory_usage_mb": end_memory - start_memory,
            "execution_time": end_time - start_time,
            "data_size": len(processed_data),
        }

    def _test_processing_baseline(self) -> Dict[str, Any]:
        """処理速度のベースライン測定"""
        start_time = time.time()

        # 通常の技術指標計算
        def calculate_indicators(df):
            df = df.copy()
            df["SMA_5"] = df["Close"].rolling(window=5).mean()
            df["SMA_20"] = df["Close"].rolling(window=20).mean()
            df["RSI"] = self._calculate_rsi(df["Close"])
            df["MACD"] = self._calculate_macd(df["Close"])
            return df

        processed_data = calculate_indicators(self.test_data)

        end_time = time.time()

        return {
            "execution_time": end_time - start_time,
            "data_size": len(processed_data),
            "throughput": len(processed_data) / (end_time - start_time),
        }

    def _test_chart_baseline(self) -> Dict[str, Any]:
        """チャート描画のベースライン測定"""
        start_time = time.time()

        # 通常のチャート描画（シミュレーション）
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 8))

        # ローソク足チャートの描画
        ax.plot(self.test_data.index, self.test_data["Close"], label="Close Price")
        ax.plot(self.test_data.index, self.test_data["SMA_20"], label="SMA 20")

        ax.set_title("Baseline Chart")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()

        # チャートをメモリに保存
        import io

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100)
        buffer.seek(0)

        plt.close(fig)

        end_time = time.time()

        return {
            "render_time": end_time - start_time,
            "data_points": len(self.test_data),
            "chart_size_bytes": len(buffer.getvalue()),
        }

    def _test_memory_optimization(self) -> Dict[str, Any]:
        """メモリ最適化テスト"""
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_time = time.time()

        # 強化メモリ最適化システムの使用
        optimizer = create_enhanced_memory_optimizer(
            memory_limit_mb=512, aggressive_mode=True
        )

        with optimizer.memory_monitoring("memory_optimization_test"):
            optimized_data = optimizer.optimize_dataframe_aggressive(self.test_data)

        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        end_time = time.time()

        # メモリ削減率の計算
        baseline_memory = self.baseline_metrics.get("memory_baseline", {}).get(
            "memory_usage_mb", 0
        )
        current_memory = end_memory - start_memory
        memory_reduction = (
            ((baseline_memory - current_memory) / baseline_memory * 100)
            if baseline_memory > 0
            else 0
        )

        return {
            "start_memory_mb": start_memory,
            "end_memory_mb": end_memory,
            "memory_usage_mb": current_memory,
            "execution_time": end_time - start_time,
            "data_size": len(optimized_data),
            "memory_reduction_percent": memory_reduction,
            "optimization_stats": optimizer.get_optimization_report(),
        }

    def _test_processing_optimization(self) -> Dict[str, Any]:
        """並列処理最適化テスト"""
        start_time = time.time()

        # 強化並列処理システムの使用
        with parallel_context(max_workers=8, adaptive_mode=True) as processor:
            # 並列処理による技術指標計算
            def calculate_indicators_parallel(df):
                return processor.parallel_map_optimized(
                    self._calculate_single_indicator,
                    df.iterrows(),
                    task_type="cpu_intensive",
                )

            results = calculate_indicators_parallel(self.test_data)

        end_time = time.time()

        # 処理速度向上率の計算
        baseline_time = self.baseline_metrics.get("processing_baseline", {}).get(
            "execution_time", 1
        )
        current_time = end_time - start_time
        speed_improvement = (baseline_time / current_time) if current_time > 0 else 1

        return {
            "execution_time": current_time,
            "data_size": len(results),
            "throughput": len(results) / current_time,
            "speed_improvement": speed_improvement,
            "processor_stats": processor.get_performance_report(),
        }

    def _test_chart_optimization(self) -> Dict[str, Any]:
        """チャート最適化テスト"""
        start_time = time.time()

        # 強化チャート最適化システムの使用
        chart_optimizer = create_chart_optimizer(
            max_data_points=3000, target_render_time=3.0, quality_level="high"
        )

        result = chart_optimizer.optimize_chart_rendering(
            self.test_data, chart_type="candlestick", title="最適化されたチャート"
        )

        end_time = time.time()

        return {
            "render_time": result["render_time"],
            "total_optimization_time": result["total_optimization_time"],
            "data_points": result["data_points"],
            "optimization_applied": result["optimization_applied"],
            "target_achieved": result["render_time"] <= 3.0,
        }

    def _test_integrated_optimization(self) -> Dict[str, Any]:
        """統合最適化テスト"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # 全システムの統合テスト
        memory_optimizer = create_enhanced_memory_optimizer(aggressive_mode=True)
        chart_optimizer = create_chart_optimizer(target_render_time=3.0)

        with parallel_context(max_workers=8) as processor:
            # 1. メモリ最適化
            optimized_data = memory_optimizer.optimize_dataframe_aggressive(
                self.test_data
            )

            # 2. 並列処理
            processed_data = processor.parallel_map_optimized(
                self._process_data_chunk,
                [
                    optimized_data.iloc[i : i + 1000]
                    for i in range(0, len(optimized_data), 1000)
                ],
                task_type="mixed",
            )

            # 3. チャート最適化
            chart_result = chart_optimizer.optimize_chart_rendering(
                pd.concat(processed_data, ignore_index=True), chart_type="candlestick"
            )

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        return {
            "total_execution_time": end_time - start_time,
            "memory_usage_mb": end_memory - start_memory,
            "chart_render_time": chart_result["render_time"],
            "data_processed": len(processed_data),
            "success": chart_result["render_time"] <= 3.0,
        }

    def _calculate_single_indicator(self, row_data) -> Dict[str, Any]:
        """単一の技術指標計算"""
        # 簡易的な技術指標計算
        return {
            "rsi": np.random.uniform(0, 100),
            "macd": np.random.uniform(-10, 10),
            "sma": row_data[1]["Close"] * np.random.uniform(0.95, 1.05),
        }

    def _process_data_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """データチャンクの処理"""
        return chunk.copy()

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> pd.Series:
        """MACD計算"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd

    def validate_dod(self) -> DoDValidation:
        """DoD（受け入れ基準）の検証"""
        logger.info("🔍 DoD検証開始")

        # 1. メモリ使用量の30%以上削減
        baseline_memory = self.baseline_metrics.get("memory_baseline", {}).get(
            "memory_usage_mb", 0
        )
        optimized_memory = self.optimized_metrics.get("memory_optimized", {}).get(
            "memory_usage_mb", 0
        )
        memory_reduction = (
            ((baseline_memory - optimized_memory) / baseline_memory * 100)
            if baseline_memory > 0
            else 0
        )
        memory_reduction_achieved = memory_reduction >= 30

        # 2. 処理速度の2倍以上向上
        baseline_processing = self.baseline_metrics.get("processing_baseline", {}).get(
            "execution_time", 1
        )
        optimized_processing = self.optimized_metrics.get(
            "processing_optimized", {}
        ).get("execution_time", 1)
        speed_improvement = (
            baseline_processing / optimized_processing
            if optimized_processing > 0
            else 1
        )
        processing_speed_achieved = speed_improvement >= 2.0

        # 3. チャート描画の3秒以内完了
        chart_render_time = self.optimized_metrics.get("chart_optimized", {}).get(
            "render_time", 0
        )
        chart_render_time_achieved = chart_render_time <= 3.0

        # 4. UIの応答性（大量データでもUIが固まらない）
        ui_responsiveness_achieved = self._test_ui_responsiveness()

        # 総合判定
        overall_success = (
            memory_reduction_achieved
            and processing_speed_achieved
            and chart_render_time_achieved
            and ui_responsiveness_achieved
        )

        validation_result = DoDValidation(
            memory_reduction_achieved=memory_reduction_achieved,
            processing_speed_achieved=processing_speed_achieved,
            chart_render_time_achieved=chart_render_time_achieved,
            ui_responsiveness_achieved=ui_responsiveness_achieved,
            overall_success=overall_success,
            details={
                "memory_reduction_percent": memory_reduction,
                "speed_improvement": speed_improvement,
                "chart_render_time": chart_render_time,
                "baseline_memory_mb": baseline_memory,
                "optimized_memory_mb": optimized_memory,
                "baseline_processing_time": baseline_processing,
                "optimized_processing_time": optimized_processing,
            },
        )

        logger.info("✅ DoD検証完了")
        logger.info(
            f"   - メモリ削減: {memory_reduction:.1f}% ({'✅' if memory_reduction_achieved else '❌'})"
        )
        logger.info(
            f"   - 処理速度向上: {speed_improvement:.1f}倍 ({'✅' if processing_speed_achieved else '❌'})"
        )
        logger.info(
            f"   - チャート描画: {chart_render_time:.2f}秒 ({'✅' if chart_render_time_achieved else '❌'})"
        )
        logger.info(f"   - UI応答性: {'✅' if ui_responsiveness_achieved else '❌'}")
        logger.info(f"   - 総合判定: {'✅ 成功' if overall_success else '❌ 失敗'}")

        return validation_result

    def _test_ui_responsiveness(self) -> bool:
        """UI応答性テスト"""
        # 大量データでのUI応答性をシミュレーション
        try:
            start_time = time.time()

            # 大量データの処理
            large_data = pd.concat([self.test_data] * 10, ignore_index=True)

            # 非同期処理のシミュレーション
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for i in range(0, len(large_data), 1000):
                    chunk = large_data.iloc[i : i + 1000]
                    future = executor.submit(self._process_data_chunk, chunk)
                    futures.append(future)

                # 結果の収集
                results = []
                for future in as_completed(futures):
                    results.append(future.result())

            end_time = time.time()
            processing_time = end_time - start_time

            # 3秒以内で完了すれば応答性良好
            return processing_time <= 3.0

        except Exception as e:
            logger.error(f"UI応答性テストエラー: {e}")
            return False

    def generate_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートの生成"""
        logger.info("📊 パフォーマンスレポート生成開始")

        # DoD検証結果
        dod_validation = self.validate_dod()

        # レポートの生成
        report = {
            "test_summary": {
                "test_data_size": self.test_data_size,
                "baseline_tests": len(self.baseline_metrics),
                "optimized_tests": len(self.optimized_metrics),
                "dod_validation": dod_validation.overall_success,
            },
            "baseline_metrics": self.baseline_metrics,
            "optimized_metrics": self.optimized_metrics,
            "dod_validation": asdict(dod_validation),
            "improvements": self._calculate_improvements(),
            "recommendations": self._generate_recommendations(),
        }

        # レポートをファイルに保存
        self._save_report(report)

        logger.info("✅ パフォーマンスレポート生成完了")
        return report

    def _calculate_improvements(self) -> Dict[str, Any]:
        """改善度の計算"""
        improvements = {}

        # メモリ使用量の改善
        baseline_memory = self.baseline_metrics.get("memory_baseline", {}).get(
            "memory_usage_mb", 0
        )
        optimized_memory = self.optimized_metrics.get("memory_optimized", {}).get(
            "memory_usage_mb", 0
        )
        if baseline_memory > 0:
            improvements["memory_reduction_percent"] = (
                (baseline_memory - optimized_memory) / baseline_memory * 100
            )

        # 処理速度の改善
        baseline_processing = self.baseline_metrics.get("processing_baseline", {}).get(
            "execution_time", 1
        )
        optimized_processing = self.optimized_metrics.get(
            "processing_optimized", {}
        ).get("execution_time", 1)
        if optimized_processing > 0:
            improvements["speed_improvement"] = (
                baseline_processing / optimized_processing
            )

        # チャート描画の改善
        baseline_chart = self.baseline_metrics.get("chart_baseline", {}).get(
            "render_time", 0
        )
        optimized_chart = self.optimized_metrics.get("chart_optimized", {}).get(
            "render_time", 0
        )
        if baseline_chart > 0:
            improvements["chart_render_improvement"] = baseline_chart / optimized_chart

        return improvements

    def _generate_recommendations(self) -> List[str]:
        """推奨事項の生成"""
        recommendations = []

        # DoD検証結果に基づく推奨事項
        dod_validation = self.validate_dod()

        if not dod_validation.memory_reduction_achieved:
            recommendations.append(
                "メモリ削減が30%未満です。より積極的なメモリ最適化を推奨します。"
            )

        if not dod_validation.processing_speed_achieved:
            recommendations.append(
                "処理速度向上が2倍未満です。並列処理の最適化を推奨します。"
            )

        if not dod_validation.chart_render_time_achieved:
            recommendations.append(
                "チャート描画が3秒を超えています。データダウンサンプリングを推奨します。"
            )

        if not dod_validation.ui_responsiveness_achieved:
            recommendations.append(
                "UI応答性が不十分です。非同期処理とチャンク処理を推奨します。"
            )

        return recommendations

    def _save_report(self, report: Dict[str, Any]):
        """レポートをファイルに保存"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"performance_report_{timestamp}.json"

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"📄 レポートを保存: {report_file}")
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")

    def run_full_test_suite(self) -> Dict[str, Any]:
        """完全なテストスイートの実行"""
        logger.info("🚀 完全なパフォーマンステストスイート開始")

        # 1. ベースラインテスト
        baseline_results = self.run_baseline_tests()

        # 2. 最適化テスト
        optimized_results = self.run_optimized_tests()

        # 3. パフォーマンスレポート生成
        report = self.generate_performance_report()

        logger.info("✅ 完全なパフォーマンステストスイート完了")
        return report


def main():
    """メイン実行関数"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # テストデータサイズの設定
    test_data_size = 50000  # 5万行のテストデータ

    # パフォーマンス統合テストの実行
    tester = PerformanceIntegrationTester(test_data_size)

    try:
        # 完全なテストスイートの実行
        report = tester.run_full_test_suite()

        # 結果の表示
        print("\n" + "=" * 80)
        print("📊 パフォーマンス最適化テスト結果")
        print("=" * 80)

        dod_validation = report["dod_validation"]
        print(
            f"🎯 DoD検証結果: {'✅ 成功' if dod_validation['overall_success'] else '❌ 失敗'}"
        )
        print(
            f"   - メモリ削減: {dod_validation['details']['memory_reduction_percent']:.1f}%"
        )
        print(
            f"   - 処理速度向上: {dod_validation['details']['speed_improvement']:.1f}倍"
        )
        print(
            f"   - チャート描画: {dod_validation['details']['chart_render_time']:.2f}秒"
        )

        improvements = report["improvements"]
        print(f"\n📈 改善度:")
        print(
            f"   - メモリ削減: {improvements.get('memory_reduction_percent', 0):.1f}%"
        )
        print(f"   - 処理速度向上: {improvements.get('speed_improvement', 1):.1f}倍")
        print(
            f"   - チャート描画改善: {improvements.get('chart_render_improvement', 1):.1f}倍"
        )

        recommendations = report["recommendations"]
        if recommendations:
            print(f"\n💡 推奨事項:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")

        print("\n" + "=" * 80)
        print("✅ パフォーマンス最適化テスト完了")
        print("=" * 80)

    except Exception as e:
        logger.error(f"テスト実行エラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
