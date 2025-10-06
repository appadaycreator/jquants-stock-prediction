#!/usr/bin/env python3
"""
簡素化リスク管理システムの統合テスト
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import json

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.simplified_risk_management import SimplifiedRiskManager
from core.simplified_risk_api import SimplifiedRiskAPI
from core.enhanced_risk_alerts import EnhancedRiskAlerts
from routine_api import RoutineAnalysisAPI


class TestSimplifiedRiskIntegration(unittest.TestCase):
    """簡素化リスク管理システムの統合テスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "risk_thresholds": {
                "low_risk_max": 30,
                "medium_risk_max": 70,
                "high_risk_min": 70,
            },
            "volatility_thresholds": {"low": 0.15, "medium": 0.30, "high": 0.30},
            "max_loss_calculation": {
                "var_multiplier": 2.0,
                "confidence_level": 0.95,
                "position_size_factor": 0.1,
            },
            "color_codes": {
                "low_risk": "#4CAF50",
                "medium_risk": "#FF9800",
                "high_risk": "#F44336",
            },
            "recommendations": {
                "low_risk": "投資推奨",
                "medium_risk": "注意深く投資",
                "high_risk": "投資見送り推奨",
            },
            "alert_settings": {
                "high_risk_threshold": 70,
                "high_volatility_threshold": 0.3,
                "max_loss_ratio_threshold": 0.1,
                "portfolio_imbalance_threshold": 0.5,
                "position_size_threshold": 0.2,
                "correlation_threshold": 0.8,
                "liquidity_threshold": 100000,
                "alert_retention_days": 30,
            },
        }

        # システム初期化
        self.risk_manager = SimplifiedRiskManager(self.config)
        self.risk_api = SimplifiedRiskAPI(self.config)
        self.risk_alerts = EnhancedRiskAlerts(self.config)
        self.routine_api = RoutineAnalysisAPI()

        # テスト用データ生成
        self.sample_stock_data = self._generate_sample_stock_data()
        self.sample_portfolio_data = self._generate_sample_portfolio_data()
        self.sample_market_data = self._generate_sample_market_data()

    def _generate_sample_stock_data(self) -> pd.DataFrame:
        """サンプル株式データ生成"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        prices = 100 + np.cumsum(np.random.normal(0, 2, 100))
        volumes = np.random.randint(1000, 5000, 100)

        return pd.DataFrame(
            {"Date": dates, "Close": prices, "Volume": volumes}
        ).set_index("Date")

    def _generate_sample_portfolio_data(self) -> dict:
        """サンプルポートフォリオデータ生成"""
        symbols = ["7203", "6758", "9984", "9434", "8306"]
        portfolio = {}

        for symbol in symbols:
            stock_data = self._generate_sample_stock_data()
            current_price = stock_data["Close"].iloc[-1]
            position_size = np.random.randint(10, 100)

            portfolio[symbol] = {
                "stock_data": stock_data,
                "current_price": current_price,
                "position_size": position_size,
                "account_balance": 1000000.0,
            }

        return portfolio

    def _generate_sample_market_data(self) -> dict:
        """サンプル市場データ生成"""
        return {
            "volatility": np.random.uniform(0.1, 0.4),
            "market_stress": np.random.uniform(0.0, 1.0),
            "liquidity": np.random.uniform(0.5, 1.0),
            "correlation": np.random.uniform(0.3, 0.8),
        }

    def test_end_to_end_risk_assessment(self):
        """エンドツーエンドリスク評価テスト"""
        # 1. 個別銘柄のリスク評価
        risk_metrics = self.risk_manager.calculate_simplified_risk_metrics(
            self.sample_stock_data, 125.0, 100.0, 1000000.0
        )

        self.assertIsNotNone(risk_metrics)
        self.assertIn(risk_metrics.risk_level.value, ["low", "medium", "high"])
        self.assertGreaterEqual(risk_metrics.risk_score, 0)
        self.assertLessEqual(risk_metrics.risk_score, 100)
        self.assertGreaterEqual(risk_metrics.max_loss_amount, 0)

        # 2. ポートフォリオ全体のリスク評価
        portfolio_balance = self.risk_manager.calculate_portfolio_risk_balance(
            self.sample_portfolio_data, 1000000.0
        )

        self.assertIsNotNone(portfolio_balance)
        self.assertGreaterEqual(portfolio_balance.total_risk_score, 0)
        self.assertLessEqual(portfolio_balance.total_risk_score, 100)
        self.assertGreaterEqual(portfolio_balance.low_risk_count, 0)
        self.assertGreaterEqual(portfolio_balance.medium_risk_count, 0)
        self.assertGreaterEqual(portfolio_balance.high_risk_count, 0)

        # 3. リスクアラート生成
        alerts = self.risk_alerts.generate_comprehensive_alerts(
            self.sample_portfolio_data, self.sample_market_data
        )

        self.assertIsInstance(alerts, list)
        for alert in alerts:
            self.assertIsNotNone(alert.id)
            self.assertIsNotNone(alert.type)
            self.assertIsNotNone(alert.severity)
            self.assertIsNotNone(alert.symbol)
            self.assertIsNotNone(alert.title)
            self.assertIsNotNone(alert.message)
            self.assertIsNotNone(alert.recommendation)

    def test_api_integration(self):
        """API統合テスト"""
        # 1. 簡素化リスク評価API
        risk_assessment = self.risk_api.get_simplified_risk_assessment(
            self.sample_stock_data, 125.0, 100.0, 1000000.0
        )

        self.assertIsInstance(risk_assessment, dict)
        self.assertIn("success", risk_assessment)
        if risk_assessment["success"]:
            self.assertIn("data", risk_assessment)
            data = risk_assessment["data"]
            self.assertIn("risk_level", data)
            self.assertIn("risk_score", data)
            self.assertIn("max_loss_amount", data)
            self.assertIn("display_text", data)

        # 2. ポートフォリオリスクバランスAPI
        portfolio_balance = self.risk_api.get_portfolio_risk_balance(
            self.sample_portfolio_data, 1000000.0
        )

        self.assertIsInstance(portfolio_balance, dict)
        self.assertIn("success", portfolio_balance)
        if portfolio_balance["success"]:
            self.assertIn("data", portfolio_balance)
            data = portfolio_balance["data"]
            self.assertIn("total_risk_score", data)
            self.assertIn("risk_distribution", data)
            self.assertIn("overall_recommendation", data)

        # 3. リスクアラートAPI
        risk_alerts = self.risk_api.get_risk_alerts(self.sample_portfolio_data)

        self.assertIsInstance(risk_alerts, dict)
        self.assertIn("success", risk_alerts)
        if risk_alerts["success"]:
            self.assertIn("data", risk_alerts)
            data = risk_alerts["data"]
            self.assertIn("alerts", data)
            self.assertIn("alert_counts", data)

        # 4. 視覚的リスク表示API
        visual_display = self.risk_api.get_visual_risk_display(
            self.sample_portfolio_data
        )

        self.assertIsInstance(visual_display, dict)
        self.assertIn("success", visual_display)
        if visual_display["success"]:
            self.assertIn("data", visual_display)
            data = visual_display["data"]
            self.assertIn("portfolio_summary", data)
            self.assertIn("stock_risk_data", data)
            self.assertIn("chart_data", data)

    def test_alert_system_integration(self):
        """アラートシステム統合テスト"""
        # 1. 包括的アラート生成
        alerts = self.risk_alerts.generate_comprehensive_alerts(
            self.sample_portfolio_data, self.sample_market_data
        )

        self.assertIsInstance(alerts, list)
        self.assertGreaterEqual(len(alerts), 0)

        # 2. アラートサマリー取得
        alert_summary = self.risk_alerts.get_alert_summary()

        self.assertIsNotNone(alert_summary)
        self.assertGreaterEqual(alert_summary.total_alerts, 0)
        self.assertGreaterEqual(alert_summary.critical_alerts, 0)
        self.assertGreaterEqual(alert_summary.warning_alerts, 0)
        self.assertGreaterEqual(alert_summary.info_alerts, 0)
        self.assertGreaterEqual(alert_summary.emergency_alerts, 0)
        self.assertIsInstance(alert_summary.alerts_by_type, dict)
        self.assertIsInstance(alert_summary.alerts_by_symbol, dict)
        self.assertIsInstance(alert_summary.recent_alerts, list)
        self.assertIsInstance(alert_summary.top_risks, list)

        # 3. 個人化推奨事項生成
        recommendations = self.risk_alerts.get_personalized_recommendations(
            self.sample_portfolio_data, "medium"
        )

        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertIn("priority", rec)
            self.assertIn("title", rec)
            self.assertIn("description", rec)
            self.assertIn("action", rec)
            self.assertIn("impact", rec)
            self.assertIn("effort", rec)

    def test_routine_api_integration(self):
        """ルーチンAPI統合テスト"""
        # 1. 簡素化リスク評価付き株式分析
        stock_codes = ["7203", "6758", "9984"]
        analysis_result = self.routine_api.analyze_stocks_with_simplified_risk(
            stock_codes, include_risk_assessment=True
        )

        self.assertIsInstance(analysis_result, dict)
        self.assertIn("success", analysis_result)
        if analysis_result["success"]:
            self.assertIn("data", analysis_result)
            data = analysis_result["data"]
            self.assertIn("analysis_date", data)
            self.assertIn("stock_codes", data)
            self.assertIn("simplified_risk_assessment", data)

        # 2. 簡素化リスクダッシュボードデータ取得
        dashboard_data = self.routine_api.get_simplified_risk_dashboard_data(
            self.sample_portfolio_data, 1000000.0
        )

        self.assertIsInstance(dashboard_data, dict)
        self.assertIn("success", dashboard_data)
        if dashboard_data["success"]:
            self.assertIn("data", dashboard_data)

        # 3. ポートフォリオリスクサマリー取得
        risk_summary = self.routine_api.get_portfolio_risk_summary(
            self.sample_portfolio_data, 1000000.0
        )

        self.assertIsInstance(risk_summary, dict)
        self.assertIn("success", risk_summary)
        if risk_summary["success"]:
            self.assertIn("data", risk_summary)
            data = risk_summary["data"]
            self.assertIn("portfolio_balance", data)
            self.assertIn("risk_alerts", data)
            self.assertIn("risk_statistics", data)
            self.assertIn("recommendations", data)

    def test_data_consistency(self):
        """データ一貫性テスト"""
        # 同じデータで複数回実行して結果の一貫性を確認
        results = []

        for i in range(3):
            risk_metrics = self.risk_manager.calculate_simplified_risk_metrics(
                self.sample_stock_data, 125.0, 100.0, 1000000.0
            )
            results.append(risk_metrics)

        # 結果の一貫性確認
        for i in range(1, len(results)):
            self.assertEqual(results[0].risk_level, results[i].risk_level)
            self.assertAlmostEqual(
                results[0].risk_score, results[i].risk_score, places=1
            )
            self.assertAlmostEqual(
                results[0].max_loss_amount, results[i].max_loss_amount, places=1
            )

    def test_performance_benchmark(self):
        """パフォーマンスベンチマークテスト"""
        import time

        # 大量データでのパフォーマンステスト
        large_portfolio = {}
        for i in range(50):  # 50銘柄のポートフォリオ
            symbol = f"TEST{i:04d}"
            stock_data = self._generate_sample_stock_data()
            current_price = stock_data["Close"].iloc[-1]

            large_portfolio[symbol] = {
                "stock_data": stock_data,
                "current_price": current_price,
                "position_size": np.random.randint(10, 100),
                "account_balance": 1000000.0,
            }

        # パフォーマンス測定
        start_time = time.time()

        # ポートフォリオリスクバランス計算
        portfolio_balance = self.risk_manager.calculate_portfolio_risk_balance(
            large_portfolio, 1000000.0
        )

        # リスクアラート生成
        alerts = self.risk_alerts.generate_comprehensive_alerts(large_portfolio)

        end_time = time.time()
        execution_time = end_time - start_time

        # パフォーマンス確認（5秒以内で完了）
        self.assertLess(execution_time, 5.0)

        # 結果の妥当性確認
        self.assertIsNotNone(portfolio_balance)
        self.assertIsInstance(alerts, list)
        self.assertGreaterEqual(len(alerts), 0)

    def test_error_recovery(self):
        """エラー回復テスト"""
        # 無効なデータでのテスト
        invalid_data = {
            "INVALID": {
                "stock_data": None,
                "current_price": -100,  # 負の価格
                "position_size": -50,  # 負のポジションサイズ
                "account_balance": -1000000,  # 負の残高
            }
        }

        # エラーが発生してもシステムが停止しないことを確認
        try:
            portfolio_balance = self.risk_manager.calculate_portfolio_risk_balance(
                invalid_data, 1000000.0
            )
            self.assertIsNotNone(portfolio_balance)
        except Exception as e:
            self.fail(f"エラー回復テストで予期しないエラーが発生: {e}")

        try:
            alerts = self.risk_alerts.generate_comprehensive_alerts(invalid_data)
            self.assertIsInstance(alerts, list)
        except Exception as e:
            self.fail(f"エラー回復テストで予期しないエラーが発生: {e}")

    def test_configuration_validation(self):
        """設定検証テスト"""
        # 無効な設定でのテスト
        invalid_config = {
            "risk_thresholds": {
                "low_risk_max": -10,  # 負の値
                "medium_risk_max": 150,  # 100を超える値
                "high_risk_min": 50,
            }
        }

        # 設定が無効でもシステムが動作することを確認
        try:
            risk_manager = SimplifiedRiskManager(invalid_config)
            self.assertIsNotNone(risk_manager)
        except Exception as e:
            self.fail(f"設定検証テストで予期しないエラーが発生: {e}")

    def test_memory_usage(self):
        """メモリ使用量テスト"""
        import psutil
        import os

        # メモリ使用量測定開始
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 大量のリスク履歴を生成
        for i in range(1000):
            risk_metrics = self.risk_manager.calculate_simplified_risk_metrics(
                self.sample_stock_data, 125.0, 100.0, 1000000.0
            )

        # メモリ使用量測定終了
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # メモリ増加量が合理的であることを確認（100MB以下）
        self.assertLess(memory_increase, 100.0)

    def test_concurrent_access(self):
        """並行アクセステスト"""
        import threading
        import time

        results = []
        errors = []

        def worker(worker_id):
            try:
                for i in range(10):
                    risk_metrics = self.risk_manager.calculate_simplified_risk_metrics(
                        self.sample_stock_data, 125.0, 100.0, 1000000.0
                    )
                    results.append((worker_id, i, risk_metrics.risk_score))
                    time.sleep(0.01)  # 短い待機
            except Exception as e:
                errors.append((worker_id, str(e)))

        # 複数スレッドで同時実行
        threads = []
        for i in range(5):  # 5つのスレッド
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()

        # エラーが発生していないことを確認
        self.assertEqual(len(errors), 0, f"並行アクセスでエラーが発生: {errors}")

        # 結果が生成されていることを確認
        self.assertGreater(len(results), 0)

        # 結果の妥当性確認
        for worker_id, iteration, risk_score in results:
            self.assertGreaterEqual(risk_score, 0)
            self.assertLessEqual(risk_score, 100)


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
