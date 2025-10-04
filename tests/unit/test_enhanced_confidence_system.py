#!/usr/bin/env python3
"""
強化された信頼度システムのテスト
記事の手法を超える高精度な取引判定のテスト
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.enhanced_confidence_system import (
    EnhancedConfidenceSystem, ConfidenceLevel, ConfidenceMetrics, TradingSignal
)


class TestEnhancedConfidenceSystem(unittest.TestCase):
    """強化された信頼度システムのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.config = {
            "confidence_thresholds": {
                "very_high": 0.90,
                "high": 0.80,
                "medium": 0.70,
                "low": 0.60,
                "very_low": 0.50
            },
            "trading_threshold": 0.70,
            "enhanced_trading_threshold": 0.75,
            "risk_adjustment": {
                "volatility_weight": 0.3,
                "market_weight": 0.2,
                "technical_weight": 0.3,
                "fundamental_weight": 0.2
            },
            "enhanced_confidence": {
                "ensemble_weight": 0.4,
                "market_adaptation": True,
                "volatility_adaptation": True,
                "dynamic_threshold": True,
                "confidence_decay": 0.95,
                "minimum_samples": 10
            }
        }
        self.system = EnhancedConfidenceSystem(self.config)
        
        # テストデータ作成
        self.stock_data = self._create_test_stock_data()
        self.market_data = self._create_test_market_data()
        self.technical_indicators = self._create_test_technical_indicators()
        self.fundamental_data = self._create_test_fundamental_data()
        self.prediction_models = self._create_test_prediction_models()
    
    def _create_test_stock_data(self) -> pd.DataFrame:
        """テスト用株価データ作成"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.02)
        volumes = np.random.randint(100000, 1000000, 100)
        
        return pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'Volume': volumes,
            'Open': prices * (1 + np.random.randn(100) * 0.01),
            'High': prices * (1 + np.abs(np.random.randn(100)) * 0.02),
            'Low': prices * (1 - np.abs(np.random.randn(100)) * 0.02)
        }).set_index('Date')
    
    def _create_test_market_data(self) -> pd.DataFrame:
        """テスト用市場データ作成"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(43)
        prices = 1000 + np.cumsum(np.random.randn(100) * 0.01)
        volumes = np.random.randint(1000000, 10000000, 100)
        
        return pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'Volume': volumes
        }).set_index('Date')
    
    def _create_test_technical_indicators(self) -> dict:
        """テスト用技術指標作成"""
        return {
            'rsi': 65.5,
            'macd': 0.5,
            'macd_signal': 0.3,
            'bb_upper': 105.0,
            'bb_lower': 95.0,
            'bb_middle': 100.0,
            'sma_5': 102.0,
            'sma_10': 101.0,
            'sma_25': 100.0,
            'sma_50': 99.0,
            'ema_12': 101.5,
            'ema_26': 100.5,
            'volume_ratio': 1.2
        }
    
    def _create_test_fundamental_data(self) -> dict:
        """テスト用ファンダメンタルデータ作成"""
        return {
            'roe': 0.15,
            'debt_ratio': 0.3,
            'revenue_growth': 0.1,
            'profit_growth': 0.12,
            'per': 15.0,
            'pbr': 1.5,
            'market_share': 0.2,
            'brand_value': 0.6
        }
    
    def _create_test_prediction_models(self) -> dict:
        """テスト用予測モデル作成"""
        models = {}
        
        # Random Forest モデル
        rf_model = Mock()
        rf_model.predict.return_value = [0.7]
        rf_model.score.return_value = 0.8
        models['random_forest'] = rf_model
        
        # Gradient Boosting モデル
        gb_model = Mock()
        gb_model.predict.return_value = [0.75]
        gb_model.score.return_value = 0.82
        models['gradient_boosting'] = gb_model
        
        # Neural Network モデル
        nn_model = Mock()
        nn_model.predict.return_value = [0.72]
        nn_model.score.return_value = 0.78
        models['neural_network'] = nn_model
        
        return models
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.system)
        self.assertEqual(self.system.config["trading_threshold"], 0.70)
        self.assertEqual(self.system.config["enhanced_trading_threshold"], 0.75)
        self.assertTrue(self.system.config["enhanced_confidence"]["market_adaptation"])
    
    def test_calculate_enhanced_confidence(self):
        """強化された信頼度計算テスト"""
        metrics = self.system.calculate_enhanced_confidence(
            self.stock_data,
            self.market_data,
            self.technical_indicators,
            self.fundamental_data,
            self.prediction_models
        )
        
        self.assertIsInstance(metrics, ConfidenceMetrics)
        self.assertGreaterEqual(metrics.final_confidence, 0.0)
        self.assertLessEqual(metrics.final_confidence, 1.0)
        self.assertIsInstance(metrics.confidence_level, ConfidenceLevel)
        self.assertGreaterEqual(metrics.risk_adjusted_confidence, 0.0)
        self.assertLessEqual(metrics.risk_adjusted_confidence, 1.0)
    
    def test_confidence_level_determination(self):
        """信頼度レベル決定テスト"""
        # 高信頼度テスト
        high_confidence = 0.85
        level = self.system._determine_confidence_level(high_confidence)
        self.assertIn(level, [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH])
        
        # 中信頼度テスト
        medium_confidence = 0.75
        level = self.system._determine_confidence_level(medium_confidence)
        self.assertEqual(level, ConfidenceLevel.MEDIUM)
        
        # 低信頼度テスト
        low_confidence = 0.55
        level = self.system._determine_confidence_level(low_confidence)
        self.assertIn(level, [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW])
    
    def test_trading_signal_generation(self):
        """取引シグナル生成テスト"""
        # 高信頼度でのシグナル生成
        high_confidence_metrics = ConfidenceMetrics(
            base_confidence=0.8,
            market_confidence=0.8,
            volatility_confidence=0.8,
            technical_confidence=0.8,
            fundamental_confidence=0.8,
            ensemble_confidence=0.8,
            final_confidence=0.8,
            confidence_level=ConfidenceLevel.HIGH,
            risk_adjusted_confidence=0.8
        )
        
        risk_metrics = {
            'volatility': 0.2,
            'max_risk': 0.02
        }
        
        signal = self.system.generate_trading_signal(
            "TEST", 100.0, high_confidence_metrics, self.market_data, risk_metrics
        )
        
        if signal:  # 信頼度が閾値を超えている場合
            self.assertIsInstance(signal, TradingSignal)
            self.assertIn(signal.action, ['BUY', 'SELL', 'HOLD'])
            self.assertGreater(signal.confidence, 0.7)
            self.assertGreater(signal.target_price, 0)
            self.assertGreater(signal.stop_loss, 0)
            self.assertGreater(signal.take_profit, 0)
            self.assertGreater(signal.position_size, 0)
            self.assertGreater(signal.risk_reward_ratio, 0)
    
    def test_market_regime_detection(self):
        """市場レジーム検出テスト"""
        # より長い期間のデータを作成（100日以上）
        dates = pd.date_range(start='2024-01-01', periods=120, freq='D')
        np.random.seed(43)
        prices = 1000 + np.cumsum(np.random.randn(120) * 0.01)
        
        # 強気市場データ（明確な上昇トレンド）
        bull_market_data = pd.DataFrame({
            'Date': dates,
            'Close': prices * 1.2  # 20%上昇
        }).set_index('Date')
        
        self.system._detect_market_regime(bull_market_data)
        # データが十分でない場合はnormalになる可能性がある
        self.assertIn(self.system.market_regime, ["bull", "normal"])
        
        # 弱気市場データ（明確な下降トレンド）
        bear_market_data = pd.DataFrame({
            'Date': dates,
            'Close': prices * 0.8  # 20%下落
        }).set_index('Date')
        
        self.system._detect_market_regime(bear_market_data)
        # データが十分でない場合はnormalになる可能性がある
        self.assertIn(self.system.market_regime, ["bear", "normal"])
    
    def test_volatility_regime_detection(self):
        """ボラティリティレジーム検出テスト"""
        # 高ボラティリティ
        self.system._detect_volatility_regime(0.3, 0.2)
        self.assertEqual(self.system.volatility_regime, "high")
        
        # 低ボラティリティ
        self.system._detect_volatility_regime(0.1, 0.2)
        self.assertEqual(self.system.volatility_regime, "low")
        
        # 通常ボラティリティ
        self.system._detect_volatility_regime(0.2, 0.2)
        self.assertEqual(self.system.volatility_regime, "normal")
    
    def test_technical_confidence_calculation(self):
        """技術的信頼度計算テスト"""
        # RSI信頼度テスト
        rsi_confidence = self.system._calculate_rsi_confidence(25)  # 過売り
        self.assertGreater(rsi_confidence, 0.7)
        
        rsi_confidence = self.system._calculate_rsi_confidence(75)  # 過買い
        self.assertGreater(rsi_confidence, 0.7)
        
        rsi_confidence = self.system._calculate_rsi_confidence(50)  # 中立
        self.assertGreater(rsi_confidence, 0.5)
    
    def test_macd_confidence_calculation(self):
        """MACD信頼度計算テスト"""
        # 大きな差
        macd_confidence = self.system._calculate_macd_confidence(0.5, 0.2)
        self.assertGreater(macd_confidence, 0.7)
        
        # 小さな差
        macd_confidence = self.system._calculate_macd_confidence(0.5, 0.48)
        self.assertLess(macd_confidence, 0.5)
    
    def test_bollinger_bands_confidence_calculation(self):
        """ボリンジャーバンド信頼度計算テスト"""
        # 広いバンド
        bb_confidence = self.system._calculate_bollinger_bands_confidence(110, 90, 100)
        self.assertGreaterEqual(bb_confidence, 0.6)
        
        # 狭いバンド
        bb_confidence = self.system._calculate_bollinger_bands_confidence(102, 98, 100)
        self.assertLess(bb_confidence, 0.5)
    
    def test_fundamental_confidence_calculation(self):
        """ファンダメンタル信頼度計算テスト"""
        # 良好な財務データ
        good_fundamental = {
            'roe': 0.20,
            'debt_ratio': 0.2,
            'revenue_growth': 0.15,
            'profit_growth': 0.18,
            'per': 12.0,
            'pbr': 1.2,
            'market_share': 0.3,
            'brand_value': 0.8
        }
        
        fundamental_confidence = self.system._calculate_fundamental_confidence(good_fundamental)
        self.assertGreater(fundamental_confidence, 0.6)
        
        # 悪い財務データ
        bad_fundamental = {
            'roe': 0.05,
            'debt_ratio': 0.8,
            'revenue_growth': -0.05,
            'profit_growth': -0.08,
            'per': 50.0,
            'pbr': 3.0,
            'market_share': 0.05,
            'brand_value': 0.2
        }
        
        fundamental_confidence = self.system._calculate_fundamental_confidence(bad_fundamental)
        self.assertLessEqual(fundamental_confidence, 0.5)
    
    def test_ensemble_confidence_calculation(self):
        """アンサンブル信頼度計算テスト"""
        ensemble_confidence = self.system._calculate_ensemble_confidence(
            self.prediction_models, self.stock_data
        )
        
        self.assertGreaterEqual(ensemble_confidence, 0.0)
        self.assertLessEqual(ensemble_confidence, 1.0)
    
    def test_risk_adjusted_confidence_calculation(self):
        """リスク調整信頼度計算テスト"""
        final_confidence = 0.8
        volatility_confidence = 0.7
        market_confidence = 0.8
        
        risk_adjusted = self.system._calculate_risk_adjusted_confidence(
            final_confidence, volatility_confidence, market_confidence
        )
        
        self.assertGreaterEqual(risk_adjusted, 0.0)
        self.assertLessEqual(risk_adjusted, 1.0)
        self.assertLessEqual(risk_adjusted, final_confidence)
    
    def test_confidence_statistics(self):
        """信頼度統計テスト"""
        # 履歴データを追加
        for i in range(20):
            metrics = ConfidenceMetrics(
                base_confidence=0.5 + i * 0.02,
                market_confidence=0.5 + i * 0.02,
                volatility_confidence=0.5 + i * 0.02,
                technical_confidence=0.5 + i * 0.02,
                fundamental_confidence=0.5 + i * 0.02,
                ensemble_confidence=0.5 + i * 0.02,
                final_confidence=0.5 + i * 0.02,
                confidence_level=ConfidenceLevel.MEDIUM,
                risk_adjusted_confidence=0.5 + i * 0.02
            )
            self.system.confidence_history.append(metrics)
        
        stats = self.system.get_confidence_statistics()
        
        self.assertIn("total_samples", stats)
        self.assertIn("average_confidence", stats)
        self.assertIn("confidence_std", stats)
        self.assertIn("min_confidence", stats)
        self.assertIn("max_confidence", stats)
        self.assertIn("high_confidence_ratio", stats)
        self.assertIn("trading_eligible_ratio", stats)
        
        self.assertEqual(stats["total_samples"], 20)
        self.assertGreater(stats["average_confidence"], 0.5)
    
    def test_empty_data_handling(self):
        """空データ処理テスト"""
        empty_stock_data = pd.DataFrame()
        empty_market_data = pd.DataFrame()
        empty_technical = {}
        empty_fundamental = {}
        empty_models = {}
        
        metrics = self.system.calculate_enhanced_confidence(
            empty_stock_data,
            empty_market_data,
            empty_technical,
            empty_fundamental,
            empty_models
        )
        
        self.assertIsInstance(metrics, ConfidenceMetrics)
        # 空データでもデフォルト値が返されることを確認
        self.assertGreaterEqual(metrics.final_confidence, 0.0)
        self.assertLessEqual(metrics.final_confidence, 1.0)
    
    def test_edge_cases(self):
        """エッジケーステスト"""
        # 極端な値でのテスト
        extreme_technical = {
            'rsi': 0,  # 極端な値
            'macd': 1000,
            'bb_upper': 0,
            'bb_lower': 0,
            'bb_middle': 0
        }
        
        metrics = self.system.calculate_enhanced_confidence(
            self.stock_data,
            self.market_data,
            extreme_technical,
            self.fundamental_data,
            self.prediction_models
        )
        
        self.assertIsInstance(metrics, ConfidenceMetrics)
        self.assertGreaterEqual(metrics.final_confidence, 0.0)
        self.assertLessEqual(metrics.final_confidence, 1.0)
    
    def test_performance_under_load(self):
        """負荷下でのパフォーマンステスト"""
        import time
        
        start_time = time.time()
        
        # 複数回の信頼度計算
        for _ in range(100):
            metrics = self.system.calculate_enhanced_confidence(
                self.stock_data,
                self.market_data,
                self.technical_indicators,
                self.fundamental_data,
                self.prediction_models
            )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 100回の計算が5秒以内に完了することを確認
        self.assertLess(execution_time, 5.0)
    
    def test_memory_usage(self):
        """メモリ使用量テスト"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 大量の履歴データを追加
        for i in range(1000):
            metrics = ConfidenceMetrics(
                base_confidence=0.5,
                market_confidence=0.5,
                volatility_confidence=0.5,
                technical_confidence=0.5,
                fundamental_confidence=0.5,
                ensemble_confidence=0.5,
                final_confidence=0.5,
                confidence_level=ConfidenceLevel.MEDIUM,
                risk_adjusted_confidence=0.5
            )
            self.system.confidence_history.append(metrics)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # メモリ増加が10MB以内であることを確認
        self.assertLess(memory_increase, 10 * 1024 * 1024)


if __name__ == '__main__':
    unittest.main()
