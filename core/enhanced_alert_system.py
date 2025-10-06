#!/usr/bin/env python3
"""
強化されたアラートシステム
多段階アラート、即座通知、通知チャネル管理を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import threading
import time
import asyncio
from queue import Queue, Empty
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor
import warnings

warnings.filterwarnings("ignore")


class AlertLevel(Enum):
    """アラートレベル"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """アラートタイプ"""

    STOP_LOSS = "stop_loss"  # 損切り
    TAKE_PROFIT = "take_profit"  # 利確
    PRICE_MOVEMENT = "price_movement"  # 価格変動
    VOLATILITY_SPIKE = "volatility_spike"  # ボラティリティ急増
    VOLUME_SPIKE = "volume_spike"  # 出来高急増
    RISK_LIMIT = "risk_limit"  # リスク制限
    SYSTEM_ERROR = "system_error"  # システムエラー
    MARKET_CRASH = "market_crash"  # 市場急落
    POSITION_OVERWEIGHT = "position_overweight"  # ポジション過大


class NotificationChannel(Enum):
    """通知チャネル"""

    EMAIL = "email"
    SLACK = "slack"
    WEB = "web"
    SMS = "sms"
    VOICE = "voice"


@dataclass
class AlertRule:
    """アラートルール"""

    id: str
    name: str
    alert_type: AlertType
    alert_level: AlertLevel
    conditions: Dict[str, Any]
    notification_channels: List[NotificationChannel]
    enabled: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Alert:
    """アラート"""

    id: str
    timestamp: datetime
    symbol: str
    alert_type: AlertType
    alert_level: AlertLevel
    title: str
    message: str
    current_value: float
    threshold_value: float
    recommendation: str
    metadata: Dict[str, Any]
    notification_channels: List[NotificationChannel]
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


@dataclass
class NotificationSettings:
    """通知設定"""

    email_enabled: bool
    email_address: str
    slack_enabled: bool
    slack_webhook_url: str
    web_enabled: bool
    sms_enabled: bool
    sms_phone: str
    voice_enabled: bool
    alert_frequency: int  # アラート頻度（分）
    quiet_hours_start: int  # 静寂時間開始（時）
    quiet_hours_end: int  # 静寂時間終了（時）


class EmailNotifier:
    """メール通知器"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """初期化"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)

    def send_alert(self, alert: Alert, recipient: str) -> bool:
        """アラート送信"""
        try:
            # メール作成
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = recipient
            msg["Subject"] = f"[{alert.alert_level.value.upper()}] {alert.title}"

            # 本文作成
            body = f"""
アラート詳細:
- 銘柄: {alert.symbol}
- タイプ: {alert.alert_type.value}
- レベル: {alert.alert_level.value}
- 現在値: {alert.current_value:.2f}
- 閾値: {alert.threshold_value:.2f}
- 時刻: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

メッセージ:
{alert.message}

推奨事項:
{alert.recommendation}

メタデータ:
{json.dumps(alert.metadata, indent=2, ensure_ascii=False)}
            """

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # メール送信
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"メールアラート送信成功: {alert.symbol}")
            return True

        except Exception as e:
            self.logger.error(f"メールアラート送信エラー: {e}")
            return False


class SlackNotifier:
    """Slack通知器"""

    def __init__(self, webhook_url: str):
        """初期化"""
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)

    def send_alert(self, alert: Alert) -> bool:
        """アラート送信"""
        try:
            # 色設定
            color_map = {
                AlertLevel.INFO: "#36a64f",
                AlertLevel.WARNING: "#ff9800",
                AlertLevel.CRITICAL: "#f44336",
                AlertLevel.EMERGENCY: "#d32f2f",
            }

            # Slackメッセージ作成
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert.alert_level, "#36a64f"),
                        "title": f"[{alert.alert_level.value.upper()}] {alert.title}",
                        "text": alert.message,
                        "fields": [
                            {"title": "銘柄", "value": alert.symbol, "short": True},
                            {
                                "title": "現在値",
                                "value": f"{alert.current_value:.2f}",
                                "short": True,
                            },
                            {
                                "title": "閾値",
                                "value": f"{alert.threshold_value:.2f}",
                                "short": True,
                            },
                            {
                                "title": "推奨事項",
                                "value": alert.recommendation,
                                "short": False,
                            },
                        ],
                        "footer": "リアルタイム損切りシステム",
                        "ts": int(alert.timestamp.timestamp()),
                    }
                ]
            }

            # Slack送信
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()

            self.logger.info(f"Slackアラート送信成功: {alert.symbol}")
            return True

        except Exception as e:
            self.logger.error(f"Slackアラート送信エラー: {e}")
            return False


