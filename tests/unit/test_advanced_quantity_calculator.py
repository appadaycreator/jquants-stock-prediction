#!/usr/bin/env python3
"""
高度な数量計算システムのテスト
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch

from core.advanced_quantity_calculator import (
    AdvancedQuantityCalculator,
    QuantityCalculationResult,
)


class TestAdvancedQuantityCalculator:
    """高度な数量計算システムのテスト"""

    def setup_method(self):
        """テストのセットアップ"""
        self.config = {
            "total_capital": 1000000,  # 100万円
            "max_position_size": 0.1,  # 10%
            "min_position_size": 0.01,  # 1%
            "risk_per_trade": 0.02,  # 2%
            "commission_rate": 0.001,  # 0.1%
            "slippage_rate": 0.0005,  # 0.05%
            "max_daily_loss": 0.05,  # 5%
            "volatility_adjustment": True,
            "correlation_adjustment": True,
            "min_trade_unit": 100,  # 100株
            "min_trade_amount": 10000,  # 1万円
        }
        self.calculator = AdvancedQuantityCalculator(self.config)

    def test_initialization(self):
        """初期化のテスト"""
        assert self.calculator.total_capital == 1000000
        assert self.calculator.max_position_size == 0.1
        assert self.calculator.min_position_size == 0.01
        assert self.calculator.risk_per_trade == 0.02
        assert self.calculator.commission_rate == 0.001
        assert self.calculator.slippage_rate == 0.0005

    def test_calculate_optimal_quantity_basic(self):
        """基本的最適数量計算テスト"""
        symbol = "TEST"
        current_price = 100.0
        target_price = 110.0
        confidence = 0.8
        volatility = 0.2

        result = self.calculator.calculate_optimal_quantity(
            symbol, current_price, target_price, confidence, volatility
        )

        assert isinstance(result, QuantityCalculationResult)
        assert result.quantity >= 0
        assert result.total_amount >= 0
        assert result.unit_price == current_price
        assert result.commission >= 0
        assert result.slippage >= 0
        assert result.net_amount >= 0
        assert result.position_size_percentage >= 0
        assert result.risk_amount >= 0
        assert result.confidence_level in [
            "VERY_HIGH",
            "HIGH",
            "MEDIUM",
            "LOW",
            "VERY_LOW",
        ]

    def test_calculate_optimal_quantity_with_existing_position(self):
        """既存ポジションありの最適数量計算テスト"""
        symbol = "TEST"
        current_price = 100.0
        target_price = 110.0
        confidence = 0.8
        volatility = 0.2
        existing_position = {
            "symbol": "TEST",
            "position_size_percentage": 0.05,  # 5%
            "market_value": 50000,
        }

        result = self.calculator.calculate_optimal_quantity(
            symbol,
            current_price,
            target_price,
            confidence,
            volatility,
            existing_position,
        )

        assert isinstance(result, QuantityCalculationResult)
        assert result.quantity >= 0
        # 既存ポジションがある場合は数量が調整される
        assert (
            result.quantity
            <= (self.calculator.total_capital * self.calculator.max_position_size)
            / current_price
        )

    def test_calculate_optimal_quantity_with_portfolio(self):
        """ポートフォリオ考慮の最適数量計算テスト"""
        symbol = "TEST"
        current_price = 100.0
        target_price = 110.0
        confidence = 0.8
        volatility = 0.2
        portfolio_positions = [
            {"symbol": "TEST2", "market_value": 200000, "volatility": 0.3},
            {"symbol": "TEST3", "market_value": 150000, "volatility": 0.25},
        ]
        market_condition = "bull_market"

        result = self.calculator.calculate_optimal_quantity(
            symbol,
            current_price,
            target_price,
            confidence,
            volatility,
            None,
            portfolio_positions,
            market_condition,
        )

        assert isinstance(result, QuantityCalculationResult)
        assert result.quantity >= 0

    def test_calculate_base_quantity(self):
        """基本数量の計算テスト"""
        current_price = 100.0
        confidence = 0.8
        volatility = 0.2

        quantity = self.calculator._calculate_base_quantity(
            current_price, confidence, volatility
        )

        assert quantity >= 0
        assert isinstance(quantity, int)

    def test_apply_risk_adjustment(self):
        """リスク調整の適用テスト"""
        quantity = 1000
        current_price = 100.0
        volatility = 0.3
        confidence = 0.8

        adjusted_quantity = self.calculator._apply_risk_adjustment(
            quantity, current_price, volatility, confidence
        )

        assert adjusted_quantity >= 0
        assert adjusted_quantity <= quantity  # リスク調整で数量は減る

    def test_apply_volatility_adjustment(self):
        """ボラティリティ調整の適用テスト"""
        # 高ボラティリティ
        high_vol_quantity = self.calculator._apply_volatility_adjustment(1000, 0.4)
        # 低ボラティリティ
        low_vol_quantity = self.calculator._apply_volatility_adjustment(1000, 0.05)
        # 通常ボラティリティ
        normal_vol_quantity = self.calculator._apply_volatility_adjustment(1000, 0.2)

        assert high_vol_quantity <= 1000  # 高ボラティリティでは数量を減らす
        assert low_vol_quantity >= 1000  # 低ボラティリティでは数量を増やす
        assert normal_vol_quantity == 1000  # 通常は変更なし

    def test_apply_correlation_adjustment(self):
        """相関調整の適用テスト"""
        quantity = 1000
        symbol = "TEST1"
        portfolio_positions = [
            {"symbol": "TEST2", "market_value": 200000},
            {"symbol": "TEST3", "market_value": 150000},
        ]

        adjusted_quantity = self.calculator._apply_correlation_adjustment(
            quantity, symbol, portfolio_positions
        )

        assert adjusted_quantity >= 0
        assert adjusted_quantity <= quantity

    def test_apply_market_condition_adjustment(self):
        """市場条件調整の適用テスト"""
        quantity = 1000
        confidence = 0.8

        # 強気市場
        bull_quantity = self.calculator._apply_market_condition_adjustment(
            quantity, "bull_market", confidence
        )
        # 弱気市場
        bear_quantity = self.calculator._apply_market_condition_adjustment(
            quantity, "bear_market", confidence
        )
        # 高ボラティリティ
        high_vol_quantity = self.calculator._apply_market_condition_adjustment(
            quantity, "high_volatility", confidence
        )

        assert bull_quantity >= quantity  # 強気市場では数量を増やす
        assert bear_quantity <= quantity  # 弱気市場では数量を減らす
        assert high_vol_quantity <= quantity  # 高ボラティリティでは数量を減らす

    def test_apply_existing_position_adjustment(self):
        """既存ポジション調整の適用テスト"""
        quantity = 1000
        existing_position = {"position_size_percentage": 0.08}  # 8%

        adjusted_quantity = self.calculator._apply_existing_position_adjustment(
            quantity, existing_position
        )

        assert adjusted_quantity >= 0
        assert adjusted_quantity <= quantity

    def test_apply_quantity_limits(self):
        """数量制限の適用テスト"""
        current_price = 100.0

        # 正常な数量
        normal_quantity = self.calculator._apply_quantity_limits(1000, current_price)
        assert normal_quantity == 1000

        # 最小取引単位未満
        small_quantity = self.calculator._apply_quantity_limits(50, current_price)
        assert small_quantity == 0

        # 最大ポジションサイズ超過
        large_quantity = self.calculator._apply_quantity_limits(20000, current_price)
        max_allowed = int(
            (self.calculator.total_capital * self.calculator.max_position_size)
            / current_price
        )
        assert large_quantity <= max_allowed

    def test_calculate_risk_amount(self):
        """リスク金額の計算テスト"""
        quantity = 1000
        current_price = 100.0
        target_price = 110.0
        volatility = 0.2

        risk_amount = self.calculator._calculate_risk_amount(
            quantity, current_price, target_price, volatility
        )

        assert risk_amount >= 0
        assert isinstance(risk_amount, float)

    def test_calculate_expected_return(self):
        """期待リターンの計算テスト"""
        quantity = 1000
        current_price = 100.0
        target_price = 110.0
        confidence = 0.8

        expected_return = self.calculator._calculate_expected_return(
            quantity, current_price, target_price, confidence
        )

        assert expected_return >= 0  # 上昇予測なので正の値
        assert isinstance(expected_return, float)

    def test_calculate_max_loss(self):
        """最大損失の計算テスト"""
        quantity = 1000
        current_price = 100.0
        volatility = 0.2

        max_loss = self.calculator._calculate_max_loss(
            quantity, current_price, volatility
        )

        assert max_loss >= 0
        assert isinstance(max_loss, float)

    def test_determine_confidence_level(self):
        """信頼度レベルの判定テスト"""
        assert self.calculator._determine_confidence_level(0.95) == "VERY_HIGH"
        assert self.calculator._determine_confidence_level(0.85) == "HIGH"
        assert self.calculator._determine_confidence_level(0.75) == "MEDIUM"
        assert self.calculator._determine_confidence_level(0.65) == "LOW"
        assert self.calculator._determine_confidence_level(0.55) == "VERY_LOW"

    def test_calculate_sector_correlation(self):
        """セクター相関の計算テスト"""
        # 同じセクター
        correlation1 = self.calculator._calculate_sector_correlation("7203", "7203")
        assert correlation1 == 0.8

        # 異なるセクター
        correlation2 = self.calculator._calculate_sector_correlation("7203", "9984")
        assert correlation2 == 0.3

        # 関連セクター
        correlation3 = self.calculator._calculate_sector_correlation("6758", "6861")
        assert correlation3 == 0.8  # 両方ともtechnologyセクター

    def test_calculate_portfolio_risk(self):
        """ポートフォリオリスクの計算テスト"""
        positions = [
            {"market_value": 200000, "volatility": 0.2},
            {"market_value": 150000, "volatility": 0.25},
        ]

        risk_metrics = self.calculator.calculate_portfolio_risk(positions)

        assert "total_risk" in risk_metrics
        assert "portfolio_volatility" in risk_metrics
        assert "max_single_position_risk" in risk_metrics
        assert "risk_concentration" in risk_metrics

        assert risk_metrics["total_risk"] >= 0
        assert risk_metrics["portfolio_volatility"] >= 0
        assert risk_metrics["max_single_position_risk"] >= 0
        assert 0 <= risk_metrics["risk_concentration"] <= 1

    def test_calculate_portfolio_risk_empty(self):
        """空ポートフォリオのリスク計算テスト"""
        positions = []

        risk_metrics = self.calculator.calculate_portfolio_risk(positions)

        assert risk_metrics["total_risk"] == 0
        assert risk_metrics["portfolio_volatility"] == 0
        assert risk_metrics["max_single_position_risk"] == 0
        assert risk_metrics["risk_concentration"] == 0

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なパラメータでの計算
        result = self.calculator.calculate_optimal_quantity("", 0, 0, 0, 0)

        assert isinstance(result, QuantityCalculationResult)
        assert result.quantity == 0
        # エラー時はVERY_LOWが返される
        assert result.confidence_level == "VERY_LOW"

    def test_edge_cases(self):
        """エッジケースのテスト"""
        # 極端に高い価格
        result1 = self.calculator.calculate_optimal_quantity(
            "TEST", 1000000, 1100000, 0.8, 0.2
        )
        assert result1.quantity >= 0

        # 極端に低い価格
        result2 = self.calculator.calculate_optimal_quantity(
            "TEST", 0.01, 0.011, 0.8, 0.2
        )
        assert result2.quantity >= 0

        # 極端に高い信頼度
        result3 = self.calculator.calculate_optimal_quantity("TEST", 100, 110, 1.0, 0.2)
        assert result3.quantity >= 0

        # 極端に低い信頼度
        result4 = self.calculator.calculate_optimal_quantity("TEST", 100, 110, 0.0, 0.2)
        assert result4.quantity >= 0
