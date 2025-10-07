#!/usr/bin/env python3
"""
強化された投資判断システムのテスト
"""

from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from core.enhanced_investment_decision_system import (
    EnhancedInvestmentDecisionSystem,
    InvestmentDecisionResult,
)


class TestEnhancedInvestmentDecisionSystem:
    """強化された投資判断システムのテスト"""

    def setup_method(self):
        """テストのセットアップ"""
        self.config = {
            "integration_enabled": True,
            "auto_optimization": True,
            "real_time_monitoring": True,
            "total_capital": 1000000,
            "max_position_size": 0.1,
            "min_confidence_threshold": 0.7,
        }
        self.system = EnhancedInvestmentDecisionSystem(self.config)

    def test_initialization(self):
        """初期化のテスト"""
        assert self.system.integration_enabled is True
        assert self.system.auto_optimization is True
        assert self.system.real_time_monitoring is True
        assert len(self.system.decision_history) == 0
        assert isinstance(self.system.performance_metrics, dict)

    def test_generate_investment_decisions_empty_data(self):
        """空データでの投資判断生成テスト"""
        market_data = []
        positions = []
        predictions = []
        confidence_scores = []

        decisions = self.system.generate_investment_decisions(
            market_data, positions, predictions, confidence_scores
        )

        assert decisions == []

    def test_generate_investment_decisions_with_data(self):
        """データありでの投資判断生成テスト"""
        market_data = [
            {
                "symbol": "TEST",
                "close": 100,
                "volume": 1000000,
                "rsi": 30,
                "macd": 1.5,
                "sma_20": 95,
                "sma_50": 90,
                "volatility": 0.2,
                "trend": 0.1,
                "momentum": 0.05,
                "bollinger_upper": 105,
                "bollinger_lower": 85,
                "pe_ratio": 15,
                "revenue_growth": 0.1,
                "profit_margin": 0.15,
                "market_cap": 1000000000,
                "sector": "technology",
            }
        ]

        positions = []
        predictions = [110]
        confidence_scores = [0.8]

        decisions = self.system.generate_investment_decisions(
            market_data, positions, predictions, confidence_scores
        )

        assert isinstance(decisions, list)
        # 信頼度が高い場合のみ判断が生成される
        if decisions:
            assert isinstance(decisions[0], InvestmentDecisionResult)
            assert decisions[0].symbol == "TEST"
            assert decisions[0].confidence >= 0.7

    def test_generate_investment_decisions_with_positions(self):
        """既存ポジションありでの投資判断生成テスト"""
        market_data = [
            {
                "symbol": "TEST",
                "close": 100,
                "volume": 1000000,
                "rsi": 70,
                "macd": -1.5,
                "sma_20": 105,
                "sma_50": 110,
                "volatility": 0.2,
                "trend": -0.1,
                "momentum": -0.05,
                "bollinger_upper": 110,
                "bollinger_lower": 90,
                "pe_ratio": 25,
                "revenue_growth": -0.05,
                "profit_margin": 0.1,
                "market_cap": 1000000000,
                "sector": "technology",
            }
        ]

        positions = [
            {
                "symbol": "TEST",
                "quantity": 100,
                "average_price": 80,
                "current_price": 100,
                "pnl": 2000,
                "pnl_percentage": 25,
                "market_value": 10000,
                "cost_basis": 8000,
            }
        ]

        predictions = [95]
        confidence_scores = [0.8]

        decisions = self.system.generate_investment_decisions(
            market_data, positions, predictions, confidence_scores
        )

        assert isinstance(decisions, list)
        if decisions:
            assert isinstance(decisions[0], InvestmentDecisionResult)

    def test_preprocess_market_data(self):
        """市場データの前処理テスト"""
        raw_data = [
            {
                "symbol": "TEST",
                "close": "100.5",
                "volume": "1000000",
                "rsi": "30.5",
                "macd": "1.5",
                "sma_20": "95.0",
                "sma_50": "90.0",
                "volatility": "0.2",
                "trend": "0.1",
                "momentum": "0.05",
                "bollinger_upper": "105.0",
                "bollinger_lower": "85.0",
                "pe_ratio": "15.0",
                "revenue_growth": "0.1",
                "profit_margin": "0.15",
                "market_cap": "1000000000",
                "sector": "technology",
            }
        ]

        processed = self.system._preprocess_market_data(raw_data)

        assert len(processed) == 1
        assert processed[0]["symbol"] == "TEST"
        assert isinstance(processed[0]["close"], float)
        assert processed[0]["close"] == 100.5
        assert isinstance(processed[0]["volume"], float)
        assert isinstance(processed[0]["rsi"], float)

    def test_convert_positions(self):
        """ポジション情報の変換テスト"""
        raw_positions = [
            {
                "symbol": "TEST",
                "quantity": "100",
                "average_price": "80.5",
                "current_price": "100.0",
                "pnl": "2000.5",
                "pnl_percentage": "25.0",
                "market_value": "10000.0",
                "cost_basis": "8000.0",
            }
        ]

        converted = self.system._convert_positions(raw_positions)

        assert len(converted) == 1
        assert converted[0].symbol == "TEST"
        assert converted[0].current_quantity == 100
        assert converted[0].average_price == 80.5
        assert converted[0].current_price == 100.0
        assert converted[0].pnl == 2000.5
        assert converted[0].pnl_percentage == 25.0

    @patch("core.enhanced_investment_decision_system.EnsemblePredictionSystem")
    def test_generate_predictions(self, mock_ensemble):
        """予測の生成テスト"""
        # モックの設定
        mock_instance = MagicMock()
        mock_instance.run_ensemble_prediction.return_value = {
            "ensemble_prediction": [110, 105],
            "confidence": [0.8, 0.7],
        }
        mock_ensemble.return_value = mock_instance
        self.system.ensemble_prediction = mock_instance

        market_data = [{"symbol": "TEST1"}, {"symbol": "TEST2"}]

        result = self.system._generate_predictions(market_data)

        assert "predictions" in result
        assert "confidence_scores" in result
        assert len(result["predictions"]) == 2
        assert len(result["confidence_scores"]) == 2
        assert result["predictions"] == [110, 105]
        assert result["confidence_scores"] == [0.8, 0.7]

    @patch("core.enhanced_investment_decision_system.EnsemblePredictionSystem")
    def test_generate_predictions_error(self, mock_ensemble):
        """予測生成エラーのテスト"""
        # エラーを返すモック
        mock_instance = MagicMock()
        mock_instance.run_ensemble_prediction.return_value = {"error": "予測エラー"}
        mock_ensemble.return_value = mock_instance
        self.system.ensemble_prediction = mock_instance

        market_data = [{"symbol": "TEST"}]

        result = self.system._generate_predictions(market_data)

        assert result["predictions"] == []
        assert result["confidence_scores"] == []

    def test_create_investment_decision(self):
        """投資判断結果の作成テスト"""
        from core.clear_investment_actions import (
            InvestmentActionDetail,
            InvestmentAction,
            ActionPriority,
            DeadlineType,
        )

        action = InvestmentActionDetail(
            action=InvestmentAction.NEW_PURCHASE,
            symbol="TEST",
            current_price=100.0,
            target_price=110.0,
            quantity=100,
            total_amount=10000,
            priority=ActionPriority.MEDIUM,
            deadline=datetime.now() + timedelta(days=1),
            deadline_type=DeadlineType.THIS_WEEK,
            confidence=0.8,
            reason="新規購入",
            risk_level="MEDIUM",
            expected_return=1000,
            max_loss=500,
            technical_signals=["RSI過売り", "MACD上昇"],
            fundamental_factors=["売上高成長"],
            market_condition="bull_market",
        )

        market_data = [{"symbol": "TEST", "close": 100, "volatility": 0.2}]

        decision = self.system._create_investment_decision(action, market_data)

        assert decision is not None
        assert isinstance(decision, InvestmentDecisionResult)
        assert decision.symbol == "TEST"
        assert decision.action == "new_purchase"
        assert decision.quantity >= 0
        assert decision.confidence == 0.8

    def test_setup_deadline_management(self):
        """期限管理の設定テスト"""
        from core.enhanced_investment_decision_system import InvestmentDecisionResult

        decisions = [
            InvestmentDecisionResult(
                symbol="TEST1",
                action="new_purchase",
                quantity=100,
                target_price=110.0,
                current_price=100.0,
                total_amount=10000,
                confidence=0.8,
                priority="medium",
                deadline=datetime.now() + timedelta(days=1),
                reason="新規購入",
                risk_level="MEDIUM",
                expected_return=1000,
                max_loss=500,
                technical_signals=[],
                fundamental_factors=[],
                market_condition="normal",
                position_size_percentage=0.01,
                commission=10,
                slippage=5,
                net_amount=10015,
            )
        ]

        # 期限管理の設定
        self.system._setup_deadline_management(decisions)

        # 期限が追加されているかチェック
        assert len(self.system.deadline_manager.deadlines) == 1

    def test_handle_deadline_alert(self):
        """期限アラートの処理テスト"""
        from core.deadline_management import AlertInfo, AlertLevel

        # アラートの作成
        alert = AlertInfo(
            alert_id="test_alert",
            action_id="test_action",
            level=AlertLevel.WARNING,
            message="テストアラート",
            created_at=datetime.now(),
        )

        # アラートの処理
        self.system._handle_deadline_alert(alert)

        # エラーが発生しないことを確認
        assert True

    def test_record_decision_history(self):
        """判断履歴の記録テスト"""
        from core.enhanced_investment_decision_system import InvestmentDecisionResult

        decisions = [
            InvestmentDecisionResult(
                symbol="TEST",
                action="new_purchase",
                quantity=100,
                target_price=110.0,
                current_price=100.0,
                total_amount=10000,
                confidence=0.8,
                priority="medium",
                deadline=datetime.now() + timedelta(days=1),
                reason="新規購入",
                risk_level="MEDIUM",
                expected_return=1000,
                max_loss=500,
                technical_signals=[],
                fundamental_factors=[],
                market_condition="normal",
                position_size_percentage=0.01,
                commission=10,
                slippage=5,
                net_amount=10015,
            )
        ]

        # 履歴の記録
        self.system._record_decision_history(decisions)

        assert len(self.system.decision_history) == 1
        assert self.system.decision_history[0]["symbol"] == "TEST"
        assert self.system.decision_history[0]["action"] == "new_purchase"

    def test_analyze_performance(self):
        """パフォーマンス分析テスト"""
        from core.enhanced_investment_decision_system import InvestmentDecisionResult

        decisions = [
            InvestmentDecisionResult(
                symbol="TEST1",
                action="new_purchase",
                quantity=100,
                target_price=110.0,
                current_price=100.0,
                total_amount=10000,
                confidence=0.8,
                priority="high",
                deadline=datetime.now() + timedelta(days=1),
                reason="新規購入",
                risk_level="MEDIUM",
                expected_return=1000,
                max_loss=500,
                technical_signals=[],
                fundamental_factors=[],
                market_condition="normal",
                position_size_percentage=0.01,
                commission=10,
                slippage=5,
                net_amount=10015,
            ),
            InvestmentDecisionResult(
                symbol="TEST2",
                action="take_profit",
                quantity=50,
                target_price=105.0,
                current_price=100.0,
                total_amount=5000,
                confidence=0.9,
                priority="medium",
                deadline=datetime.now() + timedelta(days=2),
                reason="利確",
                risk_level="LOW",
                expected_return=250,
                max_loss=250,
                technical_signals=[],
                fundamental_factors=[],
                market_condition="normal",
                position_size_percentage=0.005,
                commission=5,
                slippage=2.5,
                net_amount=5007.5,
            ),
        ]

        # パフォーマンス分析
        self.system._analyze_performance(decisions)

        assert "total_decisions" in self.system.performance_metrics
        assert "total_amount" in self.system.performance_metrics
        assert "avg_confidence" in self.system.performance_metrics
        assert "high_priority_count" in self.system.performance_metrics
        assert "action_counts" in self.system.performance_metrics
        assert "total_risk" in self.system.performance_metrics
        assert "avg_expected_return" in self.system.performance_metrics

        assert self.system.performance_metrics["total_decisions"] == 2
        assert self.system.performance_metrics["total_amount"] == 15000
        assert self.system.performance_metrics["high_priority_count"] == 1
        assert self.system.performance_metrics["action_counts"]["new_purchase"] == 1
        assert self.system.performance_metrics["action_counts"]["take_profit"] == 1

    def test_get_decision_summary(self):
        """判断サマリーの取得テスト"""
        summary = self.system.get_decision_summary()

        assert "system_status" in summary
        assert "deadline_management" in summary
        assert "performance_metrics" in summary
        assert "decision_history_count" in summary
        assert "last_updated" in summary

        assert summary["system_status"]["integration_enabled"] is True
        assert summary["system_status"]["auto_optimization"] is True
        assert summary["system_status"]["real_time_monitoring"] is True

    def test_export_decisions_to_json(self, tmp_path):
        """投資判断のJSONエクスポートテスト"""
        from core.enhanced_investment_decision_system import InvestmentDecisionResult

        decisions = [
            InvestmentDecisionResult(
                symbol="TEST",
                action="new_purchase",
                quantity=100,
                target_price=110.0,
                current_price=100.0,
                total_amount=10000,
                confidence=0.8,
                priority="medium",
                deadline=datetime.now() + timedelta(days=1),
                reason="新規購入",
                risk_level="MEDIUM",
                expected_return=1000,
                max_loss=500,
                technical_signals=["RSI過売り"],
                fundamental_factors=["売上高成長"],
                market_condition="bull_market",
                position_size_percentage=0.01,
                commission=10,
                slippage=5,
                net_amount=10015,
            )
        ]

        filepath = tmp_path / "test_decisions.json"
        result = self.system.export_decisions_to_json(decisions, str(filepath))

        assert result is True
        assert filepath.exists()

        # JSONファイルの内容確認
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "decisions" in data
        assert "summary" in data
        assert "exported_at" in data
        assert len(data["decisions"]) == 1
        assert data["decisions"][0]["symbol"] == "TEST"
        assert data["decisions"][0]["action"] == "new_purchase"

    def test_cleanup_system(self):
        """システムのクリーンアップテスト"""
        # 履歴を追加
        self.system.decision_history = [{"test": "data"}] * 1500

        # クリーンアップ実行
        self.system.cleanup_system()

        # 履歴が500件に制限されているかチェック
        assert len(self.system.decision_history) == 500

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なデータでの判断生成
        decisions = self.system.generate_investment_decisions(None, None, None, None)

        assert decisions == []

        # 無効なパラメータでのJSONエクスポート
        result = self.system.export_decisions_to_json([], "")
        assert result is False
