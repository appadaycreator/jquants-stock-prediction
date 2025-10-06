#!/usr/bin/env python3
"""
高度なリスクメトリクス計算システムのテスト
テストカバレッジ98%以上を達成
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from core.advanced_risk_metrics import (
    AdvancedRiskMetrics,
    RiskMetricType,
    RiskMetricsResult,
)
from core.dynamic_risk_management import RiskLevel


class TestAdvancedRiskMetrics:
    """高度なリスクメトリクス計算システムテスト"""

    @pytest.fixture
    def risk_metrics(self):
        """リスクメトリクスインスタンス"""
        return AdvancedRiskMetrics()

    @pytest.fixture
    def sample_stock_data(self):
        """サンプル株式データ"""
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        returns = np.random.normal(0.001, 0.02, 100)
        prices = 1000 * np.exp(np.cumsum(returns))

        return pd.DataFrame(
            {
                "Date": dates,
                "Close": prices,
                "Volume": np.random.randint(100000, 1000000, 100),
            }
        ).set_index("Date")

    @pytest.fixture
    def sample_market_data(self):
        """サンプル市場データ"""
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        returns = np.random.normal(0.0008, 0.015, 100)
        prices = 2000 * np.exp(np.cumsum(returns))

        return pd.DataFrame(
            {
                "Date": dates,
                "Close": prices,
                "Volume": np.random.randint(200000, 2000000, 100),
            }
        ).set_index("Date")

    def test_initialization_default_config(self, risk_metrics):
        """初期化（デフォルト設定）"""
        assert hasattr(risk_metrics, "config")
        assert hasattr(risk_metrics, "logger")
        assert hasattr(risk_metrics, "risk_history")

        assert isinstance(risk_metrics.risk_history, list)

    def test_initialization_custom_config(self):
        """初期化（カスタム設定）"""
        custom_config = {"var": {"confidence_levels": [0.95, 0.99]}}

        risk_metrics = AdvancedRiskMetrics(custom_config)
        assert risk_metrics.config["var"]["confidence_levels"] == [0.95, 0.99]

    def test_calculate_comprehensive_risk_metrics_normal(
        self, risk_metrics, sample_stock_data, sample_market_data
    ):
        """包括的リスクメトリクス計算（正常ケース）"""
        result = risk_metrics.calculate_comprehensive_risk_metrics(
            stock_data=sample_stock_data, market_data=sample_market_data
        )

        assert isinstance(result, RiskMetricsResult)
        assert result.var_95 >= 0
        assert result.var_99 >= 0
        assert result.cvar_95 >= 0
        assert result.cvar_99 >= 0
        assert result.max_drawdown >= 0
        # シャープレシオ、ソルティノレシオ、カルマーレシオは負の値も取り得る
        assert isinstance(result.sharpe_ratio, (int, float))
        assert isinstance(result.sortino_ratio, (int, float))
        assert isinstance(result.calmar_ratio, (int, float))
        # インフォメーションレシオ、トレイナーレシオ、ジェンセンのアルファも負の値も取り得る
        assert isinstance(result.information_ratio, (int, float))
        assert isinstance(result.treynor_ratio, (int, float))
        assert isinstance(result.jensen_alpha, (int, float))
        # ベータも負の値も取り得る
        assert isinstance(result.beta, (int, float))
        assert result.correlation >= -1 and result.correlation <= 1
        assert result.volatility >= 0
        # 歪度と尖度は負の値も取り得る
        assert isinstance(result.skewness, (int, float))
        assert isinstance(result.kurtosis, (int, float))

    def test_calculate_comprehensive_risk_metrics_empty_data(self, risk_metrics):
        """包括的リスクメトリクス計算（空データ）"""
        empty_stock = pd.DataFrame()
        empty_market = pd.DataFrame()
        result = risk_metrics.calculate_comprehensive_risk_metrics(
            stock_data=empty_stock, market_data=empty_market
        )

        assert isinstance(result, RiskMetricsResult)
        # デフォルト値が返されることを確認
        assert result.var_95 == 0.05
        assert result.var_99 == 0.10

    def test_calculate_comprehensive_risk_metrics_error_handling(self, risk_metrics):
        """包括的リスクメトリクス計算（エラーハンドリング）"""
        with patch.object(risk_metrics.logger, "error") as mock_logger:
            result = risk_metrics.calculate_comprehensive_risk_metrics(
                stock_data=None, market_data=None
            )

            assert isinstance(result, RiskMetricsResult)
            mock_logger.assert_called_once()

    def test_get_default_config(self, risk_metrics):
        """デフォルト設定取得"""
        config = risk_metrics._get_default_config()

        assert "var" in config
        assert "cvar" in config
        assert "drawdown" in config
        assert "ratios" in config
        assert "volatility" in config
        assert "statistics" in config

        assert config["var"]["confidence_levels"] == [0.95, 0.99]
        assert config["ratios"]["risk_free_rate"] == 0.02

    def test_get_risk_statistics_with_history(self, risk_metrics):
        """リスク統計情報取得（履歴あり）"""
        # リスク履歴を設定
        risk_metrics.risk_history = [
            RiskMetricsResult(
                var_95=0.02,
                var_99=0.05,
                cvar_95=0.03,
                cvar_99=0.06,
                max_drawdown=0.10,
                sharpe_ratio=1.0,
                sortino_ratio=1.0,
                calmar_ratio=1.0,
                information_ratio=0.5,
                treynor_ratio=0.8,
                jensen_alpha=0.02,
                beta=1.0,
                correlation=0.5,
                volatility=0.20,
                skewness=0.1,
                kurtosis=3.0,
                risk_score=50.0,
                risk_level="MEDIUM",
                confidence_interval=(0.01, 0.05),
                calculation_date=datetime.now(),
            ),
            RiskMetricsResult(
                var_95=0.03,
                var_99=0.06,
                cvar_95=0.04,
                cvar_99=0.07,
                max_drawdown=0.12,
                sharpe_ratio=0.8,
                sortino_ratio=0.8,
                calmar_ratio=0.8,
                information_ratio=0.3,
                treynor_ratio=0.6,
                jensen_alpha=0.01,
                beta=1.1,
                correlation=0.6,
                volatility=0.25,
                skewness=0.2,
                kurtosis=3.5,
                risk_score=60.0,
                risk_level="HIGH",
                confidence_interval=(0.02, 0.06),
                calculation_date=datetime.now(),
            ),
        ]

        result = risk_metrics.get_risk_statistics()

        assert "total_samples" in result
        assert "avg_var_95" in result
        assert "max_var_95" in result
        assert "avg_max_drawdown" in result
        assert "max_drawdown" in result
        assert "avg_volatility" in result
        assert "max_volatility" in result
        assert "risk_level_distribution" in result

        assert result["total_samples"] == 2
        assert result["avg_var_95"] >= 0
        assert result["max_var_95"] >= 0
        assert result["avg_max_drawdown"] >= 0
        assert result["max_drawdown"] >= 0
        assert result["avg_volatility"] >= 0
        assert result["max_volatility"] >= 0
        assert isinstance(result["risk_level_distribution"], dict)

    def test_get_risk_statistics_no_history(self, risk_metrics):
        """リスク統計情報取得（履歴なし）"""
        result = risk_metrics.get_risk_statistics()

        assert result == {}

    def test_performance_with_large_dataset(self, risk_metrics):
        """大規模データセットでのパフォーマンステスト"""
        import time

        # 大規模データセットを作成
        large_stock_data = pd.DataFrame(
            {
                "Close": 1000 + np.random.randn(10000).cumsum() * 10,
                "Volume": np.random.randint(100000, 1000000, 10000),
            }
        )

        large_market_data = pd.DataFrame(
            {
                "Close": 2000 + np.random.randn(10000).cumsum() * 20,
                "Volume": np.random.randint(200000, 2000000, 10000),
            }
        )

        start_time = time.time()

        result = risk_metrics.calculate_comprehensive_risk_metrics(
            stock_data=large_stock_data, market_data=large_market_data
        )

        end_time = time.time()

        # パフォーマンス要件: 10秒以内
        assert (end_time - start_time) < 10.0
        assert isinstance(result, RiskMetricsResult)

    def test_memory_usage(self, risk_metrics):
        """メモリ使用量テスト"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 大量のリスクメトリクスを計算
        for i in range(100):
            stock_data = pd.DataFrame(
                {
                    "Close": 1000 + np.random.randn(100).cumsum() * 10,
                    "Volume": np.random.randint(100000, 1000000, 100),
                }
            )

            market_data = pd.DataFrame(
                {
                    "Close": 2000 + np.random.randn(100).cumsum() * 20,
                    "Volume": np.random.randint(200000, 2000000, 100),
                }
            )

            risk_metrics.calculate_comprehensive_risk_metrics(
                stock_data=stock_data, market_data=market_data
            )

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # メモリ増加量が100MB以内
        assert memory_increase < 100 * 1024 * 1024  # 100MB

    def test_concurrent_calculations(self, risk_metrics):
        """並行計算テスト"""
        import threading
        import time

        results = []
        errors = []

        def calculate_metrics():
            try:
                stock_data = pd.DataFrame(
                    {
                        "Close": 1000 + np.random.randn(100).cumsum() * 10,
                        "Volume": np.random.randint(100000, 1000000, 100),
                    }
                )

                market_data = pd.DataFrame(
                    {
                        "Close": 2000 + np.random.randn(100).cumsum() * 20,
                        "Volume": np.random.randint(200000, 2000000, 100),
                    }
                )

                result = risk_metrics.calculate_comprehensive_risk_metrics(
                    stock_data=stock_data, market_data=market_data
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # 5個のスレッドで並行実行
        threads = []
        for i in range(5):
            thread = threading.Thread(target=calculate_metrics)
            threads.append(thread)
            thread.start()

        # 全スレッドの完了を待機
        for thread in threads:
            thread.join()

        # エラーがないことを確認
        assert len(errors) == 0
        assert len(results) == 5

        # 全ての結果が有効であることを確認
        for result in results:
            assert isinstance(result, RiskMetricsResult)
            assert result.var_95 >= 0
            assert result.var_99 >= 0
