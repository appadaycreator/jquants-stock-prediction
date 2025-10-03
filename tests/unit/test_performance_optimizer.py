#!/usr/bin/env python3
"""
パフォーマンス最適化システムのテスト
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from core.performance_optimizer import PerformanceOptimizer


class TestPerformanceOptimizer:
    """パフォーマンス最適化システムのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.logger = Mock()
        self.error_handler = Mock()
        self.optimizer = PerformanceOptimizer(self.logger, self.error_handler)

    def test_initialization(self):
        """初期化テスト"""
        assert self.optimizer.logger == self.logger
        assert self.optimizer.error_handler == self.error_handler
        assert self.optimizer.optimization_enabled is True
        assert self.optimizer.monitoring_active is False
        assert len(self.optimizer.metrics_history) == 0

    def test_start_monitoring_success(self):
        """監視開始テスト（成功）"""
        assert self.optimizer.monitoring_active is False

        self.optimizer.start_monitoring(interval=1)

        # 少し待ってから状態を確認
        time.sleep(0.1)
        assert self.optimizer.monitoring_active is True
        assert self.optimizer.monitoring_thread is not None

        # クリーンアップ
        self.optimizer.stop_monitoring()

    def test_start_monitoring_already_active(self):
        """監視開始テスト（既にアクティブ）"""
        self.optimizer.monitoring_active = True

        self.optimizer.start_monitoring()

        # ログが呼ばれることを確認
        self.logger.log_info.assert_called_with(
            "パフォーマンス監視は既に開始されています"
        )

    def test_stop_monitoring(self):
        """監視停止テスト"""
        self.optimizer.monitoring_active = True
        self.optimizer.monitoring_thread = Mock()

        self.optimizer.stop_monitoring()

        assert self.optimizer.monitoring_active is False
        self.logger.log_info.assert_called_with("パフォーマンス監視を停止しました")

    @patch("core.performance_optimizer.psutil")
    def test_collect_system_metrics(self, mock_psutil):
        """システムメトリクス収集テスト"""
        # psutilのモック設定
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = Mock(
            total=8000000000, available=4000000000, percent=50.0
        )
        mock_psutil.disk_usage.return_value = Mock(total=1000000000, used=500000000)
        mock_psutil.Process.return_value.memory_info.return_value = Mock(
            rss=100000000, vms=200000000
        )

        metrics = self.optimizer.collect_system_metrics()

        assert "timestamp" in metrics
        assert "cpu_percent" in metrics
        assert "memory_total" in metrics
        assert "memory_available" in metrics
        assert "memory_percent" in metrics
        assert "disk_total" in metrics
        assert "disk_used" in metrics
        assert "disk_percent" in metrics
        assert "process_memory_rss" in metrics
        assert "process_memory_vms" in metrics

    def test_detect_performance_issues_high_cpu(self):
        """パフォーマンス問題検出テスト（高CPU）"""
        metrics = {"cpu_percent": 95.0, "memory_percent": 50.0, "disk_percent": 50.0}

        # 警告が記録されることを確認
        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)
            mock_warning.assert_called()

    def test_detect_performance_issues_high_memory(self):
        """パフォーマンス問題検出テスト（高メモリ）"""
        metrics = {"cpu_percent": 50.0, "memory_percent": 95.0, "disk_percent": 50.0}

        # 警告が記録されることを確認
        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)
            mock_warning.assert_called()

    def test_detect_performance_issues_high_disk(self):
        """パフォーマンス問題検出テスト（高ディスク）"""
        metrics = {"cpu_percent": 50.0, "memory_percent": 50.0, "disk_percent": 95.0}

        # 警告が記録されることを確認
        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)
            mock_warning.assert_called()

    def test_detect_performance_issues_normal(self):
        """パフォーマンス問題検出テスト（正常）"""
        metrics = {"cpu_percent": 50.0, "memory_percent": 50.0, "disk_percent": 50.0}

        # 警告が記録されないことを確認
        self.optimizer._detect_performance_issues(metrics)
        self.logger.log_warning.assert_not_called()

    def test_optimize_memory_usage(self):
        """メモリ使用量最適化テスト"""
        # メトリクス履歴にデータを追加
        for i in range(5):
            self.optimizer.metrics_history.append(
                {"memory_percent": 80.0 + i, "timestamp": f"2024-01-01T{i:02d}:00:00"}
            )

        with patch("gc.collect") as mock_gc:
            result = self.optimizer.optimize_memory()
            mock_gc.assert_called()
            assert "collected_objects" in result

    def test_get_performance_summary(self):
        """パフォーマンスサマリー取得テスト"""
        # メトリクス履歴にデータを追加
        for i in range(3):
            self.optimizer.metrics_history.append(
                {
                    "cpu_percent": 50.0 + i * 10,
                    "memory_percent": 60.0 + i * 5,
                    "disk_percent": 40.0 + i * 10,
                    "timestamp": f"2024-01-01T{i:02d}:00:00",
                }
            )

        summary = self.optimizer.get_performance_summary()

        assert "average_cpu" in summary
        assert "average_memory" in summary
        assert "average_disk" in summary
        assert "total_metrics" in summary
        assert summary["total_metrics"] == 3

    def test_get_performance_summary_empty(self):
        """パフォーマンスサマリー取得テスト（空データ）"""
        summary = self.optimizer.get_performance_summary()

        assert "average_cpu" in summary
        assert "average_memory" in summary
        assert "average_disk" in summary
        assert "total_metrics" in summary
        assert summary["total_metrics"] == 0

    def test_monitoring_loop_exception_handling(self):
        """監視ループ例外処理テスト"""
        # 監視ループで例外が発生した場合の処理をテスト
        with patch.object(
            self.optimizer,
            "collect_system_metrics",
            side_effect=Exception("Test error"),
        ):
            with patch("time.sleep") as mock_sleep:
                self.optimizer.monitoring_active = True

                # 監視ループを1回だけ実行するようにモック
                def stop_after_one_iteration(*args, **kwargs):
                    self.optimizer.monitoring_active = False

                mock_sleep.side_effect = stop_after_one_iteration

                # 監視ループを実行
                self.optimizer._monitoring_loop(0.01)

                # 例外が適切にハンドリングされることを確認
                # （ログが記録されることを確認）
                self.logger.log_warning.assert_called()

    def test_optimization_enabled_property(self):
        """最適化有効フラグテスト"""
        assert self.optimizer.optimization_enabled is True

        self.optimizer.optimization_enabled = False
        assert self.optimizer.optimization_enabled is False

    def test_metrics_history_limit(self):
        """メトリクス履歴制限テスト"""
        # 大量のメトリクスを追加
        for i in range(1500):  # デフォルトのmaxlen=1000を超える
            self.optimizer.metrics_history.append(
                {"cpu_percent": 50.0, "timestamp": f"2024-01-01T{i:02d}:00:00"}
            )

        # 履歴が制限されていることを確認
        assert len(self.optimizer.metrics_history) == 1000
