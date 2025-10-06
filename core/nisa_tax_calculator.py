#!/usr/bin/env python3
"""
新NISA税務計算システム
2024年1月開始の新NISA制度に対応した税務計算機能
非課税枠利用率90%以上を目標とした税務最適化システム
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
import math

@dataclass
class TaxCalculation:
    """税務計算結果"""
    current_year: Dict[str, Any]
    next_year: Dict[str, Any]
    tax_savings: Dict[str, Any]
    total_tax_free_amount: float
    effective_tax_rate: float
    optimization: Dict[str, Any] = field(default_factory=dict)
    efficiency_score: float = 0.0

@dataclass
class TaxOptimization:
    """税務最適化提案"""
    recommended_actions: List[Dict[str, Any]]
    potential_tax_savings: float
    optimization_score: float
    priority_level: str
    efficiency_improvement: float = 0.0
    target_achievement: Dict[str, Any] = field(default_factory=dict)

class NisaTaxCalculator:
    """新NISA税務計算システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 税率設定
        self.income_tax_rate = self.config.get('income_tax_rate', 0.20)  # 所得税率20%
        self.resident_tax_rate = self.config.get('resident_tax_rate', 0.10)  # 住民税率10%
        self.total_tax_rate = round(self.income_tax_rate + self.resident_tax_rate, 2)  # 合計税率30%
        
        # NISA制度の基本設定
        self.growth_annual_limit = 2400000  # 成長投資枠年間240万円
        self.accumulation_annual_limit = 400000  # つみたて投資枠年間40万円
        
        # 最適化設定
        self.target_utilization_rate = 90.0  # 目標利用率90%
        self.optimization_threshold = 0.85  # 最適化閾値85%
        
    def calculate_tax_savings(self, quota_status: Dict[str, Any], 
                            portfolio: Dict[str, Any]) -> TaxCalculation:
        """税務計算の実行"""
        try:
            # 現在年度の税務計算
            current_year = self._calculate_current_year_tax(quota_status, portfolio)
            
            # 翌年度の税務計算
            next_year = self._calculate_next_year_tax(quota_status, portfolio)
            
            # 税務節約額の計算
            tax_savings = self._calculate_tax_savings(quota_status, portfolio)
            
            # 総非課税枠額の計算
            total_tax_free_amount = self._calculate_total_tax_free_amount(quota_status)
            
            # 実効税率の計算
            effective_tax_rate = self._calculate_effective_tax_rate(quota_status, portfolio)
            
            # 最適化指標の計算
            optimization = self._calculate_optimization_metrics(quota_status, portfolio)
            
            # 効率スコアの計算
            efficiency_score = self._calculate_efficiency_score(quota_status, portfolio)
            
            return TaxCalculation(
                current_year=current_year,
                next_year=next_year,
                tax_savings=tax_savings,
                total_tax_free_amount=total_tax_free_amount,
                effective_tax_rate=effective_tax_rate,
                optimization=optimization,
                efficiency_score=efficiency_score
            )
            
        except Exception as e:
            self.logger.error(f"税務計算エラー: {e}")
            return TaxCalculation(
                current_year={},
                next_year={},
                tax_savings={},
                total_tax_free_amount=0,
                effective_tax_rate=0,
                optimization={},
                efficiency_score=0
            )
    
    def _calculate_current_year_tax(self, quota_status: Dict[str, Any], 
                                  portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """現在年度の税務計算"""
        try:
            growth_quota_used = quota_status.get('growth_investment', {}).get('used_amount', 0)
            accumulation_quota_used = quota_status.get('accumulation_investment', {}).get('used_amount', 0)
            
            # 非課税枠内の投資額
            total_tax_free_amount = growth_quota_used + accumulation_quota_used
            
            # 仮想的な税務節約額（非課税枠内の投資が課税投資だった場合の税額）
            hypothetical_tax = total_tax_free_amount * self.total_tax_rate
            
            return {
                'growth_quota_used': growth_quota_used,
                'accumulation_quota_used': accumulation_quota_used,
                'total_tax_free_amount': total_tax_free_amount,
                'hypothetical_tax': hypothetical_tax,
                'tax_savings': hypothetical_tax
            }
            
        except Exception as e:
            self.logger.error(f"現在年度税務計算エラー: {e}")
            return {}
    
    def _calculate_next_year_tax(self, quota_status: Dict[str, Any], 
                                portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """翌年度の税務計算"""
        try:
            # 再利用可能枠の取得
            quota_reuse = quota_status.get('quota_reuse', {})
            growth_available = quota_reuse.get('growth_available', 0)
            accumulation_available = quota_reuse.get('accumulation_available', 0)
            
            # 翌年度利用可能枠
            next_year_growth = self.growth_annual_limit + growth_available
            next_year_accumulation = self.accumulation_annual_limit + accumulation_available
            
            return {
                'available_growth_quota': next_year_growth,
                'available_accumulation_quota': next_year_accumulation,
                'reusable_quota': growth_available + accumulation_available,
                'total_available': next_year_growth + next_year_accumulation
            }
            
        except Exception as e:
            self.logger.error(f"翌年度税務計算エラー: {e}")
            return {}
    
    def _calculate_tax_savings(self, quota_status: Dict[str, Any], 
                             portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """税務節約額の計算"""
        try:
            # 非課税枠内の投資額
            growth_used = quota_status.get('growth_investment', {}).get('used_amount', 0)
            accumulation_used = quota_status.get('accumulation_investment', {}).get('used_amount', 0)
            total_tax_free_amount = growth_used + accumulation_used
            
            # 税務節約額の計算
            estimated_tax_savings = total_tax_free_amount * self.total_tax_rate
            
            # 実効税率の計算
            effective_tax_rate = self.total_tax_rate
            
            return {
                'estimated_tax_savings': estimated_tax_savings,
                'tax_rate': self.total_tax_rate,
                'effective_tax_rate': effective_tax_rate,
                'annual_savings': estimated_tax_savings,
                'lifetime_savings': estimated_tax_savings * 5  # 5年間の概算
            }
            
        except Exception as e:
            self.logger.error(f"税務節約額計算エラー: {e}")
            return {}
    
    def _calculate_total_tax_free_amount(self, quota_status: Dict[str, Any]) -> float:
        """総非課税枠額の計算"""
        try:
            growth_used = quota_status.get('growth_investment', {}).get('used_amount', 0)
            accumulation_used = quota_status.get('accumulation_investment', {}).get('used_amount', 0)
            return growth_used + accumulation_used
        except Exception as e:
            self.logger.error(f"総非課税枠額計算エラー: {e}")
            return 0.0
    
    def _calculate_effective_tax_rate(self, quota_status: Dict[str, Any], 
                                    portfolio: Dict[str, Any]) -> float:
        """実効税率の計算"""
        try:
            # ポートフォリオの未実現損益
            unrealized_profit_loss = portfolio.get('unrealized_profit_loss', 0)
            
            # 非課税枠内の投資額
            total_tax_free_amount = self._calculate_total_tax_free_amount(quota_status)
            
            if total_tax_free_amount > 0:
                # 非課税枠の活用率に基づく実効税率の調整
                utilization_rate = total_tax_free_amount / (self.growth_annual_limit + self.accumulation_annual_limit)
                adjusted_tax_rate = self.total_tax_rate * utilization_rate
                return adjusted_tax_rate
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"実効税率計算エラー: {e}")
            return 0.0
    
    def get_tax_optimization(self, quota_status: Dict[str, Any], 
                           portfolio: Dict[str, Any]) -> TaxOptimization:
        """税務最適化提案の取得"""
        try:
            # 最適化提案の生成
            recommendations = self._generate_tax_recommendations(quota_status, portfolio)
            
            # 潜在的な税務節約額の計算
            potential_savings = self._calculate_potential_tax_savings(quota_status, portfolio)
            
            # 最適化スコアの計算
            optimization_score = self._calculate_optimization_score(quota_status, portfolio)
            
            # 優先度レベルの判定
            priority_level = self._determine_priority_level(optimization_score)
            
            return TaxOptimization(
                recommended_actions=recommendations,
                potential_tax_savings=potential_savings,
                optimization_score=optimization_score,
                priority_level=priority_level,
                efficiency_improvement=0.0,
                target_achievement={}
            )
            
        except Exception as e:
            self.logger.error(f"税務最適化提案取得エラー: {e}")
            return TaxOptimization(
                recommended_actions=[],
                potential_tax_savings=0,
                optimization_score=0,
                priority_level='UNKNOWN',
                efficiency_improvement=0.0,
                target_achievement={}
            )
    
    def _generate_tax_recommendations(self, quota_status: Dict[str, Any], 
                                    portfolio: Dict[str, Any]) -> List[Dict[str, Any]]:
        """税務推奨事項の生成"""
        try:
            recommendations = []
            
            # 成長投資枠の活用推奨
            growth_utilization = quota_status.get('growth_investment', {}).get('utilization_rate', 0)
            if growth_utilization < 50:
                recommendations.append({
                    'action': 'GROWTH_QUOTA_UTILIZATION',
                    'description': '成長投資枠の活用率が低いため、積極的な投資を推奨します',
                    'priority': 'HIGH',
                    'potential_savings': (self.growth_annual_limit * 0.5) * self.total_tax_rate
                })
            
            # つみたて投資枠の活用推奨
            accumulation_utilization = quota_status.get('accumulation_investment', {}).get('utilization_rate', 0)
            if accumulation_utilization < 50:
                recommendations.append({
                    'action': 'ACCUMULATION_QUOTA_UTILIZATION',
                    'description': 'つみたて投資枠の活用率が低いため、積立投資を推奨します',
                    'priority': 'MEDIUM',
                    'potential_savings': (self.accumulation_annual_limit * 0.5) * self.total_tax_rate
                })
            
            # ポートフォリオの分散推奨
            positions_count = len(portfolio.get('positions', []))
            if positions_count < 3:
                recommendations.append({
                    'action': 'PORTFOLIO_DIVERSIFICATION',
                    'description': 'ポートフォリオの分散を図ることで、リスクを軽減できます',
                    'priority': 'MEDIUM',
                    'potential_savings': 0
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"税務推奨事項生成エラー: {e}")
            return []
    
    def _calculate_potential_tax_savings(self, quota_status: Dict[str, Any], 
                                       portfolio: Dict[str, Any]) -> float:
        """潜在的な税務節約額の計算"""
        try:
            # 未活用枠の計算
            growth_available = quota_status.get('growth_investment', {}).get('available_amount', 0)
            accumulation_available = quota_status.get('accumulation_investment', {}).get('available_amount', 0)
            
            # 潜在的な税務節約額
            potential_savings = (growth_available + accumulation_available) * self.total_tax_rate
            
            return potential_savings
            
        except Exception as e:
            self.logger.error(f"潜在税務節約額計算エラー: {e}")
            return 0.0
    
    def _calculate_optimization_score(self, quota_status: Dict[str, Any], 
                                    portfolio: Dict[str, Any]) -> float:
        """最適化スコアの計算"""
        try:
            # 枠活用率の計算
            growth_utilization = quota_status.get('growth_investment', {}).get('utilization_rate', 0)
            accumulation_utilization = quota_status.get('accumulation_investment', {}).get('utilization_rate', 0)
            
            # ポートフォリオ分散度の計算
            positions_count = len(portfolio.get('positions', []))
            diversification_score = min(positions_count * 20, 100)
            
            # 総合最適化スコア
            utilization_score = (growth_utilization + accumulation_utilization) / 2
            optimization_score = (utilization_score + diversification_score) / 2
            
            return optimization_score
            
        except Exception as e:
            self.logger.error(f"最適化スコア計算エラー: {e}")
            return 0.0
    
    def _determine_priority_level(self, optimization_score: float) -> str:
        """優先度レベルの判定"""
        try:
            if optimization_score >= 80:
                return 'HIGH'
            elif optimization_score >= 60:
                return 'MEDIUM'
            else:
                return 'LOW'
        except Exception as e:
            self.logger.error(f"優先度レベル判定エラー: {e}")
            return 'UNKNOWN'
    
    def calculate_annual_tax_report(self, transactions: List[Dict[str, Any]], 
                                  quota_status: Dict[str, Any]) -> Dict[str, Any]:
        """年間税務レポートの計算"""
        try:
            # 年間取引の集計
            annual_summary = self._summarize_annual_transactions(transactions)
            
            # 税務効果の計算
            tax_effectiveness = self._calculate_tax_effectiveness(annual_summary, quota_status)
            
            # 推奨事項の生成
            recommendations = self._generate_annual_recommendations(annual_summary, quota_status)
            
            return {
                'annual_summary': annual_summary,
                'tax_effectiveness': tax_effectiveness,
                'recommendations': recommendations,
                'report_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"年間税務レポート計算エラー: {e}")
            return {'error': str(e)}
    
    def _summarize_annual_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """年間取引の集計"""
        try:
            total_buy_amount = 0
            total_sell_amount = 0
            growth_transactions = 0
            accumulation_transactions = 0
            
            for transaction in transactions:
                if transaction.get('type') == 'BUY':
                    total_buy_amount += transaction.get('amount', 0)
                elif transaction.get('type') == 'SELL':
                    total_sell_amount += transaction.get('amount', 0)
                
                if transaction.get('quota_type') == 'GROWTH':
                    growth_transactions += 1
                elif transaction.get('quota_type') == 'ACCUMULATION':
                    accumulation_transactions += 1
            
            return {
                'total_buy_amount': total_buy_amount,
                'total_sell_amount': total_sell_amount,
                'net_investment': total_buy_amount - total_sell_amount,
                'growth_transactions': growth_transactions,
                'accumulation_transactions': accumulation_transactions,
                'total_transactions': len(transactions)
            }
            
        except Exception as e:
            self.logger.error(f"年間取引集計エラー: {e}")
            return {}
    
    def _calculate_tax_effectiveness(self, annual_summary: Dict[str, Any], 
                                   quota_status: Dict[str, Any]) -> Dict[str, Any]:
        """税務効果の計算"""
        try:
            net_investment = annual_summary.get('net_investment', 0)
            total_tax_free_amount = quota_status.get('growth_investment', {}).get('used_amount', 0) + \
                                  quota_status.get('accumulation_investment', {}).get('used_amount', 0)
            
            # 税務効果率の計算
            tax_effectiveness_rate = (total_tax_free_amount / net_investment * 100) if net_investment > 0 else 0
            
            # 税務節約額の計算
            tax_savings = total_tax_free_amount * self.total_tax_rate
            
            return {
                'tax_effectiveness_rate': tax_effectiveness_rate,
                'tax_savings': tax_savings,
                'efficiency_score': min(tax_effectiveness_rate, 100)
            }
            
        except Exception as e:
            self.logger.error(f"税務効果計算エラー: {e}")
            return {}
    
    def _generate_annual_recommendations(self, annual_summary: Dict[str, Any], 
                                       quota_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """年間推奨事項の生成"""
        try:
            recommendations = []
            
            # 投資活動の評価
            total_transactions = annual_summary.get('total_transactions', 0)
            if total_transactions < 5:
                recommendations.append({
                    'type': 'INCREASE_ACTIVITY',
                    'description': '投資活動を増やすことで、NISA枠をより効果的に活用できます',
                    'priority': 'MEDIUM'
                })
            
            # 枠活用の評価
            growth_utilization = quota_status.get('growth_investment', {}).get('utilization_rate', 0)
            accumulation_utilization = quota_status.get('accumulation_investment', {}).get('utilization_rate', 0)
            
            if growth_utilization < 80:
                recommendations.append({
                    'type': 'GROWTH_QUOTA_OPTIMIZATION',
                    'description': '成長投資枠の活用を増やすことで、より多くの税務メリットを得られます',
                    'priority': 'HIGH'
                })
            
            if accumulation_utilization < 80:
                recommendations.append({
                    'type': 'ACCUMULATION_QUOTA_OPTIMIZATION',
                    'description': 'つみたて投資枠の活用を増やすことで、長期投資の税務メリットを得られます',
                    'priority': 'MEDIUM'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"年間推奨事項生成エラー: {e}")
            return []
    
    def _calculate_optimization_metrics(self, quota_status: Dict[str, Any], 
                                      portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """最適化指標の計算"""
        try:
            growth_used = quota_status.get('growth_investment', {}).get('used_amount', 0)
            accumulation_used = quota_status.get('accumulation_investment', {}).get('used_amount', 0)
            total_used = growth_used + accumulation_used
            
            # 総合利用率の計算
            total_limit = self.growth_annual_limit + self.accumulation_annual_limit
            overall_utilization = (total_used / total_limit) * 100 if total_limit > 0 else 0
            
            # 目標達成率の計算
            target_achievement = (overall_utilization / self.target_utilization_rate) * 100
            
            # 税務効率の計算
            tax_efficiency = self._calculate_tax_efficiency(quota_status, portfolio)
            
            return {
                'overall_utilization': round(overall_utilization, 2),
                'target_utilization': self.target_utilization_rate,
                'target_achievement': round(target_achievement, 2),
                'tax_efficiency': tax_efficiency,
                'optimization_level': self._determine_optimization_level(overall_utilization),
                'improvement_potential': max(0, self.target_utilization_rate - overall_utilization)
            }
            
        except Exception as e:
            self.logger.error(f"最適化指標計算エラー: {e}")
            return {
                'overall_utilization': 0,
                'target_utilization': self.target_utilization_rate,
                'target_achievement': 0,
                'tax_efficiency': 0,
                'optimization_level': 'UNKNOWN',
                'improvement_potential': self.target_utilization_rate
            }
    
    def _calculate_tax_efficiency(self, quota_status: Dict[str, Any], 
                                 portfolio: Dict[str, Any]) -> float:
        """税務効率の計算"""
        try:
            growth_used = quota_status.get('growth_investment', {}).get('used_amount', 0)
            accumulation_used = quota_status.get('accumulation_investment', {}).get('used_amount', 0)
            total_used = growth_used + accumulation_used
            
            # 税務節約額
            tax_savings = total_used * self.total_tax_rate
            
            # ポートフォリオの未実現損益
            unrealized_profit_loss = portfolio.get('unrealized_profit_loss', 0)
            
            # 税務効率（税務節約額 / 投資額）
            tax_efficiency = (tax_savings / total_used) * 100 if total_used > 0 else 0
            
            return round(tax_efficiency, 2)
            
        except Exception as e:
            self.logger.error(f"税務効率計算エラー: {e}")
            return 0.0
    
    def _determine_optimization_level(self, utilization_rate: float) -> str:
        """最適化レベルの判定"""
        try:
            if utilization_rate >= 90:
                return 'EXCELLENT'
            elif utilization_rate >= 80:
                return 'GOOD'
            elif utilization_rate >= 60:
                return 'FAIR'
            else:
                return 'POOR'
        except Exception as e:
            self.logger.error(f"最適化レベル判定エラー: {e}")
            return 'UNKNOWN'
    
    def _calculate_efficiency_score(self, quota_status: Dict[str, Any], 
                                  portfolio: Dict[str, Any]) -> float:
        """効率スコアの計算"""
        try:
            # 利用率スコア
            growth_utilization = quota_status.get('growth_investment', {}).get('utilization_rate', 0)
            accumulation_utilization = quota_status.get('accumulation_investment', {}).get('utilization_rate', 0)
            utilization_score = (growth_utilization + accumulation_utilization) / 2
            
            # 税務効率スコア
            tax_efficiency = self._calculate_tax_efficiency(quota_status, portfolio)
            tax_score = min(tax_efficiency, 100)
            
            # ポートフォリオ効率スコア
            portfolio_score = self._calculate_portfolio_efficiency(portfolio)
            
            # 総合効率スコア
            efficiency_score = (utilization_score * 0.4 + tax_score * 0.3 + portfolio_score * 0.3)
            
            return round(efficiency_score, 2)
            
        except Exception as e:
            self.logger.error(f"効率スコア計算エラー: {e}")
            return 0.0
    
    def _calculate_portfolio_efficiency(self, portfolio: Dict[str, Any]) -> float:
        """ポートフォリオ効率の計算"""
        try:
            positions = portfolio.get('positions', [])
            if not positions:
                return 0.0
            
            # 分散度スコア
            diversification_score = min(len(positions) * 10, 100)
            
            # リスクスコア（簡易版）
            risk_score = self._calculate_risk_score(positions)
            
            # リターンスコア
            return_score = self._calculate_return_score(portfolio)
            
            # 総合ポートフォリオ効率
            portfolio_efficiency = (diversification_score * 0.4 + risk_score * 0.3 + return_score * 0.3)
            
            return round(portfolio_efficiency, 2)
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ効率計算エラー: {e}")
            return 0.0
    
    def _calculate_risk_score(self, positions: List[Dict[str, Any]]) -> float:
        """リスクスコアの計算"""
        try:
            if not positions:
                return 0.0
            
            # 簡易リスクスコア（銘柄数に基づく）
            position_count = len(positions)
            if position_count >= 10:
                return 100.0
            elif position_count >= 5:
                return 80.0
            elif position_count >= 3:
                return 60.0
            else:
                return 40.0
                
        except Exception as e:
            self.logger.error(f"リスクスコア計算エラー: {e}")
            return 0.0
    
    def _calculate_return_score(self, portfolio: Dict[str, Any]) -> float:
        """リターンスコアの計算"""
        try:
            unrealized_profit_loss = portfolio.get('unrealized_profit_loss', 0)
            total_cost = portfolio.get('total_cost', 0)
            
            if total_cost > 0:
                return_rate = (unrealized_profit_loss / total_cost) * 100
                # リターンスコア（-50%から+50%の範囲で0-100スコア）
                return_score = max(0, min(100, 50 + return_rate))
                return round(return_score, 2)
            else:
                return 50.0  # 中立的なスコア
                
        except Exception as e:
            self.logger.error(f"リターンスコア計算エラー: {e}")
            return 50.0
