#!/usr/bin/env python3
"""
強化されたアラートシステムのテスト
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_alert_system import (
    EnhancedAlertSystem,
    AlertLevel,
    AlertType,
    NotificationChannel,
    EmailNotifier,
    SlackNotifier,
    WebNotifier,
)


class TestEmailNotifier(unittest.TestCase):
    """メール通知器のテスト"""

    def setUp(self):
        """テスト前準備"""
        self.notifier = EmailNotifier(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="test_password",
        )

    @patch("smtplib.SMTP")
    def test_send_alert(self, mock_smtp):
        """アラート送信テスト"""
        # モック設定
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        # アラート作成
        alert = Mock()
        alert.alert_level = AlertLevel.CRITICAL
        alert.title = "テストアラート"
        alert.symbol = "TEST"
        alert.alert_type = AlertType.STOP_LOSS
        alert.current_value = 100.0
        alert.threshold_value = 95.0
        alert.timestamp = datetime.now()
        alert.message = "テストメッセージ"
        alert.recommendation = "テスト推奨事項"
        alert.metadata = {"test": "data"}

        # 送信テスト
        result = self.notifier.send_alert(alert, "recipient@example.com")

        self.assertTrue(result)
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()


class TestSlackNotifier(unittest.TestCase):
    """Slack通知器のテスト"""

    def setUp(self):
        """テスト前準備"""
        self.notifier = SlackNotifier("https://hooks.slack.com/test")

    @patch("requests.post")
    def test_send_alert(self, mock_post):
        """アラート送信テスト"""
        # モック設定
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # アラート作成
        alert = Mock()
        alert.alert_level = AlertLevel.WARNING
        alert.title = "テストアラート"
        alert.symbol = "TEST"
        alert.alert_type = AlertType.VOLATILITY_SPIKE
        alert.current_value = 100.0
        alert.threshold_value = 95.0
        alert.timestamp = datetime.now()
        alert.message = "テストメッセージ"
        alert.recommendation = "テスト推奨事項"
        alert.metadata = {"test": "data"}

        # 送信テスト
        result = self.notifier.send_alert(alert)

        self.assertTrue(result)
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()


class TestWebNotifier(unittest.TestCase):
    """Web通知器のテスト"""

    def setUp(self):
        """テスト前準備"""
        self.notifier = WebNotifier("https://api.example.com/webhook")

    @patch("requests.post")
    def test_send_alert(self, mock_post):
        """アラート送信テスト"""
        # モック設定
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # アラート作成
        alert = Mock()
        alert.id = "test_alert_123"
        alert.timestamp = datetime.now()
        alert.symbol = "TEST"
        alert.alert_type = AlertType.PRICE_MOVEMENT
        alert.alert_level = AlertLevel.INFO
        alert.title = "テストアラート"
        alert.message = "テストメッセージ"
        alert.current_value = 100.0
        alert.threshold_value = 95.0
        alert.recommendation = "テスト推奨事項"
        alert.metadata = {"test": "data"}

        # 送信テスト
        result = self.notifier.send_alert(alert)

        self.assertTrue(result)
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()


class TestEnhancedAlertSystem(unittest.TestCase):
    """強化されたアラートシステムのテスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "alert_processing": {
                "max_active_alerts": 1000,
                "max_alert_history": 10000,
                "alert_retention_days": 30,
                "processing_interval": 1.0,
            },
            "notification": {
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "test@example.com",
                    "password": "test_password",
                },
                "slack": {"webhook_url": "https://hooks.slack.com/test"},
                "web": {"webhook_url": "https://api.example.com/webhook"},
            },
            "alert_frequency": {
                "max_alerts_per_hour": 100,
                "max_alerts_per_day": 1000,
                "quiet_hours": [22, 6],
            },
        }
        self.system = EnhancedAlertSystem(self.config)

    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.system)
        self.assertFalse(self.system.is_processing)
        self.assertEqual(len(self.system.alert_rules), 0)
        self.assertEqual(len(self.system.active_alerts), 0)

    def test_create_alert_rule(self):
        """アラートルール作成テスト"""
        result = self.system.create_alert_rule(
            rule_id="test_rule_1",
            name="テストルール",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            conditions={"price_threshold": 95.0},
            notification_channels=[
                NotificationChannel.EMAIL,
                NotificationChannel.SLACK,
            ],
            enabled=True,
        )

        self.assertTrue(result)
        self.assertIn("test_rule_1", self.system.alert_rules)

    def test_create_alert(self):
        """アラート作成テスト"""
        alert_id = self.system.create_alert(
            symbol="TEST",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            title="テストアラート",
            message="損切り条件が達成されました",
            current_value=95.0,
            threshold_value=100.0,
            recommendation="損切り執行を推奨します",
            metadata={"test": "data"},
        )

        self.assertIsNotNone(alert_id)
        self.assertIn(alert_id, self.system.active_alerts)
        self.assertEqual(len(self.system.alert_history), 1)

    def test_acknowledge_alert(self):
        """アラート確認テスト"""
        # アラート作成
        alert_id = self.system.create_alert(
            symbol="TEST",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            title="テストアラート",
            message="損切り条件が達成されました",
            current_value=95.0,
            threshold_value=100.0,
            recommendation="損切り執行を推奨します",
        )

        # アラート確認
        result = self.system.acknowledge_alert(alert_id)

        self.assertTrue(result)
        self.assertTrue(self.system.active_alerts[alert_id].acknowledged)
        self.assertIsNotNone(self.system.active_alerts[alert_id].acknowledged_at)

    def test_get_alert_status(self):
        """アラート状況取得テスト"""
        # アラート作成
        self.system.create_alert(
            symbol="TEST",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            title="テストアラート",
            message="損切り条件が達成されました",
            current_value=95.0,
            threshold_value=100.0,
            recommendation="損切り執行を推奨します",
        )

        status = self.system.get_alert_status()

        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("active_alerts", status)
        self.assertIn("unacknowledged_alerts", status)
        self.assertIn("level_counts", status)

    def test_get_alert_history(self):
        """アラート履歴取得テスト"""
        # アラート作成
        self.system.create_alert(
            symbol="TEST",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            title="テストアラート",
            message="損切り条件が達成されました",
            current_value=95.0,
            threshold_value=100.0,
            recommendation="損切り執行を推奨します",
        )

        history = self.system.get_alert_history(symbol="TEST", days=7)

        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["symbol"], "TEST")
        self.assertEqual(history[0]["alert_type"], "stop_loss")
        self.assertEqual(history[0]["alert_level"], "critical")

    def test_export_alert_report(self):
        """アラートレポート出力テスト"""
        # アラート作成
        self.system.create_alert(
            symbol="TEST",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            title="テストアラート",
            message="損切り条件が達成されました",
            current_value=95.0,
            threshold_value=100.0,
            recommendation="損切り執行を推奨します",
        )

        report = self.system.export_alert_report(symbol="TEST", days=7)

        self.assertIsInstance(report, dict)
        self.assertIn("report_period", report)
        self.assertIn("symbol", report)
        self.assertIn("total_alerts", report)
        self.assertIn("alert_counts", report)
        self.assertIn("level_counts", report)
        self.assertEqual(report["total_alerts"], 1)


