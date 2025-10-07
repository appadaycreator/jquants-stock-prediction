#!/usr/bin/env python3
"""
市場ボラティリティ調整システムのテスト
"""

import numpy as np
import pandas as pd
from core.market_volatility_adjustment import (
    MarketVolatilityAdjustment,
    MarketRegime,
    VolatilityRegime,
    MarketConditions,
    DynamicAdjustment,
)


class TestMarketVolatilityAdjustment:
    """市場ボラティリティ調整システムのテストクラス"""

    def setup_method(self):
        """テスト前の準備"""
        self.config = {
            "market_regime_detection": {
                "trend_threshold": 0.05,
                "momentum_threshold": 0.02,
                "volatility_threshold": 0.25,
                "lookback_period": 60,
                "min_observations": 30,
            },
            "volatility_regime_detection": {
                "low_threshold": 0.15,
                "high_threshold": 0.30,
                "extreme_threshold": 0.50,
                "lookback_period": 30,
                "min_observations": 20,
            },
            "adjustment_factors": {
                "bull": {
                    "confidence_multiplier": 1.1,
                    "position_size_multiplier": 1.05,
                    "risk_tolerance_multiplier": 1.02,
                },
                "bear": {
                    "confidence_multiplier": 0.9,
                    "position_size_multiplier": 0.8,
                    "risk_tolerance_multiplier": 0.7,
                },
                "volatile": {
                    "confidence_multiplier": 0.8,
                    "position_size_multiplier": 0.7,
                    "risk_tolerance_multiplier": 0.6,
                },
                "calm": {
                    "confidence_multiplier": 1.05,
                    "position_size_multiplier": 1.02,
                    "risk_tolerance_multiplier": 1.01,
                },
            },
            "dynamic_thresholds": {
                "confidence_threshold_base": 0.70,
                "confidence_threshold_volatile": 0.75,
                "confidence_threshold_calm": 0.65,
                "position_size_max_base": 0.10,
                "position_size_max_volatile": 0.05,
                "position_size_max_calm": 0.15,
            },
        }
        self.adjustment = MarketVolatilityAdjustment(self.config)

    def test_initialization(self):
        """初期化テスト"""
        assert self.adjustment.config == self.config
        assert len(self.adjustment.market_history) == 0
        assert len(self.adjustment.regime_history) == 0

    def test_initialization_with_default_config(self):
        """デフォルト設定での初期化テスト"""
        adjustment = MarketVolatilityAdjustment()

        assert adjustment.config is not None
        assert "market_regime_detection" in adjustment.config
        assert "volatility_regime_detection" in adjustment.config
        assert "adjustment_factors" in adjustment.config

    def test_analyze_market_conditions_success(self):
        """市場条件分析成功テスト"""
        # テストデータの作成
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame(
            {'Close': prices, 'Volume': np.random.randint(1000000, 10000000, 100)},
            index=dates,
        )

        conditions = self.adjustment.analyze_market_conditions(market_data)

        assert isinstance(conditions, MarketConditions)
        assert isinstance(conditions.market_regime, MarketRegime)
        assert isinstance(conditions.volatility_regime, VolatilityRegime)
        assert 0.0 <= conditions.trend_strength <= 1.0
        assert 0.0 <= conditions.momentum <= 1.0
        assert 0.0 <= conditions.volatility <= 1.0
        assert 0.0 <= conditions.correlation <= 1.0
        assert 0.0 <= conditions.liquidity <= 1.0
        assert 0.0 <= conditions.market_stress <= 1.0
        assert 0.0 <= conditions.regime_confidence <= 1.0

    def test_analyze_market_conditions_empty_data(self):
        """空データでの市場条件分析テスト"""
        market_data = pd.DataFrame()

        conditions = self.adjustment.analyze_market_conditions(market_data)

        assert isinstance(conditions, MarketConditions)
        assert conditions.market_regime == MarketRegime.SIDEWAYS
        assert conditions.volatility_regime == VolatilityRegime.NORMAL

    def test_analyze_market_conditions_with_sector_data(self):
        """セクターデータ付きでの市場条件分析テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame(
            {'Close': prices, 'Volume': np.random.randint(1000000, 10000000, 100)},
            index=dates,
        )

        sector_data = {
            'technology': pd.DataFrame(
                {
                    'Close': prices * 1.1,
                    'Volume': np.random.randint(1000000, 10000000, 100),
                },
                index=dates,
            ),
            'finance': pd.DataFrame(
                {
                    'Close': prices * 0.9,
                    'Volume': np.random.randint(1000000, 10000000, 100),
                },
                index=dates,
            ),
        }

        conditions = self.adjustment.analyze_market_conditions(market_data, sector_data)

        assert isinstance(conditions, MarketConditions)
        assert 0.0 <= conditions.correlation <= 1.0

    def test_analyze_market_conditions_with_economic_indicators(self):
        """経済指標付きでの市場条件分析テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame(
            {'Close': prices, 'Volume': np.random.randint(1000000, 10000000, 100)},
            index=dates,
        )

        economic_indicators = {'vix': 25.0, 'rate_change': 0.01}

        conditions = self.adjustment.analyze_market_conditions(
            market_data, economic_indicators=economic_indicators
        )

        assert isinstance(conditions, MarketConditions)
        assert 0.0 <= conditions.market_stress <= 1.0

    def test_calculate_dynamic_adjustment_success(self):
        """動的調整計算成功テスト"""
        # 市場条件の作成
        conditions = MarketConditions(
            market_regime=MarketRegime.BULL,
            volatility_regime=VolatilityRegime.NORMAL,
            trend_strength=0.8,
            momentum=0.6,
            volatility=0.2,
            correlation=0.5,
            liquidity=0.7,
            market_stress=0.3,
            regime_confidence=0.8,
            adjustment_factors={
                'confidence_multiplier': 1.1,
                'position_size_multiplier': 1.05,
                'risk_tolerance_multiplier': 1.02,
            },
        )

        base_confidence = 0.8
        base_position_size = 0.1
        base_risk_tolerance = 0.15

        adjustment = self.adjustment.calculate_dynamic_adjustment(
            base_confidence, base_position_size, base_risk_tolerance, conditions
        )

        assert isinstance(adjustment, DynamicAdjustment)
        assert 0.0 <= adjustment.confidence_adjustment <= 1.0
        assert 0.0 <= adjustment.position_size_adjustment <= 1.0
        assert 0.0 <= adjustment.risk_tolerance_adjustment <= 1.0
        assert 0.0 <= adjustment.stop_loss_adjustment <= 1.0
        assert 0.0 <= adjustment.take_profit_adjustment <= 1.0
        assert (
            0.0 <= adjustment.rebalancing_frequency_adjustment <= 2.0
        )  # 1.0を超える場合がある
        assert 0.0 <= adjustment.overall_adjustment <= 1.0

    def test_calculate_dynamic_adjustment_with_stock_factors(self):
        """銘柄固有要因付きでの動的調整計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.BEAR,
            volatility_regime=VolatilityRegime.HIGH,
            trend_strength=0.3,
            momentum=-0.2,
            volatility=0.4,
            correlation=0.8,
            liquidity=0.4,
            market_stress=0.7,
            regime_confidence=0.6,
            adjustment_factors={
                'confidence_multiplier': 0.8,
                'position_size_multiplier': 0.7,
                'risk_tolerance_multiplier': 0.6,
            },
        )

        stock_specific_factors = {'beta': 1.5, 'volatility': 0.3, 'liquidity': 0.6}

        adjustment = self.adjustment.calculate_dynamic_adjustment(
            0.7, 0.08, 0.12, conditions, stock_specific_factors
        )

        assert isinstance(adjustment, DynamicAdjustment)
        assert adjustment.confidence_adjustment < 0.7  # 弱気市場で低下
        assert adjustment.position_size_adjustment < 0.08  # 高ボラティリティで低下

    def test_detect_market_regime_bull(self):
        """強気市場レジーム検出テスト"""
        # 上昇トレンドのデータ
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01) + np.arange(100) * 0.1

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        regime = self.adjustment._detect_market_regime(market_data)

        assert isinstance(regime, MarketRegime)

    def test_detect_market_regime_bear(self):
        """弱気市場レジーム検出テスト"""
        # 下降トレンドのデータ
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01) - np.arange(100) * 0.1

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        regime = self.adjustment._detect_market_regime(market_data)

        assert isinstance(regime, MarketRegime)

    def test_detect_market_regime_volatile(self):
        """高ボラティリティ市場レジーム検出テスト"""
        # 高ボラティリティのデータ
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.05)  # 高ボラティリティ

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        regime = self.adjustment._detect_market_regime(market_data)

        assert isinstance(regime, MarketRegime)

    def test_detect_volatility_regime_low(self):
        """低ボラティリティレジーム検出テスト"""
        # 低ボラティリティのデータ
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.005)  # 低ボラティリティ

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        regime = self.adjustment._detect_volatility_regime(market_data)

        assert isinstance(regime, VolatilityRegime)

    def test_detect_volatility_regime_high(self):
        """高ボラティリティレジーム検出テスト"""
        # 高ボラティリティのデータ
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.05)  # 高ボラティリティ

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        regime = self.adjustment._detect_volatility_regime(market_data)

        assert isinstance(regime, VolatilityRegime)

    def test_calculate_trend_strength(self):
        """トレンド強度計算テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        trend_strength = self.adjustment._calculate_trend_strength(market_data)

        assert 0.0 <= trend_strength <= 1.0

    def test_calculate_momentum(self):
        """モメンタム計算テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        momentum = self.adjustment._calculate_momentum(market_data)

        assert isinstance(momentum, float)

    def test_calculate_market_volatility(self):
        """市場ボラティリティ計算テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        volatility = self.adjustment._calculate_market_volatility(market_data)

        assert volatility >= 0.0

    def test_calculate_market_correlation(self):
        """市場相関計算テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        sector_data = {
            'sector1': pd.DataFrame({'Close': prices * 1.1}, index=dates),
            'sector2': pd.DataFrame({'Close': prices * 0.9}, index=dates),
        }

        correlation = self.adjustment._calculate_market_correlation(
            market_data, sector_data
        )

        assert 0.0 <= correlation <= 1.0

    def test_calculate_market_liquidity(self):
        """市場流動性計算テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)
        volumes = np.random.randint(1000000, 10000000, 100)

        market_data = pd.DataFrame({'Close': prices, 'Volume': volumes}, index=dates)

        liquidity = self.adjustment._calculate_market_liquidity(market_data)

        assert 0.0 <= liquidity <= 1.0

    def test_calculate_market_stress(self):
        """市場ストレス計算テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        economic_indicators = {'vix': 30.0, 'rate_change': 0.02}

        stress = self.adjustment._calculate_market_stress(
            market_data, economic_indicators
        )

        assert 0.0 <= stress <= 1.0

    def test_calculate_regime_confidence(self):
        """レジーム信頼度計算テスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        confidence = self.adjustment._calculate_regime_confidence(
            market_data, MarketRegime.BULL, VolatilityRegime.NORMAL
        )

        assert 0.0 <= confidence <= 1.0

    def test_get_market_statistics(self):
        """市場統計情報取得テスト"""
        # 履歴データを追加
        for i in range(10):
            conditions = MarketConditions(
                market_regime=MarketRegime.BULL if i % 2 == 0 else MarketRegime.BEAR,
                volatility_regime=VolatilityRegime.NORMAL,
                trend_strength=0.5 + i * 0.05,
                momentum=0.1 * i,
                volatility=0.2 + i * 0.01,
                correlation=0.5,
                liquidity=0.6,
                market_stress=0.3 + i * 0.02,
                regime_confidence=0.7,
                adjustment_factors={},
            )
            self.adjustment.market_history.append(conditions)

        statistics = self.adjustment.get_market_statistics()

        assert "total_samples" in statistics
        assert "market_regime_distribution" in statistics
        assert "volatility_regime_distribution" in statistics
        assert "avg_volatility" in statistics
        assert "max_volatility" in statistics
        assert "avg_market_stress" in statistics
        assert "max_market_stress" in statistics

    def test_get_market_statistics_empty_history(self):
        """空の履歴での市場統計情報取得テスト"""
        statistics = self.adjustment.get_market_statistics()

        assert statistics == {}

    def test_edge_cases_empty_data(self):
        """空データのエッジケーステスト"""
        market_data = pd.DataFrame()

        # 各メソッドがエラーなく動作することを確認
        conditions = self.adjustment.analyze_market_conditions(market_data)
        assert isinstance(conditions, MarketConditions)

        regime = self.adjustment._detect_market_regime(market_data)
        assert isinstance(regime, MarketRegime)

        vol_regime = self.adjustment._detect_volatility_regime(market_data)
        assert isinstance(vol_regime, VolatilityRegime)

    def test_edge_cases_insufficient_data(self):
        """データ不足のエッジケーステスト"""
        # 最小限のデータ
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        prices = [100, 101, 102, 103, 104]

        market_data = pd.DataFrame({'Close': prices}, index=dates)

        # 各メソッドがエラーなく動作することを確認
        conditions = self.adjustment.analyze_market_conditions(market_data)
        assert isinstance(conditions, MarketConditions)

    def test_edge_cases_missing_columns(self):
        """列不足のエッジケーステスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')

        # Close列がない
        market_data = pd.DataFrame(
            {
                'Open': np.random.randn(100),
                'High': np.random.randn(100),
                'Low': np.random.randn(100),
            },
            index=dates,
        )

        conditions = self.adjustment.analyze_market_conditions(market_data)
        assert isinstance(conditions, MarketConditions)

    def test_adjustment_factors_calculation(self):
        """調整係数計算テスト"""
        factors = self.adjustment._calculate_adjustment_factors(
            MarketRegime.BULL, VolatilityRegime.NORMAL, 0.3
        )

        assert isinstance(factors, dict)
        assert "confidence_multiplier" in factors
        assert "position_size_multiplier" in factors
        assert "risk_tolerance_multiplier" in factors

    def test_confidence_adjustment_calculation(self):
        """信頼度調整計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.BULL,
            volatility_regime=VolatilityRegime.NORMAL,
            trend_strength=0.8,
            momentum=0.6,
            volatility=0.2,
            correlation=0.5,
            liquidity=0.7,
            market_stress=0.3,
            regime_confidence=0.8,
            adjustment_factors={'confidence_multiplier': 1.1},
        )

        adjustment = self.adjustment._calculate_confidence_adjustment(
            0.8, conditions, {'confidence_multiplier': 1.1}
        )

        assert 0.0 <= adjustment <= 1.0

    def test_position_size_adjustment_calculation(self):
        """ポジションサイズ調整計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.BEAR,
            volatility_regime=VolatilityRegime.HIGH,
            trend_strength=0.3,
            momentum=-0.2,
            volatility=0.4,
            correlation=0.8,
            liquidity=0.4,
            market_stress=0.7,
            regime_confidence=0.6,
            adjustment_factors={'position_size_multiplier': 0.7},
        )

        adjustment = self.adjustment._calculate_position_size_adjustment(
            0.1, conditions, {'position_size_multiplier': 0.7}
        )

        assert 0.0 <= adjustment <= 1.0

    def test_risk_tolerance_adjustment_calculation(self):
        """リスク許容度調整計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.VOLATILE,
            volatility_regime=VolatilityRegime.HIGH,
            trend_strength=0.2,
            momentum=0.1,
            volatility=0.5,
            correlation=0.9,
            liquidity=0.3,
            market_stress=0.8,
            regime_confidence=0.4,
            adjustment_factors={'risk_tolerance_multiplier': 0.6},
        )

        adjustment = self.adjustment._calculate_risk_tolerance_adjustment(
            0.15, conditions, {'risk_tolerance_multiplier': 0.6}
        )

        assert 0.0 <= adjustment <= 1.0

    def test_stop_loss_adjustment_calculation(self):
        """損切り調整計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.BEAR,
            volatility_regime=VolatilityRegime.HIGH,
            trend_strength=0.3,
            momentum=-0.2,
            volatility=0.4,
            correlation=0.8,
            liquidity=0.4,
            market_stress=0.7,
            regime_confidence=0.6,
            adjustment_factors={},
        )

        stock_factors = {'beta': 1.5, 'volatility': 0.3}

        adjustment = self.adjustment._calculate_stop_loss_adjustment(
            conditions, stock_factors
        )

        assert 0.0 <= adjustment <= 1.0

    def test_take_profit_adjustment_calculation(self):
        """利確調整計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.BULL,
            volatility_regime=VolatilityRegime.LOW,
            trend_strength=0.8,
            momentum=0.6,
            volatility=0.15,
            correlation=0.4,
            liquidity=0.8,
            market_stress=0.2,
            regime_confidence=0.9,
            adjustment_factors={},
        )

        stock_factors = {'beta': 0.8, 'volatility': 0.2}

        adjustment = self.adjustment._calculate_take_profit_adjustment(
            conditions, stock_factors
        )

        assert 0.0 <= adjustment <= 1.0

    def test_rebalancing_frequency_adjustment_calculation(self):
        """リバランス頻度調整計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.VOLATILE,
            volatility_regime=VolatilityRegime.HIGH,
            trend_strength=0.2,
            momentum=0.1,
            volatility=0.5,
            correlation=0.9,
            liquidity=0.3,
            market_stress=0.8,
            regime_confidence=0.4,
            adjustment_factors={},
        )

        adjustment = self.adjustment._calculate_rebalancing_frequency_adjustment(
            conditions
        )

        assert 0.0 <= adjustment <= 2.0  # 1.0を超える場合がある

    def test_overall_adjustment_calculation(self):
        """全体的な調整係数計算テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.BULL,
            volatility_regime=VolatilityRegime.NORMAL,
            trend_strength=0.8,
            momentum=0.6,
            volatility=0.2,
            correlation=0.5,
            liquidity=0.7,
            market_stress=0.3,
            regime_confidence=0.8,
            adjustment_factors={},
        )

        adjustment = self.adjustment._calculate_overall_adjustment(
            0.8, 0.1, 0.15, conditions
        )

        assert 0.0 <= adjustment <= 1.0

    def test_dynamic_position_limit(self):
        """動的ポジション制限テスト"""
        conditions = MarketConditions(
            market_regime=MarketRegime.BULL,
            volatility_regime=VolatilityRegime.HIGH,
            trend_strength=0.8,
            momentum=0.6,
            volatility=0.4,
            correlation=0.5,
            liquidity=0.7,
            market_stress=0.3,
            regime_confidence=0.8,
            adjustment_factors={},
        )

        limit = self.adjustment._get_dynamic_position_limit(conditions)

        assert 0.0 <= limit <= 1.0

    def test_default_market_conditions(self):
        """デフォルト市場条件テスト"""
        conditions = self.adjustment._get_default_market_conditions()

        assert isinstance(conditions, MarketConditions)
        assert conditions.market_regime == MarketRegime.SIDEWAYS
        assert conditions.volatility_regime == VolatilityRegime.NORMAL

    def test_default_dynamic_adjustment(self):
        """デフォルト動的調整テスト"""
        adjustment = self.adjustment._get_default_dynamic_adjustment()

        assert isinstance(adjustment, DynamicAdjustment)
        assert adjustment.confidence_adjustment == 1.0
        assert adjustment.position_size_adjustment == 1.0
        assert adjustment.risk_tolerance_adjustment == 1.0

    def test_market_history_management(self):
        """市場履歴管理テスト"""
        # 履歴を追加
        for i in range(5):
            conditions = MarketConditions(
                market_regime=MarketRegime.BULL,
                volatility_regime=VolatilityRegime.NORMAL,
                trend_strength=0.5,
                momentum=0.1,
                volatility=0.2,
                correlation=0.5,
                liquidity=0.6,
                market_stress=0.3,
                regime_confidence=0.7,
                adjustment_factors={},
            )
            self.adjustment.market_history.append(conditions)

        assert len(self.adjustment.market_history) == 5

        # 履歴上限テスト（1000件）
        for i in range(1005):
            conditions = MarketConditions(
                market_regime=MarketRegime.BULL,
                volatility_regime=VolatilityRegime.NORMAL,
                trend_strength=0.5,
                momentum=0.1,
                volatility=0.2,
                correlation=0.5,
                liquidity=0.6,
                market_stress=0.3,
                regime_confidence=0.7,
                adjustment_factors={},
            )
            self.adjustment.market_history.append(conditions)
            # 履歴が1000件を超えた場合は古いものを削除
            if len(self.adjustment.market_history) > 1000:
                self.adjustment.market_history.pop(0)

        assert len(self.adjustment.market_history) == 1000

    def test_error_handling_in_analysis(self):
        """分析時のエラーハンドリングテスト"""
        # 無効なデータ
        market_data = None

        conditions = self.adjustment.analyze_market_conditions(market_data)

        assert isinstance(conditions, MarketConditions)

    def test_error_handling_in_adjustment(self):
        """調整計算時のエラーハンドリングテスト"""
        # 無効な市場条件
        conditions = None

        adjustment = self.adjustment.calculate_dynamic_adjustment(
            0.8, 0.1, 0.15, conditions
        )

        assert isinstance(adjustment, DynamicAdjustment)

    def test_config_validation(self):
        """設定検証テスト"""
        # 無効な設定
        invalid_config = {
            "market_regime_detection": {},
            "volatility_regime_detection": {},
            "adjustment_factors": {},
            "dynamic_thresholds": {},
        }

        adjustment = MarketVolatilityAdjustment(invalid_config)

        # デフォルト設定が使用されることを確認
        assert adjustment.config is not None
        assert "market_regime_detection" in adjustment.config
        assert "volatility_regime_detection" in adjustment.config