class WebNotifier:
    """Web通知器"""

    def __init__(self, webhook_url: str):
        """初期化"""
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)

    def send_alert(self, alert: Alert) -> bool:
        """アラート送信"""
        try:
            # Web通知ペイロード作成
            payload = {
                "alert_id": alert.id,
                "timestamp": alert.timestamp.isoformat(),
                "symbol": alert.symbol,
                "alert_type": alert.alert_type.value,
                "alert_level": alert.alert_level.value,
                "title": alert.title,
                "message": alert.message,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "recommendation": alert.recommendation,
                "metadata": alert.metadata,
            }

            # Web送信
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()

            self.logger.info(f"Webアラート送信成功: {alert.symbol}")
            return True

        except Exception as e:
            self.logger.error(f"Webアラート送信エラー: {e}")
            return False


class EnhancedAlertSystem:
    """強化されたアラートシステム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)

        # アラート管理
        self.alert_rules = {}  # {rule_id: AlertRule}
        self.active_alerts = {}  # {alert_id: Alert}
        self.alert_history = []

        # 通知器
        self.notifiers = {}
        self._initialize_notifiers()

        # 通知設定
        self.notification_settings = self._get_default_notification_settings()

        # スレッド管理
        self.alert_queue = Queue()
        self.notification_queue = Queue()
        self.is_processing = False
        self.processing_thread = None

        # スレッドプール
        self.executor = ThreadPoolExecutor(max_workers=10)

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
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
                    "username": "",
                    "password": "",
                },
                "slack": {"webhook_url": ""},
                "web": {"webhook_url": ""},
            },
            "alert_frequency": {
                "max_alerts_per_hour": 100,
                "max_alerts_per_day": 1000,
                "quiet_hours": [22, 6],  # 22:00-06:00
            },
        }

    def _get_default_notification_settings(self) -> NotificationSettings:
        """デフォルト通知設定"""
        return NotificationSettings(
            email_enabled=True,
            email_address="",
            slack_enabled=False,
            slack_webhook_url="",
            web_enabled=True,
            sms_enabled=False,
            sms_phone="",
            voice_enabled=False,
            alert_frequency=5,  # 5分間隔
            quiet_hours_start=22,
            quiet_hours_end=6,
        )

    def _initialize_notifiers(self):
        """通知器初期化"""
        try:
            # メール通知器
            if self.config["notification"]["email"]["username"]:
                self.notifiers[NotificationChannel.EMAIL] = EmailNotifier(
                    self.config["notification"]["email"]["smtp_server"],
                    self.config["notification"]["email"]["smtp_port"],
                    self.config["notification"]["email"]["username"],
                    self.config["notification"]["email"]["password"],
                )

            # Slack通知器
            if self.config["notification"]["slack"]["webhook_url"]:
                self.notifiers[NotificationChannel.SLACK] = SlackNotifier(
                    self.config["notification"]["slack"]["webhook_url"]
                )

            # Web通知器
            if self.config["notification"]["web"]["webhook_url"]:
                self.notifiers[NotificationChannel.WEB] = WebNotifier(
                    self.config["notification"]["web"]["webhook_url"]
                )

        except Exception as e:
            self.logger.error(f"通知器初期化エラー: {e}")

    def start_processing(self):
        """アラート処理開始"""
        try:
            if self.is_processing:
                self.logger.warning("アラート処理は既に開始されています")
                return

            self.is_processing = True
            self.processing_thread = threading.Thread(
                target=self._processing_loop, daemon=True
            )
            self.processing_thread.start()

            self.logger.info("アラート処理を開始")

        except Exception as e:
            self.logger.error(f"アラート処理開始エラー: {e}")
            self.is_processing = False

    def stop_processing(self):
        """アラート処理停止"""
        try:
            self.is_processing = False
            if self.processing_thread:
                self.processing_thread.join(timeout=5.0)

            self.logger.info("アラート処理を停止")

        except Exception as e:
            self.logger.error(f"アラート処理停止エラー: {e}")

    def create_alert_rule(
        self,
        rule_id: str,
        name: str,
        alert_type: AlertType,
        alert_level: AlertLevel,
        conditions: Dict[str, Any],
        notification_channels: List[NotificationChannel],
        enabled: bool = True,
    ) -> bool:
        """アラートルール作成"""
        try:
            rule = AlertRule(
                id=rule_id,
                name=name,
                alert_type=alert_type,
                alert_level=alert_level,
                conditions=conditions,
                notification_channels=notification_channels,
                enabled=enabled,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.alert_rules[rule_id] = rule
            self.logger.info(f"アラートルール作成: {rule_id}")

            return True

        except Exception as e:
            self.logger.error(f"アラートルール作成エラー: {e}")
            return False

    def create_alert(
        self,
        symbol: str,
        alert_type: AlertType,
        alert_level: AlertLevel,
        title: str,
        message: str,
        current_value: float,
        threshold_value: float,
        recommendation: str,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """アラート作成"""
        try:
            # アラートID生成
            alert_id = f"{symbol}_{alert_type.value}_{int(time.time())}"

            # 通知チャネル決定
            notification_channels = self._determine_notification_channels(alert_level)

            # アラート作成
            alert = Alert(
                id=alert_id,
                timestamp=datetime.now(),
                symbol=symbol,
                alert_type=alert_type,
                alert_level=alert_level,
                title=title,
                message=message,
                current_value=current_value,
                threshold_value=threshold_value,
                recommendation=recommendation,
                metadata=metadata or {},
                notification_channels=notification_channels,
            )

            # アラート保存
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)

            # 履歴制限
            max_history = self.config["alert_processing"]["max_alert_history"]
            if len(self.alert_history) > max_history:
                self.alert_history = self.alert_history[-max_history:]

            # アラートキューに追加
            self.alert_queue.put(alert)

            self.logger.info(f"アラート作成: {alert_id}")

            return alert_id

        except Exception as e:
            self.logger.error(f"アラート作成エラー: {e}")
            return ""

    def _determine_notification_channels(
        self, alert_level: AlertLevel
    ) -> List[NotificationChannel]:
        """通知チャネル決定"""
        channels = []

        # レベルに応じた通知チャネル選択
        if alert_level == AlertLevel.EMERGENCY:
            channels = [
                NotificationChannel.EMAIL,
                NotificationChannel.SLACK,
                NotificationChannel.WEB,
            ]
        elif alert_level == AlertLevel.CRITICAL:
            channels = [
                NotificationChannel.EMAIL,
                NotificationChannel.SLACK,
                NotificationChannel.WEB,
            ]
        elif alert_level == AlertLevel.WARNING:
            channels = [NotificationChannel.SLACK, NotificationChannel.WEB]
        else:  # INFO
            channels = [NotificationChannel.WEB]

        # 設定に基づく有効化
        enabled_channels = []
        for channel in channels:
            if self._is_channel_enabled(channel):
                enabled_channels.append(channel)

        return enabled_channels

    def _is_channel_enabled(self, channel: NotificationChannel) -> bool:
        """チャネル有効化チェック"""
        if channel == NotificationChannel.EMAIL:
            return self.notification_settings.email_enabled
        elif channel == NotificationChannel.SLACK:
            return self.notification_settings.slack_enabled
        elif channel == NotificationChannel.WEB:
            return self.notification_settings.web_enabled
        elif channel == NotificationChannel.SMS:
            return self.notification_settings.sms_enabled
        elif channel == NotificationChannel.VOICE:
            return self.notification_settings.voice_enabled

        return False

    def _processing_loop(self):
        """アラート処理ループ"""
        while self.is_processing:
            try:
                # アラートキューから処理
                while not self.alert_queue.empty():
                    try:
                        alert = self.alert_queue.get_nowait()
                        self._process_alert(alert)
                    except Empty:
                        break

                # 通知キューから処理
                while not self.notification_queue.empty():
                    try:
                        notification = self.notification_queue.get_nowait()
                        self._process_notification(notification)
                    except Empty:
                        break

                time.sleep(self.config["alert_processing"]["processing_interval"])

            except Exception as e:
                self.logger.error(f"アラート処理ループエラー: {e}")
                time.sleep(self.config["alert_processing"]["processing_interval"])

    def _process_alert(self, alert: Alert):
        """アラート処理"""
        try:
            # アラート頻度チェック
            if not self._check_alert_frequency(alert):
                return

            # 静寂時間チェック
            if not self._check_quiet_hours():
                return

            # 通知実行
            for channel in alert.notification_channels:
                self._send_notification(alert, channel)

            self.logger.info(f"アラート処理完了: {alert.id}")

        except Exception as e:
            self.logger.error(f"アラート処理エラー: {e}")

    def _check_alert_frequency(self, alert: Alert) -> bool:
        """アラート頻度チェック"""
        try:
            # 過去1時間のアラート数チェック
            cutoff_time = datetime.now() - timedelta(hours=1)
            recent_alerts = [
                a
                for a in self.alert_history
                if a.timestamp >= cutoff_time and a.symbol == alert.symbol
            ]

            max_alerts_per_hour = self.config["alert_frequency"]["max_alerts_per_hour"]
            if len(recent_alerts) >= max_alerts_per_hour:
                self.logger.warning(f"アラート頻度制限: {alert.symbol}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"アラート頻度チェックエラー: {e}")
            return True

    def _check_quiet_hours(self) -> bool:
        """静寂時間チェック"""
        try:
            current_hour = datetime.now().hour
            quiet_start = self.notification_settings.quiet_hours_start
            quiet_end = self.notification_settings.quiet_hours_end

            # 静寂時間内かチェック
            if quiet_start <= quiet_end:
                # 通常の時間範囲（例：22:00-06:00）
                if quiet_start <= current_hour < quiet_end:
                    return False
            else:
                # 日をまたぐ時間範囲（例：22:00-06:00）
                if current_hour >= quiet_start or current_hour < quiet_end:
                    return False

            return True

        except Exception as e:
            self.logger.error(f"静寂時間チェックエラー: {e}")
            return True

    def _send_notification(self, alert: Alert, channel: NotificationChannel):
        """通知送信"""
        try:
            if channel not in self.notifiers:
                self.logger.warning(f"通知器が見つかりません: {channel}")
                return

            notifier = self.notifiers[channel]

            # 非同期で通知送信
            future = self.executor.submit(
                self._send_notification_async, notifier, alert, channel
            )

        except Exception as e:
            self.logger.error(f"通知送信エラー: {e}")

    def _send_notification_async(
        self, notifier, alert: Alert, channel: NotificationChannel
    ):
        """非同期通知送信"""
        try:
            if channel == NotificationChannel.EMAIL:
                success = notifier.send_alert(
                    alert, self.notification_settings.email_address
                )
            else:
                success = notifier.send_alert(alert)

            if success:
                self.logger.info(f"通知送信成功: {alert.id}, {channel.value}")
            else:
                self.logger.error(f"通知送信失敗: {alert.id}, {channel.value}")

        except Exception as e:
            self.logger.error(f"非同期通知送信エラー: {e}")

    def _process_notification(self, notification: Dict[str, Any]):
        """通知処理"""
        try:
            # 通知処理の実装
            pass

        except Exception as e:
            self.logger.error(f"通知処理エラー: {e}")

    def acknowledge_alert(self, alert_id: str) -> bool:
        """アラート確認"""
        try:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now()

            self.logger.info(f"アラート確認: {alert_id}")

            return True

        except Exception as e:
            self.logger.error(f"アラート確認エラー: {e}")
            return False

    def get_alert_status(self) -> Dict[str, Any]:
        """アラート状況取得"""
        try:
            active_count = len(self.active_alerts)
            unacknowledged_count = len(
                [a for a in self.active_alerts.values() if not a.acknowledged]
            )

            # レベル別集計
            level_counts = {}
            for alert in self.active_alerts.values():
                level = alert.alert_level.value
                level_counts[level] = level_counts.get(level, 0) + 1

            return {
                "status": "processing" if self.is_processing else "stopped",
                "active_alerts": active_count,
                "unacknowledged_alerts": unacknowledged_count,
                "level_counts": level_counts,
                "total_history": len(self.alert_history),
                "last_update": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"アラート状況取得エラー: {e}")
            return {"status": "error", "error": str(e)}

    def get_alert_history(
        self, symbol: str = None, days: int = 7
    ) -> List[Dict[str, Any]]:
        """アラート履歴取得"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            if symbol:
                recent_alerts = [
                    a
                    for a in self.alert_history
                    if a.symbol == symbol and a.timestamp >= cutoff_date
                ]
            else:
                recent_alerts = [
                    a for a in self.alert_history if a.timestamp >= cutoff_date
                ]

            # 時系列でソート
            recent_alerts.sort(key=lambda x: x.timestamp, reverse=True)

            return [
                {
                    "id": alert.id,
                    "timestamp": alert.timestamp.isoformat(),
                    "symbol": alert.symbol,
                    "alert_type": alert.alert_type.value,
                    "alert_level": alert.alert_level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value,
                    "recommendation": alert.recommendation,
                    "acknowledged": alert.acknowledged,
                    "acknowledged_at": alert.acknowledged_at.isoformat()
                    if alert.acknowledged_at
                    else None,
                    "metadata": alert.metadata,
                }
                for alert in recent_alerts
            ]

        except Exception as e:
            self.logger.error(f"アラート履歴取得エラー: {e}")
            return []

    def update_notification_settings(self, settings: NotificationSettings):
        """通知設定更新"""
        try:
            self.notification_settings = settings
            self._initialize_notifiers()

            self.logger.info("通知設定を更新")

        except Exception as e:
            self.logger.error(f"通知設定更新エラー: {e}")

    def export_alert_report(self, symbol: str = None, days: int = 7) -> Dict[str, Any]:
        """アラートレポート出力"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            if symbol:
                recent_alerts = [
                    a
                    for a in self.alert_history
                    if a.symbol == symbol and a.timestamp >= cutoff_date
                ]
            else:
                recent_alerts = [
                    a for a in self.alert_history if a.timestamp >= cutoff_date
                ]

            # アラート統計
            alert_counts = {}
            level_counts = {}
            type_counts = {}

            for alert in recent_alerts:
                alert_type = alert.alert_type.value
                alert_level = alert.alert_level.value

                alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
                level_counts[alert_level] = level_counts.get(alert_level, 0) + 1
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1

            return {
                "report_period": f"{days} days",
                "symbol": symbol or "all",
                "total_alerts": len(recent_alerts),
                "alert_counts": alert_counts,
                "level_counts": level_counts,
                "type_counts": type_counts,
                "acknowledged_rate": len([a for a in recent_alerts if a.acknowledged])
                / len(recent_alerts)
                if recent_alerts
                else 0,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"アラートレポート出力エラー: {e}")
            return {"error": str(e)}
