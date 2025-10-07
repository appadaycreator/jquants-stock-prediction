"""
最適なポジションサイズ提案システムのテスト
"""

import pytest
import numpy as np
from datetime import datetime
import sys
import os

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.optimal_position_sizing_system import (
    OptimalPositionSizingSystem,
    PositionSizingResult,
    MarketConditions,
)


class TestOptimalPositionSizingSystem:
    """最適なポジションサイズ提案システムのテスト"""

    @pytest.fixture
    def sizing_system(self):
        """ポジションサイジングシステムのフィクスチャ"""
        config = {
            "risk_free_rate": 0.02,
            "transaction_cost": 0.001,
            "min_trade_amount": 10000,
            "max_trade_amount": 1000000,
            "max_position_weight": 0.2,
            "max_risk_per_trade": 0.02,
            "max_portfolio_risk": 0.05,
            "max_drawdown": 0.15,
            "max_var_95": 0.03,
            "max_correlation": 0.7,
            "min_liquidity": 1000000,
            "max_volatility": 0.5,
        }
        return OptimalPositionSizingSystem(config)

    @pytest.fixture
    def sample_stock_data(self):
        """サンプル銘柄データ"""
        return {
            "symbol": "AAPL",
            "price_data": [
                {"close": 145.0, "volume": 1000000},
                {"close": 147.0, "volume": 1100000},
                {"close": 150.0, "volume": 1200000},
                {"close": 152.0, "volume": 1300000},
                {"close": 155.0, "volume": 1400000},
            ],
            "sector": "Technology",
            "market_cap": 2500000000000,
            "liquidity_score": 1000000,
            "volatility": 0.25,
            "expected_return": 0.08,
        }

    @pytest.fixture
    def sample_market_conditions(self):
        """サンプル市場条件"""
        return MarketConditions(
            volatility_regime="NORMAL",
            trend_direction="BULL",
            liquidity_level="HIGH",
            market_stress=0.3,
            correlation_level=0.4,
        )

    @pytest.fixture
    def sample_existing_portfolio(self):
        """サンプル既存ポートフォリオ"""
        return {"AAPL": 0.3, "GOOGL": 0.25, "MSFT": 0.2, "AMZN": 0.15, "TSLA": 0.1}

    def test_initialization(self, sizing_system):
        """初期化テスト"""
        assert sizing_system.risk_free_rate == 0.02
        assert sizing_system.transaction_cost == 0.001
        assert sizing_system.min_trade_amount == 10000
        assert sizing_system.max_trade_amount == 1000000

        # リスク制約の確認
        assert sizing_system.risk_constraints.max_position_weight == 0.2
        assert sizing_system.risk_constraints.max_risk_per_trade == 0.02
        assert sizing_system.risk_constraints.max_portfolio_risk == 0.05
        assert sizing_system.risk_constraints.max_drawdown == 0.15
        assert sizing_system.risk_constraints.max_var_95 == 0.03
        assert sizing_system.risk_constraints.max_correlation == 0.7
        assert sizing_system.risk_constraints.min_liquidity == 1000000
        assert sizing_system.risk_constraints.max_volatility == 0.5

    def test_get_default_config(self, sizing_system):
        """デフォルト設定取得テスト"""
        config = sizing_system._get_default_config()
        assert "risk_free_rate" in config
        assert "transaction_cost" in config
        assert "min_trade_amount" in config
        assert "max_trade_amount" in config
        assert "max_position_weight" in config
        assert "max_risk_per_trade" in config
        assert "max_portfolio_risk" in config
        assert "max_drawdown" in config
        assert "max_var_95" in config
        assert "max_correlation" in config
        assert "min_liquidity" in config
        assert "max_volatility" in config

    def test_preprocess_stock_data(self, sizing_system, sample_stock_data):
        """銘柄データ前処理テスト"""
        processed_data = sizing_system._preprocess_stock_data(sample_stock_data)

        assert "returns" in processed_data
        assert "volatilities" in processed_data
        assert "volumes" in processed_data
        assert "prices" in processed_data
        assert "liquidity_scores" in processed_data

        assert len(processed_data["returns"]) > 0
        assert len(processed_data["volatilities"]) > 0
        assert len(processed_data["volumes"]) > 0
        assert len(processed_data["prices"]) > 0
        assert len(processed_data["liquidity_scores"]) > 0

    def test_calculate_risk_metrics(self, sizing_system, sample_stock_data):
        """リスクメトリクス計算テスト"""
        processed_data = sizing_system._preprocess_stock_data(sample_stock_data)
        risk_metrics = sizing_system._calculate_risk_metrics(processed_data, 150.0)

        assert isinstance(risk_metrics, dict)
        assert "volatility" in risk_metrics
        assert "var_95" in risk_metrics
        assert "var_99" in risk_metrics
        assert "max_drawdown" in risk_metrics
        assert "sharpe_ratio" in risk_metrics
        assert "skewness" in risk_metrics
        assert "kurtosis" in risk_metrics

        assert isinstance(risk_metrics["volatility"], float)
        assert isinstance(risk_metrics["var_95"], float)
        assert isinstance(risk_metrics["var_99"], float)
        assert isinstance(risk_metrics["max_drawdown"], float)
        assert isinstance(risk_metrics["sharpe_ratio"], float)
        assert isinstance(risk_metrics["skewness"], float)
        assert isinstance(risk_metrics["kurtosis"], float)

        assert risk_metrics["volatility"] >= 0.0
        assert risk_metrics["max_drawdown"] >= 0.0
        assert np.isfinite(risk_metrics["sharpe_ratio"])
        assert np.isfinite(risk_metrics["skewness"])
        assert np.isfinite(risk_metrics["kurtosis"])

    def test_analyze_market_conditions(self, sizing_system, sample_market_conditions):
        """市場条件分析テスト"""
        market_adjustment = sizing_system._analyze_market_conditions(
            sample_market_conditions
        )

        assert isinstance(market_adjustment, dict)
        assert "volatility_adjustment" in market_adjustment
        assert "trend_adjustment" in market_adjustment
        assert "liquidity_adjustment" in market_adjustment
        assert "stress_adjustment" in market_adjustment
        assert "correlation_adjustment" in market_adjustment

        assert isinstance(market_adjustment["volatility_adjustment"], float)
        assert isinstance(market_adjustment["trend_adjustment"], float)
        assert isinstance(market_adjustment["liquidity_adjustment"], float)
        assert isinstance(market_adjustment["stress_adjustment"], float)
        assert isinstance(market_adjustment["correlation_adjustment"], float)

        assert market_adjustment["volatility_adjustment"] > 0.0
        assert market_adjustment["trend_adjustment"] > 0.0
        assert market_adjustment["liquidity_adjustment"] > 0.0
        assert market_adjustment["stress_adjustment"] > 0.0
        assert market_adjustment["correlation_adjustment"] > 0.0

    def test_calculate_kelly_position_size(self, sizing_system, sample_stock_data):
        """ケリー基準ポジションサイズ計算テスト"""
        processed_data = sizing_system._preprocess_stock_data(sample_stock_data)
        risk_metrics = sizing_system._calculate_risk_metrics(processed_data, 150.0)

        kelly_result = sizing_system._calculate_kelly_position_size(
            processed_data, 150.0, 1000000, risk_metrics
        )

        assert isinstance(kelly_result, dict)
        assert "kelly_fraction" in kelly_result
        assert "position_value" in kelly_result

        assert isinstance(kelly_result["kelly_fraction"], float)
        assert isinstance(kelly_result["position_value"], float)
        assert 0.0 <= kelly_result["kelly_fraction"] <= 1.0
        assert kelly_result["position_value"] >= 0.0

    def test_calculate_risk_parity_position_size(
        self, sizing_system, sample_stock_data
    ):
        """リスクパリティポジションサイズ計算テスト"""
        processed_data = sizing_system._preprocess_stock_data(sample_stock_data)
        risk_metrics = sizing_system._calculate_risk_metrics(processed_data, 150.0)

        risk_parity_result = sizing_system._calculate_risk_parity_position_size(
            processed_data, 150.0, 1000000, risk_metrics
        )

        assert isinstance(risk_parity_result, dict)
        assert "risk_parity_weight" in risk_parity_result
        assert "position_value" in risk_parity_result

        assert isinstance(risk_parity_result["risk_parity_weight"], float)
        assert isinstance(risk_parity_result["position_value"], float)
        assert 0.0 <= risk_parity_result["risk_parity_weight"] <= 1.0
        assert risk_parity_result["position_value"] >= 0.0

    def test_calculate_volatility_adjusted_position_size(
        self, sizing_system, sample_stock_data, sample_market_conditions
    ):
        """ボラティリティ調整ポジションサイズ計算テスト"""
        processed_data = sizing_system._preprocess_stock_data(sample_stock_data)
        risk_metrics = sizing_system._calculate_risk_metrics(processed_data, 150.0)
        market_adjustment = sizing_system._analyze_market_conditions(
            sample_market_conditions
        )

        volatility_adjusted_result = (
            sizing_system._calculate_volatility_adjusted_position_size(
                processed_data, 150.0, 1000000, risk_metrics, market_adjustment
            )
        )

        assert isinstance(volatility_adjusted_result, dict)
        assert "volatility_adjusted_weight" in volatility_adjusted_result
        assert "position_value" in volatility_adjusted_result
        assert "volatility" in volatility_adjusted_result

        assert isinstance(
            volatility_adjusted_result["volatility_adjusted_weight"], float
        )
        assert isinstance(volatility_adjusted_result["position_value"], float)
        assert isinstance(volatility_adjusted_result["volatility"], float)
        assert 0.0 <= volatility_adjusted_result["volatility_adjusted_weight"] <= 1.0
        assert volatility_adjusted_result["position_value"] >= 0.0
        assert volatility_adjusted_result["volatility"] >= 0.0

    def test_optimize_position_size(
        self,
        sizing_system,
        sample_stock_data,
        sample_market_conditions,
        sample_existing_portfolio,
    ):
        """最適化ポジションサイズ計算テスト"""
        processed_data = sizing_system._preprocess_stock_data(sample_stock_data)
        risk_metrics = sizing_system._calculate_risk_metrics(processed_data, 150.0)
        market_adjustment = sizing_system._analyze_market_conditions(
            sample_market_conditions
        )

        optimized_result = sizing_system._optimize_position_size(
            processed_data,
            150.0,
            1000000,
            risk_metrics,
            market_adjustment,
            sample_existing_portfolio,
            0.1,
            "MEDIUM",
        )

        assert isinstance(optimized_result, dict)
        assert "optimized_weight" in optimized_result
        assert "position_value" in optimized_result
        assert "optimization_success" in optimized_result

        assert isinstance(optimized_result["optimized_weight"], float)
        assert isinstance(optimized_result["position_value"], float)
        assert isinstance(optimized_result["optimization_success"], bool)
        assert 0.0 <= optimized_result["optimized_weight"] <= 1.0
        assert optimized_result["position_value"] >= 0.0

    def test_integrate_and_validate_results(
        self,
        sizing_system,
        sample_stock_data,
        sample_market_conditions,
        sample_existing_portfolio,
    ):
        """結果統合・検証テスト"""
        processed_data = sizing_system._preprocess_stock_data(sample_stock_data)
        risk_metrics = sizing_system._calculate_risk_metrics(processed_data, 150.0)
        market_adjustment = sizing_system._analyze_market_conditions(
            sample_market_conditions
        )

        kelly_result = {"kelly_fraction": 0.1, "position_value": 100000}
        risk_parity_result = {"risk_parity_weight": 0.15, "position_value": 150000}
        volatility_adjusted_result = {
            "volatility_adjusted_weight": 0.12,
            "position_value": 120000,
        }
        optimized_result = {
            "optimized_weight": 0.13,
            "position_value": 130000,
            "optimization_success": True,
        }

        result = sizing_system._integrate_and_validate_results(
            "AAPL",
            150.0,
            1000000,
            kelly_result,
            risk_parity_result,
            volatility_adjusted_result,
            optimized_result,
            risk_metrics,
            market_adjustment,
            sample_existing_portfolio,
        )

        assert isinstance(result, PositionSizingResult)
        assert hasattr(result, "symbol")
        assert hasattr(result, "recommended_quantity")
        assert hasattr(result, "recommended_value")
        assert hasattr(result, "position_weight")
        assert hasattr(result, "risk_amount")
        assert hasattr(result, "expected_return")
        assert hasattr(result, "risk_adjusted_return")
        assert hasattr(result, "confidence_score")
        assert hasattr(result, "risk_level")
        assert hasattr(result, "sizing_method")
        assert hasattr(result, "kelly_fraction")
        assert hasattr(result, "optimal_fraction")
        assert hasattr(result, "max_position_size")
        assert hasattr(result, "min_position_size")
        assert hasattr(result, "liquidity_constraint")
        assert hasattr(result, "volatility_constraint")
        assert hasattr(result, "correlation_constraint")
        assert hasattr(result, "timestamp")

        assert result.symbol == "AAPL"
        assert result.recommended_quantity >= 0
        assert result.recommended_value >= 0.0
        assert 0.0 <= result.position_weight <= 1.0
        assert result.risk_amount >= 0.0
        assert np.isfinite(result.expected_return)
        assert np.isfinite(result.risk_adjusted_return)
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        assert result.sizing_method == "integrated"
        assert 0.0 <= result.kelly_fraction <= 1.0
        assert 0.0 <= result.optimal_fraction <= 1.0
        assert result.max_position_size >= 0.0
        assert result.min_position_size >= 0.0
        assert isinstance(result.liquidity_constraint, bool)
        assert isinstance(result.volatility_constraint, bool)
        assert isinstance(result.correlation_constraint, bool)

    def test_calculate_confidence_score(self, sizing_system):
        """信頼度スコア計算テスト"""
        risk_metrics = {"volatility": 0.2, "sharpe_ratio": 1.5}
        market_adjustment = {
            "volatility_adjustment": 1.0,
            "trend_adjustment": 1.05,
            "liquidity_adjustment": 1.1,
            "stress_adjustment": 0.9,
            "correlation_adjustment": 0.95,
        }
        kelly_result = {"kelly_fraction": 0.1}
        optimized_result = {"optimization_success": True}

        confidence = sizing_system._calculate_confidence_score(
            risk_metrics, market_adjustment, kelly_result, optimized_result
        )

        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        assert np.isfinite(confidence)

    def test_determine_risk_level(self, sizing_system):
        """リスクレベル判定テスト"""
        assert sizing_system._determine_risk_level(0.1) == "LOW"
        assert sizing_system._determine_risk_level(0.2) == "MEDIUM"
        assert sizing_system._determine_risk_level(0.3) == "HIGH"
        assert sizing_system._determine_risk_level(0.4) == "VERY_HIGH"

    def test_check_liquidity_constraint(self, sizing_system):
        """流動性制約チェックテスト"""
        processed_data = {"liquidity_scores": [1000000, 2000000, 1500000]}

        # 十分な流動性
        assert sizing_system._check_liquidity_constraint(processed_data, 100000) == True

        # 不十分な流動性
        processed_data_low = {"liquidity_scores": [100000, 200000, 150000]}
        assert (
            sizing_system._check_liquidity_constraint(processed_data_low, 1000000)
            == False
        )

    def test_check_volatility_constraint(self, sizing_system):
        """ボラティリティ制約チェックテスト"""
        assert sizing_system._check_volatility_constraint(0.2) == True
        assert sizing_system._check_volatility_constraint(0.6) == False

    def test_check_correlation_constraint(
        self, sizing_system, sample_existing_portfolio
    ):
        """相関制約チェックテスト"""
        assert (
            sizing_system._check_correlation_constraint(
                sample_existing_portfolio, "AAPL"
            )
            == True
        )
        assert sizing_system._check_correlation_constraint(None, "AAPL") == True

    def test_calculate_skewness(self, sizing_system):
        """歪度計算テスト"""
        returns = np.array([0.01, 0.02, -0.01, 0.03, -0.02])
        skewness = sizing_system._calculate_skewness(returns)

        assert isinstance(skewness, float)
        assert np.isfinite(skewness)

    def test_calculate_kurtosis(self, sizing_system):
        """尖度計算テスト"""
        returns = np.array([0.01, 0.02, -0.01, 0.03, -0.02])
        kurtosis = sizing_system._calculate_kurtosis(returns)

        assert isinstance(kurtosis, float)
        assert np.isfinite(kurtosis)

    def test_calculate_optimal_position_size_integration(
        self,
        sizing_system,
        sample_stock_data,
        sample_market_conditions,
        sample_existing_portfolio,
    ):
        """最適ポジションサイズ計算統合テスト"""
        result = sizing_system.calculate_optimal_position_size(
            "AAPL",
            150.0,
            1000000,
            sample_stock_data,
            sample_market_conditions,
            sample_existing_portfolio,
            0.1,
            "MEDIUM",
        )

        assert isinstance(result, PositionSizingResult)
        assert result.symbol == "AAPL"
        assert result.recommended_quantity >= 0
        assert result.recommended_value >= 0.0
        assert 0.0 <= result.position_weight <= 1.0
        assert result.risk_amount >= 0.0
        assert np.isfinite(result.expected_return)
        assert np.isfinite(result.risk_adjusted_return)
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        assert result.sizing_method == "integrated"
        assert 0.0 <= result.kelly_fraction <= 1.0
        assert 0.0 <= result.optimal_fraction <= 1.0
        assert result.max_position_size >= 0.0
        assert result.min_position_size >= 0.0
        assert isinstance(result.liquidity_constraint, bool)
        assert isinstance(result.volatility_constraint, bool)
        assert isinstance(result.correlation_constraint, bool)

    def test_generate_position_sizing_recommendations(
        self, sizing_system, sample_market_conditions
    ):
        """ポジションサイジング推奨事項生成テスト"""
        position_result = PositionSizingResult(
            symbol="AAPL",
            recommended_quantity=100,
            recommended_value=15000.0,
            position_weight=0.15,
            risk_amount=3000.0,
            expected_return=0.08,
            risk_adjusted_return=0.4,
            confidence_score=0.8,
            risk_level="MEDIUM",
            sizing_method="integrated",
            kelly_fraction=0.1,
            optimal_fraction=0.12,
            max_position_size=200000.0,
            min_position_size=10000.0,
            liquidity_constraint=True,
            volatility_constraint=True,
            correlation_constraint=True,
            timestamp=datetime.now().isoformat(),
        )

        recommendations = sizing_system.generate_position_sizing_recommendations(
            position_result, sample_market_conditions
        )

        assert isinstance(recommendations, dict)
        assert "position_summary" in recommendations
        assert "risk_assessment" in recommendations
        assert "constraints_status" in recommendations
        assert "sizing_methods" in recommendations
        assert "market_conditions" in recommendations
        assert "action_items" in recommendations
        assert "warnings" in recommendations
        assert "timestamp" in recommendations

        # ポジションサマリーの確認
        position_summary = recommendations["position_summary"]
        assert "symbol" in position_summary
        assert "recommended_quantity" in position_summary
        assert "recommended_value" in position_summary
        assert "position_weight" in position_summary
        assert "risk_amount" in position_summary

        # リスク評価の確認
        risk_assessment = recommendations["risk_assessment"]
        assert "risk_level" in risk_assessment
        assert "expected_return" in risk_assessment
        assert "risk_adjusted_return" in risk_assessment
        assert "confidence_score" in risk_assessment

        # 制約ステータスの確認
        constraints_status = recommendations["constraints_status"]
        assert "liquidity_ok" in constraints_status
        assert "volatility_ok" in constraints_status
        assert "correlation_ok" in constraints_status

        # サイジング手法の確認
        sizing_methods = recommendations["sizing_methods"]
        assert "kelly_fraction" in sizing_methods
        assert "optimal_fraction" in sizing_methods
        assert "method" in sizing_methods

        # 市場条件の確認
        market_conditions = recommendations["market_conditions"]
        assert "volatility_regime" in market_conditions
        assert "trend_direction" in market_conditions
        assert "liquidity_level" in market_conditions
        assert "market_stress" in market_conditions

        # アクションアイテムと警告の確認
        assert isinstance(recommendations["action_items"], list)
        assert isinstance(recommendations["warnings"], list)

    def test_error_handling(self, sizing_system, sample_market_conditions):
        """エラーハンドリングテスト"""
        # 空のデータでのテスト
        empty_stock_data = {}

        result = sizing_system.calculate_optimal_position_size(
            "AAPL", 150.0, 1000000, empty_stock_data, sample_market_conditions, None
        )

        # エラーが発生しても適切に処理されることを確認
        assert isinstance(result, PositionSizingResult)
        assert result.symbol == "AAPL"
        assert result.recommended_quantity >= 0

    def test_edge_cases(self, sizing_system, sample_stock_data):
        """エッジケーステスト"""
        # 極端な市場条件でのテスト
        extreme_market_conditions = MarketConditions(
            volatility_regime="EXTREME",
            trend_direction="BEAR",
            liquidity_level="LOW",
            market_stress=0.9,
            correlation_level=0.8,
        )

        result = sizing_system.calculate_optimal_position_size(
            "AAPL", 150.0, 1000000, sample_stock_data, extreme_market_conditions, None
        )

        assert isinstance(result, PositionSizingResult)
        assert result.symbol == "AAPL"
        assert result.recommended_quantity >= 0

    def test_performance_metrics(
        self, sizing_system, sample_stock_data, sample_market_conditions
    ):
        """パフォーマンスメトリクステスト"""
        result = sizing_system.calculate_optimal_position_size(
            "AAPL", 150.0, 1000000, sample_stock_data, sample_market_conditions, None
        )

        # パフォーマンスメトリクスが適切に計算されることを確認
        assert result.recommended_quantity >= 0
        assert result.recommended_value >= 0.0
        assert 0.0 <= result.position_weight <= 1.0
        assert result.risk_amount >= 0.0
        assert np.isfinite(result.expected_return)
        assert np.isfinite(result.risk_adjusted_return)
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        assert 0.0 <= result.kelly_fraction <= 1.0
        assert 0.0 <= result.optimal_fraction <= 1.0
        assert result.max_position_size >= 0.0
        assert result.min_position_size >= 0.0
