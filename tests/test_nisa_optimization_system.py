#!/usr/bin/env python3
"""
新NISA最適化システムのテスト
非課税枠利用率90%以上を目標としたテストケース
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, date
import sys
import os

# パスの追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接インポート（依存関係の問題を回避）
import importlib.util


def load_module_from_path(module_name, file_path):
    """ファイルパスからモジュールを読み込む"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# モジュールの読み込み
nisa_quota_manager = load_module_from_path(
    "nisa_quota_manager", "core/nisa_quota_manager.py"
)
nisa_tax_calculator = load_module_from_path(
    "nisa_tax_calculator", "core/nisa_tax_calculator.py"
)
nisa_optimization_system = load_module_from_path(
    "nisa_optimization_system", "core/nisa_optimization_system.py"
)

# クラスの取得
NisaQuotaManager = nisa_quota_manager.NisaQuotaManager
NisaOptimizationEngine = nisa_quota_manager.NisaOptimizationEngine
NisaQuotaStatus = nisa_quota_manager.NisaQuotaStatus
NisaTransaction = nisa_quota_manager.NisaTransaction
NisaPosition = nisa_quota_manager.NisaPosition
NisaPortfolio = nisa_quota_manager.NisaPortfolio

NisaTaxCalculator = nisa_tax_calculator.NisaTaxCalculator
TaxCalculation = nisa_tax_calculator.TaxCalculation
TaxOptimization = nisa_tax_calculator.TaxOptimization

NisaOptimizationSystem = nisa_optimization_system.NisaOptimizationSystem
OptimizationRecommendation = nisa_optimization_system.OptimizationRecommendation
AIInvestmentStrategy = nisa_optimization_system.AIInvestmentStrategy
OptimizationReport = nisa_optimization_system.OptimizationReport


class TestNisaQuotaManager(unittest.TestCase):
    """NISA枠管理システムのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = {"nisa_data_file": "test_data/nisa_test.json"}
        self.quota_manager = NisaQuotaManager(self.config)

    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.quota_manager.growth_annual_limit, 2400000)
        self.assertEqual(self.quota_manager.accumulation_annual_limit, 400000)
        self.assertEqual(self.quota_manager.target_utilization_rate, 90.0)
        self.assertEqual(self.quota_manager.tax_rate, 0.30)

    def test_get_quota_status(self):
        """枠利用状況取得テスト"""
        quota_status = self.quota_manager.get_quota_status()

        self.assertIsInstance(quota_status, NisaQuotaStatus)
        self.assertIn("growth_investment", quota_status.__dict__)
        self.assertIn("accumulation_investment", quota_status.__dict__)
        self.assertIn("optimization", quota_status.__dict__)

    def test_add_transaction(self):
        """取引記録追加テスト"""
        transaction = NisaTransaction(
            id="test_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2000.0,
            amount=200000.0,
            quota_type="GROWTH",
            transaction_date="2024-01-15",
            tax_savings=60000.0,
            efficiency_score=85.0,
            strategy="GROWTH_FOCUSED",
            risk_level="MEDIUM",
        )

        result = self.quota_manager.add_transaction(transaction)

        self.assertIsInstance(result, dict)
        self.assertIn("success", result)

    def test_get_portfolio(self):
        """ポートフォリオ取得テスト"""
        portfolio = self.quota_manager.get_portfolio()

        self.assertIsInstance(portfolio, NisaPortfolio)
        self.assertIsInstance(portfolio.positions, list)
        self.assertIsInstance(portfolio.total_value, (int, float))
        self.assertIsInstance(portfolio.total_cost, (int, float))

    def test_get_quota_optimization(self):
        """枠最適化提案テスト"""
        optimization = self.quota_manager.get_quota_optimization()

        self.assertIsInstance(optimization, dict)
        self.assertIn("recommendations", optimization)
        self.assertIn("risk_analysis", optimization)
        self.assertIn("tax_optimization", optimization)

    def test_optimization_metrics_calculation(self):
        """最適化指標計算テスト"""
        quotas = {
            "growth_investment": {
                "utilization_rate": 75.0,
                "used_amount": 1800000,
                "available_amount": 600000,
            },
            "accumulation_investment": {
                "utilization_rate": 80.0,
                "used_amount": 320000,
                "available_amount": 80000,
            },
        }

        optimization = self.quota_manager._calculate_optimization_metrics(quotas)

        self.assertIsInstance(optimization, dict)
        self.assertIn("overall_utilization_rate", optimization)
        self.assertIn("target_utilization_rate", optimization)
        self.assertIn("efficiency_score", optimization)
        self.assertIn("optimization_level", optimization)

        # 利用率の計算確認
        expected_utilization = (75.0 + 80.0) / 2
        self.assertEqual(optimization["overall_utilization_rate"], expected_utilization)


class TestNisaOptimizationEngine(unittest.TestCase):
    """NISA最適化エンジンのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.quota_manager = Mock()
        self.quota_manager.target_utilization_rate = 90.0
        self.quota_manager.tax_rate = 0.30
        self.optimization_engine = NisaOptimizationEngine(self.quota_manager)

    def test_calculate_optimization_score(self):
        """最適化スコア計算テスト"""
        quota_status = NisaQuotaStatus(
            growth_investment={"utilization_rate": 80.0},
            accumulation_investment={"utilization_rate": 70.0},
            quota_reuse={},
            optimization={},
            last_updated=datetime.now().isoformat(),
        )

        score = self.optimization_engine.calculate_optimization_score(quota_status)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_get_optimization_recommendations(self):
        """最適化推奨事項取得テスト"""
        quota_status = NisaQuotaStatus(
            growth_investment={"utilization_rate": 60.0, "available_amount": 960000},
            accumulation_investment={
                "utilization_rate": 50.0,
                "available_amount": 200000,
            },
            quota_reuse={},
            optimization={},
            last_updated=datetime.now().isoformat(),
        )

        recommendations = self.optimization_engine.get_optimization_recommendations(
            quota_status
        )

        self.assertIsInstance(recommendations, dict)
        self.assertIn("growth_quota", recommendations)
        self.assertIn("accumulation_quota", recommendations)
        self.assertIn("overall", recommendations)

    def test_time_efficiency_calculation(self):
        """時間効率計算テスト"""
        efficiency = self.optimization_engine._calculate_time_efficiency()

        self.assertIsInstance(efficiency, float)
        self.assertGreaterEqual(efficiency, 0.0)
        self.assertLessEqual(efficiency, 1.0)


