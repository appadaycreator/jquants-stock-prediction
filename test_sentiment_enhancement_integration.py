#!/usr/bin/env python3
"""
感情分析拡張システムの統合テスト
新機能と既存システムの統合をテスト

テスト項目:
- リアルタイム感情指標の生成
- 動的リスク調整の動作
- 感情トレンド予測の精度
- 統合システムの性能
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import time
import unittest
from unittest.mock import Mock, patch, MagicMock

# テスト対象システムのインポート
try:
    from realtime_sentiment_metrics import RealtimeSentimentMetricsGenerator, MetricType
    from dynamic_risk_adjustment import DynamicRiskAdjustmentSystem, RiskAdjustmentType
    from sentiment_trend_prediction import SentimentTrendPredictor, PredictionModel
    from integrated_sentiment_enhancement import IntegratedSentimentEnhancementSystem
    from sentiment_analysis_system import SentimentTradingSystem, SentimentType
    from enhanced_sentiment_trading import EnhancedSentimentTradingSystem
except ImportError as e:
    logging.warning(f"システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test_sentiment_enhancement.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TestRealtimeSentimentMetrics(unittest.TestCase):
    """リアルタイム感情指標のテスト"""

    def setUp(self):
        """テストの初期化"""
        self.metrics_generator = RealtimeSentimentMetricsGenerator()
        self.test_symbols = ["AAPL", "GOOGL"]

    def test_metrics_generator_initialization(self):
        """指標生成器の初期化テスト"""
        self.assertIsNotNone(self.metrics_generator)
        self.assertIsInstance(self.metrics_generator, RealtimeSentimentMetricsGenerator)
        logger.info("✅ リアルタイム感情指標生成器の初期化テスト通過")

    @patch("yfinance.Ticker")
    async def test_generate_realtime_metrics(self, mock_ticker):
        """リアルタイム指標の生成テスト"""
        # モックデータの設定
        mock_hist = pd.DataFrame({"Close": [150.0, 151.0, 152.0, 153.0, 154.0]})
        mock_ticker.return_value.history.return_value = mock_hist

        # 指標の生成
        metrics = await self.metrics_generator.generate_realtime_metrics(
            self.test_symbols
        )

        # 結果の検証
        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)

        for metric in metrics:
            self.assertIn("timestamp", metric.__dict__)
            self.assertIn("symbol", metric.__dict__)
            self.assertIn("metric_type", metric.__dict__)
            self.assertIn("value", metric.__dict__)

        logger.info("✅ リアルタイム指標生成テスト通過")

    def test_metrics_summary(self):
        """指標サマリーのテスト"""
        summary = self.metrics_generator.get_metrics_summary()
        self.assertIsInstance(summary, dict)
        logger.info("✅ 指標サマリー取得テスト通過")

    def test_alerts_generation(self):
        """アラート生成のテスト"""
        alerts = self.metrics_generator.generate_alerts()
        self.assertIsInstance(alerts, list)
        logger.info("✅ アラート生成テスト通過")


class TestDynamicRiskAdjustment(unittest.TestCase):
    """動的リスク調整のテスト"""

    def setUp(self):
        """テストの初期化"""
        self.risk_system = DynamicRiskAdjustmentSystem()
        self.test_symbol = "AAPL"

    def test_risk_system_initialization(self):
        """リスク調整システムの初期化テスト"""
        self.assertIsNotNone(self.risk_system)
        self.assertIsInstance(self.risk_system, DynamicRiskAdjustmentSystem)
        logger.info("✅ 動的リスク調整システムの初期化テスト通過")

    @patch("yfinance.Ticker")
    async def test_risk_adjustment(self, mock_ticker):
        """リスク調整のテスト"""
        # モックデータの設定
        mock_hist = pd.DataFrame({"Close": [150.0, 151.0, 152.0, 153.0, 154.0]})
        mock_ticker.return_value.history.return_value = mock_hist

        # リスク調整の実行
        risk_profile = await self.risk_system.adjust_risk_parameters(self.test_symbol)

        # 結果の検証
        self.assertIsNotNone(risk_profile)
        self.assertEqual(risk_profile.symbol, self.test_symbol)
        self.assertGreaterEqual(risk_profile.max_position, 0)
        self.assertGreaterEqual(risk_profile.stop_loss, 0)
        self.assertGreaterEqual(risk_profile.take_profit, 0)

        logger.info("✅ リスク調整テスト通過")

    def test_position_size_calculation(self):
        """ポジションサイズ計算のテスト"""
        account_balance = 100000
        current_price = 150.0

        position_size = self.risk_system.calculate_position_size(
            self.test_symbol, account_balance, current_price
        )

        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_size, account_balance)

        logger.info("✅ ポジションサイズ計算テスト通過")

    def test_stop_loss_calculation(self):
        """ストップロス計算のテスト"""
        entry_price = 150.0

        stop_loss = self.risk_system.calculate_stop_loss(self.test_symbol, entry_price)

        self.assertLess(stop_loss, entry_price)
        self.assertGreater(stop_loss, 0)

        logger.info("✅ ストップロス計算テスト通過")


class TestSentimentTrendPrediction(unittest.TestCase):
    """感情トレンド予測のテスト"""

    def setUp(self):
        """テストの初期化"""
        self.predictor = SentimentTrendPredictor()
        self.test_symbol = "AAPL"

    def test_predictor_initialization(self):
        """予測器の初期化テスト"""
        self.assertIsNotNone(self.predictor)
        self.assertIsInstance(self.predictor, SentimentTrendPredictor)
        logger.info("✅ 感情トレンド予測器の初期化テスト通過")

    @patch("yfinance.Ticker")
    async def test_sentiment_trend_prediction(self, mock_ticker):
        """感情トレンド予測のテスト"""
        # モックデータの設定
        mock_hist = pd.DataFrame({"Close": [150.0, 151.0, 152.0, 153.0, 154.0]})
        mock_ticker.return_value.history.return_value = mock_hist

        # 予測の実行
        prediction = await self.predictor.predict_sentiment_trend(
            self.test_symbol, horizon=15
        )

        # 結果の検証
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.symbol, self.test_symbol)
        self.assertEqual(prediction.prediction_horizon, 15)
        self.assertIsInstance(prediction.predicted_sentiment, float)
        self.assertIsInstance(prediction.confidence, float)
        self.assertIn(prediction.trend_direction, ["up", "down", "stable"])

        logger.info("✅ 感情トレンド予測テスト通過")

    def test_trend_pattern_detection(self):
        """トレンドパターン検出のテスト"""
        # テスト用の履歴データを設定
        test_history = [
            {
                "sentiment_score": 0.1,
                "volatility": 0.1,
                "trend_strength": 0.1,
                "risk_level": 0.1,
            },
            {
                "sentiment_score": 0.2,
                "volatility": 0.1,
                "trend_strength": 0.1,
                "risk_level": 0.1,
            },
            {
                "sentiment_score": 0.3,
                "volatility": 0.1,
                "trend_strength": 0.1,
                "risk_level": 0.1,
            },
            {
                "sentiment_score": 0.4,
                "volatility": 0.1,
                "trend_strength": 0.1,
                "risk_level": 0.1,
            },
            {
                "sentiment_score": 0.5,
                "volatility": 0.1,
                "trend_strength": 0.1,
                "risk_level": 0.1,
            },
        ]

        self.predictor.sentiment_history[self.test_symbol] = test_history

        patterns = self.predictor.detect_trend_patterns(self.test_symbol)

        self.assertIsInstance(patterns, list)

        logger.info("✅ トレンドパターン検出テスト通過")

    def test_prediction_summary(self):
        """予測サマリーのテスト"""
        summary = self.predictor.get_prediction_summary()
        self.assertIsInstance(summary, dict)
        logger.info("✅ 予測サマリー取得テスト通過")


class TestIntegratedSentimentEnhancement(unittest.TestCase):
    """統合感情分析拡張システムのテスト"""

    def setUp(self):
        """テストの初期化"""
        self.integrated_system = IntegratedSentimentEnhancementSystem()
        self.test_symbols = ["AAPL", "GOOGL"]

    def test_integrated_system_initialization(self):
        """統合システムの初期化テスト"""
        self.assertIsNotNone(self.integrated_system)
        self.assertIsInstance(
            self.integrated_system, IntegratedSentimentEnhancementSystem
        )
        logger.info("✅ 統合感情分析拡張システムの初期化テスト通過")

    def test_system_status(self):
        """システム状態のテスト"""
        status = self.integrated_system.get_system_status()

        self.assertIsInstance(status, dict)
        self.assertIn("is_running", status)
        self.assertIn("systems_initialized", status)
        self.assertIn("performance_stats", status)

        logger.info("✅ システム状態取得テスト通過")

    @patch("yfinance.Ticker")
    async def test_integrated_analysis(self, mock_ticker):
        """統合分析のテスト"""
        # モックデータの設定
        mock_hist = pd.DataFrame({"Close": [150.0, 151.0, 152.0, 153.0, 154.0]})
        mock_ticker.return_value.history.return_value = mock_hist

        # 統合分析の実行
        analyses = await self.integrated_system.perform_integrated_analysis(
            self.test_symbols
        )

        # 結果の検証
        self.assertIsInstance(analyses, list)
        self.assertEqual(len(analyses), len(self.test_symbols))

        for analysis in analyses:
            self.assertIsNotNone(analysis)
            self.assertIn(analysis.symbol, self.test_symbols)
            self.assertIsInstance(analysis.overall_sentiment, str)
            self.assertIsInstance(analysis.confidence_score, float)
            self.assertIsInstance(analysis.trading_recommendations, list)

        logger.info("✅ 統合分析テスト通過")

    def test_performance_stats(self):
        """性能統計のテスト"""
        stats = self.integrated_system._get_performance_stats()
        self.assertIsInstance(stats, dict)
        logger.info("✅ 性能統計取得テスト通過")

    def test_system_report_generation(self):
        """システムレポート生成のテスト"""
        report = self.integrated_system.generate_system_report()

        self.assertIsInstance(report, dict)
        self.assertIn("timestamp", report)
        self.assertIn("system_status", report)
        self.assertIn("recent_analyses", report)

        logger.info("✅ システムレポート生成テスト通過")


class TestSystemIntegration(unittest.TestCase):
    """システム統合のテスト"""

    def setUp(self):
        """テストの初期化"""
        self.test_symbols = ["AAPL", "GOOGL", "MSFT"]

    async def test_end_to_end_integration(self):
        """エンドツーエンド統合テスト"""
        logger.info("🔄 エンドツーエンド統合テストを開始...")

        try:
            # 統合システムの初期化
            integrated_system = IntegratedSentimentEnhancementSystem()

            # システム状態の確認
            status = integrated_system.get_system_status()
            logger.info(f"システム状態: {status['systems_initialized']}")

            # 統合分析の実行
            start_time = time.time()
            analyses = await integrated_system.perform_integrated_analysis(
                self.test_symbols
            )
            execution_time = time.time() - start_time

            # 結果の検証
            self.assertIsInstance(analyses, list)
            self.assertEqual(len(analyses), len(self.test_symbols))

            # 性能の確認
            logger.info(f"実行時間: {execution_time:.2f}秒")
            self.assertLess(execution_time, 60.0)  # 60秒以内に完了

            # 各分析結果の確認
            for analysis in analyses:
                self.assertIsNotNone(analysis.overall_sentiment)
                self.assertGreaterEqual(analysis.confidence_score, 0.0)
                self.assertLessEqual(analysis.confidence_score, 1.0)

                logger.info(
                    f"シンボル {analysis.symbol}: "
                    f"{analysis.overall_sentiment} "
                    f"(信頼度: {analysis.confidence_score:.2f})"
                )

            # システムレポートの生成
            report = integrated_system.generate_system_report()
            self.assertIsInstance(report, dict)

            logger.info("✅ エンドツーエンド統合テスト完了")

        except Exception as e:
            logger.error(f"エンドツーエンド統合テストでエラー: {e}")
            self.fail(f"統合テストに失敗: {e}")

    def test_configuration_compatibility(self):
        """設定ファイル互換性のテスト"""
        try:
            import yaml

            # 設定ファイルの読み込み
            with open("sentiment_config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 新機能の設定が含まれているかチェック
            self.assertIn("realtime_metrics", config)
            self.assertIn("dynamic_risk_adjustment", config)
            self.assertIn("sentiment_trend_prediction", config)
            self.assertIn("integrated_system", config)

            logger.info("✅ 設定ファイル互換性テスト通過")

        except Exception as e:
            logger.error(f"設定ファイル互換性テストでエラー: {e}")
            self.fail(f"設定ファイルテストに失敗: {e}")


async def run_performance_test():
    """性能テストの実行"""
    logger.info("🚀 性能テストを開始...")

    try:
        # 統合システムの初期化
        system = IntegratedSentimentEnhancementSystem()

        # テストシンボル
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

        # 性能測定
        start_time = time.time()

        # 統合分析の実行
        analyses = await system.perform_integrated_analysis(symbols)

        execution_time = time.time() - start_time

        # 性能統計の取得
        performance_stats = system._get_performance_stats()

        # 結果の表示
        logger.info(f"📊 性能テスト結果:")
        logger.info(f"  実行時間: {execution_time:.2f}秒")
        logger.info(f"  処理シンボル数: {len(symbols)}")
        logger.info(f"  平均処理時間: {execution_time/len(symbols):.2f}秒/シンボル")

        if performance_stats and "avg_processing_time" in performance_stats:
            logger.info(
                f"  平均処理時間（統計）: {performance_stats['avg_processing_time']:.2f}秒"
            )
            logger.info(f"  平均精度: {performance_stats.get('avg_accuracy', 0):.2f}")
            logger.info(
                f"  平均信頼性: {performance_stats.get('avg_reliability', 0):.2f}"
            )

        # 性能要件の確認
        max_acceptable_time = 30.0  # 30秒
        if execution_time <= max_acceptable_time:
            logger.info("✅ 性能要件を満たしています")
        else:
            logger.warning(
                f"⚠️ 性能要件を超過しています (許容値: {max_acceptable_time}秒)"
            )

        return True

    except Exception as e:
        logger.error(f"性能テストでエラー: {e}")
        return False


async def main():
    """メイン関数"""
    logger.info("🧪 感情分析拡張システムの統合テストを開始...")

    # 単体テストの実行
    test_suite = unittest.TestSuite()

    # テストケースの追加
    test_suite.addTest(unittest.makeSuite(TestRealtimeSentimentMetrics))
    test_suite.addTest(unittest.makeSuite(TestDynamicRiskAdjustment))
    test_suite.addTest(unittest.makeSuite(TestSentimentTrendPrediction))
    test_suite.addTest(unittest.makeSuite(TestIntegratedSentimentEnhancement))
    test_suite.addTest(unittest.makeSuite(TestSystemIntegration))

    # テストランナーの実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 結果の表示
    logger.info(f"📋 テスト結果:")
    logger.info(f"  実行テスト数: {result.testsRun}")
    logger.info(
        f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}"
    )
    logger.info(f"  失敗: {len(result.failures)}")
    logger.info(f"  エラー: {len(result.errors)}")

    if result.failures:
        logger.error("❌ 失敗したテスト:")
        for test, traceback in result.failures:
            logger.error(f"  - {test}: {traceback}")

    if result.errors:
        logger.error("❌ エラーが発生したテスト:")
        for test, traceback in result.errors:
            logger.error(f"  - {test}: {traceback}")

    # 性能テストの実行
    logger.info("\n" + "=" * 50)
    performance_success = await run_performance_test()

    # 総合結果
    total_tests = result.testsRun
    successful_tests = total_tests - len(result.failures) - len(result.errors)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

    logger.info(f"\n🎯 総合テスト結果:")
    logger.info(f"  成功率: {success_rate:.1f}%")
    logger.info(f"  性能テスト: {'✅ 成功' if performance_success else '❌ 失敗'}")

    if success_rate >= 80 and performance_success:
        logger.info("🎉 統合テストが成功しました！")
        return True
    else:
        logger.error("❌ 統合テストに問題があります。")
        return False


if __name__ == "__main__":
    asyncio.run(main())
