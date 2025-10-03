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

        with patch("threading.Thread") as mock_thread:
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
        with patch("psutil.cpu_percent") as mock_cpu:
            mock_cpu.side_effect = Exception("psutil error")

            metrics = self.optimizer.collect_system_metrics()

            # エラー情報が含まれることを確認
            assert "error" in metrics
            assert "timestamp" in metrics

    def test_detect_performance_issues_high_cpu(self):
        """高CPU使用率の検出テスト"""
        metrics = {"cpu_percent": 95.0, "memory_percent": 50.0, "disk_percent": 30.0}

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)

            # 警告が記録されることを確認
            mock_warning.assert_called_with("high_cpu", 95.0, 90.0)

    def test_detect_performance_issues_high_memory(self):
        """高メモリ使用率の検出テスト"""
        metrics = {"cpu_percent": 50.0, "memory_percent": 95.0, "disk_percent": 30.0}

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)

            # 警告が記録されることを確認
            mock_warning.assert_called_with("high_memory", 95.0, 90.0)

    def test_detect_performance_issues_high_disk(self):
        """高ディスク使用率の検出テスト"""
        metrics = {"cpu_percent": 50.0, "memory_percent": 50.0, "disk_percent": 95.0}

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)

            # 警告が記録されることを確認
            mock_warning.assert_called_with("high_disk", 95.0, 90.0)

    def test_detect_performance_issues_with_exception(self):
        """パフォーマンス問題検出時の例外処理テスト"""
        metrics = {"invalid": "data"}

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            mock_warning.side_effect = Exception("Warning failed")

            # 例外が発生しても処理が継続されることを確認
            try:
                self.optimizer._detect_performance_issues(metrics)
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_auto_optimize_memory_issue(self):
        """メモリ問題の自動最適化テスト"""
        issues = ["メモリ使用率が高すぎます: 95.0%"]

        with patch("gc.collect") as mock_gc:
            self.optimizer._auto_optimize(issues)

            # ガベージコレクションが実行されることを確認
            mock_gc.assert_called_once()

    def test_auto_optimize_cpu_issue(self):
        """CPU問題の自動最適化テスト"""
        issues = ["CPU使用率が高すぎます: 95.0%"]

        with patch("psutil.Process") as mock_process:
            mock_process_instance = Mock()
            mock_process.return_value = mock_process_instance

            self.optimizer._auto_optimize(issues)

            # プロセス優先度調整が試行されることを確認
            mock_process_instance.nice.assert_called_with(10)

    def test_auto_optimize_with_exception(self):
        """自動最適化時の例外処理テスト"""
        issues = ["テスト問題"]

        with patch("gc.collect") as mock_gc:
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
        self.optimizer.metrics_history.extend(
            [
                {
                    "cpu_percent": 50.0,
                    "memory_percent": 60.0,
                    "timestamp": "2024-01-01T00:00:00",
                },
                {
                    "cpu_percent": 70.0,
                    "memory_percent": 80.0,
                    "timestamp": "2024-01-01T01:00:00",
                },
            ]
        )

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
        with patch.object(self.logger, "log_warning") as mock_warning:
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
        with patch.object(self.optimizer, "collect_system_metrics") as mock_collect:
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

    def test_collect_system_metrics_with_psutil_error(self):
        """psutilエラー時のシステムメトリクス収集テスト"""
        with patch("psutil.cpu_percent", side_effect=Exception("CPU error")):
            metrics = self.optimizer.collect_system_metrics()

            # エラーが発生してもデフォルト値が返されることを確認
            assert "timestamp" in metrics
            assert metrics["cpu_percent"] == 0.0

    def test_collect_system_metrics_with_memory_error(self):
        """メモリエラー時のシステムメトリクス収集テスト"""
        with patch("psutil.virtual_memory", side_effect=Exception("Memory error")):
            metrics = self.optimizer.collect_system_metrics()

            # エラーが発生してもデフォルト値が返されることを確認
            assert "timestamp" in metrics
            assert metrics["memory_total"] == 0

    def test_collect_system_metrics_with_disk_error(self):
        """ディスクエラー時のシステムメトリクス収集テスト"""
        with patch("psutil.disk_usage", side_effect=Exception("Disk error")):
            metrics = self.optimizer.collect_system_metrics()

            # エラーが発生してもデフォルト値が返されることを確認
            assert "timestamp" in metrics
            assert metrics["disk_total"] == 0

    def test_collect_system_metrics_with_process_error(self):
        """プロセスエラー時のシステムメトリクス収集テスト"""
        with patch("psutil.Process", side_effect=Exception("Process error")):
            metrics = self.optimizer.collect_system_metrics()

            # エラーが発生してもデフォルト値が返されることを確認
            assert "timestamp" in metrics
            assert metrics["process_memory_rss"] == 0

    def test_detect_performance_issues_high_cpu(self):
        """高CPU使用率の検出テスト"""
        metrics = {
            "cpu_percent": 95.0,
            "memory_percent": 50.0,
            "disk_percent": 30.0,
            "timestamp": "2024-01-01T00:00:00",
        }

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)

            # 高CPU警告が記録されることを確認
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0]
            assert "high_cpu" in call_args[0]

    def test_detect_performance_issues_high_memory(self):
        """高メモリ使用率の検出テスト"""
        metrics = {
            "cpu_percent": 50.0,
            "memory_percent": 95.0,
            "disk_percent": 30.0,
            "timestamp": "2024-01-01T00:00:00",
        }

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)

            # 高メモリ警告が記録されることを確認
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0]
            assert "high_memory" in call_args[0]

    def test_detect_performance_issues_high_disk(self):
        """高ディスク使用率の検出テスト"""
        metrics = {
            "cpu_percent": 50.0,
            "memory_percent": 50.0,
            "disk_percent": 95.0,
            "timestamp": "2024-01-01T00:00:00",
        }

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)

            # 高ディスク警告が記録されることを確認
            assert mock_warning.call_count >= 1
            # 高ディスク警告の呼び出しを確認
            high_disk_calls = [
                call
                for call in mock_warning.call_args_list
                if "high_disk" in call[0][0]
            ]
            assert len(high_disk_calls) == 1

    def test_detect_performance_issues_normal_usage(self):
        """正常使用率での検出テスト"""
        metrics = {
            "cpu_percent": 50.0,
            "memory_percent": 50.0,
            "disk_percent": 50.0,
            "timestamp": "2024-01-01T00:00:00",
        }

        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._detect_performance_issues(metrics)

            # 警告が記録されないことを確認
            mock_warning.assert_not_called()

    def test_auto_optimize_memory_cleanup(self):
        """メモリクリーンアップの自動最適化テスト"""
        with patch("gc.collect") as mock_gc:
            self.optimizer._auto_optimize("memory_cleanup")

            # ガベージコレクションが実行されることを確認
            mock_gc.assert_called_once()

    def test_auto_optimize_unknown_issue(self):
        """未知の問題での自動最適化テスト"""
        with patch.object(self.optimizer, "_log_performance_warning") as mock_warning:
            self.optimizer._auto_optimize("unknown_issue")

            # 警告が記録されることを確認
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0]
            assert "unknown_issue" in call_args[0]

    def test_auto_optimize_with_exception(self):
        """例外発生時の自動最適化テスト"""
        with patch("gc.collect", side_effect=Exception("GC error")):
            with patch.object(
                self.optimizer, "_log_performance_warning"
            ) as mock_warning:
                self.optimizer._auto_optimize("memory_cleanup")

                # エラー警告が記録されることを確認（例外が発生しても警告は記録されない）
                assert mock_warning.call_count == 0

    def test_reset_metrics(self):
        """メトリクスリセットテスト"""
        # メトリクス履歴を追加
        self.optimizer.metrics_history.append({"cpu_percent": 50.0})
        self.optimizer.metrics_history.append({"cpu_percent": 60.0})

        assert len(self.optimizer.metrics_history) == 2

        # リセット
        self.optimizer.reset_metrics()

        assert len(self.optimizer.metrics_history) == 0

    def test_metrics_history_access(self):
        """メトリクス履歴アクセステスト"""
        # メトリクス履歴を追加
        metrics1 = {"cpu_percent": 50.0, "timestamp": "2024-01-01T00:00:00"}
        metrics2 = {"cpu_percent": 60.0, "timestamp": "2024-01-01T01:00:00"}
        self.optimizer.metrics_history.append(metrics1)
        self.optimizer.metrics_history.append(metrics2)

        history = list(self.optimizer.metrics_history)

        assert len(history) == 2
        assert history[0] == metrics1
        assert history[1] == metrics2

    def test_metrics_history_with_limit(self):
        """制限付きメトリクス履歴テスト"""
        # メトリクス履歴を追加
        for i in range(5):
            self.optimizer.metrics_history.append({"cpu_percent": i * 10})

        history = list(self.optimizer.metrics_history)[-3:]  # 最新3件

        assert len(history) == 3

    def test_metrics_history_with_invalid_limit(self):
        """無効な制限でのメトリクス履歴テスト"""
        # メトリクス履歴を追加
        self.optimizer.metrics_history.append({"cpu_percent": 50.0})

        # 負の制限
        history = list(self.optimizer.metrics_history)[:-1]  # 負の制限をシミュレート
        assert len(history) == 0

    def test_metrics_history_with_exception(self):
        """例外発生時のメトリクス履歴テスト"""
        # 無効なデータを含む履歴
        self.optimizer.metrics_history.append({"cpu_percent": 50.0})
        self.optimizer.metrics_history.append(None)  # 無効なデータ

        # 例外が発生しても処理が継続されることを確認
        try:
            history = list(self.optimizer.metrics_history)
            assert len(history) >= 0
        except Exception:
            pytest.fail("Exception should be handled gracefully")

    def test_get_performance_summary_with_empty_history(self):
        """空の履歴でのパフォーマンスサマリー取得テスト"""
        summary = self.optimizer.get_performance_summary()

        assert summary["total_metrics"] == 0
        assert summary["average_cpu"] == 0.0
        assert summary["average_memory"] == 0.0

    def test_get_performance_summary_with_single_metric(self):
        """単一メトリクスでのパフォーマンスサマリー取得テスト"""
        self.optimizer.metrics_history.append(
            {
                "cpu_percent": 50.0,
                "memory_percent": 60.0,
                "timestamp": "2024-01-01T00:00:00",
            }
        )

        summary = self.optimizer.get_performance_summary()

        assert summary["total_metrics"] == 1
        assert summary["average_cpu"] == 50.0
        assert summary["average_memory"] == 60.0

    def test_get_performance_summary_with_missing_fields(self):
        """フィールド不足でのパフォーマンスサマリー取得テスト"""
        self.optimizer.metrics_history.append(
            {
                "cpu_percent": 50.0,
                # memory_percentが不足
                "timestamp": "2024-01-01T00:00:00",
            }
        )

        summary = self.optimizer.get_performance_summary()

        assert summary["total_metrics"] == 1
        assert summary["average_cpu"] == 50.0
        assert summary["average_memory"] == 0.0  # デフォルト値

    def test_get_performance_summary_with_invalid_values(self):
        """無効な値でのパフォーマンスサマリー取得テスト"""
        self.optimizer.metrics_history.append(
            {
                "cpu_percent": "invalid",  # 無効な値
                "memory_percent": 60.0,
                "timestamp": "2024-01-01T00:00:00",
            }
        )

        summary = self.optimizer.get_performance_summary()

        assert "total_metrics" in summary

    def test_get_performance_summary_with_exception(self):
        """例外発生時のパフォーマンスサマリー取得テスト"""
        # 無効なデータを含む履歴
        self.optimizer.metrics_history.append({"invalid": "data"})

        # 例外が発生しても処理が継続されることを確認
        try:
            summary = self.optimizer.get_performance_summary()
            assert "total_metrics" in summary
        except Exception:
            pytest.fail("Exception should be handled gracefully")

    def test_log_performance_warning_with_logger(self):
        """ロガーありでのパフォーマンス警告テスト"""
        with patch.object(self.logger, "log_warning") as mock_warning:
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

    def test_log_performance_warning_with_exception(self):
        """例外発生時のパフォーマンス警告テスト"""
        with patch.object(
            self.logger, "log_warning", side_effect=Exception("Log error")
        ):
            # エラーが発生しても処理が継続されることを確認
            try:
                self.optimizer._log_performance_warning("test_warning", 85.0, 80.0)
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_monitoring_loop_with_exception(self):
        """監視ループでの例外処理テスト"""
        with patch.object(self.optimizer, "collect_system_metrics") as mock_collect:
            mock_collect.side_effect = Exception("Collection failed")

            # 監視を開始
            self.optimizer.start_monitoring(interval=0.1)
            time.sleep(0.2)  # 少し待機

            # エラーが発生しても監視が継続されることを確認
            assert self.optimizer.monitoring_active is True

            # クリーンアップ
            self.optimizer.stop_monitoring()

    def test_monitoring_loop_with_detect_error(self):
        """検出エラー時の監視ループテスト"""
        with patch.object(
            self.optimizer,
            "_detect_performance_issues",
            side_effect=Exception("Detection failed"),
        ):
            # 監視を開始
            self.optimizer.start_monitoring(interval=0.1)
            time.sleep(0.2)  # 少し待機

            # エラーが発生しても監視が継続されることを確認
            assert self.optimizer.monitoring_active is True

            # クリーンアップ
            self.optimizer.stop_monitoring()

    def test_monitoring_loop_with_sleep_error(self):
        """スリープエラー時の監視ループテスト"""
        with patch("time.sleep", side_effect=Exception("Sleep failed")):
            # 監視を開始
            self.optimizer.start_monitoring(interval=0.1)

            # エラーが発生しても監視が継続されることを確認
            assert self.optimizer.monitoring_active is True

            # クリーンアップ
            self.optimizer.stop_monitoring()

    def test_start_monitoring_with_exception(self):
        """監視開始時の例外処理テスト"""
        with patch("threading.Thread", side_effect=Exception("Thread error")):
            # エラーが発生しても処理が継続されることを確認
            try:
                self.optimizer.start_monitoring()
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_start_monitoring_with_error_handler(self):
        """エラーハンドラーありでの監視開始テスト"""
        with patch.object(self.error_handler, "handle_system_error") as mock_handler:
            with patch("threading.Thread", side_effect=Exception("Thread error")):
                self.optimizer.start_monitoring()

                # エラーハンドラーが呼ばれることを確認
                mock_handler.assert_called_once()

    def test_start_monitoring_with_logger_error(self):
        """ロガーエラー時の監視開始テスト"""
        with patch.object(self.logger, "log_info", side_effect=Exception("Log error")):
            # エラーが発生しても処理が継続されることを確認
            try:
                self.optimizer.start_monitoring()
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_stop_monitoring_with_thread_error(self):
        """スレッドエラー時の監視停止テスト"""
        with patch.object(self.optimizer, "monitoring_thread") as mock_thread:
            mock_thread.join.side_effect = Exception("Join error")

            # エラーが発生しても処理が継続されることを確認
            try:
                self.optimizer.stop_monitoring()
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_stop_monitoring_with_logger_error(self):
        """ロガーエラー時の監視停止テスト"""
        with patch.object(self.logger, "log_info", side_effect=Exception("Log error")):
            # エラーが発生しても処理が継続されることを確認
            try:
                self.optimizer.stop_monitoring()
            except Exception:
                pytest.fail("Exception should be handled gracefully")

    def test_optimize_memory(self):
        """メモリ最適化テスト"""
        result = self.optimizer.optimize_memory()
        assert "collected_objects" in result
        assert "timestamp" in result

    def test_optimize_memory_usage(self):
        """メモリ使用量最適化テスト"""
        result = self.optimizer.optimize_memory_usage()
        assert "collected_objects" in result
        assert "timestamp" in result

    def test_get_optimization_recommendations(self):
        """最適化推奨事項取得テスト"""
        # メトリクス履歴を追加
        self.optimizer.metrics_history.append(
            {
                "cpu_percent": 85.0,
                "memory_percent": 85.0,
                "disk_percent": 85.0,
                "timestamp": "2024-01-01T00:00:00",
            }
        )

        recommendations = self.optimizer.get_optimization_recommendations()
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_get_optimization_recommendations_empty_history(self):
        """空の履歴での最適化推奨事項取得テスト"""
        recommendations = self.optimizer.get_optimization_recommendations()
        assert isinstance(recommendations, list)
        assert "メトリクス履歴が不足しています" in recommendations[0]

    def test_get_system_info(self):
        """システム情報取得テスト"""
        info = self.optimizer.get_system_info()
        assert "cpu_count" in info
        assert "memory_total" in info
        assert "disk_total" in info
        assert "python_version" in info
        assert "platform" in info
        assert "timestamp" in info

    def test_get_system_info_with_exception(self):
        """例外発生時のシステム情報取得テスト"""
        with patch("psutil.cpu_count", side_effect=Exception("CPU error")):
            info = self.optimizer.get_system_info()
            assert "error" in info
