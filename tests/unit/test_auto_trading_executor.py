#!/usr/bin/env python3
"""
自動損切り・利確実行システムのテスト
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auto_trading_executor import (
    AutoTradingExecutor,
    TradeType,
    ExecutionStatus,
    OrderType,
    TrailingStopManager,
    PartialCloseManager
)


class TestTrailingStopManager(unittest.TestCase):
    """トレーリングストップ管理のテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.manager = TrailingStopManager(trail_percentage=0.02)
    
    def test_update_trailing_stop_buy_position(self):
        """買いポジションのトレーリングストップ更新テスト"""
        # 買いポジション作成
        position = Mock()
        position.direction = 'BUY'
        position.max_profit_price = None
        position.trailing_stop_price = None
        
        # 価格上昇時のテスト
        current_price = 105.0
        new_trailing_stop, should_execute = self.manager.update_trailing_stop(position, current_price)
        
        self.assertIsInstance(new_trailing_stop, float)
        self.assertGreater(new_trailing_stop, 0)
        # トレーリングストップが更新される場合はTrueになる可能性がある
        self.assertIsInstance(should_execute, bool)
    
    def test_update_trailing_stop_sell_position(self):
        """売りポジションのトレーリングストップ更新テスト"""
        # 売りポジション作成
        position = Mock()
        position.direction = 'SELL'
        position.max_profit_price = None
        position.trailing_stop_price = None
        
        # 価格下降時のテスト
        current_price = 95.0
        new_trailing_stop, should_execute = self.manager.update_trailing_stop(position, current_price)
        
        self.assertIsInstance(new_trailing_stop, float)
        self.assertGreater(new_trailing_stop, 0)
        # トレーリングストップが更新される場合はTrueになる可能性がある
        self.assertIsInstance(should_execute, bool)


