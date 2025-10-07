#!/usr/bin/env python3
"""
NISA税務計算システムの単体テスト
"""

import pytest

from core.nisa_tax_calculator import NisaTaxCalculator, TaxCalculation, TaxOptimization


class TestNisaTaxCalculator:
    """NISA税務計算システムのテスト"""

    @pytest.fixture
    def tax_calculator(self):
        """税務計算システムのインスタンス"""
        config = {"income_tax_rate": 0.20, "resident_tax_rate": 0.10}
        return NisaTaxCalculator(config)

    @pytest.fixture
    def sample_quota_status(self):
        """サンプル枠状況"""
        return {
            "growth_investment": {
                "used_amount": 1200000.0,  # 120万円
                "available_amount": 1200000.0,
                "utilization_rate": 50.0,
            },
            "accumulation_investment": {
                "used_amount": 200000.0,  # 20万円
                "available_amount": 200000.0,
                "utilization_rate": 50.0,
            },
            "quota_reuse": {
                "growth_available": 100000.0,
                "accumulation_available": 50000.0,
            },
        }

    @pytest.fixture
    def sample_portfolio(self):
        """サンプルポートフォリオ"""
        return {
            "total_value": 1500000.0,
            "total_cost": 1400000.0,
            "unrealized_profit_loss": 100000.0,
            "realized_profit_loss": 50000.0,
            "tax_free_profit_loss": 80000.0,
        }

    def test_initialization(self, tax_calculator):
        """初期化テスト"""
        assert tax_calculator.income_tax_rate == 0.20
        assert tax_calculator.resident_tax_rate == 0.10
        assert tax_calculator.total_tax_rate == 0.30
        assert tax_calculator.growth_annual_limit == 2400000
        assert tax_calculator.accumulation_annual_limit == 400000

    def test_calculate_tax_savings(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """税務計算テスト"""
        result = tax_calculator.calculate_tax_savings(
            sample_quota_status, sample_portfolio
        )

        assert isinstance(result, TaxCalculation)
        assert "current_year" in result.__dict__
        assert "next_year" in result.__dict__
        assert "tax_savings" in result.__dict__
        assert result.total_tax_free_amount > 0
        assert result.effective_tax_rate > 0

    def test_calculate_current_year_tax(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """現在年度税務計算テスト"""
        current_year = tax_calculator._calculate_current_year_tax(
            sample_quota_status, sample_portfolio
        )

        assert current_year["growth_quota_used"] == 1200000.0
        assert current_year["accumulation_quota_used"] == 200000.0
        assert current_year["total_tax_free_amount"] == 1400000.0
        assert current_year["hypothetical_tax"] > 0
        assert current_year["tax_savings"] > 0

    def test_calculate_next_year_tax(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """翌年度税務計算テスト"""
        next_year = tax_calculator._calculate_next_year_tax(
            sample_quota_status, sample_portfolio
        )

        assert next_year["available_growth_quota"] == 2500000.0  # 2400000 + 100000
        assert next_year["available_accumulation_quota"] == 450000.0  # 400000 + 50000
        assert next_year["reusable_quota"] == 150000.0
        assert next_year["total_available"] == 2950000.0

    def test_calculate_tax_savings_amount(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """税務節約額計算テスト"""
        tax_savings = tax_calculator._calculate_tax_savings(
            sample_quota_status, sample_portfolio
        )

        assert tax_savings["estimated_tax_savings"] > 0
        assert tax_savings["tax_rate"] == 0.30
        assert tax_savings["effective_tax_rate"] == 0.30
        assert tax_savings["annual_savings"] > 0
        assert tax_savings["lifetime_savings"] > 0

    def test_calculate_total_tax_free_amount(self, tax_calculator, sample_quota_status):
        """総非課税枠額計算テスト"""
        total_amount = tax_calculator._calculate_total_tax_free_amount(
            sample_quota_status
        )

        assert total_amount == 1400000.0  # 1200000 + 200000

    def test_calculate_effective_tax_rate(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """実効税率計算テスト"""
        effective_rate = tax_calculator._calculate_effective_tax_rate(
            sample_quota_status, sample_portfolio
        )

        assert effective_rate > 0
        assert effective_rate <= tax_calculator.total_tax_rate

    def test_get_tax_optimization(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """税務最適化提案テスト"""
        optimization = tax_calculator.get_tax_optimization(
            sample_quota_status, sample_portfolio
        )

        assert isinstance(optimization, TaxOptimization)
        assert len(optimization.recommended_actions) >= 0
        assert optimization.potential_tax_savings >= 0
        assert optimization.optimization_score >= 0
        assert optimization.priority_level in ["HIGH", "MEDIUM", "LOW", "UNKNOWN"]

    def test_generate_tax_recommendations(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """税務推奨事項生成テスト"""
        recommendations = tax_calculator._generate_tax_recommendations(
            sample_quota_status, sample_portfolio
        )

        assert isinstance(recommendations, list)

        for rec in recommendations:
            assert "action" in rec
            assert "description" in rec
            assert "priority" in rec
            assert "potential_savings" in rec
            assert rec["priority"] in ["HIGH", "MEDIUM", "LOW"]

    def test_calculate_potential_tax_savings(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """潜在税務節約額計算テスト"""
        potential_savings = tax_calculator._calculate_potential_tax_savings(
            sample_quota_status, sample_portfolio
        )

        assert potential_savings >= 0
        # 利用可能枠 × 税率
        expected_savings = (1200000.0 + 200000.0) * 0.30
        assert potential_savings == expected_savings

    def test_calculate_optimization_score(
        self, tax_calculator, sample_quota_status, sample_portfolio
    ):
        """最適化スコア計算テスト"""
        score = tax_calculator._calculate_optimization_score(
            sample_quota_status, sample_portfolio
        )

        assert score >= 0
        assert score <= 100

    def test_determine_priority_level(self, tax_calculator):
        """優先度レベル判定テスト"""
        assert tax_calculator._determine_priority_level(85.0) == "HIGH"
        assert tax_calculator._determine_priority_level(70.0) == "MEDIUM"
        assert tax_calculator._determine_priority_level(50.0) == "LOW"
        assert tax_calculator._determine_priority_level(-10.0) == "LOW"

    def test_calculate_annual_tax_report(self, tax_calculator):
        """年間税務レポート計算テスト"""
        transactions = [
            {"type": "BUY", "amount": 100000.0, "quota_type": "GROWTH"},
            {"type": "SELL", "amount": 50000.0, "quota_type": "GROWTH"},
        ]

        quota_status = {
            "growth_investment": {"used_amount": 50000.0},
            "accumulation_investment": {"used_amount": 0.0},
        }

        report = tax_calculator.calculate_annual_tax_report(transactions, quota_status)

        assert "annual_summary" in report
        assert "tax_effectiveness" in report
        assert "recommendations" in report
        assert "report_date" in report

        # 年間サマリーの検証
        annual_summary = report["annual_summary"]
        assert annual_summary["total_buy_amount"] == 100000.0
        assert annual_summary["total_sell_amount"] == 50000.0
        assert annual_summary["net_investment"] == 50000.0

    def test_summarize_annual_transactions(self, tax_calculator):
        """年間取引集計テスト"""
        transactions = [
            {"type": "BUY", "amount": 100000.0, "quota_type": "GROWTH"},
            {"type": "BUY", "amount": 50000.0, "quota_type": "ACCUMULATION"},
            {"type": "SELL", "amount": 30000.0, "quota_type": "GROWTH"},
            {"type": "BUY", "amount": 20000.0, "quota_type": "GROWTH"},
        ]

        summary = tax_calculator._summarize_annual_transactions(transactions)

        assert summary["total_buy_amount"] == 170000.0
        assert summary["total_sell_amount"] == 30000.0
        assert summary["net_investment"] == 140000.0
        assert summary["growth_transactions"] == 3
        assert summary["accumulation_transactions"] == 1
        assert summary["total_transactions"] == 4

    def test_calculate_tax_effectiveness(self, tax_calculator):
        """税務効果計算テスト"""
        annual_summary = {"net_investment": 100000.0}
        quota_status = {
            "growth_investment": {"used_amount": 80000.0},
            "accumulation_investment": {"used_amount": 20000.0},
        }

        effectiveness = tax_calculator._calculate_tax_effectiveness(
            annual_summary, quota_status
        )

        assert effectiveness["tax_effectiveness_rate"] == 100.0  # 100000 / 100000 * 100
        assert effectiveness["tax_savings"] > 0
        assert effectiveness["efficiency_score"] == 100.0

    def test_generate_annual_recommendations(self, tax_calculator):
        """年間推奨事項生成テスト"""
        annual_summary = {"total_transactions": 3}
        quota_status = {
            "growth_investment": {"utilization_rate": 30.0},
            "accumulation_investment": {"utilization_rate": 20.0},
        }

        recommendations = tax_calculator._generate_annual_recommendations(
            annual_summary, quota_status
        )

        assert isinstance(recommendations, list)

        for rec in recommendations:
            assert "type" in rec
            assert "description" in rec
            assert "priority" in rec

    def test_empty_data_handling(self, tax_calculator):
        """空データ処理テスト"""
        empty_quota_status = {
            "growth_investment": {"used_amount": 0.0},
            "accumulation_investment": {"used_amount": 0.0},
        }
        empty_portfolio = {
            "total_value": 0.0,
            "total_cost": 0.0,
            "unrealized_profit_loss": 0.0,
        }

        result = tax_calculator.calculate_tax_savings(
            empty_quota_status, empty_portfolio
        )

        assert result.total_tax_free_amount == 0.0
        assert result.effective_tax_rate == 0.0

    def test_error_handling(self, tax_calculator):
        """エラーハンドリングテスト"""
        # 無効なデータ
        invalid_quota_status = None
        invalid_portfolio = None

        result = tax_calculator.calculate_tax_savings(
            invalid_quota_status, invalid_portfolio
        )

        assert result.total_tax_free_amount == 0.0
        assert result.effective_tax_rate == 0.0

    def test_tax_rate_calculation_accuracy(self, tax_calculator):
        """税率計算精度テスト"""
        # 100万円の非課税枠使用
        quota_status = {
            "growth_investment": {"used_amount": 1000000.0},
            "accumulation_investment": {"used_amount": 0.0},
        }
        portfolio = {"unrealized_profit_loss": 0.0}

        result = tax_calculator.calculate_tax_savings(quota_status, portfolio)

        # 税務節約額 = 100万円 × 30% = 30万円
        expected_savings = 1000000.0 * 0.30
        assert (
            abs(result.tax_savings["estimated_tax_savings"] - expected_savings) < 0.01
        )

    def test_optimization_score_edge_cases(self, tax_calculator):
        """最適化スコア境界値テスト"""
        # 100%活用の場合
        high_utilization_status = {
            "growth_investment": {"utilization_rate": 100.0},
            "accumulation_investment": {"utilization_rate": 100.0},
        }
        high_diversification_portfolio = {
            "positions": [{"symbol": f"STOCK_{i}"} for i in range(10)]
        }

        score = tax_calculator._calculate_optimization_score(
            high_utilization_status, high_diversification_portfolio
        )

        assert score > 0
        assert score <= 100

    def test_recommendation_priority_logic(self, tax_calculator):
        """推奨事項優先度ロジックテスト"""
        # 低活用率の場合
        low_utilization_status = {
            "growth_investment": {"utilization_rate": 20.0},
            "accumulation_investment": {"utilization_rate": 10.0},
        }
        portfolio = {"unrealized_profit_loss": 0.0}

        recommendations = tax_calculator._generate_tax_recommendations(
            low_utilization_status, portfolio
        )

        # 低活用率の場合は推奨事項が生成されるはず
        growth_recs = [r for r in recommendations if "GROWTH" in r.get("action", "")]
        accumulation_recs = [
            r for r in recommendations if "ACCUMULATION" in r.get("action", "")
        ]

        assert len(growth_recs) > 0 or len(accumulation_recs) > 0
