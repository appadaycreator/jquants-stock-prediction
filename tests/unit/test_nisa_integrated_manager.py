#!/usr/bin/env python3
"""
NISA統合管理システムの単体テスト
"""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.nisa_integrated_manager import (
    NisaIntegratedManager, NisaDashboard, NisaOptimization
)
from core.nisa_quota_manager import NisaTransaction, NisaPortfolio, NisaPosition
from core.nisa_tax_calculator import TaxCalculation, TaxOptimization
from core.nisa_alert_system import QuotaAlert, InvestmentOpportunity

class TestNisaIntegratedManager:
    """NISA統合管理システムのテスト"""
    
    @pytest.fixture
    def temp_config(self):
        """一時設定の作成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        return {
            'nisa_data_file': temp_file,
            'auto_optimization': True,
            'auto_alerts': True
        }
    
    @pytest.fixture
    def integrated_manager(self, temp_config):
        """統合管理システムのインスタンス"""
        return NisaIntegratedManager(temp_config)
    
    @pytest.fixture
    def sample_transaction_data(self):
        """サンプル取引データ"""
        return {
            'id': 'INTEGRATED_001',
            'type': 'BUY',
            'symbol': '7203',
            'symbol_name': 'トヨタ自動車',
            'quantity': 100,
            'price': 2500.0,
            'amount': 250000.0,
            'quota_type': 'GROWTH',
            'transaction_date': datetime.now().isoformat()
        }
    
    def test_initialization(self, integrated_manager):
        """初期化テスト"""
        assert integrated_manager.quota_manager is not None
        assert integrated_manager.tax_calculator is not None
        assert integrated_manager.alert_system is not None
        assert integrated_manager.auto_optimization == True
        assert integrated_manager.auto_alerts == True
    
    def test_get_dashboard_data(self, integrated_manager):
        """ダッシュボードデータ取得テスト"""
        dashboard = integrated_manager.get_dashboard_data()
        
        assert isinstance(dashboard, NisaDashboard)
        assert 'quota_status' in dashboard.__dict__
        assert 'portfolio' in dashboard.__dict__
        assert 'tax_calculation' in dashboard.__dict__
        assert 'alerts' in dashboard.__dict__
        assert 'opportunities' in dashboard.__dict__
        assert 'system_status' in dashboard.__dict__
        assert 'last_updated' in dashboard.__dict__
        
        # 各コンポーネントの検証
        assert isinstance(dashboard.portfolio, NisaPortfolio)
        assert isinstance(dashboard.tax_calculation, TaxCalculation)
        assert isinstance(dashboard.alerts, list)
        assert isinstance(dashboard.opportunities, list)
    
    def test_add_transaction_success(self, integrated_manager, sample_transaction_data):
        """取引追加成功テスト"""
        result = integrated_manager.add_transaction(sample_transaction_data)
        
        assert result['success'] == True
        assert result['transaction_id'] == 'INTEGRATED_001'
    
    def test_add_transaction_validation_failure(self, integrated_manager):
        """取引検証失敗テスト"""
        invalid_data = {
            'type': 'INVALID',
            'symbol': '',
            'quantity': 0,
            'price': 0,
            'amount': 0,
            'quota_type': 'INVALID'
        }
        
        result = integrated_manager.add_transaction(invalid_data)
        
        assert result['success'] == False
        assert 'error' in result
    
    def test_validate_transaction_data_success(self, integrated_manager, sample_transaction_data):
        """取引データ検証成功テスト"""
        result = integrated_manager._validate_transaction_data(sample_transaction_data)
        
        assert result['valid'] == True
    
    def test_validate_transaction_data_failure(self, integrated_manager):
        """取引データ検証失敗テスト"""
        invalid_data = {
            'type': 'INVALID',
            'symbol': '',
            'quantity': 0,
            'price': 0,
            'amount': 0,
            'quota_type': 'INVALID'
        }
        
        result = integrated_manager._validate_transaction_data(invalid_data)
        
        assert result['valid'] == False
        assert 'error' in result
    
    def test_generate_transaction_id(self, integrated_manager):
        """取引ID生成テスト"""
        transaction_id = integrated_manager._generate_transaction_id()
        
        assert transaction_id.startswith('TXN_')
        assert len(transaction_id) > 10  # 日時を含むため
    
    def test_get_optimization_recommendations(self, integrated_manager):
        """最適化提案取得テスト"""
        optimization = integrated_manager.get_optimization_recommendations()
        
        assert isinstance(optimization, NisaOptimization)
        assert 'quota_optimization' in optimization.__dict__
        assert 'tax_optimization' in optimization.__dict__
        assert 'alert_summary' in optimization.__dict__
        assert 'recommendations' in optimization.__dict__
        assert 'priority_score' in optimization.__dict__
        
        assert isinstance(optimization.tax_optimization, TaxOptimization)
        assert isinstance(optimization.recommendations, list)
        assert isinstance(optimization.priority_score, float)
        assert 0 <= optimization.priority_score <= 100
    
    def test_generate_integrated_recommendations(self, integrated_manager):
        """統合推奨事項生成テスト"""
        quota_optimization = {
            'recommendations': {
                'growth_quota': {
                    'suggested_amount': 100000,
                    'reason': '成長投資枠の最適化',
                    'priority': 'HIGH'
                },
                'accumulation_quota': {
                    'suggested_amount': 20000,
                    'reason': 'つみたて投資枠の最適化',
                    'priority': 'MEDIUM'
                }
            }
        }
        
        tax_optimization = TaxOptimization(
            recommended_actions=[
                {
                    'action': 'TAX_OPTIMIZATION',
                    'description': '税務最適化の推奨',
                    'priority': 'HIGH'
                }
            ],
            potential_tax_savings=50000.0,
            optimization_score=75.0,
            priority_level='HIGH'
        )
        
        alert_summary = {
            'critical_alerts': 1,
            'warning_alerts': 2
        }
        
        recommendations = integrated_manager._generate_integrated_recommendations(
            quota_optimization, tax_optimization, alert_summary
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert 'type' in rec
            assert 'title' in rec
            assert 'description' in rec
            assert 'priority' in rec
            assert 'action' in rec
            assert rec['priority'] in ['HIGH', 'MEDIUM', 'LOW']
    
    def test_calculate_priority_score(self, integrated_manager):
        """優先度スコア計算テスト"""
        quota_optimization = {
            'risk_analysis': {
                'diversification_score': 80.0
            }
        }
        
        tax_optimization = TaxOptimization(
            recommended_actions=[],
            potential_tax_savings=0,
            optimization_score=70.0,
            priority_level='MEDIUM'
        )
        
        alert_summary = {
            'critical_alerts': 1,
            'warning_alerts': 2
        }
        
        score = integrated_manager._calculate_priority_score(
            quota_optimization, tax_optimization, alert_summary
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_get_annual_report(self, integrated_manager):
        """年間レポート取得テスト"""
        # サンプル取引を追加
        sample_transaction = {
            'id': 'ANNUAL_001',
            'type': 'BUY',
            'symbol': '7203',
            'symbol_name': 'トヨタ自動車',
            'quantity': 100,
            'price': 2500.0,
            'amount': 250000.0,
            'quota_type': 'GROWTH',
            'transaction_date': datetime.now().isoformat()
        }
        
        integrated_manager.add_transaction(sample_transaction)
        
        report = integrated_manager.get_annual_report()
        
        assert 'annual_tax_report' in report
        assert 'portfolio_performance' in report
        assert 'alert_statistics' in report
        assert 'transaction_summary' in report
        assert 'report_date' in report
        
        # 取引サマリーの検証
        transaction_summary = report['transaction_summary']
        assert transaction_summary['total_transactions'] >= 1
        assert transaction_summary['buy_transactions'] >= 1
        assert transaction_summary['total_investment'] >= 250000.0
    
    def test_calculate_portfolio_performance(self, integrated_manager):
        """ポートフォリオパフォーマンス計算テスト"""
        # 空のポートフォリオ
        empty_portfolio = NisaPortfolio(
            positions=[],
            total_value=0,
            total_cost=0,
            unrealized_profit_loss=0,
            realized_profit_loss=0,
            tax_free_profit_loss=0
        )
        
        performance = integrated_manager._calculate_portfolio_performance(empty_portfolio)
        
        assert performance['total_return'] == 0
        assert performance['total_return_rate'] == 0
        assert performance['annualized_return'] == 0
        assert performance['sharpe_ratio'] == 0
        assert performance['max_drawdown'] == 0
        
        # 利益のあるポートフォリオ
        profitable_portfolio = NisaPortfolio(
            positions=[],
            total_value=1100000.0,
            total_cost=1000000.0,
            unrealized_profit_loss=100000.0,
            realized_profit_loss=0,
            tax_free_profit_loss=0
        )
        
        performance = integrated_manager._calculate_portfolio_performance(profitable_portfolio)
        
        assert performance['total_return'] == 100000.0
        assert performance['total_return_rate'] == 10.0
        assert performance['annualized_return'] == 10.0
    
    def test_generate_sample_market_data(self, integrated_manager):
        """サンプル市場データ生成テスト"""
        market_data = integrated_manager._generate_sample_market_data()
        
        assert isinstance(market_data, list)
        assert len(market_data) > 0
        
        for data in market_data:
            assert 'symbol' in data
            assert 'symbol_name' in data
            assert 'recommendation_score' in data
            assert 'expected_return' in data
            assert 'risk_level' in data
            assert 'dividend_yield' in data
    
    def test_get_system_health(self, integrated_manager):
        """システムヘルス取得テスト"""
        health = integrated_manager.get_system_health()
        
        assert 'health_score' in health
        assert 'health_level' in health
        assert 'quota_system' in health
        assert 'alert_count' in health
        assert 'last_updated' in health
        
        assert 0 <= health['health_score'] <= 100
        assert health['health_level'] in ['EXCELLENT', 'GOOD', 'FAIR', 'POOR']
        assert health['alert_count'] >= 0
    
    def test_export_data_json(self, integrated_manager):
        """JSON形式データエクスポートテスト"""
        export_data = integrated_manager.export_data('json')
        
        assert 'dashboard' in export_data
        assert 'optimization' in export_data
        assert 'annual_report' in export_data
        assert 'export_date' in export_data
        
        # ダッシュボードデータの検証
        dashboard_data = export_data['dashboard']
        assert 'quota_status' in dashboard_data
        assert 'portfolio' in dashboard_data
        assert 'tax_calculation' in dashboard_data
    
    def test_export_data_invalid_format(self, integrated_manager):
        """無効な形式でのエクスポートテスト"""
        export_data = integrated_manager.export_data('invalid_format')
        
        assert 'error' in export_data
        assert 'サポートされていない形式' in export_data['error']
    
    def test_auto_alerts_enabled(self, integrated_manager, sample_transaction_data):
        """自動アラート有効テスト"""
        with patch.object(integrated_manager.alert_system, 'check_quota_alerts') as mock_check:
            with patch.object(integrated_manager.alert_system, 'send_notification') as mock_send:
                mock_check.return_value = [
                    QuotaAlert(
                        type='WARNING',
                        message='テストアラート',
                        quota_type='GROWTH',
                        current_usage=85.0,
                        threshold=80.0,
                        recommended_action='テスト推奨事項',
                        priority='HIGH',
                        created_at=datetime.now().isoformat()
                    )
                ]
                
                result = integrated_manager.add_transaction(sample_transaction_data)
                
                assert result['success'] == True
                mock_check.assert_called_once()
    
    def test_auto_alerts_disabled(self, temp_config):
        """自動アラート無効テスト"""
        temp_config['auto_alerts'] = False
        manager = NisaIntegratedManager(temp_config)
        
        sample_transaction_data = {
            'id': 'NO_ALERT_001',
            'type': 'BUY',
            'symbol': '7203',
            'symbol_name': 'トヨタ自動車',
            'quantity': 100,
            'price': 2500.0,
            'amount': 250000.0,
            'quota_type': 'GROWTH',
            'transaction_date': datetime.now().isoformat()
        }
        
        with patch.object(manager.alert_system, 'check_quota_alerts') as mock_check:
            result = manager.add_transaction(sample_transaction_data)
            
            assert result['success'] == True
            mock_check.assert_not_called()
    
    def test_error_handling_in_dashboard(self, integrated_manager):
        """ダッシュボード取得時のエラーハンドリングテスト"""
        with patch.object(integrated_manager.quota_manager, 'get_quota_status', side_effect=Exception("Test error")):
            dashboard = integrated_manager.get_dashboard_data()
            
            # エラーが発生してもダッシュボードは返される
            assert isinstance(dashboard, NisaDashboard)
            assert dashboard.quota_status == {}
    
    def test_error_handling_in_optimization(self, integrated_manager):
        """最適化提案取得時のエラーハンドリングテスト"""
        with patch.object(integrated_manager.quota_manager, 'get_quota_optimization', side_effect=Exception("Test error")):
            optimization = integrated_manager.get_optimization_recommendations()
            
            # エラーが発生しても最適化提案は返される
            assert isinstance(optimization, NisaOptimization)
            assert optimization.quota_optimization == {}
    
    def test_error_handling_in_annual_report(self, integrated_manager):
        """年間レポート取得時のエラーハンドリングテスト"""
        with patch.object(integrated_manager.quota_manager, 'get_transactions', side_effect=Exception("Test error")):
            report = integrated_manager.get_annual_report()
            
            # エラーが発生した場合はエラーメッセージが返される
            assert 'error' in report
    
    def test_cleanup(self, temp_config):
        """クリーンアップ"""
        if os.path.exists(temp_config['nisa_data_file']):
            os.unlink(temp_config['nisa_data_file'])
