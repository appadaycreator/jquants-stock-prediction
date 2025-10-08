#!/usr/bin/env python3
"""
拡張信頼度システムの拡張テスト
カバレッジ向上のための追加テストケース
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import numpy as np

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_confidence_system import (
    EnhancedConfidenceSystem,
    ConfidenceLevel,
    ConfidenceMetrics,
    TradingSignal,
)


class TestEnhancedConfidenceSystemEnhanced(unittest.TestCase):
    """拡張信頼度システムの拡張テスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "confidence": {
                "min_threshold": 0.6,
                "high_threshold": 0.8,
                "update_interval": 1.0,
                "decay_factor": 0.95,
            },
            "prediction": {
                "lookback_period": 30,
                "min_observations": 10,
                "volatility_threshold": 0.2,
            },
            "validation": {
                "cross_validation_folds": 5,
                "bootstrap_samples": 100,
                "confidence_interval": 0.95,
            },
            "ensemble": {
                "min_models": 3,
                "max_models": 10,
                "weight_threshold": 0.1,
            },
        }
        self.confidence_system = EnhancedConfidenceSystem(self.config)

    def test_initialization_with_config(self):
        """設定付き初期化テスト"""
        self.assertEqual(self.confidence_system.min_threshold, 0.6)
        self.assertEqual(self.confidence_system.high_threshold, 0.8)
        self.assertEqual(self.confidence_system.update_interval, 1.0)
        self.assertEqual(self.confidence_system.decay_factor, 0.95)

    def test_initialization_without_config(self):
        """設定なし初期化テスト"""
        confidence_system = EnhancedConfidenceSystem()
        
        self.assertEqual(confidence_system.min_threshold, 0.6)
        self.assertEqual(confidence_system.high_threshold, 0.8)
        self.assertEqual(confidence_system.update_interval, 1.0)
        self.assertEqual(confidence_system.decay_factor, 0.95)

    def test_calculate_prediction_confidence_success(self):
        """予測信頼度計算成功テスト"""
        predictions = [0.1, 0.2, 0.15, 0.18, 0.12]
        actual_values = [0.11, 0.19, 0.16, 0.17, 0.13]
        
        confidence = self.confidence_system.calculate_prediction_confidence(
            predictions, actual_values
        )
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_prediction_confidence_insufficient_data(self):
        """予測信頼度計算データ不足テスト"""
        predictions = [0.1, 0.2]  # データ不足
        actual_values = [0.11, 0.19]
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_prediction_confidence(
                predictions, actual_values
            )
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_prediction_confidence_exception(self):
        """予測信頼度計算例外処理テスト"""
        predictions = [0.1, 0.2, 0.15, 0.18, 0.12]
        actual_values = [0.11, 0.19, 0.16, 0.17, 0.13]
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_prediction_confidence(
                    predictions, actual_values
                )
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_calculate_ensemble_confidence_success(self):
        """アンサンブル信頼度計算成功テスト"""
        model_predictions = {
            "model1": [0.1, 0.2, 0.15],
            "model2": [0.12, 0.18, 0.16],
            "model3": [0.11, 0.19, 0.14],
        }
        actual_values = [0.11, 0.19, 0.15]
        
        confidence = self.confidence_system.calculate_ensemble_confidence(
            model_predictions, actual_values
        )
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_ensemble_confidence_insufficient_models(self):
        """アンサンブル信頼度計算モデル不足テスト"""
        model_predictions = {
            "model1": [0.1, 0.2, 0.15],
        }  # モデル不足
        actual_values = [0.11, 0.19, 0.15]
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_ensemble_confidence(
                model_predictions, actual_values
            )
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_ensemble_confidence_exception(self):
        """アンサンブル信頼度計算例外処理テスト"""
        model_predictions = {
            "model1": [0.1, 0.2, 0.15],
            "model2": [0.12, 0.18, 0.16],
            "model3": [0.11, 0.19, 0.14],
        }
        actual_values = [0.11, 0.19, 0.15]
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_ensemble_confidence(
                    model_predictions, actual_values
                )
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_calculate_volatility_confidence_low_volatility(self):
        """低ボラティリティ信頼度計算テスト"""
        predictions = [0.1, 0.11, 0.12, 0.13, 0.14]  # 低ボラティリティ
        
        confidence = self.confidence_system.calculate_volatility_confidence(predictions)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_volatility_confidence_high_volatility(self):
        """高ボラティリティ信頼度計算テスト"""
        predictions = [0.1, 0.5, 0.2, 0.8, 0.3]  # 高ボラティリティ
        
        confidence = self.confidence_system.calculate_volatility_confidence(predictions)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_volatility_confidence_insufficient_data(self):
        """ボラティリティ信頼度計算データ不足テスト"""
        predictions = [0.1, 0.2]  # データ不足
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_volatility_confidence(predictions)
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_volatility_confidence_exception(self):
        """ボラティリティ信頼度計算例外処理テスト"""
        predictions = [0.1, 0.2, 0.15, 0.18, 0.12]
        
        with patch('numpy.std', side_effect=Exception("Std error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_volatility_confidence(predictions)
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_calculate_consensus_confidence_high_consensus(self):
        """高コンセンサス信頼度計算テスト"""
        predictions = [0.1, 0.11, 0.12, 0.13, 0.14]  # 高コンセンサス
        
        confidence = self.confidence_system.calculate_consensus_confidence(predictions)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_consensus_confidence_low_consensus(self):
        """低コンセンサス信頼度計算テスト"""
        predictions = [0.1, 0.5, 0.2, 0.8, 0.3]  # 低コンセンサス
        
        confidence = self.confidence_system.calculate_consensus_confidence(predictions)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_consensus_confidence_insufficient_data(self):
        """コンセンサス信頼度計算データ不足テスト"""
        predictions = [0.1, 0.2]  # データ不足
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_consensus_confidence(predictions)
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_consensus_confidence_exception(self):
        """コンセンサス信頼度計算例外処理テスト"""
        predictions = [0.1, 0.2, 0.15, 0.18, 0.12]
        
        with patch('numpy.std', side_effect=Exception("Std error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_consensus_confidence(predictions)
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_calculate_historical_accuracy_high_accuracy(self):
        """高精度履歴信頼度計算テスト"""
        predictions = [0.1, 0.2, 0.15, 0.18, 0.12]
        actual_values = [0.11, 0.19, 0.16, 0.17, 0.13]  # 高精度
        
        confidence = self.confidence_system.calculate_historical_accuracy(
            predictions, actual_values
        )
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_historical_accuracy_low_accuracy(self):
        """低精度履歴信頼度計算テスト"""
        predictions = [0.1, 0.2, 0.15, 0.18, 0.12]
        actual_values = [0.5, 0.8, 0.3, 0.9, 0.2]  # 低精度
        
        confidence = self.confidence_system.calculate_historical_accuracy(
            predictions, actual_values
        )
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_historical_accuracy_insufficient_data(self):
        """履歴精度信頼度計算データ不足テスト"""
        predictions = [0.1, 0.2]  # データ不足
        actual_values = [0.11, 0.19]
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_historical_accuracy(
                predictions, actual_values
            )
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_historical_accuracy_exception(self):
        """履歴精度信頼度計算例外処理テスト"""
        predictions = [0.1, 0.2, 0.15, 0.18, 0.12]
        actual_values = [0.11, 0.19, 0.16, 0.17, 0.13]
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_historical_accuracy(
                    predictions, actual_values
                )
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_calculate_market_condition_confidence_bullish(self):
        """強気市場条件信頼度計算テスト"""
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "sentiment": 0.8,
        }
        
        confidence = self.confidence_system.calculate_market_condition_confidence(market_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_market_condition_confidence_bearish(self):
        """弱気市場条件信頼度計算テスト"""
        market_data = {
            "trend": "bearish",
            "volatility": 0.25,
            "volume": 800000,
            "sentiment": 0.3,
        }
        
        confidence = self.confidence_system.calculate_market_condition_confidence(market_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_market_condition_confidence_neutral(self):
        """中立市場条件信頼度計算テスト"""
        market_data = {
            "trend": "neutral",
            "volatility": 0.20,
            "volume": 900000,
            "sentiment": 0.5,
        }
        
        confidence = self.confidence_system.calculate_market_condition_confidence(market_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_market_condition_confidence_insufficient_data(self):
        """市場条件信頼度計算データ不足テスト"""
        market_data = {}  # データ不足
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_market_condition_confidence(market_data)
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_market_condition_confidence_exception(self):
        """市場条件信頼度計算例外処理テスト"""
        market_data = {
            "trend": "bullish",
            "volatility": 0.15,
            "volume": 1000000,
            "sentiment": 0.8,
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_market_condition_confidence(market_data)
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_calculate_technical_confidence_strong_signals(self):
        """強力テクニカルシグナル信頼度計算テスト"""
        technical_data = {
            "rsi": 30,
            "macd": "bullish",
            "bollinger": "oversold",
            "moving_average": "bullish",
            "volume": "high",
        }
        
        confidence = self.confidence_system.calculate_technical_confidence(technical_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_technical_confidence_weak_signals(self):
        """弱いテクニカルシグナル信頼度計算テスト"""
        technical_data = {
            "rsi": 50,
            "macd": "neutral",
            "bollinger": "neutral",
            "moving_average": "neutral",
            "volume": "normal",
        }
        
        confidence = self.confidence_system.calculate_technical_confidence(technical_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_technical_confidence_insufficient_data(self):
        """テクニカル信頼度計算データ不足テスト"""
        technical_data = {}  # データ不足
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_technical_confidence(technical_data)
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_technical_confidence_exception(self):
        """テクニカル信頼度計算例外処理テスト"""
        technical_data = {
            "rsi": 30,
            "macd": "bullish",
            "bollinger": "oversold",
            "moving_average": "bullish",
            "volume": "high",
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_technical_confidence(technical_data)
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_calculate_fundamental_confidence_strong_fundamentals(self):
        """強力ファンダメンタル信頼度計算テスト"""
        fundamental_data = {
            "pe_ratio": 15,
            "pb_ratio": 1.5,
            "debt_ratio": 0.3,
            "roe": 0.15,
            "revenue_growth": 0.1,
        }
        
        confidence = self.confidence_system.calculate_fundamental_confidence(fundamental_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_fundamental_confidence_weak_fundamentals(self):
        """弱いファンダメンタル信頼度計算テスト"""
        fundamental_data = {
            "pe_ratio": 50,
            "pb_ratio": 5.0,
            "debt_ratio": 0.8,
            "roe": 0.05,
            "revenue_growth": -0.05,
        }
        
        confidence = self.confidence_system.calculate_fundamental_confidence(fundamental_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_calculate_fundamental_confidence_insufficient_data(self):
        """ファンダメンタル信頼度計算データ不足テスト"""
        fundamental_data = {}  # データ不足
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            confidence = self.confidence_system.calculate_fundamental_confidence(fundamental_data)
            
            self.assertIsNone(confidence)
            mock_warning.assert_called_once()

    def test_calculate_fundamental_confidence_exception(self):
        """ファンダメンタル信頼度計算例外処理テスト"""
        fundamental_data = {
            "pe_ratio": 15,
            "pb_ratio": 1.5,
            "debt_ratio": 0.3,
            "roe": 0.15,
            "revenue_growth": 0.1,
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                confidence = self.confidence_system.calculate_fundamental_confidence(fundamental_data)
                
                self.assertIsNone(confidence)
                mock_error.assert_called_once()

    def test_combine_confidence_scores_success(self):
        """信頼度スコア結合成功テスト"""
        confidence_scores = {
            "prediction": 0.8,
            "ensemble": 0.75,
            "volatility": 0.7,
            "consensus": 0.85,
            "historical": 0.8,
            "market": 0.75,
            "technical": 0.8,
            "fundamental": 0.7,
        }
        
        combined_confidence = self.confidence_system.combine_confidence_scores(confidence_scores)
        
        self.assertIsInstance(combined_confidence, float)
        self.assertGreaterEqual(combined_confidence, 0.0)
        self.assertLessEqual(combined_confidence, 1.0)

    def test_combine_confidence_scores_insufficient_scores(self):
        """信頼度スコア結合スコア不足テスト"""
        confidence_scores = {
            "prediction": 0.8,
        }  # スコア不足
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            combined_confidence = self.confidence_system.combine_confidence_scores(confidence_scores)
            
            self.assertIsNone(combined_confidence)
            mock_warning.assert_called_once()

    def test_combine_confidence_scores_exception(self):
        """信頼度スコア結合例外処理テスト"""
        confidence_scores = {
            "prediction": 0.8,
            "ensemble": 0.75,
            "volatility": 0.7,
            "consensus": 0.85,
            "historical": 0.8,
            "market": 0.75,
            "technical": 0.8,
            "fundamental": 0.7,
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                combined_confidence = self.confidence_system.combine_confidence_scores(confidence_scores)
                
                self.assertIsNone(combined_confidence)
                mock_error.assert_called_once()

    def test_determine_confidence_level_high(self):
        """高信頼度レベル判定テスト"""
        confidence_score = 0.9
        
        level = self.confidence_system.determine_confidence_level(confidence_score)
        
        self.assertEqual(level, ConfidenceLevel.HIGH)

    def test_determine_confidence_level_medium(self):
        """中信頼度レベル判定テスト"""
        confidence_score = 0.7
        
        level = self.confidence_system.determine_confidence_level(confidence_score)
        
        self.assertEqual(level, ConfidenceLevel.MEDIUM)

    def test_determine_confidence_level_low(self):
        """低信頼度レベル判定テスト"""
        confidence_score = 0.4
        
        level = self.confidence_system.determine_confidence_level(confidence_score)
        
        self.assertEqual(level, ConfidenceLevel.LOW)

    def test_determine_confidence_level_invalid(self):
        """無効信頼度レベル判定テスト"""
        confidence_score = -0.1  # 無効な値
        
        with patch.object(self.confidence_system.logger, 'warning') as mock_warning:
            level = self.confidence_system.determine_confidence_level(confidence_score)
            
            self.assertEqual(level, ConfidenceLevel.LOW)
            mock_warning.assert_called_once()

    def test_update_confidence_history_success(self):
        """信頼度履歴更新成功テスト"""
        symbol = "TEST"
        confidence_score = 0.8
        prediction_type = "PRICE"
        
        self.confidence_system.update_confidence_history(
            symbol, confidence_score, prediction_type
        )
        
        self.assertIn(symbol, self.confidence_system.confidence_history)
        self.assertEqual(
            len(self.confidence_system.confidence_history[symbol]), 1
        )

    def test_update_confidence_history_exception(self):
        """信頼度履歴更新例外処理テスト"""
        symbol = "TEST"
        confidence_score = 0.8
        prediction_type = "PRICE"
        
        with patch.object(self.confidence_system, 'confidence_history', side_effect=Exception("History error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                self.confidence_system.update_confidence_history(
                    symbol, confidence_score, prediction_type
                )
                mock_error.assert_called_once()

    def test_get_confidence_metrics_success(self):
        """信頼度メトリクス取得成功テスト"""
        symbol = "TEST"
        
        # 履歴を追加
        self.confidence_system.confidence_history[symbol] = [
            {"confidence": 0.8, "timestamp": datetime.now(), "type": PredictionType.PRICE},
            {"confidence": 0.75, "timestamp": datetime.now(), "type": PredictionType.PRICE},
            {"confidence": 0.85, "timestamp": datetime.now(), "type": PredictionType.PRICE},
        ]
        
        metrics = self.confidence_system.get_confidence_metrics(symbol)
        
        self.assertIsInstance(metrics, ConfidenceMetrics)
        self.assertIsInstance(metrics.average_confidence, float)
        self.assertIsInstance(metrics.confidence_trend, str)
        self.assertIsInstance(metrics.volatility, float)
        self.assertIsInstance(metrics.stability_score, float)

    def test_get_confidence_metrics_no_history(self):
        """信頼度メトリクス取得履歴なしテスト"""
        symbol = "TEST"
        
        metrics = self.confidence_system.get_confidence_metrics(symbol)
        
        self.assertIsNone(metrics)

    def test_get_confidence_metrics_exception(self):
        """信頼度メトリクス取得例外処理テスト"""
        symbol = "TEST"
        
        with patch.object(self.confidence_system, 'confidence_history', side_effect=Exception("Metrics error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                metrics = self.confidence_system.get_confidence_metrics(symbol)
                
                self.assertIsNone(metrics)
                mock_error.assert_called_once()

    def test_export_confidence_report_success(self):
        """信頼度レポート出力成功テスト"""
        symbol = "TEST"
        
        # 履歴を追加
        self.confidence_system.confidence_history[symbol] = [
            {"confidence": 0.8, "timestamp": datetime.now(), "type": PredictionType.PRICE},
            {"confidence": 0.75, "timestamp": datetime.now(), "type": PredictionType.PRICE},
            {"confidence": 0.85, "timestamp": datetime.now(), "type": PredictionType.PRICE},
        ]
        
        report = self.confidence_system.export_confidence_report(symbol)
        
        self.assertIsInstance(report, dict)
        self.assertIn("symbol", report)
        self.assertIn("confidence_metrics", report)
        self.assertIn("recommendations", report)
        self.assertIn("generated_at", report)

    def test_export_confidence_report_no_history(self):
        """信頼度レポート出力履歴なしテスト"""
        symbol = "TEST"
        
        report = self.confidence_system.export_confidence_report(symbol)
        
        self.assertIsInstance(report, dict)
        self.assertIn("symbol", report)
        self.assertIn("status", report)
        self.assertEqual(report["status"], "no_data")

    def test_export_confidence_report_exception(self):
        """信頼度レポート出力例外処理テスト"""
        symbol = "TEST"
        
        with patch.object(self.confidence_system, 'get_confidence_metrics', side_effect=Exception("Report error")):
            with patch.object(self.confidence_system.logger, 'error') as mock_error:
                report = self.confidence_system.export_confidence_report(symbol)
                
                self.assertIn("error", report)
                mock_error.assert_called_once()


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
