#!/usr/bin/env python3
"""
NISA枠管理システムの単体テスト
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.nisa_quota_manager import (
    NisaQuotaManager, NisaTransaction, NisaPosition, NisaPortfolio,
    QuotaType, TransactionType
)

class TestNisaQuotaManager:
    """NISA枠管理システムのテスト"""
    
    @pytest.fixture
    def temp_config(self):
        """一時設定の作成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        return {'nisa_data_file': temp_file}
    
    @pytest.fixture
    def quota_manager(self, temp_config):
        """NISA枠管理システムのインスタンス"""
        return NisaQuotaManager(temp_config)
    
    @pytest.fixture
    def sample_transaction(self):
        """サンプル取引データ"""
        return NisaTransaction(
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
    
    def test_initialization(self, quota_manager):
        """初期化テスト"""
        assert quota_manager.growth_annual_limit == 2400000
        assert quota_manager.accumulation_annual_limit == 400000
        assert quota_manager.current_tax_year >= 2024
    
    def test_get_quota_status(self, quota_manager):
        """枠利用状況取得テスト"""
        status = quota_manager.get_quota_status()
        
        assert 'growth_investment' in status.__dict__
        assert 'accumulation_investment' in status.__dict__
        assert 'quota_reuse' in status.__dict__
        assert 'last_updated' in status.__dict__
        
        # 成長投資枠の検証
        growth = status.growth_investment
        assert growth['annual_limit'] == 2400000
        assert growth['tax_free_limit'] == 12000000
        assert growth['used_amount'] == 0
        assert growth['available_amount'] == 2400000
        assert growth['utilization_rate'] == 0.0
    
    def test_add_transaction_success(self, quota_manager, sample_transaction):
        """取引追加成功テスト"""
        result = quota_manager.add_transaction(sample_transaction)
        
        assert result['success'] == True
        assert result['transaction_id'] == "TEST_001"
        
        # 枠の更新確認
        status = quota_manager.get_quota_status()
        assert status.growth_investment['used_amount'] == 250000.0
        assert status.growth_investment['available_amount'] == 2150000.0
        assert status.growth_investment['utilization_rate'] == (250000.0 / 2400000.0) * 100
    
    def test_add_transaction_insufficient_quota(self, quota_manager):
        """枠不足時の取引追加テスト"""
        # 枠を超える取引
        large_transaction = NisaTransaction(
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
    
    def test_add_transaction_invalid_type(self, quota_manager):
        """無効な取引タイプのテスト"""
        invalid_transaction = NisaTransaction(
            id="TEST_003",
            type="INVALID",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2500.0,
            amount=250000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        result = quota_manager.add_transaction(invalid_transaction)
        
        assert result['success'] == False
        assert 'error' in result
    
    def test_sell_transaction(self, quota_manager, sample_transaction):
        """売却取引テスト"""
        # まず買い注文を追加
        buy_result = quota_manager.add_transaction(sample_transaction)
        assert buy_result['success'] == True
        
        # 売却取引
        sell_transaction = NisaTransaction(
            id="TEST_004",
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
    
    def test_get_portfolio(self, quota_manager, sample_transaction):
        """ポートフォリオ取得テスト"""
        # 取引を追加
        quota_manager.add_transaction(sample_transaction)
        
        portfolio = quota_manager.get_portfolio()
        
        assert len(portfolio.positions) == 1
        assert portfolio.positions[0].symbol == "7203"
        assert portfolio.positions[0].quantity == 100
        assert portfolio.positions[0].average_price == 2500.0
        assert portfolio.positions[0].cost == 250000.0
        assert portfolio.total_cost == 250000.0
    
    def test_get_transactions(self, quota_manager, sample_transaction):
        """取引履歴取得テスト"""
        # 取引を追加
        quota_manager.add_transaction(sample_transaction)
        
        transactions = quota_manager.get_transactions()
        
        assert len(transactions) == 1
        assert transactions[0].id == "TEST_001"
        assert transactions[0].type == "BUY"
        assert transactions[0].symbol == "7203"
    
    def test_get_quota_optimization(self, quota_manager):
        """枠最適化提案テスト"""
        optimization = quota_manager.get_quota_optimization()
        
        assert 'recommendations' in optimization
        assert 'risk_analysis' in optimization
        
        recommendations = optimization['recommendations']
        assert 'growth_quota' in recommendations
        assert 'accumulation_quota' in recommendations
        
        # 成長投資枠の推奨事項
        growth_rec = recommendations['growth_quota']
        assert 'suggested_amount' in growth_rec
        assert 'reason' in growth_rec
        assert 'priority' in growth_rec
    
    def test_portfolio_risk_analysis(self, quota_manager):
        """ポートフォリオリスク分析テスト"""
        # 空のポートフォリオ
        empty_portfolio = NisaPortfolio(
            positions=[],
            total_value=0,
            total_cost=0,
            unrealized_profit_loss=0,
            realized_profit_loss=0,
            tax_free_profit_loss=0
        )
        
        risk_analysis = quota_manager._analyze_portfolio_risk(empty_portfolio)
        
        assert risk_analysis['diversification_score'] == 0
        assert risk_analysis['sector_concentration'] == 0
        assert risk_analysis['risk_level'] == 'LOW'
    
    def test_system_status(self, quota_manager):
        """システムステータステスト"""
        status = quota_manager.get_system_status()
        
        assert 'quota_status' in status
        assert 'portfolio_summary' in status
        assert 'recent_transactions' in status
        assert 'system_health' in status
        assert 'last_updated' in status
        
        assert status['system_health'] == 'HEALTHY'
    
    def test_data_persistence(self, temp_config):
        """データ永続化テスト"""
        # 最初のマネージャーで取引を追加
        manager1 = NisaQuotaManager(temp_config)
        transaction = NisaTransaction(
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
        manager2 = NisaQuotaManager(temp_config)
        transactions = manager2.get_transactions()
        
        assert len(transactions) == 1
        assert transactions[0].id == "PERSIST_001"
    
    def test_accumulation_quota_management(self, quota_manager):
        """つみたて投資枠管理テスト"""
        accumulation_transaction = NisaTransaction(
            id="ACCUM_001",
            type="BUY",
            symbol="6758",
            symbol_name="ソニーグループ",
            quantity=10,
            price=12000.0,
            amount=120000.0,
            quota_type="ACCUMULATION",
            transaction_date=datetime.now().isoformat()
        )
        
        result = quota_manager.add_transaction(accumulation_transaction)
        assert result['success'] == True
        
        status = quota_manager.get_quota_status()
        accumulation = status.accumulation_investment
        
        assert accumulation['used_amount'] == 120000.0
        assert accumulation['available_amount'] == 280000.0
        assert accumulation['utilization_rate'] == (120000.0 / 400000.0) * 100
    
    def test_quota_reuse_calculation(self, quota_manager, sample_transaction):
        """枠再利用計算テスト"""
        # 買い注文
        buy_result = quota_manager.add_transaction(sample_transaction)
        assert buy_result['success'] == True
        
        # 売却注文
        sell_transaction = NisaTransaction(
            id="REUSE_001",
            type="SELL",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=2600.0,
            amount=260000.0,
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        sell_result = quota_manager.add_transaction(sell_transaction)
        assert sell_result['success'] == True
        
        status = quota_manager.get_quota_status()
        quota_reuse = status.quota_reuse
        
        assert quota_reuse['growth_available'] == 260000.0
    
    def test_error_handling(self, quota_manager):
        """エラーハンドリングテスト"""
        # 無効な取引データ
        invalid_transaction = NisaTransaction(
            id="ERROR_001",
            type="BUY",
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
    
    def test_utilization_rate_calculation(self, quota_manager):
        """利用率計算テスト"""
        # 50%の枠を使用
        half_quota_transaction = NisaTransaction(
            id="UTIL_001",
            type="BUY",
            symbol="7203",
            symbol_name="トヨタ自動車",
            quantity=100,
            price=12000.0,
            amount=1200000.0,  # 120万円（50%）
            quota_type="GROWTH",
            transaction_date=datetime.now().isoformat()
        )
        
        result = quota_manager.add_transaction(half_quota_transaction)
        assert result['success'] == True
        
        status = quota_manager.get_quota_status()
        growth = status.growth_investment
        
        assert growth['utilization_rate'] == 50.0
        assert growth['used_amount'] == 1200000.0
        assert growth['available_amount'] == 1200000.0
    
    def test_multiple_transactions(self, quota_manager):
        """複数取引テスト"""
        transactions = [
            NisaTransaction(
                id=f"MULTI_{i:03d}",
                type="BUY",
                symbol=f"STOCK_{i:03d}",
                symbol_name=f"銘柄{i:03d}",
                quantity=10,
                price=1000.0,
                amount=10000.0,
                quota_type="GROWTH",
                transaction_date=datetime.now().isoformat()
            )
            for i in range(5)
        ]
        
        for transaction in transactions:
            result = quota_manager.add_transaction(transaction)
            assert result['success'] == True
        
        status = quota_manager.get_quota_status()
        growth = status.growth_investment
        
        assert growth['used_amount'] == 50000.0
        assert growth['available_amount'] == 2350000.0
        assert growth['utilization_rate'] == (50000.0 / 2400000.0) * 100
        
        portfolio = quota_manager.get_portfolio()
        assert len(portfolio.positions) == 5
    
    def test_cleanup(self, temp_config):
        """クリーンアップ"""
        if os.path.exists(temp_config['nisa_data_file']):
            os.unlink(temp_config['nisa_data_file'])
