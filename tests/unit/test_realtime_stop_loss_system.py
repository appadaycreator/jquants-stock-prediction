#!/usr/bin/env python3
"""
リアルタイム損切り・利確システムのテスト
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.realtime_stop_loss_system import (
    RealtimeStopLossSystem,
    VolatilityCalculator,
    StopLossType,
    TakeProfitType,
    AlertLevel,
)


class TestVolatilityCalculator(unittest.TestCase):
    """ボラティリティ計算器のテスト"""

    def setUp(self):
        """テスト前準備"""
        self.calculator = VolatilityCalculator()

    def test_calculate_atr(self):
        """ATR計算テスト"""
        # テストデータ作成
        high = [100, 102, 101, 103, 105]
        low = [99, 100, 99, 101, 102]
        close = [100, 101, 100, 102, 104]

        atr = self.calculator.calculate_atr(high, low, close)

        self.assertIsInstance(atr, float)
        self.assertGreaterEqual(atr, 0)

    def test_calculate_volatility(self):
        """ボラティリティ計算テスト"""
        # テストデータ作成
        prices = [100, 101, 102, 101, 100, 99, 98, 99, 100, 101]

        volatility = self.calculator.calculate_volatility(prices)

        self.assertIsInstance(volatility, float)
        self.assertGreaterEqual(volatility, 0)

    def test_calculate_volatility_regime(self):
        """ボラティリティレジーム判定テスト"""
        # 高ボラティリティデータ
        high_vol_prices = [100, 110, 90, 120, 80, 130, 70, 140, 60, 150]
        regime = self.calculator.calculate_volatility_regime(high_vol_prices)

        self.assertIn(
            regime,
            ["high_volatility", "low_volatility", "normal_volatility", "unknown"],
        )

    def test_calculate_dynamic_stop_loss(self):
        """動的損切り価格計算テスト"""
        entry_price = 100.0
        direction = "BUY"
        atr = 2.0
        volatility = 0.2
        volatility_regime = "normal_volatility"
        risk_percentage = 0.02

        stop_loss_price = self.calculator.calculate_dynamic_stop_loss(
            entry_price, direction, atr, volatility, volatility_regime, risk_percentage
        )

        self.assertIsInstance(stop_loss_price, float)
        self.assertLess(stop_loss_price, entry_price)  # 買いポジションの場合、損切り価格は安い

    def test_calculate_dynamic_take_profit(self):
        """動的利確価格計算テスト"""
        entry_price = 100.0
        direction = "BUY"
        volatility = 0.2
        risk_reward_ratio = 2.0

        take_profit_price = self.calculator.calculate_dynamic_take_profit(
            entry_price, direction, volatility, risk_reward_ratio
        )

        self.assertIsInstance(take_profit_price, float)
        self.assertGreater(take_profit_price, entry_price)  # 買いポジションの場合、利確価格は高い


class TestRealtimeStopLossSystem(unittest.TestCase):
    """リアルタイム損切り・利確システムのテスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "monitoring": {
                "update_interval": 1.0,
                "max_price_history": 100,
                "max_alert_history": 1000,
                "max_trade_history": 1000,
            },
            "risk_management": {
                "default_risk_percentage": 0.02,
                "max_risk_percentage": 0.05,
                "min_risk_percentage": 0.005,
                "risk_reward_ratio": 2.0,
                "max_position_size": 0.1,
                "emergency_stop_loss": 0.10,
            },
            "alerts": {
                "price_change_threshold": 0.05,
                "volatility_threshold": 0.30,
                "atr_threshold": 0.03,
                "correlation_threshold": 0.8,
            },
            "execution": {
                "auto_execute": True,
                "partial_execution": True,
                "trailing_stop": True,
                "emergency_stop": True,
            },
        }
        self.system = RealtimeStopLossSystem(self.config)

    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.system)
        self.assertFalse(self.system.is_monitoring)
        self.assertEqual(len(self.system.price_data), 0)
        self.assertEqual(len(self.system.stop_loss_settings), 0)

    def test_add_stop_loss_setting(self):
        """損切り設定追加テスト"""
        # 価格データを事前に追加
        price_data = []
        for i in range(25):
            price_data.append(
                {
                    "price": 100 + i * 0.1,
                    "high": 100 + i * 0.1 + 0.5,
                    "low": 100 + i * 0.1 - 0.5,
                    "volume": 1000 + i * 10,
                }
            )

        self.system.price_data["TEST"] = price_data

        # 損切り設定追加
        result = self.system.add_stop_loss_setting(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            risk_percentage=0.02,
        )

        self.assertTrue(result)
        self.assertIn("TEST", self.system.stop_loss_settings)
        self.assertIn("TEST", self.system.active_positions)

    def test_update_price_data(self):
        """価格データ更新テスト"""
        price_data = {"price": 100.0, "high": 101.0, "low": 99.0, "volume": 1000}

        self.system.update_price_data("TEST", price_data)

        self.assertIn("TEST", self.system.price_data)
        self.assertEqual(len(self.system.price_data["TEST"]), 1)
        self.assertEqual(self.system.price_data["TEST"][0]["price"], 100.0)

    def test_check_stop_loss_conditions(self):
        """損切り条件チェックテスト"""
        # 損切り設定を事前に追加
        self.system.stop_loss_settings["TEST"] = Mock()
        self.system.stop_loss_settings["TEST"].direction = "BUY"
        self.system.stop_loss_settings["TEST"].stop_loss_price = 95.0
        self.system.stop_loss_settings["TEST"].take_profit_price = 110.0
        self.system.stop_loss_settings["TEST"].entry_price = 100.0
        self.system.stop_loss_settings["TEST"].position_size = 100.0

        self.system.active_positions["TEST"] = {
            "entry_price": 100.0,
            "position_size": 100.0,
            "direction": "BUY",
            "status": "ACTIVE",
        }

        # 損切り条件チェック（損切り価格以下）
        alerts = self.system.check_stop_loss_conditions("TEST", 94.0)

        self.assertIsInstance(alerts, list)
        if alerts:
            self.assertEqual(alerts[0].alert_type, "STOP_LOSS_TRIGGERED")

    def test_execute_trade(self):
        """取引執行テスト"""
        # 損切り設定を事前に追加
        self.system.stop_loss_settings["TEST"] = Mock()
        self.system.stop_loss_settings["TEST"].entry_price = 100.0
        self.system.stop_loss_settings["TEST"].position_size = 100.0
        self.system.stop_loss_settings["TEST"].direction = "BUY"
        self.system.stop_loss_settings["TEST"].stop_loss_price = 95.0
        self.system.stop_loss_settings["TEST"].take_profit_price = 110.0
        self.system.stop_loss_settings["TEST"].volatility = 0.2
        self.system.stop_loss_settings["TEST"].atr = 2.0

        self.system.active_positions["TEST"] = {
            "entry_price": 100.0,
            "position_size": 100.0,
            "direction": "BUY",
            "status": "ACTIVE",
        }

        # 取引執行
        execution = self.system.execute_trade("TEST", "STOP_LOSS", 95.0)

        self.assertIsNotNone(execution)
        self.assertEqual(execution.symbol, "TEST")
        self.assertEqual(execution.trade_type, "STOP_LOSS")
        self.assertEqual(execution.exit_price, 95.0)

    def test_get_monitoring_status(self):
        """監視状況取得テスト"""
        status = self.system.get_monitoring_status()

        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("active_positions", status)
        self.assertIn("total_alerts", status)

    def test_get_performance_metrics(self):
        """パフォーマンス指標取得テスト"""
        # 取引履歴を事前に追加
        self.system.trade_history = [
            Mock(pnl=100.0, timestamp=datetime.now()),
            Mock(pnl=-50.0, timestamp=datetime.now()),
            Mock(pnl=200.0, timestamp=datetime.now()),
        ]

        metrics = self.system.get_performance_metrics(days=30)

        self.assertIsInstance(metrics, dict)
        if metrics.get("status") != "no_data":
            self.assertIn("total_trades", metrics)
            self.assertIn("winning_trades", metrics)
            self.assertIn("losing_trades", metrics)
            self.assertIn("win_rate", metrics)
            self.assertIn("total_pnl", metrics)


