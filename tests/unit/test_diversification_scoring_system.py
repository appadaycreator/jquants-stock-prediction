"""
分散投資スコア計算システムのテスト
"""

import pytest
import numpy as np
import sys
import os

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.diversification_scoring_system import (
    DiversificationScoringSystem,
    DiversificationMetrics,
    SectorAnalysis,
    CorrelationAnalysis,
)


class TestDiversificationScoringSystem:
    """分散投資スコア計算システムのテスト"""

    @pytest.fixture
    def scoring_system(self):
        """分散投資スコア計算システムのフィクスチャ"""
        config = {
            "max_sector_weight": 0.3,
            "max_correlation": 0.7,
            "min_effective_stocks": 5,
            "target_entropy": 0.8,
            "correlation_threshold": 0.5,
            "sector_threshold": 0.2,
        }
        return DiversificationScoringSystem(config)

    @pytest.fixture
    def sample_portfolio_weights(self):
        """サンプルポートフォリオウェイト"""
        return {"AAPL": 0.3, "GOOGL": 0.25, "MSFT": 0.2, "AMZN": 0.15, "TSLA": 0.1}

    @pytest.fixture
    def sample_stock_data(self):
        """サンプル銘柄データ"""
        return [
            {
                "symbol": "AAPL",
                "sector": "Technology",
                "region": "US",
                "market_cap": 2500000000000,
                "liquidity_score": 1000000,
                "price_data": [
                    {"close": 145.0, "volume": 1000000},
                    {"close": 147.0, "volume": 1100000},
                    {"close": 150.0, "volume": 1200000},
                ],
            },
            {
                "symbol": "GOOGL",
                "sector": "Technology",
                "region": "US",
                "market_cap": 1800000000000,
                "liquidity_score": 500000,
                "price_data": [
                    {"close": 2750.0, "volume": 500000},
                    {"close": 2780.0, "volume": 550000},
                    {"close": 2800.0, "volume": 600000},
                ],
            },
            {
                "symbol": "MSFT",
                "sector": "Technology",
                "region": "US",
                "market_cap": 2200000000000,
                "liquidity_score": 800000,
                "price_data": [
                    {"close": 295.0, "volume": 800000},
                    {"close": 298.0, "volume": 850000},
                    {"close": 300.0, "volume": 900000},
                ],
            },
            {
                "symbol": "AMZN",
                "sector": "Consumer Discretionary",
                "region": "US",
                "market_cap": 1500000000000,
                "liquidity_score": 700000,
                "price_data": [
                    {"close": 3200.0, "volume": 300000},
                    {"close": 3250.0, "volume": 350000},
                    {"close": 3300.0, "volume": 400000},
                ],
            },
            {
                "symbol": "TSLA",
                "sector": "Consumer Discretionary",
                "region": "US",
                "market_cap": 800000000000,
                "liquidity_score": 600000,
                "price_data": [
                    {"close": 200.0, "volume": 2000000},
                    {"close": 205.0, "volume": 2100000},
                    {"close": 210.0, "volume": 2200000},
                ],
            },
        ]

    def test_initialization(self, scoring_system):
        """初期化テスト"""
        assert scoring_system.max_sector_weight == 0.3
        assert scoring_system.max_correlation == 0.7
        assert scoring_system.min_effective_stocks == 5
        assert scoring_system.target_entropy == 0.8

    def test_get_default_config(self, scoring_system):
        """デフォルト設定取得テスト"""
        config = scoring_system._get_default_config()
        assert "max_sector_weight" in config
        assert "max_correlation" in config
        assert "min_effective_stocks" in config
        assert "target_entropy" in config
        assert "correlation_threshold" in config
        assert "sector_threshold" in config

    def test_preprocess_portfolio_data(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """ポートフォリオデータ前処理テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )

        assert "symbols" in processed_data
        assert "weights" in processed_data
        assert "sectors" in processed_data
        assert "geographic_regions" in processed_data
        assert "market_caps" in processed_data
        assert "liquidity_scores" in processed_data
        assert "returns" in processed_data
        assert "volatilities" in processed_data
        assert "correlations" in processed_data

        assert len(processed_data["symbols"]) == 5
        assert len(processed_data["weights"]) == 5
        assert len(processed_data["sectors"]) == 5
        assert len(processed_data["geographic_regions"]) == 5
        assert len(processed_data["market_caps"]) == 5
        assert len(processed_data["liquidity_scores"]) == 5
        assert len(processed_data["returns"]) == 5
        assert len(processed_data["volatilities"]) == 5

    def test_analyze_sector_diversification(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """セクター分散分析テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        sector_analysis = scoring_system._analyze_sector_diversification(processed_data)

        assert isinstance(sector_analysis, SectorAnalysis)
        assert hasattr(sector_analysis, "sector_weights")
        assert hasattr(sector_analysis, "sector_returns")
        assert hasattr(sector_analysis, "sector_volatilities")
        assert hasattr(sector_analysis, "sector_correlations")
        assert hasattr(sector_analysis, "sector_concentration")
        assert hasattr(sector_analysis, "sector_entropy")

        assert isinstance(sector_analysis.sector_weights, dict)
        assert isinstance(sector_analysis.sector_returns, dict)
        assert isinstance(sector_analysis.sector_volatilities, dict)
        assert isinstance(sector_analysis.sector_correlations, dict)
        assert isinstance(sector_analysis.sector_concentration, float)
        assert isinstance(sector_analysis.sector_entropy, float)
        assert 0.0 <= sector_analysis.sector_entropy <= 1.0

    def test_analyze_correlation_diversification(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """相関分散分析テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        correlation_analysis = scoring_system._analyze_correlation_diversification(
            processed_data
        )

        assert isinstance(correlation_analysis, CorrelationAnalysis)
        assert hasattr(correlation_analysis, "correlation_matrix")
        assert hasattr(correlation_analysis, "average_correlation")
        assert hasattr(correlation_analysis, "max_correlation")
        assert hasattr(correlation_analysis, "min_correlation")
        assert hasattr(correlation_analysis, "correlation_entropy")
        assert hasattr(correlation_analysis, "correlation_clusters")

        assert isinstance(correlation_analysis.correlation_matrix, np.ndarray)
        assert isinstance(correlation_analysis.average_correlation, float)
        assert isinstance(correlation_analysis.max_correlation, float)
        assert isinstance(correlation_analysis.min_correlation, float)
        assert isinstance(correlation_analysis.correlation_entropy, float)
        assert isinstance(correlation_analysis.correlation_clusters, list)
        assert -1.0 <= correlation_analysis.average_correlation <= 1.0
        assert -1.0 <= correlation_analysis.max_correlation <= 1.0
        assert -1.0 <= correlation_analysis.min_correlation <= 1.0
        assert 0.0 <= correlation_analysis.correlation_entropy <= 1.0

    def test_calculate_correlation_entropy(self, scoring_system):
        """相関エントロピー計算テスト"""
        correlation_matrix = np.array(
            [[1.0, 0.5, 0.3], [0.5, 1.0, 0.4], [0.3, 0.4, 1.0]]
        )
        entropy = scoring_system._calculate_correlation_entropy(correlation_matrix)

        assert isinstance(entropy, float)
        assert 0.0 <= entropy <= 1.0
        assert np.isfinite(entropy)

    def test_perform_correlation_clustering(self, scoring_system):
        """相関クラスタリングテスト"""
        correlation_matrix = np.array(
            [[1.0, 0.8, 0.2], [0.8, 1.0, 0.3], [0.2, 0.3, 1.0]]
        )
        clusters = scoring_system._perform_correlation_clustering(correlation_matrix)

        assert isinstance(clusters, list)
        assert len(clusters) > 0
        # 全銘柄がクラスターに含まれていることを確認
        all_indices = set()
        for cluster in clusters:
            all_indices.update(cluster)
        assert len(all_indices) == correlation_matrix.shape[0]

    def test_analyze_concentration_risk(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """集中度リスク分析テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        concentration_risk = scoring_system._analyze_concentration_risk(processed_data)

        assert isinstance(concentration_risk, float)
        assert 0.0 <= concentration_risk <= 1.0
        assert np.isfinite(concentration_risk)

    def test_analyze_geographic_diversification(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """地理的分散分析テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        geographic_diversification = scoring_system._analyze_geographic_diversification(
            processed_data
        )

        assert isinstance(geographic_diversification, float)
        assert 0.0 <= geographic_diversification <= 1.0
        assert np.isfinite(geographic_diversification)

    def test_analyze_market_cap_diversification(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """時価総額分散分析テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        market_cap_diversification = scoring_system._analyze_market_cap_diversification(
            processed_data
        )

        assert isinstance(market_cap_diversification, float)
        assert 0.0 <= market_cap_diversification <= 1.0
        assert np.isfinite(market_cap_diversification)

    def test_analyze_liquidity_diversification(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """流動性分散分析テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        liquidity_diversification = scoring_system._analyze_liquidity_diversification(
            processed_data
        )

        assert isinstance(liquidity_diversification, float)
        assert 0.0 <= liquidity_diversification <= 1.0
        assert np.isfinite(liquidity_diversification)

    def test_analyze_risk_contribution_diversification(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """リスク寄与分散分析テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        correlation_analysis = scoring_system._analyze_correlation_diversification(
            processed_data
        )
        risk_contribution_diversification = (
            scoring_system._analyze_risk_contribution_diversification(
                processed_data, correlation_analysis
            )
        )

        assert isinstance(risk_contribution_diversification, float)
        assert 0.0 <= risk_contribution_diversification <= 1.0
        assert np.isfinite(risk_contribution_diversification)

    def test_calculate_entropy_score(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """エントロピースコア計算テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        entropy_score = scoring_system._calculate_entropy_score(processed_data)

        assert isinstance(entropy_score, float)
        assert 0.0 <= entropy_score <= 1.0
        assert np.isfinite(entropy_score)

    def test_calculate_herfindahl_index(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """ハーフィンダール指数計算テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        herfindahl_index = scoring_system._calculate_herfindahl_index(processed_data)

        assert isinstance(herfindahl_index, float)
        assert 0.0 <= herfindahl_index <= 1.0
        assert np.isfinite(herfindahl_index)

    def test_calculate_effective_number_of_stocks(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """実効銘柄数計算テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        effective_number = scoring_system._calculate_effective_number_of_stocks(
            processed_data
        )

        assert isinstance(effective_number, float)
        assert effective_number >= 1.0
        assert np.isfinite(effective_number)

    def test_calculate_diversification_ratio(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """分散投資比率計算テスト"""
        processed_data = scoring_system._preprocess_portfolio_data(
            sample_portfolio_weights, sample_stock_data
        )
        correlation_analysis = scoring_system._analyze_correlation_diversification(
            processed_data
        )
        diversification_ratio = scoring_system._calculate_diversification_ratio(
            processed_data, correlation_analysis
        )

        assert isinstance(diversification_ratio, float)
        assert diversification_ratio >= 0.0
        assert np.isfinite(diversification_ratio)

    def test_calculate_overall_diversification_score(self, scoring_system):
        """総合分散投資スコア計算テスト"""
        overall_score = scoring_system._calculate_overall_diversification_score(
            sector_entropy=0.8,
            correlation_entropy=0.7,
            concentration_risk=0.2,
            geographic_diversification=0.6,
            market_cap_diversification=0.7,
            liquidity_diversification=0.8,
            risk_contribution_diversification=0.75,
            entropy_score=0.8,
            effective_number_of_stocks=8.0,
        )

        assert isinstance(overall_score, float)
        assert 0.0 <= overall_score <= 1.0
        assert np.isfinite(overall_score)

    def test_calculate_diversification_score_integration(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """分散投資スコア計算統合テスト"""
        result = scoring_system.calculate_diversification_score(
            sample_portfolio_weights, sample_stock_data, None
        )

        assert isinstance(result, DiversificationMetrics)
        assert hasattr(result, "overall_score")
        assert hasattr(result, "sector_diversification")
        assert hasattr(result, "correlation_diversification")
        assert hasattr(result, "concentration_risk")
        assert hasattr(result, "geographic_diversification")
        assert hasattr(result, "market_cap_diversification")
        assert hasattr(result, "liquidity_diversification")
        assert hasattr(result, "risk_contribution_diversification")
        assert hasattr(result, "entropy_score")
        assert hasattr(result, "herfindahl_index")
        assert hasattr(result, "effective_number_of_stocks")
        assert hasattr(result, "diversification_ratio")

        # 各スコアが適切な範囲内であることを確認
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.sector_diversification <= 1.0
        assert 0.0 <= result.correlation_diversification <= 1.0
        assert 0.0 <= result.concentration_risk <= 1.0
        assert 0.0 <= result.geographic_diversification <= 1.0
        assert 0.0 <= result.market_cap_diversification <= 1.0
        assert 0.0 <= result.liquidity_diversification <= 1.0
        assert 0.0 <= result.risk_contribution_diversification <= 1.0
        assert 0.0 <= result.entropy_score <= 1.0
        assert 0.0 <= result.herfindahl_index <= 1.0
        assert result.effective_number_of_stocks >= 1.0
        assert result.diversification_ratio >= 0.0

    def test_generate_diversification_recommendations(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """分散投資推奨事項生成テスト"""
        diversification_metrics = scoring_system.calculate_diversification_score(
            sample_portfolio_weights, sample_stock_data, None
        )

        recommendations = scoring_system.generate_diversification_recommendations(
            diversification_metrics, None
        )

        assert isinstance(recommendations, dict)
        assert "overall_assessment" in recommendations
        assert "detailed_analysis" in recommendations
        assert "action_items" in recommendations
        assert "warnings" in recommendations
        assert "timestamp" in recommendations

        # 全体評価の確認
        overall_assessment = recommendations["overall_assessment"]
        assert "score" in overall_assessment
        assert "grade" in overall_assessment
        assert "status" in overall_assessment
        assert 0.0 <= overall_assessment["score"] <= 1.0
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
        assert overall_assessment["status"] in ["EXCELLENT", "GOOD", "FAIR", "POOR"]

        # 詳細分析の確認
        detailed_analysis = recommendations["detailed_analysis"]
        assert "sector_diversification" in detailed_analysis
        assert "correlation_diversification" in detailed_analysis
        assert "concentration_risk" in detailed_analysis

        # アクションアイテムと警告の確認
        assert isinstance(recommendations["action_items"], list)
        assert isinstance(recommendations["warnings"], list)

    def test_get_diversification_grade(self, scoring_system):
        """分散投資グレード取得テスト"""
        assert scoring_system._get_diversification_grade(0.95) == "A+"
        assert scoring_system._get_diversification_grade(0.85) == "A"
        assert scoring_system._get_diversification_grade(0.75) == "B+"
        assert scoring_system._get_diversification_grade(0.65) == "B"
        assert scoring_system._get_diversification_grade(0.55) == "C"
        assert scoring_system._get_diversification_grade(0.45) == "D"

    def test_get_diversification_status(self, scoring_system):
        """分散投資ステータス取得テスト"""
        assert scoring_system._get_diversification_status(0.85) == "EXCELLENT"
        assert scoring_system._get_diversification_status(0.65) == "GOOD"
        assert scoring_system._get_diversification_status(0.45) == "FAIR"
        assert scoring_system._get_diversification_status(0.25) == "POOR"

    def test_get_sector_recommendation(self, scoring_system):
        """セクター推奨事項取得テスト"""
        assert "良好" in scoring_system._get_sector_recommendation(0.85)
        assert "改善" in scoring_system._get_sector_recommendation(0.65)
        assert "不十分" in scoring_system._get_sector_recommendation(0.45)

    def test_get_correlation_recommendation(self, scoring_system):
        """相関推奨事項取得テスト"""
        assert "良好" in scoring_system._get_correlation_recommendation(0.85)
        assert "改善" in scoring_system._get_correlation_recommendation(0.65)
        assert "不十分" in scoring_system._get_correlation_recommendation(0.45)

    def test_get_concentration_recommendation(self, scoring_system):
        """集中度推奨事項取得テスト"""
        assert "低い" in scoring_system._get_concentration_recommendation(0.15)
        assert "注意" in scoring_system._get_concentration_recommendation(0.35)
        assert "高い" in scoring_system._get_concentration_recommendation(0.55)

    def test_error_handling(self, scoring_system):
        """エラーハンドリングテスト"""
        # 空のデータでのテスト
        empty_weights = {}
        empty_stock_data = []

        result = scoring_system.calculate_diversification_score(
            empty_weights, empty_stock_data, None
        )

        # エラーが発生しても適切に処理されることを確認
        assert isinstance(result, DiversificationMetrics)
        assert 0.0 <= result.overall_score <= 1.0

    def test_edge_cases(self, scoring_system):
        """エッジケーステスト"""
        # 単一銘柄のテスト
        single_stock_weights = {"AAPL": 1.0}
        single_stock_data = [
            {
                "symbol": "AAPL",
                "sector": "Technology",
                "region": "US",
                "market_cap": 2500000000000,
                "liquidity_score": 1000000,
                "price_data": [
                    {"close": 145.0, "volume": 1000000},
                    {"close": 147.0, "volume": 1100000},
                    {"close": 150.0, "volume": 1200000},
                ],
            }
        ]

        result = scoring_system.calculate_diversification_score(
            single_stock_weights, single_stock_data, None
        )
        assert isinstance(result, DiversificationMetrics)
        assert 0.0 <= result.overall_score <= 1.0

    def test_performance_metrics(
        self, scoring_system, sample_portfolio_weights, sample_stock_data
    ):
        """パフォーマンスメトリクステスト"""
        result = scoring_system.calculate_diversification_score(
            sample_portfolio_weights, sample_stock_data, None
        )

        # パフォーマンスメトリクスが適切に計算されることを確認
        assert result.overall_score >= 0.0
        assert result.sector_diversification >= 0.0
        assert result.correlation_diversification >= 0.0
        assert result.concentration_risk >= 0.0
        assert result.geographic_diversification >= 0.0
        assert result.market_cap_diversification >= 0.0
        assert result.liquidity_diversification >= 0.0
        assert result.risk_contribution_diversification >= 0.0
        assert result.entropy_score >= 0.0
        assert result.herfindahl_index >= 0.0
        assert result.effective_number_of_stocks >= 1.0
        assert result.diversification_ratio >= 0.0
