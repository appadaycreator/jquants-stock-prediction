#!/usr/bin/env python3
"""
1日5分ルーティン作業の完全自動化スケジューラー
朝の決まった時間に自動実行し、結果を通知するシステム
"""

import schedule
import time
import logging
import json
import os
import subprocess
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import threading
import sys

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/automated_scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NotificationConfig:
    """通知設定"""

    def __init__(self):
        self.email_enabled = (
            os.getenv("EMAIL_NOTIFICATION_ENABLED", "false").lower() == "true"
        )
        self.slack_enabled = (
            os.getenv("SLACK_NOTIFICATION_ENABLED", "false").lower() == "true"
        )

        # メール設定
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.email_to = os.getenv("EMAIL_TO", "")

        # Slack設定
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.slack_channel = os.getenv("SLACK_CHANNEL", "#stock-analysis")


class AutomatedScheduler:
    """自動化スケジューラー"""

    def __init__(self):
        self.config = NotificationConfig()
        self.analysis_results = []
        self.is_running = False

        # ログディレクトリの作成
        os.makedirs("logs", exist_ok=True)

    def run_ultra_fast_analysis(self) -> Dict:
        """超高速分析の実行"""
        try:
            logger.info("超高速分析を開始します...")
            start_time = datetime.now()

            # 分析スクリプトの実行
            result = subprocess.run(
                ["python3", "web_analysis_runner.py", "ultra_fast"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            if result.returncode == 0:
                logger.info(f"分析完了: {duration:.2f}秒")
                return {
                    "status": "success",
                    "duration": duration,
                    "timestamp": start_time.isoformat(),
                    "output": result.stdout,
                    "analysis_type": "ultra_fast",
                }
            else:
                logger.error(f"分析失敗: {result.stderr}")
                return {
                    "status": "error",
                    "duration": duration,
                    "timestamp": start_time.isoformat(),
                    "error": result.stderr,
                    "analysis_type": "ultra_fast",
                }

        except Exception as e:
            logger.error(f"分析実行エラー: {str(e)}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "analysis_type": "ultra_fast",
            }

    def send_email_notification(self, result: Dict):
        """メール通知の送信"""
        if not self.config.email_enabled or not self.config.email_user:
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = self.config.email_user
            msg["To"] = self.config.email_to
            msg["Subject"] = (
                f"株価分析結果 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

            # メール本文の作成
            if result["status"] == "success":
                body = f"""
株価分析が完了しました。

実行時間: {result.get('duration', 0):.2f}秒
分析タイプ: {result.get('analysis_type', 'ultra_fast')}
実行日時: {result.get('timestamp', '')}

結果:
{result.get('output', '')}

詳細はダッシュボードでご確認ください。
                """
            else:
                body = f"""
株価分析でエラーが発生しました。

エラー内容: {result.get('error', '不明なエラー')}
実行日時: {result.get('timestamp', '')}

ログファイルを確認してください。
                """

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # SMTPサーバーに接続してメール送信
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.email_user, self.config.email_password)
            server.send_message(msg)
            server.quit()

            logger.info("メール通知を送信しました")

        except Exception as e:
            logger.error(f"メール送信エラー: {str(e)}")

    def send_slack_notification(self, result: Dict):
        """Slack通知の送信"""
        if not self.config.slack_enabled or not self.config.slack_webhook_url:
            return

        try:
            if result["status"] == "success":
                color = "good"
                title = "✅ 株価分析完了"
                text = f"実行時間: {result.get('duration', 0):.2f}秒\n分析タイプ: {result.get('analysis_type', 'ultra_fast')}"
            else:
                color = "danger"
                title = "❌ 株価分析エラー"
                text = f"エラー: {result.get('error', '不明なエラー')}"

            payload = {
                "channel": self.config.slack_channel,
                "username": "株価分析Bot",
                "icon_emoji": ":chart_with_upwards_trend:",
                "attachments": [
                    {
                        "color": color,
                        "title": title,
                        "text": text,
                        "footer": "J-Quants株価予測システム",
                        "ts": int(datetime.now().timestamp()),
                    }
                ],
            }

            response = requests.post(self.config.slack_webhook_url, json=payload)
            response.raise_for_status()

            logger.info("Slack通知を送信しました")

        except Exception as e:
            logger.error(f"Slack送信エラー: {str(e)}")

    def send_notifications(self, result: Dict):
        """通知の送信"""
        logger.info("通知を送信中...")

        # メール通知
        if self.config.email_enabled:
            self.send_email_notification(result)

        # Slack通知
        if self.config.slack_enabled:
            self.send_slack_notification(result)

    def scheduled_analysis(self):
        """スケジュールされた分析の実行"""
        logger.info("スケジュールされた分析を開始します")

        # 分析実行
        result = self.run_ultra_fast_analysis()

        # 結果を保存
        self.analysis_results.append(result)

        # 最新10件のみ保持
        if len(self.analysis_results) > 10:
            self.analysis_results = self.analysis_results[-10:]

        # 結果をファイルに保存
        with open("logs/latest_analysis_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 通知送信
        self.send_notifications(result)

        logger.info("スケジュールされた分析が完了しました")

    def setup_schedule(self):
        """スケジュールの設定"""
        # 毎日午前9時に実行
        schedule.every().day.at("09:00").do(self.scheduled_analysis)

        # 毎日午後3時にも実行（市場終了後）
        schedule.every().day.at("15:00").do(self.scheduled_analysis)

        logger.info("スケジュールを設定しました: 毎日9:00, 15:00")

    def run_scheduler(self):
        """スケジューラーの実行"""
        self.setup_schedule()
        self.is_running = True

        logger.info("自動化スケジューラーを開始しました")

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
            except KeyboardInterrupt:
                logger.info("スケジューラーを停止します")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"スケジューラーエラー: {str(e)}")
                time.sleep(60)

    def run_immediate_analysis(self):
        """即座に分析を実行"""
        logger.info("即座に分析を実行します")
        self.scheduled_analysis()

    def get_analysis_history(self) -> List[Dict]:
        """分析履歴の取得"""
        return self.analysis_results

    def get_latest_result(self) -> Optional[Dict]:
        """最新の分析結果の取得"""
        if self.analysis_results:
            return self.analysis_results[-1]
        return None


def main():
    """メイン関数"""
    scheduler = AutomatedScheduler()

    if len(sys.argv) > 1 and sys.argv[1] == "--immediate":
        # 即座に実行
        scheduler.run_immediate_analysis()
    else:
        # スケジューラーとして実行
        scheduler.run_scheduler()


if __name__ == "__main__":
    main()
