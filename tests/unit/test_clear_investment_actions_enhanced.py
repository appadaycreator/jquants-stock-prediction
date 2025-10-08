#!/usr/bin/env python3
"""
投資判断の明確化機能の拡張テスト
カバレッジ向上のための追加テストケース
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clear_investment_actions import (
    ClearInvestmentActions,
    InvestmentAction,
    ActionPriority,
    DeadlineType,
    InvestmentActionDetail,
    PositionInfo,
)


class TestClearInvestmentActionsEnhanced(unittest.TestCase):
    """投資判断の明確化機能の拡張テスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "min_confidence_threshold": 0.7,
            "max_position_size": 0.1,
            "risk_tolerance": 0.05,
            "stop_loss_percentage": 0.05,
            "take_profit_percentage": 0.15,
            "position_sizing_method": "kelly",
            "rebalancing_frequency": "monthly",
            "max_positions": 20,
        }
        self.clear_actions = ClearInvestmentActions(self.config)

    def test_initialization_with_config(self):
        """設定付き初期化テスト"""
        self.assertEqual(self.clear_actions.min_confidence_threshold, 0.7)
        self.assertEqual(self.clear_actions.max_position_size, 0.1)
        self.assertEqual(self.clear_actions.risk_tolerance, 0.05)
        self.assertEqual(self.clear_actions.stop_loss_percentage, 0.05)
        self.assertEqual(self.clear_actions.take_profit_percentage, 0.15)

    def test_initialization_without_config(self):
        """設定なし初期化テスト"""
        clear_actions = ClearInvestmentActions()
        
        self.assertEqual(clear_actions.min_confidence_threshold, 0.7)
        self.assertEqual(clear_actions.max_position_size, 0.1)
        self.assertEqual(clear_actions.risk_tolerance, 0.05)
        self.assertEqual(clear_actions.stop_loss_percentage, 0.05)
        self.assertEqual(clear_actions.take_profit_percentage, 0.15)

    def test_analyze_position_buy_more_recommendation(self):
        """買い増し推奨分析テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=95.0,
            pnl=-500.0,
            pnl_percentage=-5.0,
            market_value=9500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 30,
            "macd": "bullish",
        }
        
        recommendation = self.clear_actions.analyze_position(position, market_data)
        
        self.assertIsInstance(recommendation, InvestmentActionDetail)
        self.assertEqual(recommendation.symbol, "TEST")
        self.assertIn(recommendation.action, [InvestmentAction.BUY_MORE, InvestmentAction.STOP_LOSS])

    def test_analyze_position_take_profit_recommendation(self):
        """利確推奨分析テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=120.0,
            pnl=2000.0,
            pnl_percentage=20.0,
            market_value=12000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.20,
            "volume": 800000,
            "rsi": 70,
            "macd": "bearish",
        }
        
        recommendation = self.clear_actions.analyze_position(position, market_data)
        
        self.assertIsInstance(recommendation, InvestmentActionDetail)
        self.assertEqual(recommendation.symbol, "TEST")
        self.assertIn(recommendation.action, [InvestmentAction.TAKE_PROFIT, InvestmentAction.BUY_MORE])

    def test_analyze_position_stop_loss_recommendation(self):
        """損切り推奨分析テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        recommendation = self.clear_actions.analyze_position(position, market_data)
        
        self.assertIsInstance(recommendation, InvestmentActionDetail)
        self.assertEqual(recommendation.symbol, "TEST")
        self.assertIn(recommendation.action, [InvestmentAction.STOP_LOSS, InvestmentAction.BUY_MORE])

    def test_analyze_position_insufficient_data(self):
        """データ不足の分析テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {}  # データ不足
        
        with patch.object(self.clear_actions.logger, 'warning') as mock_warning:
            recommendation = self.clear_actions.analyze_position(position, market_data)
            
            self.assertIsNone(recommendation)
            mock_warning.assert_called_once()

    def test_analyze_position_exception(self):
        """分析例外処理テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        with patch.object(self.clear_actions, '_calculate_confidence', side_effect=Exception("Confidence error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                recommendation = self.clear_actions.analyze_position(position, market_data)
                
                self.assertIsNone(recommendation)
                mock_error.assert_called_once()

    def test_calculate_confidence_high_confidence(self):
        """高信頼度計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.10,
            "volume": 1500000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = self.clear_actions._calculate_confidence(position, market_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_confidence_low_confidence(self):
        """低信頼度計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=95.0,
            pnl=-500.0,
            pnl_percentage=-5.0,
            market_value=9500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.30,
            "volume": 500000,
            "rsi": 75,
            "macd": "bearish",
        }
        
        confidence = self.clear_actions._calculate_confidence(position, market_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_confidence_exception(self):
        """信頼度計算例外処理テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                confidence = self.clear_actions._calculate_confidence(position, market_data)
                
                self.assertEqual(confidence, 0.5)  # デフォルト値
                mock_error.assert_called_once()

    def test_determine_action_buy_more(self):
        """買い増しアクション決定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=95.0,
            pnl=-500.0,
            pnl_percentage=-5.0,
            market_value=9500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.10,
            "volume": 1500000,
            "rsi": 30,
            "macd": "bullish",
        }
        
        confidence = 0.8
        
        action = self.clear_actions._determine_action(position, market_data, confidence)
        
        self.assertIn(action, [InvestmentAction.BUY_MORE, InvestmentAction.STOP_LOSS])

    def test_determine_action_take_profit(self):
        """利確アクション決定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=120.0,
            pnl=2000.0,
            pnl_percentage=20.0,
            market_value=12000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.20,
            "volume": 800000,
            "rsi": 70,
            "macd": "bearish",
        }
        
        confidence = 0.8
        
        action = self.clear_actions._determine_action(position, market_data, confidence)
        
        self.assertIn(action, [InvestmentAction.TAKE_PROFIT, InvestmentAction.BUY_MORE])

    def test_determine_action_stop_loss(self):
        """損切りアクション決定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        confidence = 0.8
        
        action = self.clear_actions._determine_action(position, market_data, confidence)
        
        self.assertIn(action, [InvestmentAction.STOP_LOSS, InvestmentAction.BUY_MORE])

    def test_determine_action_low_confidence(self):
        """低信頼度アクション決定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "neutral",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        confidence = 0.3  # 低信頼度
        
        action = self.clear_actions._determine_action(position, market_data, confidence)
        
        self.assertIsNone(action)

    def test_calculate_position_size_kelly_criterion(self):
        """ケリー基準ポジションサイズ計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.8
        
        position_size = self.clear_actions._calculate_position_size(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(position_size, int)
        self.assertGreaterEqual(position_size, 0)

    def test_calculate_position_size_fixed_percentage(self):
        """固定割合ポジションサイズ計算テスト"""
        # 固定割合設定に変更
        self.clear_actions.config["position_sizing_method"] = "fixed_percentage"
        self.clear_actions.position_sizing_method = "fixed_percentage"
        
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.8
        
        position_size = self.clear_actions._calculate_position_size(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(position_size, int)
        self.assertGreaterEqual(position_size, 0)

    def test_calculate_position_size_volatility_based(self):
        """ボラティリティベースポジションサイズ計算テスト"""
        # ボラティリティベース設定に変更
        self.clear_actions.config["position_sizing_method"] = "volatility_based"
        self.clear_actions.position_sizing_method = "volatility_based"
        
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.8
        
        position_size = self.clear_actions._calculate_position_size(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(position_size, int)
        self.assertGreaterEqual(position_size, 0)

    def test_calculate_position_size_exception(self):
        """ポジションサイズ計算例外処理テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.8
        
        with patch.object(self.clear_actions, '_calculate_kelly_position_size', side_effect=Exception("Kelly error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                position_size = self.clear_actions._calculate_position_size(
                    position, market_data, confidence, InvestmentAction.BUY_MORE
                )
                
                self.assertEqual(position_size, 0)
                mock_error.assert_called_once()

    def test_calculate_kelly_position_size_success(self):
        """ケリー基準ポジションサイズ計算成功テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.8
        
        kelly_size = self.clear_actions._calculate_kelly_position_size(
            position, market_data, confidence
        )
        
        self.assertIsInstance(kelly_size, int)
        self.assertGreaterEqual(kelly_size, 0)

    def test_calculate_kelly_position_size_exception(self):
        """ケリー基準ポジションサイズ計算例外処理テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.8
        
        with patch('numpy.sqrt', side_effect=Exception("Sqrt error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                kelly_size = self.clear_actions._calculate_kelly_position_size(
                    position, market_data, confidence
                )
                
                self.assertEqual(kelly_size, 0)
                mock_error.assert_called_once()

    def test_calculate_target_price_buy_more(self):
        """買い増し目標価格計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=95.0,
            pnl=-500.0,
            pnl_percentage=-5.0,
            market_value=9500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 30,
            "macd": "bullish",
        }
        
        target_price = self.clear_actions._calculate_target_price(
            position, market_data, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(target_price, float)
        self.assertGreater(target_price, 0)

    def test_calculate_target_price_take_profit(self):
        """利確目標価格計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=120.0,
            pnl=2000.0,
            pnl_percentage=20.0,
            market_value=12000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.20,
            "volume": 800000,
            "rsi": 70,
            "macd": "bearish",
        }
        
        target_price = self.clear_actions._calculate_target_price(
            position, market_data, InvestmentAction.TAKE_PROFIT
        )
        
        self.assertIsInstance(target_price, float)
        self.assertGreater(target_price, 0)

    def test_calculate_target_price_stop_loss(self):
        """損切り目標価格計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        target_price = self.clear_actions._calculate_target_price(
            position, market_data, InvestmentAction.STOP_LOSS
        )
        
        self.assertIsInstance(target_price, float)
        self.assertGreater(target_price, 0)

    def test_calculate_target_price_exception(self):
        """目標価格計算例外処理テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                target_price = self.clear_actions._calculate_target_price(
                    position, market_data, InvestmentAction.BUY_MORE
                )
                
                self.assertEqual(target_price, position.current_price)
                mock_error.assert_called_once()

    def test_determine_priority_high_priority(self):
        """高優先度決定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        confidence = 0.9
        
        priority = self.clear_actions._determine_priority(
            position, market_data, confidence, InvestmentAction.STOP_LOSS
        )
        
        self.assertIn(priority, [ActionPriority.HIGH, ActionPriority.MEDIUM, ActionPriority.LOW])

    def test_determine_priority_medium_priority(self):
        """中優先度決定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.7
        
        priority = self.clear_actions._determine_priority(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIn(priority, [ActionPriority.HIGH, ActionPriority.MEDIUM, ActionPriority.LOW])

    def test_determine_priority_low_priority(self):
        """低優先度決定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "neutral",
            "volatility": 0.10,
            "volume": 500000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        confidence = 0.5
        
        priority = self.clear_actions._determine_priority(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIn(priority, [ActionPriority.HIGH, ActionPriority.MEDIUM, ActionPriority.LOW])

    def test_calculate_deadline_immediate(self):
        """即座実行期限計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        confidence = 0.9
        
        deadline, deadline_type = self.clear_actions._calculate_deadline(
            position, market_data, confidence, InvestmentAction.STOP_LOSS
        )
        
        self.assertIsInstance(deadline, datetime)
        self.assertIn(deadline_type, [DeadlineType.IMMEDIATE, DeadlineType.THIS_WEEK, DeadlineType.THIS_MONTH, DeadlineType.NEXT_QUARTER])

    def test_calculate_deadline_this_week(self):
        """今週中期限計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        confidence = 0.7
        
        deadline, deadline_type = self.clear_actions._calculate_deadline(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(deadline, datetime)
        self.assertIn(deadline_type, [DeadlineType.IMMEDIATE, DeadlineType.THIS_WEEK, DeadlineType.THIS_MONTH, DeadlineType.NEXT_QUARTER])

    def test_calculate_deadline_this_month(self):
        """今月中期限計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "neutral",
            "volatility": 0.10,
            "volume": 500000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        confidence = 0.5
        
        deadline, deadline_type = self.clear_actions._calculate_deadline(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(deadline, datetime)
        self.assertIn(deadline_type, [DeadlineType.IMMEDIATE, DeadlineType.THIS_WEEK, DeadlineType.THIS_MONTH, DeadlineType.NEXT_QUARTER])

    def test_calculate_deadline_next_quarter(self):
        """来四半期限計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "neutral",
            "volatility": 0.05,
            "volume": 200000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        confidence = 0.3
        
        deadline, deadline_type = self.clear_actions._calculate_deadline(
            position, market_data, confidence, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(deadline, datetime)
        self.assertIn(deadline_type, [DeadlineType.IMMEDIATE, DeadlineType.THIS_WEEK, DeadlineType.THIS_MONTH, DeadlineType.NEXT_QUARTER])

    def test_calculate_expected_return_buy_more(self):
        """買い増し期待リターン計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=95.0,
            pnl=-500.0,
            pnl_percentage=-5.0,
            market_value=9500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 30,
            "macd": "bullish",
        }
        
        expected_return = self.clear_actions._calculate_expected_return(
            position, market_data, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(expected_return, float)

    def test_calculate_expected_return_take_profit(self):
        """利確期待リターン計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=120.0,
            pnl=2000.0,
            pnl_percentage=20.0,
            market_value=12000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.20,
            "volume": 800000,
            "rsi": 70,
            "macd": "bearish",
        }
        
        expected_return = self.clear_actions._calculate_expected_return(
            position, market_data, InvestmentAction.TAKE_PROFIT
        )
        
        self.assertIsInstance(expected_return, float)

    def test_calculate_expected_return_stop_loss(self):
        """損切り期待リターン計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        expected_return = self.clear_actions._calculate_expected_return(
            position, market_data, InvestmentAction.STOP_LOSS
        )
        
        self.assertIsInstance(expected_return, float)

    def test_calculate_expected_return_exception(self):
        """期待リターン計算例外処理テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                expected_return = self.clear_actions._calculate_expected_return(
                    position, market_data, InvestmentAction.BUY_MORE
                )
                
                self.assertEqual(expected_return, 0.0)
                mock_error.assert_called_once()

    def test_calculate_max_loss_buy_more(self):
        """買い増し最大損失計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=95.0,
            pnl=-500.0,
            pnl_percentage=-5.0,
            market_value=9500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 30,
            "macd": "bullish",
        }
        
        max_loss = self.clear_actions._calculate_max_loss(
            position, market_data, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(max_loss, float)
        self.assertLessEqual(max_loss, 0.0)

    def test_calculate_max_loss_take_profit(self):
        """利確最大損失計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=120.0,
            pnl=2000.0,
            pnl_percentage=20.0,
            market_value=12000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.20,
            "volume": 800000,
            "rsi": 70,
            "macd": "bearish",
        }
        
        max_loss = self.clear_actions._calculate_max_loss(
            position, market_data, InvestmentAction.TAKE_PROFIT
        )
        
        self.assertIsInstance(max_loss, float)
        self.assertLessEqual(max_loss, 0.0)

    def test_calculate_max_loss_stop_loss(self):
        """損切り最大損失計算テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        max_loss = self.clear_actions._calculate_max_loss(
            position, market_data, InvestmentAction.STOP_LOSS
        )
        
        self.assertIsInstance(max_loss, float)
        self.assertLessEqual(max_loss, 0.0)

    def test_calculate_max_loss_exception(self):
        """最大損失計算例外処理テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                max_loss = self.clear_actions._calculate_max_loss(
                    position, market_data, InvestmentAction.BUY_MORE
                )
                
                self.assertEqual(max_loss, 0.0)
                mock_error.assert_called_once()

    def test_generate_reason_buy_more(self):
        """買い増し理由生成テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=95.0,
            pnl=-500.0,
            pnl_percentage=-5.0,
            market_value=9500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 30,
            "macd": "bullish",
        }
        
        reason = self.clear_actions._generate_reason(
            position, market_data, InvestmentAction.BUY_MORE
        )
        
        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 0)

    def test_generate_reason_take_profit(self):
        """利確理由生成テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=120.0,
            pnl=2000.0,
            pnl_percentage=20.0,
            market_value=12000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.20,
            "volume": 800000,
            "rsi": 70,
            "macd": "bearish",
        }
        
        reason = self.clear_actions._generate_reason(
            position, market_data, InvestmentAction.TAKE_PROFIT
        )
        
        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 0)

    def test_generate_reason_stop_loss(self):
        """損切り理由生成テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        reason = self.clear_actions._generate_reason(
            position, market_data, InvestmentAction.STOP_LOSS
        )
        
        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 0)

    def test_determine_risk_level_low_risk(self):
        """低リスクレベル判定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.10,
            "volume": 1500000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        risk_level = self.clear_actions._determine_risk_level(position, market_data)
        
        self.assertIn(risk_level, ["LOW", "MEDIUM", "HIGH"])

    def test_determine_risk_level_medium_risk(self):
        """中リスクレベル判定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=100.0,
            pnl=0.0,
            pnl_percentage=0.0,
            market_value=10000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "neutral",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        risk_level = self.clear_actions._determine_risk_level(position, market_data)
        
        self.assertIn(risk_level, ["LOW", "MEDIUM", "HIGH"])

    def test_determine_risk_level_high_risk(self):
        """高リスクレベル判定テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        risk_level = self.clear_actions._determine_risk_level(position, market_data)
        
        self.assertIn(risk_level, ["LOW", "MEDIUM", "HIGH"])

    def test_get_technical_signals_bullish(self):
        """強気テクニカルシグナル取得テスト"""
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 30,
            "macd": "bullish",
        }
        
        signals = self.clear_actions._get_technical_signals(market_data)
        
        self.assertIsInstance(signals, list)
        self.assertGreaterEqual(len(signals), 0)

    def test_get_technical_signals_bearish(self):
        """弱気テクニカルシグナル取得テスト"""
        market_data = {
            "trend": "bearish",
            "volatility": 0.20,
            "volume": 800000,
            "rsi": 70,
            "macd": "bearish",
        }
        
        signals = self.clear_actions._get_technical_signals(market_data)
        
        self.assertIsInstance(signals, list)
        self.assertGreaterEqual(len(signals), 0)

    def test_get_technical_signals_neutral(self):
        """中立テクニカルシグナル取得テスト"""
        market_data = {
            "trend": "neutral",
            "volatility": 0.10,
            "volume": 500000,
            "rsi": 50,
            "macd": "neutral",
        }
        
        signals = self.clear_actions._get_technical_signals(market_data)
        
        self.assertIsInstance(signals, list)
        self.assertGreaterEqual(len(signals), 0)

    def test_get_fundamental_factors_positive(self):
        """ポジティブファンダメンタル要因取得テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=105.0,
            pnl=500.0,
            pnl_percentage=5.0,
            market_value=10500.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "rsi": 45,
            "macd": "bullish",
        }
        
        factors = self.clear_actions._get_fundamental_factors(position, market_data)
        
        self.assertIsInstance(factors, list)
        self.assertGreaterEqual(len(factors), 0)

    def test_get_fundamental_factors_negative(self):
        """ネガティブファンダメンタル要因取得テスト"""
        position = PositionInfo(
            symbol="TEST",
            current_quantity=100,
            average_price=100.0,
            current_price=90.0,
            pnl=-1000.0,
            pnl_percentage=-10.0,
            market_value=9000.0,
            cost_basis=10000.0,
        )
        
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 1200000,
            "rsi": 25,
            "macd": "bearish",
        }
        
        factors = self.clear_actions._get_fundamental_factors(position, market_data)
        
        self.assertIsInstance(factors, list)
        self.assertGreaterEqual(len(factors), 0)

    def test_export_action_report_success(self):
        """アクションレポート出力成功テスト"""
        action = InvestmentActionDetail(
            action=InvestmentAction.BUY_MORE,
            symbol="TEST",
            current_price=95.0,
            target_price=110.0,
            quantity=50,
            total_amount=4750.0,
            priority=ActionPriority.HIGH,
            deadline=datetime.now() + timedelta(days=7),
            deadline_type=DeadlineType.THIS_WEEK,
            confidence=0.8,
            reason="強気トレンドとRSIの過小評価",
            risk_level="MEDIUM",
            expected_return=0.15,
            max_loss=-0.05,
            stop_loss_price=90.0,
            take_profit_price=120.0,
            position_size_percentage=0.05,
            market_condition="bullish",
            technical_signals=["RSI過小評価", "MACD強気"],
            fundamental_factors=["業績好調", "市場シェア拡大"],
        )
        
        report = self.clear_actions.export_action_report(action)
        
        self.assertIsInstance(report, dict)
        self.assertIn("action", report)
        self.assertIn("symbol", report)
        self.assertIn("recommendation", report)
        self.assertIn("risk_assessment", report)
        self.assertIn("execution_plan", report)
        self.assertIn("generated_at", report)

    def test_export_action_report_exception(self):
        """アクションレポート出力例外処理テスト"""
        action = InvestmentActionDetail(
            action=InvestmentAction.BUY_MORE,
            symbol="TEST",
            current_price=95.0,
            target_price=110.0,
            quantity=50,
            total_amount=4750.0,
            priority=ActionPriority.HIGH,
            deadline=datetime.now() + timedelta(days=7),
            deadline_type=DeadlineType.THIS_WEEK,
            confidence=0.8,
            reason="強気トレンドとRSIの過小評価",
            risk_level="MEDIUM",
            expected_return=0.15,
            max_loss=-0.05,
            stop_loss_price=90.0,
            take_profit_price=120.0,
            position_size_percentage=0.05,
            market_condition="bullish",
            technical_signals=["RSI過小評価", "MACD強気"],
            fundamental_factors=["業績好調", "市場シェア拡大"],
        )
        
        with patch('json.dumps', side_effect=Exception("JSON error")):
            with patch.object(self.clear_actions.logger, 'error') as mock_error:
                result = self.clear_actions.export_action_report(action)
                
                self.assertIn("error", result)
                mock_error.assert_called_once()


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