class TestNisaTaxCalculator(unittest.TestCase):
    """NISA税務計算システムのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = {"income_tax_rate": 0.20, "resident_tax_rate": 0.10}
        self.tax_calculator = NisaTaxCalculator(self.config)

    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.tax_calculator.income_tax_rate, 0.20)
        self.assertEqual(self.tax_calculator.resident_tax_rate, 0.10)
        self.assertEqual(self.tax_calculator.total_tax_rate, 0.30)
        self.assertEqual(self.tax_calculator.target_utilization_rate, 90.0)

    def test_calculate_tax_savings(self):
        """税務計算テスト"""
        quota_status = {
            "growth_investment": {"used_amount": 1800000, "utilization_rate": 75.0},
            "accumulation_investment": {
                "used_amount": 300000,
                "utilization_rate": 75.0,
            },
        }

        portfolio = {
            "positions": [],
            "total_value": 2100000,
            "total_cost": 2100000,
            "unrealized_profit_loss": 0,
            "realized_profit_loss": 0,
        }

        tax_calculation = self.tax_calculator.calculate_tax_savings(
            quota_status, portfolio
        )

        self.assertIsInstance(tax_calculation, TaxCalculation)
        self.assertIn("current_year", tax_calculation.__dict__)
        self.assertIn("next_year", tax_calculation.__dict__)
        self.assertIn("tax_savings", tax_calculation.__dict__)
        self.assertIn("optimization", tax_calculation.__dict__)
        self.assertIn("efficiency_score", tax_calculation.__dict__)

    def test_get_tax_optimization(self):
        """税務最適化テスト"""
        quota_status = {
            "growth_investment": {"utilization_rate": 60.0, "used_amount": 1440000},
            "accumulation_investment": {
                "utilization_rate": 50.0,
                "used_amount": 200000,
            },
        }

        portfolio = {
            "positions": [],
            "total_value": 1640000,
            "total_cost": 1640000,
            "unrealized_profit_loss": 0,
        }

        optimization = self.tax_calculator.get_tax_optimization(quota_status, portfolio)

        self.assertIsInstance(optimization, TaxOptimization)
        self.assertIsInstance(optimization.recommended_actions, list)
        self.assertIsInstance(optimization.potential_tax_savings, (int, float))
        self.assertIsInstance(optimization.optimization_score, (int, float))
        self.assertIn(optimization.priority_level, ["HIGH", "MEDIUM", "LOW", "UNKNOWN"])

    def test_calculate_optimization_metrics(self):
        """最適化指標計算テスト"""
        quota_status = {
            "growth_investment": {"used_amount": 1800000, "utilization_rate": 75.0},
            "accumulation_investment": {
                "used_amount": 300000,
                "utilization_rate": 75.0,
            },
        }

        portfolio = {"positions": [], "unrealized_profit_loss": 0}

        metrics = self.tax_calculator._calculate_optimization_metrics(
            quota_status, portfolio
        )

        self.assertIsInstance(metrics, dict)
        self.assertIn("overall_utilization", metrics)
        self.assertIn("target_utilization", metrics)
        self.assertIn("target_achievement", metrics)
        self.assertIn("tax_efficiency", metrics)
        self.assertIn("optimization_level", metrics)
        self.assertIn("improvement_potential", metrics)

    def test_calculate_efficiency_score(self):
        """効率スコア計算テスト"""
        quota_status = {
            "growth_investment": {"utilization_rate": 80.0},
            "accumulation_investment": {"utilization_rate": 70.0},
        }

        portfolio = {
            "positions": [{"symbol": "7203"}, {"symbol": "6758"}],
            "unrealized_profit_loss": 100000,
            "total_cost": 2000000,
        }

        score = self.tax_calculator._calculate_efficiency_score(quota_status, portfolio)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)


class TestNisaOptimizationSystem(unittest.TestCase):
    """NISA最適化システムのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = {}
        self.optimization_system = NisaOptimizationSystem(self.config)

    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.optimization_system.target_utilization_rate, 90.0)
        self.assertEqual(self.optimization_system.optimization_threshold, 0.85)
        self.assertEqual(self.optimization_system.tax_rate, 0.30)
        self.assertIsInstance(self.optimization_system.ai_strategies, list)
        self.assertGreater(len(self.optimization_system.ai_strategies), 0)

    def test_generate_optimization_report(self):
        """最適化レポート生成テスト"""
        quota_status = {
            "growth_investment": {
                "utilization_rate": 70.0,
                "used_amount": 1680000,
                "available_amount": 720000,
            },
            "accumulation_investment": {
                "utilization_rate": 60.0,
                "used_amount": 240000,
                "available_amount": 160000,
            },
        }

        portfolio = {
            "positions": [
                {"symbol": "7203", "quota_type": "GROWTH"},
                {"symbol": "6758", "quota_type": "GROWTH"},
                {"symbol": "9984", "quota_type": "ACCUMULATION"},
            ],
            "total_value": 2000000,
            "total_cost": 1920000,
            "unrealized_profit_loss": 80000,
        }

        report = self.optimization_system.generate_optimization_report(
            quota_status, portfolio
        )

        self.assertIsInstance(report, OptimizationReport)
        self.assertIsInstance(report.current_score, (int, float))
        self.assertIsInstance(report.target_score, (int, float))
        self.assertIsInstance(report.improvement_potential, (int, float))
        self.assertIsInstance(report.recommendations, list)
        self.assertIsInstance(report.ai_strategies, list)
        self.assertIsInstance(report.risk_analysis, dict)
        self.assertIsInstance(report.tax_optimization, dict)
        self.assertIsInstance(report.implementation_plan, dict)

    def test_calculate_current_score(self):
        """現在スコア計算テスト"""
        quota_status = {
            "growth_investment": {"utilization_rate": 80.0},
            "accumulation_investment": {"utilization_rate": 70.0},
        }

        portfolio = {
            "positions": [{"symbol": "7203"}, {"symbol": "6758"}],
            "total_value": 2000000,
            "total_cost": 1900000,
            "unrealized_profit_loss": 100000,
        }

        score = self.optimization_system._calculate_current_score(
            quota_status, portfolio
        )

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_generate_recommendations(self):
        """推奨事項生成テスト"""
        quota_status = {
            "growth_investment": {
                "utilization_rate": 60.0,
                "used_amount": 1440000,
                "available_amount": 960000,
            },
            "accumulation_investment": {
                "utilization_rate": 50.0,
                "used_amount": 200000,
                "available_amount": 200000,
            },
        }

        portfolio = {
            "positions": [{"symbol": "7203"}],
            "total_value": 1640000,
            "total_cost": 1640000,
            "unrealized_profit_loss": 0,
        }

        recommendations = self.optimization_system._generate_recommendations(
            quota_status, portfolio
        )

        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIsInstance(rec, OptimizationRecommendation)
            self.assertIn(rec.priority, ["HIGH", "MEDIUM", "LOW"])
            self.assertIsInstance(rec.expected_impact, (int, float))
            self.assertIsInstance(rec.potential_savings, (int, float))

    def test_generate_ai_strategies(self):
        """AI戦略生成テスト"""
        quota_status = {
            "growth_investment": {"utilization_rate": 70.0},
            "accumulation_investment": {"utilization_rate": 60.0},
        }

        portfolio = {
            "positions": [{"symbol": "7203"}, {"symbol": "6758"}, {"symbol": "9984"}],
            "total_value": 2000000,
            "total_cost": 1900000,
            "unrealized_profit_loss": 100000,
        }

        strategies = self.optimization_system._generate_ai_strategies(
            quota_status, portfolio
        )

        self.assertIsInstance(strategies, list)
        for strategy in strategies:
            self.assertIsInstance(strategy, AIInvestmentStrategy)
            self.assertIn(strategy.risk_level, ["LOW", "MEDIUM", "HIGH"])
            self.assertIsInstance(strategy.expected_return, (int, float))
            self.assertIsInstance(strategy.confidence, (int, float))
            self.assertIsInstance(strategy.optimization_score, (int, float))

    def test_analyze_risk(self):
        """リスク分析テスト"""
        portfolio = {
            "positions": [
                {"symbol": "7203", "quota_type": "GROWTH"},
                {"symbol": "6758", "quota_type": "GROWTH"},
                {"symbol": "9984", "quota_type": "ACCUMULATION"},
                {"symbol": "6861", "quota_type": "GROWTH"},
                {"symbol": "7974", "quota_type": "ACCUMULATION"},
            ]
        }

        risk_analysis = self.optimization_system._analyze_risk(portfolio)

        self.assertIsInstance(risk_analysis, dict)
        self.assertIn("diversification_score", risk_analysis)
        self.assertIn("sector_concentration", risk_analysis)
        self.assertIn("risk_level", risk_analysis)
        self.assertIn("recommendations", risk_analysis)
        self.assertIn(risk_analysis["risk_level"], ["LOW", "MEDIUM", "HIGH"])

    def test_calculate_tax_optimization(self):
        """税務最適化計算テスト"""
        quota_status = {
            "growth_investment": {"used_amount": 1800000, "available_amount": 600000},
            "accumulation_investment": {
                "used_amount": 300000,
                "available_amount": 100000,
            },
        }

        portfolio = {
            "positions": [],
            "total_value": 2100000,
            "total_cost": 2100000,
            "unrealized_profit_loss": 0,
        }

        tax_optimization = self.optimization_system._calculate_tax_optimization(
            quota_status, portfolio
        )

        self.assertIsInstance(tax_optimization, dict)
        self.assertIn("current_tax_savings", tax_optimization)
        self.assertIn("potential_tax_savings", tax_optimization)
        self.assertIn("optimization_score", tax_optimization)
        self.assertIn("tax_rate", tax_optimization)
        self.assertIn("recommendations", tax_optimization)

        # 税務節約額の計算確認
        expected_current = 2100000 * 0.30
        self.assertEqual(tax_optimization["current_tax_savings"], expected_current)

    def test_create_implementation_plan(self):
        """実装計画作成テスト"""
        recommendations = [
            OptimizationRecommendation(
                type="GROWTH_QUOTA_OPTIMIZATION",
                priority="HIGH",
                title="成長投資枠の活用促進",
                description="成長投資枠の活用率を向上させる",
                expected_impact=72.0,
                implementation_difficulty="MEDIUM",
                timeframe="1-3ヶ月",
                required_action="成長株への投資を増やす",
                potential_savings=72.0,
            ),
            OptimizationRecommendation(
                type="ACCUMULATION_QUOTA_OPTIMIZATION",
                priority="MEDIUM",
                title="つみたて投資枠の活用促進",
                description="つみたて投資枠の活用率を向上させる",
                expected_impact=12.0,
                implementation_difficulty="LOW",
                timeframe="3-6ヶ月",
                required_action="積立投資の開始・増額",
                potential_savings=12.0,
            ),
        ]

        ai_strategies = [
            AIInvestmentStrategy(
                strategy_name="バランス型投資戦略",
                description="成長株と安定株のバランスを取った投資戦略",
                risk_level="MEDIUM",
                expected_return=8.0,
                timeframe="3-5年",
                confidence=0.85,
                growth_quota_allocation={"growth_stocks": 0.6, "value_stocks": 0.4},
                accumulation_quota_allocation={"index_funds": 0.7, "bond_funds": 0.3},
                optimization_score=85.0,
            )
        ]

        plan = self.optimization_system._create_implementation_plan(
            recommendations, ai_strategies
        )

        self.assertIsInstance(plan, dict)
        self.assertIn("high_priority_actions", plan)
        self.assertIn("medium_priority_actions", plan)
        self.assertIn("low_priority_actions", plan)
        self.assertIn("recommended_strategy", plan)
        self.assertIn("implementation_timeline", plan)
        self.assertIn("success_metrics", plan)


