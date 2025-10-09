#!/usr/bin/env python3
"""
高度なリスクメトリクス計算システムの拡張テスト
カバレッジ向上のための追加テストケース
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import numpy as np
import pandas as pd

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.advanced_risk_metrics import (
    AdvancedRiskMetrics,
    RiskMetricType,
    RiskMetricsResult,
)


class TestAdvancedRiskMetricsEnhanced(unittest.TestCase):
    """高度なリスクメトリクス計算システムの拡張テスト"""

    def setUp(self):
        """テスト前準備"""
        self.config = {
            "var": {
                "confidence_levels": [0.95, 0.99],
                "method": "historical",
                "lookback_period": 252,
                "min_observations": 30,
            },
            "cvar": {"confidence_levels": [0.95, 0.99], "method": "historical"},
            "drawdown": {
                "method": "peak_to_trough",
                "min_duration": 1,
                "recovery_threshold": 0.95,
            },
            "ratios": {
                "risk_free_rate": 0.02,
                "benchmark_return": 0.08,
                "benchmark_volatility": 0.15,
            },
            "volatility": {
                "method": "annualized",
                "lookback_period": 252,
                "min_observations": 30,
            },
            "statistics": {
                "skewness_threshold": 0.5,
                "kurtosis_threshold": 3.0,
            },
        }
        self.risk_metrics = AdvancedRiskMetrics(self.config)

    def test_get_default_config(self):
        """デフォルト設定取得テスト"""
        config = self.risk_metrics._get_default_config()
        
        self.assertIsInstance(config, dict)
        self.assertIn("var", config)
        self.assertIn("cvar", config)
        self.assertIn("drawdown", config)
        self.assertIn("ratios", config)
        self.assertIn("volatility", config)
        self.assertIn("statistics", config)

    def test_calculate_var_historical_success(self):
        """VaR計算（ヒストリカル法）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        var_95 = self.risk_metrics._calculate_var_historical(returns, 0.95)
        var_99 = self.risk_metrics._calculate_var_historical(returns, 0.99)
        
        self.assertIsInstance(var_95, float)
        self.assertIsInstance(var_99, float)
        self.assertLess(var_99, var_95)  # 99%VaR < 95%VaR

    def test_calculate_var_historical_insufficient_data(self):
        """VaR計算（ヒストリカル法）データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_var_historical(returns, 0.95)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_var_historical_exception(self):
        """VaR計算（ヒストリカル法）例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('numpy.percentile', side_effect=Exception("Percentile error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_var_historical(returns, 0.95)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_var_parametric_success(self):
        """VaR計算（パラメトリック法）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        var_95 = self.risk_metrics._calculate_var_parametric(returns, 0.95)
        var_99 = self.risk_metrics._calculate_var_parametric(returns, 0.99)
        
        self.assertIsInstance(var_95, float)
        self.assertIsInstance(var_99, float)
        self.assertLess(var_99, var_95)  # 99%VaR < 95%VaR

    def test_calculate_var_parametric_insufficient_data(self):
        """VaR計算（パラメトリック法）データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_var_parametric(returns, 0.95)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_var_parametric_exception(self):
        """VaR計算（パラメトリック法）例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_var_parametric(returns, 0.95)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_var_monte_carlo_success(self):
        """VaR計算（モンテカルロ法）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        var_95 = self.risk_metrics._calculate_var_monte_carlo(returns, 0.95)
        var_99 = self.risk_metrics._calculate_var_monte_carlo(returns, 0.99)
        
        self.assertIsInstance(var_95, float)
        self.assertIsInstance(var_99, float)
        self.assertLess(var_99, var_95)  # 99%VaR < 95%VaR

    def test_calculate_var_monte_carlo_insufficient_data(self):
        """VaR計算（モンテカルロ法）データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_var_monte_carlo(returns, 0.95)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_var_monte_carlo_exception(self):
        """VaR計算（モンテカルロ法）例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('numpy.random.normal', side_effect=Exception("Random error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_var_monte_carlo(returns, 0.95)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_cvar_historical_success(self):
        """CVaR計算（ヒストリカル法）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        cvar_95 = self.risk_metrics._calculate_cvar_historical(returns, 0.95)
        cvar_99 = self.risk_metrics._calculate_cvar_historical(returns, 0.99)
        
        self.assertIsInstance(cvar_95, float)
        self.assertIsInstance(cvar_99, float)
        self.assertLess(cvar_99, cvar_95)  # 99%CVaR < 95%CVaR

    def test_calculate_cvar_historical_insufficient_data(self):
        """CVaR計算（ヒストリカル法）データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_cvar_historical(returns, 0.95)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_cvar_historical_exception(self):
        """CVaR計算（ヒストリカル法）例外処理テスト"""
        returns = np.random.normal(0.001, 0.02, 100)  # 十分なデータポイント
        
        with patch('numpy.percentile', side_effect=Exception("Percentile error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_cvar_historical(returns, 0.95)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_max_drawdown_peak_to_trough_success(self):
        """最大ドローダウン計算（ピーク・トゥ・トラフ法）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        cumulative_returns = np.cumprod(1 + returns)
        
        max_dd = self.risk_metrics._calculate_max_drawdown_peak_to_trough(cumulative_returns)
        
        self.assertIsInstance(max_dd, float)
        self.assertLessEqual(max_dd, 0.0)  # ドローダウンは負の値

    def test_calculate_max_drawdown_peak_to_trough_insufficient_data(self):
        """最大ドローダウン計算（ピーク・トゥ・トラフ法）データ不足テスト"""
        cumulative_returns = np.array([1.0])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_max_drawdown_peak_to_trough(cumulative_returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_max_drawdown_peak_to_trough_exception(self):
        """最大ドローダウン計算（ピーク・トゥ・トラフ法）例外処理テスト"""
        cumulative_returns = np.array([1.0, 1.1, 1.05])
        
        with patch('numpy.maximum.accumulate', side_effect=Exception("Accumulate error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_max_drawdown_peak_to_trough(cumulative_returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_max_drawdown_rolling_success(self):
        """最大ドローダウン計算（ローリング法）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        cumulative_returns = np.cumprod(1 + returns)
        
        max_dd = self.risk_metrics._calculate_max_drawdown_rolling(cumulative_returns)
        
        self.assertIsInstance(max_dd, float)
        self.assertLessEqual(max_dd, 0.0)  # ドローダウンは負の値

    def test_calculate_max_drawdown_rolling_insufficient_data(self):
        """最大ドローダウン計算（ローリング法）データ不足テスト"""
        cumulative_returns = np.array([1.0])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_max_drawdown_rolling(cumulative_returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_max_drawdown_rolling_exception(self):
        """最大ドローダウン計算（ローリング法）例外処理テスト"""
        cumulative_returns = np.array([1.0, 1.1, 1.05])
        
        with patch('pandas.Series.rolling', side_effect=Exception("Rolling error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_max_drawdown_rolling(cumulative_returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_sharpe_ratio_success(self):
        """シャープレシオ計算成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        risk_free_rate = 0.02
        
        sharpe = self.risk_metrics._calculate_sharpe_ratio(returns, risk_free_rate)
        
        self.assertIsInstance(sharpe, float)

    def test_calculate_sharpe_ratio_insufficient_data(self):
        """シャープレシオ計算データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_sharpe_ratio(returns, 0.02)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_sharpe_ratio_exception(self):
        """シャープレシオ計算例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_sharpe_ratio(returns, 0.02)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_sortino_ratio_success(self):
        """ソルティノレシオ計算成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        risk_free_rate = 0.02
        
        sortino = self.risk_metrics._calculate_sortino_ratio(returns, risk_free_rate)
        
        self.assertIsInstance(sortino, float)

    def test_calculate_sortino_ratio_insufficient_data(self):
        """ソルティノレシオ計算データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_sortino_ratio(returns, 0.02)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_sortino_ratio_exception(self):
        """ソルティノレシオ計算例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_sortino_ratio(returns, 0.02)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_calmar_ratio_success(self):
        """カルマーレシオ計算成功テスト"""
        import pandas as pd
        
        returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
        max_drawdown = -0.1
        
        calmar = self.risk_metrics._calculate_calmar_ratio(returns, max_drawdown)
        
        self.assertIsInstance(calmar, float)

    def test_calculate_calmar_ratio_insufficient_data(self):
        """カルマーレシオ計算データ不足テスト"""
        import pandas as pd
        
        returns = pd.Series([0.01, 0.02])  # データ不足
        
        result = self.risk_metrics._calculate_calmar_ratio(returns, -0.1)
        
        self.assertEqual(result, 0.0)  # デフォルト値

    def test_calculate_calmar_ratio_exception(self):
        """カルマーレシオ計算例外処理テスト"""
        import pandas as pd
        
        returns = pd.Series(np.random.normal(0.001, 0.02, 100))  # 十分なデータポイント
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_calmar_ratio(returns, -0.1)
                
                self.assertEqual(result, 0.0)  # デフォルト値
                mock_error.assert_called_once()

    def test_calculate_information_ratio_success(self):
        """インフォメーションレシオ計算成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        benchmark_returns = np.random.normal(0.0008, 0.015, 1000)
        
        info_ratio = self.risk_metrics._calculate_information_ratio(returns, benchmark_returns)
        
        self.assertIsInstance(info_ratio, float)

    def test_calculate_information_ratio_insufficient_data(self):
        """インフォメーションレシオ計算データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        benchmark_returns = np.array([0.008, 0.015])
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_information_ratio(returns, benchmark_returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_information_ratio_exception(self):
        """インフォメーションレシオ計算例外処理テスト"""
        returns = np.array([0.01, 0.02])
        benchmark_returns = np.array([0.008, 0.015])
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_information_ratio(returns, benchmark_returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_treynor_ratio_success(self):
        """トレイノーレシオ計算成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        benchmark_returns = np.random.normal(0.0008, 0.015, 1000)
        risk_free_rate = 0.02
        
        treynor = self.risk_metrics._calculate_treynor_ratio(returns, benchmark_returns, risk_free_rate)
        
        self.assertIsInstance(treynor, float)

    def test_calculate_treynor_ratio_insufficient_data(self):
        """トレイノーレシオ計算データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        benchmark_returns = np.array([0.008, 0.015])
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_treynor_ratio(returns, benchmark_returns, 0.02)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_treynor_ratio_exception(self):
        """トレイノーレシオ計算例外処理テスト"""
        returns = np.array([0.01, 0.02])
        benchmark_returns = np.array([0.008, 0.015])
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_treynor_ratio(returns, benchmark_returns, 0.02)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_jensen_alpha_success(self):
        """ジェンセンのアルファ計算成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        benchmark_returns = np.random.normal(0.0008, 0.015, 1000)
        risk_free_rate = 0.02
        
        alpha = self.risk_metrics._calculate_jensen_alpha(returns, benchmark_returns, risk_free_rate)
        
        self.assertIsInstance(alpha, float)

    def test_calculate_jensen_alpha_insufficient_data(self):
        """ジェンセンのアルファ計算データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        benchmark_returns = np.array([0.008, 0.015])
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_jensen_alpha(returns, benchmark_returns, 0.02)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_jensen_alpha_exception(self):
        """ジェンセンのアルファ計算例外処理テスト"""
        returns = np.array([0.01, 0.02])
        benchmark_returns = np.array([0.008, 0.015])
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_jensen_alpha(returns, benchmark_returns, 0.02)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_beta_success(self):
        """ベータ計算成功テスト"""
        import pandas as pd
        
        dates = pd.date_range('2023-01-01', periods=1000, freq='D')
        returns = pd.Series(np.random.normal(0.001, 0.02, 1000), index=dates)
        benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, 1000), index=dates)
        
        beta = self.risk_metrics._calculate_beta(returns, benchmark_returns)
        
        self.assertIsInstance(beta, float)

    def test_calculate_beta_insufficient_data(self):
        """ベータ計算データ不足テスト"""
        import pandas as pd
        
        returns = pd.Series([0.01, 0.02])  # データ不足
        benchmark_returns = pd.Series([0.008, 0.015])
        
        result = self.risk_metrics._calculate_beta(returns, benchmark_returns)
        
        self.assertEqual(result, 1.0)  # デフォルト値

    def test_calculate_beta_exception(self):
        """ベータ計算例外処理テスト"""
        import pandas as pd
        
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=dates)
        benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, 100), index=dates)
        
        with patch('numpy.cov', side_effect=Exception("Covariance error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_beta(returns, benchmark_returns)
                
                self.assertEqual(result, 1.0)  # デフォルト値
                mock_error.assert_called_once()

    def test_calculate_correlation_success(self):
        """相関係数計算成功テスト"""
        import pandas as pd
        
        returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
        benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, 1000))
        
        correlation = self.risk_metrics._calculate_correlation(returns, benchmark_returns)
        
        self.assertIsInstance(correlation, float)
        self.assertGreaterEqual(correlation, -1.0)
        self.assertLessEqual(correlation, 1.0)

    def test_calculate_correlation_insufficient_data(self):
        """相関係数計算データ不足テスト"""
        import pandas as pd
        
        returns = pd.Series([0.01, 0.02])  # データ不足
        benchmark_returns = pd.Series([0.008, 0.015])
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_correlation(returns, benchmark_returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_correlation_exception(self):
        """相関係数計算例外処理テスト"""
        import pandas as pd
        
        returns = pd.Series(np.random.normal(0.001, 0.02, 100))  # 十分なデータポイント
        benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, 100))
        
        with patch('numpy.corrcoef', side_effect=Exception("Correlation error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_correlation(returns, benchmark_returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_volatility_annualized_success(self):
        """ボラティリティ計算（年率化）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        volatility = self.risk_metrics._calculate_volatility_annualized(returns)
        
        self.assertIsInstance(volatility, float)
        self.assertGreater(volatility, 0.0)

    def test_calculate_volatility_annualized_insufficient_data(self):
        """ボラティリティ計算（年率化）データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_volatility_annualized(returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_volatility_annualized_exception(self):
        """ボラティリティ計算（年率化）例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('numpy.std', side_effect=Exception("Std error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_volatility_annualized(returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_volatility_rolling_success(self):
        """ボラティリティ計算（ローリング）成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        volatility = self.risk_metrics._calculate_volatility_rolling(returns)
        
        self.assertIsInstance(volatility, float)
        self.assertGreater(volatility, 0.0)

    def test_calculate_volatility_rolling_insufficient_data(self):
        """ボラティリティ計算（ローリング）データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_volatility_rolling(returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_volatility_rolling_exception(self):
        """ボラティリティ計算（ローリング）例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('pandas.Series.rolling', side_effect=Exception("Rolling error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_volatility_rolling(returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_skewness_success(self):
        """歪度計算成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        skewness = self.risk_metrics._calculate_skewness(returns)
        
        self.assertIsInstance(skewness, float)

    def test_calculate_skewness_insufficient_data(self):
        """歪度計算データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_skewness(returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_skewness_exception(self):
        """歪度計算例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('scipy.stats.skew', side_effect=Exception("Skew error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_skewness(returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_kurtosis_success(self):
        """尖度計算成功テスト"""
        returns = np.random.normal(0.001, 0.02, 1000)
        
        kurtosis = self.risk_metrics._calculate_kurtosis(returns)
        
        self.assertIsInstance(kurtosis, float)

    def test_calculate_kurtosis_insufficient_data(self):
        """尖度計算データ不足テスト"""
        returns = np.array([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_kurtosis(returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_kurtosis_exception(self):
        """尖度計算例外処理テスト"""
        returns = np.array([0.01, 0.02])
        
        with patch('scipy.stats.kurtosis', side_effect=Exception("Kurtosis error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_kurtosis(returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_risk_score_success(self):
        """リスクスコア計算成功テスト"""
        metrics = {
            'var_95': -0.05,
            'var_99': -0.08,
            'max_drawdown': -0.15,
            'volatility': 0.20,
            'sharpe_ratio': 1.5,
            'sortino_ratio': 2.0,
            'calmar_ratio': 1.2,
        }
        
        risk_score = self.risk_metrics._calculate_risk_score(metrics)
        
        self.assertIsInstance(risk_score, float)
        self.assertGreaterEqual(risk_score, 0.0)
        self.assertLessEqual(risk_score, 100.0)

    def test_calculate_risk_score_exception(self):
        """リスクスコア計算例外処理テスト"""
        metrics = {
            'var_95': -0.05,
            'var_99': -0.08,
            'max_drawdown': -0.15,
            'volatility': 0.20,
            'sharpe_ratio': 1.5,
            'sortino_ratio': 2.0,
            'calmar_ratio': 1.2,
        }
        
        with patch('numpy.mean', side_effect=Exception("Mean error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_risk_score(metrics)
                
                self.assertEqual(result, 50.0)  # デフォルト値
                mock_error.assert_called_once()

    def test_determine_risk_level_success(self):
        """リスクレベル判定成功テスト"""
        # 低リスク
        risk_score_low = 20.0
        risk_level_low = self.risk_metrics._determine_risk_level(risk_score_low)
        self.assertEqual(risk_level_low, "LOW")
        
        # 中リスク
        risk_score_medium = 50.0
        risk_level_medium = self.risk_metrics._determine_risk_level(risk_score_medium)
        self.assertEqual(risk_level_medium, "MEDIUM")
        
        # 高リスク
        risk_score_high = 80.0
        risk_level_high = self.risk_metrics._determine_risk_level(risk_score_high)
        self.assertEqual(risk_level_high, "HIGH")

    def test_calculate_confidence_interval_success(self):
        """信頼区間計算成功テスト"""
        import pandas as pd
        
        returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
        
        ci = self.risk_metrics._calculate_confidence_interval(returns)
        
        self.assertIsInstance(ci, tuple)
        self.assertEqual(len(ci), 2)
        self.assertLess(ci[0], ci[1])

    def test_calculate_confidence_interval_insufficient_data(self):
        """信頼区間計算データ不足テスト"""
        import pandas as pd
        
        returns = pd.Series([0.01, 0.02])  # データ不足
        
        with patch.object(self.risk_metrics.logger, 'warning') as mock_warning:
            result = self.risk_metrics._calculate_confidence_interval(returns)
            
            self.assertIsNone(result)
            mock_warning.assert_called_once()

    def test_calculate_confidence_interval_exception(self):
        """信頼区間計算例外処理テスト"""
        import pandas as pd
        
        returns = pd.Series(np.random.normal(0.001, 0.02, 100))  # 十分なデータポイント
        
        with patch('scipy.stats.t.ppf', side_effect=Exception("t distribution error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics._calculate_confidence_interval(returns)
                
                self.assertIsNone(result)
                mock_error.assert_called_once()

    def test_calculate_comprehensive_metrics_success(self):
        """包括的メトリクス計算成功テスト"""
        import pandas as pd
        
        # テストデータを作成
        dates = pd.date_range('2023-01-01', periods=1000, freq='D')
        stock_data = pd.DataFrame({
            'close': np.random.normal(100, 5, 1000).cumsum() + 10000
        }, index=dates)
        
        market_data = pd.DataFrame({
            'close': np.random.normal(100, 3, 1000).cumsum() + 10000
        }, index=dates)
        
        benchmark_data = pd.DataFrame({
            'close': np.random.normal(100, 2, 1000).cumsum() + 10000
        }, index=dates)
        
        result = self.risk_metrics.calculate_comprehensive_risk_metrics(
            stock_data, market_data, benchmark_data
        )
        
        self.assertIsInstance(result, RiskMetricsResult)
        self.assertIsInstance(result.var_95, float)
        self.assertIsInstance(result.var_99, float)
        self.assertIsInstance(result.cvar_95, float)
        self.assertIsInstance(result.cvar_99, float)
        self.assertIsInstance(result.max_drawdown, float)
        self.assertIsInstance(result.sharpe_ratio, float)
        self.assertIsInstance(result.sortino_ratio, float)
        self.assertIsInstance(result.calmar_ratio, float)
        self.assertIsInstance(result.information_ratio, float)
        self.assertIsInstance(result.treynor_ratio, float)
        self.assertIsInstance(result.jensen_alpha, float)
        self.assertIsInstance(result.beta, float)
        self.assertIsInstance(result.correlation, float)
        self.assertIsInstance(result.volatility, float)
        self.assertIsInstance(result.skewness, float)
        self.assertIsInstance(result.kurtosis, float)
        self.assertIsInstance(result.risk_score, float)
        self.assertIsInstance(result.risk_level, str)
        self.assertIsInstance(result.confidence_interval, tuple)
        self.assertIsInstance(result.calculation_date, datetime)

    def test_calculate_comprehensive_metrics_insufficient_data(self):
        """包括的メトリクス計算データ不足テスト"""
        import pandas as pd
        
        # 空のデータフレーム
        empty_data = pd.DataFrame()
        
        result = self.risk_metrics.calculate_comprehensive_risk_metrics(
            empty_data, empty_data, empty_data
        )
        
        self.assertIsInstance(result, RiskMetricsResult)

    def test_calculate_comprehensive_metrics_exception(self):
        """包括的メトリクス計算例外処理テスト"""
        import pandas as pd
        
        # テストデータを作成
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        stock_data = pd.DataFrame({
            'close': np.random.normal(100, 5, 100).cumsum() + 10000
        }, index=dates)
        
        market_data = pd.DataFrame({
            'close': np.random.normal(100, 3, 100).cumsum() + 10000
        }, index=dates)
        
        with patch.object(self.risk_metrics, '_calculate_var', side_effect=Exception("Var error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result = self.risk_metrics.calculate_comprehensive_risk_metrics(
                    stock_data, market_data
                )
                
                self.assertIsInstance(result, RiskMetricsResult)
                mock_error.assert_called_once()

    def test_get_risk_summary_success(self):
        """リスクサマリー取得成功テスト"""
        # メトリクス結果を作成
        result = RiskMetricsResult(
            var_95=-0.05,
            var_99=-0.08,
            cvar_95=-0.06,
            cvar_99=-0.09,
            max_drawdown=-0.15,
            sharpe_ratio=1.5,
            sortino_ratio=2.0,
            calmar_ratio=1.2,
            information_ratio=0.8,
            treynor_ratio=1.2,
            jensen_alpha=0.02,
            beta=1.1,
            correlation=0.8,
            volatility=0.20,
            skewness=0.1,
            kurtosis=3.2,
            risk_score=30.0,
            risk_level="LOW",
            confidence_interval=(-0.05, 0.05),
            calculation_date=datetime.now(),
        )
        
        summary = self.risk_metrics.get_risk_summary(result)
        
        self.assertIsInstance(summary, dict)
        self.assertIn("risk_level", summary)
        self.assertIn("risk_score", summary)
        self.assertIn("key_metrics", summary)
        self.assertIn("recommendations", summary)

    def test_get_risk_summary_exception(self):
        """リスクサマリー取得例外処理テスト"""
        result = RiskMetricsResult(
            var_95=-0.05,
            var_99=-0.08,
            cvar_95=-0.06,
            cvar_99=-0.09,
            max_drawdown=-0.15,
            sharpe_ratio=1.5,
            sortino_ratio=2.0,
            calmar_ratio=1.2,
            information_ratio=0.8,
            treynor_ratio=1.2,
            jensen_alpha=0.02,
            beta=1.1,
            correlation=0.8,
            volatility=0.20,
            skewness=0.1,
            kurtosis=3.2,
            risk_score=30.0,
            risk_level="LOW",
            confidence_interval=(-0.05, 0.05),
            calculation_date=datetime.now(),
        )
        
        with patch.object(self.risk_metrics, '_determine_risk_level', side_effect=Exception("Risk level error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result_summary = self.risk_metrics.get_risk_summary(result)
                
                self.assertEqual(result_summary["status"], "error")
                self.assertIn("error", result_summary)
                mock_error.assert_called_once()

    def test_export_risk_report_success(self):
        """リスクレポート出力成功テスト"""
        # メトリクス結果を作成
        result = RiskMetricsResult(
            var_95=-0.05,
            var_99=-0.08,
            cvar_95=-0.06,
            cvar_99=-0.09,
            max_drawdown=-0.15,
            sharpe_ratio=1.5,
            sortino_ratio=2.0,
            calmar_ratio=1.2,
            information_ratio=0.8,
            treynor_ratio=1.2,
            jensen_alpha=0.02,
            beta=1.1,
            correlation=0.8,
            volatility=0.20,
            skewness=0.1,
            kurtosis=3.2,
            risk_score=30.0,
            risk_level="LOW",
            confidence_interval=(-0.05, 0.05),
            calculation_date=datetime.now(),
        )
        
        report = self.risk_metrics.export_risk_report(result)
        
        self.assertIsInstance(report, dict)
        self.assertIn("report_type", report)
        self.assertIn("calculation_date", report)
        self.assertIn("risk_metrics", report)
        self.assertIn("risk_summary", report)
        self.assertIn("recommendations", report)

    def test_export_risk_report_exception(self):
        """リスクレポート出力例外処理テスト"""
        result = RiskMetricsResult(
            var_95=-0.05,
            var_99=-0.08,
            cvar_95=-0.06,
            cvar_99=-0.09,
            max_drawdown=-0.15,
            sharpe_ratio=1.5,
            sortino_ratio=2.0,
            calmar_ratio=1.2,
            information_ratio=0.8,
            treynor_ratio=1.2,
            jensen_alpha=0.02,
            beta=1.1,
            correlation=0.8,
            volatility=0.20,
            skewness=0.1,
            kurtosis=3.2,
            risk_score=30.0,
            risk_level="LOW",
            confidence_interval=(-0.05, 0.05),
            calculation_date=datetime.now(),
        )
        
        with patch.object(self.risk_metrics, 'get_risk_summary', side_effect=Exception("Summary error")):
            with patch.object(self.risk_metrics.logger, 'error') as mock_error:
                result_report = self.risk_metrics.export_risk_report(result)
                
                self.assertIn("error", result_report)
                mock_error.assert_called_once()


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
