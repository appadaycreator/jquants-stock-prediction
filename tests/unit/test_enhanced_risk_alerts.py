#!/usr/bin/env python3
"""
enhanced_risk_alerts.py のテスト
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch
import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.enhanced_risk_alerts import (
    EnhancedRiskAlerts,
    AlertSeverity,
    AlertType,
    RiskAlert,
    AlertSummary,
)


class TestEnhancedRiskAlerts:
    """EnhancedRiskAlerts のテストクラス"""

    def setup_method(self):
        """テスト前の準備"""
        self.risk_alerts = EnhancedRiskAlerts()
        self.sample_stock_data = pd.DataFrame(
            {
                'Date': pd.date_range('2023-01-01', periods=100, freq='D'),
                'Close': np.random.normal(100, 10, 100).cumsum(),
                'Volume': np.random.randint(1000, 10000, 100),
            }
        )

    def test_initialization(self):
        """初期化テスト"""
        assert self.risk_alerts is not None
        assert self.risk_alerts.config is not None
        assert self.risk_alerts.alert_history == []

    def test_get_default_config(self):
        """デフォルト設定テスト"""
        config = self.risk_alerts._get_default_config()
        assert "alert_settings" in config
        assert "notification_settings" in config
        assert "severity_colors" in config
        assert "severity_icons" in config

    def test_generate_comprehensive_alerts_empty_portfolio(self):
        """空のポートフォリオでのアラート生成テスト"""
        alerts = self.risk_alerts.generate_comprehensive_alerts({})
        assert isinstance(alerts, list)
        assert len(alerts) == 0

    def test_generate_comprehensive_alerts_with_data(self):
        """データ付きポートフォリオでのアラート生成テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 100.0,
                "position_size": 100,
                "account_balance": 1000000.0,
            }
        }

        alerts = self.risk_alerts.generate_comprehensive_alerts(portfolio_data)
        assert isinstance(alerts, list)

    def test_get_alert_summary_empty_history(self):
        """空の履歴でのアラートサマリー取得テスト"""
        summary = self.risk_alerts.get_alert_summary()
        assert isinstance(summary, AlertSummary)
        assert summary.total_alerts == 0
        assert summary.critical_alerts == 0
        assert summary.warning_alerts == 0
        assert summary.info_alerts == 0
        assert summary.emergency_alerts == 0

    def test_get_alert_summary_with_alerts(self):
        """アラート履歴付きでのサマリー取得テスト"""
        # テスト用アラートを追加
        test_alert = RiskAlert(
            id="test_alert_1",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨",
            action_required=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata={},
            color_code="#F44336",
            icon="error",
        )

        self.risk_alerts.alert_history.append(test_alert)
        summary = self.risk_alerts.get_alert_summary()

        assert summary.total_alerts >= 1
        assert summary.critical_alerts >= 1

    def test_get_personalized_recommendations_low_risk_tolerance(self):
        """低リスク許容度での個人化推奨事項テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 100.0,
                "position_size": 100,
                "account_balance": 1000000.0,
            }
        }

        recommendations = self.risk_alerts.get_personalized_recommendations(
            portfolio_data, "low"
        )
        assert isinstance(recommendations, list)

    def test_get_personalized_recommendations_high_risk_tolerance(self):
        """高リスク許容度での個人化推奨事項テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 100.0,
                "position_size": 100,
                "account_balance": 1000000.0,
            }
        }

        recommendations = self.risk_alerts.get_personalized_recommendations(
            portfolio_data, "high"
        )
        assert isinstance(recommendations, list)

    def test_create_alert_notification(self):
        """アラート通知作成テスト"""
        test_alert = RiskAlert(
            id="test_alert_1",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨",
            action_required=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata={},
            color_code="#F44336",
            icon="error",
        )

        notification = self.risk_alerts.create_alert_notification(test_alert)
        assert notification["success"] is True
        assert "data" in notification

    def test_create_alert_notification_with_methods(self):
        """指定メソッドでのアラート通知作成テスト"""
        test_alert = RiskAlert(
            id="test_alert_1",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨",
            action_required=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata={},
            color_code="#F44336",
            icon="error",
        )

        notification = self.risk_alerts.create_alert_notification(
            test_alert, ["email", "push"]
        )
        assert notification["success"] is True
        assert notification["data"]["notification_methods"] == ["email", "push"]

    def test_generate_stock_alerts_empty_data(self):
        """空データでの銘柄アラート生成テスト"""
        alerts = self.risk_alerts._generate_stock_alerts("7203", {})
        assert isinstance(alerts, list)
        assert len(alerts) == 0

    def test_generate_stock_alerts_with_data(self):
        """データ付きでの銘柄アラート生成テスト"""
        data = {
            "stock_data": self.sample_stock_data,
            "current_price": 100.0,
            "position_size": 100,
            "account_balance": 1000000.0,
        }

        alerts = self.risk_alerts._generate_stock_alerts("7203", data)
        assert isinstance(alerts, list)

    def test_generate_portfolio_alerts_empty_portfolio(self):
        """空ポートフォリオでのポートフォリオアラート生成テスト"""
        alerts = self.risk_alerts._generate_portfolio_alerts({}, None)
        assert isinstance(alerts, list)

    def test_generate_portfolio_alerts_with_data(self):
        """データ付きでのポートフォリオアラート生成テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 100.0,
                "position_size": 100,
                "account_balance": 1000000.0,
            }
        }

        alerts = self.risk_alerts._generate_portfolio_alerts(portfolio_data, None)
        assert isinstance(alerts, list)

    def test_generate_market_alerts_empty_data(self):
        """空データでの市場アラート生成テスト"""
        alerts = self.risk_alerts._generate_market_alerts({})
        assert isinstance(alerts, list)

    def test_generate_market_alerts_with_data(self):
        """データ付きでの市場アラート生成テスト"""
        market_data = {"volatility": 0.4, "market_stress": 0.3}

        alerts = self.risk_alerts._generate_market_alerts(market_data)
        assert isinstance(alerts, list)

    def test_create_alert(self):
        """アラート作成テスト"""
        alert = self.risk_alerts._create_alert(
            symbol="7203",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨",
        )

        assert isinstance(alert, RiskAlert)
        assert alert.symbol == "7203"
        assert alert.type == AlertType.HIGH_RISK
        assert alert.severity == AlertSeverity.CRITICAL

    def test_deduplicate_and_prioritize_alerts(self):
        """アラート重複除去・優先度調整テスト"""
        alerts = [
            RiskAlert(
                id="alert_1",
                type=AlertType.HIGH_RISK,
                severity=AlertSeverity.CRITICAL,
                symbol="7203",
                title="アラート1",
                message="メッセージ1",
                recommendation="推奨1",
                action_required=True,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),
                metadata={},
                color_code="#F44336",
                icon="error",
            ),
            RiskAlert(
                id="alert_2",
                type=AlertType.HIGH_RISK,
                severity=AlertSeverity.WARNING,
                symbol="7203",
                title="アラート2",
                message="メッセージ2",
                recommendation="推奨2",
                action_required=False,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),
                metadata={},
                color_code="#FF9800",
                icon="warning",
            ),
        ]

        unique_alerts = self.risk_alerts._deduplicate_and_prioritize_alerts(alerts)
        assert isinstance(unique_alerts, list)
        assert len(unique_alerts) <= len(alerts)

    def test_get_alert_priority_score(self):
        """アラート優先度スコア計算テスト"""
        alert = RiskAlert(
            id="test_alert",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨",
            action_required=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata={},
            color_code="#F44336",
            icon="error",
        )

        score = self.risk_alerts._get_alert_priority_score(alert)
        assert isinstance(score, int)
        assert score > 0

    def test_cleanup_old_alerts(self):
        """古いアラート削除テスト"""
        # 古いアラートを追加
        old_alert = RiskAlert(
            id="old_alert",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="古いアラート",
            message="古いメッセージ",
            recommendation="古い推奨",
            action_required=True,
            created_at=datetime.now() - timedelta(days=35),
            expires_at=datetime.now() - timedelta(days=28),
            metadata={},
            color_code="#F44336",
            icon="error",
        )

        self.risk_alerts.alert_history.append(old_alert)
        initial_count = len(self.risk_alerts.alert_history)

        self.risk_alerts._cleanup_old_alerts()

        # 古いアラートが削除されていることを確認
        assert len(self.risk_alerts.alert_history) < initial_count

    def test_format_alert_for_display(self):
        """表示用アラートフォーマットテスト"""
        alert = RiskAlert(
            id="test_alert",
            type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            symbol="7203",
            title="テストアラート",
            message="テストメッセージ",
            recommendation="テスト推奨",
            action_required=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata={"test": "value"},
            color_code="#F44336",
            icon="error",
        )

        formatted = self.risk_alerts._format_alert_for_display(alert)
        assert isinstance(formatted, dict)
        assert "id" in formatted
        assert "type" in formatted
        assert "severity" in formatted
        assert "symbol" in formatted

    def test_get_risk_tolerance_multiplier(self):
        """リスク許容度倍率取得テスト"""
        assert self.risk_alerts._get_risk_tolerance_multiplier("low") == 0.5
        assert self.risk_alerts._get_risk_tolerance_multiplier("medium") == 1.0
        assert self.risk_alerts._get_risk_tolerance_multiplier("high") == 1.5
        assert self.risk_alerts._get_risk_tolerance_multiplier("unknown") == 1.0

    def test_analyze_portfolio_risk_empty_portfolio(self):
        """空ポートフォリオでのリスク分析テスト"""
        analysis = self.risk_alerts._analyze_portfolio_risk({})
        assert isinstance(analysis, dict)
        assert analysis["high_risk_count"] == 0
        assert analysis["high_risk_ratio"] == 0.0
        assert analysis["diversification_score"] == 1.0
        assert analysis["max_position_ratio"] == 0.0

    def test_analyze_portfolio_risk_with_data(self):
        """データ付きでのポートフォリオリスク分析テスト"""
        portfolio_data = {
            "7203": {
                "stock_data": self.sample_stock_data,
                "current_price": 100.0,
                "position_size": 100,
                "account_balance": 1000000.0,
            }
        }

        analysis = self.risk_alerts._analyze_portfolio_risk(portfolio_data)
        assert isinstance(analysis, dict)
        assert "high_risk_count" in analysis
        assert "high_risk_ratio" in analysis
        assert "diversification_score" in analysis
        assert "max_position_ratio" in analysis

    def test_calculate_volatility(self):
        """ボラティリティ計算テスト"""
        volatility = self.risk_alerts._calculate_volatility(self.sample_stock_data)
        assert isinstance(volatility, float)
        assert volatility >= 0

    def test_calculate_volatility_empty_data(self):
        """空データでのボラティリティ計算テスト"""
        empty_data = pd.DataFrame()
        volatility = self.risk_alerts._calculate_volatility(empty_data)
        assert volatility == 0.2  # デフォルト値

    def test_calculate_var_95(self):
        """95% VaR計算テスト"""
        var_95 = self.risk_alerts._calculate_var_95(self.sample_stock_data)
        assert isinstance(var_95, float)
        assert var_95 >= 0

    def test_calculate_var_95_empty_data(self):
        """空データでの95% VaR計算テスト"""
        empty_data = pd.DataFrame()
        var_95 = self.risk_alerts._calculate_var_95(empty_data)
        assert var_95 == 0.05  # デフォルト値

    def test_calculate_max_drawdown(self):
        """最大ドローダウン計算テスト"""
        drawdown = self.risk_alerts._calculate_max_drawdown(self.sample_stock_data)
        assert isinstance(drawdown, float)
        assert drawdown >= 0

    def test_calculate_max_drawdown_empty_data(self):
        """空データでの最大ドローダウン計算テスト"""
        empty_data = pd.DataFrame()
        drawdown = self.risk_alerts._calculate_max_drawdown(empty_data)
        assert drawdown == 0.0

    def test_calculate_risk_score(self):
        """リスクスコア計算テスト"""
        risk_score = self.risk_alerts._calculate_risk_score(0.2, 0.05, 0.1)
        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 100

    def test_determine_risk_level(self):
        """リスクレベル決定テスト"""
        from core.dynamic_risk_management import RiskLevel

        assert self.risk_alerts._determine_risk_level(20) == RiskLevel.LOW
        assert self.risk_alerts._determine_risk_level(50) == RiskLevel.MEDIUM
        assert self.risk_alerts._determine_risk_level(80) == RiskLevel.HIGH

    def test_error_handling_in_generate_comprehensive_alerts(self):
        """包括的アラート生成でのエラーハンドリングテスト"""
        # 無効なデータでテスト
        invalid_data = {"invalid": None}
        alerts = self.risk_alerts.generate_comprehensive_alerts(invalid_data)
        assert isinstance(alerts, list)

    def test_error_handling_in_get_alert_summary(self):
        """アラートサマリー取得でのエラーハンドリングテスト"""
        # 無効なアラート履歴でテスト
        self.risk_alerts.alert_history = [None]
        summary = self.risk_alerts.get_alert_summary()
        assert isinstance(summary, AlertSummary)

    def test_error_handling_in_personalized_recommendations(self):
        """個人化推奨事項でのエラーハンドリングテスト"""
        # 無効なデータでテスト
        recommendations = self.risk_alerts.get_personalized_recommendations(
            {}, "invalid"
        )
        assert isinstance(recommendations, list)

    def test_error_handling_in_create_alert_notification(self):
        """アラート通知作成でのエラーハンドリングテスト"""
        # 無効なアラートでテスト
        with patch.object(self.risk_alerts, 'logger') as mock_logger:
            result = self.risk_alerts.create_alert_notification(None)
            assert result["success"] is False
            assert "error" in result

    def test_edge_cases_in_volatility_calculation(self):
        """ボラティリティ計算のエッジケーステスト"""
        # 単一データポイント
        single_data = pd.DataFrame({'Close': [100]})
        volatility = self.risk_alerts._calculate_volatility(single_data)
        assert volatility == 0.2  # デフォルト値

    def test_edge_cases_in_var_calculation(self):
        """VaR計算のエッジケーステスト"""
        # 単一データポイント
        single_data = pd.DataFrame({'Close': [100]})
        var_95 = self.risk_alerts._calculate_var_95(single_data)
        assert var_95 == 0.05  # デフォルト値

    def test_edge_cases_in_drawdown_calculation(self):
        """ドローダウン計算のエッジケーステスト"""
        # 単一データポイント
        single_data = pd.DataFrame({'Close': [100]})
        drawdown = self.risk_alerts._calculate_max_drawdown(single_data)
        assert drawdown == 0.0

    def test_performance_with_large_dataset(self):
        """大規模データセットでのパフォーマンステスト"""
        # 大規模データセットを作成
        large_data = pd.DataFrame(
            {
                'Date': pd.date_range('2020-01-01', periods=1000, freq='D'),
                'Close': np.random.normal(100, 10, 1000).cumsum(),
                'Volume': np.random.randint(1000, 10000, 1000),
            }
        )

        portfolio_data = {
            "7203": {
                "stock_data": large_data,
                "current_price": 100.0,
                "position_size": 100,
                "account_balance": 1000000.0,
            }
        }

        # パフォーマンステスト（タイムアウトなし）
        alerts = self.risk_alerts.generate_comprehensive_alerts(portfolio_data)
        assert isinstance(alerts, list)

    def test_memory_usage_optimization(self):
        """メモリ使用量最適化テスト"""
        # 大量のアラート履歴を作成（古いアラートを含む）
        for i in range(1000):
            # 古いアラートを作成（35日前）
            old_alert = RiskAlert(
                id=f"old_alert_{i}",
                type=AlertType.HIGH_RISK,
                severity=AlertSeverity.CRITICAL,
                symbol="7203",
                title=f"古いアラート{i}",
                message=f"古いメッセージ{i}",
                recommendation=f"古い推奨{i}",
                action_required=True,
                created_at=datetime.now() - timedelta(days=35),
                expires_at=datetime.now() - timedelta(days=28),
                metadata={},
                color_code="#F44336",
                icon="error",
            )
            self.risk_alerts.alert_history.append(old_alert)

        # 古いアラートの削除を実行
        self.risk_alerts._cleanup_old_alerts()

        # 古いアラートが削除されていることを確認
        assert len(self.risk_alerts.alert_history) == 0