class TestIntegration(unittest.TestCase):
    """統合テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = {"nisa_data_file": "test_data/nisa_integration_test.json"}
        self.quota_manager = NisaQuotaManager(self.config)
        self.tax_calculator = NisaTaxCalculator(self.config)
        self.optimization_system = NisaOptimizationSystem(self.config)

    def test_end_to_end_optimization(self):
        """エンドツーエンド最適化テスト"""
        # 1. 初期状態の確認
        quota_status = self.quota_manager.get_quota_status()
        self.assertIsInstance(quota_status, NisaQuotaStatus)

        # 2. 取引の追加
        transaction = NisaTransaction(
            id="test_integration_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2000.0,
            amount=200000.0,
            quota_type="GROWTH",
            transaction_date="2024-01-15",
            tax_savings=60000.0,
            efficiency_score=85.0,
            strategy="GROWTH_FOCUSED",
            risk_level="MEDIUM",
        )

        result = self.quota_manager.add_transaction(transaction)
        self.assertIn("success", result)

        # 3. ポートフォリオの取得
        portfolio = self.quota_manager.get_portfolio()
        self.assertIsInstance(portfolio, NisaPortfolio)

        # 4. 税務計算
        quota_data = quota_status.__dict__
        portfolio_data = portfolio.__dict__
        tax_calculation = self.tax_calculator.calculate_tax_savings(
            quota_data, portfolio_data
        )
        self.assertIsInstance(tax_calculation, TaxCalculation)

        # 5. 最適化レポートの生成
        optimization_report = self.optimization_system.generate_optimization_report(
            quota_data, portfolio_data
        )
        self.assertIsInstance(optimization_report, OptimizationReport)

        # 6. 最適化スコアの確認
        self.assertGreaterEqual(optimization_report.current_score, 0.0)
        self.assertLessEqual(optimization_report.current_score, 100.0)
        self.assertEqual(optimization_report.target_score, 90.0)

        # 7. 推奨事項の確認
        self.assertIsInstance(optimization_report.recommendations, list)
        self.assertIsInstance(optimization_report.ai_strategies, list)

        # 8. 実装計画の確認
        self.assertIsInstance(optimization_report.implementation_plan, dict)
        self.assertIn("high_priority_actions", optimization_report.implementation_plan)
        self.assertIn("success_metrics", optimization_report.implementation_plan)


if __name__ == "__main__":
    # テストの実行
    unittest.main(verbosity=2)
