#!/usr/bin/env python3
"""
NISAアラートシステムの単体テスト
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from core.nisa_alert_system import (
    NisaAlertSystem,
    QuotaAlert,
    InvestmentOpportunity,
    SystemAlert,
    AlertType,
    AlertPriority,
)


class TestNisaAlertSystem:
    """NISAアラートシステムのテスト"""

    @pytest.fixture
    def alert_system(self):
        """アラートシステムのインスタンス"""
        config = {
            "growth_warning_threshold": 80.0,
            "growth_critical_threshold": 95.0,
            "accumulation_warning_threshold": 80.0,
            "accumulation_critical_threshold": 95.0,
            "email_notifications": True,
            "browser_notifications": True,
            "push_notifications": False,
        }
        return NisaAlertSystem(config)

    @pytest.fixture
    def sample_quota_status(self):
        """サンプル枠状況"""
        return {
            "growth_investment": {
                "utilization_rate": 85.0,
                "used_amount": 2040000.0,
                "available_amount": 360000.0,
            },
            "accumulation_investment": {
                "utilization_rate": 75.0,
                "used_amount": 300000.0,
                "available_amount": 100000.0,
            },
        }

    @pytest.fixture
    def sample_market_data(self):
        """サンプル市場データ"""
        return [
            {
                "symbol": "7203",
                "symbol_name": "トヨタ自動車",
                "recommendation_score": 0.85,
                "expected_return": 0.12,
                "risk_level": "MEDIUM",
                "dividend_yield": 0.025,
            },
            {
                "symbol": "6758",
                "symbol_name": "ソニーグループ",
                "recommendation_score": 0.75,
                "expected_return": 0.15,
                "risk_level": "HIGH",
                "dividend_yield": 0.015,
            },
        ]

    def test_initialization(self, alert_system):
        """初期化テスト"""
        assert alert_system.alert_thresholds["growth_warning"] == 80.0
        assert alert_system.alert_thresholds["growth_critical"] == 95.0
        assert alert_system.alert_thresholds["accumulation_warning"] == 80.0
        assert alert_system.alert_thresholds["accumulation_critical"] == 95.0
        assert alert_system.notification_settings["email"] == True
        assert alert_system.notification_settings["browser"] == True
        assert alert_system.notification_settings["push"] == False

    def test_check_quota_alerts(self, alert_system, sample_quota_status):
        """枠使用状況アラートチェックテスト"""
        alerts = alert_system.check_quota_alerts(sample_quota_status)

        assert isinstance(alerts, list)
        assert len(alerts) > 0

        # アラートの検証
        for alert in alerts:
            assert isinstance(alert, QuotaAlert)
            assert alert.type in [
                AlertType.WARNING.value,
                AlertType.CRITICAL.value,
                AlertType.INFO.value,
            ]
            assert alert.quota_type in ["GROWTH", "ACCUMULATION"]
            assert alert.current_usage >= 0
            assert alert.threshold >= 0
            assert alert.priority in [
                AlertPriority.HIGH.value,
                AlertPriority.MEDIUM.value,
                AlertPriority.LOW.value,
            ]

    def test_check_growth_quota_alerts_warning(self, alert_system):
        """成長投資枠警告アラートテスト"""
        quota_status = {
            "growth_investment": {
                "utilization_rate": 85.0,
                "used_amount": 2040000.0,
                "available_amount": 360000.0,
            }
        }

        alerts = alert_system._check_growth_quota_alerts(quota_status)

        assert len(alerts) > 0
        warning_alerts = [a for a in alerts if a.type == AlertType.WARNING.value]
        assert len(warning_alerts) > 0

        warning_alert = warning_alerts[0]
        assert warning_alert.quota_type == "GROWTH"
        assert warning_alert.current_usage == 85.0
        assert "成長投資枠の使用率が85.0%" in warning_alert.message

    def test_check_growth_quota_alerts_critical(self, alert_system):
        """成長投資枠クリティカルアラートテスト"""
        quota_status = {
            "growth_investment": {
                "utilization_rate": 98.0,
                "used_amount": 2352000.0,
                "available_amount": 48000.0,
            }
        }

        alerts = alert_system._check_growth_quota_alerts(quota_status)

        critical_alerts = [a for a in alerts if a.type == AlertType.CRITICAL.value]
        assert len(critical_alerts) > 0

        critical_alert = critical_alerts[0]
        assert critical_alert.quota_type == "GROWTH"
        assert critical_alert.current_usage == 98.0
        assert "成長投資枠の使用率が98.0%" in critical_alert.message
        assert critical_alert.priority == AlertPriority.HIGH.value

    def test_check_accumulation_quota_alerts(self, alert_system):
        """つみたて投資枠アラートテスト"""
        quota_status = {
            "accumulation_investment": {
                "utilization_rate": 90.0,
                "used_amount": 360000.0,
                "available_amount": 40000.0,
            }
        }

        alerts = alert_system._check_accumulation_quota_alerts(quota_status)

        assert len(alerts) > 0
        warning_alerts = [a for a in alerts if a.type == AlertType.WARNING.value]
        assert len(warning_alerts) > 0

        warning_alert = warning_alerts[0]
        assert warning_alert.quota_type == "ACCUMULATION"
        assert warning_alert.current_usage == 90.0

    def test_generate_investment_opportunities(
        self, alert_system, sample_market_data, sample_quota_status
    ):
        """投資機会通知生成テスト"""
        opportunities = alert_system.generate_investment_opportunities(
            sample_market_data, sample_quota_status
        )

        assert isinstance(opportunities, list)

        for opportunity in opportunities:
            assert isinstance(opportunity, InvestmentOpportunity)
            assert opportunity.symbol != ""
            assert opportunity.symbol_name != ""
            assert opportunity.reason != ""
            assert opportunity.expected_return >= 0
            assert opportunity.risk_level in ["LOW", "MEDIUM", "HIGH"]
            assert opportunity.quota_recommendation in ["GROWTH", "ACCUMULATION"]
            assert opportunity.suggested_amount > 0
            assert opportunity.priority in [
                AlertPriority.HIGH.value,
                AlertPriority.MEDIUM.value,
                AlertPriority.LOW.value,
            ]

    def test_generate_growth_opportunities(self, alert_system, sample_market_data):
        """成長投資枠投資機会生成テスト"""
        quota_status = {"growth_investment": {"available_amount": 500000.0}}  # 十分な枠がある

        opportunities = alert_system._generate_growth_opportunities(
            sample_market_data, quota_status
        )

        assert isinstance(opportunities, list)

        for opportunity in opportunities:
            assert opportunity.quota_recommendation == "GROWTH"
            assert opportunity.suggested_amount > 0
            assert opportunity.suggested_amount <= 100000  # 10万円以下

    def test_generate_accumulation_opportunities(
        self, alert_system, sample_market_data
    ):
        """つみたて投資枠投資機会生成テスト"""
        quota_status = {
            "accumulation_investment": {"available_amount": 100000.0}  # 十分な枠がある
        }

        opportunities = alert_system._generate_accumulation_opportunities(
            sample_market_data, quota_status
        )

        assert isinstance(opportunities, list)

        for opportunity in opportunities:
            assert opportunity.quota_recommendation == "ACCUMULATION"
            assert opportunity.suggested_amount > 0
            assert opportunity.suggested_amount <= 20000  # 2万円以下

    def test_check_system_alerts(self, alert_system):
        """システムアラートチェックテスト"""
        system_status = {
            "system_health": "HEALTHY",
            "data_integrity": True,
            "response_time": 2.5,
        }

        alerts = alert_system.check_system_alerts(system_status)

        assert isinstance(alerts, list)
        # 正常なシステムではアラートは発生しない
        assert len(alerts) == 0

    def test_check_system_alerts_unhealthy(self, alert_system):
        """不健康なシステムアラートテスト"""
        system_status = {
            "system_health": "DEGRADED",
            "data_integrity": False,
            "response_time": 8.0,
        }

        alerts = alert_system.check_system_alerts(system_status)

        assert len(alerts) > 0

        for alert in alerts:
            assert isinstance(alert, SystemAlert)
            assert alert.type in [AlertType.WARNING.value, AlertType.CRITICAL.value]
            assert alert.component in ["SYSTEM", "DATA", "PERFORMANCE"]
            assert alert.severity in ["LOW", "MEDIUM", "HIGH"]
            assert isinstance(alert.action_required, bool)

    def test_send_notification_email(self, alert_system):
        """メール通知送信テスト"""
        alert = QuotaAlert(
            type=AlertType.WARNING.value,
            message="テストアラート",
            quota_type="GROWTH",
            current_usage=85.0,
            threshold=80.0,
            recommended_action="テスト推奨事項",
            priority=AlertPriority.MEDIUM.value,
            created_at=datetime.now().isoformat(),
        )

        with patch.object(
            alert_system, "_send_email_notification", return_value=True
        ) as mock_send:
            result = alert_system.send_notification(alert, "email")

            assert result == True
            mock_send.assert_called_once_with(alert)

    def test_send_notification_browser(self, alert_system):
        """ブラウザ通知送信テスト"""
        alert = QuotaAlert(
            type=AlertType.INFO.value,
            message="テストアラート",
            quota_type="ACCUMULATION",
            current_usage=50.0,
            threshold=80.0,
            recommended_action="テスト推奨事項",
            priority=AlertPriority.LOW.value,
            created_at=datetime.now().isoformat(),
        )

        with patch.object(
            alert_system, "_send_browser_notification", return_value=True
        ) as mock_send:
            result = alert_system.send_notification(alert, "browser")

            assert result == True
            mock_send.assert_called_once_with(alert)

    def test_send_notification_push(self, alert_system):
        """プッシュ通知送信テスト"""
        # プッシュ通知を有効にする
        alert_system.notification_settings["push"] = True

        alert = QuotaAlert(
            type=AlertType.CRITICAL.value,
            message="テストアラート",
            quota_type="GROWTH",
            current_usage=98.0,
            threshold=95.0,
            recommended_action="テスト推奨事項",
            priority=AlertPriority.HIGH.value,
            created_at=datetime.now().isoformat(),
        )

        with patch.object(
            alert_system, "_send_push_notification", return_value=True
        ) as mock_send:
            result = alert_system.send_notification(alert, "push")

            assert result == True
            mock_send.assert_called_once_with(alert)

    def test_send_notification_disabled(self, alert_system):
        """無効な通知タイプテスト"""
        alert = QuotaAlert(
            type=AlertType.WARNING.value,
            message="テストアラート",
            quota_type="GROWTH",
            current_usage=85.0,
            threshold=80.0,
            recommended_action="テスト推奨事項",
            priority=AlertPriority.MEDIUM.value,
            created_at=datetime.now().isoformat(),
        )

        # 無効な通知タイプ
        result = alert_system.send_notification(alert, "invalid_type")
        assert result == False

    def test_get_alert_summary(self, alert_system):
        """アラートサマリー取得テスト"""
        # サンプルアラートを追加
        alert1 = QuotaAlert(
            type=AlertType.CRITICAL.value,
            message="クリティカルアラート",
            quota_type="GROWTH",
            current_usage=98.0,
            threshold=95.0,
            recommended_action="緊急対応",
            priority=AlertPriority.HIGH.value,
            created_at=datetime.now().isoformat(),
        )

        alert2 = QuotaAlert(
            type=AlertType.WARNING.value,
            message="警告アラート",
            quota_type="ACCUMULATION",
            current_usage=85.0,
            threshold=80.0,
            recommended_action="注意事項",
            priority=AlertPriority.MEDIUM.value,
            created_at=datetime.now().isoformat(),
        )

        alert_system.alert_history = [alert1, alert2]

        summary = alert_system.get_alert_summary()

        assert summary["total_alerts"] == 2
        assert summary["critical_alerts"] == 1
        assert summary["warning_alerts"] == 1
        assert summary["info_alerts"] == 0
        assert summary["recent_alerts"] == 2
        assert summary["alert_rate"] > 0
        assert "last_updated" in summary

    def test_clear_old_alerts(self, alert_system):
        """古いアラート削除テスト"""
        # 古いアラートと新しいアラートを作成
        old_alert = QuotaAlert(
            type=AlertType.WARNING.value,
            message="古いアラート",
            quota_type="GROWTH",
            current_usage=80.0,
            threshold=80.0,
            recommended_action="古い推奨事項",
            priority=AlertPriority.MEDIUM.value,
            created_at=(datetime.now() - timedelta(days=35)).isoformat(),
        )

        new_alert = QuotaAlert(
            type=AlertType.INFO.value,
            message="新しいアラート",
            quota_type="ACCUMULATION",
            current_usage=50.0,
            threshold=80.0,
            recommended_action="新しい推奨事項",
            priority=AlertPriority.LOW.value,
            created_at=datetime.now().isoformat(),
        )

        alert_system.alert_history = [old_alert, new_alert]

        # 30日より古いアラートを削除
        deleted_count = alert_system.clear_old_alerts(days=30)

        assert deleted_count == 1
        assert len(alert_system.alert_history) == 1
        assert alert_system.alert_history[0].message == "新しいアラート"

    def test_update_alert_settings(self, alert_system):
        """アラート設定更新テスト"""
        new_settings = {
            "thresholds": {"growth_warning": 70.0, "growth_critical": 90.0},
            "notifications": {"email": False, "push": True},
        }

        result = alert_system.update_alert_settings(new_settings)

        assert result == True
        assert alert_system.alert_thresholds["growth_warning"] == 70.0
        assert alert_system.alert_thresholds["growth_critical"] == 90.0
        assert alert_system.notification_settings["email"] == False
        assert alert_system.notification_settings["push"] == True

    def test_alert_threshold_logic(self, alert_system):
        """アラート閾値ロジックテスト"""
        # 閾値未満の場合はアラートなし
        low_utilization_status = {
            "growth_investment": {
                "utilization_rate": 50.0,
                "used_amount": 1200000.0,
                "available_amount": 1200000.0,
            }
        }

        alerts = alert_system.check_quota_alerts(low_utilization_status)

        # 50%の使用率ではアラートは発生しない
        growth_alerts = [a for a in alerts if a.quota_type == "GROWTH"]
        assert len(growth_alerts) == 0

    def test_opportunity_generation_with_insufficient_quota(
        self, alert_system, sample_market_data
    ):
        """枠不足時の投資機会生成テスト"""
        quota_status = {
            "growth_investment": {"available_amount": 50000.0},  # 5万円（少ない）
            "accumulation_investment": {"available_amount": 5000.0},  # 5千円（少ない）
        }

        opportunities = alert_system.generate_investment_opportunities(
            sample_market_data, quota_status
        )

        # 枠が少ない場合は投資機会は生成されない
        assert len(opportunities) == 0

    def test_error_handling(self, alert_system):
        """エラーハンドリングテスト"""
        # 無効なデータ
        invalid_quota_status = None

        alerts = alert_system.check_quota_alerts(invalid_quota_status)
        assert alerts == []

        # 無効な市場データ
        invalid_market_data = None
        quota_status = {
            "growth_investment": {"available_amount": 100000.0},
            "accumulation_investment": {"available_amount": 10000.0},
        }

        opportunities = alert_system.generate_investment_opportunities(
            invalid_market_data, quota_status
        )
        assert opportunities == []

    def test_alert_priority_consistency(self, alert_system):
        """アラート優先度一貫性テスト"""
        quota_status = {
            "growth_investment": {
                "utilization_rate": 98.0,  # クリティカル
                "used_amount": 2352000.0,
                "available_amount": 48000.0,
            }
        }

        alerts = alert_system.check_quota_alerts(quota_status)

        critical_alerts = [a for a in alerts if a.type == AlertType.CRITICAL.value]
        assert len(critical_alerts) > 0

        for alert in critical_alerts:
            assert alert.priority == AlertPriority.HIGH.value
            assert alert.current_usage >= alert.threshold
