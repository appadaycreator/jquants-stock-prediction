"""
強化された推奨事項生成システムのテスト
"""

import pytest
import numpy as np
import sys
import os

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.enhanced_recommendation_system import (
    EnhancedRecommendationSystem,
    PortfolioRecommendation,
    Recommendation,
    RecommendationType,
    PriorityLevel,
    RiskLevel,
)


class TestEnhancedRecommendationSystem:
    """強化された推奨事項生成システムのテスト"""

    @pytest.fixture
    def recommendation_system(self):
        """推奨事項生成システムのフィクスチャ"""
        config = {
            "min_confidence": 0.7,
            "max_risk_per_trade": 0.02,
            "target_sharpe_ratio": 1.5,
            "rebalancing_threshold": 0.05,
            "diversification_threshold": 0.6,
            "correlation_threshold": 0.7,
            "volatility_threshold": 0.3,
            "liquidity_threshold": 1000000,
            "max_position_weight": 0.2,
            "min_position_weight": 0.01,
        }
        return EnhancedRecommendationSystem(config)

    @pytest.fixture
    def sample_portfolio_data(self):
        """サンプルポートフォリオデータ"""
        return {
            "total_value": 1000000,
            "positions": {
                "AAPL": {
                    "weight": 0.3,
                    "current_price": 150.0,
                    "quantity": 2000,
                    "unrealized_pnl": 10000,
                    "cost_basis": 140000,
                    "volatility": 0.25,
                    "confidence": 0.8,
                    "sector": "Technology",
                    "expected_return": 0.08,
                },
                "GOOGL": {
                    "weight": 0.25,
                    "current_price": 2800.0,
                    "quantity": 89,
                    "unrealized_pnl": 5000,
                    "cost_basis": 245000,
                    "volatility": 0.22,
                    "confidence": 0.75,
                    "sector": "Technology",
                    "expected_return": 0.09,
                },
                "MSFT": {
                    "weight": 0.2,
                    "current_price": 300.0,
                    "quantity": 667,
                    "unrealized_pnl": -2000,
                    "cost_basis": 200000,
                    "volatility": 0.18,
                    "confidence": 0.85,
                    "sector": "Technology",
                    "expected_return": 0.07,
                },
                "AMZN": {
                    "weight": 0.15,
                    "current_price": 3300.0,
                    "quantity": 45,
                    "unrealized_pnl": 3000,
                    "cost_basis": 150000,
                    "volatility": 0.28,
                    "confidence": 0.7,
                    "sector": "Consumer Discretionary",
                    "expected_return": 0.06,
                },
                "TSLA": {
                    "weight": 0.1,
                    "current_price": 210.0,
                    "quantity": 476,
                    "unrealized_pnl": -5000,
                    "cost_basis": 100000,
                    "volatility": 0.35,
                    "confidence": 0.65,
                    "sector": "Consumer Discretionary",
                    "expected_return": 0.05,
                },
            },
            "weights": {
                "AAPL": 0.3,
                "GOOGL": 0.25,
                "MSFT": 0.2,
                "AMZN": 0.15,
                "TSLA": 0.1,
            },
        }

    @pytest.fixture
    def sample_market_conditions(self):
        """サンプル市場条件"""
        return {
            "volatility_regime": "NORMAL",
            "trend_direction": "BULL",
            "liquidity_level": "HIGH",
            "market_stress": 0.3,
            "correlation_level": 0.4,
        }

    @pytest.fixture
    def sample_optimization_results(self):
        """サンプル最適化結果"""
        return {
            "weights": {
                "AAPL": 0.35,
                "GOOGL": 0.2,
                "MSFT": 0.25,
                "AMZN": 0.1,
                "TSLA": 0.1,
            },
            "expected_return": 0.08,
            "volatility": 0.22,
            "sharpe_ratio": 1.8,
            "diversification_score": 0.75,
            "rebalancing_needed": True,
        }

    @pytest.fixture
    def sample_risk_metrics(self):
        """サンプルリスクメトリクス"""
        return {
            "volatility": 0.22,
            "max_drawdown": 0.12,
            "var_95": -0.03,
            "sharpe_ratio": 1.8,
            "sortino_ratio": 2.1,
            "calmar_ratio": 1.5,
        }

    @pytest.fixture
    def sample_diversification_metrics(self):
        """サンプル分散投資メトリクス"""
        return {
            "overall_score": 0.75,
            "sector_diversification": 0.7,
            "correlation_diversification": 0.8,
            "concentration_risk": 0.3,
            "geographic_diversification": 0.6,
            "market_cap_diversification": 0.7,
            "liquidity_diversification": 0.8,
            "risk_contribution_diversification": 0.75,
            "entropy_score": 0.8,
            "herfindahl_index": 0.25,
            "effective_number_of_stocks": 8.5,
            "diversification_ratio": 1.2,
        }

    def test_initialization(self, recommendation_system):
        """初期化テスト"""
        assert recommendation_system.min_confidence == 0.7
        assert recommendation_system.max_risk_per_trade == 0.02
        assert recommendation_system.target_sharpe_ratio == 1.5
        assert recommendation_system.rebalancing_threshold == 0.05
        assert recommendation_system.diversification_threshold == 0.6
        assert recommendation_system.correlation_threshold == 0.7
        assert recommendation_system.volatility_threshold == 0.3
        assert recommendation_system.liquidity_threshold == 1000000
        assert recommendation_system.max_position_weight == 0.2
        assert recommendation_system.min_position_weight == 0.01

    def test_get_default_config(self, recommendation_system):
        """デフォルト設定取得テスト"""
        config = recommendation_system._get_default_config()
        assert "min_confidence" in config
        assert "max_risk_per_trade" in config
        assert "target_sharpe_ratio" in config
        assert "rebalancing_threshold" in config
        assert "diversification_threshold" in config
        assert "correlation_threshold" in config
        assert "volatility_threshold" in config
        assert "liquidity_threshold" in config
        assert "max_position_weight" in config
        assert "min_position_weight" in config

    def test_assess_portfolio_overall(
        self,
        recommendation_system,
        sample_portfolio_data,
        sample_market_conditions,
        sample_optimization_results,
        sample_risk_metrics,
        sample_diversification_metrics,
    ):
        """ポートフォリオ全体評価テスト"""
        overall_assessment = recommendation_system._assess_portfolio_overall(
            sample_portfolio_data,
            sample_market_conditions,
            sample_optimization_results,
            sample_risk_metrics,
            sample_diversification_metrics,
        )

        assert isinstance(overall_assessment, dict)
        assert "overall_score" in overall_assessment
        assert "grade" in overall_assessment
        assert "status" in overall_assessment
        assert "performance_metrics" in overall_assessment
        assert "diversification_metrics" in overall_assessment
        assert "market_conditions" in overall_assessment
        assert "portfolio_summary" in overall_assessment

        assert isinstance(overall_assessment["overall_score"], float)
        assert isinstance(overall_assessment["grade"], str)
        assert isinstance(overall_assessment["status"], str)
        assert 0.0 <= overall_assessment["overall_score"] <= 1.0
        assert overall_assessment["grade"] in [
            "A+",
            "A",
            "B+",
            "B",
            "C+",
            "C",
            "D",
            "F",
        ]
        assert overall_assessment["status"] in [
            "EXCELLENT",
            "VERY_GOOD",
            "GOOD",
            "FAIR",
            "NEEDS_IMPROVEMENT",
            "POOR",
        ]

        # パフォーマンスメトリクスの確認
        performance_metrics = overall_assessment["performance_metrics"]
        assert "current_sharpe_ratio" in performance_metrics
        assert "target_sharpe_ratio" in performance_metrics
        assert "sharpe_performance" in performance_metrics
        assert "volatility" in performance_metrics
        assert "max_drawdown" in performance_metrics
        assert "var_95" in performance_metrics

        # 分散投資メトリクスの確認
        diversification_metrics = overall_assessment["diversification_metrics"]
        assert "diversification_score" in diversification_metrics
        assert "effective_stocks" in diversification_metrics
        assert "sector_diversification" in diversification_metrics
        assert "correlation_diversification" in diversification_metrics

        # 市場条件の確認
        market_conditions = overall_assessment["market_conditions"]
        assert "market_stress" in market_conditions
        assert "volatility_regime" in market_conditions
        assert "trend_direction" in market_conditions
        assert "liquidity_level" in market_conditions

        # ポートフォリオサマリーの確認
        portfolio_summary = overall_assessment["portfolio_summary"]
        assert "total_value" in portfolio_summary
        assert "num_positions" in portfolio_summary
        assert "avg_position_size" in portfolio_summary

    def test_generate_individual_recommendations(
        self,
        recommendation_system,
        sample_portfolio_data,
        sample_market_conditions,
        sample_optimization_results,
        sample_risk_metrics,
    ):
        """個別推奨事項生成テスト"""
        recommendations = recommendation_system._generate_individual_recommendations(
            sample_portfolio_data,
            sample_market_conditions,
            sample_optimization_results,
            sample_risk_metrics,
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) == 5  # 5銘柄

        for recommendation in recommendations:
            assert isinstance(recommendation, Recommendation)
            assert hasattr(recommendation, "symbol")
            assert hasattr(recommendation, "recommendation_type")
            assert hasattr(recommendation, "priority")
            assert hasattr(recommendation, "confidence")
            assert hasattr(recommendation, "expected_return")
            assert hasattr(recommendation, "risk_level")
            assert hasattr(recommendation, "quantity")
            assert hasattr(recommendation, "price")
            assert hasattr(recommendation, "value")
            assert hasattr(recommendation, "reasoning")
            assert hasattr(recommendation, "conditions")
            assert hasattr(recommendation, "timeframe")
            assert hasattr(recommendation, "risk_amount")
            assert hasattr(recommendation, "stop_loss")
            assert hasattr(recommendation, "take_profit")
            assert hasattr(recommendation, "timestamp")

            assert isinstance(recommendation.symbol, str)
            assert isinstance(recommendation.recommendation_type, RecommendationType)
            assert isinstance(recommendation.priority, PriorityLevel)
            assert isinstance(recommendation.confidence, float)
            assert isinstance(recommendation.expected_return, float)
            assert isinstance(recommendation.risk_level, RiskLevel)
            assert isinstance(recommendation.quantity, int)
            assert isinstance(recommendation.price, float)
            assert isinstance(recommendation.value, float)
            assert isinstance(recommendation.reasoning, list)
            assert isinstance(recommendation.conditions, list)
            assert isinstance(recommendation.timeframe, str)
            assert isinstance(recommendation.risk_amount, float)
            assert recommendation.stop_loss is None or isinstance(
                recommendation.stop_loss, float
            )
            assert recommendation.take_profit is None or isinstance(
                recommendation.take_profit, float
            )
            assert isinstance(recommendation.timestamp, str)

            assert 0.0 <= recommendation.confidence <= 1.0
            assert np.isfinite(recommendation.expected_return)
            assert recommendation.quantity >= 0
            assert recommendation.price > 0.0
            assert recommendation.value >= 0.0
            assert recommendation.risk_amount >= 0.0
            assert len(recommendation.reasoning) > 0
            assert len(recommendation.conditions) > 0
            assert recommendation.timeframe in [
                "即座実行",
                "今週中",
                "今月中",
                "来四半期",
            ]

    def test_determine_recommendation_type(self, recommendation_system):
        """推奨タイプ決定テスト"""
        # 買い増しケース
        position_data = {"unrealized_pnl": 5000, "cost_basis": 100000}
        assert (
            recommendation_system._determine_recommendation_type(0.1, position_data)
            == RecommendationType.BUY_MORE
        )

        # 売却ケース
        assert (
            recommendation_system._determine_recommendation_type(-0.1, position_data)
            == RecommendationType.SELL
        )

        # 利確ケース
        position_data_profit = {"unrealized_pnl": 15000, "cost_basis": 100000}
        assert (
            recommendation_system._determine_recommendation_type(
                0.0, position_data_profit
            )
            == RecommendationType.TAKE_PROFIT
        )

        # 損切りケース
        position_data_loss = {"unrealized_pnl": -8000, "cost_basis": 100000}
        assert (
            recommendation_system._determine_recommendation_type(
                0.0, position_data_loss
            )
            == RecommendationType.STOP_LOSS
        )

        # ホールドケース
        position_data_hold = {"unrealized_pnl": 2000, "cost_basis": 100000}
        assert (
            recommendation_system._determine_recommendation_type(
                0.0, position_data_hold
            )
            == RecommendationType.HOLD
        )

    def test_calculate_recommendation_confidence(
        self, recommendation_system, sample_market_conditions, sample_risk_metrics
    ):
        """推奨信頼度計算テスト"""
        position_data = {"confidence": 0.8, "volatility": 0.2}

        confidence = recommendation_system._calculate_recommendation_confidence(
            position_data, sample_market_conditions, sample_risk_metrics
        )

        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        assert np.isfinite(confidence)

    def test_determine_priority(self, recommendation_system):
        """優先度決定テスト"""
        # 高優先度ケース
        assert (
            recommendation_system._determine_priority(0.15, 0.8, {})
            == PriorityLevel.HIGH
        )

        # 中優先度ケース
        assert (
            recommendation_system._determine_priority(0.08, 0.7, {})
            == PriorityLevel.MEDIUM
        )

        # 低優先度ケース
        assert (
            recommendation_system._determine_priority(0.03, 0.5, {})
            == PriorityLevel.LOW
        )

    def test_calculate_expected_return(
        self, recommendation_system, sample_market_conditions
    ):
        """期待リターン計算テスト"""
        position_data = {"expected_return": 0.08}

        expected_return = recommendation_system._calculate_expected_return(
            position_data, sample_market_conditions
        )

        assert isinstance(expected_return, float)
        assert np.isfinite(expected_return)
        assert expected_return > 0.0

    def test_determine_risk_level(self, recommendation_system, sample_risk_metrics):
        """リスクレベル判定テスト"""
        position_data_low = {"volatility": 0.1}
        position_data_medium = {"volatility": 0.2}
        position_data_high = {"volatility": 0.3}
        position_data_very_high = {"volatility": 0.4}

        assert (
            recommendation_system._determine_risk_level(
                position_data_low, sample_risk_metrics
            )
            == RiskLevel.LOW
        )
        assert (
            recommendation_system._determine_risk_level(
                position_data_medium, sample_risk_metrics
            )
            == RiskLevel.MEDIUM
        )
        assert (
            recommendation_system._determine_risk_level(
                position_data_high, sample_risk_metrics
            )
            == RiskLevel.HIGH
        )
        assert (
            recommendation_system._determine_risk_level(
                position_data_very_high, sample_risk_metrics
            )
            == RiskLevel.VERY_HIGH
        )

    def test_calculate_recommended_quantity(self, recommendation_system):
        """推奨数量計算テスト"""
        quantity = recommendation_system._calculate_recommended_quantity(
            "AAPL", 150.0, 0.35, 1000000
        )

        assert isinstance(quantity, int)
        assert quantity >= 0

    def test_generate_reasoning(self, recommendation_system, sample_market_conditions):
        """推奨理由生成テスト"""
        position_data = {"volatility": 0.2}

        reasoning = recommendation_system._generate_reasoning(
            RecommendationType.BUY_MORE, 0.1, position_data, sample_market_conditions
        )

        assert isinstance(reasoning, list)
        assert len(reasoning) > 0
        assert all(isinstance(reason, str) for reason in reasoning)

    def test_generate_conditions(self, recommendation_system, sample_market_conditions):
        """条件生成テスト"""
        position_data = {"volatility": 0.2}

        conditions = recommendation_system._generate_conditions(
            RecommendationType.BUY, sample_market_conditions, position_data
        )

        assert isinstance(conditions, list)
        assert len(conditions) > 0
        assert all(isinstance(condition, str) for condition in conditions)

    def test_determine_timeframe(self, recommendation_system):
        """タイムフレーム決定テスト"""
        assert (
            recommendation_system._determine_timeframe(
                RecommendationType.STOP_LOSS, PriorityLevel.HIGH
            )
            == "即座実行"
        )
        assert (
            recommendation_system._determine_timeframe(
                RecommendationType.TAKE_PROFIT, PriorityLevel.HIGH
            )
            == "即座実行"
        )
        assert (
            recommendation_system._determine_timeframe(
                RecommendationType.BUY_MORE, PriorityLevel.HIGH
            )
            == "今週中"
        )
        assert (
            recommendation_system._determine_timeframe(
                RecommendationType.BUY, PriorityLevel.MEDIUM
            )
            == "今月中"
        )
        assert (
            recommendation_system._determine_timeframe(
                RecommendationType.HOLD, PriorityLevel.LOW
            )
            == "来四半期"
        )

    def test_calculate_stop_take_prices(self, recommendation_system):
        """損切り・利確価格計算テスト"""
        position_data = {"volatility": 0.2}

        stop_loss, take_profit = recommendation_system._calculate_stop_take_prices(
            150.0, RecommendationType.BUY, position_data
        )

        assert stop_loss is None or isinstance(stop_loss, float)
        assert take_profit is None or isinstance(take_profit, float)

        if stop_loss is not None:
            assert stop_loss < 150.0
        if take_profit is not None:
            assert take_profit > 150.0

    def test_generate_portfolio_actions(
        self,
        recommendation_system,
        sample_portfolio_data,
        sample_optimization_results,
        sample_risk_metrics,
        sample_diversification_metrics,
    ):
        """ポートフォリオアクション生成テスト"""
        actions = recommendation_system._generate_portfolio_actions(
            sample_portfolio_data,
            sample_optimization_results,
            sample_risk_metrics,
            sample_diversification_metrics,
        )

        assert isinstance(actions, list)

        for action in actions:
            assert isinstance(action, dict)
            assert "type" in action
            assert "description" in action
            assert "priority" in action
            assert "expected_impact" in action

            assert isinstance(action["type"], str)
            assert isinstance(action["description"], str)
            assert isinstance(action["priority"], str)
            assert isinstance(action["expected_impact"], str)
            assert action["priority"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_generate_risk_warnings(
        self,
        recommendation_system,
        sample_portfolio_data,
        sample_risk_metrics,
        sample_market_conditions,
    ):
        """リスク警告生成テスト"""
        warnings = recommendation_system._generate_risk_warnings(
            sample_portfolio_data, sample_risk_metrics, sample_market_conditions
        )

        assert isinstance(warnings, list)

        for warning in warnings:
            assert isinstance(warning, dict)
            assert "type" in warning
            assert "message" in warning
            assert "severity" in warning
            assert "recommendation" in warning

            assert isinstance(warning["type"], str)
            assert isinstance(warning["message"], str)
            assert isinstance(warning["severity"], str)
            assert isinstance(warning["recommendation"], str)
            assert warning["severity"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_generate_optimization_suggestions(
        self,
        recommendation_system,
        sample_optimization_results,
        sample_risk_metrics,
        sample_diversification_metrics,
    ):
        """最適化提案生成テスト"""
        suggestions = recommendation_system._generate_optimization_suggestions(
            sample_optimization_results,
            sample_risk_metrics,
            sample_diversification_metrics,
        )

        assert isinstance(suggestions, list)

        for suggestion in suggestions:
            assert isinstance(suggestion, dict)
            assert "type" in suggestion
            assert "description" in suggestion
            assert "current_value" in suggestion
            assert "target_value" in suggestion
            assert "improvement_method" in suggestion

            assert isinstance(suggestion["type"], str)
            assert isinstance(suggestion["description"], str)
            assert isinstance(suggestion["current_value"], (int, float))
            assert isinstance(suggestion["target_value"], (int, float))
            assert isinstance(suggestion["improvement_method"], str)

    def test_generate_rebalancing_plan(
        self, recommendation_system, sample_portfolio_data, sample_optimization_results
    ):
        """リバランス計画生成テスト"""
        plan = recommendation_system._generate_rebalancing_plan(
            sample_portfolio_data, sample_optimization_results, None
        )

        assert isinstance(plan, dict)
        assert "rebalancing_needed" in plan
        assert "total_trades" in plan
        assert "total_value" in plan
        assert "trades" in plan
        assert "frequency" in plan
        assert "threshold" in plan

        assert isinstance(plan["rebalancing_needed"], bool)
        assert isinstance(plan["total_trades"], int)
        assert isinstance(plan["total_value"], (int, float))
        assert isinstance(plan["trades"], list)
        assert isinstance(plan["frequency"], str)
        assert isinstance(plan["threshold"], float)

        assert plan["total_trades"] >= 0
        assert plan["total_value"] >= 0.0
        assert plan["threshold"] >= 0.0

    def test_generate_diversification_advice(
        self,
        recommendation_system,
        sample_diversification_metrics,
        sample_portfolio_data,
    ):
        """分散投資アドバイス生成テスト"""
        advice = recommendation_system._generate_diversification_advice(
            sample_diversification_metrics, sample_portfolio_data
        )

        assert isinstance(advice, list)

        for advice_item in advice:
            assert isinstance(advice_item, dict)
            assert "type" in advice_item
            assert "description" in advice_item
            assert "current_score" in advice_item
            assert "target_score" in advice_item
            assert "suggestions" in advice_item

            assert isinstance(advice_item["type"], str)
            assert isinstance(advice_item["description"], str)
            assert isinstance(advice_item["current_score"], (int, float))
            assert isinstance(advice_item["target_score"], (int, float))
            assert isinstance(advice_item["suggestions"], list)

    def test_generate_portfolio_recommendations_integration(
        self,
        recommendation_system,
        sample_portfolio_data,
        sample_market_conditions,
        sample_optimization_results,
        sample_risk_metrics,
        sample_diversification_metrics,
    ):
        """ポートフォリオ推奨事項生成統合テスト"""
        result = recommendation_system.generate_portfolio_recommendations(
            sample_portfolio_data,
            sample_market_conditions,
            sample_optimization_results,
            sample_risk_metrics,
            sample_diversification_metrics,
            None,
        )

        assert isinstance(result, PortfolioRecommendation)
        assert hasattr(result, "overall_assessment")
        assert hasattr(result, "individual_recommendations")
        assert hasattr(result, "portfolio_actions")
        assert hasattr(result, "risk_warnings")
        assert hasattr(result, "optimization_suggestions")
        assert hasattr(result, "rebalancing_plan")
        assert hasattr(result, "diversification_advice")
        assert hasattr(result, "timestamp")

        # 全体評価の確認
        assert isinstance(result.overall_assessment, dict)
        assert "overall_score" in result.overall_assessment
        assert "grade" in result.overall_assessment
        assert "status" in result.overall_assessment

        # 個別推奨事項の確認
        assert isinstance(result.individual_recommendations, list)
        assert len(result.individual_recommendations) == 5  # 5銘柄

        # ポートフォリオアクションの確認
        assert isinstance(result.portfolio_actions, list)

        # リスク警告の確認
        assert isinstance(result.risk_warnings, list)

        # 最適化提案の確認
        assert isinstance(result.optimization_suggestions, list)

        # リバランス計画の確認
        assert isinstance(result.rebalancing_plan, dict)
        assert "rebalancing_needed" in result.rebalancing_plan

        # 分散投資アドバイスの確認
        assert isinstance(result.diversification_advice, list)

        # タイムスタンプの確認
        assert isinstance(result.timestamp, str)

    def test_error_handling(self, recommendation_system):
        """エラーハンドリングテスト"""
        # 空のデータでのテスト
        empty_portfolio_data = {"total_value": 0, "positions": {}, "weights": {}}
        empty_market_conditions = {}
        empty_optimization_results = {}
        empty_risk_metrics = {}
        empty_diversification_metrics = {}

        result = recommendation_system.generate_portfolio_recommendations(
            empty_portfolio_data,
            empty_market_conditions,
            empty_optimization_results,
            empty_risk_metrics,
            empty_diversification_metrics,
            None,
        )

        # エラーが発生しても適切に処理されることを確認
        assert isinstance(result, PortfolioRecommendation)
        assert hasattr(result, "overall_assessment")
        assert hasattr(result, "individual_recommendations")
        assert hasattr(result, "portfolio_actions")
        assert hasattr(result, "risk_warnings")
        assert hasattr(result, "optimization_suggestions")
        assert hasattr(result, "rebalancing_plan")
        assert hasattr(result, "diversification_advice")
        assert hasattr(result, "timestamp")

    def test_edge_cases(
        self,
        recommendation_system,
        sample_portfolio_data,
        sample_optimization_results,
        sample_risk_metrics,
        sample_diversification_metrics,
    ):
        """エッジケーステスト"""
        # 極端な市場条件でのテスト
        extreme_market_conditions = {
            "volatility_regime": "EXTREME",
            "trend_direction": "BEAR",
            "liquidity_level": "LOW",
            "market_stress": 0.9,
            "correlation_level": 0.8,
        }

        result = recommendation_system.generate_portfolio_recommendations(
            sample_portfolio_data,
            extreme_market_conditions,
            sample_optimization_results,
            sample_risk_metrics,
            sample_diversification_metrics,
            None,
        )

        assert isinstance(result, PortfolioRecommendation)
        assert hasattr(result, "overall_assessment")
        assert hasattr(result, "individual_recommendations")
        assert hasattr(result, "portfolio_actions")
        assert hasattr(result, "risk_warnings")
        assert hasattr(result, "optimization_suggestions")
        assert hasattr(result, "rebalancing_plan")
        assert hasattr(result, "diversification_advice")
        assert hasattr(result, "timestamp")

    def test_performance_metrics(
        self,
        recommendation_system,
        sample_portfolio_data,
        sample_market_conditions,
        sample_optimization_results,
        sample_risk_metrics,
        sample_diversification_metrics,
    ):
        """パフォーマンスメトリクステスト"""
        result = recommendation_system.generate_portfolio_recommendations(
            sample_portfolio_data,
            sample_market_conditions,
            sample_optimization_results,
            sample_risk_metrics,
            sample_diversification_metrics,
            None,
        )

        # パフォーマンスメトリクスが適切に計算されることを確認
        assert isinstance(result.overall_assessment, dict)
        assert "overall_score" in result.overall_assessment
        assert 0.0 <= result.overall_assessment["overall_score"] <= 1.0

        assert isinstance(result.individual_recommendations, list)
        assert len(result.individual_recommendations) == 5

        assert isinstance(result.portfolio_actions, list)
        assert isinstance(result.risk_warnings, list)
        assert isinstance(result.optimization_suggestions, list)
        assert isinstance(result.rebalancing_plan, dict)
        assert isinstance(result.diversification_advice, list)
        assert isinstance(result.timestamp, str)
