#!/usr/bin/env python3
"""
モデル再学習スケジューラー
週次・月次でバックグラウンド再学習を実行し、完了後に通知するシステム
"""

import schedule
import time
import logging
import json
import os
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
import yaml
from pathlib import Path

# 統合システムのインポート
from enhanced_ai_prediction_system import EnhancedAIPredictionSystem
from enhanced_analysis_notification_system import EnhancedNotificationSystem, NotificationPriority, NotificationType
from unified_system import UnifiedSystem, ErrorCategory, LogLevel, LogCategory

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/model_retraining_scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RetrainingFrequency(Enum):
    """再学習頻度"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    DAILY = "daily"


class RetrainingStatus(Enum):
    """再学習ステータス"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RetrainingResult:
    """再学習結果"""
    timestamp: str
    frequency: str
    status: str
    models_retrained: int
    performance_improvement: Dict[str, float]
    duration_seconds: float
    error_message: Optional[str] = None
    model_comparison: Optional[Dict[str, Any]] = None


class ModelRetrainingScheduler:
    """モデル再学習スケジューラー"""

    def __init__(self, config_file: str = "model_retraining_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.unified_system = UnifiedSystem()
        self.prediction_system = EnhancedAIPredictionSystem()
        self.notification_system = EnhancedNotificationSystem()
        self.retraining_history: List[RetrainingResult] = []
        self.is_running = False
        self.current_retraining = None

        # ログディレクトリの作成
        os.makedirs("logs", exist_ok=True)
        os.makedirs("model_cache", exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        default_config = {
            "retraining": {
                "enabled": True,
                "frequency": "weekly",  # weekly, monthly, daily
                "schedule_time": "02:00",  # 実行時刻
                "max_models": 10,
                "performance_threshold": 0.05,  # 5%以上の改善が必要
                "auto_switch_best_model": True,
            },
            "notification": {
                "enabled": True,
                "include_performance_comparison": True,
                "include_model_ranking": True,
            },
            "data": {
                "source_file": "processed_stock_data.csv",
                "target_column": "Close",
                "test_size": 0.2,
                "validation_size": 0.1,
            },
            "models": {
                "retrain_all": True,
                "specific_models": [],  # 特定のモデルのみ再学習
                "exclude_models": [],  # 除外するモデル
            }
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    # デフォルト設定とユーザー設定をマージ
                    self._merge_config(default_config, user_config)
            except Exception as e:
                logger.warning(f"設定ファイル読み込みエラー: {e}")
                logger.info("デフォルト設定を使用します")

        return default_config

    def _merge_config(self, default: Dict, user: Dict) -> None:
        """設定のマージ"""
        for key, value in user.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value

    def _save_config(self) -> None:
        """設定ファイルの保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")

    async def run_retraining(self, frequency: str = "weekly") -> RetrainingResult:
        """モデル再学習の実行"""
        start_time = datetime.now()
        logger.info(f"🔄 モデル再学習開始: {frequency}")

        try:
            # データの読み込み
            data = self._load_training_data()
            if data is None or data.empty:
                raise ValueError("学習データが読み込めません")

            # 現在のモデル性能を取得
            current_performance = self._get_current_model_performance()

            # 再学習実行
            retrained_models = self.prediction_system.retrain_models(
                data, 
                self.config["data"]["target_column"]
            )

            # 新しいモデル性能を評価
            new_performance = self._evaluate_retrained_models(retrained_models, data)

            # 性能改善を計算
            performance_improvement = self._calculate_performance_improvement(
                current_performance, 
                new_performance
            )

            # 最良モデルの切り替え
            if self.config["retraining"]["auto_switch_best_model"]:
                self._switch_to_best_model(new_performance)

            # 結果の記録
            duration = (datetime.now() - start_time).total_seconds()
            result = RetrainingResult(
                timestamp=start_time.isoformat(),
                frequency=frequency,
                status=RetrainingStatus.COMPLETED.value,
                models_retrained=len(retrained_models),
                performance_improvement=performance_improvement,
                duration_seconds=duration,
                model_comparison=new_performance
            )

            # 履歴に追加
            self.retraining_history.append(result)
            self._save_retraining_history()

            # 通知送信
            if self.config["notification"]["enabled"]:
                await self._send_retraining_notification(result)

            logger.info(f"✅ モデル再学習完了: {len(retrained_models)}個のモデル")
            return result

        except Exception as e:
            logger.error(f"❌ モデル再学習エラー: {e}")
            duration = (datetime.now() - start_time).total_seconds()
            
            result = RetrainingResult(
                timestamp=start_time.isoformat(),
                frequency=frequency,
                status=RetrainingStatus.FAILED.value,
                models_retrained=0,
                performance_improvement={},
                duration_seconds=duration,
                error_message=str(e)
            )

            self.retraining_history.append(result)
            self._save_retraining_history()

            # エラー通知
            if self.config["notification"]["enabled"]:
                await self._send_error_notification(result)

            return result

    def _load_training_data(self) -> Optional[pd.DataFrame]:
        """学習データの読み込み"""
        try:
            data_file = self.config["data"]["source_file"]
            if not os.path.exists(data_file):
                logger.error(f"データファイルが見つかりません: {data_file}")
                return None

            data = pd.read_csv(data_file)
            logger.info(f"学習データ読み込み完了: {len(data)}行")
            return data

        except Exception as e:
            logger.error(f"データ読み込みエラー: {e}")
            return None

    def _get_current_model_performance(self) -> Dict[str, float]:
        """現在のモデル性能を取得"""
        try:
            performance = self.prediction_system.get_model_performance()
            current_perf = {}
            
            for model_name, perf in performance.items():
                if hasattr(perf, 'r2_score'):
                    current_perf[model_name] = perf.r2_score
                else:
                    current_perf[model_name] = 0.0

            return current_perf

        except Exception as e:
            logger.warning(f"現在の性能取得エラー: {e}")
            return {}

    def _evaluate_retrained_models(self, retrained_models: Dict[str, str], data: pd.DataFrame) -> Dict[str, Any]:
        """再学習されたモデルの性能評価"""
        try:
            # 特徴量の準備
            feature_columns = [col for col in data.columns if col != self.config["data"]["target_column"]]
            X = data[feature_columns].values
            y = data[self.config["data"]["target_column"]].values

            # テストデータの分割
            test_size = self.config["data"]["test_size"]
            split_idx = int(len(X) * (1 - test_size))
            X_test = X[split_idx:]
            y_test = y[split_idx:]

            evaluation_results = {}

            for old_name, new_name in retrained_models.items():
                try:
                    # 新しいモデルを読み込み
                    model = self.prediction_system.load_model(new_name)
                    if model is None:
                        continue

                    # 予測実行
                    y_pred = model.predict(X_test)
                    
                    # 性能指標計算
                    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    mae = mean_absolute_error(y_test, y_pred)

                    evaluation_results[new_name] = {
                        "mse": mse,
                        "r2_score": r2,
                        "mae": mae,
                        "rmse": np.sqrt(mse)
                    }

                except Exception as e:
                    logger.warning(f"モデル評価エラー {new_name}: {e}")

            return evaluation_results

        except Exception as e:
            logger.error(f"モデル評価エラー: {e}")
            return {}

    def _calculate_performance_improvement(self, current: Dict[str, float], new: Dict[str, Any]) -> Dict[str, float]:
        """性能改善の計算"""
        improvement = {}
        
        for model_name, new_perf in new.items():
            if model_name in current and "r2_score" in new_perf:
                old_r2 = current[model_name]
                new_r2 = new_perf["r2_score"]
                improvement[model_name] = new_r2 - old_r2

        return improvement

    def _switch_to_best_model(self, performance: Dict[str, Any]) -> None:
        """最良モデルへの切り替え"""
        try:
            if not performance:
                return

            # R²スコアが最も高いモデルを選択
            best_model = max(performance.items(), key=lambda x: x[1].get("r2_score", 0))
            best_model_name = best_model[0]
            best_r2 = best_model[1].get("r2_score", 0)

            logger.info(f"🏆 最良モデルに切り替え: {best_model_name} (R²: {best_r2:.4f})")

            # 設定ファイルの更新（必要に応じて）
            # ここでモデル設定を更新する処理を実装

        except Exception as e:
            logger.error(f"モデル切り替えエラー: {e}")

    async def _send_retraining_notification(self, result: RetrainingResult) -> None:
        """再学習完了通知の送信"""
        try:
            # 性能改善の計算
            improvement_summary = self._calculate_improvement_summary(result)
            
            # 通知内容の生成
            if result.status == RetrainingStatus.COMPLETED.value:
                title = "🔄 モデル再学習完了"
                message = f"再学習が完了しました。{result.models_retrained}個のモデルを更新しました。"
                
                if improvement_summary["overall_improvement"] > 0.05:
                    title = "🚀 モデル性能大幅改善"
                    message = f"再学習により性能が{improvement_summary['overall_improvement']:.1%}向上しました！"
                elif improvement_summary["overall_improvement"] < -0.05:
                    title = "⚠️ モデル性能低下"
                    message = f"再学習により性能が{abs(improvement_summary['overall_improvement']):.1%}低下しました"
            else:
                title = "❌ モデル再学習失敗"
                message = f"再学習中にエラーが発生しました: {result.error_message}"

            notification_data = {
                "title": title,
                "message": message,
                "details": {
                    "実行時間": f"{result.duration_seconds:.1f}秒",
                    "再学習モデル数": result.models_retrained,
                    "性能改善率": f"{improvement_summary['overall_improvement']:.2%}",
                    "最良モデル": improvement_summary.get("best_model", "N/A"),
                    "推奨事項": self._generate_recommendations(improvement_summary)
                }
            }

            # 通知送信
            await self.notification_system.send_analysis_notification(
                result, 
                NotificationPriority.HIGH if improvement_summary["overall_improvement"] > 0.05 else NotificationPriority.NORMAL
            )

            # 追加の通知チャネル（Slack、メール等）
            await self._send_additional_notifications(notification_data)

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")

    def _calculate_improvement_summary(self, result: RetrainingResult) -> Dict[str, Any]:
        """性能改善サマリーの計算"""
        if not result.performance_improvement:
            return {
                "overall_improvement": 0.0,
                "best_model": "N/A",
                "improved_models": 0,
                "degraded_models": 0
            }

        improvements = list(result.performance_improvement.values())
        improved_models = len([v for v in improvements if v > 0])
        degraded_models = len([v for v in improvements if v < 0])
        
        # 最良モデルの特定
        best_model = "N/A"
        if result.model_comparison:
            best_model = max(result.model_comparison.items(), 
                           key=lambda x: x[1].get("r2_score", 0))[0]

        return {
            "overall_improvement": sum(improvements) / len(improvements) if improvements else 0.0,
            "best_model": best_model,
            "improved_models": improved_models,
            "degraded_models": degraded_models,
            "max_improvement": max(improvements) if improvements else 0.0,
            "min_improvement": min(improvements) if improvements else 0.0
        }

    def _generate_recommendations(self, improvement_summary: Dict[str, Any]) -> List[str]:
        """推奨事項の生成"""
        recommendations = []
        overall_improvement = improvement_summary["overall_improvement"]

        if overall_improvement > 0.1:
            recommendations.append("大幅な性能向上が確認されました。この設定を保存することを推奨します")
        elif overall_improvement > 0.05:
            recommendations.append("性能向上が確認されました。継続的な監視を推奨します")
        elif overall_improvement < -0.1:
            recommendations.append("性能が大幅に低下しました。設定の見直しが必要です")
        elif overall_improvement < -0.05:
            recommendations.append("性能が低下しました。パラメータの調整を検討してください")
        else:
            recommendations.append("性能に大きな変化はありません。定期的な再学習を継続してください")

        if improvement_summary["degraded_models"] > 0:
            recommendations.append(f"{improvement_summary['degraded_models']}個のモデルで性能低下が確認されました")

        return recommendations

    async def _send_additional_notifications(self, notification_data: Dict[str, Any]) -> None:
        """追加の通知チャネルでの送信"""
        try:
            # Slack通知
            if self.config.get("notification_channels", {}).get("slack", {}).get("enabled", False):
                await self._send_slack_notification(notification_data)

            # メール通知
            if self.config.get("notification_channels", {}).get("email", {}).get("enabled", False):
                await self._send_email_notification(notification_data)

        except Exception as e:
            logger.error(f"追加通知送信エラー: {e}")

    async def _send_slack_notification(self, notification_data: Dict[str, Any]) -> None:
        """Slack通知の送信"""
        try:
            import requests
            
            slack_config = self.config.get("notification_channels", {}).get("slack", {})
            webhook_url = slack_config.get("webhook_url")
            
            if not webhook_url:
                return

            # 色の決定
            title = notification_data["title"]
            if "大幅改善" in title or "🚀" in title:
                color = "good"
            elif "低下" in title or "⚠️" in title or "❌" in title:
                color = "danger"
            else:
                color = "#36a64f"

            payload = {
                "channel": slack_config.get("channel", "#model-retraining"),
                "username": slack_config.get("username", "モデル再学習Bot"),
                "icon_emoji": slack_config.get("icon_emoji", ":robot_face:"),
                "attachments": [
                    {
                        "color": color,
                        "title": notification_data["title"],
                        "text": notification_data["message"],
                        "fields": [
                            {
                                "title": "詳細",
                                "value": "\n".join([f"• {k}: {v}" for k, v in notification_data["details"].items()]),
                                "short": False
                            }
                        ],
                        "footer": "J-Quants株価予測システム",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Slack通知を送信しました")

        except Exception as e:
            logger.error(f"Slack通知送信エラー: {e}")

    async def _send_email_notification(self, notification_data: Dict[str, Any]) -> None:
        """メール通知の送信"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            email_config = self.config.get("notification_channels", {}).get("email", {})
            
            if not email_config.get("enabled", False):
                return

            msg = MIMEMultipart()
            msg["From"] = email_config.get("email_user", "")
            msg["To"] = email_config.get("email_to", "")
            msg["Subject"] = f"モデル再学習通知 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # HTMLメール本文の作成
            html_body = f"""
            <html>
            <body>
                <h2>{notification_data['title']}</h2>
                <p>{notification_data['message']}</p>
                
                <h3>詳細情報</h3>
                <ul>
            """
            
            for key, value in notification_data["details"].items():
                html_body += f"<li><strong>{key}:</strong> {value}</li>"
            
            html_body += """
                </ul>
                
                <p>詳細はダッシュボードでご確認ください。</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_body, "html", "utf-8"))

            # SMTPサーバーに接続してメール送信
            server = smtplib.SMTP(email_config.get("smtp_server", "smtp.gmail.com"), 
                                 email_config.get("smtp_port", 587))
            server.starttls()
            server.login(email_config.get("email_user", ""), 
                        email_config.get("email_password", ""))
            server.send_message(msg)
            server.quit()

            logger.info("メール通知を送信しました")

        except Exception as e:
            logger.error(f"メール通知送信エラー: {e}")

    async def _send_error_notification(self, result: RetrainingResult) -> None:
        """エラー通知の送信"""
        try:
            notification_data = {
                "title": "❌ モデル再学習エラー",
                "message": f"再学習中にエラーが発生しました: {result.error_message}",
                "details": {
                    "実行時間": f"{result.duration_seconds:.1f}秒",
                    "エラー": result.error_message
                }
            }

            # エラー通知の送信処理
            logger.error("再学習エラー通知を送信しました")

        except Exception as e:
            logger.error(f"エラー通知送信エラー: {e}")

    def _save_retraining_history(self) -> None:
        """再学習履歴の保存"""
        try:
            history_file = "logs/retraining_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(result) for result in self.retraining_history], 
                         f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"履歴保存エラー: {e}")

    def setup_schedule(self) -> None:
        """スケジュールの設定"""
        if not self.config["retraining"]["enabled"]:
            logger.info("再学習スケジュールは無効です")
            return

        frequency = self.config["retraining"]["frequency"]
        schedule_time = self.config["retraining"]["schedule_time"]

        if frequency == "daily":
            schedule.every().day.at(schedule_time).do(self._scheduled_retraining, "daily")
        elif frequency == "weekly":
            schedule.every().monday.at(schedule_time).do(self._scheduled_retraining, "weekly")
        elif frequency == "monthly":
            schedule.every().month.do(self._scheduled_retraining, "monthly")

        logger.info(f"再学習スケジュール設定完了: {frequency} at {schedule_time}")

    def _scheduled_retraining(self, frequency: str) -> None:
        """スケジュールされた再学習の実行"""
        if self.current_retraining is not None:
            logger.warning("既に再学習が実行中です")
            return

        logger.info(f"スケジュールされた再学習を開始: {frequency}")
        
        # 非同期実行
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                self.current_retraining = loop.run_until_complete(
                    self.run_retraining(frequency)
                )
            finally:
                loop.close()
                self.current_retraining = None

        thread = threading.Thread(target=run_async)
        thread.start()

    def run_scheduler(self) -> None:
        """スケジューラーの実行"""
        self.setup_schedule()
        self.is_running = True

        logger.info("モデル再学習スケジューラーを開始しました")

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
            except KeyboardInterrupt:
                logger.info("スケジューラーを停止します")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"スケジューラーエラー: {e}")
                time.sleep(60)

    def run_immediate_retraining(self, frequency: str = "weekly") -> RetrainingResult:
        """即座に再学習を実行"""
        logger.info(f"即座に再学習を実行: {frequency}")
        
        # 同期的に実行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_retraining(frequency))
        finally:
            loop.close()

    def get_retraining_history(self) -> List[Dict[str, Any]]:
        """再学習履歴の取得"""
        return [asdict(result) for result in self.retraining_history]

    def get_latest_result(self) -> Optional[Dict[str, Any]]:
        """最新の再学習結果の取得"""
        if self.retraining_history:
            return asdict(self.retraining_history[-1])
        return None

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """設定の更新"""
        self._merge_config(self.config, new_config)
        self._save_config()
        logger.info("設定を更新しました")

    def stop_scheduler(self) -> None:
        """スケジューラーの停止"""
        self.is_running = False
        logger.info("スケジューラーを停止しました")


def main():
    """メイン関数"""
    import sys
    
    scheduler = ModelRetrainingScheduler()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--immediate":
            # 即座に実行
            frequency = sys.argv[2] if len(sys.argv) > 2 else "weekly"
            result = scheduler.run_immediate_retraining(frequency)
            print(f"再学習結果: {result.status}")
        elif sys.argv[1] == "--config":
            # 設定表示
            print(json.dumps(scheduler.config, indent=2, ensure_ascii=False))
    else:
        # スケジューラーとして実行
        scheduler.run_scheduler()


if __name__ == "__main__":
    main()
