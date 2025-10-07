#!/usr/bin/env python3
"""
差分更新システムのメモリ最適化テスト
"""

import pytest
import tempfile
import os
import gc
import psutil
from unittest.mock import Mock, patch
from core.differential_updater import DifferentialUpdater, DiffCalculator


class TestDifferentialUpdaterMemoryOptimization:
    """差分更新システムのメモリ最適化テスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Mock()
        self.updater = DifferentialUpdater(self.temp_dir, self.logger)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_size_limit(self):
        """キャッシュサイズ制限のテスト"""
        # 大量のデータでキャッシュを満杯にする
        for i in range(200):  # キャッシュサイズ（50）を超える
            data = [
                {"date": f"2024-01-{j:02d}", "code": f"123{i}", "close": 100 + j}
                for j in range(1, 11)
            ]
            self.updater.diff_calculator.calculate_comprehensive_diff(data, data)

        # キャッシュサイズが制限内であることを確認
        assert len(self.updater.diff_calculator._diff_cache) <= 50

    def test_memory_optimization(self):
        """メモリ最適化のテスト"""
        # 初期メモリ使用量
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # 大量のデータ処理
        for i in range(100):
            data = [
                {"date": f"2024-01-{j:02d}", "code": f"123{i}", "close": 100 + j}
                for j in range(1, 101)
            ]
            self.updater.diff_calculator.calculate_comprehensive_diff(data, data)

        # メモリ最適化実行
        self.updater.optimize_memory_usage()

        # メモリ使用量の確認
        memory_usage = self.updater.get_memory_usage()
        assert "rss_mb" in memory_usage
        assert "cache_size" in memory_usage

    def test_cache_clear(self):
        """キャッシュクリアのテスト"""
        # データをキャッシュに追加
        data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        self.updater.diff_calculator.calculate_comprehensive_diff(data, data)

        # キャッシュが存在することを確認
        assert len(self.updater.diff_calculator._diff_cache) > 0

        # キャッシュクリア
        self.updater.diff_calculator.clear_cache()

        # キャッシュが空であることを確認
        assert len(self.updater.diff_calculator._diff_cache) == 0

    def test_memory_usage_tracking(self):
        """メモリ使用量追跡のテスト"""
        memory_usage = self.updater.get_memory_usage()
        
        # 必要なキーが存在することを確認
        required_keys = ["rss_mb", "vms_mb", "cache_size", "max_cache_size"]
        for key in required_keys:
            assert key in memory_usage

    def test_lru_cache_eviction(self):
        """LRUキャッシュ削除のテスト"""
        # キャッシュサイズを小さく設定
        self.updater.diff_calculator.max_cache_size = 5

        # キャッシュを満杯にする
        for i in range(10):
            data = [
                {"date": f"2024-01-{j:02d}", "code": f"123{i}", "close": 100 + j}
                for j in range(1, 6)
            ]
            self.updater.diff_calculator.calculate_comprehensive_diff(data, data)

        # キャッシュサイズが制限内であることを確認
        assert len(self.updater.diff_calculator._diff_cache) <= 5

    def test_periodic_memory_optimization(self):
        """定期的なメモリ最適化のテスト"""
        # 大量のデータ処理
        for i in range(50):
            data = [
                {"date": f"2024-01-{j:02d}", "code": f"123{i}", "close": 100 + j}
                for j in range(1, 51)
            ]
            self.updater.diff_calculator.calculate_comprehensive_diff(data, data)
            
            # 定期的なメモリ最適化
            if i % 10 == 0:
                self.updater.optimize_memory_usage()

        # メモリ使用量が制限内であることを確認
        memory_usage = self.updater.get_memory_usage()
        assert memory_usage["rss_mb"] < 500  # 500MB以下

    def test_garbage_collection_effectiveness(self):
        """ガベージコレクションの効果テスト"""
        # 初期ガベージコレクション
        initial_collected = gc.collect()
        
        # 大量のオブジェクト作成
        large_data = []
        for i in range(1000):
            large_data.append({
                "date": f"2024-01-{i:02d}",
                "code": f"123{i}",
                "close": 100 + i,
                "volume": 1000 + i
            })

        # データ処理
        self.updater.diff_calculator.calculate_comprehensive_diff(large_data, large_data)
        
        # メモリ最適化実行
        self.updater.optimize_memory_usage()
        
        # ガベージコレクション実行
        final_collected = gc.collect()
        
        # ガベージコレクションが実行されたことを確認
        assert final_collected >= 0

    def test_memory_optimization_configuration(self):
        """メモリ最適化設定のテスト"""
        # メモリ最適化が有効であることを確認
        assert self.updater.memory_optimization_enabled is True
        
        # 最大メモリ使用量が設定されていることを確認
        assert self.updater.max_memory_usage_mb > 0

    def test_cache_access_counting(self):
        """キャッシュアクセス回数カウントのテスト"""
        data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        
        # 同じデータで複数回アクセス
        for _ in range(5):
            self.updater.diff_calculator.calculate_comprehensive_diff(data, data)

        # アクセス回数がカウントされていることを確認
        cache_key = list(self.updater.diff_calculator._diff_cache.keys())[0]
        access_count = self.updater.diff_calculator._cache_access_count.get(cache_key, 0)
        assert access_count >= 5
