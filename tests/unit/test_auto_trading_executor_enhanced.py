#!/usr/bin/env python3
"""
自動損切り・利確実行システムの拡張テスト
カバレッジ向上のための追加テストケース
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import threading
import time
from queue import Empty

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auto_trading_executor import (
    AutoTradingExecutor,
    TradeType,
    ExecutionStatus,
    OrderType,
    TrailingStopManager,
    PartialCloseManager,
    TradeOrder,
    Position,
    ExecutionResult,
)


class TestTrailingStopManagerEnhanced(unittest.TestCase):
    """トレーリングストップ管理の拡張テスト"""

    def setUp(self):
        """テスト前準備"""
        self.manager = TrailingStopManager(trail_percentage=0.02)

    def test_update_trailing_stop_buy_position_profit_update(self):
        """買いポジションの利益更新時のトレーリングストップテスト"""
        position = Mock()
        position.direction = "BUY"
        position.max_profit_price = 100.0
        position.trailing_stop_price = 98.0

        # 価格が最高値を更新
        current_price = 105.0
        new_trailing_stop, should_execute = self.manager.update_trailing_stop(
            position, current_price
        )

        self.assertEqual(position.max_profit_price, 105.0)
        self.assertGreater(new_trailing_stop, 98.0)
        self.assertTrue(should_execute)

    def test_update_trailing_stop_buy_position_no_update(self):
        """買いポジションの価格下落時のトレーリングストップテスト"""
        position = Mock()
        position.direction = "BUY"
        position.max_profit_price = 105.0
        position.trailing_stop_price = 102.9

        # 価格が最高値を更新しない
        current_price = 103.0
        new_trailing_stop, should_execute = self.manager.update_trailing_stop(
            position, current_price
        )

        self.assertEqual(position.max_profit_price, 105.0)
        self.assertEqual(new_trailing_stop, 102.9)
        self.assertFalse(should_execute)

    def test_update_trailing_stop_buy_position_stop_triggered(self):
        """買いポジションのストップ発動テスト"""
        position = Mock()
        position.direction = "BUY"
        position.max_profit_price = 105.0
        position.trailing_stop_price = 102.9

        # ストップ価格以下
        current_price = 102.0
        new_trailing_stop, should_execute = self.manager.update_trailing_stop(
            position, current_price
        )

        self.assertEqual(new_trailing_stop, 102.9)
        self.assertTrue(should_execute)

    def test_update_trailing_stop_sell_position_profit_update(self):
        """売りポジションの利益更新時のトレーリングストップテスト"""
        position = Mock()
        position.direction = "SELL"
        position.max_profit_price = 100.0
        position.trailing_stop_price = 102.0

        # 価格が最高値を更新
        current_price = 95.0
        new_trailing_stop, should_execute = self.manager.update_trailing_stop(
            position, current_price
        )

        self.assertEqual(position.max_profit_price, 95.0)
        self.assertLess(new_trailing_stop, 102.0)
        self.assertTrue(should_execute)

    def test_update_trailing_stop_sell_position_stop_triggered(self):
        """売りポジションのストップ発動テスト"""
        position = Mock()
        position.direction = "SELL"
        position.max_profit_price = 95.0
        position.trailing_stop_price = 97.0

        # ストップ価格以上
        current_price = 98.0
        new_trailing_stop, should_execute = self.manager.update_trailing_stop(
            position, current_price
        )

        self.assertEqual(new_trailing_stop, 97.0)
        self.assertTrue(should_execute)

    def test_update_trailing_stop_exception_handling(self):
        """トレーリングストップ更新の例外処理テスト"""
        position = Mock()
        position.direction = "BUY"
        position.max_profit_price = None
        position.trailing_stop_price = None

        # 例外を発生させる - max_profit_priceの設定で例外を発生
        with patch.object(
            position, "max_profit_price", side_effect=Exception("Test error")
        ):
            new_trailing_stop, should_execute = self.manager.update_trailing_stop(
                position, 100.0
            )

            self.assertIsNone(new_trailing_stop)
            self.assertFalse(should_execute)


class TestPartialCloseManagerEnhanced(unittest.TestCase):
    """部分決済管理の拡張テスト"""

    def setUp(self):
        """テスト前準備"""
        self.manager = PartialCloseManager(close_percentage=0.5)

    def test_calculate_partial_close_quantity_buy_profit_target_met(self):
        """買いポジションの利益目標達成時の部分決済テスト"""
        position = Mock()
        position.direction = "BUY"
        position.entry_price = 100.0
        position.quantity = 100.0
        position.current_price = 120.0

        profit_target = 20.0
        quantity = self.manager.calculate_partial_close_quantity(
            position, profit_target
        )

        self.assertEqual(quantity, 50.0)  # 100 * 0.5

    def test_calculate_partial_close_quantity_buy_profit_target_not_met(self):
        """買いポジションの利益目標未達成時の部分決済テスト"""
        position = Mock()
        position.direction = "BUY"
        position.entry_price = 100.0
        position.quantity = 100.0
        position.current_price = 110.0

        profit_target = 20.0
        quantity = self.manager.calculate_partial_close_quantity(
            position, profit_target
        )

        self.assertEqual(quantity, 0.0)

    def test_calculate_partial_close_quantity_sell_profit_target_met(self):
        """売りポジションの利益目標達成時の部分決済テスト"""
        position = Mock()
        position.direction = "SELL"
        position.entry_price = 100.0
        position.quantity = 100.0
        position.current_price = 80.0

        profit_target = 20.0
        quantity = self.manager.calculate_partial_close_quantity(
            position, profit_target
        )

        self.assertEqual(quantity, 50.0)  # 100 * 0.5

    def test_calculate_partial_close_quantity_no_profit_target(self):
        """利益目標なしの部分決済テスト"""
        position = Mock()
        position.direction = "BUY"
        position.entry_price = 100.0
        position.quantity = 100.0
        position.current_price = 110.0

        quantity = self.manager.calculate_partial_close_quantity(position, None)

        self.assertEqual(quantity, 50.0)  # 100 * 0.5

    def test_calculate_partial_close_quantity_exception_handling(self):
        """部分決済数量計算の例外処理テスト"""
        position = Mock()
        position.direction = "BUY"
        position.entry_price = 100.0
        position.quantity = 100.0
        position.current_price = 110.0

        with patch.object(position, "direction", side_effect=Exception("Test error")):
            quantity = self.manager.calculate_partial_close_quantity(position, 20.0)
            self.assertEqual(quantity, 0.0)


class TestAutoTradingExecutorEnhanced(unittest.TestCase):
    """自動損切り・利確実行システムの拡張テスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "execution": {
                "max_concurrent_orders": 10,
                "execution_timeout": 30.0,
                "retry_attempts": 3,
                "retry_delay": 1.0,
            },
            "risk_management": {
                "max_position_size": 0.1,
                "max_daily_loss": 0.05,
                "emergency_stop_loss": 0.10,
                "commission_rate": 0.001,
            },
            "trailing_stop": {
                "enabled": True,
                "trail_percentage": 0.02,
                "min_profit_ratio": 1.5,
            },
            "partial_close": {
                "enabled": True,
                "close_percentage": 0.5,
                "profit_target_ratio": 2.0,
            },
        }
        self.executor = AutoTradingExecutor(self.config)

    def test_get_default_config(self):
        """デフォルト設定取得テスト"""
        config = self.executor._get_default_config()

        self.assertIsInstance(config, dict)
        self.assertIn("execution", config)
        self.assertIn("risk_management", config)
        self.assertIn("trailing_stop", config)
        self.assertIn("partial_close", config)

    def test_start_execution_already_running(self):
        """既に実行中の執行開始テスト"""
        self.executor.is_executing = True

        with patch.object(self.executor.logger, "warning") as mock_warning:
            self.executor.start_execution()
            mock_warning.assert_called_once()

    def test_start_execution_success(self):
        """執行開始成功テスト"""
        with patch("threading.Thread") as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            self.executor.start_execution()

            self.assertTrue(self.executor.is_executing)
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

    def test_start_execution_exception(self):
        """執行開始例外処理テスト"""
        with patch("threading.Thread", side_effect=Exception("Thread error")):
            with patch.object(self.executor.logger, "error") as mock_error:
                self.executor.start_execution()

                self.assertFalse(self.executor.is_executing)
                mock_error.assert_called_once()

    def test_stop_execution_success(self):
        """執行停止成功テスト"""
        self.executor.is_executing = True
        mock_thread = Mock()
        self.executor.execution_thread = mock_thread

        with patch.object(self.executor.logger, "info") as mock_info:
            self.executor.stop_execution()

            self.assertFalse(self.executor.is_executing)
            mock_thread.join.assert_called_once_with(timeout=5.0)
            mock_info.assert_called_once()

    def test_stop_execution_exception(self):
        """執行停止例外処理テスト"""
        self.executor.is_executing = True
        mock_thread = Mock()
        mock_thread.join.side_effect = Exception("Join error")
        self.executor.execution_thread = mock_thread

        with patch.object(self.executor.logger, "error") as mock_error:
            self.executor.stop_execution()

            self.assertFalse(self.executor.is_executing)
            mock_error.assert_called_once()

    def test_create_position_exception(self):
        """ポジション作成例外処理テスト"""
        with patch(
            "core.auto_trading_executor.Position",
            side_effect=Exception("Position error"),
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                result = self.executor.create_position(
                    symbol="TEST",
                    direction="BUY",
                    entry_price=100.0,
                    quantity=100.0,
                    stop_loss_price=95.0,
                    take_profit_price=110.0,
                )

                self.assertEqual(result, "")
                mock_error.assert_called_once()

    def test_update_position_price_sell_position(self):
        """売りポジションの価格更新テスト"""
        # 売りポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="SELL",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=105.0,
            take_profit_price=95.0,
        )

        # 価格更新
        self.executor.update_position_price("TEST", 95.0)

        position = self.executor.positions["TEST"]
        self.assertEqual(position.current_price, 95.0)
        self.assertEqual(position.unrealized_pnl, 500.0)  # (100-95) * 100

    def test_update_position_price_nonexistent_position(self):
        """存在しないポジションの価格更新テスト"""
        with patch.object(self.executor.logger, "error") as mock_error:
            self.executor.update_position_price("NONEXISTENT", 100.0)
            # エラーログは出力されない（早期リターンのため）

    def test_check_stop_loss_take_profit_sell_position_stop_loss(self):
        """売りポジションの損切りテスト"""
        # 売りポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="SELL",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=105.0,
            take_profit_price=95.0,
        )

        # 損切り価格での更新
        self.executor.update_position_price("TEST", 106.0)

        # 注文が作成されているかチェック
        self.assertGreater(len(self.executor.orders), 0)

    def test_check_stop_loss_take_profit_sell_position_take_profit(self):
        """売りポジションの利確テスト"""
        # 売りポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="SELL",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=105.0,
            take_profit_price=95.0,
        )

        # 利確価格での更新
        self.executor.update_position_price("TEST", 94.0)

        # 注文が作成されているかチェック
        self.assertGreater(len(self.executor.orders), 0)

    def test_check_stop_loss_take_profit_nonexistent_position(self):
        """存在しないポジションの損切り・利確チェックテスト"""
        with patch.object(self.executor.logger, "error") as mock_error:
            self.executor._check_stop_loss_take_profit("NONEXISTENT", 100.0)
            # エラーログは出力されない（早期リターンのため）

    def test_create_stop_loss_order_success(self):
        """損切り注文作成成功テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
        )

        with patch.object(self.executor.logger, "info") as mock_info:
            self.executor._create_stop_loss_order("TEST", 95.0, TradeType.STOP_LOSS)

            self.assertGreater(len(self.executor.orders), 0)
            self.assertGreater(self.executor.execution_queue.qsize(), 0)
            mock_info.assert_called_once()

    def test_create_take_profit_order_success(self):
        """利確注文作成成功テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
        )

        with patch.object(self.executor.logger, "info") as mock_info:
            self.executor._create_take_profit_order("TEST", 110.0)

            self.assertGreater(len(self.executor.orders), 0)
            self.assertGreater(self.executor.execution_queue.qsize(), 0)
            mock_info.assert_called_once()

    def test_create_partial_close_order_success(self):
        """部分決済注文作成成功テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
        )

        with patch.object(self.executor.logger, "info") as mock_info:
            self.executor._create_partial_close_order("TEST", 110.0, 50.0)

            self.assertGreater(len(self.executor.orders), 0)
            self.assertGreater(self.executor.execution_queue.qsize(), 0)
            mock_info.assert_called_once()

    def test_create_stop_loss_order_exception(self):
        """損切り注文作成例外処理テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
        )

        with patch(
            "core.auto_trading_executor.TradeOrder",
            side_effect=Exception("Order error"),
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                self.executor._create_stop_loss_order("TEST", 95.0, TradeType.STOP_LOSS)
                mock_error.assert_called_once()

    def test_create_take_profit_order_exception(self):
        """利確注文作成例外処理テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
        )

        with patch(
            "core.auto_trading_executor.TradeOrder",
            side_effect=Exception("Order error"),
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                self.executor._create_take_profit_order("TEST", 110.0)
                mock_error.assert_called_once()

    def test_create_partial_close_order_exception(self):
        """部分決済注文作成例外処理テスト"""
        # ポジション作成
        self.executor.create_position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
        )

        with patch(
            "core.auto_trading_executor.TradeOrder",
            side_effect=Exception("Order error"),
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                self.executor._create_partial_close_order("TEST", 110.0, 50.0)
                mock_error.assert_called_once()

    def test_execution_loop_success(self):
        """執行ループ成功テスト"""
        # 注文をキューに追加
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        # 執行ループを短時間実行
        self.executor.is_executing = True

        with patch.object(self.executor, "_execute_order") as mock_execute:
            with patch.object(self.executor.execution_queue, "get_nowait") as mock_get:
                # 最初の呼び出しで注文を返し、2回目の呼び出しでEmpty例外を発生させる
                mock_get.side_effect = [order, Empty()]

                # ループを1回だけ実行
                self.executor._execution_loop()

                # 注文が処理されたことを確認
                mock_execute.assert_called_once_with(order)

    def test_execution_loop_exception(self):
        """執行ループ例外処理テスト"""
        self.executor.is_executing = True

        with patch.object(
            self.executor.execution_queue,
            "get_nowait",
            side_effect=Exception("Queue error"),
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                # ループを1回だけ実行
                self.executor._execution_loop()
                mock_error.assert_called_once()

    def test_execute_order_success(self):
        """注文執行成功テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        with patch.object(self.executor, "_simulate_order_execution") as mock_simulate:
            mock_result = ExecutionResult(
                order_id="test_order",
                symbol="TEST",
                trade_type=TradeType.STOP_LOSS,
                executed_price=95.0,
                executed_quantity=100.0,
                commission=0.1,
                pnl=-500.0,
                execution_time=datetime.now(),
                status=ExecutionStatus.COMPLETED,
            )
            mock_simulate.return_value = mock_result

            with patch.object(
                self.executor, "_update_position_after_execution"
            ) as mock_update:
                with patch.object(self.executor.logger, "info") as mock_info:
                    self.executor._execute_order(order)

                    self.assertEqual(order.status, ExecutionStatus.EXECUTING)
                    mock_update.assert_called_once()
                    mock_info.assert_called_once()

    def test_execute_order_failure(self):
        """注文執行失敗テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        with patch.object(self.executor, "_simulate_order_execution") as mock_simulate:
            mock_result = ExecutionResult(
                order_id="test_order",
                symbol="TEST",
                trade_type=TradeType.STOP_LOSS,
                executed_price=0.0,
                executed_quantity=0.0,
                commission=0.0,
                pnl=0.0,
                execution_time=datetime.now(),
                status=ExecutionStatus.FAILED,
                error_message="Execution failed",
            )
            mock_simulate.return_value = mock_result

            with patch.object(self.executor.logger, "error") as mock_error:
                self.executor._execute_order(order)

                self.assertEqual(order.status, ExecutionStatus.EXECUTING)
                mock_error.assert_called_once()

    def test_execute_order_exception(self):
        """注文執行例外処理テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        with patch.object(
            self.executor,
            "_simulate_order_execution",
            side_effect=Exception("Execution error"),
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                self.executor._execute_order(order)

                self.assertEqual(order.status, ExecutionStatus.FAILED)
                mock_error.assert_called_once()

    def test_simulate_order_execution_buy_position(self):
        """買いポジションの注文執行シミュレーションテスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        # 買いポジション設定
        position = Position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            current_price=95.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.executor.positions["TEST"] = position

        result = self.executor._simulate_order_execution(order)

        self.assertEqual(result.order_id, "test_order")
        self.assertEqual(result.symbol, "TEST")
        self.assertEqual(result.trade_type, TradeType.STOP_LOSS)
        self.assertIsInstance(result.executed_price, float)
        self.assertEqual(result.executed_quantity, 100.0)
        self.assertIsInstance(result.commission, float)
        self.assertIsInstance(result.pnl, float)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)

    def test_simulate_order_execution_sell_position(self):
        """売りポジションの注文執行シミュレーションテスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.TAKE_PROFIT,
            order_type=OrderType.MARKET,
            direction="BUY",
            quantity=100.0,
            price=110.0,
            created_at=datetime.now(),
        )

        # 売りポジション設定
        position = Position(
            symbol="TEST",
            direction="SELL",
            entry_price=100.0,
            quantity=100.0,
            current_price=110.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            stop_loss_price=105.0,
            take_profit_price=95.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.executor.positions["TEST"] = position

        result = self.executor._simulate_order_execution(order)

        self.assertEqual(result.order_id, "test_order")
        self.assertEqual(result.symbol, "TEST")
        self.assertEqual(result.trade_type, TradeType.TAKE_PROFIT)
        self.assertIsInstance(result.executed_price, float)
        self.assertEqual(result.executed_quantity, 100.0)
        self.assertIsInstance(result.commission, float)
        self.assertIsInstance(result.pnl, float)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)

    def test_simulate_order_execution_no_position(self):
        """ポジションなしの注文執行シミュレーションテスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        result = self.executor._simulate_order_execution(order)

        self.assertEqual(result.order_id, "test_order")
        self.assertEqual(result.symbol, "TEST")
        self.assertEqual(result.trade_type, TradeType.STOP_LOSS)
        self.assertIsInstance(result.executed_price, float)
        self.assertEqual(result.executed_quantity, 100.0)
        self.assertIsInstance(result.commission, float)
        self.assertEqual(result.pnl, 0.0)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)

    def test_simulate_order_execution_exception(self):
        """注文執行シミュレーション例外処理テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        with patch("numpy.random.normal", side_effect=Exception("Random error")):
            with patch.object(self.executor.logger, "error") as mock_error:
                result = self.executor._simulate_order_execution(order)

                self.assertEqual(result.status, ExecutionStatus.FAILED)
                self.assertIsNotNone(result.error_message)
                mock_error.assert_called_once()

    def test_update_position_after_execution_partial_close(self):
        """部分決済後のポジション更新テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.PARTIAL_CLOSE,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=50.0,
            price=105.0,
            created_at=datetime.now(),
        )

        execution_result = ExecutionResult(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.PARTIAL_CLOSE,
            executed_price=105.0,
            executed_quantity=50.0,
            commission=0.1,
            pnl=250.0,
            execution_time=datetime.now(),
            status=ExecutionStatus.COMPLETED,
        )

        # ポジション設定
        position = Position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            current_price=105.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.executor.positions["TEST"] = position

        self.executor._update_position_after_execution(order, execution_result)

        updated_position = self.executor.positions["TEST"]
        self.assertEqual(updated_position.quantity, 50.0)
        self.assertEqual(updated_position.realized_pnl, 250.0)
        self.assertEqual(updated_position.status, "PARTIAL")

    def test_update_position_after_execution_full_close(self):
        """完全決済後のポジション更新テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        execution_result = ExecutionResult(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            executed_price=95.0,
            executed_quantity=100.0,
            commission=0.1,
            pnl=-500.0,
            execution_time=datetime.now(),
            status=ExecutionStatus.COMPLETED,
        )

        # ポジション設定
        position = Position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            current_price=95.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.executor.positions["TEST"] = position

        self.executor._update_position_after_execution(order, execution_result)

        updated_position = self.executor.positions["TEST"]
        self.assertEqual(updated_position.quantity, 0)
        self.assertEqual(updated_position.realized_pnl, -500.0)
        self.assertEqual(updated_position.status, "CLOSED")

    def test_update_position_after_execution_nonexistent_position(self):
        """存在しないポジションの更新テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="NONEXISTENT",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        execution_result = ExecutionResult(
            order_id="test_order",
            symbol="NONEXISTENT",
            trade_type=TradeType.STOP_LOSS,
            executed_price=95.0,
            executed_quantity=100.0,
            commission=0.1,
            pnl=-500.0,
            execution_time=datetime.now(),
            status=ExecutionStatus.COMPLETED,
        )

        with patch.object(self.executor.logger, "error") as mock_error:
            self.executor._update_position_after_execution(order, execution_result)
            # エラーログは出力されない（早期リターンのため）

    def test_update_position_after_execution_exception(self):
        """ポジション更新例外処理テスト"""
        order = TradeOrder(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            order_type=OrderType.MARKET,
            direction="SELL",
            quantity=100.0,
            price=95.0,
            created_at=datetime.now(),
        )

        execution_result = ExecutionResult(
            order_id="test_order",
            symbol="TEST",
            trade_type=TradeType.STOP_LOSS,
            executed_price=95.0,
            executed_quantity=100.0,
            commission=0.1,
            pnl=-500.0,
            execution_time=datetime.now(),
            status=ExecutionStatus.COMPLETED,
        )

        # ポジション設定
        position = Position(
            symbol="TEST",
            direction="BUY",
            entry_price=100.0,
            quantity=100.0,
            current_price=95.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            stop_loss_price=95.0,
            take_profit_price=110.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.executor.positions["TEST"] = position

        with patch.object(position, "quantity", side_effect=Exception("Update error")):
            with patch.object(self.executor.logger, "error") as mock_error:
                self.executor._update_position_after_execution(order, execution_result)
                mock_error.assert_called_once()

    def test_get_execution_status_exception(self):
        """執行状況取得例外処理テスト"""
        with patch.object(
            self.executor, "positions", side_effect=Exception("Status error")
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                result = self.executor.get_execution_status()

                self.assertEqual(result["status"], "error")
                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_get_position_summary_exception(self):
        """ポジションサマリー取得例外処理テスト"""
        with patch.object(
            self.executor, "positions", side_effect=Exception("Summary error")
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                result = self.executor.get_position_summary()

                self.assertEqual(result["status"], "error")
                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_get_performance_metrics_exception(self):
        """パフォーマンス指標取得例外処理テスト"""
        with patch.object(
            self.executor, "execution_history", side_effect=Exception("Metrics error")
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                result = self.executor.get_performance_metrics()

                self.assertEqual(result["status"], "error")
                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_export_execution_report_success(self):
        """執行レポート出力成功テスト"""
        # 執行履歴を追加
        execution1 = ExecutionResult(
            order_id="test_1",
            symbol="TEST1",
            trade_type=TradeType.STOP_LOSS,
            executed_price=95.0,
            executed_quantity=100.0,
            commission=0.1,
            pnl=100.0,
            execution_time=datetime.now(),
            status=ExecutionStatus.COMPLETED,
        )

        execution2 = ExecutionResult(
            order_id="test_2",
            symbol="TEST2",
            trade_type=TradeType.TAKE_PROFIT,
            executed_price=110.0,
            executed_quantity=100.0,
            commission=0.1,
            pnl=-50.0,
            execution_time=datetime.now(),
            status=ExecutionStatus.COMPLETED,
        )

        self.executor.execution_history = [execution1, execution2]

        report = self.executor.export_execution_report(days=30)

        self.assertIsInstance(report, dict)
        self.assertIn("report_period", report)
        self.assertIn("total_executions", report)
        self.assertIn("symbol_statistics", report)
        self.assertIn("performance_metrics", report)
        self.assertIn("generated_at", report)

    def test_export_execution_report_exception(self):
        """執行レポート出力例外処理テスト"""
        with patch.object(
            self.executor, "execution_history", side_effect=Exception("Report error")
        ):
            with patch.object(self.executor.logger, "error") as mock_error:
                result = self.executor.export_execution_report()

                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_add_execution_callback(self):
        """執行コールバック追加テスト"""
        callback = Mock()
        self.executor.add_execution_callback(callback)

        self.assertIn(callback, self.executor.execution_callbacks)

    def test_add_position_callback(self):
        """ポジションコールバック追加テスト"""
        callback = Mock()
        self.executor.add_position_callback(callback)

        self.assertIn(callback, self.executor.position_callbacks)


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