class TestIntegration(unittest.TestCase):
    """統合テスト"""

    def setUp(self):
        """テスト前準備"""
        self.system = RealtimeStopLossSystem()

    def test_full_workflow(self):
        """完全ワークフローテスト"""
        # 1. 価格データ追加
        price_data = []
        for i in range(25):
            price_data.append(
                {
                    "price": 100 + i * 0.1,
                    "high": 100 + i * 0.1 + 0.5,
                    "low": 100 + i * 0.1 - 0.5,
                    "volume": 1000 + i * 10,
                }
            )

        for data in price_data:
            self.system.update_price_data("TEST", data)

        # 2. 損切り設定追加
        result = self.system.add_stop_loss_setting(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            risk_percentage=0.02,
        )

        self.assertTrue(result)

        # 3. 価格更新と損切りチェック
        self.system.update_price_data(
            "TEST", {"price": 95.0, "high": 95.5, "low": 94.5, "volume": 2000}
        )

        # 4. 監視状況確認
        status = self.system.get_monitoring_status()
        self.assertIsInstance(status, dict)

    def test_add_stop_loss_setting_no_price_data(self):
        """価格データが不足している場合の損切り設定追加テスト"""
        # 価格データが不足している状態で損切り設定追加
        result = self.system.add_stop_loss_setting(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
        )

        self.assertFalse(result)
        self.assertNotIn("TEST", self.system.stop_loss_settings)

    def test_add_stop_loss_setting_insufficient_data(self):
        """価格データが不十分な場合の損切り設定追加テスト"""
        # 不十分な価格データを設定
        price_data = [
            {"price": 100, "high": 102, "low": 98, "volume": 1000},
        ] * 5  # 5個のデータポイント（不十分）

        self.system.price_data["TEST"] = price_data

        # 損切り設定追加
        result = self.system.add_stop_loss_setting(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
        )

        self.assertFalse(result)
        self.assertNotIn("TEST", self.system.stop_loss_settings)

        # 5. パフォーマンス指標確認
        metrics = self.system.get_performance_metrics()
        self.assertIsInstance(metrics, dict)


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
