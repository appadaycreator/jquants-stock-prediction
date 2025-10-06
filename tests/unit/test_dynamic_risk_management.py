#!/usr/bin/env python3
"""
動的リスク管理システムのテスト
記事の手法を超える高度なリスク管理機能のテスト
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.dynamic_risk_management import (
    DynamicRiskManager,
    RiskLevel,
    RiskMetrics,
    DynamicRiskAdjustment,
)


class TestDynamicRiskManager(unittest.TestCase):
    """動的リスク管理システムのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = {
            "risk_limits": {
                "max_position_size": 0.1,
                "max_portfolio_risk": 0.05,
                "max_drawdown_limit": 0.15,
                "var_limit_95": 0.02,
                "var_limit_99": 0.05,
            },
            "dynamic_adjustments": {
                "volatility_sensitivity": 0.5,
                "market_regime_weight": 0.3,
                "confidence_weight": 0.4,
                "liquidity_weight": 0.2,
                "time_decay_factor": 0.95,
            },
            "stop_loss": {
                "base_stop_loss": 0.05,
                "volatility_multiplier": 2.0,
                "confidence_multiplier": 1.5,
                "min_stop_loss": 0.02,
                "max_stop_loss": 0.15,
            },
            "take_profit": {
                "base_take_profit": 0.10,
                "risk_reward_ratio": 2.0,
                "volatility_adjustment": True,
                "confidence_adjustment": True,
            },
        }
        self.manager = DynamicRiskManager(self.config)

        # テストデータ作成
        self.stock_data = self._create_test_stock_data()
        self.market_data = self._create_test_market_data()

    def _create_test_stock_data(self) -> pd.DataFrame:
        """テスト用株価データ作成"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.02)
        volumes = np.random.randint(100000, 1000000, 100)

        return pd.DataFrame(
            {
                "Date": dates,
                "Close": prices,
                "Volume": volumes,
                "Open": prices * (1 + np.random.randn(100) * 0.01),
                "High": prices * (1 + np.abs(np.random.randn(100)) * 0.02),
                "Low": prices * (1 - np.abs(np.random.randn(100)) * 0.02),
            }
        ).set_index("Date")

    def _create_test_market_data(self) -> pd.DataFrame:
        """テスト用市場データ作成"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        np.random.seed(43)
        prices = 1000 + np.cumsum(np.random.randn(100) * 0.01)
        volumes = np.random.randint(1000000, 10000000, 100)

        return pd.DataFrame(
            {"Date": dates, "Close": prices, "Volume": volumes}
        ).set_index("Date")

    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.config["risk_limits"]["max_position_size"], 0.1)
        self.assertEqual(self.manager.config["risk_limits"]["var_limit_95"], 0.02)

    def test_calculate_risk_metrics(self):
        """リスクメトリクス計算テスト"""
        current_price = 100.0
        position_size = 0.05

        metrics = self.manager.calculate_risk_metrics(
            self.stock_data, self.market_data, current_price, position_size
        )

        self.assertIsInstance(metrics, RiskMetrics)
        self.assertGreaterEqual(metrics.var_95, 0.0)
        self.assertGreaterEqual(metrics.var_99, 0.0)
        self.assertGreaterEqual(metrics.max_drawdown, 0.0)
        self.assertIsInstance(metrics.risk_level, RiskLevel)
        self.assertGreaterEqual(metrics.position_size, 0.0)
        self.assertGreater(metrics.stop_loss, 0.0)
        self.assertGreater(metrics.take_profit, 0.0)

    def test_var_calculation(self):
        """VaR計算テスト"""
        var_95, var_99 = self.manager._calculate_var(self.stock_data)

        self.assertGreaterEqual(var_95, 0.0)
        self.assertGreaterEqual(var_99, 0.0)
        self.assertLessEqual(var_95, 1.0)
        self.assertLessEqual(var_99, 1.0)
        self.assertLessEqual(var_95, var_99)  # 95% VaR <= 99% VaR

    def test_max_drawdown_calculation(self):
        """最大ドローダウン計算テスト"""
        max_dd = self.manager._calculate_max_drawdown(self.stock_data)

        self.assertGreaterEqual(max_dd, 0.0)
        self.assertLessEqual(max_dd, 1.0)

    def test_sharpe_ratio_calculation(self):
        """シャープレシオ計算テスト"""
        sharpe = self.manager._calculate_sharpe_ratio(self.stock_data, self.market_data)

        self.assertIsInstance(sharpe, float)
        self.assertFalse(np.isnan(sharpe))
        self.assertFalse(np.isinf(sharpe))

    def test_sortino_ratio_calculation(self):
        """ソルティノレシオ計算テスト"""
        sortino = self.manager._calculate_sortino_ratio(self.stock_data)

        self.assertIsInstance(sortino, float)
        self.assertFalse(np.isnan(sortino))
        if not np.isinf(sortino):
            self.assertGreaterEqual(sortino, 0.0)

    def test_calmar_ratio_calculation(self):
        """カルマーレシオ計算テスト"""
        calmar = self.manager._calculate_calmar_ratio(self.stock_data)

        self.assertIsInstance(calmar, float)
        self.assertFalse(np.isnan(calmar))
        if not np.isinf(calmar):
            self.assertGreaterEqual(calmar, 0.0)

    def test_volatility_calculation(self):
        """ボラティリティ計算テスト"""
        volatility = self.manager._calculate_volatility(self.stock_data)

        self.assertGreaterEqual(volatility, 0.0)
        self.assertLessEqual(volatility, 1.0)

    def test_beta_calculation(self):
        """ベータ計算テスト"""
        beta = self.manager._calculate_beta(self.stock_data, self.market_data)

        self.assertIsInstance(beta, float)
        self.assertFalse(np.isnan(beta))
        self.assertGreaterEqual(beta, 0.0)

    def test_correlation_calculation(self):
        """相関計算テスト"""
        correlation = self.manager._calculate_correlation(
            self.stock_data, self.market_data
        )

        self.assertIsInstance(correlation, float)
        self.assertFalse(np.isnan(correlation))
        self.assertGreaterEqual(correlation, -1.0)
        self.assertLessEqual(correlation, 1.0)

    def test_risk_level_determination(self):
        """リスクレベル決定テスト"""
        # 低リスク
        low_risk_level = self.manager._determine_risk_level(0.01, 0.05, 0.15)
        self.assertIn(low_risk_level, [RiskLevel.VERY_LOW, RiskLevel.LOW])

        # 高リスク（var_95=0.08, max_drawdown=0.25, volatility=0.50）
        # スコア計算: var_95(3) + max_drawdown(3) + volatility(3) = 9点 → VERY_HIGH
        high_risk_level = self.manager._determine_risk_level(0.08, 0.25, 0.50)
        self.assertEqual(high_risk_level, RiskLevel.VERY_HIGH)

    def test_dynamic_position_size_calculation(self):
        """動的ポジションサイズ計算テスト"""
        base_size = 0.1
        risk_level = RiskLevel.MEDIUM
        volatility = 0.2
        beta = 1.0

        position_size = self.manager._calculate_dynamic_position_size(
            base_size, risk_level, volatility, beta
        )

        self.assertGreaterEqual(position_size, 0.0)
        self.assertLessEqual(
            position_size, self.config["risk_limits"]["max_position_size"]
        )

    def test_dynamic_stop_take_calculation(self):
        """動的損切り・利確計算テスト"""
        current_price = 100.0
        volatility = 0.2
        risk_level = RiskLevel.MEDIUM

        stop_loss, take_profit = self.manager._calculate_dynamic_stop_take(
            current_price, volatility, risk_level
        )

        self.assertGreater(stop_loss, 0.0)
        self.assertGreater(take_profit, 0.0)
        self.assertLess(stop_loss, current_price)  # 損切りは現在価格より低い
        self.assertGreater(take_profit, current_price)  # 利確は現在価格より高い

    def test_dynamic_risk_adjustment(self):
        """動的リスク調整計算テスト"""
        confidence = 0.8
        sector_data = None

        adjustment = self.manager.calculate_dynamic_risk_adjustment(
            self.stock_data, self.market_data, confidence, sector_data
        )

        self.assertIsInstance(adjustment, DynamicRiskAdjustment)
        self.assertGreaterEqual(adjustment.final_adjustment, 0.0)
        self.assertLessEqual(adjustment.final_adjustment, 2.0)

    def test_position_adjustment_decision(self):
        """ポジション調整判定テスト"""
        # 正常なリスクメトリクス
        normal_metrics = RiskMetrics(
            var_95=0.02,
            var_99=0.04,
            max_drawdown=0.08,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            calmar_ratio=1.2,
            volatility=0.20,
            beta=1.0,
            correlation=0.6,
            risk_level=RiskLevel.MEDIUM,
            position_size=0.05,
            stop_loss=95.0,
            take_profit=110.0,
        )

        adjustments = self.manager.should_adjust_position(normal_metrics)

        self.assertIn("should_reduce", adjustments)
        self.assertIn("should_increase", adjustments)
        self.assertIn("should_close", adjustments)
        self.assertIn("adjustment_reason", adjustments)
        self.assertIn("new_position_size", adjustments)
        self.assertIn("risk_level_change", adjustments)

        # 高リスクメトリクス
        high_risk_metrics = RiskMetrics(
            var_95=0.08,  # 制限超過
            var_99=0.12,
            max_drawdown=0.20,  # 制限超過
            sharpe_ratio=0.5,
            sortino_ratio=0.6,
            calmar_ratio=0.4,
            volatility=0.45,  # 高ボラティリティ
            beta=1.5,
            correlation=0.9,  # 高相関
            risk_level=RiskLevel.VERY_HIGH,
            position_size=0.15,  # 制限超過
            stop_loss=80.0,
            take_profit=120.0,
        )

        adjustments = self.manager.should_adjust_position(high_risk_metrics)

        # 高リスクでは削減が推奨される
        self.assertTrue(adjustments["should_reduce"])
        self.assertLess(
            adjustments["new_position_size"], high_risk_metrics.position_size
        )

    def test_optimal_position_size_calculation(self):
        """最適ポジションサイズ計算テスト"""
        account_value = 1000000.0
        risk_metrics = RiskMetrics(
            var_95=0.03,
            var_99=0.06,
            max_drawdown=0.10,
            sharpe_ratio=1.2,
            sortino_ratio=1.5,
            calmar_ratio=1.0,
            volatility=0.25,
            beta=1.1,
            correlation=0.7,
            risk_level=RiskLevel.MEDIUM,
            position_size=0.05,
            stop_loss=95.0,
            take_profit=110.0,
        )
        confidence = 0.75
        market_conditions = {"high_volatility": False, "low_liquidity": False}

        optimal_size = self.manager.calculate_optimal_position_size(
            account_value, risk_metrics, confidence, market_conditions
        )

        self.assertGreaterEqual(optimal_size, 0.01)  # 最小1%
        self.assertLessEqual(
            optimal_size, self.config["risk_limits"]["max_position_size"]
        )

    def test_market_conditions_adjustment(self):
        """市場条件調整テスト"""
        # 高ボラティリティ市場
        high_vol_conditions = {"high_volatility": True, "low_liquidity": False}
        high_vol_size = self.manager.calculate_optimal_position_size(
            1000000.0, self._create_test_risk_metrics(), 0.8, high_vol_conditions
        )

        # 通常市場
        normal_conditions = {"high_volatility": False, "low_liquidity": False}
        normal_size = self.manager.calculate_optimal_position_size(
            1000000.0, self._create_test_risk_metrics(), 0.8, normal_conditions
        )

        # 高ボラティリティ時はポジションサイズが小さくなる（または同じ）
        self.assertLessEqual(high_vol_size, normal_size)

    def test_liquidity_adjustment(self):
        """流動性調整テスト"""
        # 高流動性データ
        high_liquidity_data = self.stock_data.copy()
        high_liquidity_data["Volume"] = high_liquidity_data["Volume"] * 2

        adjustment = self.manager._calculate_liquidity_adjustment(high_liquidity_data)
        self.assertGreaterEqual(adjustment, 0.8)

        # 低流動性データ
        low_liquidity_data = self.stock_data.copy()
        low_liquidity_data["Volume"] = low_liquidity_data["Volume"] * 0.1

        adjustment = self.manager._calculate_liquidity_adjustment(low_liquidity_data)
        self.assertLessEqual(adjustment, 0.8)

    def test_volatility_adjustment(self):
        """ボラティリティ調整テスト"""
        # 高ボラティリティ
        high_vol_adjustment = self.manager._calculate_volatility_adjustment(0.35)
        self.assertLess(high_vol_adjustment, 1.0)

        # 低ボラティリティ
        low_vol_adjustment = self.manager._calculate_volatility_adjustment(0.15)
        self.assertGreaterEqual(low_vol_adjustment, 0.9)

    def test_confidence_adjustment(self):
        """信頼度調整テスト"""
        # 高信頼度
        high_conf_adjustment = self.manager._calculate_confidence_adjustment(0.9)
        self.assertGreater(high_conf_adjustment, 1.0)

        # 低信頼度
        low_conf_adjustment = self.manager._calculate_confidence_adjustment(0.5)
        self.assertLess(low_conf_adjustment, 1.0)

    def test_kelly_fraction_calculation(self):
        """ケリー基準計算テスト"""
        risk_metrics = self._create_test_risk_metrics()
        kelly_fraction = self.manager._calculate_kelly_fraction(risk_metrics)

        self.assertGreaterEqual(kelly_fraction, 0.0)
        self.assertLessEqual(kelly_fraction, 0.25)  # 最大25%に制限

    def test_empty_data_handling(self):
        """空データ処理テスト"""
        empty_stock_data = pd.DataFrame()
        empty_market_data = pd.DataFrame()

        metrics = self.manager.calculate_risk_metrics(
            empty_stock_data, empty_market_data, 100.0, 0.05
        )

        self.assertIsInstance(metrics, RiskMetrics)
        # 空データでもデフォルト値が返されることを確認
        self.assertGreaterEqual(metrics.var_95, 0.0)
        self.assertGreaterEqual(metrics.max_drawdown, 0.0)

    def test_edge_cases(self):
        """エッジケーステスト"""
        # 極端な値でのテスト
        extreme_stock_data = self.stock_data.copy()
        extreme_stock_data["Close"] = [0.01] * len(extreme_stock_data)  # 極端に低い価格

        metrics = self.manager.calculate_risk_metrics(
            extreme_stock_data, self.market_data, 0.01, 0.05
        )

        self.assertIsInstance(metrics, RiskMetrics)
        self.assertGreaterEqual(metrics.var_95, 0.0)

    def test_performance_under_load(self):
        """負荷下でのパフォーマンステスト"""
        import time

        start_time = time.time()

        # 複数回のリスク計算
        for _ in range(50):
            metrics = self.manager.calculate_risk_metrics(
                self.stock_data, self.market_data, 100.0, 0.05
            )

        end_time = time.time()
        execution_time = end_time - start_time

        # 50回の計算が3秒以内に完了することを確認
        self.assertLess(execution_time, 3.0)

    def test_risk_statistics(self):
        """リスク統計テスト"""
        # 履歴データを追加
        for i in range(10):
            metrics = self._create_test_risk_metrics()
            self.manager.risk_history.append(metrics)

        stats = self.manager.get_risk_statistics()

        self.assertIn("total_samples", stats)
        self.assertIn("avg_var_95", stats)
        self.assertIn("max_var_95", stats)
        self.assertIn("avg_max_drawdown", stats)
        self.assertIn("max_drawdown", stats)
        self.assertIn("avg_volatility", stats)
        self.assertIn("max_volatility", stats)
        self.assertIn("risk_level_distribution", stats)

        self.assertEqual(stats["total_samples"], 10)

    def _create_test_risk_metrics(self) -> RiskMetrics:
        """テスト用リスクメトリクス作成"""
        return RiskMetrics(
            var_95=0.03,
            var_99=0.06,
            max_drawdown=0.10,
            sharpe_ratio=1.2,
            sortino_ratio=1.5,
            calmar_ratio=1.0,
            volatility=0.25,
            beta=1.1,
            correlation=0.7,
            risk_level=RiskLevel.MEDIUM,
            position_size=0.05,
            stop_loss=95.0,
            take_profit=110.0,
        )


if __name__ == "__main__":
    unittest.main()