class TestIntegration(unittest.TestCase):
    """統合テスト"""

    def setUp(self):
        """テスト前準備"""
        self.system = EnhancedAlertSystem()

    def test_full_alert_workflow(self):
        """完全アラートワークフローテスト"""
        # 1. アラートルール作成
        rule_result = self.system.create_alert_rule(
            rule_id="test_rule_1",
            name="テストルール",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            conditions={"price_threshold": 95.0},
            notification_channels=[NotificationChannel.EMAIL],
            enabled=True,
        )

        self.assertTrue(rule_result)

        # 2. アラート作成
        alert_id = self.system.create_alert(
            symbol="TEST",
            alert_type=AlertType.STOP_LOSS,
            alert_level=AlertLevel.CRITICAL,
            title="テストアラート",
            message="損切り条件が達成されました",
            current_value=95.0,
            threshold_value=100.0,
            recommendation="損切り執行を推奨します",
        )

        self.assertIsNotNone(alert_id)

        # 3. アラート確認
        ack_result = self.system.acknowledge_alert(alert_id)
        self.assertTrue(ack_result)

        # 4. 状況確認
        status = self.system.get_alert_status()
        self.assertIsInstance(status, dict)

        # 5. 履歴確認
        history = self.system.get_alert_history()
        self.assertIsInstance(history, list)

        # 6. レポート出力
        report = self.system.export_alert_report()
        self.assertIsInstance(report, dict)


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
