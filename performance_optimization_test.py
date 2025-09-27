#!/usr/bin/env python3
"""
パフォーマンス最適化の実装検証システム
最適化効果を測定し、改善点を特定する包括的なテストシステム
"""

import pandas as pd
import numpy as np
import logging
import time
import psutil
import gc
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from unified_system import UnifiedSystem
from unified_performance_optimizer import create_unified_performance_optimizer
from advanced_performance_optimizer import create_performance_optimizer
from enhanced_model_comparator import create_enhanced_model_comparator
from ultra_efficient_dataframe_processor import create_ultra_efficient_processor

logger = logging.getLogger(__name__)


@dataclass
class PerformanceTestResult:
    """パフォーマンステスト結果"""

    test_name: str
    baseline_time: float
    optimized_time: float
    time_improvement: float
    baseline_memory: float
    optimized_memory: float
    memory_improvement: float
    success: bool
    error_message: str = ""


class PerformanceOptimizationTester:
    """パフォーマンス最適化テストクラス"""

    def __init__(self):
        self.system = UnifiedSystem("PerformanceOptimizationTester")
        self.logger = logging.getLogger(__name__)
        self.test_results = []

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """包括的なパフォーマンステストを実行"""
        self.logger.info("🚀 包括的パフォーマンステスト開始")

        test_results = {}

        # 1. データフレーム処理最適化テスト
        test_results["dataframe_processing"] = self._test_dataframe_processing()

        # 2. 技術指標計算最適化テスト
        test_results["technical_indicators"] = self._test_technical_indicators()

        # 3. モデル比較最適化テスト
        test_results["model_comparison"] = self._test_model_comparison()

        # 4. メモリ最適化テスト
        test_results["memory_optimization"] = self._test_memory_optimization()

        # 5. 並列処理最適化テスト
        test_results["parallel_processing"] = self._test_parallel_processing()

        # 総合レポートを生成
        comprehensive_report = self._generate_comprehensive_report(test_results)

        self.logger.info("✅ 包括的パフォーマンステスト完了")
        return comprehensive_report

    def _test_dataframe_processing(self) -> Dict[str, Any]:
        """データフレーム処理最適化テスト"""
        self.logger.info("📊 データフレーム処理最適化テスト開始")

        # テストデータ生成
        np.random.seed(42)
        n_rows = 10000
        n_cols = 20

        data = {f"col_{i}": np.random.randn(n_rows) for i in range(n_cols)}
        df = pd.DataFrame(data)

        # ベースライン処理（最適化なし）
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        baseline_df = df.copy()
        baseline_df = baseline_df.fillna(method="ffill")
        baseline_df = baseline_df.dropna()
        baseline_df = baseline_df.astype(
            {f"col_{i}": np.float32 for i in range(n_cols)}
        )

        baseline_time = time.time() - start_time
        baseline_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        # 最適化処理
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        processor = create_ultra_efficient_processor()
        operations = [
            {"type": "dtype_optimization", "params": {}},
            {
                "type": "inplace",
                "params": {"type": "fillna", "params": {"method": "ffill"}},
            },
            {"type": "inplace", "params": {"type": "dropna", "params": {}}},
        ]

        optimized_df = processor.process_dataframe_ultra_efficient(df, operations)

        optimized_time = time.time() - start_time
        optimized_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        # 結果を返す
        return {
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "time_improvement": (baseline_time - optimized_time) / baseline_time * 100,
            "baseline_memory": baseline_memory,
            "optimized_memory": optimized_memory,
            "memory_improvement": (baseline_memory - optimized_memory)
            / baseline_memory
            * 100,
            "success": True,
        }

    def _test_technical_indicators(self) -> Dict[str, Any]:
        """技術指標計算最適化テスト"""
        self.logger.info("📈 技術指標計算最適化テスト開始")

        # テストデータ生成
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=1000, freq="D")
        base_price = 1000 + np.cumsum(np.random.randn(1000) * 0.02) * 1000

        df = pd.DataFrame(
            {
                "Date": dates,
                "Open": base_price,
                "High": base_price * (1 + np.random.uniform(0, 0.05, 1000)),
                "Low": base_price * (1 - np.random.uniform(0, 0.05, 1000)),
                "Close": base_price + np.random.uniform(-20, 20, 1000),
                "Volume": np.random.randint(1000000, 10000000, 1000),
            }
        )

        # ベースライン処理（最適化なし）
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        baseline_df = df.copy()
        # 簡単な技術指標計算
        baseline_df["SMA_20"] = baseline_df["Close"].rolling(window=20).mean()
        baseline_df["RSI"] = 100 - (
            100 / (1 + baseline_df["Close"].diff().rolling(window=14).mean())
        )

        baseline_time = time.time() - start_time
        baseline_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        # 最適化処理
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        optimizer = create_performance_optimizer()
        optimized_df = optimizer.technical_indicators.calculate_indicators_optimized(df)

        optimized_time = time.time() - start_time
        optimized_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        return {
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "time_improvement": (baseline_time - optimized_time) / baseline_time * 100,
            "baseline_memory": baseline_memory,
            "optimized_memory": optimized_memory,
            "memory_improvement": (baseline_memory - optimized_memory)
            / baseline_memory
            * 100,
            "success": True,
        }

    def _test_model_comparison(self) -> Dict[str, Any]:
        """モデル比較最適化テスト"""
        self.logger.info("🤖 モデル比較最適化テスト開始")

        # テストデータ生成
        np.random.seed(42)
        n_samples = 1000
        n_features = 10

        X = np.random.randn(n_samples, n_features)
        y = np.random.randn(n_samples)

        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        models_config = {
            "random_forest": {
                "type": "random_forest",
                "params": {"n_estimators": 50, "random_state": 42},
            },
            "linear_regression": {"type": "linear_regression", "params": {}},
            "ridge": {"type": "ridge", "params": {"alpha": 1.0}},
        }

        # ベースライン処理（最適化なし）
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # 簡単なモデル比較
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.linear_model import LinearRegression, Ridge
        from sklearn.metrics import mean_absolute_error

        baseline_results = []
        for model_name, config in models_config.items():
            if config["type"] == "random_forest":
                model = RandomForestRegressor(**config["params"])
            elif config["type"] == "linear_regression":
                model = LinearRegression(**config["params"])
            elif config["type"] == "ridge":
                model = Ridge(**config["params"])

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            baseline_results.append({"model": model_name, "mae": mae})

        baseline_time = time.time() - start_time
        baseline_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        # 最適化処理
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        comparator = create_enhanced_model_comparator(use_cache=True, use_parallel=True)
        optimized_results = comparator.compare_models_enhanced(
            models_config, X_train, X_test, y_train, y_test
        )

        optimized_time = time.time() - start_time
        optimized_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        return {
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "time_improvement": (baseline_time - optimized_time) / baseline_time * 100,
            "baseline_memory": baseline_memory,
            "optimized_memory": optimized_memory,
            "memory_improvement": (baseline_memory - optimized_memory)
            / baseline_memory
            * 100,
            "success": True,
        }

    def _test_memory_optimization(self) -> Dict[str, Any]:
        """メモリ最適化テスト"""
        self.logger.info("💾 メモリ最適化テスト開始")

        # テストデータ生成
        np.random.seed(42)
        n_rows = 50000
        n_cols = 50

        data = {f"col_{i}": np.random.randn(n_rows) for i in range(n_cols)}
        df = pd.DataFrame(data)

        # ベースライン処理（最適化なし）
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        baseline_df = df.copy()
        baseline_df = baseline_df.fillna(method="ffill")
        baseline_df = baseline_df.dropna()

        baseline_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        # 最適化処理
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        optimizer = create_performance_optimizer()
        optimized_df = optimizer.memory_optimizer.optimize_dataframe_memory(df)
        optimized_df = optimized_df.fillna(method="ffill")
        optimized_df = optimized_df.dropna()

        optimized_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        )

        return {
            "baseline_memory": baseline_memory,
            "optimized_memory": optimized_memory,
            "memory_improvement": (baseline_memory - optimized_memory)
            / baseline_memory
            * 100,
            "success": True,
        }

    def _test_parallel_processing(self) -> Dict[str, Any]:
        """並列処理最適化テスト"""
        self.logger.info("🚀 並列処理最適化テスト開始")

        # テストデータ生成
        np.random.seed(42)
        n_samples = 2000
        n_features = 15

        X = np.random.randn(n_samples, n_features)
        y = np.random.randn(n_samples)

        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        models_config = {
            f"model_{i}": {
                "type": "random_forest",
                "params": {"n_estimators": 30, "random_state": 42},
            }
            for i in range(5)
        }

        # ベースライン処理（逐次処理）
        start_time = time.time()

        comparator_sequential = create_enhanced_model_comparator(use_parallel=False)
        sequential_results = comparator_sequential.compare_models_enhanced(
            models_config, X_train, X_test, y_train, y_test
        )

        sequential_time = time.time() - start_time

        # 最適化処理（並列処理）
        start_time = time.time()

        comparator_parallel = create_enhanced_model_comparator(use_parallel=True)
        parallel_results = comparator_parallel.compare_models_enhanced(
            models_config, X_train, X_test, y_train, y_test
        )

        parallel_time = time.time() - start_time

        return {
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "speedup": sequential_time / parallel_time,
            "success": True,
        }

    def _generate_comprehensive_report(
        self, test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """包括的なレポートを生成"""
        report = {
            "test_summary": {
                "total_tests": len(test_results),
                "successful_tests": sum(
                    1
                    for result in test_results.values()
                    if result.get("success", False)
                ),
                "failed_tests": sum(
                    1
                    for result in test_results.values()
                    if not result.get("success", False)
                ),
            },
            "performance_improvements": {},
            "recommendations": [],
        }

        # パフォーマンス改善の計算
        for test_name, result in test_results.items():
            if result.get("success", False):
                if "time_improvement" in result:
                    report["performance_improvements"][
                        f"{test_name}_time_improvement"
                    ] = result["time_improvement"]
                if "memory_improvement" in result:
                    report["performance_improvements"][
                        f"{test_name}_memory_improvement"
                    ] = result["memory_improvement"]
                if "speedup" in result:
                    report["performance_improvements"][f"{test_name}_speedup"] = result[
                        "speedup"
                    ]

        # 推奨事項の生成
        if test_results.get("dataframe_processing", {}).get("time_improvement", 0) > 0:
            report["recommendations"].append("データフレーム処理の最適化が効果的です")

        if test_results.get("model_comparison", {}).get("time_improvement", 0) > 0:
            report["recommendations"].append("モデル比較の最適化が効果的です")

        if test_results.get("memory_optimization", {}).get("memory_improvement", 0) > 0:
            report["recommendations"].append("メモリ最適化が効果的です")

        if test_results.get("parallel_processing", {}).get("speedup", 1) > 1:
            report["recommendations"].append("並列処理の活用が効果的です")

        return report

    def log_test_results(self, report: Dict[str, Any]):
        """テスト結果をログ出力"""
        self.logger.info("📊 パフォーマンス最適化テスト結果:")

        summary = report["test_summary"]
        self.logger.info(f"  📈 総テスト数: {summary['total_tests']}")
        self.logger.info(f"  ✅ 成功: {summary['successful_tests']}")
        self.logger.info(f"  ❌ 失敗: {summary['failed_tests']}")

        improvements = report["performance_improvements"]
        for metric, value in improvements.items():
            if "time_improvement" in metric:
                self.logger.info(f"  ⏱️ {metric}: {value:.1f}%改善")
            elif "memory_improvement" in metric:
                self.logger.info(f"  💾 {metric}: {value:.1f}%改善")
            elif "speedup" in metric:
                self.logger.info(f"  🚀 {metric}: {value:.1f}倍高速化")

        recommendations = report["recommendations"]
        if recommendations:
            self.logger.info("  💡 推奨事項:")
            for rec in recommendations:
                self.logger.info(f"    - {rec}")


def run_performance_optimization_tests() -> Dict[str, Any]:
    """パフォーマンス最適化テストを実行"""
    tester = PerformanceOptimizationTester()
    report = tester.run_comprehensive_tests()
    tester.log_test_results(report)
    return report


if __name__ == "__main__":
    # パフォーマンス最適化テストを実行
    test_report = run_performance_optimization_tests()

    print("📊 パフォーマンス最適化テスト完了")
    print(
        f"✅ 成功: {test_report['test_summary']['successful_tests']}/{test_report['test_summary']['total_tests']}"
    )

    if test_report["recommendations"]:
        print("💡 推奨事項:")
        for rec in test_report["recommendations"]:
            print(f"  - {rec}")
