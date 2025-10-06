#!/usr/bin/env python3
"""
自動スケジューラーの拡張テスト
テストカバレッジ98%以上を目指す追加テストケース
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


class TestAutomatedSchedulerExtended:
    """自動スケジューラーの拡張テストクラス"""
    
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
    def test_scheduler_loop_exception_handling(self, mock_error_handler, mock_logging, mock_config):
        """スケジューラーループ例外処理テスト"""
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
        
        # スケジューラーループで例外が発生する場合のテスト
        with patch('automated_scheduler.schedule.run_pending', side_effect=Exception("Test exception")):
            with patch('automated_scheduler.time.sleep') as mock_sleep:
                # ループを1回だけ実行するように制御
                call_count = 0
                
                def mock_sleep_side_effect(duration):
                    nonlocal call_count
                    call_count += 1
                    if call_count >= 1:
                        scheduler.is_running = False  # ループを終了
                    # 実際のsleepは呼ばない
                
                mock_sleep.side_effect = mock_sleep_side_effect
                
                # スケジューラーループ実行
                scheduler._scheduler_loop()
                
                # 例外が発生してもsleepが呼ばれることを確認
                assert call_count > 0
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_execute_routine_weekend_enabled(self, mock_error_handler, mock_logging, mock_config):
        """週末実行有効時のテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "enable_weekend": True
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        
        # 土曜日をモック
        with patch('automated_scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 6)  # 土曜日
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # 週末でも実行される
            with patch.object(scheduler, '_run_routine_with_retry', return_value=True):
                with patch.object(scheduler, '_send_notifications'):
                    scheduler._execute_routine()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_execute_routine_not_running(self, mock_error_handler, mock_logging, mock_config):
        """スケジューラー停止時のテスト"""
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
        
        # 停止中は実行されない
        scheduler._execute_routine()
        assert scheduler.execution_count == 0
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_execute_routine_stop_event_set(self, mock_error_handler, mock_logging, mock_config):
        """停止イベント設定時のテスト"""
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
        scheduler.stop_event.set()  # 停止イベント設定
        
        # 停止イベントが設定されている場合は実行されない
        scheduler._execute_routine()
        assert scheduler.execution_count == 0
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_run_routine_with_retry_success(self, mock_error_handler, mock_logging, mock_config):
        """リトライ機能成功テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "max_retries": 3,
                "retry_delay": 1  # テスト用に短縮
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # 1回目で成功する場合
        with patch.object(scheduler, '_call_routine_api', return_value={"success": True, "result": "test"}):
            result = scheduler._run_routine_with_retry()
            assert result == True
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_run_routine_with_retry_all_failures(self, mock_error_handler, mock_logging, mock_config):
        """リトライ機能全失敗テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "max_retries": 2,
                "retry_delay": 1  # テスト用に短縮
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # 全て失敗する場合
        with patch.object(scheduler, '_call_routine_api', return_value={"success": False, "error": "test error"}):
            result = scheduler._run_routine_with_retry()
            assert result == False
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_run_routine_with_retry_exception(self, mock_error_handler, mock_logging, mock_config):
        """リトライ機能例外テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "max_retries": 2,
                "retry_delay": 1  # テスト用に短縮
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # 例外が発生する場合
        with patch.object(scheduler, '_call_routine_api', side_effect=Exception("Test exception")):
            result = scheduler._run_routine_with_retry()
            assert result == False
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.get')
    def test_wait_for_job_completion_success(self, mock_get, mock_error_handler, mock_logging, mock_config):
        """ジョブ完了待機成功テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "timeout": 60
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # ジョブ完了レスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "succeeded",
            "resultUrl": "http://example.com/result",
            "progress": 100
        }
        mock_get.return_value = mock_response
        
        # ジョブ完了待機テスト
        result = scheduler._wait_for_job_completion("test_job_id")
        
        # アサーション
        assert result["success"] == True
        assert result["job_id"] == "test_job_id"
        assert result["result_url"] == "http://example.com/result"
        assert result["progress"] == 100
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.get')
    def test_wait_for_job_completion_failed(self, mock_get, mock_error_handler, mock_logging, mock_config):
        """ジョブ完了待機失敗テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "timeout": 60
            },
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # ジョブ失敗レスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "failed",
            "error": "Job failed"
        }
        mock_get.return_value = mock_response
        
        # ジョブ完了待機テスト
        result = scheduler._wait_for_job_completion("test_job_id")
        
        # アサーション
        assert result["success"] == False
        assert result["error"] == "Job failed"
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.get')
    @patch('automated_scheduler.time.sleep')
    def test_wait_for_job_completion_timeout(self, mock_sleep, mock_get, mock_error_handler, mock_logging, mock_config):
        """ジョブ完了待機タイムアウトテスト"""
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
    def test_wait_for_job_completion_http_error(self, mock_sleep, mock_get, mock_error_handler, mock_logging, mock_config):
        """ジョブ完了待機HTTPエラーテスト"""
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
        
        # HTTPエラーレスポンスモック
        mock_response = Mock()
        mock_response.status_code = 500
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
    def test_wait_for_job_completion_exception(self, mock_sleep, mock_get, mock_error_handler, mock_logging, mock_config):
        """ジョブ完了待機例外テスト"""
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
        
        # 例外発生モック
        mock_get.side_effect = Exception("Connection error")
        
        # ジョブ完了待機テスト
        result = scheduler._wait_for_job_completion("test_job_id")
        
        # アサーション
        assert result["success"] == False
        assert "タイムアウト" in result["error"]
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_send_notifications_all_enabled(self, mock_error_handler, mock_logging, mock_config):
        """全通知有効時のテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "email": {"enabled": True},
                "slack": {"enabled": True},
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
                    mock_slack.assert_called_once()
                    mock_browser.assert_called_once()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_send_notifications_all_disabled(self, mock_error_handler, mock_logging, mock_config):
        """全通知無効時のテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "email": {"enabled": False},
                "slack": {"enabled": False},
                "browser": {"enabled": False}
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
                    
                    # アサーション（呼ばれない）
                    mock_email.assert_not_called()
                    mock_slack.assert_not_called()
                    mock_browser.assert_not_called()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_send_notifications_exception(self, mock_error_handler, mock_logging, mock_config):
        """通知送信例外テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "email": {"enabled": True},
                "slack": {"enabled": False},
                "browser": {"enabled": False}
            }
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # 通知送信で例外が発生する場合
        with patch.object(scheduler, '_send_email_notification', side_effect=Exception("Email error")):
            # 例外が発生しても処理は継続される
            scheduler._send_notifications(True)
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_notification_content_with_no_last_execution(self, mock_error_handler, mock_logging, mock_config):
        """前回実行なし時の通知内容テスト"""
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
        scheduler.execution_count = 0
        scheduler.error_count = 0
        scheduler.last_execution = None  # 前回実行なし
        
        # 通知内容テスト
        subject, message = scheduler._prepare_notification_content(True)
        assert "未実行" in message
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.smtplib.SMTP')
    @patch('automated_scheduler.time.sleep')
    def test_email_notification_retry_success(self, mock_sleep, mock_smtp, mock_error_handler, mock_logging, mock_config):
        """メール通知リトライ成功テスト"""
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
        
        # SMTPモック（1回目失敗、2回目成功）
        mock_server = Mock()
        mock_smtp.side_effect = [Exception("First attempt failed"), mock_server]
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # メール送信テスト
        scheduler._send_email_notification("テスト件名", "テストメッセージ")
        
        # アサーション（2回呼ばれる）
        assert mock_smtp.call_count == 2
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.smtplib.SMTP')
    @patch('automated_scheduler.time.sleep')
    def test_email_notification_retry_all_failures(self, mock_sleep, mock_smtp, mock_error_handler, mock_logging, mock_config):
        """メール通知リトライ全失敗テスト"""
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
        
        # SMTPモック（全て失敗）
        mock_smtp.side_effect = Exception("All attempts failed")
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # メール送信テスト
        scheduler._send_email_notification("テスト件名", "テストメッセージ")
        
        # アサーション（3回呼ばれる）
        assert mock_smtp.call_count == 3
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_email_notification_incomplete_config(self, mock_error_handler, mock_logging, mock_config):
        """メール通知設定不完全テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "email": {
                    "enabled": True,
                    "user": "",  # 空のユーザー
                    "to": ""     # 空の宛先
                }
            }
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # メール送信テスト（設定不完全のため送信されない）
        scheduler._send_email_notification("テスト件名", "テストメッセージ")
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    @patch('automated_scheduler.requests.post')
    def test_slack_notification_http_error(self, mock_post, mock_error_handler, mock_logging, mock_config):
        """Slack通知HTTPエラーテスト"""
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
        
        # HTTPエラーレスポンスモック
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # Slack送信テスト
        scheduler._send_slack_notification("テスト件名", "テストメッセージ")
        
        # アサーション
        mock_post.assert_called_once()
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_slack_notification_no_webhook(self, mock_error_handler, mock_logging, mock_config):
        """Slack通知Webhook URLなしテスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {
                "slack": {
                    "enabled": True,
                    "webhook_url": "",  # 空のWebhook URL
                    "channel": "#test",
                    "username": "Test Bot",
                    "icon_emoji": ":test:"
                }
            }
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        
        # Slack送信テスト（Webhook URLなしのため送信されない）
        scheduler._send_slack_notification("テスト件名", "テストメッセージ")
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_browser_notification_file_error(self, mock_error_handler, mock_logging, mock_config):
        """ブラウザ通知ファイルエラーテスト"""
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
        
        # ファイル書き込みで例外が発生する場合
        with patch('builtins.open', side_effect=Exception("File write error")):
            scheduler._send_browser_notification("テスト件名", "テストメッセージ")
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_get_status_with_none_last_execution(self, mock_error_handler, mock_logging, mock_config):
        """前回実行なし時のステータス取得テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {
                "execution_time": "09:00",
                "timezone": "Asia/Tokyo"
            },
            "notifications": {
                "email": {"enabled": True},
                "slack": {"enabled": False},
                "browser": {"enabled": True}
            }
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = True
        scheduler.last_execution = None  # 前回実行なし
        scheduler.execution_count = 5
        scheduler.error_count = 1
        
        # ステータス取得
        status = scheduler.get_status()
        
        # アサーション
        assert status["is_running"] == True
        assert status["last_execution"] is None
        assert status["execution_count"] == 5
        assert status["error_count"] == 1
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_manual_execute_not_running(self, mock_error_handler, mock_logging, mock_config):
        """スケジューラー停止時の手動実行テスト"""
        # モック設定
        mock_config_instance = Mock()
        mock_config_instance.get_config.return_value = {
            "automated_scheduler": {},
            "notifications": {}
        }
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化
        scheduler = AutomatedScheduler(self.config_path)
        scheduler.is_running = False  # 停止中
        
        # 手動実行テスト
        result = scheduler.manual_execute()
        
        # アサーション（停止中は実行されない）
        assert result == False
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_config_loading_exception(self, mock_error_handler, mock_logging, mock_config):
        """設定読み込み例外テスト"""
        # モック設定（例外発生）
        mock_config_instance = Mock()
        mock_config_instance.get_config.side_effect = Exception("Config error")
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化（例外が発生しても初期化される）
        scheduler = AutomatedScheduler(self.config_path)
        
        # デフォルト値が使用される
        assert scheduler.scheduler_config.execution_time == "09:00"
        assert scheduler.scheduler_config.timezone == "Asia/Tokyo"
    
    @patch('automated_scheduler.ConfigManager')
    @patch('automated_scheduler.LoggingManager')
    @patch('automated_scheduler.ErrorHandler')
    def test_notification_config_loading_exception(self, mock_error_handler, mock_logging, mock_config):
        """通知設定読み込み例外テスト"""
        # モック設定（例外発生）
        mock_config_instance = Mock()
        mock_config_instance.get_config.side_effect = Exception("Config error")
        mock_config.return_value = mock_config_instance
        
        # スケジューラー初期化（例外が発生しても初期化される）
        scheduler = AutomatedScheduler(self.config_path)
        
        # デフォルト値が使用される
        assert scheduler.notification_config.email_enabled == False
        assert scheduler.notification_config.slack_enabled == False
        assert scheduler.notification_config.browser_enabled == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=automated_scheduler", "--cov-report=html"])
