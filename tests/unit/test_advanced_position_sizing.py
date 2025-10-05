#!/usr/bin/env python3
"""
高度なポジションサイジング機能のテスト
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from core.advanced_position_sizing import AdvancedPositionSizing


class TestAdvancedPositionSizing:
    """高度なポジションサイジングテスト"""
    
    @pytest.fixture
    def position_sizing(self):
        """ポジションサイジングインスタンス"""
        config = {
            'max_position_percent': 0.2,
            'base_position_size': 100,
            'risk_per_trade': 0.02,
            'confidence_multiplier': 2.0,
            'min_confidence': 0.6,
            'volatility_adjustment': True,
            'max_volatility': 0.05,
            'correlation_adjustment': True,
            'max_correlation': 0.7
        }
        return AdvancedPositionSizing(config)
    
    def test_initialization(self, position_sizing):
        """初期化テスト"""
        assert position_sizing.max_position_percent == 0.2
        assert position_sizing.base_position_size == 100
        assert position_sizing.risk_per_trade == 0.02
        assert position_sizing.confidence_multiplier == 2.0
        assert position_sizing.min_confidence == 0.6
        assert position_sizing.volatility_adjustment == True
        assert position_sizing.max_volatility == 0.05
        assert position_sizing.correlation_adjustment == True
        assert position_sizing.max_correlation == 0.7
    
    def test_calculate_position_size_basic(self, position_sizing):
        """基本ポジションサイズ計算テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.8,
            volatility=0.02,
            correlation=0.3,
            risk_level='MEDIUM'
        )
        
        assert 'position_size' in result
        assert 'base_size' in result
        assert 'risk_adjusted_size' in result
        assert 'volatility_adjusted_size' in result
        assert 'correlation_adjusted_size' in result
        assert 'portfolio_adjusted_size' in result
        assert 'confidence' in result
        assert 'volatility' in result
        assert 'correlation' in result
        assert 'risk_metrics' in result
        assert result['position_size'] > 0
        assert result['confidence'] == 0.8
        assert result['volatility'] == 0.02
        assert result['correlation'] == 0.3
    
    def test_calculate_position_size_with_max_loss(self, position_sizing):
        """最大損失額制限付きポジションサイズ計算テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.8,
            volatility=0.02,
            correlation=0.3,
            risk_level='MEDIUM',
            max_loss_amount=50000.0
        )
        
        assert 'position_size' in result
        assert 'max_loss_amount' in result
        assert result['max_loss_amount'] == 50000.0
        assert result['position_size'] > 0
    
    def test_calculate_position_size_with_portfolio_correlation(self, position_sizing):
        """ポートフォリオ相関考慮ポジションサイズ計算テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.8,
            volatility=0.02,
            correlation=0.3,
            risk_level='MEDIUM',
            portfolio_correlation=0.9
        )
        
        assert 'portfolio_correlation' in result
        assert result['portfolio_correlation'] == 0.9
        assert result['position_size'] > 0
    
    def test_high_volatility_adjustment(self, position_sizing):
        """高ボラティリティ調整テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.8,
            volatility=0.1,  # 高ボラティリティ
            correlation=0.3,
            risk_level='MEDIUM'
        )
        
        assert result['volatility'] == 0.1
        assert result['position_size'] > 0
    
    def test_high_correlation_adjustment(self, position_sizing):
        """高相関調整テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.8,
            volatility=0.02,
            correlation=0.9,  # 高相関
            risk_level='MEDIUM'
        )
        
        assert result['correlation'] == 0.9
        assert result['position_size'] > 0
    
    def test_low_confidence_adjustment(self, position_sizing):
        """低信頼度調整テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.3,  # 低信頼度
            volatility=0.02,
            correlation=0.3,
            risk_level='MEDIUM'
        )
        
        assert result['confidence'] == 0.3
        assert result['position_size'] >= 0
    
    def test_high_risk_level_adjustment(self, position_sizing):
        """高リスクレベル調整テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.8,
            volatility=0.02,
            correlation=0.3,
            risk_level='HIGH'  # 高リスク
        )
        
        assert result['risk_level'] == 'HIGH'
        assert result['position_size'] > 0
    
    def test_calculate_portfolio_position_sizes(self, position_sizing):
        """ポートフォリオポジションサイズ計算テスト"""
        stock_data = [
            {
                'symbol': '7203',
                'price': 2500.0,
                'confidence': 0.8,
                'volatility': 0.02,
                'correlation': 0.3,
                'risk_level': 'MEDIUM'
            },
            {
                'symbol': '6758',
                'price': 12000.0,
                'confidence': 0.7,
                'volatility': 0.03,
                'correlation': 0.2,
                'risk_level': 'LOW'
            }
        ]
        
        result = position_sizing.calculate_portfolio_position_sizes(
            account_balance=1000000.0,
            stock_data=stock_data
        )
        
        assert 'positions' in result
        assert 'total_position_value' in result
        assert 'remaining_balance' in result
        assert 'portfolio_percent' in result
        assert 'diversification_score' in result
        assert len(result['positions']) > 0
        assert result['total_position_value'] > 0
    
    def test_optimize_position_sizes(self, position_sizing):
        """ポジションサイズ最適化テスト"""
        stock_data = [
            {
                'symbol': '7203',
                'price': 2500.0,
                'confidence': 0.8,
                'volatility': 0.02,
                'correlation': 0.3,
                'risk_level': 'MEDIUM'
            },
            {
                'symbol': '6758',
                'price': 12000.0,
                'confidence': 0.7,
                'volatility': 0.03,
                'correlation': 0.2,
                'risk_level': 'LOW'
            }
        ]
        
        result = position_sizing.optimize_position_sizes(
            account_balance=1000000.0,
            stock_data=stock_data,
            target_return=0.1,
            max_risk=0.15
        )
        
        assert 'optimized_positions' in result
        assert 'total_risk' in result
        assert 'expected_return' in result
        assert 'risk_utilization' in result
        assert 'return_target_achievement' in result
        assert result['total_risk'] >= 0
        assert result['expected_return'] >= 0
    
    def test_optimize_portfolio_allocation(self, position_sizing):
        """ポートフォリオ最適化テスト"""
        stock_data = [
            {
                'symbol': '7203',
                'price': 2500.0,
                'confidence': 0.8,
                'volatility': 0.02,
                'correlation': 0.3,
                'risk_level': 'MEDIUM'
            },
            {
                'symbol': '6758',
                'price': 12000.0,
                'confidence': 0.7,
                'volatility': 0.03,
                'correlation': 0.2,
                'risk_level': 'LOW'
            }
        ]
        
        result = position_sizing.optimize_portfolio_allocation(
            account_balance=1000000.0,
            stock_data=stock_data,
            target_return=0.1,
            max_risk=0.15,
            diversification_target=0.8
        )
        
        assert 'optimized_allocation' in result
        assert 'stock_analysis' in result
        assert 'validation_result' in result
        assert 'diversification_score' in result
        assert 'risk_return_ratio' in result
        assert 'optimization_timestamp' in result
    
    def test_calculate_individual_stock_limits(self, position_sizing):
        """個別銘柄損失額設定テスト"""
        stock_data = [
            {
                'symbol': '7203',
                'volatility': 0.02,
                'confidence': 0.8,
                'risk_level': 'MEDIUM'
            },
            {
                'symbol': '6758',
                'volatility': 0.03,
                'confidence': 0.7,
                'risk_level': 'LOW'
            }
        ]
        
        result = position_sizing.calculate_individual_stock_limits(
            account_balance=1000000.0,
            stock_data=stock_data,
            max_total_loss=100000.0
        )
        
        assert 'individual_limits' in result
        assert 'total_allocated' in result
        assert 'max_total_loss' in result
        assert 'utilization_rate' in result
        assert len(result['individual_limits']) > 0
        assert result['max_total_loss'] == 100000.0
    
    def test_get_position_sizing_recommendations(self, position_sizing):
        """ポジションサイジング推奨事項テスト"""
        stock_data = [
            {
                'symbol': '7203',
                'confidence': 0.5,  # 低信頼度
                'volatility': 0.08,  # 高ボラティリティ
                'risk_level': 'HIGH'
            },
            {
                'symbol': '6758',
                'confidence': 0.8,
                'volatility': 0.02,
                'risk_level': 'LOW'
            }
        ]
        
        result = position_sizing.get_position_sizing_recommendations(
            account_balance=1000000.0,
            stock_data=stock_data
        )
        
        assert 'recommendations' in result
        assert 'total_recommendations' in result
        assert 'high_priority' in result
        assert len(result['recommendations']) > 0
        assert result['total_recommendations'] > 0
    
    def test_risk_metrics_calculation(self, position_sizing):
        """リスクメトリクス計算テスト"""
        result = position_sizing.calculate_position_size(
            account_balance=1000000.0,
            stock_price=1000.0,
            confidence=0.8,
            volatility=0.02,
            correlation=0.3,
            risk_level='MEDIUM'
        )
        
        risk_metrics = result['risk_metrics']
        assert 'position_value' in risk_metrics
        assert 'position_percent' in risk_metrics
        assert 'daily_var' in risk_metrics
        assert 'portfolio_impact' in risk_metrics
        assert 'risk_score' in risk_metrics
        assert 'volatility_contribution' in risk_metrics
        assert 'correlation_risk' in risk_metrics
        assert risk_metrics['position_value'] > 0
        assert risk_metrics['position_percent'] > 0
        assert risk_metrics['daily_var'] > 0
        assert risk_metrics['risk_score'] >= 0
    
    def test_error_handling(self, position_sizing):
        """エラーハンドリングテスト"""
        # 無効なパラメータでテスト
        result = position_sizing.calculate_position_size(
            account_balance=-1000.0,  # 負の残高
            stock_price=0.0,  # ゼロ価格
            confidence=2.0,  # 無効な信頼度
            volatility=-0.1,  # 負のボラティリティ
            correlation=1.5,  # 無効な相関
            risk_level='INVALID'  # 無効なリスクレベル
        )
        
        assert 'position_size' in result
        assert result['position_size'] >= 0  # エラーでも負の値は返さない
    
    def test_edge_cases(self, position_sizing):
        """境界値テスト"""
        # 極端な値でのテスト
        result = position_sizing.calculate_position_size(
            account_balance=100.0,  # 小さい残高
            stock_price=100000.0,  # 高い株価
            confidence=0.99,  # 高信頼度
            volatility=0.001,  # 低ボラティリティ
            correlation=0.0,  # 無相関
            risk_level='LOW'
        )
        
        assert result['position_size'] >= 0
        assert result['position_value'] >= 0
        assert result['position_percent'] >= 0
    
    def test_performance_requirements(self, position_sizing):
        """パフォーマンス要件テスト"""
        import time
        
        stock_data = [
            {
                'symbol': f'STOCK_{i}',
                'price': 1000.0 + i * 100,
                'confidence': 0.7 + (i % 3) * 0.1,
                'volatility': 0.02 + (i % 2) * 0.01,
                'correlation': (i % 5) * 0.2,
                'risk_level': ['LOW', 'MEDIUM', 'HIGH'][i % 3]
            }
            for i in range(100)  # 100銘柄
        ]
        
        start_time = time.time()
        result = position_sizing.calculate_portfolio_position_sizes(
            account_balance=10000000.0,
            stock_data=stock_data
        )
        end_time = time.time()
        
        # パフォーマンス要件: 1秒以内
        assert (end_time - start_time) < 1.0
        assert 'positions' in result
        assert len(result['positions']) > 0

