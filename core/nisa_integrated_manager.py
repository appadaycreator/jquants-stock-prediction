#!/usr/bin/env python3
"""
新NISA統合管理システム
2024年1月開始の新NISA制度に対応した統合管理機能
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# 実装したモジュールのインポート
from .nisa_quota_manager import NisaQuotaManager, NisaTransaction, NisaPosition, NisaPortfolio
from .nisa_tax_calculator import NisaTaxCalculator, TaxCalculation, TaxOptimization
from .nisa_alert_system import NisaAlertSystem, QuotaAlert, InvestmentOpportunity, SystemAlert

@dataclass
class NisaDashboard:
    """NISAダッシュボードデータ"""
    quota_status: Dict[str, Any]
    portfolio: NisaPortfolio
    tax_calculation: TaxCalculation
    alerts: List[QuotaAlert]
    opportunities: List[InvestmentOpportunity]
    system_status: Dict[str, Any]
    last_updated: str

@dataclass
class NisaOptimization:
    """NISA最適化提案"""
    quota_optimization: Dict[str, Any]
    tax_optimization: TaxOptimization
    alert_summary: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    priority_score: float

class NisaIntegratedManager:
    """新NISA統合管理システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 各システムの初期化
        self.quota_manager = NisaQuotaManager(config)
        self.tax_calculator = NisaTaxCalculator(config)
        self.alert_system = NisaAlertSystem(config)
        
        # 統合設定
        self.auto_optimization = self.config.get('auto_optimization', True)
        self.auto_alerts = self.config.get('auto_alerts', True)
        
    def get_dashboard_data(self) -> NisaDashboard:
        """ダッシュボードデータの取得"""
        try:
            # 各システムからデータを取得
            quota_status = self.quota_manager.get_quota_status()
            portfolio = self.quota_manager.get_portfolio()
            
            # 税務計算の実行
            tax_calculation = self.tax_calculator.calculate_tax_savings(
                asdict(quota_status), asdict(portfolio)
            )
            
            # アラートのチェック
            alerts = self.alert_system.check_quota_alerts(asdict(quota_status))
            
            # 投資機会の生成（サンプルデータを使用）
            market_data = self._generate_sample_market_data()
            opportunities = self.alert_system.generate_investment_opportunities(
                market_data, asdict(quota_status)
            )
            
            # システムステータスの取得
            system_status = self.quota_manager.get_system_status()
            
            return NisaDashboard(
                quota_status=asdict(quota_status),
                portfolio=portfolio,
                tax_calculation=tax_calculation,
                alerts=alerts,
                opportunities=opportunities,
                system_status=system_status,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"ダッシュボードデータ取得エラー: {e}")
            return NisaDashboard(
                quota_status={},
                portfolio=NisaPortfolio(positions=[], total_value=0, total_cost=0, 
                                     unrealized_profit_loss=0, realized_profit_loss=0, 
                                     tax_free_profit_loss=0),
                tax_calculation=TaxCalculation({}, {}, {}, 0, 0, {}, 0),
                alerts=[],
                opportunities=[],
                system_status={},
                last_updated=datetime.now().isoformat()
            )
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """取引の追加"""
        try:
            # 取引データの検証
            validation_result = self._validate_transaction_data(transaction_data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # 取引オブジェクトの作成
            transaction = NisaTransaction(
                id=transaction_data.get('id', self._generate_transaction_id()),
                type=transaction_data['type'],
                symbol=transaction_data['symbol'],
                symbol_name=transaction_data['symbol_name'],
                quantity=transaction_data['quantity'],
                price=transaction_data['price'],
                amount=transaction_data['amount'],
                quota_type=transaction_data['quota_type'],
                transaction_date=transaction_data.get('transaction_date', datetime.now().isoformat()),
                profit_loss=transaction_data.get('profit_loss'),
                tax_free_amount=transaction_data.get('tax_free_amount')
            )
            
            # 取引の追加
            result = self.quota_manager.add_transaction(transaction)
            
            if result['success']:
                # アラートのチェック
                if self.auto_alerts:
                    quota_status = self.quota_manager.get_quota_status()
                    alerts = self.alert_system.check_quota_alerts(asdict(quota_status))
                    
                    # 重要なアラートの通知
                    for alert in alerts:
                        if alert.priority == 'HIGH':
                            self.alert_system.send_notification(alert, 'browser')
                
                return {'success': True, 'transaction_id': transaction.id}
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"取引追加エラー: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_transaction_data(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """取引データの検証"""
        try:
            required_fields = ['type', 'symbol', 'symbol_name', 'quantity', 'price', 'amount', 'quota_type']
            
            for field in required_fields:
                if field not in transaction_data:
                    return {'valid': False, 'error': f'必須フィールド{field}が不足しています'}
            
            # データ型の検証
            if transaction_data['type'] not in ['BUY', 'SELL']:
                return {'valid': False, 'error': '取引タイプはBUYまたはSELLである必要があります'}
            
            if transaction_data['quota_type'] not in ['GROWTH', 'ACCUMULATION']:
                return {'valid': False, 'error': '枠タイプはGROWTHまたはACCUMULATIONである必要があります'}
            
            if transaction_data['quantity'] <= 0:
                return {'valid': False, 'error': '数量は0より大きい必要があります'}
            
            if transaction_data['price'] <= 0:
                return {'valid': False, 'error': '価格は0より大きい必要があります'}
            
            if transaction_data['amount'] <= 0:
                return {'valid': False, 'error': '金額は0より大きい必要があります'}
            
            return {'valid': True}
            
        except Exception as e:
            self.logger.error(f"取引データ検証エラー: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _generate_transaction_id(self) -> str:
        """取引IDの生成"""
        return f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_optimization_recommendations(self) -> NisaOptimization:
        """最適化提案の取得"""
        try:
            # 枠最適化の取得
            quota_optimization = self.quota_manager.get_quota_optimization()
            
            # 税務最適化の取得
            quota_status = self.quota_manager.get_quota_status()
            portfolio = self.quota_manager.get_portfolio()
            tax_optimization = self.tax_calculator.get_tax_optimization(
                asdict(quota_status), asdict(portfolio)
            )
            
            # アラートサマリーの取得
            alert_summary = self.alert_system.get_alert_summary()
            
            # 統合推奨事項の生成
            recommendations = self._generate_integrated_recommendations(
                quota_optimization, tax_optimization, alert_summary
            )
            
            # 優先度スコアの計算
            priority_score = self._calculate_priority_score(
                quota_optimization, tax_optimization, alert_summary
            )
            
            return NisaOptimization(
                quota_optimization=quota_optimization,
                tax_optimization=tax_optimization,
                alert_summary=alert_summary,
                recommendations=recommendations,
                priority_score=priority_score
            )
            
        except Exception as e:
            self.logger.error(f"最適化提案取得エラー: {e}")
            return NisaOptimization(
                quota_optimization={},
                tax_optimization=TaxOptimization([], 0, 0, 'UNKNOWN', 0.0, {}),
                alert_summary={},
                recommendations=[],
                priority_score=0
            )
    
    def _generate_integrated_recommendations(self, quota_optimization: Dict[str, Any], 
                                           tax_optimization: TaxOptimization, 
                                           alert_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """統合推奨事項の生成"""
        try:
            recommendations = []
            
            # 枠最適化の推奨事項
            quota_recs = quota_optimization.get('recommendations', {})
            if quota_recs:
                growth_rec = quota_recs.get('growth_quota', {})
                if growth_rec.get('priority') == 'HIGH':
                    recommendations.append({
                        'type': 'QUOTA_OPTIMIZATION',
                        'title': '成長投資枠の最適化',
                        'description': growth_rec.get('reason', ''),
                        'priority': 'HIGH',
                        'action': f"成長投資枠に{growth_rec.get('suggested_amount', 0):,.0f}円の投資を検討してください"
                    })
                
                accumulation_rec = quota_recs.get('accumulation_quota', {})
                if accumulation_rec.get('priority') == 'HIGH':
                    recommendations.append({
                        'type': 'QUOTA_OPTIMIZATION',
                        'title': 'つみたて投資枠の最適化',
                        'description': accumulation_rec.get('reason', ''),
                        'priority': 'MEDIUM',
                        'action': f"つみたて投資枠に{accumulation_rec.get('suggested_amount', 0):,.0f}円の投資を検討してください"
                    })
            
            # 税務最適化の推奨事項
            tax_recs = tax_optimization.recommended_actions
            for tax_rec in tax_recs:
                if tax_rec.get('priority') == 'HIGH':
                    recommendations.append({
                        'type': 'TAX_OPTIMIZATION',
                        'title': '税務最適化',
                        'description': tax_rec.get('description', ''),
                        'priority': 'HIGH',
                        'action': tax_rec.get('action', '')
                    })
            
            # アラートに基づく推奨事項
            critical_alerts = alert_summary.get('critical_alerts', 0)
            if critical_alerts > 0:
                recommendations.append({
                    'type': 'ALERT_RESPONSE',
                    'title': '緊急対応が必要',
                    'description': f'{critical_alerts}件の重要なアラートが発生しています',
                    'priority': 'HIGH',
                    'action': 'アラートの詳細を確認し、適切な対応を取ってください'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"統合推奨事項生成エラー: {e}")
            return []
    
    def _calculate_priority_score(self, quota_optimization: Dict[str, Any], 
                                 tax_optimization: TaxOptimization, 
                                 alert_summary: Dict[str, Any]) -> float:
        """優先度スコアの計算"""
        try:
            score = 0.0
            
            # 枠最適化スコア
            risk_analysis = quota_optimization.get('risk_analysis', {})
            diversification_score = risk_analysis.get('diversification_score', 0)
            score += diversification_score * 0.3
            
            # 税務最適化スコア
            score += tax_optimization.optimization_score * 0.4
            
            # アラートスコア
            critical_alerts = alert_summary.get('critical_alerts', 0)
            warning_alerts = alert_summary.get('warning_alerts', 0)
            score += (critical_alerts * 20 + warning_alerts * 10) * 0.3
            
            return min(score, 100.0)  # 最大100点
            
        except Exception as e:
            self.logger.error(f"優先度スコア計算エラー: {e}")
            return 0.0
    
    def get_annual_report(self) -> Dict[str, Any]:
        """年間レポートの取得"""
        try:
            # 年間取引の取得
            transactions = self.quota_manager.get_transactions(limit=1000)
            
            # 年間税務レポートの計算
            quota_status = self.quota_manager.get_quota_status()
            annual_tax_report = self.tax_calculator.calculate_annual_tax_report(
                [asdict(t) for t in transactions], asdict(quota_status)
            )
            
            # ポートフォリオパフォーマンスの計算
            portfolio = self.quota_manager.get_portfolio()
            portfolio_performance = self._calculate_portfolio_performance(portfolio)
            
            # アラート統計の取得
            alert_summary = self.alert_system.get_alert_summary()
            
            return {
                'annual_tax_report': annual_tax_report,
                'portfolio_performance': portfolio_performance,
                'alert_statistics': alert_summary,
                'transaction_summary': {
                    'total_transactions': len(transactions),
                    'buy_transactions': len([t for t in transactions if t.type == 'BUY']),
                    'sell_transactions': len([t for t in transactions if t.type == 'SELL']),
                    'total_investment': sum(t.amount for t in transactions if t.type == 'BUY'),
                    'total_sales': sum(t.amount for t in transactions if t.type == 'SELL')
                },
                'report_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"年間レポート取得エラー: {e}")
            return {'error': str(e)}
    
    def _calculate_portfolio_performance(self, portfolio: NisaPortfolio) -> Dict[str, Any]:
        """ポートフォリオパフォーマンスの計算"""
        try:
            if portfolio.total_cost == 0:
                return {
                    'total_return': 0,
                    'total_return_rate': 0,
                    'annualized_return': 0,
                    'sharpe_ratio': 0,
                    'max_drawdown': 0
                }
            
            # 総リターンの計算
            total_return = portfolio.unrealized_profit_loss
            total_return_rate = (total_return / portfolio.total_cost) * 100
            
            # 年率リターンの計算（簡易版）
            annualized_return = total_return_rate  # 実際の実装では期間を考慮
            
            # シャープレシオの計算（簡易版）
            sharpe_ratio = annualized_return / 10  # 仮のリスク率10%
            
            return {
                'total_return': total_return,
                'total_return_rate': total_return_rate,
                'annualized_return': annualized_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': 0  # 実際の実装では最大ドローダウンの計算
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオパフォーマンス計算エラー: {e}")
            return {}
    
    def _generate_sample_market_data(self) -> List[Dict[str, Any]]:
        """サンプル市場データの生成"""
        try:
            sample_data = [
                {
                    'symbol': '7203',
                    'symbol_name': 'トヨタ自動車',
                    'recommendation_score': 0.85,
                    'expected_return': 0.12,
                    'risk_level': 'MEDIUM',
                    'dividend_yield': 0.025
                },
                {
                    'symbol': '6758',
                    'symbol_name': 'ソニーグループ',
                    'recommendation_score': 0.78,
                    'expected_return': 0.15,
                    'risk_level': 'HIGH',
                    'dividend_yield': 0.015
                },
                {
                    'symbol': '9984',
                    'symbol_name': 'ソフトバンクグループ',
                    'recommendation_score': 0.65,
                    'expected_return': 0.08,
                    'risk_level': 'HIGH',
                    'dividend_yield': 0.020
                }
            ]
            return sample_data
            
        except Exception as e:
            self.logger.error(f"サンプル市場データ生成エラー: {e}")
            return []
    
    def get_system_health(self) -> Dict[str, Any]:
        """システムヘルスの取得"""
        try:
            # 各システムのステータス
            quota_status = self.quota_manager.get_system_status()
            alert_summary = self.alert_system.get_alert_summary()
            
            # システムヘルスの計算
            health_score = 100.0
            
            # アラートによる減点
            critical_alerts = alert_summary.get('critical_alerts', 0)
            warning_alerts = alert_summary.get('warning_alerts', 0)
            health_score -= critical_alerts * 10
            health_score -= warning_alerts * 5
            
            # ヘルスレベルの判定
            if health_score >= 90:
                health_level = 'EXCELLENT'
            elif health_score >= 70:
                health_level = 'GOOD'
            elif health_score >= 50:
                health_level = 'FAIR'
            else:
                health_level = 'POOR'
            
            return {
                'health_score': max(health_score, 0),
                'health_level': health_level,
                'quota_system': quota_status.get('system_health', 'UNKNOWN'),
                'alert_count': critical_alerts + warning_alerts,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"システムヘルス取得エラー: {e}")
            return {'error': str(e)}
    
    def export_data(self, format: str = 'json') -> Dict[str, Any]:
        """データのエクスポート"""
        try:
            if format == 'json':
                # JSON形式でのエクスポート
                dashboard_data = self.get_dashboard_data()
                optimization_data = self.get_optimization_recommendations()
                annual_report = self.get_annual_report()
                
                return {
                    'dashboard': asdict(dashboard_data),
                    'optimization': asdict(optimization_data),
                    'annual_report': annual_report,
                    'export_date': datetime.now().isoformat()
                }
            else:
                return {'error': f'サポートされていない形式: {format}'}
                
        except Exception as e:
            self.logger.error(f"データエクスポートエラー: {e}")
            return {'error': str(e)}
