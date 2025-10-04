#!/usr/bin/env python3
"""
1日5分ルーティン完全自動化スケジューラー

機能:
- 朝9:00に自動実行
- 結果をメール/Slack/ブラウザ通知で即座に通知
- モバイル最適化されたUI対応
- エラーハンドリングとリトライ機能
- ログ記録と監視機能
"""

import os
import sys
import time
import json
import logging
import schedule
import threading
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from enum import Enum

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logging_manager import LoggingManager
from core.error_handler import ErrorHandler
from core.config_manager import ConfigManager


class NotificationType(Enum):
    """通知タイプ"""
    EMAIL = "email"
    SLACK = "slack"
    BROWSER = "browser"


@dataclass
class NotificationConfig:
    """通知設定"""
    email_enabled: bool = False
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_to: str = ""
    
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    slack_channel: str = "#stock-analysis"
    slack_username: str = "株価分析Bot"
    slack_icon_emoji: str = ":chart_with_upwards_trend:"
    
    browser_enabled: bool = True
    browser_title: str = "5分ルーティン完了"
    browser_icon: str = "/favicon.ico"


@dataclass
class SchedulerConfig:
    """スケジューラー設定"""
    execution_time: str = "09:00"  # 実行時間
    timezone: str = "Asia/Tokyo"   # タイムゾーン
    max_retries: int = 3           # 最大リトライ回数
    retry_delay: int = 300         # リトライ間隔（秒）
    timeout: int = 1800            # タイムアウト（秒）
    enable_weekend: bool = False   # 週末実行の有無


