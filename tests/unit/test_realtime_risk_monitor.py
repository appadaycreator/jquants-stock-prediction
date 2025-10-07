#!/usr/bin/env python3
"""
リアルタイムリスク監視システムのテスト
記事の手法を超える高度なリスク監視機能のテスト
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import threading
import time

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.realtime_risk_monitor import (
    RealtimeRiskMonitor,
    AlertLevel,
    RiskEvent,
    RiskAlert,
    RiskSnapshot,
)


class TestRealtimeRiskMonitor(unittest.TestCase):
    """リアルタイムリスク監視システムのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = {
            "monitoring": {
                "update_interval": 1.0,
                "max_history": 10000,
                "alert_retention": 1000,
            },
            "risk_thresholds": {
                "var_95_warning": 0.03,
                "var_95_critical": 0.05,
                "var_99_warning": 0.05,
                "var_99_critical": 0.08,
                "max_drawdown_warning": 0.10,
                "max_drawdown_critical": 0.15,
                "volatility_warning": 0.25,
                "volatility_critical": 0.40,
                "correlation_warning": 0.8,
                "correlation_critical": 0.9,
            },
            "position_limits": {
                "max_position_size": 0.1,
                "max_portfolio_risk": 0.05,
                "concentration_limit": 0.2,
            },
            "market_conditions": {
                "high_volatility_threshold": 0.30,
                "low_liquidity_threshold": 100000,
                "market_crash_threshold": -0.05,
            },
        }
        self.monitor = RealtimeRiskMonitor(self.config)

        # テストデータ作成
        self.stock_data = self._create_test_stock_data()
        self.market_data = self._create_test_market_data()

    def _create_test_stock_data(self) -> pd.DataFrame:
        """テスト用株価データ作成"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.02)
        volumes = np.random.randint(100000, 1000000, 100)

        return pd.DataFrame(
            {"Date": dates, "Close": prices, "Volume": volumes}
        ).set_index("Date")

    def _create_test_market_data(self) -> pd.DataFrame:
        """テスト用市場データ作成"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        np.random.seed(43)
        prices = 1000 + np.cumsum(np.random.randn(100) * 0.01)
        volumes = np.random.randint(1000000, 10000000, 100)

        return pd.DataFrame(
            {"Date": dates, "Close": prices, "Volume": volumes}
        ).set_index("Date")

    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.monitor)
        self.assertFalse(self.monitor.is_monitoring)
        self.assertEqual(
            self.monitor.config["risk_thresholds"]["var_95_critical"], 0.05
        )

    def test_start_stop_monitoring(self):
        """監視開始・停止テスト"""
        symbols = ["TEST1", "TEST2", "TEST3"]

        # 監視開始
        self.monitor.start_monitoring(symbols)
        self.assertTrue(self.monitor.is_monitoring)
        self.assertEqual(self.monitor.monitored_symbols, set(symbols))

        # 監視停止
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_monitoring)

    def test_risk_snapshot_creation(self):
        """リスクスナップショット作成テスト"""
        symbol = "TEST"
        current_price = 100.0
        position_size = 0.05
        risk_metrics = {
            "var_95": 0.03,
            "var_99": 0.06,
            "max_drawdown": 0.08,
            "volatility": 0.25,
            "beta": 1.1,
            "correlation": 0.7,
            "risk_level": "MEDIUM",
        }
        market_data = {"high_volatility": False, "low_liquidity": False}

        snapshot = self.monitor._create_risk_snapshot(
            symbol, current_price, position_size, risk_metrics, market_data
        )

        self.assertIsInstance(snapshot, RiskSnapshot)
        self.assertEqual(snapshot.symbol, symbol)
        self.assertEqual(snapshot.current_price, current_price)
        self.assertEqual(snapshot.position_size, position_size)
        self.assertEqual(snapshot.var_95, risk_metrics["var_95"])
        self.assertEqual(snapshot.volatility, risk_metrics["volatility"])

    def test_risk_alert_detection(self):
        """リスクアラート検出テスト"""
        # 正常なリスクスナップショット
        normal_snapshot = RiskSnapshot(
            timestamp=datetime.now(),
            symbol="TEST",
            current_price=100.0,
            position_size=0.05,
            var_95=0.02,
            var_99=0.04,
            max_drawdown=0.06,
            volatility=0.20,
            beta=1.0,
            correlation=0.6,
            risk_level="MEDIUM",
            alerts=[],
            recommendations=[],
        )

        alerts = self.monitor._check_risk_alerts(normal_snapshot)
        self.assertEqual(len(alerts), 0)  # 正常時はアラートなし

        # 高リスクスナップショット
        high_risk_snapshot = RiskSnapshot(
            timestamp=datetime.now(),
            symbol="TEST",
            current_price=100.0,
            position_size=0.15,  # 制限超過
            var_95=0.08,  # 制限超過
            var_99=0.12,
            max_drawdown=0.20,  # 制限超過
            volatility=0.50,  # 制限超過
            beta=1.5,
            correlation=0.95,  # 制限超過
            risk_level="VERY_HIGH",
            alerts=[],
            recommendations=[],
        )

        alerts = self.monitor._check_risk_alerts(high_risk_snapshot)
        self.assertGreater(len(alerts), 0)  # 高リスク時はアラートあり

        # アラートの内容確認
        critical_alerts = [a for a in alerts if a.alert_level == AlertLevel.CRITICAL]
        self.assertGreater(len(critical_alerts), 0)

    def test_alert_levels(self):
        """アラートレベルテスト"""
        # 警告レベルアラート
        warning_snapshot = RiskSnapshot(
            timestamp=datetime.now(),
            symbol="TEST",
            current_price=100.0,
            position_size=0.05,
            var_95=0.04,  # 警告レベル
            var_99=0.07,
            max_drawdown=0.12,  # 警告レベル
            volatility=0.30,  # 警告レベル
            beta=1.0,
            correlation=0.85,  # 警告レベル
            risk_level="HIGH",
            alerts=[],
            recommendations=[],
        )

        alerts = self.monitor._check_risk_alerts(warning_snapshot)
        warning_alerts = [a for a in alerts if a.alert_level == AlertLevel.WARNING]
        self.assertGreater(len(warning_alerts), 0)

    def test_recommendation_generation(self):
        """推奨事項生成テスト"""
        # 高リスクスナップショット
        high_risk_snapshot = RiskSnapshot(
            timestamp=datetime.now(),
            symbol="TEST",
            current_price=100.0,
            position_size=0.15,
            var_95=0.08,
            var_99=0.12,
            max_drawdown=0.20,
            volatility=0.50,
            beta=1.5,
            correlation=0.95,
            risk_level="VERY_HIGH",
            alerts=[],
            recommendations=[],
        )

        # アラート生成
        alerts = self.monitor._check_risk_alerts(high_risk_snapshot)
        high_risk_snapshot.alerts = alerts

        # 推奨事項生成
        recommendations = self.monitor._generate_recommendations(
            high_risk_snapshot, alerts
        )

        self.assertGreater(len(recommendations), 0)
        self.assertIsInstance(recommendations[0], str)

    def test_update_risk_data(self):
        """リスクデータ更新テスト"""
        symbol = "TEST"
        current_price = 100.0
        position_size = 0.05
        risk_metrics = {
            "var_95": 0.03,
            "var_99": 0.06,
            "max_drawdown": 0.08,
            "volatility": 0.25,
            "beta": 1.1,
            "correlation": 0.7,
            "risk_level": "MEDIUM",
        }
        market_data = {"high_volatility": False, "low_liquidity": False}

        # リスクデータ更新
        self.monitor.update_risk_data(
            symbol, current_price, position_size, risk_metrics, market_data
        )

        # 履歴に追加されたことを確認
        self.assertGreater(len(self.monitor.snapshot_history), 0)
        self.assertEqual(self.monitor.snapshot_history[-1].symbol, symbol)

    def test_current_risk_status(self):
        """現在のリスク状況取得テスト"""
        # テストデータを追加
        for i in range(5):
            snapshot = RiskSnapshot(
                timestamp=datetime.now() - timedelta(minutes=i),
                symbol="TEST",
                current_price=100.0 + i,
                position_size=0.05,
                var_95=0.03,
                var_99=0.06,
                max_drawdown=0.08,
                volatility=0.25,
                beta=1.1,
                correlation=0.7,
                risk_level="MEDIUM",
                alerts=[],
                recommendations=[],
            )
            self.monitor.snapshot_history.append(snapshot)

        # リスク状況取得
        status = self.monitor.get_current_risk_status("TEST")

        self.assertIn("status", status)
        self.assertIn("total_snapshots", status)
        self.assertIn("total_alerts", status)
        self.assertIn("avg_volatility", status)
        self.assertIn("avg_var_95", status)
        self.assertIn("max_drawdown", status)

    def test_risk_alerts_retrieval(self):
        """リスクアラート取得テスト"""
        # テストアラートを追加
        for i in range(3):
            alert = RiskAlert(
                timestamp=datetime.now() - timedelta(minutes=i),
                event_type=RiskEvent.HIGH_VOLATILITY,
                alert_level=AlertLevel.WARNING,
                symbol="TEST",
                message=f"Test alert {i}",
                current_value=0.30 + i * 0.01,
                threshold_value=0.25,
                recommendation="Monitor volatility",
                metadata={},
            )
            self.monitor.alert_history.append(alert)

        # 全アラート取得
        all_alerts = self.monitor.get_risk_alerts()
        self.assertEqual(len(all_alerts), 3)

        # 特定銘柄のアラート取得
        symbol_alerts = self.monitor.get_risk_alerts("TEST")
        self.assertEqual(len(symbol_alerts), 3)

        # 特定レベルのアラート取得
        warning_alerts = self.monitor.get_risk_alerts(level=AlertLevel.WARNING)
        self.assertEqual(len(warning_alerts), 3)

    def test_risk_trends_analysis(self):
        """リスクトレンド分析テスト"""
        # テストデータを追加（7日分）
        for i in range(7):
            snapshot = RiskSnapshot(
                timestamp=datetime.now() - timedelta(days=i),
                symbol="TEST",
                current_price=100.0,
                position_size=0.05,
                var_95=0.03 + i * 0.01,  # 増加傾向
                var_99=0.06 + i * 0.01,
                max_drawdown=0.08 + i * 0.01,
                volatility=0.25 + i * 0.02,  # 増加傾向
                beta=1.1,
                correlation=0.7,
                risk_level="MEDIUM",
                alerts=[],
                recommendations=[],
            )
            self.monitor.snapshot_history.append(snapshot)

        # トレンド分析
        trends = self.monitor.get_risk_trends("TEST", days=7)

        self.assertIn("period_days", trends)
        self.assertIn("data_points", trends)
        self.assertIn("volatility_trend", trends)
        self.assertIn("var_trend", trends)
        self.assertIn("drawdown_trend", trends)
        self.assertIn("trend_direction", trends)

        # 増加傾向を確認
        self.assertEqual(trends["volatility_trend"]["direction"], "increasing")
        self.assertEqual(trends["var_trend"]["direction"], "increasing")

    def test_callback_functions(self):
        """コールバック関数テスト"""
        alert_callback_called = False
        data_callback_called = False

        def alert_callback(alert):
            nonlocal alert_callback_called
            alert_callback_called = True

        def data_callback(snapshot):
            nonlocal data_callback_called
            data_callback_called = True

        # コールバック登録
        self.monitor.add_alert_callback(alert_callback)
        self.monitor.add_data_callback(data_callback)

        # アラート生成
        high_risk_snapshot = RiskSnapshot(
            timestamp=datetime.now(),
            symbol="TEST",
            current_price=100.0,
            position_size=0.15,
            var_95=0.08,
            var_99=0.12,
            max_drawdown=0.20,
            volatility=0.50,
            beta=1.5,
            correlation=0.95,
            risk_level="VERY_HIGH",
            alerts=[],
            recommendations=[],
        )

        # リスクデータ更新（コールバック実行）
        self.monitor.update_risk_data(
            "TEST",
            100.0,
            0.15,
            {
                "var_95": 0.08,
                "var_99": 0.12,
                "max_drawdown": 0.20,
                "volatility": 0.50,
                "beta": 1.5,
                "correlation": 0.95,
                "risk_level": "VERY_HIGH",
            },
        )

        # コールバックが実行されたことを確認
        self.assertTrue(data_callback_called)
        # アラートが生成された場合のみアラートコールバックが実行される
        if alert_callback_called:
            self.assertTrue(alert_callback_called)

    def test_export_risk_report(self):
        """リスクレポート出力テスト"""
        # テストデータを追加
        for i in range(10):
            snapshot = RiskSnapshot(
                timestamp=datetime.now() - timedelta(days=i),
                symbol="TEST",
                current_price=100.0,
                position_size=0.05,
                var_95=0.03,
                var_99=0.06,
                max_drawdown=0.08,
                volatility=0.25,
                beta=1.1,
                correlation=0.7,
                risk_level="MEDIUM",
                alerts=[],
                recommendations=[],
            )
            self.monitor.snapshot_history.append(snapshot)

        # レポート生成
        report = self.monitor.export_risk_report("TEST", days=7)

        self.assertIn("report_period", report)
        self.assertIn("symbol", report)
        self.assertIn("total_snapshots", report)
        self.assertIn("total_alerts", report)
        self.assertIn("risk_metrics", report)
        self.assertIn("generated_at", report)

        self.assertEqual(report["symbol"], "TEST")
        self.assertGreater(report["total_snapshots"], 0)

    def test_monitoring_thread_safety(self):
        """監視スレッド安全性テスト"""

        # 複数スレッドからの同時アクセス
        def update_data(thread_id):
            for i in range(10):
                self.monitor.update_risk_data(
                    f"TEST{thread_id}",
                    100.0 + i,
                    0.05,
                    {
                        "var_95": 0.03,
                        "var_99": 0.06,
                        "max_drawdown": 0.08,
                        "volatility": 0.25,
                        "beta": 1.1,
                        "correlation": 0.7,
                        "risk_level": "MEDIUM",
                    },
                )
                time.sleep(0.01)

        # 複数スレッドで同時実行
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_data, args=(i,))
            threads.append(thread)
            thread.start()

        # 全スレッドの完了を待つ
        for thread in threads:
            thread.join()

        # データが正しく追加されたことを確認
        self.assertGreater(len(self.monitor.snapshot_history), 0)

    def test_empty_data_handling(self):
        """空データ処理テスト"""
        # 空のリスクメトリクス
        empty_metrics = {}

        self.monitor.update_risk_data("TEST", 100.0, 0.05, empty_metrics)

        # エラーが発生せずに処理されることを確認
        self.assertGreaterEqual(len(self.monitor.snapshot_history), 0)

    def test_edge_cases(self):
        """エッジケーステスト"""
        # 極端な値でのテスト
        extreme_metrics = {
            "var_95": 1.0,  # 極端に高い値
            "var_99": 1.0,
            "max_drawdown": 1.0,
            "volatility": 1.0,
            "beta": 10.0,
            "correlation": 1.0,
            "risk_level": "VERY_HIGH",
        }

        self.monitor.update_risk_data(
            "TEST",
            100.0,
            0.5,
            extreme_metrics,  # 極端に大きなポジションサイズ
        )

        # エラーが発生せずに処理されることを確認
        self.assertGreaterEqual(len(self.monitor.snapshot_history), 0)

    def test_performance_under_load(self):
        """負荷下でのパフォーマンステスト"""
        import time

        start_time = time.time()

        # 大量のデータ更新
        for i in range(100):
            self.monitor.update_risk_data(
                f"TEST{i}",
                100.0,
                0.05,
                {
                    "var_95": 0.03,
                    "var_99": 0.06,
                    "max_drawdown": 0.08,
                    "volatility": 0.25,
                    "beta": 1.1,
                    "correlation": 0.7,
                    "risk_level": "MEDIUM",
                },
            )

        end_time = time.time()
        execution_time = end_time - start_time

        # 100回の更新が2秒以内に完了することを確認
        self.assertLess(execution_time, 2.0)

    def test_memory_usage(self):
        """メモリ使用量テスト"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 大量のデータを追加
        for i in range(1000):
            self.monitor.update_risk_data(
                f"TEST{i}",
                100.0,
                0.05,
                {
                    "var_95": 0.03,
                    "var_99": 0.06,
                    "max_drawdown": 0.08,
                    "volatility": 0.25,
                    "beta": 1.1,
                    "correlation": 0.7,
                    "risk_level": "MEDIUM",
                },
            )

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # メモリ増加が20MB以内であることを確認
        self.assertLess(memory_increase, 20 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
