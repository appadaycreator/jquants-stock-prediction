#!/usr/bin/env python3
"""
信頼度ベースの取引判定システム
記事の手法を超える高精度な取引判定を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging

class ConfidenceBasedTrading:
    """信頼度ベースの取引判定システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 信頼度設定
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.max_confidence = self.config.get('max_confidence', 0.95)
        
        # リスク管理設定
        self.risk_adjustment = self.config.get('risk_adjustment', True)
        self.volatility_threshold = self.config.get('volatility_threshold', 0.02)
        
        # 取引履歴
        self.trade_history = []
        self.performance_metrics = {}
        
    def calculate_confidence(self, prediction: float, market_data: Dict[str, Any]) -> float:
        """
        予測の信頼度を計算
        記事の単純な0.5閾値を超える高度な信頼度計算
        """
        try:
            # 基本信頼度（予測値の絶対値に基づく）
            base_confidence = abs(prediction - 0.5) * 2  # 0.5からの距離を2倍
            
            # 市場データに基づく調整
            market_adjustment = self._calculate_market_adjustment(market_data)
            
            # ボラティリティ調整
            volatility_adjustment = self._calculate_volatility_adjustment(market_data)
            
            # 最終信頼度の計算
            confidence = base_confidence * market_adjustment * volatility_adjustment
            
            # 信頼度の範囲制限
            confidence = max(self.min_confidence, min(confidence, self.max_confidence))
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"信頼度計算エラー: {e}")
            return self.min_confidence
    
    def _calculate_market_adjustment(self, market_data: Dict[str, Any]) -> float:
        """市場データに基づく信頼度調整"""
        try:
            # 出来高の正規化
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume)
            volume_ratio = min(volume / avg_volume, 2.0) if avg_volume > 0 else 1.0
            
            # 価格変動の安定性
            price_change = abs(market_data.get('price_change', 0))
            stability_factor = max(0.5, 1.0 - price_change * 10)
            
            # 市場調整係数
            market_adjustment = (volume_ratio * stability_factor) / 2.0
            
            return max(0.5, min(market_adjustment, 1.5))
            
        except Exception as e:
            self.logger.error(f"市場調整計算エラー: {e}")
            return 1.0
    
    def _calculate_volatility_adjustment(self, market_data: Dict[str, Any]) -> float:
        """ボラティリティに基づく信頼度調整"""
        try:
            volatility = market_data.get('volatility', 0)
            
            # ボラティリティが高い場合は信頼度を下げる
            if volatility > self.volatility_threshold:
                adjustment = 1.0 - (volatility - self.volatility_threshold) * 2
                return max(0.3, adjustment)
            
            return 1.0
            
        except Exception as e:
            self.logger.error(f"ボラティリティ調整計算エラー: {e}")
            return 1.0
    
    def should_trade(self, prediction: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        取引すべきかを判定
        記事の単純な0.5閾値を超える高度な判定
        """
        try:
            # 信頼度計算
            confidence = self.calculate_confidence(prediction, market_data)
            
            # 取引判定
            should_trade = confidence >= self.confidence_threshold
            
            # 取引方向の判定
            if should_trade:
                if prediction >= 0.5:
                    trade_direction = 'BUY'
                    trade_strength = min((prediction - 0.5) * 2, 1.0)
                else:
                    trade_direction = 'SELL'
                    trade_strength = min((0.5 - prediction) * 2, 1.0)
            else:
                trade_direction = 'HOLD'
                trade_strength = 0.0
            
            # リスクレベル計算
            risk_level = self._calculate_risk_level(market_data)
            
            # ポジションサイズ計算
            position_size = self._calculate_position_size(confidence, risk_level)
            
            return {
                'should_trade': should_trade,
                'confidence': confidence,
                'trade_direction': trade_direction,
                'trade_strength': trade_strength,
                'risk_level': risk_level,
                'position_size': position_size,
                'prediction': prediction,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"取引判定エラー: {e}")
            return {
                'should_trade': False,
                'confidence': 0.0,
                'trade_direction': 'HOLD',
                'trade_strength': 0.0,
                'risk_level': 'HIGH',
                'position_size': 0.0,
                'prediction': prediction,
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_risk_level(self, market_data: Dict[str, Any]) -> str:
        """リスクレベルの計算"""
        try:
            volatility = market_data.get('volatility', 0)
            price_change = abs(market_data.get('price_change', 0))
            
            # リスクスコア計算
            risk_score = volatility * 2 + price_change * 5
            
            if risk_score < 0.1:
                return 'LOW'
            elif risk_score < 0.3:
                return 'MEDIUM'
            else:
                return 'HIGH'
                
        except Exception as e:
            self.logger.error(f"リスクレベル計算エラー: {e}")
            return 'HIGH'
    
    def _calculate_position_size(self, confidence: float, risk_level: str) -> float:
        """ポジションサイズの計算"""
        try:
            # 基本ポジションサイズ（信頼度に基づく）
            base_size = confidence * 100  # 最大100株
            
            # リスクレベルによる調整
            risk_multiplier = {
                'LOW': 1.0,
                'MEDIUM': 0.7,
                'HIGH': 0.3
            }.get(risk_level, 0.3)
            
            position_size = base_size * risk_multiplier
            
            return max(0, min(position_size, 100))  # 0-100株の範囲
            
        except Exception as e:
            self.logger.error(f"ポジションサイズ計算エラー: {e}")
            return 0.0
    
    def execute_trade(self, trade_decision: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """取引の実行"""
        try:
            if not trade_decision['should_trade']:
                return {
                    'executed': False,
                    'reason': '信頼度不足',
                    'trade_decision': trade_decision
                }
            
            # 取引実行のシミュレーション
            trade_result = {
                'executed': True,
                'direction': trade_decision['trade_direction'],
                'position_size': trade_decision['position_size'],
                'confidence': trade_decision['confidence'],
                'risk_level': trade_decision['risk_level'],
                'entry_price': market_data.get('current_price', 0),
                'timestamp': datetime.now().isoformat(),
                'trade_decision': trade_decision
            }
            
            # 取引履歴に追加
            self.trade_history.append(trade_result)
            
            return trade_result
            
        except Exception as e:
            self.logger.error(f"取引実行エラー: {e}")
            return {
                'executed': False,
                'reason': f'取引実行エラー: {e}',
                'trade_decision': trade_decision
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンス指標の計算"""
        try:
            if not self.trade_history:
                return {
                    'total_trades': 0,
                    'success_rate': 0.0,
                    'avg_confidence': 0.0,
                    'risk_distribution': {}
                }
            
            # 基本統計
            total_trades = len(self.trade_history)
            avg_confidence = np.mean([trade['confidence'] for trade in self.trade_history])
            
            # リスク分布
            risk_levels = [trade['risk_level'] for trade in self.trade_history]
            risk_distribution = {
                'LOW': risk_levels.count('LOW'),
                'MEDIUM': risk_levels.count('MEDIUM'),
                'HIGH': risk_levels.count('HIGH')
            }
            
            return {
                'total_trades': total_trades,
                'avg_confidence': avg_confidence,
                'risk_distribution': risk_distribution,
                'confidence_threshold': self.confidence_threshold,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"パフォーマンス指標計算エラー: {e}")
            return {
                'total_trades': 0,
                'success_rate': 0.0,
                'avg_confidence': 0.0,
                'risk_distribution': {},
                'error': str(e)
            }
