#!/usr/bin/env python3
"""
強化された分析結果自動通知システム
ワンクリック分析の完全自動化 - 通知機能強化版
"""

import asyncio
import json
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/enhanced_notification.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """通知優先度"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(Enum):
    """通知タイプ"""

    ANALYSIS_COMPLETE = "analysis_complete"
    ANALYSIS_ERROR = "analysis_error"
    RISK_ALERT = "risk_alert"
    PERFORMANCE_ALERT = "performance_alert"
    SYSTEM_STATUS = "system_status"


@dataclass
class AnalysisResult:
    """分析結果データクラス"""

    analysis_id: str
    analysis_type: str
    timestamp: datetime
    duration: float
    status: str
    confidence_score: float
    predictions: Dict[str, Any]
    risk_metrics: Dict[str, float]
    recommendations: List[str]
    performance_metrics: Dict[str, float]
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class NotificationConfig:
    """通知設定"""

    email_enabled: bool = True
    slack_enabled: bool = True
    webhook_enabled: bool = False

    # メール設定
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_to: List[str] = None

    # Slack設定
    slack_webhook_url: str = ""
    slack_channel: str = "#stock-analysis"
    slack_username: str = "株価分析Bot"

    # Webhook設定
    webhook_urls: List[str] = None

    # 通知フィルタリング
    min_confidence_threshold: float = 0.7
    include_errors: bool = True
    include_success: bool = True
    rate_limit_per_hour: int = 10

    def __post_init__(self):
        if self.email_to is None:
            self.email_to = []
        if self.webhook_urls is None:
            self.webhook_urls = []


class EnhancedNotificationSystem:
    """強化された通知システム"""

    def __init__(self, config: NotificationConfig = None):
        self.config = config or NotificationConfig()
        self.notification_history = []
        self.rate_limit_tracker = {}
        self.load_config()

    def load_config(self):
        """設定ファイルから設定を読み込み"""
        config_file = Path("notification_config.yaml")
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f)

                if "notification" in yaml_config:
                    notif_config = yaml_config["notification"]

                    # メール設定
                    if "email" in notif_config:
                        email_config = notif_config["email"]
                        self.config.email_enabled = email_config.get("enabled", True)
                        self.config.smtp_server = email_config.get(
                            "smtp_server", self.config.smtp_server
                        )
                        self.config.smtp_port = email_config.get(
                            "smtp_port", self.config.smtp_port
                        )
                        self.config.email_user = email_config.get(
                            "email_user", self.config.email_user
                        )
                        self.config.email_password = email_config.get(
                            "email_password", self.config.email_password
                        )
                        self.config.email_to = (
                            [email_config.get("email_to", "")]
                            if email_config.get("email_to")
                            else []
                        )

                    # Slack設定
                    if "slack" in notif_config:
                        slack_config = notif_config["slack"]
                        self.config.slack_enabled = slack_config.get("enabled", True)
                        self.config.slack_webhook_url = slack_config.get(
                            "webhook_url", self.config.slack_webhook_url
                        )
                        self.config.slack_channel = slack_config.get(
                            "channel", self.config.slack_channel
                        )
                        self.config.slack_username = slack_config.get(
                            "username", self.config.slack_username
                        )

                    # 通知フィルタリング
                    if "filters" in notif_config:
                        filters = notif_config["filters"]
                        self.config.min_confidence_threshold = filters.get(
                            "min_confidence_threshold", 0.7
                        )
                        self.config.include_errors = filters.get("include_errors", True)
                        self.config.include_success = filters.get(
                            "include_success", True
                        )

                    # レート制限
                    if "rate_limiting" in notif_config:
                        rate_limit = notif_config["rate_limiting"]
                        self.config.rate_limit_per_hour = rate_limit.get(
                            "max_notifications_per_hour", 10
                        )

            except Exception as e:
                logger.error(f"設定ファイル読み込みエラー: {e}")

    async def send_analysis_notification(
        self,
        result: AnalysisResult,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ):
        """分析結果の通知を送信"""
        try:
            # レート制限チェック
            if not self._check_rate_limit():
                logger.warning("レート制限により通知をスキップしました")
                return False

            # 通知フィルタリング
            if not self._should_send_notification(result):
                logger.info(f"通知フィルタにより通知をスキップ: {result.analysis_id}")
                return False

            # 通知内容の生成
            notification_data = self._generate_notification_content(result, priority)

            # 複数チャネルでの通知送信
            success_count = 0

            if self.config.email_enabled and self.config.email_to:
                if await self._send_email_notification(notification_data):
                    success_count += 1

            if self.config.slack_enabled and self.config.slack_webhook_url:
                if await self._send_slack_notification(notification_data):
                    success_count += 1

            if self.config.webhook_enabled and self.config.webhook_urls:
                if await self._send_webhook_notification(notification_data):
                    success_count += 1

            # 通知履歴に記録
            self._record_notification(result, success_count > 0)

            logger.info(f"通知送信完了: {success_count}チャネル成功")
            return success_count > 0

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            return False

    def _check_rate_limit(self) -> bool:
        """レート制限チェック"""
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)

        if current_hour not in self.rate_limit_tracker:
            self.rate_limit_tracker[current_hour] = 0

        if self.rate_limit_tracker[current_hour] >= self.config.rate_limit_per_hour:
            return False

        self.rate_limit_tracker[current_hour] += 1
        return True

    def _should_send_notification(self, result: AnalysisResult) -> bool:
        """通知送信の判定"""
        # エラー通知の判定
        if result.status == "error":
            return self.config.include_errors

        # 成功通知の判定
        if result.status == "success":
            if not self.config.include_success:
                return False

            # 信頼度閾値チェック
            if result.confidence_score < self.config.min_confidence_threshold:
                return False

        return True

    def _generate_notification_content(
        self, result: AnalysisResult, priority: NotificationPriority
    ) -> Dict[str, Any]:
        """通知内容の生成"""
        # 基本情報
        content = {
            "analysis_id": result.analysis_id,
            "analysis_type": result.analysis_type,
            "timestamp": result.timestamp.isoformat(),
            "duration": f"{result.duration:.2f}秒",
            "status": result.status,
            "priority": priority.value,
            "confidence_score": result.confidence_score,
        }

        # 成功時の詳細情報
        if result.status == "success":
            content.update(
                {
                    "predictions": result.predictions,
                    "risk_metrics": result.risk_metrics,
                    "recommendations": result.recommendations,
                    "performance_metrics": result.performance_metrics,
                }
            )

            # 推奨アクションの生成
            content["suggested_actions"] = self._generate_action_suggestions(result)

        # エラー時の情報
        elif result.status == "error":
            content.update(
                {
                    "error_message": result.error_message,
                    "retry_count": result.retry_count,
                    "suggested_actions": [
                        "システム管理者に連絡",
                        "ログを確認",
                        "手動で再実行",
                    ],
                }
            )

        return content

    def _generate_action_suggestions(self, result: AnalysisResult) -> List[str]:
        """アクション提案の生成"""
        suggestions = []

        # 信頼度に基づく提案
        if result.confidence_score >= 0.8:
            suggestions.append("高信頼度の予測 - 投資判断に活用可能")
        elif result.confidence_score >= 0.6:
            suggestions.append("中程度の信頼度 - 追加分析を推奨")
        else:
            suggestions.append("低信頼度 - より詳細な分析が必要")

        # リスク指標に基づく提案
        if result.risk_metrics:
            max_risk = (
                max(result.risk_metrics.values()) if result.risk_metrics.values() else 0
            )
            if max_risk > 0.7:
                suggestions.append("高リスク検知 - リスク管理を強化")
            elif max_risk > 0.4:
                suggestions.append("中程度のリスク - 注意深い監視が必要")
            else:
                suggestions.append("低リスク - 通常の投資判断で対応可能")

        # 推奨事項の追加
        suggestions.extend(result.recommendations[:3])  # 上位3件

        return suggestions

    async def _send_email_notification(self, content: Dict[str, Any]) -> bool:
        """メール通知の送信"""
        try:
            # メール本文の生成
            subject = (
                f"【株価分析】{content['analysis_type']} - {content['status'].upper()}"
            )
            body = self._generate_email_body(content)

            # メール送信
            msg = MIMEMultipart()
            msg["From"] = self.config.email_user
            msg["To"] = ", ".join(self.config.email_to)
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html", "utf-8"))

            # 添付ファイル（チャート画像）の生成
            if content.get("predictions"):
                chart_image = self._generate_chart_image(content)
                if chart_image:
                    attachment = MIMEBase("application", "octet-stream")
                    attachment.set_payload(chart_image)
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        "Content-Disposition",
                        f'attachment; filename=analysis_chart_{content["analysis_id"]}.png',
                    )
                    msg.attach(attachment)

            # SMTP送信
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_user, self.config.email_password)
                server.send_message(msg)

            logger.info("メール通知送信成功")
            return True

        except Exception as e:
            logger.error(f"メール通知送信エラー: {e}")
            return False

    def _generate_email_body(self, content: Dict[str, Any]) -> str:
        """メール本文の生成"""
        html_body = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .success {{ color: #28a745; }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                .info {{ color: #17a2b8; }}
                .metrics {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .recommendations {{ background-color: #e7f3ff; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .actions {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📊 株価分析結果通知</h2>
                <p><strong>分析ID:</strong> {content['analysis_id']}</p>
                <p><strong>分析タイプ:</strong> {content['analysis_type']}</p>
                <p><strong>実行時刻:</strong> {content['timestamp']}</p>
                <p><strong>実行時間:</strong> {content['duration']}</p>
            </div>
        """

        if content["status"] == "success":
            html_body += f"""
            <div class="success">
                <h3>✅ 分析完了</h3>
                <p><strong>信頼度スコア:</strong> {content['confidence_score']:.2f}</p>
            </div>
            
            <div class="metrics">
                <h4>📈 パフォーマンス指標</h4>
                <ul>
            """
            for metric, value in content.get("performance_metrics", {}).items():
                html_body += f"<li><strong>{metric}:</strong> {value:.2f}</li>"

            html_body += """
                </ul>
            </div>
            
            <div class="recommendations">
                <h4>💡 推奨事項</h4>
                <ul>
            """
            for rec in content.get("recommendations", []):
                html_body += f"<li>{rec}</li>"

            html_body += """
                </ul>
            </div>
            """
        else:
            html_body += f"""
            <div class="error">
                <h3>❌ 分析エラー</h3>
                <p><strong>エラーメッセージ:</strong> {content.get('error_message', '不明なエラー')}</p>
                <p><strong>リトライ回数:</strong> {content.get('retry_count', 0)}</p>
            </div>
            """

        # 推奨アクション
        if content.get("suggested_actions"):
            html_body += """
            <div class="actions">
                <h4>🎯 推奨アクション</h4>
                <ul>
            """
            for action in content["suggested_actions"]:
                html_body += f"<li>{action}</li>"

            html_body += """
                </ul>
            </div>
            """

        html_body += """
            <hr>
            <p><small>この通知は自動生成されました。J-Quants株価予測システム</small></p>
        </body>
        </html>
        """

        return html_body

    def _generate_chart_image(self, content: Dict[str, Any]) -> Optional[bytes]:
        """チャート画像の生成"""
        try:
            if not content.get("predictions"):
                return None

            # 予測データの可視化
            fig, ax = plt.subplots(figsize=(10, 6))

            # 予測データのプロット
            predictions = content["predictions"]
            if "stock_prices" in predictions:
                prices = predictions["stock_prices"]
                ax.plot(range(len(prices)), prices, "b-", label="予測価格")
                ax.set_title(f'株価予測 - {content["analysis_id"]}')
                ax.set_xlabel("時間")
                ax.set_ylabel("価格")
                ax.legend()
                ax.grid(True)

            # 画像をバイト配列に変換
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
            img_buffer.seek(0)
            image_bytes = img_buffer.getvalue()
            plt.close()

            return image_bytes

        except Exception as e:
            logger.error(f"チャート画像生成エラー: {e}")
            return None

    async def _send_slack_notification(self, content: Dict[str, Any]) -> bool:
        """Slack通知の送信"""
        try:
            # Slackメッセージの構築
            message = {
                "channel": self.config.slack_channel,
                "username": self.config.slack_username,
                "icon_emoji": ":chart_with_upwards_trend:",
                "attachments": [
                    {
                        "color": "good" if content["status"] == "success" else "danger",
                        "title": f"株価分析結果 - {content['analysis_type']}",
                        "fields": [
                            {
                                "title": "分析ID",
                                "value": content["analysis_id"],
                                "short": True,
                            },
                            {
                                "title": "ステータス",
                                "value": content["status"].upper(),
                                "short": True,
                            },
                            {
                                "title": "実行時間",
                                "value": content["duration"],
                                "short": True,
                            },
                            {
                                "title": "信頼度スコア",
                                "value": f"{content['confidence_score']:.2f}",
                                "short": True,
                            },
                        ],
                        "footer": "J-Quants株価予測システム",
                        "ts": int(datetime.now().timestamp()),
                    }
                ],
            }

            # 成功時の追加情報
            if content["status"] == "success":
                if content.get("recommendations"):
                    message["attachments"][0]["fields"].append(
                        {
                            "title": "推奨事項",
                            "value": "\n".join(content["recommendations"][:3]),
                            "short": False,
                        }
                    )

                if content.get("suggested_actions"):
                    message["attachments"][0]["fields"].append(
                        {
                            "title": "推奨アクション",
                            "value": "\n".join(content["suggested_actions"][:3]),
                            "short": False,
                        }
                    )

            # Webhook送信
            response = requests.post(
                self.config.slack_webhook_url, json=message, timeout=10
            )

            if response.status_code == 200:
                logger.info("Slack通知送信成功")
                return True
            else:
                logger.error(f"Slack通知送信失敗: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Slack通知送信エラー: {e}")
            return False

    async def _send_webhook_notification(self, content: Dict[str, Any]) -> bool:
        """Webhook通知の送信"""
        try:
            success_count = 0

            for webhook_url in self.config.webhook_urls:
                try:
                    response = requests.post(
                        webhook_url,
                        json=content,
                        timeout=10,
                        headers={"Content-Type": "application/json"},
                    )

                    if response.status_code in [200, 201, 202]:
                        success_count += 1
                        logger.info(f"Webhook通知送信成功: {webhook_url}")
                    else:
                        logger.error(
                            f"Webhook通知送信失敗: {webhook_url} - {response.status_code}"
                        )

                except Exception as e:
                    logger.error(f"Webhook通知送信エラー: {webhook_url} - {e}")

            return success_count > 0

        except Exception as e:
            logger.error(f"Webhook通知送信エラー: {e}")
            return False

    def _record_notification(self, result: AnalysisResult, success: bool):
        """通知履歴の記録"""
        notification_record = {
            "timestamp": datetime.now(),
            "analysis_id": result.analysis_id,
            "analysis_type": result.analysis_type,
            "status": result.status,
            "notification_success": success,
            "channels_used": {
                "email": self.config.email_enabled,
                "slack": self.config.slack_enabled,
                "webhook": self.config.webhook_enabled,
            },
        }

        self.notification_history.append(notification_record)

        # 履歴の保存（最新100件を保持）
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]

    async def send_batch_notifications(self, results: List[AnalysisResult]):
        """複数の分析結果を一括通知"""
        success_count = 0

        for result in results:
            if await self.send_analysis_notification(result):
                success_count += 1

        logger.info(f"一括通知完了: {success_count}/{len(results)}件成功")
        return success_count

    def get_notification_stats(self) -> Dict[str, Any]:
        """通知統計の取得"""
        total_notifications = len(self.notification_history)
        successful_notifications = sum(
            1 for n in self.notification_history if n["notification_success"]
        )

        return {
            "total_notifications": total_notifications,
            "successful_notifications": successful_notifications,
            "success_rate": (
                successful_notifications / total_notifications
                if total_notifications > 0
                else 0
            ),
            "recent_notifications": (
                self.notification_history[-10:] if self.notification_history else []
            ),
        }


# 使用例
async def main():
    """使用例"""
    # 通知設定
    config = NotificationConfig(
        email_enabled=True,
        slack_enabled=True,
        email_user="your-email@gmail.com",
        email_password="your-app-password",
        email_to=["recipient@example.com"],
        slack_webhook_url="https://hooks.slack.com/services/...",
        slack_channel="#stock-analysis",
    )

    # 通知システムの初期化
    notification_system = EnhancedNotificationSystem(config)

    # 分析結果の作成（例）
    result = AnalysisResult(
        analysis_id="analysis_001",
        analysis_type="ultra_fast",
        timestamp=datetime.now(),
        duration=120.5,
        status="success",
        confidence_score=0.85,
        predictions={"stock_prices": [100, 102, 105, 108, 110]},
        risk_metrics={"volatility": 0.15, "max_drawdown": 0.05},
        recommendations=[
            "買いシグナル検知",
            "リスク管理を強化",
            "ポートフォリオの再バランス",
        ],
        performance_metrics={"sharpe_ratio": 1.2, "return": 0.08},
    )

    # 通知送信
    await notification_system.send_analysis_notification(
        result, NotificationPriority.HIGH
    )


if __name__ == "__main__":
    asyncio.run(main())
