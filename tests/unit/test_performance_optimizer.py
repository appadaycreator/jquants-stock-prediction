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

    def test_start_monitoring_with_error(self):
        """監視開始エラーハンドリングテスト"""
        # エラーハンドラーなしでテスト
        optimizer = PerformanceOptimizer(self.logger, None)
        
        with patch('threading.Thread') as mock_thread:
            mock_thread.side_effect = Exception("Thread creation failed")
            
            # エラーが発生しても例外が発生しないことを確認
            try:
                optimizer.start_monitoring()
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_stop_monitoring_when_not_active(self):
        """非アクティブ時の監視停止テスト"""
        self.optimizer.monitoring_active = False
        self.optimizer.monitoring_thread = None
        
        # エラーが発生しないことを確認
        self.optimizer.stop_monitoring()

    def test_collect_system_metrics_with_psutil_error(self):
        """psutilエラー時のメトリクス収集テスト"""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.side_effect = Exception("psutil error")
            
            metrics = self.optimizer.collect_system_metrics()
            
            # エラー情報が含まれることを確認
            assert "error" in metrics
            assert "timestamp" in metrics

    def test_detect_performance_issues_high_cpu(self):
        """高CPU使用率の検出テスト"""
        metrics = {
            "cpu_percent": 95.0,
            "memory_percent": 50.0,
            "disk_percent": 30.0
        }
        
        with patch.object(self.optimizer, '_log_performance_warning') as mock_warning:
            self.optimizer._detect_performance_issues(metrics)
            
            # 警告が記録されることを確認
            mock_warning.assert_called_with("high_cpu", 95.0, 90.0)

    def test_detect_performance_issues_high_memory(self):
        """高メモリ使用率の検出テスト"""
        metrics = {
            "cpu_percent": 50.0,
            "memory_percent": 95.0,
            "disk_percent": 30.0
        }
        
        with patch.object(self.optimizer, '_log_performance_warning') as mock_warning:
            self.optimizer._detect_performance_issues(metrics)
            
            # 警告が記録されることを確認
            mock_warning.assert_called_with("high_memory", 95.0, 90.0)

    def test_detect_performance_issues_high_disk(self):
        """高ディスク使用率の検出テスト"""
        metrics = {
            "cpu_percent": 50.0,
            "memory_percent": 50.0,
            "disk_percent": 95.0
        }
        
        with patch.object(self.optimizer, '_log_performance_warning') as mock_warning:
            self.optimizer._detect_performance_issues(metrics)
            
            # 警告が記録されることを確認
            mock_warning.assert_called_with("high_disk", 95.0, 90.0)

    def test_detect_performance_issues_with_exception(self):
        """パフォーマンス問題検出時の例外処理テスト"""
        metrics = {"invalid": "data"}
        
        with patch.object(self.optimizer, '_log_performance_warning') as mock_warning:
            mock_warning.side_effect = Exception("Warning failed")
            
            # 例外が発生しても処理が継続されることを確認
            try:
                self.optimizer._detect_performance_issues(metrics)
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_auto_optimize_memory_issue(self):
        """メモリ問題の自動最適化テスト"""
        issues = ["メモリ使用率が高すぎます: 95.0%"]
        
        with patch('gc.collect') as mock_gc:
            self.optimizer._auto_optimize(issues)
            
            # ガベージコレクションが実行されることを確認
            mock_gc.assert_called_once()

    def test_auto_optimize_cpu_issue(self):
        """CPU問題の自動最適化テスト"""
        issues = ["CPU使用率が高すぎます: 95.0%"]
        
        with patch('psutil.Process') as mock_process:
            mock_process_instance = Mock()
            mock_process.return_value = mock_process_instance
            
            self.optimizer._auto_optimize(issues)
            
            # プロセス優先度調整が試行されることを確認
            mock_process_instance.nice.assert_called_with(10)

    def test_auto_optimize_with_exception(self):
        """自動最適化時の例外処理テスト"""
        issues = ["テスト問題"]
        
        with patch('gc.collect') as mock_gc:
            mock_gc.side_effect = Exception("GC failed")
            
            # 例外が発生しても処理が継続されることを確認
            try:
                self.optimizer._auto_optimize(issues)
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_get_performance_summary_empty_history(self):
        """空の履歴でのパフォーマンスサマリー取得テスト"""
        self.optimizer.metrics_history.clear()
        
        summary = self.optimizer.get_performance_summary()
        
        assert summary["total_metrics"] == 0
        assert summary["average_cpu"] == 0.0
        assert summary["average_memory"] == 0.0

    def test_get_performance_summary_with_data(self):
        """データありでのパフォーマンスサマリー取得テスト"""
        # テストデータを追加
        self.optimizer.metrics_history.extend([
            {"cpu_percent": 50.0, "memory_percent": 60.0, "timestamp": "2024-01-01T00:00:00"},
            {"cpu_percent": 70.0, "memory_percent": 80.0, "timestamp": "2024-01-01T01:00:00"},
        ])
        
        summary = self.optimizer.get_performance_summary()
        
        assert summary["total_metrics"] == 2
        assert summary["average_cpu"] == 60.0
        assert summary["average_memory"] == 70.0

    def test_get_performance_summary_with_exception(self):
        """パフォーマンスサマリー取得時の例外処理テスト"""
        # 無効なデータを含む履歴
        self.optimizer.metrics_history.append({"invalid": "data"})
        
        # 例外が発生しても処理が継続されることを確認
        try:
            summary = self.optimizer.get_performance_summary()
            assert "total_metrics" in summary
        except Exception:
            pytest.fail("Exception should be handled gracefully")

    def test_log_performance_warning(self):
        """パフォーマンス警告ログテスト"""
        with patch.object(self.logger, 'log_warning') as mock_warning:
            self.optimizer._log_performance_warning("test_warning", 85.0, 80.0)
            
            # 警告ログが記録されることを確認
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0][0]
            assert "test_warning" in call_args
            assert "85.0" in call_args
            assert "80.0" in call_args

    def test_log_performance_warning_without_logger(self):
        """ロガーなしでのパフォーマンス警告テスト"""
        optimizer = PerformanceOptimizer(None, None)
        
        # エラーが発生しないことを確認
        try:
            optimizer._log_performance_warning("test_warning", 85.0, 80.0)
        except Exception:
            pytest.fail("Exception should not occur without logger")

    def test_monitoring_loop_with_exception(self):
        """監視ループでの例外処理テスト"""
        with patch.object(self.optimizer, 'collect_system_metrics') as mock_collect:
            mock_collect.side_effect = Exception("Collection failed")
            
            # 監視を開始
            self.optimizer.start_monitoring(interval=0.1)
            time.sleep(0.2)  # 少し待機
            
            # エラーが発生しても監視が継続されることを確認
            assert self.optimizer.monitoring_active is True
            
            # クリーンアップ
            self.optimizer.stop_monitoring()

    def test_optimization_enabled_property(self):
        """最適化有効フラグのテスト"""
        # デフォルト値の確認
        assert self.optimizer.optimization_enabled is True
        
        # 無効化
        self.optimizer.optimization_enabled = False
        assert self.optimizer.optimization_enabled is False
        
        # 有効化
        self.optimizer.optimization_enabled = True
        assert self.optimizer.optimization_enabled is True
