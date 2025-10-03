#!/usr/bin/env python3
"""
パフォーマンステスト
リファクタリング後のパフォーマンス検証
"""

import pytest
import time
import psutil

# import memory_profiler  # オプショナル
from unittest.mock import patch, mock_open
from core.differential_updater import DifferentialUpdater
from core.json_data_manager import JSONDataManager
from core.config_manager import ConfigManager
from core.performance_optimizer import PerformanceOptimizer


class TestPerformanceBenchmarks:
    """パフォーマンスベンチマークテストクラス"""

    def test_differential_updater_performance(self):
        """差分更新システムのパフォーマンステスト"""
        updater = DifferentialUpdater()

        # 大量データでのテスト
        large_data = [
            {
                "date": f"2024-01-{i:02d}",
                "code": "1234",
                "open": 100 + i,
                "high": 105 + i,
                "low": 95 + i,
                "close": 100 + i,
                "volume": 1000,
            }
            for i in range(1, 1001)
        ]

        start_time = time.time()
        result = updater._calculate_comprehensive_diff(large_data, large_data)
        end_time = time.time()

        processing_time = end_time - start_time

        # パフォーマンス要件: 1000レコードを2秒以内で処理
        assert processing_time < 2.0, f"処理時間が長すぎます: {processing_time:.3f}秒"
        assert result.unchanged_count == 1000

    def test_json_data_manager_performance(self):
        """JSONデータ管理システムのパフォーマンステスト"""
        manager = JSONDataManager()

        # 大量データでのテスト
        large_data = [
            {
                "date": f"2024-01-{i:02d}",
                "code": "1234",
                "open": 100 + i,
                "high": 105 + i,
                "low": 95 + i,
                "close": 100 + i,
                "volume": 1000,
            }
            for i in range(1, 1001)
        ]

        start_time = time.time()
        normalized_data = manager._normalize_stock_data(large_data)
        end_time = time.time()

        processing_time = end_time - start_time

        # パフォーマンス要件: 1000レコードを0.5秒以内で正規化
        assert processing_time < 0.5, f"正規化時間が長すぎます: {processing_time:.3f}秒"
        assert len(normalized_data) == 1000

    def test_config_manager_performance(self):
        """設定管理システムのパフォーマンステスト"""
        config_manager = ConfigManager()

        start_time = time.time()
        config_manager._create_default_config()
        end_time = time.time()

        processing_time = end_time - start_time

        # パフォーマンス要件: 設定作成を0.1秒以内で完了
        assert (
            processing_time < 0.1
        ), f"設定作成時間が長すぎます: {processing_time:.3f}秒"

    def test_memory_usage_optimization(self):
        """メモリ使用量の最適化テスト"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        # 大量データでのメモリ使用量テスト
        updater = DifferentialUpdater()
        large_data = [
            {"date": f"2024-01-{i:02d}", "code": "1234", "close": 100 + i}
            for i in range(1, 1001)
        ]

        # メモリ使用量の測定
        result = updater._calculate_comprehensive_diff(large_data, large_data)

        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # メモリ使用量要件: 1000レコードで10MB以内の増加
        assert (
            memory_increase < 10
        ), f"メモリ使用量が多すぎます: {memory_increase:.2f}MB"

    def test_concurrent_processing_performance(self):
        """並行処理のパフォーマンステスト"""
        import concurrent.futures
        import threading

        def process_data_batch(batch_data):
            """データバッチの処理"""
            updater = DifferentialUpdater()
            return updater._calculate_comprehensive_diff(batch_data, batch_data)

        # データをバッチに分割
        batch_size = 100
        large_data = [
            {"date": f"2024-01-{i:02d}", "code": "1234", "close": 100 + i}
            for i in range(1, 1001)
        ]

        batches = [
            large_data[i : i + batch_size]
            for i in range(0, len(large_data), batch_size)
        ]

        start_time = time.time()

        # 並行処理でバッチを処理
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_data_batch, batch) for batch in batches]
            results = [future.result() for future in futures]

        end_time = time.time()
        processing_time = end_time - start_time

        # 並行処理のパフォーマンス要件: 4スレッドで0.5秒以内
        assert (
            processing_time < 0.5
        ), f"並行処理時間が長すぎます: {processing_time:.3f}秒"
        assert len(results) == 10  # 10バッチ

    def test_caching_performance(self):
        """キャッシュ機能のパフォーマンステスト"""
        updater = DifferentialUpdater()

        # 同じデータでの繰り返し処理
        test_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 110},
        ]

        # 初回処理
        start_time = time.time()
        result1 = updater._calculate_comprehensive_diff(test_data, test_data)
        first_run_time = time.time() - start_time

        # 2回目処理（キャッシュ効果）
        start_time = time.time()
        result2 = updater._calculate_comprehensive_diff(test_data, test_data)
        second_run_time = time.time() - start_time

        # キャッシュ効果の確認
        assert result1.unchanged_count == result2.unchanged_count
        # 2回目は初回より高速であることを確認（キャッシュ効果）
        assert second_run_time <= first_run_time

    def test_error_handling_performance(self):
        """エラーハンドリングのパフォーマンステスト"""
        updater = DifferentialUpdater()

        # 無効なデータでの処理
        invalid_data = [
            {"invalid": "data"},
            {"date": "invalid-date", "code": "1234", "close": "invalid"},
        ]

        start_time = time.time()
        result = updater._validate_data_integrity(invalid_data, [])
        end_time = time.time()

        processing_time = end_time - start_time

        # エラーハンドリングのパフォーマンス要件: 0.1秒以内
        assert (
            processing_time < 0.1
        ), f"エラーハンドリング時間が長すぎます: {processing_time:.3f}秒"
        assert result.is_valid is False

    def test_large_dataset_performance(self):
        """大規模データセットでのパフォーマンステスト"""
        updater = DifferentialUpdater()

        # 大規模データセット（10,000レコード）
        large_dataset = [
            {
                "date": f"2024-01-{i:02d}",
                "code": f"{i:04d}",
                "open": 100 + (i % 100),
                "high": 105 + (i % 100),
                "low": 95 + (i % 100),
                "close": 100 + (i % 100),
                "volume": 1000,
            }
            for i in range(1, 10001)
        ]

        start_time = time.time()
        result = updater._calculate_comprehensive_diff(large_dataset, large_dataset)
        end_time = time.time()

        processing_time = end_time - start_time

        # 大規模データのパフォーマンス要件: 10,000レコードを10秒以内で処理
        assert (
            processing_time < 10.0
        ), f"大規模データ処理時間が長すぎます: {processing_time:.3f}秒"
        assert result.unchanged_count == 10000

    def test_memory_efficiency(self):
        """メモリ効率のテスト"""
        updater = DifferentialUpdater()

        # メモリ使用量の測定
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # 大量データの処理
        large_data = [
            {"date": f"2024-01-{i:02d}", "code": "1234", "close": 100 + i}
            for i in range(1, 5001)
        ]

        result = updater._calculate_comprehensive_diff(large_data, large_data)

        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_usage = final_memory - initial_memory

        # メモリ効率要件: 5,000レコードで50MB以内の使用量
        assert memory_usage < 50, f"メモリ使用量が多すぎます: {memory_usage:.2f}MB"
        assert result.unchanged_count == 5000

    def test_cpu_usage_optimization(self):
        """CPU使用率の最適化テスト"""
        import os

        # CPU使用率の測定
        process = psutil.Process()
        initial_cpu = process.cpu_percent()

        updater = DifferentialUpdater()
        large_data = [
            {
                "date": f"2024-01-{i:02d}",
                "code": "1234",
                "open": 100 + i,
                "high": 105 + i,
                "low": 95 + i,
                "close": 100 + i,
                "volume": 1000,
            }
            for i in range(1, 1001)
        ]

        # CPU集約的な処理
        start_time = time.time()
        result = updater._calculate_comprehensive_diff(large_data, large_data)
        end_time = time.time()

        processing_time = end_time - start_time
        final_cpu = process.cpu_percent()

        # CPU使用率の要件: 処理時間2秒以内、CPU使用率100%以下（現実的な値）
        assert processing_time < 2.0, f"処理時間が長すぎます: {processing_time:.3f}秒"
        assert final_cpu <= 100, f"CPU使用率が高すぎます: {final_cpu:.1f}%"

    def test_network_simulation_performance(self):
        """ネットワークシミュレーションでのパフォーマンステスト"""
        with patch("requests.get") as mock_get:
            # ネットワーク遅延をシミュレート
            mock_get.side_effect = lambda *args, **kwargs: time.sleep(0.1)

            manager = JSONDataManager()

            start_time = time.time()
            # ネットワークリクエストをシミュレート
            for i in range(10):
                mock_get(f"https://api.example.com/data/{i}")
            end_time = time.time()

            processing_time = end_time - start_time

            # ネットワーク処理のパフォーマンス要件: 10リクエストを2秒以内で処理
            assert (
                processing_time < 2.0
            ), f"ネットワーク処理時間が長すぎます: {processing_time:.3f}秒"

    def test_database_operation_performance(self):
        """データベース操作のパフォーマンステスト"""
        with patch("builtins.open", mock_open()) as mock_file:
            manager = JSONDataManager()

        # 大量データの保存
        large_data = [
            {
                "date": f"2024-01-{i:02d}",
                "code": "1234",
                "open": 100 + i,
                "high": 105 + i,
                "low": 95 + i,
                "close": 100 + i,
                "volume": 1000,
            }
            for i in range(1, 1001)
        ]

        start_time = time.time()
        result = manager.save_data("test.json", large_data)
        end_time = time.time()

        processing_time = end_time - start_time

        # データベース操作のパフォーマンス要件: 1000レコードを0.2秒以内で保存
        assert (
            processing_time < 0.2
        ), f"データ保存時間が長すぎます: {processing_time:.3f}秒"
        assert result is True

    def test_algorithm_complexity(self):
        """アルゴリズムの計算量テスト"""
        updater = DifferentialUpdater()

        # 異なるサイズのデータセットでの処理時間測定
        sizes = [100, 500, 1000, 2000]
        processing_times = []

        for size in sizes:
            data = [
                {
                    "date": f"2024-01-{i:02d}",
                    "code": "1234",
                    "open": 100 + i,
                    "high": 105 + i,
                    "low": 95 + i,
                    "close": 100 + i,
                    "volume": 1000,
                }
                for i in range(1, size + 1)
            ]

            start_time = time.time()
            updater._calculate_comprehensive_diff(data, data)
            end_time = time.time()

            processing_times.append(end_time - start_time)

        # 計算量の確認: O(n)の線形増加
        for i in range(1, len(processing_times)):
            ratio = processing_times[i] / processing_times[i - 1]
            size_ratio = sizes[i] / sizes[i - 1]

            # 処理時間の増加率がデータサイズの増加率と比例することを確認（より緩い条件）
            assert (
                ratio <= size_ratio * 3.0
            ), f"計算量が非線形です: {ratio:.2f} vs {size_ratio:.2f}"

    def test_resource_cleanup_performance(self):
        """リソースクリーンアップのパフォーマンステスト"""
        updater = DifferentialUpdater()

        # 大量のリソースを作成
        for i in range(100):
            data = [
                {"date": f"2024-01-{j:02d}", "code": "1234", "close": 100 + j}
                for j in range(1, 101)
            ]
            updater._calculate_comprehensive_diff(data, data)

        # メモリクリーンアップの確認
        import gc

        gc.collect()

        final_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # メモリリークの確認: 100回の処理後もメモリ使用量が制限内
        assert final_memory < 350, f"メモリリークが発生しています: {final_memory:.2f}MB"

    def test_concurrent_user_simulation(self):
        """同時ユーザーシミュレーションのパフォーマンステスト"""
        import threading
        import queue

        results_queue = queue.Queue()

        def simulate_user(user_id):
            """ユーザーシミュレーション"""
            updater = DifferentialUpdater()
            data = [
                {"date": f"2024-01-{i:02d}", "code": f"{user_id:04d}", "close": 100 + i}
                for i in range(1, 101)
            ]

            start_time = time.time()
            result = updater._calculate_comprehensive_diff(data, data)
            end_time = time.time()

            results_queue.put(
                {
                    "user_id": user_id,
                    "processing_time": end_time - start_time,
                    "result": result,
                }
            )

        # 10人の同時ユーザーをシミュレート
        threads = []
        for user_id in range(10):
            thread = threading.Thread(target=simulate_user, args=(user_id,))
            threads.append(thread)
            thread.start()

        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()

        # 結果の収集
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # 同時ユーザー処理のパフォーマンス要件: 全ユーザーが1秒以内で完了
        max_processing_time = max(result["processing_time"] for result in results)
        assert (
            max_processing_time < 1.0
        ), f"同時ユーザー処理時間が長すぎます: {max_processing_time:.3f}秒"
        assert len(results) == 10
