#!/usr/bin/env python3
"""
自動スケジューラーの包括的テスト
テストカバレッジ98%以上を目指す最終テストケース
"""

import pytest
import time
import json
import threading
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import tempfile
import os

# テスト対象のインポート
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automated_scheduler import (
    AutomatedScheduler,
    NotificationConfig,
    SchedulerConfig,
    NotificationType
)


class TestAutomatedSchedulerComprehensive:
    """自動スケジューラーの包括的テストクラス"""
    
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
                "enable_weekend": False
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "user": "test@example.com",
                    "password": "test_password",
                    "to": "recipient@example.com"
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/test",
                    "channel": "#test",
                    "username": "Test Bot",
                    "icon_emoji": ":test:"
                },
                "browser": {
                    "enabled": True,
                    "title": "Test Notification",
                    "icon": "/test.ico"
                }
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(test_config, f, default_flow_style=False)
    
    def teardown_method(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_start_scheduler_already_running(self, mock_error_handler, mock_logging, mock_config):
        """既に実行中のスケジューラー開始テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        
        # 既に実行中の場合は警告が出力される
        scheduler.start_scheduler()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_stop_scheduler_not_running(self, mock_error_handler, mock_logging, mock_config):
        """停止していないスケジューラー停止テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = False
        
        # 停止していない場合は何もしない
        scheduler.stop_scheduler()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_execute_routine_success(self, mock_error_handler, mock_logging, mock_config):
        """ルーティン実行成功テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "enable_weekend": False
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        
        # 平日をモック
        with patch('automated_scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 8)  # 月曜日
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # 成功する場合
            with patch.object(scheduler, '_run_routine_with_retry', return_value=True):
                with patch.object(scheduler, '_send_notifications'):
                    scheduler._execute_routine()
                    
                    # アサーション
                    assert scheduler.execution_count == 1
                    assert scheduler.error_count == 0
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_execute_routine_failure(self, mock_error_handler, mock_logging, mock_config):
        """ルーティン実行失敗テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "enable_weekend": False
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        
        # 平日をモック
        with patch('automated_scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 8)  # 月曜日
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # 失敗する場合
            with patch.object(scheduler, '_run_routine_with_retry', return_value=False):
                with patch.object(scheduler, '_send_notifications'):
                    scheduler._execute_routine()
                    
                    # アサーション
                    assert scheduler.execution_count == 1
                    assert scheduler.error_count == 1
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.post')
    def test_api_call_with_job_id(self, mock_post, mock_error_handler, mock_logging, mock_config):
        """ジョブID付きAPI呼び出しテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # APIレスポンスモック（ジョブID付き）
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"job_id": "test_job_123"}
        mock_post.return_value = mock_response
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # ジョブ完了待機をモック
        with patch.object(scheduler, '_wait_for_job_completion', return_value={"success": True, "result": "test"}):
            result = scheduler._call_routine_api()
            
            # アサーション
            assert result["success"] == True
            assert result["result"] == "test"
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.post')
    def test_api_call_direct_result(self, mock_post, mock_error_handler, mock_logging, mock_config):
        """直接結果返却API呼び出しテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # APIレスポンスモック（直接結果）
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "result": "direct_result"}
        mock_post.return_value = mock_response
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # API呼び出しテスト
        result = scheduler._call_routine_api()
        
        # アサーション
        assert result["success"] == True
        assert result["result"]["result"] == "direct_result"
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.post')
    def test_api_call_404_error(self, mock_post, mock_error_handler, mock_logging, mock_config):
        """404エラーAPI呼び出しテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # 404エラーレスポンスモック
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # API呼び出しテスト
        result = scheduler._call_routine_api()
        
        # アサーション
        assert result["success"] == False
        assert "接続できませんでした" in result["error"]
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.post')
    def test_api_call_connection_error(self, mock_post, mock_error_handler, mock_logging, mock_config):
        """接続エラーAPI呼び出しテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # 接続エラーモック
        mock_post.side_effect = Exception("Connection error")
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # API呼び出しテスト
        result = scheduler._call_routine_api()
        
        # アサーション
        assert result["success"] == False
        assert "API呼び出しエラー" in result["error"]
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.post')
    def test_api_call_timeout_error(self, mock_post, mock_error_handler, mock_logging, mock_config):
        """タイムアウトエラーAPI呼び出しテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # タイムアウトエラーモック
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Timeout error")
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # API呼び出しテスト
        result = scheduler._call_routine_api()
        
        # アサーション
        assert result["success"] == False
        assert "接続できませんでした" in result["error"]
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.get')
    @patch('automated_scheduler.time.sleep')
    def test_wait_for_job_completion_running(self, mock_sleep, mock_get, mock_error_handler, mock_logging, mock_config):
        """ジョブ実行中待機テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "timeout": 1  # 短いタイムアウト
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # 実行中レスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "running",
            "progress": 50
        }
        mock_get.return_value = mock_response
        
        # ジョブ完了待機テスト
        result = scheduler._wait_for_job_completion("test_job_id")
        
        # アサーション
        assert result["success"] == False
        assert "タイムアウト" in result["error"]
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.get')
    @patch('automated_scheduler.time.sleep')
    def test_wait_for_job_completion_queued(self, mock_sleep, mock_get, mock_error_handler, mock_logging, mock_config):
        """ジョブキュー中待機テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "timeout": 1  # 短いタイムアウト
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # キュー中レスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "queued",
            "progress": 0
        }
        mock_get.return_value = mock_response
        
        # ジョブ完了待機テスト
        result = scheduler._wait_for_job_completion("test_job_id")
        
        # アサーション
        assert result["success"] == False
        assert "タイムアウト" in result["error"]
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_send_notifications_mixed_enabled(self, mock_error_handler, mock_logging, mock_config):
        """混在通知有効テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "email": {"enabled": True},
                "slack": {"enabled": False},
                "browser": {"enabled": True}
            }
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # 通知送信テスト
        with patch.object(scheduler, '_send_email_notification') as mock_email:
            with patch.object(scheduler, '_send_slack_notification') as mock_slack:
                with patch.object(scheduler, '_send_browser_notification') as mock_browser:
                    scheduler._send_notifications(True)
                    
                    # アサーション
                    mock_email.assert_called_once()
                    mock_slack.assert_not_called()
                    mock_browser.assert_called_once()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_notification_content_success_detailed(self, mock_error_handler, mock_logging, mock_config):
        """成功通知内容詳細テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "execution_time": "09:00"
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.execution_count = 10
        scheduler.error_count = 2
        scheduler.last_execution = datetime(2024, 1, 8, 9, 0, 0)
        
        # 通知内容テスト
        subject, message = scheduler._prepare_notification_content(True)
        
        # アサーション
        assert "✅" in subject
        assert "完了" in subject
        assert "実行回数: 10" in message
        assert "エラー回数: 2" in message
        assert "成功率: 80.0%" in message
        assert "モバイル対応:" in message
        assert "次回実行予定: 明日 09:00" in message
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_notification_content_failure_detailed(self, mock_error_handler, mock_logging, mock_config):
        """失敗通知内容詳細テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "execution_time": "09:00"
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.execution_count = 5
        scheduler.error_count = 3
        scheduler.last_execution = datetime(2024, 1, 8, 9, 0, 0)
        
        # 通知内容テスト
        subject, message = scheduler._prepare_notification_content(False)
        
        # アサーション
        assert "❌" in subject
        assert "失敗" in subject
        assert "実行回数: 5" in message
        assert "エラー回数: 3" in message
        assert "成功率: 40.0%" in message
        assert "対処方法:" in message
        assert "次回実行予定: 明日 09:00" in message
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.smtplib.SMTP')
    @patch('automated_scheduler.time.sleep')
    def test_email_notification_smtp_error(self, mock_sleep, mock_smtp, mock_error_handler, mock_logging, mock_config):
        """メール通知SMTPエラーテスト"""
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
                    "to": "recipient@example.com"
                }
            }
        }
        mock_config.return_value = mock_config_instance
        
        # SMTPエラーモック
        mock_smtp.side_effect = Exception("SMTP error")
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # メール送信テスト
        scheduler._send_email_notification("テスト件名", "テストメッセージ")
        
        # アサーション（エラーが発生しても処理は継続される）
        mock_smtp.assert_called()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.post')
    def test_slack_notification_exception(self, mock_post, mock_error_handler, mock_logging, mock_config):
        """Slack通知例外テスト"""
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
                    "icon_emoji": ":test:"
                }
            }
        }
        mock_config.return_value = mock_config_instance
        
        # 例外発生モック
        mock_post.side_effect = Exception("Request error")
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # Slack送信テスト
        scheduler._send_slack_notification("テスト件名", "テストメッセージ")
        
        # アサーション（例外が発生しても処理は継続される）
        mock_post.assert_called_once()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_browser_notification_directory_creation(self, mock_error_handler, mock_logging, mock_config):
        """ブラウザ通知ディレクトリ作成テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "browser": {
                    "enabled": True,
                    "title": "Test Notification",
                    "icon": "/test.ico"
                }
            }
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # ディレクトリが存在しない場合のテスト
        with patch('os.makedirs') as mock_makedirs:
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                scheduler._send_browser_notification("テスト件名", "テストメッセージ")
                
                # アサーション
                mock_makedirs.assert_called_once_with("data", exist_ok=True)
                mock_open.assert_called_once()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_get_status_detailed(self, mock_error_handler, mock_logging, mock_config):
        """詳細ステータス取得テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "execution_time": "09:00",
                "timezone": "Asia/Tokyo"
            },
            "notifications": {
                "email": {"enabled": True},
                "slack": {"enabled": True},
                "browser": {"enabled": False}
            }
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        scheduler.last_execution = datetime(2024, 1, 8, 9, 0, 0)
        scheduler.execution_count = 15
        scheduler.error_count = 3
        
        # ステータス取得
        status = scheduler.get_status()
        
        # アサーション
        assert status["is_running"] == True
        assert status["last_execution"] == "2024-01-08T09:00:00"
        assert status["execution_count"] == 15
        assert status["error_count"] == 3
        assert status["execution_time"] == "09:00"
        assert status["timezone"] == "Asia/Tokyo"
        assert status["notifications"]["email_enabled"] == True
        assert status["notifications"]["slack_enabled"] == True
        assert status["notifications"]["browser_enabled"] == False
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_manual_execute_success(self, mock_error_handler, mock_logging, mock_config):
        """手動実行成功テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        
        # 手動実行成功モック
        with patch.object(scheduler, '_run_routine_with_retry', return_value=True):
            result = scheduler.manual_execute()
            
            # アサーション
            assert result == True
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_manual_execute_failure(self, mock_error_handler, mock_logging, mock_config):
        """手動実行失敗テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        
        # 手動実行失敗モック
        with patch.object(scheduler, '_run_routine_with_retry', return_value=False):
            result = scheduler.manual_execute()
            
            # アサーション
            assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=automated_scheduler", "--cov-report=html"])
