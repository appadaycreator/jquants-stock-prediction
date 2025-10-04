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
