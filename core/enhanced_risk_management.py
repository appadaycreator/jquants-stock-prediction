#!/usr/bin/env python3
"""
強化されたリスク管理システム
記事の手法を超える高度なリスク管理機能を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

class EnhancedRiskManagement:
    """強化されたリスク管理システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # リスク管理設定
        self.stop_loss_percentage = self.config.get('stop_loss_percentage', 0.05)  # 5%損切り
        self.take_profit_percentage = self.config.get('take_profit_percentage', 0.10)  # 10%利確
        self.max_drawdown = self.config.get('max_drawdown', 0.15)  # 最大15%ドローダウン
        self.var_confidence = self.config.get('var_confidence', 0.95)  # VaR信頼度95%
        
        # ポジション管理
        self.positions = {}
        self.risk_metrics = {}
        
    def calculate_stop_loss(self, entry_price: float, direction: str, volatility: float = 0.02) -> float:
        """
        動的損切り価格の計算
        記事の固定損切りを超える高度な損切り計算
        """
        try:
            # 基本損切り率
            base_stop_loss = self.stop_loss_percentage
            
            # ボラティリティ調整
            volatility_adjustment = min(volatility * 2, 0.02)  # 最大2%調整
            adjusted_stop_loss = base_stop_loss + volatility_adjustment
            
            # 方向に応じた損切り価格計算
            if direction == 'BUY':
                stop_loss_price = entry_price * (1 - adjusted_stop_loss)
            else:  # SELL
                stop_loss_price = entry_price * (1 + adjusted_stop_loss)
            
            return stop_loss_price
            
        except Exception as e:
            self.logger.error(f"損切り価格計算エラー: {e}")
            return entry_price * (1 - self.stop_loss_percentage) if direction == 'BUY' else entry_price * (1 + self.stop_loss_percentage)
    
    def calculate_take_profit(self, entry_price: float, direction: str, confidence: float = 0.7) -> float:
        """
        動的利確価格の計算
        信頼度に基づく利確価格の調整
        """
        try:
            # 基本利確率
            base_take_profit = self.take_profit_percentage
            
            # 信頼度調整
            confidence_adjustment = (confidence - 0.5) * 0.1  # 信頼度に応じて調整
            adjusted_take_profit = base_take_profit + confidence_adjustment
            
            # 方向に応じた利確価格計算
            if direction == 'BUY':
                take_profit_price = entry_price * (1 + adjusted_take_profit)
            else:  # SELL
                take_profit_price = entry_price * (1 - adjusted_take_profit)
            
            return take_profit_price
            
        except Exception as e:
            self.logger.error(f"利確価格計算エラー: {e}")
            return entry_price * (1 + self.take_profit_percentage) if direction == 'BUY' else entry_price * (1 - self.take_profit_percentage)
    
    def calculate_position_size(self, account_balance: float, risk_per_trade: float, 
                              entry_price: float, stop_loss_price: float) -> float:
        """
        リスクベースのポジションサイズ計算
        記事の固定1株を超える高度なポジションサイジング
        """
        try:
            # リスク金額の計算
            risk_amount = account_balance * risk_per_trade
            
            # 1株あたりのリスク
            risk_per_share = abs(entry_price - stop_loss_price)
            
            # ポジションサイズの計算
            if risk_per_share > 0:
                position_size = risk_amount / risk_per_share
            else:
                position_size = 0
            
            # 最大ポジションサイズの制限（口座残高の20%まで）
            max_position_value = account_balance * 0.2
            max_position_size = max_position_value / entry_price
            
            position_size = min(position_size, max_position_size)
            
            return max(0, position_size)
            
        except Exception as e:
            self.logger.error(f"ポジションサイズ計算エラー: {e}")
            return 0.0
    
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """
        Value at Risk (VaR) の計算
        記事にはない高度なリスク指標
        """
        try:
            if not returns:
                return 0.0
            
            # リターンの配列をnumpy配列に変換
            returns_array = np.array(returns)
            
            # VaRの計算（パーセンタイル法）
            var_percentile = (1 - confidence) * 100
            var_value = np.percentile(returns_array, var_percentile)
            
            return abs(var_value)
            
        except Exception as e:
            self.logger.error(f"VaR計算エラー: {e}")
            return 0.0
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Dict[str, float]:
        """
        最大ドローダウンの計算
        記事にはない高度なリスク指標
        """
        try:
            if not equity_curve:
                return {'max_drawdown': 0.0, 'max_drawdown_duration': 0}
            
            equity_array = np.array(equity_curve)
            
            # ピーク価格の計算
            peak_prices = np.maximum.accumulate(equity_array)
            
            # ドローダウンの計算
            drawdowns = (equity_array - peak_prices) / peak_prices
            
            # 最大ドローダウン
            max_drawdown = abs(np.min(drawdowns))
            
            # 最大ドローダウン期間の計算
            drawdown_duration = 0
            current_drawdown_duration = 0
            
            for i, dd in enumerate(drawdowns):
                if dd < 0:
                    current_drawdown_duration += 1
                    drawdown_duration = max(drawdown_duration, current_drawdown_duration)
                else:
                    current_drawdown_duration = 0
            
            return {
                'max_drawdown': max_drawdown,
                'max_drawdown_duration': drawdown_duration
            }
            
        except Exception as e:
            self.logger.error(f"最大ドローダウン計算エラー: {e}")
            return {'max_drawdown': 0.0, 'max_drawdown_duration': 0}
    
    def check_risk_limits(self, current_price: float, position: Dict[str, Any]) -> Dict[str, Any]:
        """
        リスク制限のチェック
        損切り・利確の自動判定
        """
        try:
            entry_price = position['entry_price']
            direction = position['direction']
            stop_loss = position.get('stop_loss', 0)
            take_profit = position.get('take_profit', 0)
            
            # 損切りチェック
            stop_loss_triggered = False
            if direction == 'BUY' and current_price <= stop_loss:
                stop_loss_triggered = True
            elif direction == 'SELL' and current_price >= stop_loss:
                stop_loss_triggered = True
            
            # 利確チェック
            take_profit_triggered = False
            if direction == 'BUY' and current_price >= take_profit:
                take_profit_triggered = True
            elif direction == 'SELL' and current_price <= take_profit:
                take_profit_triggered = True
            
            # リスク判定
            risk_action = 'HOLD'
            if stop_loss_triggered:
                risk_action = 'STOP_LOSS'
            elif take_profit_triggered:
                risk_action = 'TAKE_PROFIT'
            
            return {
                'risk_action': risk_action,
                'stop_loss_triggered': stop_loss_triggered,
                'take_profit_triggered': take_profit_triggered,
                'current_price': current_price,
                'entry_price': entry_price,
                'unrealized_pnl': self._calculate_unrealized_pnl(current_price, position)
            }
            
        except Exception as e:
            self.logger.error(f"リスク制限チェックエラー: {e}")
            return {
                'risk_action': 'HOLD',
                'stop_loss_triggered': False,
                'take_profit_triggered': False,
                'current_price': current_price,
                'entry_price': 0,
                'unrealized_pnl': 0
            }
    
    def _calculate_unrealized_pnl(self, current_price: float, position: Dict[str, Any]) -> float:
        """未実現損益の計算"""
        try:
            entry_price = position['entry_price']
            direction = position['direction']
            position_size = position.get('position_size', 0)
            
            if direction == 'BUY':
                pnl = (current_price - entry_price) * position_size
            else:  # SELL
                pnl = (entry_price - current_price) * position_size
            
            return pnl
            
        except Exception as e:
            self.logger.error(f"未実現損益計算エラー: {e}")
            return 0.0
    
    def create_position(self, symbol: str, direction: str, entry_price: float, 
                       position_size: float, confidence: float, volatility: float = 0.02) -> Dict[str, Any]:
        """
        ポジションの作成
        リスク管理パラメータを自動設定
        """
        try:
            # 損切り・利確価格の計算
            stop_loss = self.calculate_stop_loss(entry_price, direction, volatility)
            take_profit = self.calculate_take_profit(entry_price, direction, confidence)
            
            position = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': entry_price,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'volatility': volatility,
                'created_at': datetime.now().isoformat(),
                'status': 'ACTIVE'
            }
            
            # ポジション管理に追加
            self.positions[symbol] = position
            
            return position
            
        except Exception as e:
            self.logger.error(f"ポジション作成エラー: {e}")
            return {}
    
    def update_position(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """
        ポジションの更新
        リスク管理の自動実行
        """
        try:
            if symbol not in self.positions:
                return {'error': 'ポジションが見つかりません'}
            
            position = self.positions[symbol]
            
            # リスク制限のチェック
            risk_check = self.check_risk_limits(current_price, position)
            
            # ポジションの更新
            position['current_price'] = current_price
            position['unrealized_pnl'] = risk_check['unrealized_pnl']
            position['updated_at'] = datetime.now().isoformat()
            
            # リスクアクションの実行
            if risk_check['risk_action'] != 'HOLD':
                position['status'] = 'CLOSED'
                position['close_reason'] = risk_check['risk_action']
                position['closed_at'] = datetime.now().isoformat()
            
            return {
                'position': position,
                'risk_check': risk_check
            }
            
        except Exception as e:
            self.logger.error(f"ポジション更新エラー: {e}")
            return {'error': str(e)}
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """リスクサマリーの取得"""
        try:
            active_positions = [p for p in self.positions.values() if p['status'] == 'ACTIVE']
            closed_positions = [p for p in self.positions.values() if p['status'] == 'CLOSED']
            
            # 総未実現損益
            total_unrealized_pnl = sum(p.get('unrealized_pnl', 0) for p in active_positions)
            
            # リスク指標
            risk_metrics = {
                'active_positions': len(active_positions),
                'closed_positions': len(closed_positions),
                'total_unrealized_pnl': total_unrealized_pnl,
                'avg_confidence': np.mean([p.get('confidence', 0) for p in active_positions]) if active_positions else 0,
                'high_risk_positions': len([p for p in active_positions if p.get('volatility', 0) > 0.03])
            }
            
            return risk_metrics
            
        except Exception as e:
            self.logger.error(f"リスクサマリー取得エラー: {e}")
            return {'error': str(e)}
    
    def calculate_portfolio_risk_metrics(self, account_balance: float) -> Dict[str, Any]:
        """ポートフォリオリスクメトリクスの計算"""
        try:
            active_positions = [p for p in self.positions.values() if p['status'] == 'ACTIVE']
            
            if not active_positions:
                return {
                    'portfolio_var': 0.0,
                    'portfolio_volatility': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                    'risk_score': 0.0
                }
            
            # ポートフォリオVaR計算
            portfolio_var = self._calculate_portfolio_var(active_positions, account_balance)
            
            # ポートフォリオボラティリティ計算
            portfolio_volatility = self._calculate_portfolio_volatility(active_positions)
            
            # 最大ドローダウン計算
            max_drawdown = self._calculate_portfolio_max_drawdown(active_positions)
            
            # シャープレシオ計算
            sharpe_ratio = self._calculate_portfolio_sharpe_ratio(active_positions)
            
            # 総合リスクスコア計算
            risk_score = self._calculate_portfolio_risk_score(
                portfolio_var, portfolio_volatility, max_drawdown, sharpe_ratio
            )
            
            return {
                'portfolio_var': portfolio_var,
                'portfolio_volatility': portfolio_volatility,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'risk_score': risk_score,
                'position_count': len(active_positions),
                'total_exposure': sum(p.get('position_size', 0) * p.get('current_price', 0) for p in active_positions),
                'exposure_ratio': sum(p.get('position_size', 0) * p.get('current_price', 0) for p in active_positions) / account_balance
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスクメトリクス計算エラー: {e}")
            return {'error': str(e)}
    
    def _calculate_portfolio_var(self, positions: List[Dict[str, Any]], account_balance: float) -> float:
        """ポートフォリオVaR計算"""
        try:
            if not positions:
                return 0.0
            
            # 各ポジションのVaR計算
            position_vars = []
            for position in positions:
                position_value = position.get('position_size', 0) * position.get('current_price', 0)
                volatility = position.get('volatility', 0.02)
                position_var = position_value * volatility * 1.96  # 95%信頼区間
                position_vars.append(position_var)
            
            # ポートフォリオVaR（簡易版：各ポジションのVaRの合計）
            portfolio_var = sum(position_vars)
            
            return portfolio_var / account_balance  # 正規化
            
        except Exception as e:
            self.logger.error(f"ポートフォリオVaR計算エラー: {e}")
            return 0.0
    
    def _calculate_portfolio_volatility(self, positions: List[Dict[str, Any]]) -> float:
        """ポートフォリオボラティリティ計算"""
        try:
            if not positions:
                return 0.0
            
            # 各ポジションのボラティリティの加重平均
            total_value = sum(p.get('position_size', 0) * p.get('current_price', 0) for p in positions)
            
            if total_value == 0:
                return 0.0
            
            weighted_volatility = 0.0
            for position in positions:
                position_value = position.get('position_size', 0) * position.get('current_price', 0)
                volatility = position.get('volatility', 0.02)
                weight = position_value / total_value
                weighted_volatility += volatility * weight
            
            return weighted_volatility
            
        except Exception as e:
            self.logger.error(f"ポートフォリオボラティリティ計算エラー: {e}")
            return 0.0
    
    def _calculate_portfolio_max_drawdown(self, positions: List[Dict[str, Any]]) -> float:
        """ポートフォリオ最大ドローダウン計算"""
        try:
            if not positions:
                return 0.0
            
            # 各ポジションの最大ドローダウン計算
            max_drawdowns = []
            for position in positions:
                entry_price = position.get('entry_price', 0)
                current_price = position.get('current_price', entry_price)
                
                if entry_price > 0:
                    drawdown = max(0, (entry_price - current_price) / entry_price)
                    max_drawdowns.append(drawdown)
            
            return max(max_drawdowns) if max_drawdowns else 0.0
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ最大ドローダウン計算エラー: {e}")
            return 0.0
    
    def _calculate_portfolio_sharpe_ratio(self, positions: List[Dict[str, Any]]) -> float:
        """ポートフォリオシャープレシオ計算"""
        try:
            if not positions:
                return 0.0
            
            # 各ポジションの期待リターンとリスク計算
            total_return = 0.0
            total_risk = 0.0
            
            for position in positions:
                confidence = position.get('confidence', 0.7)
                volatility = position.get('volatility', 0.02)
                
                # 期待リターン（信頼度ベース）
                expected_return = confidence * 0.1
                total_return += expected_return
                total_risk += volatility
            
            # 平均リターンとリスク
            avg_return = total_return / len(positions)
            avg_risk = total_risk / len(positions)
            
            # シャープレシオ計算
            if avg_risk > 0:
                return avg_return / avg_risk
            else:
                return 0.0
            
        except Exception as e:
            self.logger.error(f"ポートフォリオシャープレシオ計算エラー: {e}")
            return 0.0
    
    def _calculate_portfolio_risk_score(self, portfolio_var: float, portfolio_volatility: float, 
                                      max_drawdown: float, sharpe_ratio: float) -> float:
        """ポートフォリオリスクスコア計算"""
        try:
            # リスクスコア計算（0-100）
            var_score = min(100, portfolio_var * 1000)  # VaRスコア
            volatility_score = min(100, portfolio_volatility * 1000)  # ボラティリティスコア
            drawdown_score = min(100, max_drawdown * 100)  # ドローダウンスコア
            sharpe_score = max(0, 100 - sharpe_ratio * 10)  # シャープレシオスコア（逆転）
            
            # 総合リスクスコア
            risk_score = (var_score + volatility_score + drawdown_score + sharpe_score) / 4
            
            return min(100, max(0, risk_score))
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスクスコア計算エラー: {e}")
            return 50.0  # デフォルト値
    
    def set_individual_stock_limits(self, symbol: str, max_loss_amount: float) -> bool:
        """個別銘柄の最大損失額設定"""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            position['max_loss_amount'] = max_loss_amount
            
            # 最大損失額に基づく損切り価格の再計算
            entry_price = position['entry_price']
            direction = position['direction']
            
            if direction == 'BUY':
                max_loss_price = entry_price - max_loss_amount / position.get('position_size', 1)
                position['stop_loss'] = max(position.get('stop_loss', 0), max_loss_price)
            else:  # SELL
                max_loss_price = entry_price + max_loss_amount / position.get('position_size', 1)
                position['stop_loss'] = min(position.get('stop_loss', float('inf')), max_loss_price)
            
            return True
            
        except Exception as e:
            self.logger.error(f"個別銘柄損失額設定エラー: {e}")
            return False
    
    def get_risk_alerts(self) -> List[Dict[str, Any]]:
        """リスクアラートの取得"""
        try:
            alerts = []
            active_positions = [p for p in self.positions.values() if p['status'] == 'ACTIVE']
            
            for position in active_positions:
                symbol = position['symbol']
                current_price = position.get('current_price', position['entry_price'])
                entry_price = position['entry_price']
                volatility = position.get('volatility', 0.02)
                confidence = position.get('confidence', 0.7)
                
                # 価格変動アラート
                price_change = (current_price - entry_price) / entry_price
                if abs(price_change) > 0.05:  # 5%以上の変動
                    alerts.append({
                        'type': 'PRICE_MOVEMENT',
                        'symbol': symbol,
                        'message': f'価格変動が大きいです: {price_change:.2%}',
                        'severity': 'HIGH' if abs(price_change) > 0.1 else 'MEDIUM',
                        'current_price': current_price,
                        'price_change': price_change
                    })
                
                # 高ボラティリティアラート
                if volatility > 0.05:  # 5%以上のボラティリティ
                    alerts.append({
                        'type': 'HIGH_VOLATILITY',
                        'symbol': symbol,
                        'message': f'ボラティリティが高いです: {volatility:.2%}',
                        'severity': 'HIGH',
                        'volatility': volatility
                    })
                
                # 低信頼度アラート
                if confidence < 0.6:  # 60%未満の信頼度
                    alerts.append({
                        'type': 'LOW_CONFIDENCE',
                        'symbol': symbol,
                        'message': f'信頼度が低いです: {confidence:.1%}',
                        'severity': 'MEDIUM',
                        'confidence': confidence
                    })
                
                # 最大損失額アラート
                max_loss_amount = position.get('max_loss_amount')
                if max_loss_amount:
                    current_loss = abs((current_price - entry_price) * position.get('position_size', 0))
                    if current_loss > max_loss_amount * 0.8:  # 80%以上
                        alerts.append({
                            'type': 'LOSS_LIMIT_WARNING',
                            'symbol': symbol,
                            'message': f'最大損失額に近づいています: {current_loss:.0f}円',
                            'severity': 'HIGH',
                            'current_loss': current_loss,
                            'max_loss_amount': max_loss_amount
                        })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"リスクアラート取得エラー: {e}")
            return []
    
    def get_risk_recommendations(self) -> List[Dict[str, Any]]:
        """リスク推奨事項の取得"""
        try:
            recommendations = []
            active_positions = [p for p in self.positions.values() if p['status'] == 'ACTIVE']
            
            if not active_positions:
                return recommendations
            
            # ポートフォリオリスクメトリクス取得
            risk_metrics = self.calculate_portfolio_risk_metrics(1000000.0)  # 仮の残高
            
            # 高リスク推奨事項
            if risk_metrics.get('risk_score', 0) > 70:
                recommendations.append({
                    'type': 'REDUCE_RISK',
                    'message': 'ポートフォリオのリスクが高いため、ポジションサイズを削減することを推奨',
                    'priority': 'HIGH',
                    'risk_score': risk_metrics.get('risk_score', 0)
                })
            
            # 高ボラティリティ推奨事項
            if risk_metrics.get('portfolio_volatility', 0) > 0.05:
                recommendations.append({
                    'type': 'VOLATILITY_WARNING',
                    'message': 'ポートフォリオのボラティリティが高いため、分散投資を検討',
                    'priority': 'MEDIUM',
                    'volatility': risk_metrics.get('portfolio_volatility', 0)
                })
            
            # 高エクスポージャー推奨事項
            if risk_metrics.get('exposure_ratio', 0) > 0.8:
                recommendations.append({
                    'type': 'HIGH_EXPOSURE',
                    'message': 'ポートフォリオのエクスポージャーが高いため、現金比率を増やすことを推奨',
                    'priority': 'HIGH',
                    'exposure_ratio': risk_metrics.get('exposure_ratio', 0)
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"リスク推奨事項取得エラー: {e}")
            return []