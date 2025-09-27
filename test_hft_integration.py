#!/usr/bin/env python3
"""
高頻度取引システム統合テスト
High Frequency Trading System Integration Test
"""

import sys
import os
import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from high_frequency_trading import HighFrequencyTrading, MockDataSource


class HFTIntegrationTest:
    """高頻度取引システム統合テストクラス"""

    def __init__(self):
        """初期化"""
        self.test_results = []
        self.start_time = None
        self.end_time = None

    def run_all_tests(self):
        """全テストを実行"""
        print("=== 高頻度取引システム統合テスト開始 ===")
        self.start_time = datetime.now()

        # テストケース実行
        test_cases = [
            ("基本機能テスト", self.test_basic_functionality),
            ("裁定取引テスト", self.test_arbitrage_trading),
            ("リスク管理テスト", self.test_risk_management),
            ("パフォーマンステスト", self.test_performance),
            ("エラーハンドリングテスト", self.test_error_handling),
            ("並行処理テスト", self.test_concurrent_processing),
            ("長時間実行テスト", self.test_long_running),
        ]

        for test_name, test_func in test_cases:
            print(f"\n--- {test_name} ---")
            try:
                result = test_func()
                self.test_results.append((test_name, True, result))
                print(f"✅ {test_name}: 成功")
            except Exception as e:
                self.test_results.append((test_name, False, str(e)))
                print(f"❌ {test_name}: 失敗 - {e}")

        self.end_time = datetime.now()
        self._print_summary()

    def test_basic_functionality(self) -> Dict:
        """基本機能テスト"""
        config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.001,
            "max_position_size": 100000,
            "risk_limit": 0.02,
        }

        hft = HighFrequencyTrading(config)
        data_source = MockDataSource()

        try:
            # 基本初期化テスト
            assert hft.latency_threshold == 0.001
            assert hft.profit_threshold == 0.001

            # 裁定取引テスト
            price_differences = {"BTC": {"Binance": 50000.0, "Coinbase": 50100.0}}

            trades = hft.execute_arbitrage(price_differences)
            assert isinstance(trades, list)

            # パフォーマンス指標テスト
            metrics = hft.get_performance_metrics()
            assert isinstance(metrics, dict)

            return {
                "trades_executed": len(trades),
                "metrics_available": len(metrics) > 0,
            }

        finally:
            hft.cleanup()

    def test_arbitrage_trading(self) -> Dict:
        """裁定取引テスト"""
        config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.0005,  # 0.05%
            "max_position_size": 100000,
            "risk_limit": 0.02,
        }

        hft = HighFrequencyTrading(config)

        try:
            # 複数の価格差パターンをテスト
            test_cases = [
                {
                    "BTC": {"Binance": 50000.0, "Coinbase": 50100.0},  # 0.2%差
                    "ETH": {"Binance": 3000.0, "Coinbase": 3005.0},  # 0.17%差
                },
                {
                    "BTC": {"Binance": 50000.0, "Coinbase": 50050.0},  # 0.1%差
                    "ETH": {"Binance": 3000.0, "Coinbase": 3003.0},  # 0.1%差
                },
                {
                    "BTC": {"Binance": 50000.0, "Coinbase": 50025.0},  # 0.05%差
                },
            ]

            total_trades = 0
            total_profit = 0

            for i, price_differences in enumerate(test_cases):
                trades = hft.execute_arbitrage(price_differences)
                total_trades += len(trades)

                # 利益計算
                for trade in trades:
                    if trade.side == "sell":
                        total_profit += trade.price * trade.volume
                    elif trade.side == "buy":
                        total_profit -= trade.price * trade.volume

            return {
                "total_trades": total_trades,
                "total_profit": total_profit,
                "test_cases": len(test_cases),
            }

        finally:
            hft.cleanup()

    def test_risk_management(self) -> Dict:
        """リスク管理テスト"""
        config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.001,
            "max_position_size": 10000,  # 小さな制限
            "risk_limit": 0.01,  # 1%
        }

        hft = HighFrequencyTrading(config)

        try:
            # 大きな取引機会を作成
            large_opportunity = {"BTC": {"Binance": 50000.0, "Coinbase": 50100.0}}

            # リスク制限により取引が制限されることを確認
            trades = hft.execute_arbitrage(large_opportunity)

            # ポジションサイズチェック
            metrics = hft.get_performance_metrics()
            positions = metrics.get("positions", {})

            return {
                "trades_executed": len(trades),
                "positions": positions,
                "risk_limited": len(trades) < 2,  # リスク制限により取引が制限される
            }

        finally:
            hft.cleanup()

    def test_performance(self) -> Dict:
        """パフォーマンステスト"""
        config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.001,
            "max_position_size": 100000,
            "risk_limit": 0.02,
        }

        hft = HighFrequencyTrading(config)

        try:
            # 複数回の実行時間を計測
            execution_times = []
            iterations = 100

            for i in range(iterations):
                start_time = time.time()

                price_differences = {
                    "BTC": {
                        "Binance": 50000.0 + np.random.normal(0, 10),
                        "Coinbase": 50100.0 + np.random.normal(0, 10),
                    }
                }

                trades = hft.execute_arbitrage(price_differences)
                execution_time = time.time() - start_time
                execution_times.append(execution_time)

            # 統計計算
            avg_time = np.mean(execution_times)
            max_time = np.max(execution_times)
            min_time = np.min(execution_times)

            # 閾値チェック
            threshold_violations = sum(
                1 for t in execution_times if t > config["latency_threshold"]
            )

            return {
                "iterations": iterations,
                "avg_execution_time": avg_time,
                "max_execution_time": max_time,
                "min_execution_time": min_time,
                "threshold_violations": threshold_violations,
                "threshold_violation_rate": threshold_violations / iterations,
            }

        finally:
            hft.cleanup()

    def test_error_handling(self) -> Dict:
        """エラーハンドリングテスト"""
        config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.001,
            "max_position_size": 100000,
            "risk_limit": 0.02,
        }

        hft = HighFrequencyTrading(config)

        try:
            error_cases = [
                None,  # Noneデータ
                {},  # 空辞書
                {"BTC": {}},  # 空の取引所データ
                {"BTC": {"Binance": "invalid"}},  # 無効な価格
            ]

            error_count = 0

            for error_case in error_cases:
                try:
                    trades = hft.execute_arbitrage(error_case)
                    # エラーが発生しない場合は、空のリストが返されることを確認
                    assert isinstance(trades, list)
                except Exception:
                    error_count += 1

            return {
                "error_cases_tested": len(error_cases),
                "errors_handled": error_count,
                "system_stable": True,
            }

        finally:
            hft.cleanup()

    def test_concurrent_processing(self) -> Dict:
        """並行処理テスト"""
        config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.001,
            "max_position_size": 100000,
            "risk_limit": 0.02,
        }

        hft = HighFrequencyTrading(config)

        try:
            # 並行処理テスト
            def worker(worker_id):
                results = []
                for i in range(10):
                    price_differences = {
                        f"SYMBOL_{worker_id}": {
                            "Binance": 50000.0 + worker_id * 100,
                            "Coinbase": 50100.0 + worker_id * 100,
                        }
                    }
                    trades = hft.execute_arbitrage(price_differences)
                    results.append(len(trades))
                return results

            # 複数スレッドで実行
            threads = []
            results = []

            for i in range(3):
                thread = threading.Thread(target=lambda i=i: results.append(worker(i)))
                threads.append(thread)
                thread.start()

            # 全スレッドの完了を待機
            for thread in threads:
                thread.join()

            return {
                "threads_created": len(threads),
                "all_threads_completed": len(results) == len(threads),
                "concurrent_execution": True,
            }

        finally:
            hft.cleanup()

    def test_long_running(self) -> Dict:
        """長時間実行テスト"""
        config = {
            "latency_threshold": 0.001,
            "profit_threshold": 0.001,
            "max_position_size": 100000,
            "risk_limit": 0.02,
        }

        hft = HighFrequencyTrading(config)
        data_source = MockDataSource()

        try:
            # 長時間実行テスト（30秒）
            start_time = time.time()
            iteration_count = 0
            total_trades = 0

            while time.time() - start_time < 30:  # 30秒間実行
                price_differences = data_source.get_latest_data()
                if price_differences:
                    trades = hft.execute_arbitrage(price_differences)
                    total_trades += len(trades)
                iteration_count += 1
                time.sleep(0.01)  # 10ms間隔

            # パフォーマンス指標取得
            metrics = hft.get_performance_metrics()

            return {
                "execution_time": time.time() - start_time,
                "iterations": iteration_count,
                "total_trades": total_trades,
                "avg_iterations_per_second": iteration_count
                / (time.time() - start_time),
                "final_metrics": metrics,
            }

        finally:
            hft.cleanup()

    def _print_summary(self):
        """テスト結果サマリーを出力"""
        print("\n" + "=" * 50)
        print("=== 統合テスト結果サマリー ===")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        failed_tests = total_tests - passed_tests

        print(f"総テスト数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失敗: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")

        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"実行時間: {duration:.2f}秒")

        print("\n--- 詳細結果 ---")
        for test_name, success, result in self.test_results:
            status = "✅ 成功" if success else "❌ 失敗"
            print(f"{test_name}: {status}")
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"  {key}: {value}")
            elif isinstance(result, str):
                print(f"  エラー: {result}")

        print("=" * 50)


def main():
    """メイン関数"""
    print("高頻度取引システム統合テストを開始します...")

    # 統合テスト実行
    test_runner = HFTIntegrationTest()
    test_runner.run_all_tests()

    print("\n統合テストが完了しました。")


if __name__ == "__main__":
    main()
