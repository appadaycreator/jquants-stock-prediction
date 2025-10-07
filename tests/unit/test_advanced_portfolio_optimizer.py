"""
高度なポートフォリオ最適化システムのテスト
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock
from datetime import datetime
import sys
import os

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.advanced_portfolio_optimizer import (
    AdvancedPortfolioOptimizer,
    OptimizationResult,
    RiskMetrics,
)


class TestAdvancedPortfolioOptimizer:
    """高度なポートフォリオ最適化システムのテスト"""

    @pytest.fixture
    def optimizer(self):
        """最適化システムのフィクスチャ"""
        config = {
            "max_iterations": 100,
            "tolerance": 1e-6,
            "risk_free_rate": 0.02,
            "max_position_weight": 0.2,
            "min_position_weight": 0.01,
        }
        return AdvancedPortfolioOptimizer(config)

    @pytest.fixture
    def sample_stock_data(self):
        """サンプル銘柄データ"""
        return [
            {
                "symbol": "AAPL",
                "price": 150.0,
                "price_data": [
                    {"close": 145.0, "volume": 1000000},
                    {"close": 147.0, "volume": 1100000},
                    {"close": 150.0, "volume": 1200000},
                ],
                "sector": "Technology",
                "market_cap": 2500000000000,
                "liquidity_score": 1000000,
            },
            {
                "symbol": "GOOGL",
                "price": 2800.0,
                "price_data": [
                    {"close": 2750.0, "volume": 500000},
                    {"close": 2780.0, "volume": 550000},
                    {"close": 2800.0, "volume": 600000},
                ],
                "sector": "Technology",
                "market_cap": 1800000000000,
                "liquidity_score": 500000,
            },
            {
                "symbol": "MSFT",
                "price": 300.0,
                "price_data": [
                    {"close": 295.0, "volume": 800000},
                    {"close": 298.0, "volume": 850000},
                    {"close": 300.0, "volume": 900000},
                ],
                "sector": "Technology",
                "market_cap": 2200000000000,
                "liquidity_score": 800000,
            },
        ]

    @pytest.fixture
    def sample_market_data(self):
        """サンプル市場データ"""
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        return pd.DataFrame(
            {
                "Date": dates,
                "Close": np.random.normal(100, 10, 100),
                "Volume": np.random.normal(1000000, 100000, 100),
            }
        )

    def test_initialization(self, optimizer):
        """初期化テスト"""
        assert optimizer.max_iterations == 100
        assert optimizer.tolerance == 1e-6
        assert optimizer.risk_free_rate == 0.02
        assert optimizer.max_position_weight == 0.2
        assert optimizer.min_position_weight == 0.01

    def test_get_default_config(self, optimizer):
        """デフォルト設定取得テスト"""
        config = optimizer._get_default_config()
        assert "max_iterations" in config
        assert "tolerance" in config
        assert "risk_free_rate" in config
        assert "max_position_weight" in config
        assert "min_position_weight" in config

    def test_preprocess_data(self, optimizer, sample_stock_data, sample_market_data):
        """データ前処理テスト"""
        processed_data = optimizer._preprocess_data(
            sample_stock_data, sample_market_data, None
        )

        assert "symbols" in processed_data
        assert "prices" in processed_data
        assert "returns" in processed_data
        assert "volatilities" in processed_data
        assert "correlations" in processed_data
        assert "sectors" in processed_data
        assert "market_caps" in processed_data
        assert "liquidity_scores" in processed_data

        assert len(processed_data["symbols"]) == 3
        assert len(processed_data["prices"]) == 3
        assert len(processed_data["returns"]) == 3
        assert len(processed_data["volatilities"]) == 3

    def test_calculate_returns_and_covariance(self, optimizer, sample_stock_data):
        """リターン・共分散計算テスト"""
        processed_data = optimizer._preprocess_data(sample_stock_data, None, None)
        returns_matrix, cov_matrix = optimizer._calculate_returns_and_covariance(
            processed_data
        )

        assert isinstance(returns_matrix, np.ndarray)
        assert isinstance(cov_matrix, np.ndarray)
        assert cov_matrix.shape[0] == cov_matrix.shape[1]  # 正方行列
        assert np.all(np.isfinite(cov_matrix))  # 有限値

    def test_calculate_expected_returns(self, optimizer, sample_stock_data):
        """期待リターン計算テスト"""
        processed_data = optimizer._preprocess_data(sample_stock_data, None, None)
        expected_returns = optimizer._calculate_expected_returns(
            processed_data, np.array([[0.01, 0.02], [0.02, 0.03], [0.01, 0.02]])
        )

        assert isinstance(expected_returns, np.ndarray)
        assert len(expected_returns) == 3
        assert np.all(np.isfinite(expected_returns))

    def test_optimize_max_sharpe(self, optimizer, sample_stock_data):
        """最大シャープレシオ最適化テスト"""
        processed_data = optimizer._preprocess_data(sample_stock_data, None, None)
        expected_returns = np.array([0.1, 0.12, 0.08])
        cov_matrix = np.array(
            [[0.04, 0.02, 0.01], [0.02, 0.06, 0.02], [0.01, 0.02, 0.05]]
        )

        result = optimizer._optimize_max_sharpe(expected_returns, cov_matrix)

        assert isinstance(result, OptimizationResult)
        assert "weights" in result.__dict__
        assert "expected_return" in result.__dict__
        assert "volatility" in result.__dict__
        assert "sharpe_ratio" in result.__dict__
        assert "diversification_score" in result.__dict__
        assert "risk_level" in result.__dict__
        assert "confidence" in result.__dict__
        assert "optimization_timestamp" in result.__dict__
        assert "method" in result.__dict__
        assert "iterations" in result.__dict__
        assert "convergence" in result.__dict__

    def test_optimize_mean_variance(self, optimizer, sample_stock_data):
        """平均分散最適化テスト"""
        processed_data = optimizer._preprocess_data(sample_stock_data, None, None)
        expected_returns = np.array([0.1, 0.12, 0.08])
        cov_matrix = np.array(
            [[0.04, 0.02, 0.01], [0.02, 0.06, 0.02], [0.01, 0.02, 0.05]]
        )

        result = optimizer._optimize_mean_variance(
            expected_returns, cov_matrix, 0.1, 0.15
        )

        assert isinstance(result, OptimizationResult)
        assert "weights" in result.__dict__
        assert "expected_return" in result.__dict__
        assert "volatility" in result.__dict__
        assert "sharpe_ratio" in result.__dict__

    def test_optimize_black_litterman(
        self, optimizer, sample_stock_data, sample_market_data
    ):
        """ブラック・リッターマン最適化テスト"""
        processed_data = optimizer._preprocess_data(
            sample_stock_data, sample_market_data, None
        )
        expected_returns = np.array([0.1, 0.12, 0.08])
        cov_matrix = np.array(
            [[0.04, 0.02, 0.01], [0.02, 0.06, 0.02], [0.01, 0.02, 0.05]]
        )

        result = optimizer._optimize_black_litterman(
            expected_returns, cov_matrix, sample_market_data
        )

        assert isinstance(result, OptimizationResult)
        assert "weights" in result.__dict__
        assert "expected_return" in result.__dict__
        assert "volatility" in result.__dict__
        assert "sharpe_ratio" in result.__dict__

    def test_optimize_risk_parity(self, optimizer, sample_stock_data):
        """リスクパリティ最適化テスト"""
        processed_data = optimizer._preprocess_data(sample_stock_data, None, None)
        cov_matrix = np.array(
            [[0.04, 0.02, 0.01], [0.02, 0.06, 0.02], [0.01, 0.02, 0.05]]
        )

        result = optimizer._optimize_risk_parity(cov_matrix)

        assert isinstance(result, OptimizationResult)
        assert "weights" in result.__dict__
        assert "expected_return" in result.__dict__
        assert "volatility" in result.__dict__
        assert "sharpe_ratio" in result.__dict__

    def test_calculate_diversification_score(self, optimizer):
        """分散投資スコア計算テスト"""
        weights = np.array([0.4, 0.3, 0.3])
        cov_matrix = np.array(
            [[0.04, 0.02, 0.01], [0.02, 0.06, 0.02], [0.01, 0.02, 0.05]]
        )

        score = optimizer._calculate_diversification_score(weights, cov_matrix)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_ensure_positive_definite(self, optimizer):
        """正定値行列確保テスト"""
        matrix = np.array([[1.0, 0.5], [0.5, 1.0]])
        result = optimizer._ensure_positive_definite(matrix)

        assert isinstance(result, np.ndarray)
        assert result.shape == matrix.shape

        # 固有値が正であることを確認
        eigenvalues = np.linalg.eigvals(result)
        assert np.all(eigenvalues > 0)

    def test_determine_risk_level(self, optimizer):
        """リスクレベル判定テスト"""
        assert optimizer._determine_risk_level(0.1) == "LOW"
        assert optimizer._determine_risk_level(0.2) == "MEDIUM"
        assert optimizer._determine_risk_level(0.3) == "HIGH"
        assert optimizer._determine_risk_level(0.4) == "VERY_HIGH"

    def test_calculate_optimization_confidence(self, optimizer):
        """最適化信頼度計算テスト"""
        mock_result = Mock()
        mock_result.success = True
        mock_result.nit = 50

        confidence = optimizer._calculate_optimization_confidence(mock_result)

        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_validate_and_adjust_result(self, optimizer, sample_stock_data):
        """結果検証・調整テスト"""
        processed_data = optimizer._preprocess_data(sample_stock_data, None, None)
        mock_result = OptimizationResult(
            weights={0: 0.4, 1: 0.3, 2: 0.3},
            expected_return=0.1,
            volatility=0.15,
            sharpe_ratio=0.8,
            diversification_score=0.7,
            risk_level="MEDIUM",
            confidence=0.8,
            optimization_timestamp=datetime.now().isoformat(),
            method="max_sharpe",
            iterations=100,
            convergence=True,
        )

        result = optimizer._validate_and_adjust_result(mock_result, processed_data)

        assert isinstance(result, OptimizationResult)
        assert "weights" in result.__dict__
        assert "expected_return" in result.__dict__
        assert "volatility" in result.__dict__
        assert "sharpe_ratio" in result.__dict__

    def test_verify_sharpe_improvement(self, optimizer):
        """シャープレシオ改善確認テスト"""
        mock_result = OptimizationResult(
            weights={},
            expected_return=0.1,
            volatility=0.15,
            sharpe_ratio=0.8,
            diversification_score=0.7,
            risk_level="MEDIUM",
            confidence=0.8,
            optimization_timestamp=datetime.now().isoformat(),
            method="max_sharpe",
            iterations=100,
            convergence=True,
        )

        improvement_achieved = optimizer._verify_sharpe_improvement(mock_result)

        assert isinstance(improvement_achieved, bool)

    def test_calculate_risk_metrics(self, optimizer):
        """リスクメトリクス計算テスト"""
        weights = {0: 0.4, 1: 0.3, 2: 0.3}
        returns_matrix = np.array(
            [[0.01, 0.02, 0.01], [0.02, 0.03, 0.02], [0.01, 0.02, 0.01]]
        )
        cov_matrix = np.array(
            [[0.04, 0.02, 0.01], [0.02, 0.06, 0.02], [0.01, 0.02, 0.05]]
        )

        risk_metrics = optimizer.calculate_risk_metrics(
            weights, returns_matrix, cov_matrix
        )

        assert isinstance(risk_metrics, RiskMetrics)
        assert hasattr(risk_metrics, "var_95")
        assert hasattr(risk_metrics, "var_99")
        assert hasattr(risk_metrics, "cvar_95")
        assert hasattr(risk_metrics, "cvar_99")
        assert hasattr(risk_metrics, "max_drawdown")
        assert hasattr(risk_metrics, "sharpe_ratio")
        assert hasattr(risk_metrics, "sortino_ratio")
        assert hasattr(risk_metrics, "calmar_ratio")
        assert hasattr(risk_metrics, "information_ratio")
        assert hasattr(risk_metrics, "treynor_ratio")
        assert hasattr(risk_metrics, "jensen_alpha")
        assert hasattr(risk_metrics, "beta")
        assert hasattr(risk_metrics, "volatility")
        assert hasattr(risk_metrics, "skewness")
        assert hasattr(risk_metrics, "kurtosis")

    def test_calculate_skewness(self, optimizer):
        """歪度計算テスト"""
        returns = np.array([0.01, 0.02, -0.01, 0.03, -0.02])
        skewness = optimizer._calculate_skewness(returns)

        assert isinstance(skewness, float)
        assert np.isfinite(skewness)

    def test_calculate_kurtosis(self, optimizer):
        """尖度計算テスト"""
        returns = np.array([0.01, 0.02, -0.01, 0.03, -0.02])
        kurtosis = optimizer._calculate_kurtosis(returns)

        assert isinstance(kurtosis, float)
        assert np.isfinite(kurtosis)

    def test_generate_recommendations(self, optimizer):
        """推奨事項生成テスト"""
        optimization_result = OptimizationResult(
            weights={0: 0.4, 1: 0.3, 2: 0.3},
            expected_return=0.1,
            volatility=0.15,
            sharpe_ratio=0.8,
            diversification_score=0.7,
            risk_level="MEDIUM",
            confidence=0.8,
            optimization_timestamp=datetime.now().isoformat(),
            method="max_sharpe",
            iterations=100,
            convergence=True,
        )

        risk_metrics = RiskMetrics(
            var_95=-0.05,
            var_99=-0.08,
            cvar_95=-0.06,
            cvar_99=-0.09,
            max_drawdown=0.1,
            sharpe_ratio=0.8,
            sortino_ratio=1.0,
            calmar_ratio=1.2,
            information_ratio=0.5,
            treynor_ratio=0.6,
            jensen_alpha=0.02,
            beta=1.0,
            volatility=0.15,
            skewness=0.1,
            kurtosis=3.0,
        )

        recommendations = optimizer.generate_recommendations(
            optimization_result, risk_metrics
        )

        assert isinstance(recommendations, dict)
        assert "portfolio_allocation" in recommendations
        assert "expected_performance" in recommendations
        assert "risk_assessment" in recommendations
        assert "optimization_quality" in recommendations
        assert "action_items" in recommendations
        assert "warnings" in recommendations
        assert "timestamp" in recommendations

    def test_optimize_portfolio_integration(
        self, optimizer, sample_stock_data, sample_market_data
    ):
        """ポートフォリオ最適化統合テスト"""
        result = optimizer.optimize_portfolio(
            sample_stock_data,
            sample_market_data,
            None,
            target_return=0.1,
            max_risk=0.15,
            optimization_method="max_sharpe",
        )

        assert isinstance(result, OptimizationResult)
        assert "weights" in result.__dict__
        assert "expected_return" in result.__dict__
        assert "volatility" in result.__dict__
        assert "sharpe_ratio" in result.__dict__
        assert "diversification_score" in result.__dict__
        assert "risk_level" in result.__dict__
        assert "confidence" in result.__dict__
        assert "optimization_timestamp" in result.__dict__
        assert "method" in result.__dict__
        assert "iterations" in result.__dict__
        assert "convergence" in result.__dict__

    def test_error_handling(self, optimizer):
        """エラーハンドリングテスト"""
        # 空のデータでのテスト
        empty_data = []
        result = optimizer.optimize_portfolio(empty_data, None, None)

        # エラーが発生しても適切に処理されることを確認
        assert isinstance(result, OptimizationResult)

    def test_edge_cases(self, optimizer):
        """エッジケーステスト"""
        # 単一銘柄のテスト
        single_stock_data = [
            {
                "symbol": "AAPL",
                "price": 150.0,
                "price_data": [
                    {"close": 145.0, "volume": 1000000},
                    {"close": 147.0, "volume": 1100000},
                    {"close": 150.0, "volume": 1200000},
                ],
                "sector": "Technology",
                "market_cap": 2500000000000,
                "liquidity_score": 1000000,
            }
        ]

        result = optimizer.optimize_portfolio(single_stock_data, None, None)
        assert isinstance(result, OptimizationResult)

    def test_performance_metrics(self, optimizer, sample_stock_data):
        """パフォーマンスメトリクステスト"""
        processed_data = optimizer._preprocess_data(sample_stock_data, None, None)
        expected_returns = np.array([0.1, 0.12, 0.08])
        cov_matrix = np.array(
            [[0.04, 0.02, 0.01], [0.02, 0.06, 0.02], [0.01, 0.02, 0.05]]
        )

        result = optimizer._optimize_max_sharpe(expected_returns, cov_matrix)

        # パフォーマンスメトリクスが適切に計算されることを確認
        assert result.expected_return > 0
        assert result.volatility > 0
        assert result.sharpe_ratio >= 0
        assert result.diversification_score >= 0
        assert result.confidence >= 0