class TestPartialCloseManager(unittest.TestCase):
    """部分決済管理のテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.manager = PartialCloseManager(close_percentage=0.5)
    
    def test_calculate_partial_close_quantity(self):
        """部分決済数量計算テスト"""
        # ポジション作成
        position = Mock()
        position.direction = 'BUY'
        position.entry_price = 100.0
        position.quantity = 100.0
        position.current_price = 110.0
        
        # 利益目標設定
        profit_target = 20.0
        
        quantity = self.manager.calculate_partial_close_quantity(position, profit_target)
        
        self.assertIsInstance(quantity, float)
        self.assertGreaterEqual(quantity, 0)
        self.assertLessEqual(quantity, position.quantity)


class TestAutoTradingExecutor(unittest.TestCase):
    """自動損切り・利確実行システムのテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.config = {
            "execution": {
                "max_concurrent_orders": 10,
                "execution_timeout": 30.0,
                "retry_attempts": 3,
                "retry_delay": 1.0
            },
            "risk_management": {
                "max_position_size": 0.1,
                "max_daily_loss": 0.05,
                "emergency_stop_loss": 0.10,
                "commission_rate": 0.001
            },
            "trailing_stop": {
                "enabled": True,
                "trail_percentage": 0.02,
                "min_profit_ratio": 1.5
            },
            "partial_close": {
                "enabled": True,
                "close_percentage": 0.5,
                "profit_target_ratio": 2.0
            }
        }
        self.executor = AutoTradingExecutor(self.config)
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.executor)
        self.assertFalse(self.executor.is_executing)
        self.assertEqual(len(self.executor.positions), 0)
        self.assertEqual(len(self.executor.orders), 0)
    
    def test_create_position(self):
        """ポジション作成テスト"""
        position_id = self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0
        )
        
        self.assertIsNotNone(position_id)
        self.assertIn("TEST", self.executor.positions)
        self.assertEqual(self.executor.positions["TEST"].symbol, "TEST")
        self.assertEqual(self.executor.positions["TEST"].direction, "BUY")
        self.assertEqual(self.executor.positions["TEST"].entry_price, 100.0)
    
    def test_update_position_price(self):
        """ポジション価格更新テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0
        )
        
        # 価格更新
        self.executor.update_position_price("TEST", 105.0)
        
        position = self.executor.positions["TEST"]
        self.assertEqual(position.current_price, 105.0)
        self.assertEqual(position.unrealized_pnl, 500.0)  # (105-100) * 100
    
    def test_check_stop_loss_take_profit(self):
        """損切り・利確チェックテスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0
        )
        
        # 損切り価格での更新
        self.executor.update_position_price("TEST", 94.0)
        
        # 注文が作成されているかチェック
        self.assertGreater(len(self.executor.orders), 0)
    
    def test_simulate_order_execution(self):
        """注文執行シミュレーションテスト"""
        # 注文作成
        order = Mock()
        order.order_id = "test_order_1"
        order.symbol = "TEST"
        order.trade_type = TradeType.STOP_LOSS
        order.price = 95.0
        order.quantity = 100.0
        
        # ポジション設定
        self.executor.positions["TEST"] = Mock()
        self.executor.positions["TEST"].entry_price = 100.0
        
        # 執行シミュレーション
        result = self.executor._simulate_order_execution(order)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.order_id, "test_order_1")
        self.assertEqual(result.symbol, "TEST")
        self.assertEqual(result.trade_type, TradeType.STOP_LOSS)
        self.assertIsInstance(result.executed_price, float)
        self.assertIsInstance(result.executed_quantity, float)
        self.assertIsInstance(result.commission, float)
        self.assertIsInstance(result.pnl, float)
    
    def test_get_execution_status(self):
        """執行状況取得テスト"""
        status = self.executor.get_execution_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('status', status)
        self.assertIn('active_positions', status)
        self.assertIn('pending_orders', status)
        self.assertIn('executing_orders', status)
        self.assertIn('total_executions', status)
    
    def test_get_position_summary(self):
        """ポジションサマリー取得テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0
        )
        
        # 価格更新
        self.executor.update_position_price("TEST", 105.0)
        
        summary = self.executor.get_position_summary()
        
        self.assertIsInstance(summary, dict)
        if summary.get('status') != 'no_positions':
            self.assertIn('active_positions', summary)
            self.assertIn('total_unrealized_pnl', summary)
            self.assertIn('total_realized_pnl', summary)
            self.assertIn('positions', summary)
    
    def test_get_performance_metrics(self):
        """パフォーマンス指標取得テスト"""
        # 執行履歴を事前に追加（Mockではなく実際のExecutionResultオブジェクト）
        from core.auto_trading_executor import ExecutionResult, TradeType, ExecutionStatus
        
        self.executor.execution_history = [
            ExecutionResult(
                order_id="test_1",
                symbol="TEST",
                trade_type=TradeType.STOP_LOSS,
                executed_price=95.0,
                executed_quantity=100.0,
                commission=0.1,
                pnl=100.0,
                execution_time=datetime.now(),
                status=ExecutionStatus.COMPLETED
            ),
            ExecutionResult(
                order_id="test_2",
                symbol="TEST",
                trade_type=TradeType.TAKE_PROFIT,
                executed_price=110.0,
                executed_quantity=100.0,
                commission=0.1,
                pnl=-50.0,
                execution_time=datetime.now(),
                status=ExecutionStatus.COMPLETED
            )
        ]
        
        metrics = self.executor.get_performance_metrics(days=30)
        
        self.assertIsInstance(metrics, dict)
        if metrics.get('status') != 'no_data':
            self.assertIn('total_trades', metrics)
            self.assertIn('winning_trades', metrics)
            self.assertIn('losing_trades', metrics)
            self.assertIn('win_rate', metrics)
            self.assertIn('total_pnl', metrics)
            self.assertIn('net_pnl', metrics)


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.executor = AutoTradingExecutor()
    
    def test_full_trading_workflow(self):
        """完全取引ワークフローテスト"""
        # 1. ポジション作成
        position_id = self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0
        )
        
        self.assertIsNotNone(position_id)
        
        # 2. 価格更新（利益方向）
        self.executor.update_position_price("TEST", 105.0)
        
        position = self.executor.positions["TEST"]
        self.assertEqual(position.current_price, 105.0)
        self.assertEqual(position.unrealized_pnl, 500.0)
        
        # 3. 価格更新（損切り方向）
        self.executor.update_position_price("TEST", 94.0)
        
        # 4. 執行状況確認
        status = self.executor.get_execution_status()
        self.assertIsInstance(status, dict)
        
        # 5. ポジションサマリー確認
        summary = self.executor.get_position_summary()
        self.assertIsInstance(summary, dict)
        
        # 6. パフォーマンス指標確認
        metrics = self.executor.get_performance_metrics()
        self.assertIsInstance(metrics, dict)


if __name__ == '__main__':
    # テスト実行
    unittest.main(verbosity=2)
