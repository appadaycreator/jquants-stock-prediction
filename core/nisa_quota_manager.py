#!/usr/bin/env python3
"""
新NISA枠管理システム
2024年1月開始の新NISA制度に対応した投資枠管理機能
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

class QuotaType(Enum):
    """NISA枠の種類"""
    GROWTH = "GROWTH"  # 成長投資枠
    ACCUMULATION = "ACCUMULATION"  # つみたて投資枠

class TransactionType(Enum):
    """取引の種類"""
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class NisaQuotaStatus:
    """NISA枠の利用状況"""
    # 成長投資枠
    growth_investment: Dict[str, Any]
    # つみたて投資枠
    accumulation_investment: Dict[str, Any]
    # 枠の再利用状況
    quota_reuse: Dict[str, Any]
    # 更新日時
    last_updated: str

@dataclass
class NisaTransaction:
    """NISA取引記録"""
    id: str
    type: str  # BUY or SELL
    symbol: str
    symbol_name: str
    quantity: int
    price: float
    amount: float
    quota_type: str  # GROWTH or ACCUMULATION
    transaction_date: str
    profit_loss: Optional[float] = None
    tax_free_amount: Optional[float] = None

@dataclass
class NisaPosition:
    """NISAポジション"""
    symbol: str
    symbol_name: str
    quantity: int
    average_price: float
    current_price: float
    cost: float
    current_value: float
    unrealized_profit_loss: float
    quota_type: str
    purchase_date: str

@dataclass
class NisaPortfolio:
    """NISAポートフォリオ"""
    positions: List[NisaPosition]
    total_value: float
    total_cost: float
    unrealized_profit_loss: float
    realized_profit_loss: float
    tax_free_profit_loss: float

class NisaQuotaManager:
    """新NISA枠管理システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # NISA制度の基本設定
        self.growth_annual_limit = 2400000  # 成長投資枠年間240万円
        self.growth_tax_free_limit = 12000000  # 成長投資枠非課税保有限度額1200万円
        self.accumulation_annual_limit = 400000  # つみたて投資枠年間40万円
        self.accumulation_tax_free_limit = 2000000  # つみたて投資枠非課税保有限度額200万円
        
        # データ管理
        self.data_file = self.config.get('nisa_data_file', 'data/nisa_data.json')
        self.nisa_data = self._load_nisa_data()
        
        # 現在の課税年度
        self.current_tax_year = self._get_current_tax_year()
        
    def _get_current_tax_year(self) -> int:
        """現在の課税年度を取得"""
        current_date = date.today()
        if current_date.month >= 1 and current_date.month <= 3:
            return current_date.year - 1
        return current_date.year
    
    def _load_nisa_data(self) -> Dict[str, Any]:
        """NISAデータの読み込み"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # 初期データの作成
            initial_data = {
                'user_profile': {
                    'user_id': 'default_user',
                    'start_date': datetime.now().isoformat(),
                    'tax_year': self._get_current_tax_year()
                },
                'quotas': {
                    'growth_investment': {
                        'annual_limit': self.growth_annual_limit,
                        'tax_free_limit': self.growth_tax_free_limit,
                        'used_amount': 0,
                        'available_amount': self.growth_annual_limit,
                        'utilization_rate': 0.0
                    },
                    'accumulation_investment': {
                        'annual_limit': self.accumulation_annual_limit,
                        'tax_free_limit': self.accumulation_tax_free_limit,
                        'used_amount': 0,
                        'available_amount': self.accumulation_annual_limit,
                        'utilization_rate': 0.0
                    }
                },
                'quota_reuse': {
                    'growth_available': 0,
                    'accumulation_available': 0,
                    'next_year_available': 0
                },
                'transactions': [],
                'portfolio': {
                    'positions': [],
                    'total_value': 0,
                    'total_cost': 0,
                    'unrealized_profit_loss': 0,
                    'realized_profit_loss': 0,
                    'tax_free_profit_loss': 0
                },
                'settings': {
                    'auto_rebalancing': False,
                    'alert_thresholds': {
                        'growth_warning': 80.0,
                        'accumulation_warning': 80.0
                    },
                    'notifications': {
                        'email': True,
                        'browser': True,
                        'push': False
                    }
                }
            }
            self._save_nisa_data(initial_data)
            return initial_data
        except Exception as e:
            self.logger.error(f"NISAデータ読み込みエラー: {e}")
            return {}
    
    def _save_nisa_data(self, data: Dict[str, Any]) -> None:
        """NISAデータの保存"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"NISAデータ保存エラー: {e}")
    
    def get_quota_status(self) -> NisaQuotaStatus:
        """枠利用状況の取得"""
        try:
            quotas = self.nisa_data.get('quotas', {})
            quota_reuse = self.nisa_data.get('quota_reuse', {})
            
            return NisaQuotaStatus(
                growth_investment=quotas.get('growth_investment', {}),
                accumulation_investment=quotas.get('accumulation_investment', {}),
                quota_reuse=quota_reuse,
                last_updated=datetime.now().isoformat()
            )
        except Exception as e:
            self.logger.error(f"枠利用状況取得エラー: {e}")
            return NisaQuotaStatus(
                growth_investment={},
                accumulation_investment={},
                quota_reuse={},
                last_updated=datetime.now().isoformat()
            )
    
    def add_transaction(self, transaction: NisaTransaction) -> Dict[str, Any]:
        """取引記録の追加"""
        try:
            # 取引の検証
            validation_result = self._validate_transaction(transaction)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # 取引の追加
            self.nisa_data['transactions'].append(asdict(transaction))
            
            # 枠の更新
            self._update_quotas(transaction)
            
            # ポートフォリオの更新
            self._update_portfolio(transaction)
            
            # データの保存
            self._save_nisa_data(self.nisa_data)
            
            return {'success': True, 'transaction_id': transaction.id}
            
        except Exception as e:
            self.logger.error(f"取引記録追加エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_transaction(self, transaction: NisaTransaction) -> Dict[str, Any]:
        """取引の検証"""
        try:
            # 基本検証
            if transaction.amount <= 0:
                return {'valid': False, 'error': '取引金額が無効です'}
            
            if transaction.type not in ['BUY', 'SELL']:
                return {'valid': False, 'error': '無効な取引タイプです'}
            
            if transaction.quota_type not in ['GROWTH', 'ACCUMULATION']:
                return {'valid': False, 'error': '無効な枠タイプです'}
            
            # 枠の利用可能性チェック
            quota_status = self.get_quota_status()
            
            if transaction.type == 'BUY':
                if transaction.quota_type == 'GROWTH':
                    available = quota_status.growth_investment.get('available_amount', 0)
                    if transaction.amount > available:
                        return {'valid': False, 'error': '成長投資枠の利用可能額を超えています'}
                elif transaction.quota_type == 'ACCUMULATION':
                    available = quota_status.accumulation_investment.get('available_amount', 0)
                    if transaction.amount > available:
                        return {'valid': False, 'error': 'つみたて投資枠の利用可能額を超えています'}
            
            return {'valid': True}
            
        except Exception as e:
            self.logger.error(f"取引検証エラー: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _update_quotas(self, transaction: NisaTransaction) -> None:
        """枠の更新"""
        try:
            if transaction.type == 'BUY':
                if transaction.quota_type == 'GROWTH':
                    self.nisa_data['quotas']['growth_investment']['used_amount'] += transaction.amount
                    self.nisa_data['quotas']['growth_investment']['available_amount'] -= transaction.amount
                elif transaction.quota_type == 'ACCUMULATION':
                    self.nisa_data['quotas']['accumulation_investment']['used_amount'] += transaction.amount
                    self.nisa_data['quotas']['accumulation_investment']['available_amount'] -= transaction.amount
            elif transaction.type == 'SELL':
                # 売却時の枠解放
                if transaction.quota_type == 'GROWTH':
                    self.nisa_data['quotas']['growth_investment']['used_amount'] -= transaction.amount
                    self.nisa_data['quotas']['growth_investment']['available_amount'] += transaction.amount
                    # 再利用可能枠の追加
                    self.nisa_data['quota_reuse']['growth_available'] += transaction.amount
                elif transaction.quota_type == 'ACCUMULATION':
                    self.nisa_data['quotas']['accumulation_investment']['used_amount'] -= transaction.amount
                    self.nisa_data['quotas']['accumulation_investment']['available_amount'] += transaction.amount
                    # 再利用可能枠の追加
                    self.nisa_data['quota_reuse']['accumulation_available'] += transaction.amount
            
            # 利用率の更新
            self._update_utilization_rates()
            
        except Exception as e:
            self.logger.error(f"枠更新エラー: {e}")
    
    def _update_utilization_rates(self) -> None:
        """利用率の更新"""
        try:
            # 成長投資枠の利用率
            growth_used = self.nisa_data['quotas']['growth_investment']['used_amount']
            growth_limit = self.nisa_data['quotas']['growth_investment']['annual_limit']
            self.nisa_data['quotas']['growth_investment']['utilization_rate'] = (growth_used / growth_limit) * 100
            
            # つみたて投資枠の利用率
            accumulation_used = self.nisa_data['quotas']['accumulation_investment']['used_amount']
            accumulation_limit = self.nisa_data['quotas']['accumulation_investment']['annual_limit']
            self.nisa_data['quotas']['accumulation_investment']['utilization_rate'] = (accumulation_used / accumulation_limit) * 100
            
        except Exception as e:
            self.logger.error(f"利用率更新エラー: {e}")
    
    def _update_portfolio(self, transaction: NisaTransaction) -> None:
        """ポートフォリオの更新"""
        try:
            portfolio = self.nisa_data['portfolio']
            
            if transaction.type == 'BUY':
                # 新規ポジションの追加または既存ポジションの更新
                self._add_or_update_position(transaction)
            elif transaction.type == 'SELL':
                # ポジションの削除または数量の減少
                self._reduce_or_remove_position(transaction)
            
            # ポートフォリオの再計算
            self._recalculate_portfolio()
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ更新エラー: {e}")
    
    def _add_or_update_position(self, transaction: NisaTransaction) -> None:
        """ポジションの追加または更新"""
        try:
            positions = self.nisa_data['portfolio']['positions']
            
            # 既存ポジションの検索
            existing_position = None
            for pos in positions:
                if (pos['symbol'] == transaction.symbol and 
                    pos['quota_type'] == transaction.quota_type):
                    existing_position = pos
                    break
            
            if existing_position:
                # 既存ポジションの更新
                total_quantity = existing_position['quantity'] + transaction.quantity
                total_cost = existing_position['cost'] + transaction.amount
                new_average_price = total_cost / total_quantity
                
                existing_position['quantity'] = total_quantity
                existing_position['average_price'] = new_average_price
                existing_position['cost'] = total_cost
            else:
                # 新規ポジションの追加
                new_position = {
                    'symbol': transaction.symbol,
                    'symbol_name': transaction.symbol_name,
                    'quantity': transaction.quantity,
                    'average_price': transaction.price,
                    'current_price': transaction.price,
                    'cost': transaction.amount,
                    'current_value': transaction.amount,
                    'unrealized_profit_loss': 0,
                    'quota_type': transaction.quota_type,
                    'purchase_date': transaction.transaction_date
                }
                positions.append(new_position)
                
        except Exception as e:
            self.logger.error(f"ポジション追加/更新エラー: {e}")
    
    def _reduce_or_remove_position(self, transaction: NisaTransaction) -> None:
        """ポジションの削除または数量の減少"""
        try:
            positions = self.nisa_data['portfolio']['positions']
            
            for i, pos in enumerate(positions):
                if (pos['symbol'] == transaction.symbol and 
                    pos['quota_type'] == transaction.quota_type):
                    
                    if pos['quantity'] <= transaction.quantity:
                        # ポジションの完全削除
                        positions.pop(i)
                    else:
                        # 数量の減少
                        pos['quantity'] -= transaction.quantity
                        pos['cost'] -= transaction.amount
                        pos['average_price'] = pos['cost'] / pos['quantity'] if pos['quantity'] > 0 else 0
                    break
                    
        except Exception as e:
            self.logger.error(f"ポジション削除/減少エラー: {e}")
    
    def _recalculate_portfolio(self) -> None:
        """ポートフォリオの再計算"""
        try:
            portfolio = self.nisa_data['portfolio']
            positions = portfolio['positions']
            
            total_value = 0
            total_cost = 0
            unrealized_profit_loss = 0
            
            for pos in positions:
                current_value = pos['current_price'] * pos['quantity']
                pos['current_value'] = current_value
                pos['unrealized_profit_loss'] = current_value - pos['cost']
                
                total_value += current_value
                total_cost += pos['cost']
                unrealized_profit_loss += pos['unrealized_profit_loss']
            
            portfolio['total_value'] = total_value
            portfolio['total_cost'] = total_cost
            portfolio['unrealized_profit_loss'] = unrealized_profit_loss
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ再計算エラー: {e}")
    
    def get_portfolio(self) -> NisaPortfolio:
        """ポートフォリオの取得"""
        try:
            portfolio_data = self.nisa_data.get('portfolio', {})
            positions_data = portfolio_data.get('positions', [])
            
            positions = []
            for pos_data in positions_data:
                position = NisaPosition(
                    symbol=pos_data['symbol'],
                    symbol_name=pos_data['symbol_name'],
                    quantity=pos_data['quantity'],
                    average_price=pos_data['average_price'],
                    current_price=pos_data['current_price'],
                    cost=pos_data['cost'],
                    current_value=pos_data['current_value'],
                    unrealized_profit_loss=pos_data['unrealized_profit_loss'],
                    quota_type=pos_data['quota_type'],
                    purchase_date=pos_data['purchase_date']
                )
                positions.append(position)
            
            return NisaPortfolio(
                positions=positions,
                total_value=portfolio_data.get('total_value', 0),
                total_cost=portfolio_data.get('total_cost', 0),
                unrealized_profit_loss=portfolio_data.get('unrealized_profit_loss', 0),
                realized_profit_loss=portfolio_data.get('realized_profit_loss', 0),
                tax_free_profit_loss=portfolio_data.get('tax_free_profit_loss', 0)
            )
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ取得エラー: {e}")
            return NisaPortfolio(
                positions=[],
                total_value=0,
                total_cost=0,
                unrealized_profit_loss=0,
                realized_profit_loss=0,
                tax_free_profit_loss=0
            )
    
    def get_transactions(self, limit: int = 100) -> List[NisaTransaction]:
        """取引履歴の取得"""
        try:
            transactions_data = self.nisa_data.get('transactions', [])
            
            # 最新の取引から取得
            recent_transactions = transactions_data[-limit:] if limit > 0 else transactions_data
            
            transactions = []
            for trans_data in recent_transactions:
                transaction = NisaTransaction(
                    id=trans_data['id'],
                    type=trans_data['type'],
                    symbol=trans_data['symbol'],
                    symbol_name=trans_data['symbol_name'],
                    quantity=trans_data['quantity'],
                    price=trans_data['price'],
                    amount=trans_data['amount'],
                    quota_type=trans_data['quota_type'],
                    transaction_date=trans_data['transaction_date'],
                    profit_loss=trans_data.get('profit_loss'),
                    tax_free_amount=trans_data.get('tax_free_amount')
                )
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            self.logger.error(f"取引履歴取得エラー: {e}")
            return []
    
    def get_quota_optimization(self) -> Dict[str, Any]:
        """枠最適化提案の取得"""
        try:
            quota_status = self.get_quota_status()
            portfolio = self.get_portfolio()
            
            # 成長投資枠の最適化提案
            growth_utilization = quota_status.growth_investment.get('utilization_rate', 0)
            growth_available = quota_status.growth_investment.get('available_amount', 0)
            
            growth_recommendation = {
                'suggested_amount': min(growth_available, 100000),  # 10万円単位での提案
                'reason': '成長投資枠の効率的活用',
                'priority': 'HIGH' if growth_utilization < 50 else 'MEDIUM'
            }
            
            # つみたて投資枠の最適化提案
            accumulation_utilization = quota_status.accumulation_investment.get('utilization_rate', 0)
            accumulation_available = quota_status.accumulation_investment.get('available_amount', 0)
            
            accumulation_recommendation = {
                'suggested_amount': min(accumulation_available, 10000),  # 1万円単位での提案
                'reason': 'つみたて投資枠の効率的活用',
                'priority': 'HIGH' if accumulation_utilization < 50 else 'MEDIUM'
            }
            
            # リスク分析
            risk_analysis = self._analyze_portfolio_risk(portfolio)
            
            return {
                'recommendations': {
                    'growth_quota': growth_recommendation,
                    'accumulation_quota': accumulation_recommendation
                },
                'risk_analysis': risk_analysis
            }
            
        except Exception as e:
            self.logger.error(f"枠最適化提案取得エラー: {e}")
            return {'error': str(e)}
    
    def _analyze_portfolio_risk(self, portfolio: NisaPortfolio) -> Dict[str, Any]:
        """ポートフォリオリスク分析"""
        try:
            positions = portfolio.positions
            
            if not positions:
                return {
                    'diversification_score': 0,
                    'sector_concentration': 0,
                    'risk_level': 'LOW'
                }
            
            # 分散度スコアの計算（簡易版）
            diversification_score = min(len(positions) * 20, 100)
            
            # セクター集中度の計算（簡易版）
            sector_concentration = 100 / len(positions) if positions else 0
            
            # リスクレベルの判定
            if diversification_score >= 80 and sector_concentration <= 20:
                risk_level = 'LOW'
            elif diversification_score >= 60 and sector_concentration <= 40:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'HIGH'
            
            return {
                'diversification_score': diversification_score,
                'sector_concentration': sector_concentration,
                'risk_level': risk_level
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスク分析エラー: {e}")
            return {
                'diversification_score': 0,
                'sector_concentration': 0,
                'risk_level': 'UNKNOWN'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスの取得"""
        try:
            quota_status = self.get_quota_status()
            portfolio = self.get_portfolio()
            transactions = self.get_transactions(limit=10)
            
            return {
                'quota_status': asdict(quota_status),
                'portfolio_summary': {
                    'total_positions': len(portfolio.positions),
                    'total_value': portfolio.total_value,
                    'total_cost': portfolio.total_cost,
                    'unrealized_profit_loss': portfolio.unrealized_profit_loss
                },
                'recent_transactions': len(transactions),
                'system_health': 'HEALTHY',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"システムステータス取得エラー: {e}")
            return {'error': str(e)}
