#!/usr/bin/env python3
"""
高度なポジションサイジングシステム
記事の固定1株を超える高度なポジションサイジング機能を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging

class AdvancedPositionSizing:
    """高度なポジションサイジングシステム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # ポジションサイジング設定
        self.max_position_percent = self.config.get('max_position_percent', 0.2)  # 最大20%
        self.base_position_size = self.config.get('base_position_size', 100)  # 基本100株
        self.risk_per_trade = self.config.get('risk_per_trade', 0.02)  # 取引あたり2%リスク
        
        # 信頼度ベースの設定
        self.confidence_multiplier = self.config.get('confidence_multiplier', 2.0)
        self.min_confidence = self.config.get('min_confidence', 0.6)
        
        # ボラティリティベースの設定
        self.volatility_adjustment = self.config.get('volatility_adjustment', True)
        self.max_volatility = self.config.get('max_volatility', 0.05)  # 最大5%ボラティリティ
        
        # 相関ベースの設定
        self.correlation_adjustment = self.config.get('correlation_adjustment', True)
        self.max_correlation = self.config.get('max_correlation', 0.7)  # 最大70%相関
        
    def calculate_position_size(self, account_balance: float, stock_price: float, 
                              confidence: float, volatility: float = 0.02, 
                              correlation: float = 0.0, risk_level: str = 'MEDIUM') -> Dict[str, Any]:
        """
        高度なポジションサイズの計算
        記事の固定1株を超える高度な計算
        """
        try:
            # 基本ポジションサイズの計算
            base_size = self._calculate_base_position_size(account_balance, stock_price, confidence)
            
            # リスク調整
            risk_adjusted_size = self._apply_risk_adjustment(base_size, risk_level)
            
            # ボラティリティ調整
            if self.volatility_adjustment:
                volatility_adjusted_size = self._apply_volatility_adjustment(risk_adjusted_size, volatility)
            else:
                volatility_adjusted_size = risk_adjusted_size
            
            # 相関調整
            if self.correlation_adjustment:
                correlation_adjusted_size = self._apply_correlation_adjustment(volatility_adjusted_size, correlation)
            else:
                correlation_adjusted_size = volatility_adjusted_size
            
            # 最終調整
            final_size = self._apply_final_adjustments(correlation_adjusted_size, account_balance, stock_price)
            
            return {
                'position_size': final_size,
                'base_size': base_size,
                'risk_adjusted_size': risk_adjusted_size,
                'volatility_adjusted_size': volatility_adjusted_size,
                'correlation_adjusted_size': correlation_adjusted_size,
                'confidence': confidence,
                'volatility': volatility,
                'correlation': correlation,
                'risk_level': risk_level,
                'position_value': final_size * stock_price,
                'position_percent': (final_size * stock_price) / account_balance * 100
            }
            
        except Exception as e:
            self.logger.error(f"ポジションサイズ計算エラー: {e}")
            return {
                'position_size': 0,
                'error': str(e)
            }
    
    def _calculate_base_position_size(self, account_balance: float, stock_price: float, confidence: float) -> float:
        """基本ポジションサイズの計算"""
        try:
            # 信頼度に基づく基本サイズ
            confidence_factor = (confidence - 0.5) * self.confidence_multiplier
            base_size = self.base_position_size * confidence_factor
            
            # 資本制限
            max_position_value = account_balance * self.max_position_percent
            max_size = max_position_value / stock_price
            
            base_size = min(base_size, max_size)
            
            return max(0, base_size)
            
        except Exception as e:
            self.logger.error(f"基本ポジションサイズ計算エラー: {e}")
            return 0.0
    
    def _apply_risk_adjustment(self, base_size: float, risk_level: str) -> float:
        """リスクレベルに基づく調整"""
        try:
            risk_multipliers = {
                'LOW': 1.0,
                'MEDIUM': 0.7,
                'HIGH': 0.3,
                'CRITICAL': 0.1
            }
            
            risk_multiplier = risk_multipliers.get(risk_level, 0.5)
            adjusted_size = base_size * risk_multiplier
            
            return max(0, adjusted_size)
            
        except Exception as e:
            self.logger.error(f"リスク調整エラー: {e}")
            return base_size
    
    def _apply_volatility_adjustment(self, base_size: float, volatility: float) -> float:
        """ボラティリティに基づく調整"""
        try:
            if volatility > self.max_volatility:
                # 高ボラティリティの場合はサイズを削減
                volatility_factor = self.max_volatility / volatility
                adjusted_size = base_size * volatility_factor
            else:
                # 低ボラティリティの場合はサイズを増加
                volatility_factor = 1.0 + (self.max_volatility - volatility) * 0.5
                adjusted_size = base_size * volatility_factor
            
            return max(0, adjusted_size)
            
        except Exception as e:
            self.logger.error(f"ボラティリティ調整エラー: {e}")
            return base_size
    
    def _apply_correlation_adjustment(self, base_size: float, correlation: float) -> float:
        """相関に基づく調整"""
        try:
            if correlation > self.max_correlation:
                # 高相関の場合はサイズを削減
                correlation_factor = 1.0 - (correlation - self.max_correlation)
                adjusted_size = base_size * correlation_factor
            else:
                # 低相関の場合はサイズを維持
                adjusted_size = base_size
            
            return max(0, adjusted_size)
            
        except Exception as e:
            self.logger.error(f"相関調整エラー: {e}")
            return base_size
    
    def _apply_final_adjustments(self, base_size: float, account_balance: float, stock_price: float) -> float:
        """最終調整の適用"""
        try:
            # 最小・最大サイズの制限
            min_size = 1  # 最小1株
            max_size = account_balance * self.max_position_percent / stock_price
            
            # サイズの調整
            adjusted_size = max(min_size, min(base_size, max_size))
            
            # 整数化
            final_size = int(adjusted_size)
            
            return max(0, final_size)
            
        except Exception as e:
            self.logger.error(f"最終調整エラー: {e}")
            return 0
    
    def calculate_portfolio_position_sizes(self, account_balance: float, 
                                          stock_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ポートフォリオ全体のポジションサイズ計算
        複数銘柄の最適な配分を計算
        """
        try:
            total_positions = {}
            remaining_balance = account_balance
            
            # 各銘柄のポジションサイズを計算
            for stock in stock_data:
                symbol = stock['symbol']
                price = stock['price']
                confidence = stock.get('confidence', 0.7)
                volatility = stock.get('volatility', 0.02)
                correlation = stock.get('correlation', 0.0)
                risk_level = stock.get('risk_level', 'MEDIUM')
                
                # ポジションサイズの計算
                position_info = self.calculate_position_size(
                    remaining_balance, price, confidence, volatility, correlation, risk_level
                )
                
                if position_info['position_size'] > 0:
                    total_positions[symbol] = position_info
                    remaining_balance -= position_info['position_value']
            
            # ポートフォリオ統計
            total_position_value = sum(pos['position_value'] for pos in total_positions.values())
            portfolio_percent = total_position_value / account_balance * 100
            
            return {
                'positions': total_positions,
                'total_position_value': total_position_value,
                'remaining_balance': remaining_balance,
                'portfolio_percent': portfolio_percent,
                'diversification_score': self._calculate_diversification_score(total_positions)
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオポジションサイズ計算エラー: {e}")
            return {'error': str(e)}
    
    def _calculate_diversification_score(self, positions: Dict[str, Any]) -> float:
        """分散投資スコアの計算"""
        try:
            if not positions:
                return 0.0
            
            # ポジション数の分散
            position_count = len(positions)
            count_score = min(position_count / 10, 1.0)  # 最大10銘柄で1.0
            
            # ポジションサイズの分散
            position_values = [pos['position_value'] for pos in positions.values()]
            if position_values:
                size_variance = np.var(position_values)
                size_score = max(0, 1.0 - size_variance / np.mean(position_values))
            else:
                size_score = 0.0
            
            # 総合スコア
            diversification_score = (count_score + size_score) / 2
            
            return diversification_score
            
        except Exception as e:
            self.logger.error(f"分散投資スコア計算エラー: {e}")
            return 0.0
    
    def optimize_position_sizes(self, account_balance: float, 
                              stock_data: List[Dict[str, Any]], 
                              target_return: float = 0.1, 
                              max_risk: float = 0.15) -> Dict[str, Any]:
        """
        ポジションサイズの最適化
        目標リターンとリスク制限に基づく最適化
        """
        try:
            # 最適化の実行
            optimized_positions = {}
            total_risk = 0.0
            expected_return = 0.0
            
            # 各銘柄の最適化
            for stock in stock_data:
                symbol = stock['symbol']
                price = stock['price']
                confidence = stock.get('confidence', 0.7)
                volatility = stock.get('volatility', 0.02)
                correlation = stock.get('correlation', 0.0)
                risk_level = stock.get('risk_level', 'MEDIUM')
                
                # 最適化されたポジションサイズ
                position_info = self.calculate_position_size(
                    account_balance, price, confidence, volatility, correlation, risk_level
                )
                
                # リスク制限のチェック
                position_risk = position_info['position_size'] * price * volatility / account_balance
                if total_risk + position_risk <= max_risk:
                    optimized_positions[symbol] = position_info
                    total_risk += position_risk
                    expected_return += position_info['position_size'] * price * confidence / account_balance
            
            return {
                'optimized_positions': optimized_positions,
                'total_risk': total_risk,
                'expected_return': expected_return,
                'risk_utilization': total_risk / max_risk * 100,
                'return_target_achievement': expected_return / target_return * 100
            }
            
        except Exception as e:
            self.logger.error(f"ポジションサイズ最適化エラー: {e}")
            return {'error': str(e)}
    
    def get_position_sizing_recommendations(self, account_balance: float, 
                                          stock_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ポジションサイジングの推奨事項"""
        try:
            recommendations = []
            
            for stock in stock_data:
                symbol = stock['symbol']
                confidence = stock.get('confidence', 0.7)
                volatility = stock.get('volatility', 0.02)
                risk_level = stock.get('risk_level', 'MEDIUM')
                
                # 推奨事項の生成
                if confidence < self.min_confidence:
                    recommendations.append({
                        'symbol': symbol,
                        'type': 'LOW_CONFIDENCE',
                        'message': f'信頼度が低いため取引を控えることを推奨',
                        'confidence': confidence
                    })
                elif volatility > self.max_volatility:
                    recommendations.append({
                        'symbol': symbol,
                        'type': 'HIGH_VOLATILITY',
                        'message': f'ボラティリティが高いためポジションサイズを削減',
                        'volatility': volatility
                    })
                elif risk_level == 'HIGH':
                    recommendations.append({
                        'symbol': symbol,
                        'type': 'HIGH_RISK',
                        'message': f'リスクレベルが高いため注意深く監視',
                        'risk_level': risk_level
                    })
                else:
                    recommendations.append({
                        'symbol': symbol,
                        'type': 'GOOD',
                        'message': f'取引条件が良好',
                        'confidence': confidence
                    })
            
            return {
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'high_priority': len([r for r in recommendations if r['type'] in ['LOW_CONFIDENCE', 'HIGH_VOLATILITY']])
            }
            
        except Exception as e:
            self.logger.error(f"推奨事項生成エラー: {e}")
            return {'error': str(e)}
