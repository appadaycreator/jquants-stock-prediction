#!/usr/bin/env python3
"""
新NISAアラートシステム
2024年1月開始の新NISA制度に対応したアラート・通知機能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class AlertType(Enum):
    """アラートの種類"""

    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    INFO = "INFO"
    SUCCESS = "SUCCESS"


class AlertPriority(Enum):
    """アラートの優先度"""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class QuotaAlert:
    """枠使用状況アラート"""

    type: str
    message: str
    quota_type: str
    current_usage: float
    threshold: float
    recommended_action: str
    priority: str
    created_at: str


@dataclass
class InvestmentOpportunity:
    """投資機会通知"""

    symbol: str
    symbol_name: str
    reason: str
    expected_return: float
    risk_level: str
    quota_recommendation: str
    suggested_amount: float
    priority: str
    created_at: str


@dataclass
class SystemAlert:
    """システムアラート"""

    type: str
    message: str
    component: str
    severity: str
    action_required: bool
    created_at: str


class NisaAlertSystem:
    """新NISAアラートシステム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # アラート設定
        self.alert_thresholds = {
            "growth_warning": self.config.get("growth_warning_threshold", 80.0),
            "growth_critical": self.config.get("growth_critical_threshold", 95.0),
            "accumulation_warning": self.config.get(
                "accumulation_warning_threshold", 80.0
            ),
            "accumulation_critical": self.config.get(
                "accumulation_critical_threshold", 95.0
            ),
        }

        # 通知設定
        self.notification_settings = {
            "email": self.config.get("email_notifications", True),
            "browser": self.config.get("browser_notifications", True),
            "push": self.config.get("push_notifications", False),
        }

        # アラート履歴
        self.alert_history = []

    def check_quota_alerts(self, quota_status: Dict[str, Any]) -> List[QuotaAlert]:
        """枠使用状況アラートのチェック"""
        try:
            alerts = []

            # 成長投資枠のアラートチェック
            growth_alerts = self._check_growth_quota_alerts(quota_status)
            alerts.extend(growth_alerts)

            # つみたて投資枠のアラートチェック
            accumulation_alerts = self._check_accumulation_quota_alerts(quota_status)
            alerts.extend(accumulation_alerts)

            # アラート履歴の更新
            for alert in alerts:
                self.alert_history.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"枠使用状況アラートチェックエラー: {e}")
            return []

    def _check_growth_quota_alerts(
        self, quota_status: Dict[str, Any]
    ) -> List[QuotaAlert]:
        """成長投資枠のアラートチェック"""
        try:
            alerts = []
            growth_investment = quota_status.get("growth_investment", {})

            utilization_rate = growth_investment.get("utilization_rate", 0)
            used_amount = growth_investment.get("used_amount", 0)
            available_amount = growth_investment.get("available_amount", 0)

            # 警告レベルのアラート
            if utilization_rate >= self.alert_thresholds["growth_warning"]:
                alert = QuotaAlert(
                    type=AlertType.WARNING.value,
                    message=f"成長投資枠の使用率が{utilization_rate:.1f}%に達しています",
                    quota_type="GROWTH",
                    current_usage=utilization_rate,
                    threshold=self.alert_thresholds["growth_warning"],
                    recommended_action="残りの枠を有効活用することを検討してください",
                    priority=AlertPriority.MEDIUM.value,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            # クリティカルレベルのアラート
            if utilization_rate >= self.alert_thresholds["growth_critical"]:
                alert = QuotaAlert(
                    type=AlertType.CRITICAL.value,
                    message=f"成長投資枠の使用率が{utilization_rate:.1f}%に達しています。枠が不足する可能性があります",
                    quota_type="GROWTH",
                    current_usage=utilization_rate,
                    threshold=self.alert_thresholds["growth_critical"],
                    recommended_action="枠の効率的な活用を検討し、必要に応じて売却を検討してください",
                    priority=AlertPriority.HIGH.value,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            # 枠不足のアラート
            if available_amount < 100000:  # 10万円未満
                alert = QuotaAlert(
                    type=AlertType.WARNING.value,
                    message=f"成長投資枠の残りが{available_amount:,.0f}円です",
                    quota_type="GROWTH",
                    current_usage=utilization_rate,
                    threshold=100000,
                    recommended_action="枠の有効活用を検討してください",
                    priority=AlertPriority.MEDIUM.value,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"成長投資枠アラートチェックエラー: {e}")
            return []

    def _check_accumulation_quota_alerts(
        self, quota_status: Dict[str, Any]
    ) -> List[QuotaAlert]:
        """つみたて投資枠のアラートチェック"""
        try:
            alerts = []
            accumulation_investment = quota_status.get("accumulation_investment", {})

            utilization_rate = accumulation_investment.get("utilization_rate", 0)
            used_amount = accumulation_investment.get("used_amount", 0)
            available_amount = accumulation_investment.get("available_amount", 0)

            # 警告レベルのアラート
            if utilization_rate >= self.alert_thresholds["accumulation_warning"]:
                alert = QuotaAlert(
                    type=AlertType.WARNING.value,
                    message=f"つみたて投資枠の使用率が{utilization_rate:.1f}%に達しています",
                    quota_type="ACCUMULATION",
                    current_usage=utilization_rate,
                    threshold=self.alert_thresholds["accumulation_warning"],
                    recommended_action="残りの枠を有効活用することを検討してください",
                    priority=AlertPriority.MEDIUM.value,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            # クリティカルレベルのアラート
            if utilization_rate >= self.alert_thresholds["accumulation_critical"]:
                alert = QuotaAlert(
                    type=AlertType.CRITICAL.value,
                    message=f"つみたて投資枠の使用率が{utilization_rate:.1f}%に達しています。枠が不足する可能性があります",
                    quota_type="ACCUMULATION",
                    current_usage=utilization_rate,
                    threshold=self.alert_thresholds["accumulation_critical"],
                    recommended_action="枠の効率的な活用を検討し、必要に応じて売却を検討してください",
                    priority=AlertPriority.HIGH.value,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            # 枠不足のアラート
            if available_amount < 10000:  # 1万円未満
                alert = QuotaAlert(
                    type=AlertType.WARNING.value,
                    message=f"つみたて投資枠の残りが{available_amount:,.0f}円です",
                    quota_type="ACCUMULATION",
                    current_usage=utilization_rate,
                    threshold=10000,
                    recommended_action="枠の有効活用を検討してください",
                    priority=AlertPriority.MEDIUM.value,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"つみたて投資枠アラートチェックエラー: {e}")
            return []

    def generate_investment_opportunities(
        self, market_data: List[Dict[str, Any]], quota_status: Dict[str, Any]
    ) -> List[InvestmentOpportunity]:
        """投資機会通知の生成"""
        try:
            opportunities = []

            # 成長投資枠の投資機会
            growth_opportunities = self._generate_growth_opportunities(
                market_data, quota_status
            )
            opportunities.extend(growth_opportunities)

            # つみたて投資枠の投資機会
            accumulation_opportunities = self._generate_accumulation_opportunities(
                market_data, quota_status
            )
            opportunities.extend(accumulation_opportunities)

            return opportunities

        except Exception as e:
            self.logger.error(f"投資機会通知生成エラー: {e}")
            return []

    def _generate_growth_opportunities(
        self, market_data: List[Dict[str, Any]], quota_status: Dict[str, Any]
    ) -> List[InvestmentOpportunity]:
        """成長投資枠の投資機会生成"""
        try:
            opportunities = []
            growth_available = quota_status.get("growth_investment", {}).get(
                "available_amount", 0
            )

            if growth_available < 100000:  # 10万円未満の場合は機会を生成しない
                return opportunities

            # 市場データから投資機会を抽出
            for data in market_data:
                if data.get("recommendation_score", 0) > 0.7:  # 推奨スコアが高い場合
                    opportunity = InvestmentOpportunity(
                        symbol=data.get("symbol", ""),
                        symbol_name=data.get("symbol_name", ""),
                        reason=f"推奨スコア{data.get('recommendation_score', 0):.2f}で投資機会を検出",
                        expected_return=data.get("expected_return", 0),
                        risk_level=data.get("risk_level", "MEDIUM"),
                        quota_recommendation="GROWTH",
                        suggested_amount=min(
                            growth_available * 0.1, 100000
                        ),  # 利用可能枠の10%または10万円
                        priority=AlertPriority.MEDIUM.value,
                        created_at=datetime.now().isoformat(),
                    )
                    opportunities.append(opportunity)

            return opportunities

        except Exception as e:
            self.logger.error(f"成長投資枠投資機会生成エラー: {e}")
            return []

    def _generate_accumulation_opportunities(
        self, market_data: List[Dict[str, Any]], quota_status: Dict[str, Any]
    ) -> List[InvestmentOpportunity]:
        """つみたて投資枠の投資機会生成"""
        try:
            opportunities = []
            accumulation_available = quota_status.get(
                "accumulation_investment", {}
            ).get("available_amount", 0)

            if accumulation_available < 10000:  # 1万円未満の場合は機会を生成しない
                return opportunities

            # つみたて投資に適した銘柄を抽出
            for data in market_data:
                if (
                    data.get("risk_level") == "LOW"
                    and data.get("dividend_yield", 0) > 0.02
                ):  # 低リスクで配当利回りが高い
                    opportunity = InvestmentOpportunity(
                        symbol=data.get("symbol", ""),
                        symbol_name=data.get("symbol_name", ""),
                        reason="低リスク・高配当でつみたて投資に適している",
                        expected_return=data.get("expected_return", 0),
                        risk_level="LOW",
                        quota_recommendation="ACCUMULATION",
                        suggested_amount=min(
                            accumulation_available * 0.2, 20000
                        ),  # 利用可能枠の20%または2万円
                        priority=AlertPriority.MEDIUM.value,
                        created_at=datetime.now().isoformat(),
                    )
                    opportunities.append(opportunity)

            return opportunities

        except Exception as e:
            self.logger.error(f"つみたて投資枠投資機会生成エラー: {e}")
            return []

    def check_system_alerts(self, system_status: Dict[str, Any]) -> List[SystemAlert]:
        """システムアラートのチェック"""
        try:
            alerts = []

            # システムヘルスチェック
            system_health = system_status.get("system_health", "UNKNOWN")
            if system_health != "HEALTHY":
                alert = SystemAlert(
                    type=AlertType.WARNING.value,
                    message=f"システムの状態が{system_health}です",
                    component="SYSTEM",
                    severity="MEDIUM",
                    action_required=True,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            # データ整合性チェック
            data_integrity = system_status.get("data_integrity", True)
            if not data_integrity:
                alert = SystemAlert(
                    type=AlertType.CRITICAL.value,
                    message="データの整合性に問題が検出されました",
                    component="DATA",
                    severity="HIGH",
                    action_required=True,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            # パフォーマンスチェック
            response_time = system_status.get("response_time", 0)
            if response_time > 5.0:  # 5秒以上
                alert = SystemAlert(
                    type=AlertType.WARNING.value,
                    message=f"システムの応答時間が{response_time:.1f}秒と長くなっています",
                    component="PERFORMANCE",
                    severity="LOW",
                    action_required=False,
                    created_at=datetime.now().isoformat(),
                )
                alerts.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"システムアラートチェックエラー: {e}")
            return []

    def send_notification(self, alert: Any, notification_type: str = "browser") -> bool:
        """通知の送信"""
        try:
            if notification_type == "email" and self.notification_settings["email"]:
                return self._send_email_notification(alert)
            elif (
                notification_type == "browser" and self.notification_settings["browser"]
            ):
                return self._send_browser_notification(alert)
            elif notification_type == "push" and self.notification_settings["push"]:
                return self._send_push_notification(alert)
            else:
                self.logger.warning(
                    f"通知タイプ{notification_type}が無効または設定されていません"
                )
                return False

        except Exception as e:
            self.logger.error(f"通知送信エラー: {e}")
            return False

    def _send_email_notification(self, alert: Any) -> bool:
        """メール通知の送信"""
        try:
            # メール送信の実装（実際の実装ではSMTP等を使用）
            self.logger.info(f"メール通知送信: {alert.message}")
            return True
        except Exception as e:
            self.logger.error(f"メール通知送信エラー: {e}")
            return False

    def _send_browser_notification(self, alert: Any) -> bool:
        """ブラウザ通知の送信"""
        try:
            # ブラウザ通知の実装（実際の実装ではWebSocket等を使用）
            self.logger.info(f"ブラウザ通知送信: {alert.message}")
            return True
        except Exception as e:
            self.logger.error(f"ブラウザ通知送信エラー: {e}")
            return False

    def _send_push_notification(self, alert: Any) -> bool:
        """プッシュ通知の送信"""
        try:
            # プッシュ通知の実装（実際の実装ではFCM等を使用）
            self.logger.info(f"プッシュ通知送信: {alert.message}")
            return True
        except Exception as e:
            self.logger.error(f"プッシュ通知送信エラー: {e}")
            return False

    def get_alert_summary(self) -> Dict[str, Any]:
        """アラートサマリーの取得"""
        try:
            # アラートの集計
            total_alerts = len(self.alert_history)
            critical_alerts = len(
                [a for a in self.alert_history if a.type == AlertType.CRITICAL.value]
            )
            warning_alerts = len(
                [a for a in self.alert_history if a.type == AlertType.WARNING.value]
            )
            info_alerts = len(
                [a for a in self.alert_history if a.type == AlertType.INFO.value]
            )

            # 最近のアラート（過去24時間）
            recent_alerts = [
                a
                for a in self.alert_history
                if datetime.fromisoformat(a.created_at)
                > datetime.now() - timedelta(hours=24)
            ]

            return {
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "warning_alerts": warning_alerts,
                "info_alerts": info_alerts,
                "recent_alerts": len(recent_alerts),
                "alert_rate": len(recent_alerts) / 24
                if recent_alerts
                else 0,  # 時間あたりのアラート数
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"アラートサマリー取得エラー: {e}")
            return {"error": str(e)}

    def clear_old_alerts(self, days: int = 30) -> int:
        """古いアラートの削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            old_alerts = [
                a
                for a in self.alert_history
                if datetime.fromisoformat(a.created_at) < cutoff_date
            ]

            # 古いアラートの削除
            self.alert_history = [
                a
                for a in self.alert_history
                if datetime.fromisoformat(a.created_at) >= cutoff_date
            ]

            return len(old_alerts)

        except Exception as e:
            self.logger.error(f"古いアラート削除エラー: {e}")
            return 0

    def update_alert_settings(self, new_settings: Dict[str, Any]) -> bool:
        """アラート設定の更新"""
        try:
            # 閾値設定の更新
            if "thresholds" in new_settings:
                self.alert_thresholds.update(new_settings["thresholds"])

            # 通知設定の更新
            if "notifications" in new_settings:
                self.notification_settings.update(new_settings["notifications"])

            return True

        except Exception as e:
            self.logger.error(f"アラート設定更新エラー: {e}")
            return False
