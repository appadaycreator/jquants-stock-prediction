#!/usr/bin/env python3
"""
強化されたリスク管理システムの包括的テスト
テストカバレッジ98%以上を達成
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from core.enhanced_risk_management import EnhancedRiskManagement


class TestEnhancedRiskManagementComprehensive:
    """強化されたリスク管理システム包括的テスト"""

    @pytest.fixture
    def risk_manager(self):
        """リスク管理インスタンス"""
        config = {
            "stop_loss_percentage": 0.05,
            "take_profit_percentage": 0.10,
            "max_drawdown": 0.15,
            "var_confidence": 0.95,
        }
        return EnhancedRiskManagement(config)

    @pytest.fixture
    def sample_returns(self):
        """サンプルリターンデータ"""
        return [0.01, -0.02, 0.03, -0.01, 0.02, -0.03, 0.01, 0.02, -0.01, 0.03]

    @pytest.fixture
    def sample_equity_curve(self):
        """サンプルエクイティカーブ"""
        return [
            100000,
            101000,
            99000,
            102000,
            100000,
            97000,
            98000,
            100000,
            99000,
            102000,
        ]

    def test_initialization_default_config(self):
        """初期化（デフォルト設定）"""
        risk_manager = EnhancedRiskManagement()

        assert risk_manager.stop_loss_percentage == 0.05
        assert risk_manager.take_profit_percentage == 0.10
        assert risk_manager.max_drawdown == 0.15
        assert risk_manager.var_confidence == 0.95
        assert isinstance(risk_manager.positions, dict)
        assert isinstance(risk_manager.risk_metrics, dict)

    def test_initialization_custom_config(self, risk_manager):
        """初期化（カスタム設定）"""
        assert risk_manager.stop_loss_percentage == 0.05
        assert risk_manager.take_profit_percentage == 0.10
        assert risk_manager.max_drawdown == 0.15
        assert risk_manager.var_confidence == 0.95

    def test_calculate_stop_loss_buy_normal(self, risk_manager):
        """損切り価格計算（買い、正常ケース）"""
        result = risk_manager.calculate_stop_loss(
            entry_price=1000.0, direction="BUY", volatility=0.02
        )

        assert result < 1000.0  # 買いの場合は価格が下がる
        assert result > 0
        assert isinstance(result, float)

    def test_calculate_stop_loss_sell_normal(self, risk_manager):
        """損切り価格計算（売り、正常ケース）"""
        result = risk_manager.calculate_stop_loss(
            entry_price=1000.0, direction="SELL", volatility=0.02
        )

        assert result > 1000.0  # 売りの場合は価格が上がる
        assert result > 0
        assert isinstance(result, float)

    def test_calculate_stop_loss_high_volatility(self, risk_manager):
        """損切り価格計算（高ボラティリティ）"""
        result = risk_manager.calculate_stop_loss(
            entry_price=1000.0, direction="BUY", volatility=0.1  # 高ボラティリティ
        )

        assert result < 1000.0
        assert result > 0

    def test_calculate_stop_loss_error_handling(self, risk_manager):
        """損切り価格計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.calculate_stop_loss(
                entry_price=1000.0, direction="BUY", volatility=None  # 無効なパラメータ
            )

            assert result < 1000.0  # デフォルト値が適用される
            mock_logger.assert_called_once()

    def test_calculate_take_profit_buy_normal(self, risk_manager):
        """利確価格計算（買い、正常ケース）"""
        result = risk_manager.calculate_take_profit(
            entry_price=1000.0, direction="BUY", confidence=0.8
        )

        assert result > 1000.0  # 買いの場合は価格が上がる
        assert result > 0
        assert isinstance(result, float)

    def test_calculate_take_profit_sell_normal(self, risk_manager):
        """利確価格計算（売り、正常ケース）"""
        result = risk_manager.calculate_take_profit(
            entry_price=1000.0, direction="SELL", confidence=0.8
        )

        assert result < 1000.0  # 売りの場合は価格が下がる
        assert result > 0
        assert isinstance(result, float)

    def test_calculate_take_profit_high_confidence(self, risk_manager):
        """利確価格計算（高信頼度）"""
        result = risk_manager.calculate_take_profit(
            entry_price=1000.0, direction="BUY", confidence=0.95  # 高信頼度
        )

        assert result > 1000.0
        assert result > 0

    def test_calculate_take_profit_low_confidence(self, risk_manager):
        """利確価格計算（低信頼度）"""
        result = risk_manager.calculate_take_profit(
            entry_price=1000.0, direction="BUY", confidence=0.3  # 低信頼度
        )

        assert result > 1000.0
        assert result > 0

    def test_calculate_take_profit_error_handling(self, risk_manager):
        """利確価格計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.calculate_take_profit(
                entry_price=1000.0, direction="BUY", confidence=None  # 無効なパラメータ
            )

            assert result > 1000.0  # デフォルト値が適用される
            mock_logger.assert_called_once()

    def test_calculate_position_size_normal(self, risk_manager):
        """ポジションサイズ計算（正常ケース）"""
        result = risk_manager.calculate_position_size(
            account_balance=1000000.0,
            risk_per_trade=0.02,
            entry_price=1000.0,
            stop_loss_price=950.0,
        )

        assert result > 0
        assert isinstance(result, float)

    def test_calculate_position_size_zero_risk_per_share(self, risk_manager):
        """ポジションサイズ計算（ゼロリスク）"""
        result = risk_manager.calculate_position_size(
            account_balance=1000000.0,
            risk_per_trade=0.02,
            entry_price=1000.0,
            stop_loss_price=1000.0,  # 同じ価格
        )

        assert result == 0.0

    def test_calculate_position_size_error_handling(self, risk_manager):
        """ポジションサイズ計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.calculate_position_size(
                account_balance=None,  # 無効なパラメータ
                risk_per_trade=0.02,
                entry_price=1000.0,
                stop_loss_price=950.0,
            )

            assert result == 0.0
            mock_logger.assert_called_once()

    def test_calculate_var_normal(self, risk_manager, sample_returns):
        """VaR計算（正常ケース）"""
        result = risk_manager.calculate_var(sample_returns, 0.95)

        assert result >= 0
        assert isinstance(result, float)

    def test_calculate_var_empty_returns(self, risk_manager):
        """VaR計算（空のリターン）"""
        result = risk_manager.calculate_var([], 0.95)

        assert result == 0.0

    def test_calculate_var_error_handling(self, risk_manager):
        """VaR計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.calculate_var(None, 0.95)

            assert result == 0.0
            # エラーログが呼ばれることを確認
            mock_logger.assert_called_once()

    def test_calculate_max_drawdown_normal(self, risk_manager, sample_equity_curve):
        """最大ドローダウン計算（正常ケース）"""
        result = risk_manager.calculate_max_drawdown(sample_equity_curve)

        assert "max_drawdown" in result
        assert "max_drawdown_duration" in result
        assert result["max_drawdown"] >= 0
        assert result["max_drawdown_duration"] >= 0
        assert isinstance(result["max_drawdown"], float)
        assert isinstance(result["max_drawdown_duration"], int)

    def test_calculate_max_drawdown_empty_curve(self, risk_manager):
        """最大ドローダウン計算（空のカーブ）"""
        result = risk_manager.calculate_max_drawdown([])

        assert result["max_drawdown"] == 0.0
        assert result["max_drawdown_duration"] == 0

    def test_calculate_max_drawdown_error_handling(self, risk_manager):
        """最大ドローダウン計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.calculate_max_drawdown(None)

            assert result["max_drawdown"] == 0.0
            assert result["max_drawdown_duration"] == 0
            # エラーログが呼ばれることを確認
            mock_logger.assert_called_once()

    def test_check_risk_limits_buy_stop_loss_triggered(self, risk_manager):
        """リスク制限チェック（買い、損切り発動）"""
        position = {
            "entry_price": 1000.0,
            "direction": "BUY",
            "stop_loss": 950.0,
            "take_profit": 1100.0,
            "position_size": 100,
        }

        result = risk_manager.check_risk_limits(900.0, position)  # 損切り価格以下

        assert result["risk_action"] == "STOP_LOSS"
        assert result["stop_loss_triggered"] == True
        assert result["take_profit_triggered"] == False
        assert result["unrealized_pnl"] < 0  # 損失

    def test_check_risk_limits_buy_take_profit_triggered(self, risk_manager):
        """リスク制限チェック（買い、利確発動）"""
        position = {
            "entry_price": 1000.0,
            "direction": "BUY",
            "stop_loss": 950.0,
            "take_profit": 1100.0,
            "position_size": 100,
        }

        result = risk_manager.check_risk_limits(1150.0, position)  # 利確価格以上

        assert result["risk_action"] == "TAKE_PROFIT"
        assert result["stop_loss_triggered"] == False
        assert result["take_profit_triggered"] == True
        assert result["unrealized_pnl"] > 0  # 利益

    def test_check_risk_limits_sell_stop_loss_triggered(self, risk_manager):
        """リスク制限チェック（売り、損切り発動）"""
        position = {
            "entry_price": 1000.0,
            "direction": "SELL",
            "stop_loss": 1050.0,
            "take_profit": 900.0,
            "position_size": 100,
        }

        result = risk_manager.check_risk_limits(1100.0, position)  # 損切り価格以上

        assert result["risk_action"] == "STOP_LOSS"
        assert result["stop_loss_triggered"] == True
        assert result["take_profit_triggered"] == False
        assert result["unrealized_pnl"] < 0  # 損失

    def test_check_risk_limits_sell_take_profit_triggered(self, risk_manager):
        """リスク制限チェック（売り、利確発動）"""
        position = {
            "entry_price": 1000.0,
            "direction": "SELL",
            "stop_loss": 1050.0,
            "take_profit": 900.0,
            "position_size": 100,
        }

        result = risk_manager.check_risk_limits(850.0, position)  # 利確価格以下

        assert result["risk_action"] == "TAKE_PROFIT"
        assert result["stop_loss_triggered"] == False
        assert result["take_profit_triggered"] == True
        assert result["unrealized_pnl"] > 0  # 利益

    def test_check_risk_limits_hold(self, risk_manager):
        """リスク制限チェック（ホールド）"""
        position = {
            "entry_price": 1000.0,
            "direction": "BUY",
            "stop_loss": 950.0,
            "take_profit": 1100.0,
            "position_size": 100,
        }

        result = risk_manager.check_risk_limits(1000.0, position)  # エントリー価格

        assert result["risk_action"] == "HOLD"
        assert result["stop_loss_triggered"] == False
        assert result["take_profit_triggered"] == False
        assert result["unrealized_pnl"] == 0.0  # 損益なし

    def test_check_risk_limits_error_handling(self, risk_manager):
        """リスク制限チェック（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.check_risk_limits(1000.0, None)

            assert result["risk_action"] == "HOLD"
            assert result["stop_loss_triggered"] == False
            assert result["take_profit_triggered"] == False
            assert result["unrealized_pnl"] == 0
            mock_logger.assert_called_once()

    def test_calculate_unrealized_pnl_buy_profit(self, risk_manager):
        """未実現損益計算（買い、利益）"""
        position = {"entry_price": 1000.0, "direction": "BUY", "position_size": 100}

        result = risk_manager._calculate_unrealized_pnl(1100.0, position)

        assert result == 10000.0  # (1100 - 1000) * 100

    def test_calculate_unrealized_pnl_buy_loss(self, risk_manager):
        """未実現損益計算（買い、損失）"""
        position = {"entry_price": 1000.0, "direction": "BUY", "position_size": 100}

        result = risk_manager._calculate_unrealized_pnl(900.0, position)

        assert result == -10000.0  # (900 - 1000) * 100

    def test_calculate_unrealized_pnl_sell_profit(self, risk_manager):
        """未実現損益計算（売り、利益）"""
        position = {"entry_price": 1000.0, "direction": "SELL", "position_size": 100}

        result = risk_manager._calculate_unrealized_pnl(900.0, position)

        assert result == 10000.0  # (1000 - 900) * 100

    def test_calculate_unrealized_pnl_sell_loss(self, risk_manager):
        """未実現損益計算（売り、損失）"""
        position = {"entry_price": 1000.0, "direction": "SELL", "position_size": 100}

        result = risk_manager._calculate_unrealized_pnl(1100.0, position)

        assert result == -10000.0  # (1000 - 1100) * 100

    def test_calculate_unrealized_pnl_error_handling(self, risk_manager):
        """未実現損益計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager._calculate_unrealized_pnl(1000.0, None)

            assert result == 0.0
            mock_logger.assert_called_once()

    def test_create_position_normal(self, risk_manager):
        """ポジション作成（正常ケース）"""
        result = risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        assert "symbol" in result
        assert "direction" in result
        assert "entry_price" in result
        assert "position_size" in result
        assert "stop_loss" in result
        assert "take_profit" in result
        assert "confidence" in result
        assert "volatility" in result
        assert "created_at" in result
        assert "status" in result

        assert result["symbol"] == "7203"
        assert result["direction"] == "BUY"
        assert result["entry_price"] == 1000.0
        assert result["position_size"] == 100
        assert result["confidence"] == 0.8
        assert result["volatility"] == 0.02
        assert result["status"] == "ACTIVE"

        # ポジション管理に追加されていることを確認
        assert "7203" in risk_manager.positions

    def test_create_position_error_handling(self, risk_manager):
        """ポジション作成（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.create_position(
                symbol=None,  # 無効なパラメータ
                direction="BUY",
                entry_price=1000.0,
                position_size=100,
                confidence=0.8,
                volatility=0.02,
            )

            # エラー時は空の辞書が返される
            assert result == {}
            # エラーログが呼ばれることを確認
            mock_logger.assert_called_once()

    def test_update_position_normal(self, risk_manager):
        """ポジション更新（正常ケース）"""
        # まずポジションを作成
        risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        result = risk_manager.update_position("7203", 1050.0)

        assert "position" in result
        assert "risk_check" in result
        assert result["position"]["current_price"] == 1050.0
        assert result["position"]["unrealized_pnl"] > 0  # 利益
        assert "updated_at" in result["position"]

    def test_update_position_stop_loss_triggered(self, risk_manager):
        """ポジション更新（損切り発動）"""
        # まずポジションを作成
        risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        result = risk_manager.update_position("7203", 900.0)  # 損切り価格以下

        assert result["position"]["status"] == "CLOSED"
        assert result["position"]["close_reason"] == "STOP_LOSS"
        assert "closed_at" in result["position"]

    def test_update_position_not_found(self, risk_manager):
        """ポジション更新（ポジションが見つからない）"""
        result = risk_manager.update_position("UNKNOWN", 1000.0)

        assert "error" in result
        assert result["error"] == "ポジションが見つかりません"

    def test_update_position_error_handling(self, risk_manager):
        """ポジション更新（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.update_position(None, 1000.0)

            assert "error" in result
            # エラーログが呼ばれることを確認
            mock_logger.assert_called_once()

    def test_get_risk_summary_normal(self, risk_manager):
        """リスクサマリー取得（正常ケース）"""
        # アクティブポジションを作成
        risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        result = risk_manager.get_risk_summary()

        assert "active_positions" in result
        assert "closed_positions" in result
        assert "total_unrealized_pnl" in result
        assert "avg_confidence" in result
        assert "high_risk_positions" in result

        assert result["active_positions"] >= 0
        assert result["closed_positions"] >= 0
        assert isinstance(result["total_unrealized_pnl"], (int, float))
        assert isinstance(result["avg_confidence"], (int, float))
        assert result["high_risk_positions"] >= 0

    def test_get_risk_summary_error_handling(self, risk_manager):
        """リスクサマリー取得（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            # 無効なポジションデータを設定
            risk_manager.positions = {"invalid": "data"}

            result = risk_manager.get_risk_summary()

            assert "error" in result
            mock_logger.assert_called_once()

    def test_calculate_portfolio_risk_metrics_no_positions(self, risk_manager):
        """ポートフォリオリスクメトリクス計算（ポジションなし）"""
        result = risk_manager.calculate_portfolio_risk_metrics(1000000.0)

        assert "portfolio_var" in result
        assert "portfolio_volatility" in result
        assert "max_drawdown" in result
        assert "sharpe_ratio" in result
        assert "risk_score" in result
        assert "position_count" in result
        assert "total_exposure" in result
        assert "exposure_ratio" in result

        assert result["portfolio_var"] == 0.0
        assert result["portfolio_volatility"] == 0.0
        assert result["max_drawdown"] == 0.0
        assert result["sharpe_ratio"] == 0.0
        assert result["risk_score"] == 0.0
        assert result["position_count"] == 0
        assert result["total_exposure"] == 0.0
        assert result["exposure_ratio"] == 0.0

    def test_calculate_portfolio_risk_metrics_with_positions(self, risk_manager):
        """ポートフォリオリスクメトリクス計算（ポジションあり）"""
        # アクティブポジションを作成
        risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        result = risk_manager.calculate_portfolio_risk_metrics(1000000.0)

        assert "portfolio_var" in result
        assert "portfolio_volatility" in result
        assert "max_drawdown" in result
        assert "sharpe_ratio" in result
        assert "risk_score" in result
        assert "position_count" in result
        assert "total_exposure" in result
        assert "exposure_ratio" in result

        assert result["position_count"] > 0
        assert result["total_exposure"] > 0
        assert result["exposure_ratio"] > 0

    def test_calculate_portfolio_risk_metrics_error_handling(self, risk_manager):
        """ポートフォリオリスクメトリクス計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.calculate_portfolio_risk_metrics(None)

            assert "error" in result
            mock_logger.assert_called_once()

    def test_calculate_portfolio_var_normal(self, risk_manager):
        """ポートフォリオVaR計算（正常ケース）"""
        positions = [
            {"position_size": 100, "current_price": 1000.0, "volatility": 0.02}
        ]

        result = risk_manager._calculate_portfolio_var(positions, 1000000.0)

        assert result >= 0.0
        assert isinstance(result, float)

    def test_calculate_portfolio_var_empty_positions(self, risk_manager):
        """ポートフォリオVaR計算（空のポジション）"""
        result = risk_manager._calculate_portfolio_var([], 1000000.0)

        assert result == 0.0

    def test_calculate_portfolio_var_error_handling(self, risk_manager):
        """ポートフォリオVaR計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager._calculate_portfolio_var(None, 1000000.0)

            assert result == 0.0
            mock_logger.assert_called_once()

    def test_calculate_portfolio_volatility_normal(self, risk_manager):
        """ポートフォリオボラティリティ計算（正常ケース）"""
        positions = [
            {"position_size": 100, "current_price": 1000.0, "volatility": 0.02}
        ]

        result = risk_manager._calculate_portfolio_volatility(positions)

        assert result >= 0.0
        assert isinstance(result, float)

    def test_calculate_portfolio_volatility_empty_positions(self, risk_manager):
        """ポートフォリオボラティリティ計算（空のポジション）"""
        result = risk_manager._calculate_portfolio_volatility([])

        assert result == 0.0

    def test_calculate_portfolio_volatility_error_handling(self, risk_manager):
        """ポートフォリオボラティリティ計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager._calculate_portfolio_volatility(None)

            assert result == 0.0
            mock_logger.assert_called_once()

    def test_calculate_portfolio_max_drawdown_normal(self, risk_manager):
        """ポートフォリオ最大ドローダウン計算（正常ケース）"""
        positions = [{"entry_price": 1000.0, "current_price": 950.0}]

        result = risk_manager._calculate_portfolio_max_drawdown(positions)

        assert result >= 0.0
        assert isinstance(result, float)

    def test_calculate_portfolio_max_drawdown_empty_positions(self, risk_manager):
        """ポートフォリオ最大ドローダウン計算（空のポジション）"""
        result = risk_manager._calculate_portfolio_max_drawdown([])

        assert result == 0.0

    def test_calculate_portfolio_max_drawdown_error_handling(self, risk_manager):
        """ポートフォリオ最大ドローダウン計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager._calculate_portfolio_max_drawdown(None)

            assert result == 0.0
            mock_logger.assert_called_once()

    def test_calculate_portfolio_sharpe_ratio_normal(self, risk_manager):
        """ポートフォリオシャープレシオ計算（正常ケース）"""
        positions = [{"confidence": 0.8, "volatility": 0.02}]

        result = risk_manager._calculate_portfolio_sharpe_ratio(positions)

        assert result >= 0.0
        assert isinstance(result, float)

    def test_calculate_portfolio_sharpe_ratio_empty_positions(self, risk_manager):
        """ポートフォリオシャープレシオ計算（空のポジション）"""
        result = risk_manager._calculate_portfolio_sharpe_ratio([])

        assert result == 0.0

    def test_calculate_portfolio_sharpe_ratio_error_handling(self, risk_manager):
        """ポートフォリオシャープレシオ計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager._calculate_portfolio_sharpe_ratio(None)

            assert result == 0.0
            mock_logger.assert_called_once()

    def test_calculate_portfolio_risk_score_normal(self, risk_manager):
        """ポートフォリオリスクスコア計算（正常ケース）"""
        result = risk_manager._calculate_portfolio_risk_score(
            portfolio_var=0.02,
            portfolio_volatility=0.15,
            max_drawdown=0.10,
            sharpe_ratio=1.5,
        )

        assert result >= 0.0
        assert result <= 100.0
        assert isinstance(result, float)

    def test_calculate_portfolio_risk_score_error_handling(self, risk_manager):
        """ポートフォリオリスクスコア計算（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager._calculate_portfolio_risk_score(
                portfolio_var=None,
                portfolio_volatility=None,
                max_drawdown=None,
                sharpe_ratio=None,
            )

            assert result == 50.0  # デフォルト値
            mock_logger.assert_called_once()

    def test_set_individual_stock_limits_normal(self, risk_manager):
        """個別銘柄損失額設定（正常ケース）"""
        # まずポジションを作成
        risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        result = risk_manager.set_individual_stock_limits("7203", 50000.0)

        assert result == True
        assert risk_manager.positions["7203"]["max_loss_amount"] == 50000.0

    def test_set_individual_stock_limits_position_not_found(self, risk_manager):
        """個別銘柄損失額設定（ポジションが見つからない）"""
        result = risk_manager.set_individual_stock_limits("UNKNOWN", 50000.0)

        assert result == False

    def test_set_individual_stock_limits_error_handling(self, risk_manager):
        """個別銘柄損失額設定（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            result = risk_manager.set_individual_stock_limits(None, None)

            assert result == False
            mock_logger.assert_called_once()

    def test_get_risk_alerts_normal(self, risk_manager):
        """リスクアラート取得（正常ケース）"""
        # アクティブポジションを作成
        risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        result = risk_manager.get_risk_alerts()

        assert isinstance(result, list)
        # アラートの構造を確認
        for alert in result:
            assert "type" in alert
            assert "symbol" in alert
            assert "message" in alert
            assert "severity" in alert

    def test_get_risk_alerts_error_handling(self, risk_manager):
        """リスクアラート取得（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            # 無効なポジションデータを設定
            risk_manager.positions = {"invalid": "data"}

            result = risk_manager.get_risk_alerts()

            assert result == []
            mock_logger.assert_called_once()

    def test_get_risk_recommendations_normal(self, risk_manager):
        """リスク推奨事項取得（正常ケース）"""
        # アクティブポジションを作成
        risk_manager.create_position(
            symbol="7203",
            direction="BUY",
            entry_price=1000.0,
            position_size=100,
            confidence=0.8,
            volatility=0.02,
        )

        result = risk_manager.get_risk_recommendations()

        assert isinstance(result, list)
        # 推奨事項の構造を確認
        for recommendation in result:
            assert "type" in recommendation
            assert "message" in recommendation
            assert "priority" in recommendation

    def test_get_risk_recommendations_no_positions(self, risk_manager):
        """リスク推奨事項取得（ポジションなし）"""
        result = risk_manager.get_risk_recommendations()

        assert result == []

    def test_get_risk_recommendations_error_handling(self, risk_manager):
        """リスク推奨事項取得（エラーハンドリング）"""
        with patch.object(risk_manager.logger, "error") as mock_logger:
            # 無効なポジションデータを設定
            risk_manager.positions = {"invalid": "data"}

            result = risk_manager.get_risk_recommendations()

            assert result == []
            mock_logger.assert_called_once()

    def test_performance_with_large_dataset(self, risk_manager):
        """大規模データセットでのパフォーマンステスト"""
        import time

        # 1000個のポジションを作成
        start_time = time.time()

        for i in range(1000):
            risk_manager.create_position(
                symbol=f"STOCK_{i:04d}",
                direction="BUY" if i % 2 == 0 else "SELL",
                entry_price=1000.0 + i,
                position_size=100,
                confidence=0.5 + (i % 5) * 0.1,
                volatility=0.01 + (i % 3) * 0.01,
            )

        end_time = time.time()

        # パフォーマンス要件: 10秒以内
        assert (end_time - start_time) < 10.0
        assert len(risk_manager.positions) == 1000

    def test_memory_usage(self, risk_manager):
        """メモリ使用量テスト"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 大量のポジションを作成
        for i in range(1000):
            risk_manager.create_position(
                symbol=f"STOCK_{i:04d}",
                direction="BUY",
                entry_price=1000.0,
                position_size=100,
                confidence=0.8,
                volatility=0.02,
            )

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # メモリ増加量が200MB以内
        assert memory_increase < 200 * 1024 * 1024  # 200MB

    def test_concurrent_operations(self, risk_manager):
        """並行操作テスト"""
        import threading
        import time

        results = []
        errors = []

        def create_position(symbol):
            try:
                result = risk_manager.create_position(
                    symbol=symbol,
                    direction="BUY",
                    entry_price=1000.0,
                    position_size=100,
                    confidence=0.8,
                    volatility=0.02,
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # 10個のスレッドで並行実行
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_position, args=(f"STOCK_{i}",))
            threads.append(thread)
            thread.start()

        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()

        # エラーがないことを確認
        assert len(errors) == 0
        assert len(results) == 10

        # 全ての結果が有効であることを確認
        for result in results:
            assert "symbol" in result
            assert result["status"] == "ACTIVE"
