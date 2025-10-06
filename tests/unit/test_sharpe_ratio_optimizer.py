"""
シャープレシオ最適化システムのテスト
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.sharpe_ratio_optimizer import SharpeRatioOptimizer, SharpeOptimizationResult, OptimizationConstraints

class TestSharpeRatioOptimizer:
    """シャープレシオ最適化システムのテスト"""
    
    @pytest.fixture
    def optimizer(self):
        """最適化システムのフィクスチャ"""
        config = {
            'risk_free_rate': 0.02,
            'max_iterations': 100,
            'tolerance': 1e-6,
            'max_position_weight': 0.2,
            'min_position_weight': 0.01,
            'max_sector_weight': 0.3,
            'max_correlation': 0.7,
            'max_volatility': 0.5,
            'min_liquidity': 1000000,
            'max_turnover': 0.5,
            'transaction_costs': 0.001
        }
        return SharpeRatioOptimizer(config)
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """サンプルポートフォリオデータ"""
        return {
            'total_value': 1000000,
            'positions': {
                'AAPL': {
                    'weight': 0.3,
                    'price_data': [
                        {'close': 145.0, 'volume': 1000000},
                        {'close': 147.0, 'volume': 1100000},
                        {'close': 150.0, 'volume': 1200000},
                        {'close': 152.0, 'volume': 1300000},
                        {'close': 155.0, 'volume': 1400000}
                    ],
                    'sector': 'Technology',
                    'market_cap': 2500000000000,
                    'liquidity_score': 1000000
                },
                'GOOGL': {
                    'weight': 0.25,
                    'price_data': [
                        {'close': 2750.0, 'volume': 500000},
                        {'close': 2780.0, 'volume': 550000},
                        {'close': 2800.0, 'volume': 600000},
                        {'close': 2820.0, 'volume': 650000},
                        {'close': 2850.0, 'volume': 700000}
                    ],
                    'sector': 'Technology',
                    'market_cap': 1800000000000,
                    'liquidity_score': 500000
                },
                'MSFT': {
                    'weight': 0.2,
                    'price_data': [
                        {'close': 295.0, 'volume': 800000},
                        {'close': 298.0, 'volume': 850000},
                        {'close': 300.0, 'volume': 900000},
                        {'close': 302.0, 'volume': 950000},
                        {'close': 305.0, 'volume': 1000000}
                    ],
                    'sector': 'Technology',
                    'market_cap': 2200000000000,
                    'liquidity_score': 800000
                },
                'AMZN': {
                    'weight': 0.15,
                    'price_data': [
                        {'close': 3200.0, 'volume': 300000},
                        {'close': 3250.0, 'volume': 350000},
                        {'close': 3300.0, 'volume': 400000},
                        {'close': 3350.0, 'volume': 450000},
                        {'close': 3400.0, 'volume': 500000}
                    ],
                    'sector': 'Consumer Discretionary',
                    'market_cap': 1500000000000,
                    'liquidity_score': 700000
                },
                'TSLA': {
                    'weight': 0.1,
                    'price_data': [
                        {'close': 200.0, 'volume': 2000000},
                        {'close': 205.0, 'volume': 2100000},
                        {'close': 210.0, 'volume': 2200000},
                        {'close': 215.0, 'volume': 2300000},
                        {'close': 220.0, 'volume': 2400000}
                    ],
                    'sector': 'Consumer Discretionary',
                    'market_cap': 800000000000,
                    'liquidity_score': 600000
                }
            }
        }
    
    @pytest.fixture
    def sample_market_data(self):
        """サンプル市場データ"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        return pd.DataFrame({
            'Date': dates,
            'Close': np.random.normal(100, 10, 100),
            'Volume': np.random.normal(1000000, 100000, 100)
        })
    
    def test_initialization(self, optimizer):
        """初期化テスト"""
        assert optimizer.target_improvement == 0.20  # 20%向上目標
        assert optimizer.risk_free_rate == 0.02
        assert optimizer.max_iterations == 100
        assert optimizer.tolerance == 1e-6
        
        # 制約条件の確認
        assert optimizer.constraints.max_position_weight == 0.2
        assert optimizer.constraints.min_position_weight == 0.01
        assert optimizer.constraints.max_sector_weight == 0.3
        assert optimizer.constraints.max_correlation == 0.7
        assert optimizer.constraints.max_volatility == 0.5
        assert optimizer.constraints.min_liquidity == 1000000
        assert optimizer.constraints.max_turnover == 0.5
        assert optimizer.constraints.transaction_costs == 0.001
    
    def test_get_default_config(self, optimizer):
        """デフォルト設定取得テスト"""
        config = optimizer._get_default_config()
        assert 'risk_free_rate' in config
        assert 'max_iterations' in config
        assert 'tolerance' in config
        assert 'max_position_weight' in config
        assert 'min_position_weight' in config
        assert 'max_sector_weight' in config
        assert 'max_correlation' in config
        assert 'max_volatility' in config
        assert 'min_liquidity' in config
        assert 'max_turnover' in config
        assert 'transaction_costs' in config
        assert 'optimization_methods' in config
        assert 'rebalancing_frequency' in config
        assert 'lookback_period' in config
        assert 'volatility_target' in config
        assert 'correlation_threshold' in config
    
    def test_preprocess_portfolio_data(self, optimizer, sample_portfolio_data, sample_market_data):
        """ポートフォリオデータ前処理テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        
        assert 'symbols' in processed_data
        assert 'weights' in processed_data
        assert 'returns' in processed_data
        assert 'volatilities' in processed_data
        assert 'sectors' in processed_data
        assert 'market_caps' in processed_data
        assert 'liquidity_scores' in processed_data
        assert 'correlations' in processed_data
        
        assert len(processed_data['symbols']) == 5
        assert len(processed_data['weights']) == 5
        assert len(processed_data['returns']) == 5
        assert len(processed_data['volatilities']) == 5
        assert len(processed_data['sectors']) == 5
        assert len(processed_data['market_caps']) == 5
        assert len(processed_data['liquidity_scores']) == 5
    
    def test_calculate_current_sharpe_ratio(self, optimizer, sample_portfolio_data, sample_market_data):
        """現在のシャープレシオ計算テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        sharpe_ratio = optimizer._calculate_current_sharpe_ratio(processed_data)
        
        assert isinstance(sharpe_ratio, float)
        assert np.isfinite(sharpe_ratio)
        assert sharpe_ratio >= 0.0
    
    def test_optimize_max_sharpe(self, optimizer, sample_portfolio_data, sample_market_data):
        """最大シャープレシオ最適化テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        result = optimizer._optimize_max_sharpe(processed_data)
        
        assert isinstance(result, dict)
        assert 'weights' in result
        assert 'sharpe_ratio' in result
        assert 'convergence' in result
        assert 'iterations' in result
        
        assert isinstance(result['weights'], dict)
        assert isinstance(result['sharpe_ratio'], float)
        assert isinstance(result['convergence'], bool)
        assert isinstance(result['iterations'], int)
        
        assert result['sharpe_ratio'] >= 0.0
        assert result['iterations'] >= 0
    
    def test_optimize_mean_variance(self, optimizer, sample_portfolio_data, sample_market_data):
        """平均分散最適化テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        result = optimizer._optimize_mean_variance(processed_data)
        
        assert isinstance(result, dict)
        assert 'weights' in result
        assert 'sharpe_ratio' in result
        assert 'convergence' in result
        assert 'iterations' in result
        
        assert isinstance(result['weights'], dict)
        assert isinstance(result['sharpe_ratio'], float)
        assert isinstance(result['convergence'], bool)
        assert isinstance(result['iterations'], int)
        
        assert result['sharpe_ratio'] >= 0.0
        assert result['iterations'] >= 0
    
    def test_optimize_black_litterman(self, optimizer, sample_portfolio_data, sample_market_data):
        """ブラック・リッターマン最適化テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        result = optimizer._optimize_black_litterman(processed_data, sample_market_data)
        
        assert isinstance(result, dict)
        assert 'weights' in result
        assert 'sharpe_ratio' in result
        assert 'convergence' in result
        assert 'iterations' in result
        
        assert isinstance(result['weights'], dict)
        assert isinstance(result['sharpe_ratio'], float)
        assert isinstance(result['convergence'], bool)
        assert isinstance(result['iterations'], int)
        
        assert result['sharpe_ratio'] >= 0.0
        assert result['iterations'] >= 0
    
    def test_optimize_risk_parity(self, optimizer, sample_portfolio_data, sample_market_data):
        """リスクパリティ最適化テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        result = optimizer._optimize_risk_parity(processed_data)
        
        assert isinstance(result, dict)
        assert 'weights' in result
        assert 'sharpe_ratio' in result
        assert 'convergence' in result
        assert 'iterations' in result
        
        assert isinstance(result['weights'], dict)
        assert isinstance(result['sharpe_ratio'], float)
        assert isinstance(result['convergence'], bool)
        assert isinstance(result['iterations'], int)
        
        assert result['sharpe_ratio'] >= 0.0
        assert result['iterations'] >= 0
    
    def test_optimize_min_variance(self, optimizer, sample_portfolio_data, sample_market_data):
        """最小分散最適化テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        result = optimizer._optimize_min_variance(processed_data)
        
        assert isinstance(result, dict)
        assert 'weights' in result
        assert 'sharpe_ratio' in result
        assert 'convergence' in result
        assert 'iterations' in result
        
        assert isinstance(result['weights'], dict)
        assert isinstance(result['sharpe_ratio'], float)
        assert isinstance(result['convergence'], bool)
        assert isinstance(result['iterations'], int)
        
        assert result['sharpe_ratio'] >= 0.0
        assert result['iterations'] >= 0
    
    def test_optimize_equal_risk_contribution(self, optimizer, sample_portfolio_data, sample_market_data):
        """等リスク寄与最適化テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        result = optimizer._optimize_equal_risk_contribution(processed_data)
        
        assert isinstance(result, dict)
        assert 'weights' in result
        assert 'sharpe_ratio' in result
        assert 'convergence' in result
        assert 'iterations' in result
        
        assert isinstance(result['weights'], dict)
        assert isinstance(result['sharpe_ratio'], float)
        assert isinstance(result['convergence'], bool)
        assert isinstance(result['iterations'], int)
        
        assert result['sharpe_ratio'] >= 0.0
        assert result['iterations'] >= 0
    
    def test_calculate_expected_returns(self, optimizer, sample_portfolio_data, sample_market_data):
        """期待リターン計算テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        expected_returns = optimizer._calculate_expected_returns(processed_data)
        
        assert isinstance(expected_returns, np.ndarray)
        assert len(expected_returns) == 5
        assert np.all(np.isfinite(expected_returns))
    
    def test_calculate_covariance_matrix(self, optimizer, sample_portfolio_data, sample_market_data):
        """共分散行列計算テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        cov_matrix = optimizer._calculate_covariance_matrix(processed_data)
        
        assert isinstance(cov_matrix, np.ndarray)
        assert cov_matrix.shape == (5, 5)  # 5x5正方行列
        assert np.all(np.isfinite(cov_matrix))
        
        # 対称行列であることを確認
        assert np.allclose(cov_matrix, cov_matrix.T)
        
        # 正定値行列であることを確認（固有値が正）
        eigenvalues = np.linalg.eigvals(cov_matrix)
        assert np.all(eigenvalues > 0)
    
    def test_ensure_positive_definite(self, optimizer):
        """正定値行列確保テスト"""
        matrix = np.array([[1.0, 0.5], [0.5, 1.0]])
        result = optimizer._ensure_positive_definite(matrix)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == matrix.shape
        
        # 固有値が正であることを確認
        eigenvalues = np.linalg.eigvals(result)
        assert np.all(eigenvalues > 0)
    
    def test_calculate_black_litterman_returns(self, optimizer, sample_portfolio_data, sample_market_data):
        """ブラック・リッターマン期待リターン計算テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        expected_returns = optimizer._calculate_expected_returns(processed_data)
        market_weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        
        bl_returns = optimizer._calculate_black_litterman_returns(
            expected_returns, processed_data, market_weights
        )
        
        assert isinstance(bl_returns, np.ndarray)
        assert len(bl_returns) == 5
        assert np.all(np.isfinite(bl_returns))
    
    def test_optimize_max_sharpe_with_returns(self, optimizer, sample_portfolio_data, sample_market_data):
        """指定された期待リターンで最大シャープレシオ最適化テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        expected_returns = np.array([0.08, 0.09, 0.07, 0.06, 0.05])
        
        result = optimizer._optimize_max_sharpe_with_returns(processed_data, expected_returns)
        
        assert isinstance(result, dict)
        assert 'weights' in result
        assert 'sharpe_ratio' in result
        assert 'convergence' in result
        assert 'iterations' in result
        
        assert isinstance(result['weights'], dict)
        assert isinstance(result['sharpe_ratio'], float)
        assert isinstance(result['convergence'], bool)
        assert isinstance(result['iterations'], int)
        
        assert result['sharpe_ratio'] >= 0.0
        assert result['iterations'] >= 0
    
    def test_calculate_risk_metrics(self, optimizer, sample_portfolio_data, sample_market_data):
        """リスクメトリクス計算テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        optimization_result = {
            'weights': {'AAPL': 0.3, 'GOOGL': 0.25, 'MSFT': 0.2, 'AMZN': 0.15, 'TSLA': 0.1},
            'sharpe_ratio': 1.5
        }
        
        risk_metrics = optimizer._calculate_risk_metrics(optimization_result, processed_data)
        
        assert isinstance(risk_metrics, dict)
        assert 'portfolio_volatility' in risk_metrics
        assert 'var_95' in risk_metrics
        assert 'var_99' in risk_metrics
        assert 'max_drawdown' in risk_metrics
        assert 'sharpe_ratio' in risk_metrics
        
        assert isinstance(risk_metrics['portfolio_volatility'], float)
        assert isinstance(risk_metrics['var_95'], float)
        assert isinstance(risk_metrics['var_99'], float)
        assert isinstance(risk_metrics['max_drawdown'], float)
        assert isinstance(risk_metrics['sharpe_ratio'], float)
        
        assert risk_metrics['portfolio_volatility'] >= 0.0
        assert risk_metrics['max_drawdown'] >= 0.0
        assert risk_metrics['sharpe_ratio'] >= 0.0
        assert np.isfinite(risk_metrics['portfolio_volatility'])
        assert np.isfinite(risk_metrics['var_95'])
        assert np.isfinite(risk_metrics['var_99'])
        assert np.isfinite(risk_metrics['max_drawdown'])
        assert np.isfinite(risk_metrics['sharpe_ratio'])
    
    def test_calculate_performance_metrics(self, optimizer, sample_portfolio_data, sample_market_data):
        """パフォーマンスメトリクス計算テスト"""
        processed_data = optimizer._preprocess_portfolio_data(sample_portfolio_data, sample_market_data, None)
        optimization_result = {
            'weights': {'AAPL': 0.3, 'GOOGL': 0.25, 'MSFT': 0.2, 'AMZN': 0.15, 'TSLA': 0.1},
            'sharpe_ratio': 1.5
        }
        
        performance_metrics = optimizer._calculate_performance_metrics(optimization_result, processed_data)
        
        assert isinstance(performance_metrics, dict)
        assert 'portfolio_return' in performance_metrics
        assert 'portfolio_volatility' in performance_metrics
        assert 'sharpe_ratio' in performance_metrics
        assert 'sortino_ratio' in performance_metrics
        assert 'calmar_ratio' in performance_metrics
        
        assert isinstance(performance_metrics['portfolio_return'], float)
        assert isinstance(performance_metrics['portfolio_volatility'], float)
        assert isinstance(performance_metrics['sharpe_ratio'], float)
        assert isinstance(performance_metrics['sortino_ratio'], float)
        assert isinstance(performance_metrics['calmar_ratio'], float)
        
        assert performance_metrics['portfolio_volatility'] >= 0.0
        assert performance_metrics['sharpe_ratio'] >= 0.0
        assert performance_metrics['sortino_ratio'] >= 0.0
        assert performance_metrics['calmar_ratio'] >= 0.0
        assert np.isfinite(performance_metrics['portfolio_return'])
        assert np.isfinite(performance_metrics['portfolio_volatility'])
        assert np.isfinite(performance_metrics['sharpe_ratio'])
        assert np.isfinite(performance_metrics['sortino_ratio'])
        assert np.isfinite(performance_metrics['calmar_ratio'])
    
    def test_optimize_sharpe_ratio_integration(self, optimizer, sample_portfolio_data, sample_market_data):
        """シャープレシオ最適化統合テスト"""
        result = optimizer.optimize_sharpe_ratio(
            sample_portfolio_data, sample_market_data, None, 'max_sharpe'
        )
        
        assert isinstance(result, SharpeOptimizationResult)
        assert hasattr(result, 'original_sharpe')
        assert hasattr(result, 'optimized_sharpe')
        assert hasattr(result, 'improvement_ratio')
        assert hasattr(result, 'target_achieved')
        assert hasattr(result, 'optimization_method')
        assert hasattr(result, 'portfolio_weights')
        assert hasattr(result, 'risk_metrics')
        assert hasattr(result, 'performance_metrics')
        assert hasattr(result, 'optimization_timestamp')
        assert hasattr(result, 'convergence_success')
        assert hasattr(result, 'iterations')
        
        assert isinstance(result.original_sharpe, float)
        assert isinstance(result.optimized_sharpe, float)
        assert isinstance(result.improvement_ratio, float)
        assert isinstance(result.target_achieved, bool)
        assert isinstance(result.optimization_method, str)
        assert isinstance(result.portfolio_weights, dict)
        assert isinstance(result.risk_metrics, dict)
        assert isinstance(result.performance_metrics, dict)
        assert isinstance(result.optimization_timestamp, str)
        assert isinstance(result.convergence_success, bool)
        assert isinstance(result.iterations, int)
        
        assert result.original_sharpe >= 0.0
        assert result.optimized_sharpe >= 0.0
        assert result.improvement_ratio >= -1.0  # 改善率は-100%以上
        assert result.optimization_method == 'max_sharpe'
        assert len(result.portfolio_weights) == 5
        assert result.iterations >= 0
        assert np.isfinite(result.original_sharpe)
        assert np.isfinite(result.optimized_sharpe)
        assert np.isfinite(result.improvement_ratio)
    
    def test_generate_optimization_recommendations(self, optimizer, sample_portfolio_data, sample_market_data):
        """最適化推奨事項生成テスト"""
        optimization_result = optimizer.optimize_sharpe_ratio(
            sample_portfolio_data, sample_market_data, None, 'max_sharpe'
        )
        
        recommendations = optimizer.generate_optimization_recommendations(optimization_result)
        
        assert isinstance(recommendations, dict)
        assert 'optimization_summary' in recommendations
        assert 'portfolio_weights' in recommendations
        assert 'risk_metrics' in recommendations
        assert 'performance_metrics' in recommendations
        assert 'action_items' in recommendations
        assert 'warnings' in recommendations
        assert 'timestamp' in recommendations
        
        # 最適化サマリーの確認
        optimization_summary = recommendations['optimization_summary']
        assert 'original_sharpe' in optimization_summary
        assert 'optimized_sharpe' in optimization_summary
        assert 'improvement_ratio' in optimization_summary
        assert 'target_achieved' in optimization_summary
        assert 'method' in optimization_summary
        
        assert isinstance(optimization_summary['original_sharpe'], float)
        assert isinstance(optimization_summary['optimized_sharpe'], float)
        assert isinstance(optimization_summary['improvement_ratio'], float)
        assert isinstance(optimization_summary['target_achieved'], bool)
        assert isinstance(optimization_summary['method'], str)
        
        # ポートフォリオウェイトの確認
        assert isinstance(recommendations['portfolio_weights'], dict)
        assert len(recommendations['portfolio_weights']) == 5
        
        # リスクメトリクスの確認
        assert isinstance(recommendations['risk_metrics'], dict)
        assert 'portfolio_volatility' in recommendations['risk_metrics']
        assert 'var_95' in recommendations['risk_metrics']
        assert 'max_drawdown' in recommendations['risk_metrics']
        assert 'sharpe_ratio' in recommendations['risk_metrics']
        
        # パフォーマンスメトリクスの確認
        assert isinstance(recommendations['performance_metrics'], dict)
        assert 'portfolio_return' in recommendations['performance_metrics']
        assert 'portfolio_volatility' in recommendations['performance_metrics']
        assert 'sharpe_ratio' in recommendations['performance_metrics']
        assert 'sortino_ratio' in recommendations['performance_metrics']
        assert 'calmar_ratio' in recommendations['performance_metrics']
        
        # アクションアイテムと警告の確認
        assert isinstance(recommendations['action_items'], list)
        assert isinstance(recommendations['warnings'], list)
        
        # タイムスタンプの確認
        assert isinstance(recommendations['timestamp'], str)
    
    def test_error_handling(self, optimizer):
        """エラーハンドリングテスト"""
        # 空のデータでのテスト
        empty_portfolio_data = {'total_value': 0, 'positions': {}}
        
        result = optimizer.optimize_sharpe_ratio(empty_portfolio_data, None, None)
        
        # エラーが発生しても適切に処理されることを確認
        assert isinstance(result, SharpeOptimizationResult)
        assert hasattr(result, 'original_sharpe')
        assert hasattr(result, 'optimized_sharpe')
        assert hasattr(result, 'improvement_ratio')
        assert hasattr(result, 'target_achieved')
        assert hasattr(result, 'optimization_method')
        assert hasattr(result, 'portfolio_weights')
        assert hasattr(result, 'risk_metrics')
        assert hasattr(result, 'performance_metrics')
        assert hasattr(result, 'optimization_timestamp')
        assert hasattr(result, 'convergence_success')
        assert hasattr(result, 'iterations')
    
    def test_edge_cases(self, optimizer):
        """エッジケーステスト"""
        # 単一銘柄のテスト
        single_stock_portfolio = {
            'total_value': 1000000,
            'positions': {
                'AAPL': {
                    'weight': 1.0,
                    'price_data': [
                        {'close': 145.0, 'volume': 1000000},
                        {'close': 147.0, 'volume': 1100000},
                        {'close': 150.0, 'volume': 1200000}
                    ],
                    'sector': 'Technology',
                    'market_cap': 2500000000000,
                    'liquidity_score': 1000000
                }
            }
        }
        
        result = optimizer.optimize_sharpe_ratio(single_stock_portfolio, None, None)
        assert isinstance(result, SharpeOptimizationResult)
        assert hasattr(result, 'original_sharpe')
        assert hasattr(result, 'optimized_sharpe')
        assert hasattr(result, 'improvement_ratio')
        assert hasattr(result, 'target_achieved')
        assert hasattr(result, 'optimization_method')
        assert hasattr(result, 'portfolio_weights')
        assert hasattr(result, 'risk_metrics')
        assert hasattr(result, 'performance_metrics')
        assert hasattr(result, 'optimization_timestamp')
        assert hasattr(result, 'convergence_success')
        assert hasattr(result, 'iterations')
    
    def test_performance_metrics(self, optimizer, sample_portfolio_data, sample_market_data):
        """パフォーマンスメトリクステスト"""
        result = optimizer.optimize_sharpe_ratio(
            sample_portfolio_data, sample_market_data, None, 'max_sharpe'
        )
        
        # パフォーマンスメトリクスが適切に計算されることを確認
        assert result.original_sharpe >= 0.0
        assert result.optimized_sharpe >= 0.0
        assert result.improvement_ratio >= -1.0
        assert result.target_achieved in [True, False]
        assert result.optimization_method == 'max_sharpe'
        assert len(result.portfolio_weights) == 5
        assert result.iterations >= 0
        assert np.isfinite(result.original_sharpe)
        assert np.isfinite(result.optimized_sharpe)
        assert np.isfinite(result.improvement_ratio)
        
        # リスクメトリクスの確認
        assert isinstance(result.risk_metrics, dict)
        assert 'portfolio_volatility' in result.risk_metrics
        assert 'var_95' in result.risk_metrics
        assert 'var_99' in result.risk_metrics
        assert 'max_drawdown' in result.risk_metrics
        assert 'sharpe_ratio' in result.risk_metrics
        
        # パフォーマンスメトリクスの確認
        assert isinstance(result.performance_metrics, dict)
        assert 'portfolio_return' in result.performance_metrics
        assert 'portfolio_volatility' in result.performance_metrics
        assert 'sharpe_ratio' in result.performance_metrics
        assert 'sortino_ratio' in result.performance_metrics
        assert 'calmar_ratio' in result.performance_metrics
