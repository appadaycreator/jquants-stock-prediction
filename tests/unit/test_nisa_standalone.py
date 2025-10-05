#!/usr/bin/env python3
"""
NISAシステムのスタンドアロンテスト
依存関係を完全に分離したテスト
"""

import pytest
import json
import tempfile
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# 依存関係を回避するために直接インポート
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

# 直接ファイルをインポート
import importlib.util

def load_module_from_file(file_path, module_name):
    """ファイルから直接モジュールを読み込み"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# NISAモジュールを直接読み込み
core_dir = os.path.join(project_root, 'core')
nisa_quota_manager = load_module_from_file(
    os.path.join(core_dir, 'nisa_quota_manager.py'),
    'nisa_quota_manager'
)

nisa_tax_calculator = load_module_from_file(
    os.path.join(core_dir, 'nisa_tax_calculator.py'),
    'nisa_tax_calculator'
)

nisa_alert_system = load_module_from_file(
    os.path.join(core_dir, 'nisa_alert_system.py'),
    'nisa_alert_system'
)

class TestNisaStandalone:
    """NISAシステムのスタンドアロンテスト"""
    
    @pytest.fixture
    def temp_config(self):
        """一時設定の作成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        return {'nisa_data_file': temp_file}
    
    @pytest.fixture
    def quota_manager(self, temp_config):
        """NISA枠管理システムのインスタンス"""
        return nisa_quota_manager.NisaQuotaManager(temp_config)
    
    @pytest.fixture
    def tax_calculator(self):
        """税務計算システムのインスタンス"""
        config = {
            'income_tax_rate': 0.20,
            'resident_tax_rate': 0.10
        }
        return nisa_tax_calculator.NisaTaxCalculator(config)
    
    @pytest.fixture
    def alert_system(self):
        """アラートシステムのインスタンス"""
        config = {
            'growth_warning_threshold': 80.0,
            'growth_critical_threshold': 95.0,
            'accumulation_warning_threshold': 80.0,
            'accumulation_critical_threshold': 95.0
        }
        return nisa_alert_system.NisaAlertSystem(config)
    
    def test_quota_manager_initialization(self, quota_manager):
        """枠管理システム初期化テスト"""
        assert quota_manager.growth_annual_limit == 2400000
        assert quota_manager.accumulation_annual_limit == 400000
        assert quota_manager.current_tax_year >= 2024
    
    def test_quota_status_retrieval(self, quota_manager):
        """枠状況取得テスト"""
        status = quota_manager.get_quota_status()
        
        assert hasattr(status, 'growth_investment')
        assert hasattr(status, 'accumulation_investment')
        assert hasattr(status, 'quota_reuse')
        assert hasattr(status, 'last_updated')
        
        # 成長投資枠の検証
        growth = status.growth_investment
        assert growth['annual_limit'] == 2400000
        assert growth['tax_free_limit'] == 12000000
        assert growth['used_amount'] == 0
        assert growth['available_amount'] == 2400000
        assert growth['utilization_rate'] == 0.0
    
    def test_transaction_addition(self, quota_manager):
        """取引追加テスト"""
        transaction = nisa_quota_manager.NisaTransaction(
            id="TEST_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2500.0,
            amount=250000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        result = quota_manager.add_transaction(transaction)
        
        assert result['success'] == True
        assert result['transaction_id'] == "TEST_001"
        
        # 枠の更新確認
        status = quota_manager.get_quota_status()
        assert status.growth_investment['used_amount'] == 250000.0
        assert status.growth_investment['available_amount'] == 2150000.0
    
    def test_insufficient_quota_handling(self, quota_manager):
        """枠不足処理テスト"""
        large_transaction = nisa_quota_manager.NisaTransaction(
            id="TEST_002",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=1000,
            price=3000.0,
            amount=3000000.0,  # 300万円（枠を超える）
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        result = quota_manager.add_transaction(large_transaction)
        
        assert result['success'] == False
        assert 'error' in result
        assert '利用可能額を超えています' in result['error']
    
    def test_sell_transaction(self, quota_manager):
        """売却取引テスト"""
        # 買い注文
        buy_transaction = nisa_quota_manager.NisaTransaction(
            id="BUY_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2500.0,
            amount=250000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        buy_result = quota_manager.add_transaction(buy_transaction)
        assert buy_result['success'] == True
        
        # 売却注文
        sell_transaction = nisa_quota_manager.NisaTransaction(
            id="SELL_001",
            type="SELL",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=50,
            price=2600.0,
            amount=130000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        sell_result = quota_manager.add_transaction(sell_transaction)
        assert sell_result['success'] == True
        
        # 枠の更新確認
        status = quota_manager.get_quota_status()
        assert status.growth_investment['used_amount'] == 120000.0  # 250000 - 130000
        assert status.growth_investment['available_amount'] == 2280000.0  # 2150000 + 130000
    
    def test_portfolio_management(self, quota_manager):
        """ポートフォリオ管理テスト"""
        transaction = nisa_quota_manager.NisaTransaction(
            id="PORTFOLIO_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2500.0,
            amount=250000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        quota_manager.add_transaction(transaction)
        
        portfolio = quota_manager.get_portfolio()
        
        assert len(portfolio.positions) == 1
        assert portfolio.positions[0].symbol == "7203"
        assert portfolio.positions[0].quantity == 100
        assert portfolio.positions[0].average_price == 2500.0
        assert portfolio.positions[0].cost == 250000.0
        assert portfolio.total_cost == 250000.0
    
    def test_tax_calculator_initialization(self, tax_calculator):
        """税務計算システム初期化テスト"""
        assert tax_calculator.income_tax_rate == 0.20
        assert tax_calculator.resident_tax_rate == 0.10
        assert tax_calculator.total_tax_rate == 0.30
        assert tax_calculator.growth_annual_limit == 2400000
        assert tax_calculator.accumulation_annual_limit == 400000
    
    def test_tax_calculation(self, tax_calculator):
        """税務計算テスト"""
        quota_status = {
            'growth_investment': {
                'used_amount': 1200000.0,  # 120万円
                'available_amount': 1200000.0,
                'utilization_rate': 50.0
            },
            'accumulation_investment': {
                'used_amount': 200000.0,  # 20万円
                'available_amount': 200000.0,
                'utilization_rate': 50.0
            },
            'quota_reuse': {
                'growth_available': 100000.0,
                'accumulation_available': 50000.0
            }
        }
        
        portfolio = {
            'total_value': 1500000.0,
            'total_cost': 1400000.0,
            'unrealized_profit_loss': 100000.0,
            'realized_profit_loss': 50000.0,
            'tax_free_profit_loss': 80000.0
        }
        
        result = tax_calculator.calculate_tax_savings(quota_status, portfolio)
        
        assert hasattr(result, 'current_year')
        assert hasattr(result, 'next_year')
        assert hasattr(result, 'tax_savings')
        assert result.total_tax_free_amount > 0
        assert result.effective_tax_rate > 0
    
    def test_alert_system_initialization(self, alert_system):
        """アラートシステム初期化テスト"""
        assert alert_system.alert_thresholds['growth_warning'] == 80.0
        assert alert_system.alert_thresholds['growth_critical'] == 95.0
        assert alert_system.alert_thresholds['accumulation_warning'] == 80.0
        assert alert_system.alert_thresholds['accumulation_critical'] == 95.0
    
    def test_quota_alert_generation(self, alert_system):
        """枠アラート生成テスト"""
        quota_status = {
            'growth_investment': {
                'utilization_rate': 85.0,
                'used_amount': 2040000.0,
                'available_amount': 360000.0
            },
            'accumulation_investment': {
                'utilization_rate': 75.0,
                'used_amount': 300000.0,
                'available_amount': 100000.0
            }
        }
        
        alerts = alert_system.check_quota_alerts(quota_status)
        
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        
        for alert in alerts:
            assert hasattr(alert, 'type')
            assert hasattr(alert, 'message')
            assert hasattr(alert, 'quota_type')
            assert hasattr(alert, 'current_usage')
            assert hasattr(alert, 'threshold')
            assert hasattr(alert, 'priority')
    
    def test_system_integration(self, quota_manager, tax_calculator, alert_system):
        """システム統合テスト"""
        # 1. 取引の追加
        transaction = nisa_quota_manager.NisaTransaction(
            id="INTEGRATION_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2500.0,
            amount=250000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        result = quota_manager.add_transaction(transaction)
        assert result['success'] == True
        
        # 2. 枠状況の取得
        quota_status = quota_manager.get_quota_status()
        assert quota_status.growth_investment['used_amount'] == 250000.0
        
        # 3. 税務計算
        portfolio = quota_manager.get_portfolio()
        tax_calculation = tax_calculator.calculate_tax_savings(
            quota_status.__dict__, portfolio.__dict__
        )
        assert tax_calculation.total_tax_free_amount > 0
        
        # 4. アラートチェック
        alerts = alert_system.check_quota_alerts(quota_status.__dict__)
        assert isinstance(alerts, list)
    
    def test_data_persistence(self, temp_config):
        """データ永続化テスト"""
        # 最初のマネージャーで取引を追加
        manager1 = nisa_quota_manager.NisaQuotaManager(temp_config)
        transaction = nisa_quota_manager.NisaTransaction(
            id="PERSIST_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2500.0,
            amount=250000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        result1 = manager1.add_transaction(transaction)
        assert result1['success'] == True
        
        # 新しいマネージャーでデータを読み込み
        manager2 = nisa_quota_manager.NisaQuotaManager(temp_config)
        transactions = manager2.get_transactions()
        
        assert len(transactions) == 1
        assert transactions[0].id == "PERSIST_001"
    
    def test_error_handling(self, quota_manager):
        """エラーハンドリングテスト"""
        # 無効な取引データ
        invalid_transaction = nisa_quota_manager.NisaTransaction(
            id="ERROR_001",
            type="INVALID",
            symbol="",
            symbol_name="",
            quantity=0,
            price=0.0,
            amount=0.0,
            quota_type="INVALID",
            transaction_date=datetime.now().isoformat()
        )
        
        result = quota_manager.add_transaction(invalid_transaction)
        assert result['success'] == False
        assert 'error' in result
    
    def test_cleanup(self, temp_config):
        """クリーンアップ"""
        if os.path.exists(temp_config['nisa_data_file']):
            os.unlink(temp_config['nisa_data_file'])
