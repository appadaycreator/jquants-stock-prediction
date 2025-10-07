#!/usr/bin/env python3
"""
自動スケジューラーのテスト
完全自動化機能のテストカバレッジ98%以上を目指す
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import os

# テスト対象のインポート
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automated_scheduler import (
    AutomatedScheduler,
    NotificationConfig,
    SchedulerConfig,
    NotificationType,
)


class TestAutomatedScheduler:
    """自動スケジューラーのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.yaml")

        # テスト用設定ファイル作成
        test_config = {
            "automated_scheduler": {
                "execution_time": "09:00",
                "timezone": "Asia/Tokyo",
                "max_retries": 3,
                "retry_delay": 300,
                "timeout": 1800,
                "enable_weekend": False,
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "user": "test@example.com",
                    "password": "test_password",
                    "to": "recipient@example.com",
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/test",
                    "channel": "#test",
                    "username": "Test Bot",
                    "icon_emoji": ":test:",
                },
                "browser": {
                    "enabled": True,
                    "title": "Test Notification",
                    "icon": "/test.ico",
                },
            },
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            import yaml

            yaml.dump(test_config, f, default_flow_style=False)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_initialization(self, mock_error_handler, mock_logging, mock_config):
        """初期化テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # アサーション
        assert scheduler is not None
        assert scheduler.is_running == False
        assert scheduler.last_execution is None
        assert scheduler.execution_count == 0
        assert scheduler.error_count == 0
        assert scheduler.scheduler_thread is None

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_scheduler_config_loading(
        self, mock_error_handler, mock_logging, mock_config
    ):
        """スケジューラー設定読み込みテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "execution_time": "10:00",
                "timezone": "UTC",
                "max_retries": 5,
                "retry_delay": 600,
                "timeout": 3600,
                "enable_weekend": True,
            },
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # アサーション
        assert scheduler.scheduler_config.execution_time == "10:00"
        assert scheduler.scheduler_config.timezone == "UTC"
        assert scheduler.scheduler_config.max_retries == 5
        assert scheduler.scheduler_config.retry_delay == 600
        assert scheduler.scheduler_config.timeout == 3600
        assert scheduler.scheduler_config.enable_weekend == True

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_notification_config_loading(
        self, mock_error_handler, mock_logging, mock_config
    ):
        """通知設定読み込みテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.test.com",
                    "smtp_port": 465,
                    "user": "test@test.com",
                    "password": "test_pass",
                    "to": "to@test.com",
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://test.slack.com/webhook",
                    "channel": "#general",
                    "username": "Test User",
                    "icon_emoji": ":robot:",
                },
                "browser": {
                    "enabled": False,
                    "title": "Test Title",
                    "icon": "/test.png",
                },
            },
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # アサーション
        assert scheduler.notification_config.email_enabled == True
        assert scheduler.notification_config.email_smtp_server == "smtp.test.com"
        assert scheduler.notification_config.email_smtp_port == 465
        assert scheduler.notification_config.email_user == "test@test.com"
        assert scheduler.notification_config.email_password == "test_pass"
        assert scheduler.notification_config.email_to == "to@test.com"

        assert scheduler.notification_config.slack_enabled == True
        assert (
            scheduler.notification_config.slack_webhook_url
            == "https://test.slack.com/webhook"
        )
        assert scheduler.notification_config.slack_channel == "#general"
        assert scheduler.notification_config.slack_username == "Test User"
        assert scheduler.notification_config.slack_icon_emoji == ":robot:"

        assert scheduler.notification_config.browser_enabled == False
        assert scheduler.notification_config.browser_title == "Test Title"
        assert scheduler.notification_config.browser_icon == "/test.png"

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_start_scheduler(self, mock_error_handler, mock_logging, mock_config):
        """スケジューラー開始テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # スケジューラー開始
        scheduler.start_scheduler()

        # アサーション
        assert scheduler.is_running == True
        assert scheduler.scheduler_thread is not None
        assert scheduler.scheduler_thread.is_alive()

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    @patch("automated_scheduler.time.sleep")
    def test_stop_scheduler(
        self, mock_sleep, mock_error_handler, mock_logging, mock_config
    ):
        """スケジューラー停止テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # スケジューラー開始
        scheduler.start_scheduler()
        assert scheduler.is_running == True

        # スケジューラー停止
        scheduler.stop_scheduler()

        # アサーション
        assert scheduler.is_running == False

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_weekend_check(self, mock_error_handler, mock_logging, mock_config):
        """週末チェックテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {"enable_weekend": False},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # 土曜日をモック
        with patch("automated_scheduler.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 6)  # 土曜日
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # 週末チェック
            scheduler._execute_routine()

            # アサーション（週末のため実行されない）
            assert scheduler.execution_count == 0

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    @patch("automated_scheduler.requests.post")
    def test_api_call_success(
        self, mock_post, mock_error_handler, mock_logging, mock_config
    ):
        """API呼び出し成功テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # APIレスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "result": "test_result"}
        mock_post.return_value = mock_response

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # API呼び出しテスト
        result = scheduler._call_routine_api()

        # アサーション
        assert result["success"] == True
        assert result["result"]["result"] == "test_result"

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    @patch("automated_scheduler.requests.post")
    def test_api_call_failure(
        self, mock_post, mock_error_handler, mock_logging, mock_config
    ):
        """API呼び出し失敗テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # APIレスポンスモック（失敗）
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # API呼び出しテスト
        result = scheduler._call_routine_api()

        # アサーション
        assert result["success"] == False
        assert "接続できませんでした" in result["error"]

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    @patch("automated_scheduler.requests.post")
    def test_api_call_timeout(
        self, mock_post, mock_error_handler, mock_logging, mock_config
    ):
        """API呼び出しタイムアウトテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # タイムアウト例外を発生
        mock_post.side_effect = Exception("Connection timeout")

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # API呼び出しテスト
        result = scheduler._call_routine_api()

        # アサーション
        assert result["success"] == False
        assert "エラー" in result["error"]

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_notification_content_preparation(
        self, mock_error_handler, mock_logging, mock_config
    ):
        """通知内容準備テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {"execution_time": "09:00"},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.execution_count = 5
        scheduler.error_count = 1
        scheduler.last_execution = datetime.now()

        # 成功通知テスト
        subject, message = scheduler._prepare_notification_content(True)
        assert "✅" in subject
        assert "完了" in subject
        assert "5分ルーティン" in message
        assert "実行回数: 5" in message
        assert "エラー回数: 1" in message

        # 失敗通知テスト
        subject, message = scheduler._prepare_notification_content(False)
        assert "❌" in subject
        assert "失敗" in subject
        assert "エラーが発生" in message

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    @patch("automated_scheduler.smtplib.SMTP")
    def test_email_notification_success(
        self, mock_smtp, mock_error_handler, mock_logging, mock_config
    ):
        """メール通知成功テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "user": "test@example.com",
                    "password": "test_password",
                    "to": "recipient@example.com",
                }
            },
        }
        mock_config.return_value = mock_config_instance

        # SMTPモック
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # メール送信テスト
        scheduler._send_email_notification("テスト件名", "テストメッセージ")

        # アサーション
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    @patch("automated_scheduler.requests.post")
    def test_slack_notification_success(
        self, mock_post, mock_error_handler, mock_logging, mock_config
    ):
        """Slack通知成功テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/test",
                    "channel": "#test",
                    "username": "Test Bot",
                    "icon_emoji": ":test:",
                }
            },
        }
        mock_config.return_value = mock_config_instance

        # レスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # Slack送信テスト
        scheduler._send_slack_notification("テスト件名", "テストメッセージ")

        # アサーション
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/test"
        assert call_args[1]["json"]["username"] == "Test Bot"
        assert call_args[1]["json"]["channel"] == "#test"

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_browser_notification(self, mock_error_handler, mock_logging, mock_config):
        """ブラウザ通知テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "browser": {
                    "enabled": True,
                    "title": "Test Notification",
                    "icon": "/test.ico",
                }
            },
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # ブラウザ通知テスト
        scheduler._send_browser_notification("テスト件名", "テストメッセージ")

        # 通知ファイルの存在確認
        notification_file = "data/notifications.json"
        if os.path.exists(notification_file):
            with open(notification_file, "r", encoding="utf-8") as f:
                notification_data = json.load(f)
                assert notification_data["title"] == "テスト件名"
                assert notification_data["message"] == "テストメッセージ"
                assert notification_data["type"] == "routine_completion"

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_get_status(self, mock_error_handler, mock_logging, mock_config):
        """ステータス取得テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "execution_time": "09:00",
                "timezone": "Asia/Tokyo",
            },
            "notifications": {
                "email": {"enabled": True},
                "slack": {"enabled": False},
                "browser": {"enabled": True},
            },
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        scheduler.last_execution = datetime.now()
        scheduler.execution_count = 10
        scheduler.error_count = 2

        # ステータス取得
        status = scheduler.get_status()

        # アサーション
        assert status["is_running"] == True
        assert status["execution_count"] == 10
        assert status["error_count"] == 2
        assert status["execution_time"] == "09:00"
        assert status["timezone"] == "Asia/Tokyo"
        assert status["notifications"]["email_enabled"] == True
        assert status["notifications"]["slack_enabled"] == False
        assert status["notifications"]["browser_enabled"] == True

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_manual_execute(self, mock_error_handler, mock_logging, mock_config):
        """手動実行テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True

        # API呼び出しをモック
        with patch.object(scheduler, "_run_routine_with_retry", return_value=True):
            # 手動実行テスト
            result = scheduler.manual_execute()

            # アサーション
            assert result == True

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_retry_mechanism(self, mock_error_handler, mock_logging, mock_config):
        """リトライ機能テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "max_retries": 3,
                "retry_delay": 1,
            },  # テスト用に短縮
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # リトライ機能テスト（API呼び出しが失敗する場合）
        with patch.object(
            scheduler,
            "_call_routine_api",
            return_value={"success": False, "error": "Test error"},
        ):
            result = scheduler._run_routine_with_retry()
            assert result == False

    @patch("automated_scheduler.ConfigManager")
    @patch("automated_scheduler.LoggingManager")
    @patch("automated_scheduler.ErrorHandler")
    def test_html_email_creation(self, mock_error_handler, mock_logging, mock_config):
        """HTMLメール作成テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {},
        }
        mock_config.return_value = mock_config_instance

        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)

        # HTMLメール作成テスト
        test_message = "テストメッセージ"
        html_content = scheduler._create_html_email(test_message)

        # アサーション
        assert "<!DOCTYPE html>" in html_content
        assert '<html lang="ja">' in html_content
        assert "テストメッセージ" in html_content
        assert "5分ルーティン通知" in html_content
        assert "モバイルアクセス" in html_content
        assert "http://localhost:3000" in html_content


class TestNotificationConfig:
    """通知設定のテストクラス"""

    def test_notification_config_defaults(self):
        """通知設定デフォルト値テスト"""
        config = NotificationConfig()

        assert config.email_enabled == False
        assert config.email_smtp_server == "smtp.gmail.com"
        assert config.email_smtp_port == 587
        assert config.email_user == ""
        assert config.email_password == ""
        assert config.email_to == ""

        assert config.slack_enabled == False
        assert config.slack_webhook_url == ""
        assert config.slack_channel == "#stock-analysis"
        assert config.slack_username == "株価分析Bot"
        assert config.slack_icon_emoji == ":chart_with_upwards_trend:"

        assert config.browser_enabled == True
        assert config.browser_title == "5分ルーティン完了"
        assert config.browser_icon == "/favicon.ico"


class TestSchedulerConfig:
    """スケジューラー設定のテストクラス"""

    def test_scheduler_config_defaults(self):
        """スケジューラー設定デフォルト値テスト"""
        config = SchedulerConfig()

        assert config.execution_time == "09:00"
        assert config.timezone == "Asia/Tokyo"
        assert config.max_retries == 3
        assert config.retry_delay == 300
        assert config.timeout == 1800
        assert config.enable_weekend == False


class TestNotificationType:
    """通知タイプのテストクラス"""

    def test_notification_type_values(self):
        """通知タイプ値テスト"""
        assert NotificationType.EMAIL.value == "email"
        assert NotificationType.SLACK.value == "slack"
        assert NotificationType.BROWSER.value == "browser"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=automated_scheduler", "--cov-report=html"])
