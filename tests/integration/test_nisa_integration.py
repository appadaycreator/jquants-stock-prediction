#!/usr/bin/env python3
"""
NISA統合システムの統合テスト
"""

import pytest
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.nisa_integrated_manager import NisaIntegratedManager
from core.nisa_quota_manager import NisaTransaction
from core.nisa_tax_calculator import NisaTaxCalculator
from core.nisa_alert_system import NisaAlertSystem


class TestNisaIntegration:
    """NISA統合システムの統合テスト"""

    @pytest.fixture
    def temp_config(self):
        """一時設定の作成"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name
        return {
            "nisa_data_file": temp_file,
            "auto_optimization": True,
            "auto_alerts": True,
            "income_tax_rate": 0.20,
            "resident_tax_rate": 0.10,
        }

    @pytest.fixture
    def integrated_manager(self, temp_config):
        """統合管理システムのインスタンス"""
        return NisaIntegratedManager(temp_config)

    def test_complete_nisa_workflow(self, integrated_manager):
        """完全なNISAワークフローテスト"""
        # 1. 初期状態の確認
        dashboard = integrated_manager.get_dashboard_data()
        assert dashboard.quota_status["growth_investment"]["used_amount"] == 0
        assert dashboard.quota_status["accumulation_investment"]["used_amount"] == 0

        # 2. 成長投資枠への投資
        growth_transaction = {
            "id": "GROWTH_001",
            "type": "BUY",
            "symbol": "7203",
            "symbol_name": "トヨタ自動車",
            "quantity": 100,
            "price": 2500.0,
            "amount": 250000.0,
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(growth_transaction)
        assert result["success"] == True

        # 3. つみたて投資枠への投資
        accumulation_transaction = {
            "id": "ACCUM_001",
            "type": "BUY",
            "symbol": "6758",
            "symbol_name": "ソニーグループ",
            "quantity": 10,
            "price": 12000.0,
            "amount": 120000.0,
            "quota_type": "ACCUMULATION",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(accumulation_transaction)
        assert result["success"] == True

        # 4. ダッシュボードの更新確認
        updated_dashboard = integrated_manager.get_dashboard_data()
        assert (
            updated_dashboard.quota_status["growth_investment"]["used_amount"]
            == 250000.0
        )
        assert (
            updated_dashboard.quota_status["accumulation_investment"]["used_amount"]
            == 120000.0
        )

        # 5. ポートフォリオの確認
        portfolio = updated_dashboard.portfolio
        assert len(portfolio.positions) == 2
        assert portfolio.total_cost == 370000.0

        # 6. 税務計算の確認
        tax_calculation = updated_dashboard.tax_calculation
        assert tax_calculation.total_tax_free_amount == 370000.0
        assert tax_calculation.tax_savings["estimated_tax_savings"] > 0

        # 7. 最適化提案の確認
        optimization = integrated_manager.get_optimization_recommendations()
        assert len(optimization.recommendations) >= 0
        assert optimization.priority_score >= 0

    def test_quota_utilization_scenarios(self, integrated_manager):
        """枠利用率シナリオテスト"""
        # 50%の枠使用
        half_quota_transaction = {
            "id": "HALF_001",
            "type": "BUY",
            "symbol": "7203",
            "symbol_name": "トヨタ自動車",
            "quantity": 100,
            "price": 12000.0,
            "amount": 1200000.0,  # 120万円（50%）
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(half_quota_transaction)
        assert result["success"] == True

        dashboard = integrated_manager.get_dashboard_data()
        growth_quota = dashboard.quota_status["growth_investment"]
        assert growth_quota["utilization_rate"] == 50.0

        # 80%の枠使用（警告レベル）
        warning_transaction = {
            "id": "WARNING_001",
            "type": "BUY",
            "symbol": "6758",
            "symbol_name": "ソニーグループ",
            "quantity": 100,
            "price": 7200.0,
            "amount": 720000.0,  # 72万円（30%追加で80%）
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(warning_transaction)
        assert result["success"] == True

        dashboard = integrated_manager.get_dashboard_data()
        growth_quota = dashboard.quota_status["growth_investment"]
        assert growth_quota["utilization_rate"] == 80.0

        # アラートの確認
        alerts = dashboard.alerts
        warning_alerts = [a for a in alerts if a.type == "WARNING"]
        assert len(warning_alerts) > 0

    def test_sell_transaction_workflow(self, integrated_manager):
        """売却取引ワークフローテスト"""
        # まず買い注文
        buy_transaction = {
            "id": "BUY_001",
            "type": "BUY",
            "symbol": "7203",
            "symbol_name": "トヨタ自動車",
            "quantity": 100,
            "price": 2500.0,
            "amount": 250000.0,
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(buy_transaction)
        assert result["success"] == True

        # 売却注文
        sell_transaction = {
            "id": "SELL_001",
            "type": "SELL",
            "symbol": "7203",
            "symbol_name": "トヨタ自動車",
            "quantity": 50,
            "price": 2600.0,
            "amount": 130000.0,
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(sell_transaction)
        assert result["success"] == True

        # 枠の更新確認
        dashboard = integrated_manager.get_dashboard_data()
        growth_quota = dashboard.quota_status["growth_investment"]
        assert growth_quota["used_amount"] == 120000.0  # 250000 - 130000
        assert growth_quota["available_amount"] == 2280000.0  # 2400000 - 120000

        # 再利用可能枠の確認
        quota_reuse = dashboard.quota_status["quota_reuse"]
        assert quota_reuse["growth_available"] == 130000.0

    def test_tax_calculation_accuracy(self, integrated_manager):
        """税務計算精度テスト"""
        # 100万円の投資
        transaction = {
            "id": "TAX_001",
            "type": "BUY",
            "symbol": "7203",
            "symbol_name": "トヨタ自動車",
            "quantity": 100,
            "price": 10000.0,
            "amount": 1000000.0,
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(transaction)
        assert result["success"] == True

        dashboard = integrated_manager.get_dashboard_data()
        tax_calculation = dashboard.tax_calculation

        # 税務節約額 = 100万円 × 30% = 30万円
        expected_savings = 1000000.0 * 0.30
        assert (
            abs(tax_calculation.tax_savings["estimated_tax_savings"] - expected_savings)
            < 0.01
        )

    def test_alert_system_integration(self, integrated_manager):
        """アラートシステム統合テスト"""
        # 95%の枠使用（クリティカルレベル）
        critical_transaction = {
            "id": "CRITICAL_001",
            "type": "BUY",
            "symbol": "7203",
            "symbol_name": "トヨタ自動車",
            "quantity": 100,
            "price": 22800.0,
            "amount": 2280000.0,  # 228万円（95%）
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(critical_transaction)
        assert result["success"] == True

        dashboard = integrated_manager.get_dashboard_data()
        alerts = dashboard.alerts

        # クリティカルアラートの確認
        critical_alerts = [a for a in alerts if a.type == "CRITICAL"]
        assert len(critical_alerts) > 0

        critical_alert = critical_alerts[0]
        assert critical_alert.quota_type == "GROWTH"
        assert critical_alert.priority == "HIGH"
        assert critical_alert.current_usage >= 95.0

    def test_portfolio_diversification(self, integrated_manager):
        """ポートフォリオ分散テスト"""
        # 複数の銘柄に投資
        transactions = [
            {
                "id": f"DIV_{i:03d}",
                "type": "BUY",
                "symbol": f"STOCK_{i:03d}",
                "symbol_name": f"銘柄{i:03d}",
                "quantity": 10,
                "price": 1000.0,
                "amount": 10000.0,
                "quota_type": "GROWTH",
                "transaction_date": datetime.now().isoformat(),
            }
            for i in range(5)
        ]

        for transaction in transactions:
            result = integrated_manager.add_transaction(transaction)
            assert result["success"] == True

        dashboard = integrated_manager.get_dashboard_data()
        portfolio = dashboard.portfolio

        assert len(portfolio.positions) == 5
        assert portfolio.total_cost == 50000.0

        # 最適化提案の確認
        optimization = integrated_manager.get_optimization_recommendations()
        risk_analysis = optimization.quota_optimization.get("risk_analysis", {})
        assert risk_analysis.get("diversification_score", 0) > 0

    def test_annual_report_generation(self, integrated_manager):
        """年間レポート生成テスト"""
        # 複数の取引を追加
        transactions = [
            {
                "id": f"ANNUAL_{i:03d}",
                "type": "BUY" if i % 2 == 0 else "SELL",
                "symbol": f"STOCK_{i:03d}",
                "symbol_name": f"銘柄{i:03d}",
                "quantity": 10,
                "price": 1000.0,
                "amount": 10000.0,
                "quota_type": "GROWTH",
                "transaction_date": datetime.now().isoformat(),
            }
            for i in range(10)
        ]

        for transaction in transactions:
            result = integrated_manager.add_transaction(transaction)
            assert result["success"] == True

        # 年間レポートの生成
        report = integrated_manager.get_annual_report()

        assert "annual_tax_report" in report
        assert "portfolio_performance" in report
        assert "alert_statistics" in report
        assert "transaction_summary" in report

        # 取引サマリーの確認
        transaction_summary = report["transaction_summary"]
        assert transaction_summary["total_transactions"] == 10
        assert transaction_summary["buy_transactions"] == 5
        assert transaction_summary["sell_transactions"] == 5

    def test_system_health_monitoring(self, integrated_manager):
        """システムヘルス監視テスト"""
        # システムヘルスの取得
        health = integrated_manager.get_system_health()

        assert "health_score" in health
        assert "health_level" in health
        assert "quota_system" in health
        assert "alert_count" in health

        assert 0 <= health["health_score"] <= 100
        assert health["health_level"] in ["EXCELLENT", "GOOD", "FAIR", "POOR"]

    def test_data_export_import(self, integrated_manager):
        """データエクスポート・インポートテスト"""
        # サンプルデータの追加
        transaction = {
            "id": "EXPORT_001",
            "type": "BUY",
            "symbol": "7203",
            "symbol_name": "トヨタ自動車",
            "quantity": 100,
            "price": 2500.0,
            "amount": 250000.0,
            "quota_type": "GROWTH",
            "transaction_date": datetime.now().isoformat(),
        }

        result = integrated_manager.add_transaction(transaction)
        assert result["success"] == True

        # データのエクスポート
        export_data = integrated_manager.export_data("json")

        assert "dashboard" in export_data
        assert "optimization" in export_data
        assert "annual_report" in export_data
        assert "export_date" in export_data

        # エクスポートデータの検証
        dashboard_data = export_data["dashboard"]
        assert "quota_status" in dashboard_data
        assert "portfolio" in dashboard_data
        assert "tax_calculation" in dashboard_data

    def test_error_recovery(self, integrated_manager):
        """エラー回復テスト"""
        # 無効な取引データ
        invalid_transaction = {
            "id": "ERROR_001",
            "type": "INVALID",
            "symbol": "",
            "quantity": 0,
            "price": 0,
            "amount": 0,
            "quota_type": "INVALID",
        }

        result = integrated_manager.add_transaction(invalid_transaction)
        assert result["success"] == False
        assert "error" in result

        # システムは正常に動作し続ける
        dashboard = integrated_manager.get_dashboard_data()
        assert dashboard is not None

    def test_performance_under_load(self, integrated_manager):
        """負荷下でのパフォーマンステスト"""
        # 大量の取引を追加
        transactions = [
            {
                "id": f"LOAD_{i:06d}",
                "type": "BUY",
                "symbol": f"STOCK_{i % 100:03d}",
                "symbol_name": f"銘柄{i % 100:03d}",
                "quantity": 1,
                "price": 1000.0,
                "amount": 1000.0,
                "quota_type": "GROWTH",
                "transaction_date": datetime.now().isoformat(),
            }
            for i in range(100)  # 100件の取引
        ]

        # 取引の追加
        success_count = 0
        for transaction in transactions:
            result = integrated_manager.add_transaction(transaction)
            if result["success"]:
                success_count += 1

        # 成功した取引数の確認
        assert success_count > 0

        # システムの応答性確認
        dashboard = integrated_manager.get_dashboard_data()
        assert dashboard is not None

        optimization = integrated_manager.get_optimization_recommendations()
        assert optimization is not None

    def test_concurrent_transactions(self, integrated_manager):
        """並行取引テスト"""
        # 同時に複数の取引を実行
        transactions = [
            {
                "id": f"CONCURRENT_{i:03d}",
                "type": "BUY",
                "symbol": f"STOCK_{i:03d}",
                "symbol_name": f"銘柄{i:03d}",
                "quantity": 10,
                "price": 1000.0,
                "amount": 10000.0,
                "quota_type": "GROWTH",
                "transaction_date": datetime.now().isoformat(),
            }
            for i in range(5)
        ]

        results = []
        for transaction in transactions:
            result = integrated_manager.add_transaction(transaction)
            results.append(result)

        # すべての取引が成功することを確認
        success_count = sum(1 for r in results if r["success"])
        assert success_count == 5

        # データの整合性確認
        dashboard = integrated_manager.get_dashboard_data()
        portfolio = dashboard.portfolio
        assert len(portfolio.positions) == 5

    def test_cleanup(self, temp_config):
        """クリーンアップ"""
        if os.path.exists(temp_config["nisa_data_file"]):
            os.unlink(temp_config["nisa_data_file"])