class AutomatedScheduler:
    """完全自動化スケジューラー"""
    
    def __init__(self, config_path: str = "config_final.yaml"):
        """初期化"""
        self.config_manager = ConfigManager(config_path)
        self.logging_manager = LoggingManager()
        self.error_handler = ErrorHandler()
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 設定読み込み
        self.scheduler_config = self._load_scheduler_config()
        self.notification_config = self._load_notification_config()
        
        # 実行状態管理
        self.is_running = False
        self.last_execution = None
        self.execution_count = 0
        self.error_count = 0
        
        # スレッド管理
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
        self.logger.info("自動スケジューラーが初期化されました")
    
    def _load_scheduler_config(self) -> SchedulerConfig:
        """スケジューラー設定の読み込み"""
        try:
            config_data = self.config_manager.get_config()
            scheduler_data = config_data.get("automated_scheduler", {})
            
            return SchedulerConfig(
                execution_time=scheduler_data.get("execution_time", "09:00"),
                timezone=scheduler_data.get("timezone", "Asia/Tokyo"),
                max_retries=scheduler_data.get("max_retries", 3),
                retry_delay=scheduler_data.get("retry_delay", 300),
                timeout=scheduler_data.get("timeout", 1800),
                enable_weekend=scheduler_data.get("enable_weekend", False)
            )
        except Exception as e:
            self.logger.warning(f"スケジューラー設定の読み込みに失敗: {e}")
            return SchedulerConfig()
    
    def _load_notification_config(self) -> NotificationConfig:
        """通知設定の読み込み"""
        try:
            config_data = self.config_manager.get_config()
            notification_data = config_data.get("notifications", {})
            
            return NotificationConfig(
                email_enabled=notification_data.get("email", {}).get("enabled", False),
                email_smtp_server=notification_data.get("email", {}).get("smtp_server", "smtp.gmail.com"),
                email_smtp_port=notification_data.get("email", {}).get("smtp_port", 587),
                email_user=notification_data.get("email", {}).get("user", ""),
                email_password=notification_data.get("email", {}).get("password", ""),
                email_to=notification_data.get("email", {}).get("to", ""),
                
                slack_enabled=notification_data.get("slack", {}).get("enabled", False),
                slack_webhook_url=notification_data.get("slack", {}).get("webhook_url", ""),
                slack_channel=notification_data.get("slack", {}).get("channel", "#stock-analysis"),
                slack_username=notification_data.get("slack", {}).get("username", "株価分析Bot"),
                slack_icon_emoji=notification_data.get("slack", {}).get("icon_emoji", ":chart_with_upwards_trend:"),
                
                browser_enabled=notification_data.get("browser", {}).get("enabled", True),
                browser_title=notification_data.get("browser", {}).get("title", "5分ルーティン完了"),
                browser_icon=notification_data.get("browser", {}).get("icon", "/favicon.ico")
            )
        except Exception as e:
            self.logger.warning(f"通知設定の読み込みに失敗: {e}")
            return NotificationConfig()
    
    def start_scheduler(self) -> None:
        """スケジューラーの開始"""
        if self.is_running:
            self.logger.warning("スケジューラーは既に実行中です")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        # スケジュール設定
        schedule.every().day.at(self.scheduler_config.execution_time).do(self._execute_routine)
        
        # スケジューラースレッド開始
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info(f"自動スケジューラーが開始されました (実行時間: {self.scheduler_config.execution_time})")
    
    def stop_scheduler(self) -> None:
        """スケジューラーの停止"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("自動スケジューラーが停止されました")
    
    def _scheduler_loop(self) -> None:
        """スケジューラーループ"""
        while self.is_running and not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
            except Exception as e:
                self.logger.error(f"スケジューラーループでエラー: {e}")
                time.sleep(60)
    
    def _execute_routine(self) -> None:
        """5分ルーティンの実行"""
        if self.is_running and not self.stop_event.is_set():
            self.logger.info("5分ルーティンの自動実行を開始します")
            
            # 週末チェック
            if not self.scheduler_config.enable_weekend:
                today = datetime.now()
                if today.weekday() >= 5:  # 土日
                    self.logger.info("週末のため実行をスキップします")
                    return
            
            # 実行
            success = self._run_routine_with_retry()
            
            # 結果通知
            self._send_notifications(success)
            
            # 実行記録更新
            self.last_execution = datetime.now()
            self.execution_count += 1
            if not success:
                self.error_count += 1
    
    def _run_routine_with_retry(self) -> bool:
        """リトライ機能付きルーティン実行"""
        for attempt in range(self.scheduler_config.max_retries):
            try:
                self.logger.info(f"ルーティン実行試行 {attempt + 1}/{self.scheduler_config.max_retries}")
                
                # ルーティンAPI呼び出し
                result = self._call_routine_api()
                
                if result.get("success", False):
                    self.logger.info("ルーティン実行が成功しました")
                    return True
                else:
                    self.logger.warning(f"ルーティン実行が失敗: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.logger.error(f"ルーティン実行でエラー (試行 {attempt + 1}): {e}")
            
            # リトライ前の待機
            if attempt < self.scheduler_config.max_retries - 1:
                self.logger.info(f"{self.scheduler_config.retry_delay}秒後にリトライします")
                time.sleep(self.scheduler_config.retry_delay)
        
        self.logger.error("最大リトライ回数に達しました")
        return False
    
    def _call_routine_api(self) -> Dict[str, Any]:
        """ルーティンAPI呼び出し"""
        try:
            # ルーティンAPIのエンドポイント
            api_url = "http://localhost:5057/routine/run-today"
            
            # リクエストデータ
            data = {
                "client_token": f"automated_{int(time.time())}",
                "automated": True
            }
            
            # API呼び出し
            response = requests.post(
                api_url,
                json=data,
                timeout=self.scheduler_config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                
                if job_id:
                    # ジョブ完了まで待機
                    return self._wait_for_job_completion(job_id)
                else:
                    return {"success": False, "error": "ジョブIDが取得できませんでした"}
            else:
                return {"success": False, "error": f"API呼び出し失敗: {response.status_code}"}
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "API呼び出しがタイムアウトしました"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "APIサーバーに接続できませんでした"}
        except Exception as e:
            return {"success": False, "error": f"API呼び出しエラー: {str(e)}"}
    
    def _wait_for_job_completion(self, job_id: str) -> Dict[str, Any]:
        """ジョブ完了まで待機"""
        max_wait_time = self.scheduler_config.timeout
        check_interval = 30  # 30秒ごとにチェック
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            try:
                # ジョブ状態確認
                response = requests.get(f"http://localhost:5057/routine/jobs/{job_id}")
                
                if response.status_code == 200:
                    job_data = response.json()
                    status = job_data.get("status")
                    
                    if status == "succeeded":
                        return {
                            "success": True,
                            "job_id": job_id,
                            "result_url": job_data.get("resultUrl"),
                            "progress": job_data.get("progress", 100)
                        }
                    elif status == "failed":
                        return {
                            "success": False,
                            "error": job_data.get("error", "ジョブが失敗しました")
                        }
                    else:
                        # 実行中またはキュー中
                        self.logger.info(f"ジョブ実行中... 進捗: {job_data.get('progress', 0)}%")
                        time.sleep(check_interval)
                        elapsed_time += check_interval
                else:
                    self.logger.warning(f"ジョブ状態確認失敗: {response.status_code}")
                    time.sleep(check_interval)
                    elapsed_time += check_interval
                    
            except Exception as e:
                self.logger.error(f"ジョブ状態確認でエラー: {e}")
                time.sleep(check_interval)
                elapsed_time += check_interval
        
        return {"success": False, "error": "ジョブ完了待機がタイムアウトしました"}
    
    def _send_notifications(self, success: bool) -> None:
        """結果通知の送信"""
        try:
            # 通知内容の準備
            subject, message = self._prepare_notification_content(success)
            
            # 各通知方法で送信
            if self.notification_config.email_enabled:
                self._send_email_notification(subject, message)
            
            if self.notification_config.slack_enabled:
                self._send_slack_notification(subject, message)
            
            if self.notification_config.browser_enabled:
                self._send_browser_notification(subject, message)
                
        except Exception as e:
            self.logger.error(f"通知送信でエラー: {e}")
    
    def _prepare_notification_content(self, success: bool) -> tuple[str, str]:
        """通知内容の準備"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if success:
            subject = f"✅ 5分ルーティン完了 - {timestamp}"
            message = f"""
5分ルーティンが正常に完了しました。

実行時刻: {timestamp}
実行回数: {self.execution_count}
エラー回数: {self.error_count}

詳細はダッシュボードで確認してください。
"""
        else:
            subject = f"❌ 5分ルーティン失敗 - {timestamp}"
            message = f"""
5分ルーティンでエラーが発生しました。

実行時刻: {timestamp}
実行回数: {self.execution_count}
エラー回数: {self.error_count}

詳細はログを確認してください。
"""
        
        return subject, message
    
    def _send_email_notification(self, subject: str, message: str) -> None:
        """メール通知の送信"""
        try:
            if not self.notification_config.email_user or not self.notification_config.email_to:
                self.logger.warning("メール設定が不完全です")
                return
            
            # メール作成
            msg = MIMEMultipart()
            msg['From'] = self.notification_config.email_user
            msg['To'] = self.notification_config.email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # SMTP送信
            server = smtplib.SMTP(self.notification_config.email_smtp_server, self.notification_config.email_smtp_port)
            server.starttls()
            server.login(self.notification_config.email_user, self.notification_config.email_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info("メール通知を送信しました")
            
        except Exception as e:
            self.logger.error(f"メール通知送信でエラー: {e}")
    
    def _send_slack_notification(self, subject: str, message: str) -> None:
        """Slack通知の送信"""
        try:
            if not self.notification_config.slack_webhook_url:
                self.logger.warning("Slack Webhook URLが設定されていません")
                return
            
            # Slackメッセージ作成
            slack_message = {
                "channel": self.notification_config.slack_channel,
                "username": self.notification_config.slack_username,
                "icon_emoji": self.notification_config.slack_icon_emoji,
                "text": subject,
                "attachments": [
                    {
                        "color": "good" if "完了" in subject else "danger",
                        "text": message,
                        "footer": "5分ルーティン自動化システム",
                        "ts": int(time.time())
                    }
                ]
            }
            
            # Slack送信
            response = requests.post(
                self.notification_config.slack_webhook_url,
                json=slack_message,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("Slack通知を送信しました")
            else:
                self.logger.error(f"Slack通知送信失敗: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Slack通知送信でエラー: {e}")
    
    def _send_browser_notification(self, subject: str, message: str) -> None:
        """ブラウザ通知の送信"""
        try:
            # 通知データをファイルに保存（フロントエンドが読み取り）
            notification_data = {
                "title": subject,
                "message": message,
                "icon": self.notification_config.browser_icon,
                "timestamp": datetime.now().isoformat(),
                "type": "routine_completion"
            }
            
            # 通知ファイル保存
            notification_file = "data/notifications.json"
            os.makedirs(os.path.dirname(notification_file), exist_ok=True)
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info("ブラウザ通知データを保存しました")
            
        except Exception as e:
            self.logger.error(f"ブラウザ通知でエラー: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """スケジューラー状態の取得"""
        return {
            "is_running": self.is_running,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "execution_time": self.scheduler_config.execution_time,
            "timezone": self.scheduler_config.timezone,
            "notifications": {
                "email_enabled": self.notification_config.email_enabled,
                "slack_enabled": self.notification_config.slack_enabled,
                "browser_enabled": self.notification_config.browser_enabled
            }
        }
    
    def manual_execute(self) -> bool:
        """手動実行"""
        if self.is_running:
            self.logger.info("手動実行を開始します")
            return self._run_routine_with_retry()
        else:
            self.logger.warning("スケジューラーが停止中です")
            return False


def main():
    """メイン関数"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/automated_scheduler.log'),
            logging.StreamHandler()
        ]
    )
    
    # スケジューラー作成
    scheduler = AutomatedScheduler()
    
    try:
        # スケジューラー開始
        scheduler.start_scheduler()
        
        # メインループ
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nスケジューラーを停止しています...")
        scheduler.stop_scheduler()
    except Exception as e:
        logging.error(f"スケジューラーでエラー: {e}")
        scheduler.stop_scheduler()


if __name__ == "__main__":
    main()
