#!/usr/bin/env python3
"""
リアルタイム損切り・利確システムの拡張テスト
カバレッジ向上のための追加テストケース
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import threading
import time

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.realtime_stop_loss_system import (
    RealtimeStopLossSystem,
    StopLossType,
    TakeProfitType,
    AlertLevel,
    StopLossSettings,
    PriceAlert,
    TradeExecution,
)


class TestRealtimeStopLossSystemEnhanced(unittest.TestCase):
    """リアルタイム損切り・利確システムの拡張テスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "monitoring": {
                "update_interval": 1.0,
                "max_concurrent_monitors": 10,
                "alert_threshold": 0.02,
            },
            "stop_loss": {
                "default_type": "atr_based",
                "atr_multiplier": 2.0,
                "volatility_multiplier": 1.5,
                "time_decay_factor": 0.1,
            },
            "take_profit": {
                "default_type": "ratio_based",
                "risk_reward_ratio": 2.0,
                "volatility_multiplier": 1.2,
            },
            "risk_management": {
                "max_position_size": 0.1,
                "max_daily_loss": 0.05,
                "emergency_stop_loss": 0.10,
            },
        }
        self.system = RealtimeStopLossSystem(self.config)

    def test_get_default_config(self):
        """デフォルト設定取得テスト"""
        config = self.system._get_default_config()
        
        self.assertIsInstance(config, dict)
        self.assertIn("monitoring", config)
        self.assertIn("stop_loss", config)
        self.assertIn("take_profit", config)
        self.assertIn("risk_management", config)

    def test_start_monitoring_already_running(self):
        """既に実行中の監視開始テスト"""
        self.system.is_monitoring = True
        
        with patch.object(self.system.logger, 'warning') as mock_warning:
            self.system.start_monitoring()
            mock_warning.assert_called_once()

    def test_start_monitoring_success(self):
        """監視開始成功テスト"""
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            self.system.start_monitoring()
            
            self.assertTrue(self.system.is_monitoring)
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

    def test_start_monitoring_exception(self):
        """監視開始例外処理テスト"""
        with patch('threading.Thread', side_effect=Exception("Thread error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                self.system.start_monitoring()
                
                self.assertFalse(self.system.is_monitoring)
                mock_error.assert_called_once()

    def test_stop_monitoring_success(self):
        """監視停止成功テスト"""
        self.system.is_monitoring = True
        mock_thread = Mock()
        self.system.monitoring_thread = mock_thread
        
        with patch.object(self.system.logger, 'info') as mock_info:
            self.system.stop_monitoring()
            
            self.assertFalse(self.system.is_monitoring)
            mock_thread.join.assert_called_once_with(timeout=5.0)
            mock_info.assert_called_once()

    def test_stop_monitoring_exception(self):
        """監視停止例外処理テスト"""
        self.system.is_monitoring = True
        mock_thread = Mock()
        mock_thread.join.side_effect = Exception("Join error")
        self.system.monitoring_thread = mock_thread
        
        with patch.object(self.system.logger, 'error') as mock_error:
            self.system.stop_monitoring()
            
            self.assertFalse(self.system.is_monitoring)
            mock_error.assert_called_once()

    def test_add_position_success(self):
        """ポジション追加成功テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.ATR_BASED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.RATIO_BASED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        with patch.object(self.system.logger, 'info') as mock_info:
            self.system.add_position(settings)
            
            self.assertIn("TEST", self.system.positions)
            self.assertEqual(self.system.positions["TEST"], settings)
            mock_info.assert_called_once()

    def test_add_position_exception(self):
        """ポジション追加例外処理テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.ATR_BASED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.RATIO_BASED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # 例外を発生させるために、loggerのinfoメソッドをモックして例外を発生させる
        with patch.object(self.system.logger, 'info', side_effect=Exception("Position error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                self.system.add_position(settings)
                mock_error.assert_called_once()

    def test_remove_position_success(self):
        """ポジション削除成功テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.ATR_BASED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.RATIO_BASED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(self.system.logger, 'info') as mock_info:
            self.system.remove_position("TEST")
            
            self.assertNotIn("TEST", self.system.positions)
            mock_info.assert_called_once()

    def test_remove_position_nonexistent(self):
        """存在しないポジション削除テスト"""
        with patch.object(self.system.logger, 'warning') as mock_warning:
            self.system.remove_position("NONEXISTENT")
            mock_warning.assert_called_once()

    def test_remove_position_exception(self):
        """ポジション削除例外処理テスト"""
        with patch.object(self.system, 'positions', side_effect=Exception("Remove error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                self.system.remove_position("TEST")
                mock_error.assert_called_once()

    def test_update_price_success(self):
        """価格更新成功テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.ATR_BASED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.RATIO_BASED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_check_stop_loss_take_profit') as mock_check:
            self.system.update_price("TEST", 105.0)
            
            self.assertEqual(settings.current_price, 105.0)
            self.assertIsNotNone(settings.updated_at)
            mock_check.assert_called_once_with("TEST", 105.0)

    def test_update_price_nonexistent_position(self):
        """存在しないポジションの価格更新テスト"""
        with patch.object(self.system.logger, 'warning') as mock_warning:
            self.system.update_price("NONEXISTENT", 105.0)
            mock_warning.assert_called_once()

    def test_update_price_exception(self):
        """価格更新例外処理テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.ATR_BASED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.RATIO_BASED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(settings, 'current_price', side_effect=Exception("Update error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                self.system.update_price("TEST", 105.0)
                mock_error.assert_called_once()

    def test_check_stop_loss_take_profit_buy_stop_loss(self):
        """買いポジションの損切りチェックテスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        settings.current_price = 94.0
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_execute_stop_loss') as mock_execute:
            self.system._check_stop_loss_take_profit("TEST", 94.0)
            mock_execute.assert_called_once_with("TEST", 94.0, "損切り価格到達")

    def test_check_stop_loss_take_profit_buy_take_profit(self):
        """買いポジションの利確チェックテスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        settings.current_price = 111.0
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_execute_take_profit') as mock_execute:
            self.system._check_stop_loss_take_profit("TEST", 111.0)
            mock_execute.assert_called_once_with("TEST", 111.0, "利確価格到達")

    def test_check_stop_loss_take_profit_sell_stop_loss(self):
        """売りポジションの損切りチェックテスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="SELL",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=105.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=95.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        settings.current_price = 106.0
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_execute_stop_loss') as mock_execute:
            self.system._check_stop_loss_take_profit("TEST", 106.0)
            mock_execute.assert_called_once_with("TEST", 106.0, "損切り価格到達")

    def test_check_stop_loss_take_profit_sell_take_profit(self):
        """売りポジションの利確チェックテスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="SELL",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=105.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=95.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        settings.current_price = 94.0
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_execute_take_profit') as mock_execute:
            self.system._check_stop_loss_take_profit("TEST", 94.0)
            mock_execute.assert_called_once_with("TEST", 94.0, "利確価格到達")

    def test_check_stop_loss_take_profit_nonexistent_position(self):
        """存在しないポジションの損切り・利確チェックテスト"""
        with patch.object(self.system.logger, 'warning') as mock_warning:
            self.system._check_stop_loss_take_profit("NONEXISTENT", 100.0)
            mock_warning.assert_called_once()

    def test_check_stop_loss_take_profit_exception(self):
        """損切り・利確チェック例外処理テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        # 例外を発生させるために、_execute_stop_lossメソッドをモック
        with patch.object(self.system, '_execute_stop_loss', side_effect=Exception("Check error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                # 損切り条件を満たす価格でテスト
                self.system._check_stop_loss_take_profit("TEST", 90.0)  # 損切り価格以下
                mock_error.assert_called_once()

    def test_execute_stop_loss_success(self):
        """損切り執行成功テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_create_trade_execution') as mock_create:
            with patch.object(self.system, '_remove_position') as mock_remove:
                with patch.object(self.system.logger, 'info') as mock_info:
                    self.system._execute_stop_loss("TEST", 94.0, "損切り価格到達")
                    
                    mock_create.assert_called_once()
                    mock_remove.assert_called_once_with("TEST")
                    mock_info.assert_called_once()

    def test_execute_stop_loss_nonexistent_position(self):
        """存在しないポジションの損切り執行テスト"""
        with patch.object(self.system.logger, 'warning') as mock_warning:
            self.system._execute_stop_loss("NONEXISTENT", 94.0, "損切り価格到達")
            mock_warning.assert_called_once()

    def test_execute_stop_loss_exception(self):
        """損切り執行例外処理テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_create_trade_execution', side_effect=Exception("Execution error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                self.system._execute_stop_loss("TEST", 94.0, "損切り価格到達")
                mock_error.assert_called_once()

    def test_execute_take_profit_success(self):
        """利確執行成功テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_create_trade_execution') as mock_create:
            with patch.object(self.system, '_remove_position') as mock_remove:
                with patch.object(self.system.logger, 'info') as mock_info:
                    self.system._execute_take_profit("TEST", 111.0, "利確価格到達")
                    
                    mock_create.assert_called_once()
                    mock_remove.assert_called_once_with("TEST")
                    mock_info.assert_called_once()

    def test_execute_take_profit_nonexistent_position(self):
        """存在しないポジションの利確執行テスト"""
        with patch.object(self.system.logger, 'warning') as mock_warning:
            self.system._execute_take_profit("NONEXISTENT", 111.0, "利確価格到達")
            mock_warning.assert_called_once()

    def test_execute_take_profit_exception(self):
        """利確執行例外処理テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_create_trade_execution', side_effect=Exception("Execution error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                self.system._execute_take_profit("TEST", 111.0, "利確価格到達")
                mock_error.assert_called_once()

    def test_create_trade_execution_success(self):
        """取引執行作成成功テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        execution = self.system._create_trade_execution(
            settings, 94.0, "STOP_LOSS", "損切り価格到達"
        )

        self.assertIsInstance(execution, TradeExecution)
        self.assertEqual(execution.symbol, "TEST")
        self.assertEqual(execution.trade_type, "STOP_LOSS")
        self.assertEqual(execution.entry_price, 100.0)
        self.assertEqual(execution.exit_price, 94.0)
        self.assertEqual(execution.position_size, 100.0)
        self.assertEqual(execution.pnl, -600.0)  # (94-100) * 100
        self.assertEqual(execution.execution_reason, "損切り価格到達")

    def test_create_trade_execution_take_profit(self):
        """利確取引執行作成テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        execution = self.system._create_trade_execution(
            settings, 111.0, "TAKE_PROFIT", "利確価格到達"
        )

        self.assertIsInstance(execution, TradeExecution)
        self.assertEqual(execution.symbol, "TEST")
        self.assertEqual(execution.trade_type, "TAKE_PROFIT")
        self.assertEqual(execution.entry_price, 100.0)
        self.assertEqual(execution.exit_price, 111.0)
        self.assertEqual(execution.position_size, 100.0)
        self.assertEqual(execution.pnl, 1100.0)  # (111-100) * 100
        self.assertEqual(execution.execution_reason, "利確価格到達")

    def test_create_trade_execution_sell_position(self):
        """売りポジションの取引執行作成テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="SELL",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=105.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=95.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        execution = self.system._create_trade_execution(
            settings, 94.0, "TAKE_PROFIT", "利確価格到達"
        )

        self.assertIsInstance(execution, TradeExecution)
        self.assertEqual(execution.symbol, "TEST")
        self.assertEqual(execution.trade_type, "TAKE_PROFIT")
        self.assertEqual(execution.entry_price, 100.0)
        self.assertEqual(execution.exit_price, 94.0)
        self.assertEqual(execution.position_size, 100.0)
        self.assertEqual(execution.pnl, 600.0)  # (100-94) * 100
        self.assertEqual(execution.execution_reason, "利確価格到達")

    def test_create_trade_execution_exception(self):
        """取引執行作成例外処理テスト"""
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        with patch('core.realtime_stop_loss_system.TradeExecution', side_effect=Exception("Execution error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                result = self.system._create_trade_execution(
                    settings, 94.0, "STOP_LOSS", "損切り価格到達"
                )
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_monitoring_loop_success(self):
        """監視ループ成功テスト"""
        self.system.is_monitoring = True
        
        # ポジションを追加
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        with patch.object(self.system, '_check_stop_loss_take_profit') as mock_check:
            # ループを1回だけ実行
            self.system._monitoring_loop()
            
            # チェックが呼ばれるまで待機
            time.sleep(0.1)
            
            # チェックが呼ばれたことを確認
            mock_check.assert_called_once_with("TEST", settings.current_price)

    def test_monitoring_loop_exception(self):
        """監視ループ例外処理テスト"""
        self.system.is_monitoring = True
        
        with patch.object(self.system, 'positions', side_effect=Exception("Loop error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                # ループを1回だけ実行
                self.system._monitoring_loop()
                mock_error.assert_called_once()

    def test_get_monitoring_status_success(self):
        """監視状況取得成功テスト"""
        # ポジションを追加
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.system.positions["TEST"] = settings

        status = self.system.get_monitoring_status()

        self.assertIsInstance(status, dict)
        self.assertIn("is_monitoring", status)
        self.assertIn("active_positions", status)
        self.assertIn("total_alerts", status)
        self.assertIn("total_executions", status)
        self.assertIn("last_update", status)

    def test_get_monitoring_status_exception(self):
        """監視状況取得例外処理テスト"""
        with patch.object(self.system, 'positions', side_effect=Exception("Status error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                result = self.system.get_monitoring_status()
                
                self.assertEqual(result["status"], "error")
                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_get_position_summary_success(self):
        """ポジションサマリー取得成功テスト"""
        # ポジションを追加
        settings = StopLossSettings(
            symbol="TEST",
            entry_price=100.0,
            position_size=100.0,
            direction="BUY",
            stop_loss_type=StopLossType.FIXED,
            stop_loss_price=95.0,
            take_profit_type=TakeProfitType.FIXED,
            take_profit_price=110.0,
            volatility=0.02,
            atr=2.0,
            risk_percentage=0.05,
            max_loss_amount=500.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        settings.current_price = 105.0
        self.system.positions["TEST"] = settings

        summary = self.system.get_position_summary()

        self.assertIsInstance(summary, dict)
        self.assertIn("total_positions", summary)
        self.assertIn("total_unrealized_pnl", summary)
        self.assertIn("positions", summary)

    def test_get_position_summary_no_positions(self):
        """ポジションなしのサマリー取得テスト"""
        summary = self.system.get_position_summary()

        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["total_positions"], 0)
        self.assertEqual(summary["total_unrealized_pnl"], 0.0)
        self.assertEqual(len(summary["positions"]), 0)

    def test_get_position_summary_exception(self):
        """ポジションサマリー取得例外処理テスト"""
        with patch.object(self.system, 'positions', side_effect=Exception("Summary error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                result = self.system.get_position_summary()
                
                self.assertEqual(result["status"], "error")
                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_get_performance_metrics_success(self):
        """パフォーマンス指標取得成功テスト"""
        # 執行履歴を追加
        execution1 = TradeExecution(
            timestamp=datetime.now(),
            symbol="TEST1",
            trade_type="STOP_LOSS",
            entry_price=100.0,
            exit_price=95.0,
            position_size=100.0,
            pnl=-500.0,
            execution_reason="損切り価格到達",
            metadata={},
        )
        
        execution2 = TradeExecution(
            timestamp=datetime.now(),
            symbol="TEST2",
            trade_type="TAKE_PROFIT",
            entry_price=100.0,
            exit_price=110.0,
            position_size=100.0,
            pnl=1000.0,
            execution_reason="利確価格到達",
            metadata={},
        )
        
        self.system.execution_history = [execution1, execution2]

        metrics = self.system.get_performance_metrics(days=30)

        self.assertIsInstance(metrics, dict)
        self.assertIn("total_trades", metrics)
        self.assertIn("winning_trades", metrics)
        self.assertIn("losing_trades", metrics)
        self.assertIn("win_rate", metrics)
        self.assertIn("total_pnl", metrics)
        self.assertIn("avg_pnl", metrics)

    def test_get_performance_metrics_no_data(self):
        """データなしのパフォーマンス指標取得テスト"""
        metrics = self.system.get_performance_metrics(days=30)

        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics["status"], "no_data")

    def test_get_performance_metrics_exception(self):
        """パフォーマンス指標取得例外処理テスト"""
        with patch.object(self.system, 'execution_history', side_effect=Exception("Metrics error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                result = self.system.get_performance_metrics()
                
                self.assertEqual(result["status"], "error")
                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_export_performance_report_success(self):
        """パフォーマンスレポート出力成功テスト"""
        # 執行履歴を追加
        execution1 = TradeExecution(
            timestamp=datetime.now(),
            symbol="TEST1",
            trade_type="STOP_LOSS",
            entry_price=100.0,
            exit_price=95.0,
            position_size=100.0,
            pnl=-500.0,
            execution_reason="損切り価格到達",
            metadata={},
        )
        
        execution2 = TradeExecution(
            timestamp=datetime.now(),
            symbol="TEST2",
            trade_type="TAKE_PROFIT",
            entry_price=100.0,
            exit_price=110.0,
            position_size=100.0,
            pnl=1000.0,
            execution_reason="利確価格到達",
            metadata={},
        )
        
        self.system.execution_history = [execution1, execution2]

        report = self.system.export_performance_report(days=30)

        self.assertIsInstance(report, dict)
        self.assertIn("report_period", report)
        self.assertIn("total_executions", report)
        self.assertIn("symbol_statistics", report)
        self.assertIn("performance_metrics", report)
        self.assertIn("generated_at", report)

    def test_export_performance_report_exception(self):
        """パフォーマンスレポート出力例外処理テスト"""
        with patch.object(self.system, 'execution_history', side_effect=Exception("Report error")):
            with patch.object(self.system.logger, 'error') as mock_error:
                result = self.system.export_performance_report()
                
                self.assertIn("error", result)
                mock_error.assert_called_once()

    def test_add_alert_callback(self):
        """アラートコールバック追加テスト"""
        callback = Mock()
        self.system.add_alert_callback(callback)
        
        self.assertIn(callback, self.system.alert_callbacks)

    def test_add_execution_callback(self):
        """執行コールバック追加テスト"""
        callback = Mock()
        self.system.add_execution_callback(callback)
        
        self.assertIn(callback, self.system.execution_callbacks)


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
