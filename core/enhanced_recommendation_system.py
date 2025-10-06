"""
強化された推奨事項生成システム
ポートフォリオ最適化に基づく包括的な投資推奨システム
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class RecommendationType(Enum):
    """推奨タイプ"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    BUY_MORE = "BUY_MORE"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    REBALANCE = "REBALANCE"
    DIVERSIFY = "DIVERSIFY"

class PriorityLevel(Enum):
    """優先度レベル"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskLevel(Enum):
    """リスクレベル"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

@dataclass
class Recommendation:
    """推奨事項"""
    symbol: str
    recommendation_type: RecommendationType
    priority: PriorityLevel
    confidence: float
    expected_return: float
    risk_level: RiskLevel
    quantity: int
    price: float
    value: float
    reasoning: List[str]
    conditions: List[str]
    timeframe: str
    risk_amount: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    timestamp: str

@dataclass
class PortfolioRecommendation:
    """ポートフォリオ推奨事項"""
    overall_assessment: Dict[str, Any]
    individual_recommendations: List[Recommendation]
    portfolio_actions: List[Dict[str, Any]]
    risk_warnings: List[Dict[str, Any]]
    optimization_suggestions: List[Dict[str, Any]]
    rebalancing_plan: Dict[str, Any]
    diversification_advice: List[Dict[str, Any]]
    timestamp: str

class EnhancedRecommendationSystem:
    """強化された推奨事項生成システム"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # 推奨パラメータ
        self.min_confidence = self.config.get('min_confidence', 0.7)
        self.max_risk_per_trade = self.config.get('max_risk_per_trade', 0.02)
        self.target_sharpe_ratio = self.config.get('target_sharpe_ratio', 1.5)
        self.rebalancing_threshold = self.config.get('rebalancing_threshold', 0.05)
        # テストで参照される追加しきい値をインスタンス属性として保持
        self.diversification_threshold = self.config.get('diversification_threshold', 0.6)
        self.correlation_threshold = self.config.get('correlation_threshold', 0.7)
        self.volatility_threshold = self.config.get('volatility_threshold', 0.3)
        self.liquidity_threshold = self.config.get('liquidity_threshold', 1000000)
        self.max_position_weight = self.config.get('max_position_weight', 0.2)
        self.min_position_weight = self.config.get('min_position_weight', 0.01)
        # テストが要求するしきい値類（インスタンス属性として保持）
        self.diversification_threshold = self.config.get('diversification_threshold', 0.6)
        self.correlation_threshold = self.config.get('correlation_threshold', 0.7)
        self.volatility_threshold = self.config.get('volatility_threshold', 0.3)
        self.liquidity_threshold = self.config.get('liquidity_threshold', 1000000)
        self.max_position_weight = self.config.get('max_position_weight', 0.2)
        self.min_position_weight = self.config.get('min_position_weight', 0.01)
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定取得"""
        return {
            'min_confidence': 0.7,
            'max_risk_per_trade': 0.02,
            'target_sharpe_ratio': 1.5,
            'rebalancing_threshold': 0.05,
            'diversification_threshold': 0.6,
            'correlation_threshold': 0.7,
            'volatility_threshold': 0.3,
            'liquidity_threshold': 1000000,
            'max_position_weight': 0.2,
            'min_position_weight': 0.01,
            'rebalancing_frequency': 'monthly',
            'risk_tolerance_levels': {
                'LOW': {'max_volatility': 0.15, 'max_drawdown': 0.05},
                'MEDIUM': {'max_volatility': 0.25, 'max_drawdown': 0.10},
                'HIGH': {'max_volatility': 0.35, 'max_drawdown': 0.15},
                'VERY_HIGH': {'max_volatility': 0.50, 'max_drawdown': 0.25}
            }
        }
    
    def generate_portfolio_recommendations(
        self,
        portfolio_data: Dict[str, Any],
        market_conditions: Dict[str, Any],
        optimization_results: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        diversification_metrics: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> PortfolioRecommendation:
        """
        ポートフォリオ推奨事項生成
        
        Args:
            portfolio_data: ポートフォリオデータ
            market_conditions: 市場条件
            optimization_results: 最適化結果
            risk_metrics: リスクメトリクス
            diversification_metrics: 分散投資メトリクス
            user_preferences: ユーザー設定
            
        Returns:
            PortfolioRecommendation: ポートフォリオ推奨事項
        """
        try:
            # 全体評価
            overall_assessment = self._assess_portfolio_overall(
                portfolio_data, market_conditions, optimization_results, risk_metrics, diversification_metrics
            )
            
            # 個別推奨事項生成
            individual_recommendations = self._generate_individual_recommendations(
                portfolio_data, market_conditions, optimization_results, risk_metrics
            )
            
            # ポートフォリオアクション生成
            portfolio_actions = self._generate_portfolio_actions(
                portfolio_data, optimization_results, risk_metrics, diversification_metrics
            )
            
            # リスク警告生成
            risk_warnings = self._generate_risk_warnings(
                portfolio_data, risk_metrics, market_conditions
            )
            
            # 最適化提案生成
            optimization_suggestions = self._generate_optimization_suggestions(
                optimization_results, risk_metrics, diversification_metrics
            )
            
            # リバランス計画生成
            rebalancing_plan = self._generate_rebalancing_plan(
                portfolio_data, optimization_results, user_preferences
            )
            
            # 分散投資アドバイス生成
            diversification_advice = self._generate_diversification_advice(
                diversification_metrics, portfolio_data
            )
            
            return PortfolioRecommendation(
                overall_assessment=overall_assessment,
                individual_recommendations=individual_recommendations,
                portfolio_actions=portfolio_actions,
                risk_warnings=risk_warnings,
                optimization_suggestions=optimization_suggestions,
                rebalancing_plan=rebalancing_plan,
                diversification_advice=diversification_advice,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ推奨事項生成エラー: {e}")
            raise
    
    def _assess_portfolio_overall(
        self,
        portfolio_data: Dict[str, Any],
        market_conditions: Dict[str, Any],
        optimization_results: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        diversification_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ポートフォリオ全体評価"""
        try:
            # 基本統計
            total_value = portfolio_data.get('total_value', 0)
            num_positions = len(portfolio_data.get('positions', {}))
            
            # パフォーマンス評価
            current_sharpe = risk_metrics.get('sharpe_ratio', 0)
            target_sharpe = self.target_sharpe_ratio
            sharpe_performance = current_sharpe / target_sharpe if target_sharpe > 0 else 0
            
            # リスク評価
            volatility = risk_metrics.get('volatility', 0)
            max_drawdown = risk_metrics.get('max_drawdown', 0)
            var_95 = risk_metrics.get('var_95', 0)
            
            # 分散投資評価
            diversification_score = diversification_metrics.get('overall_score', 0)
            effective_stocks = diversification_metrics.get('effective_number_of_stocks', 0)
            
            # 市場条件評価
            market_stress = market_conditions.get('market_stress', 0)
            volatility_regime = market_conditions.get('volatility_regime', 'NORMAL')
            
            # 総合スコア計算
            performance_score = min(1.0, sharpe_performance)
            risk_score = max(0.0, 1.0 - (volatility / 0.5 + max_drawdown / 0.2) / 2)
            diversification_score_normalized = diversification_score
            market_score = max(0.0, 1.0 - market_stress)
            
            overall_score = (
                performance_score * 0.4 +
                risk_score * 0.3 +
                diversification_score_normalized * 0.2 +
                market_score * 0.1
            )
            
            # グレード判定
            if overall_score >= 0.9:
                grade = 'A+'
                status = 'EXCELLENT'
            elif overall_score >= 0.8:
                grade = 'A'
                status = 'VERY_GOOD'
            elif overall_score >= 0.7:
                grade = 'B+'
                status = 'GOOD'
            elif overall_score >= 0.6:
                grade = 'B'
                status = 'FAIR'
            elif overall_score >= 0.5:
                grade = 'C'
                status = 'NEEDS_IMPROVEMENT'
            else:
                grade = 'D'
                status = 'POOR'
            
            return {
                'overall_score': overall_score,
                'grade': grade,
                'status': status,
                'performance_metrics': {
                    'current_sharpe_ratio': current_sharpe,
                    'target_sharpe_ratio': target_sharpe,
                    'sharpe_performance': sharpe_performance,
                    'volatility': volatility,
                    'max_drawdown': max_drawdown,
                    'var_95': var_95
                },
                'diversification_metrics': {
                    'diversification_score': diversification_score,
                    'effective_stocks': effective_stocks,
                    'sector_diversification': diversification_metrics.get('sector_diversification', 0),
                    'correlation_diversification': diversification_metrics.get('correlation_diversification', 0)
                },
                'market_conditions': {
                    'market_stress': market_stress,
                    'volatility_regime': volatility_regime,
                    'trend_direction': market_conditions.get('trend_direction', 'SIDEWAYS'),
                    'liquidity_level': market_conditions.get('liquidity_level', 'MEDIUM')
                },
                'portfolio_summary': {
                    'total_value': total_value,
                    'num_positions': num_positions,
                    'avg_position_size': total_value / num_positions if num_positions > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ全体評価エラー: {e}")
            return {
                'overall_score': 0.5,
                'grade': 'C',
                'status': 'NEEDS_IMPROVEMENT',
                'performance_metrics': {},
                'diversification_metrics': {},
                'market_conditions': {},
                'portfolio_summary': {}
            }
    
    def _generate_individual_recommendations(
        self,
        portfolio_data: Dict[str, Any],
        market_conditions: Dict[str, Any],
        optimization_results: Dict[str, Any],
        risk_metrics: Dict[str, Any]
    ) -> List[Recommendation]:
        """個別推奨事項生成"""
        try:
            recommendations = []
            positions = portfolio_data.get('positions', {})
            optimized_weights = optimization_results.get('weights', {})
            
            for symbol, position_data in positions.items():
                current_weight = position_data.get('weight', 0)
                target_weight = optimized_weights.get(symbol, 0)
                current_price = position_data.get('current_price', 0)
                quantity = position_data.get('quantity', 0)
                
                # 推奨タイプ決定
                weight_diff = target_weight - current_weight
                recommendation_type = self._determine_recommendation_type(weight_diff, position_data)
                
                # 信頼度計算
                confidence = self._calculate_recommendation_confidence(
                    position_data, market_conditions, risk_metrics
                )
                
                # 優先度決定
                priority = self._determine_priority(weight_diff, confidence, position_data)
                
                # 期待リターン計算
                expected_return = self._calculate_expected_return(position_data, market_conditions)
                
                # リスクレベル判定
                risk_level = self._determine_risk_level(position_data, risk_metrics)
                
                # 推奨数量計算
                recommended_quantity = self._calculate_recommended_quantity(
                    symbol, current_price, target_weight, portfolio_data.get('total_value', 0)
                )
                
                # 推奨価値計算
                recommended_value = recommended_quantity * current_price
                
                # 推奨理由生成
                reasoning = self._generate_reasoning(
                    recommendation_type, weight_diff, position_data, market_conditions
                )
                
                # 条件生成
                conditions = self._generate_conditions(
                    recommendation_type, market_conditions, position_data
                )
                
                # タイムフレーム決定
                timeframe = self._determine_timeframe(recommendation_type, priority)
                
                # リスク金額計算
                risk_amount = recommended_value * position_data.get('volatility', 0.2)
                
                # 損切り・利確価格計算
                stop_loss, take_profit = self._calculate_stop_take_prices(
                    current_price, recommendation_type, position_data
                )
                
                recommendation = Recommendation(
                    symbol=symbol,
                    recommendation_type=recommendation_type,
                    priority=priority,
                    confidence=confidence,
                    expected_return=expected_return,
                    risk_level=risk_level,
                    quantity=recommended_quantity,
                    price=current_price,
                    value=recommended_value,
                    reasoning=reasoning,
                    conditions=conditions,
                    timeframe=timeframe,
                    risk_amount=risk_amount,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    timestamp=datetime.now().isoformat()
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"個別推奨事項生成エラー: {e}")
            return []
    
    def _determine_recommendation_type(self, weight_diff: float, position_data: Dict[str, Any]) -> RecommendationType:
        """推奨タイプ決定"""
        try:
            if weight_diff > self.rebalancing_threshold:
                return RecommendationType.BUY_MORE
            elif weight_diff < -self.rebalancing_threshold:
                return RecommendationType.SELL
            elif position_data.get('unrealized_pnl', 0) > position_data.get('cost_basis', 0) * 0.1:
                return RecommendationType.TAKE_PROFIT
            elif position_data.get('unrealized_pnl', 0) < -position_data.get('cost_basis', 0) * 0.05:
                return RecommendationType.STOP_LOSS
            else:
                return RecommendationType.HOLD
                
        except Exception as e:
            self.logger.error(f"推奨タイプ決定エラー: {e}")
            return RecommendationType.HOLD
    
    def _calculate_recommendation_confidence(
        self,
        position_data: Dict[str, Any],
        market_conditions: Dict[str, Any],
        risk_metrics: Dict[str, Any]
    ) -> float:
        """推奨信頼度計算"""
        try:
            # 基本信頼度
            base_confidence = position_data.get('confidence', 0.7)
            
            # 市場条件調整
            market_stress = market_conditions.get('market_stress', 0)
            market_adjustment = 1.0 - market_stress * 0.3
            
            # リスク調整
            volatility = position_data.get('volatility', 0.2)
            risk_adjustment = max(0.5, 1.0 - volatility * 2)
            
            # 総合信頼度
            confidence = base_confidence * market_adjustment * risk_adjustment
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            self.logger.error(f"推奨信頼度計算エラー: {e}")
            return 0.5
    
    def _determine_priority(
        self,
        weight_diff: float,
        confidence: float,
        position_data: Dict[str, Any]
    ) -> PriorityLevel:
        """優先度決定"""
        try:
            # 重み差分による優先度
            if abs(weight_diff) > 0.1:
                weight_priority = PriorityLevel.HIGH
            elif abs(weight_diff) > 0.05:
                weight_priority = PriorityLevel.MEDIUM
            else:
                weight_priority = PriorityLevel.LOW
            
            # 信頼度による調整
            if confidence < 0.6:
                return PriorityLevel.LOW
            elif confidence >= 0.8:
                return weight_priority
            else:
                return PriorityLevel.MEDIUM
                
        except Exception as e:
            self.logger.error(f"優先度決定エラー: {e}")
            return PriorityLevel.MEDIUM
    
    def _calculate_expected_return(
        self,
        position_data: Dict[str, Any],
        market_conditions: Dict[str, Any]
    ) -> float:
        """期待リターン計算"""
        try:
            base_return = position_data.get('expected_return', 0.05)
            trend = market_conditions.get('trend_direction', 'SIDEWAYS')
            regime = market_conditions.get('volatility_regime', 'NORMAL')
            market_adjustment = 1.0 + (0.1 if trend == 'BULL' else ( -0.1 if trend == 'BEAR' else 0.0))
            volatility_adjustment = 1.0 + ( -0.1 if regime == 'HIGH' else ( -0.2 if regime == 'EXTREME' else 0.0))
            
            expected_return = base_return * market_adjustment * volatility_adjustment
            
            return expected_return
            
        except Exception as e:
            self.logger.error(f"期待リターン計算エラー: {e}")
            return 0.05
    
    def _determine_risk_level(
        self,
        position_data: Dict[str, Any],
        risk_metrics: Dict[str, Any]
    ) -> RiskLevel:
        """リスクレベル判定"""
        try:
            volatility = position_data.get('volatility', 0.2)
            
            if volatility < 0.15:
                return RiskLevel.LOW
            elif volatility < 0.25:
                return RiskLevel.MEDIUM
            elif volatility < 0.35:
                return RiskLevel.HIGH
            else:
                return RiskLevel.VERY_HIGH
                
        except Exception as e:
            self.logger.error(f"リスクレベル判定エラー: {e}")
            return RiskLevel.MEDIUM
    
    def _calculate_recommended_quantity(
        self,
        symbol: str,
        current_price: float,
        target_weight: float,
        total_value: float
    ) -> int:
        """推奨数量計算"""
        try:
            target_value = total_value * target_weight
            recommended_quantity = int(target_value / current_price)
            
            return max(0, recommended_quantity)
            
        except Exception as e:
            self.logger.error(f"推奨数量計算エラー: {e}")
            return 0
    
    def _generate_reasoning(
        self,
        recommendation_type: RecommendationType,
        weight_diff: float,
        position_data: Dict[str, Any],
        market_conditions: Dict[str, Any]
    ) -> List[str]:
        """推奨理由生成"""
        try:
            reasoning = []
            
            if recommendation_type == RecommendationType.BUY_MORE:
                reasoning.append(f"ポートフォリオ最適化により、{abs(weight_diff):.1%}の増量が推奨されています")
                reasoning.append("期待リターンがリスクを上回る状況です")
            elif recommendation_type == RecommendationType.SELL:
                reasoning.append(f"ポートフォリオ最適化により、{abs(weight_diff):.1%}の減量が推奨されています")
                reasoning.append("リスク調整後のリターンが低下しています")
            elif recommendation_type == RecommendationType.TAKE_PROFIT:
                reasoning.append("利益確定のタイミングです")
                reasoning.append("目標リターンを達成しています")
            elif recommendation_type == RecommendationType.STOP_LOSS:
                reasoning.append("損失限定のため売却を推奨します")
                reasoning.append("リスク管理の観点から必要です")
            else:
                # HOLD 等でも最低1件は理由を提示
                reasoning.append("現状維持が適切と判断されます（過度な乖離なし）")
            
            # 市場条件による追加理由
            if market_conditions.get('volatility_regime') == 'HIGH':
                reasoning.append("高ボラティリティ環境のため注意が必要です")
            
            if market_conditions.get('trend_direction') == 'BEAR':
                reasoning.append("弱気市場のため慎重な判断が必要です")
            # フォールバック（空配列回避）
            if not reasoning:
                reasoning.append("分析結果に基づく推奨です")

            return reasoning
            
        except Exception as e:
            self.logger.error(f"推奨理由生成エラー: {e}")
            return ["分析結果に基づく推奨です"]
    
    def _generate_conditions(
        self,
        recommendation_type: RecommendationType,
        market_conditions: Dict[str, Any],
        position_data: Dict[str, Any]
    ) -> List[str]:
        """条件生成"""
        try:
            conditions = []
            
            if recommendation_type in [RecommendationType.BUY, RecommendationType.BUY_MORE]:
                conditions.append("市場の流動性が十分であること")
                conditions.append("価格の急激な変動がないこと")
            elif recommendation_type in [RecommendationType.SELL, RecommendationType.STOP_LOSS]:
                conditions.append("損失を最小限に抑えること")
                conditions.append("市場の流動性を確認すること")
            else:
                # HOLD などでも最低限の条件を提示
                conditions.append("重要なニュースやイベントがないこと")
                conditions.append("過度なボラティリティ上昇がないこと")
            
            # 市場条件による条件
            if market_conditions.get('volatility_regime') == 'HIGH':
                conditions.append("高ボラティリティ環境での取引に注意")
            
            if market_conditions.get('liquidity_level') == 'LOW':
                conditions.append("流動性の低い環境での取引に注意")
            
            return conditions
            
        except Exception as e:
            self.logger.error(f"条件生成エラー: {e}")
            return ["一般的な取引条件を満たすこと"]
    
    def _determine_timeframe(
        self,
        recommendation_type: RecommendationType,
        priority: PriorityLevel
    ) -> str:
        """タイムフレーム決定"""
        try:
            if recommendation_type in [RecommendationType.STOP_LOSS, RecommendationType.TAKE_PROFIT]:
                return "即座実行"
            elif priority == PriorityLevel.HIGH:
                return "今週中"
            elif priority == PriorityLevel.MEDIUM:
                return "今月中"
            else:
                return "来四半期"
                
        except Exception as e:
            self.logger.error(f"タイムフレーム決定エラー: {e}")
            return "今月中"
    
    def _calculate_stop_take_prices(
        self,
        current_price: float,
        recommendation_type: RecommendationType,
        position_data: Dict[str, Any]
    ) -> Tuple[Optional[float], Optional[float]]:
        """損切り・利確価格計算"""
        try:
            volatility = position_data.get('volatility', 0.2)
            
            if recommendation_type in [RecommendationType.BUY, RecommendationType.BUY_MORE]:
                # 新規・追加購入の場合
                stop_loss = current_price * (1 - volatility * 2)
                take_profit = current_price * (1 + volatility * 3)
            elif recommendation_type in [RecommendationType.SELL, RecommendationType.STOP_LOSS]:
                # 売却の場合
                stop_loss = None
                take_profit = None
            else:
                # ホールドの場合
                stop_loss = current_price * (1 - volatility * 1.5)
                take_profit = current_price * (1 + volatility * 2)
            
            return stop_loss, take_profit
            
        except Exception as e:
            self.logger.error(f"損切り・利確価格計算エラー: {e}")
            return None, None
    
    def _generate_portfolio_actions(
        self,
        portfolio_data: Dict[str, Any],
        optimization_results: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        diversification_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """ポートフォリオアクション生成"""
        try:
            actions = []
            
            # リバランスアクション
            if optimization_results.get('rebalancing_needed', False):
                actions.append({
                    'type': 'REBALANCE',
                    'description': 'ポートフォリオのリバランスが必要です',
                    'priority': 'HIGH',
                    'expected_impact': 'リスク・リターンの最適化'
                })
            
            # 分散投資アクション
            if diversification_metrics.get('overall_score', 0) < 0.6:
                actions.append({
                    'type': 'DIVERSIFY',
                    'description': '分散投資を強化してください',
                    'priority': 'MEDIUM',
                    'expected_impact': 'リスク分散の向上'
                })
            
            # リスク管理アクション
            if risk_metrics.get('volatility', 0) > 0.3:
                actions.append({
                    'type': 'RISK_REDUCTION',
                    'description': 'リスクを削減してください',
                    'priority': 'HIGH',
                    'expected_impact': 'リスク管理の強化'
                })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"ポートフォリオアクション生成エラー: {e}")
            return []
    
    def _generate_risk_warnings(
        self,
        portfolio_data: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        market_conditions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """リスク警告生成"""
        try:
            warnings = []
            
            # ボラティリティ警告
            if risk_metrics.get('volatility', 0) > 0.4:
                warnings.append({
                    'type': 'HIGH_VOLATILITY',
                    'message': 'ポートフォリオのボラティリティが高すぎます',
                    'severity': 'HIGH',
                    'recommendation': 'リスクを削減することを検討してください'
                })
            
            # 最大ドローダウン警告
            if risk_metrics.get('max_drawdown', 0) > 0.2:
                warnings.append({
                    'type': 'HIGH_DRAWDOWN',
                    'message': '最大ドローダウンが大きすぎます',
                    'severity': 'CRITICAL',
                    'recommendation': '損失限定のための対策を講じてください'
                })
            
            # 市場ストレス警告
            if market_conditions.get('market_stress', 0) > 0.7:
                warnings.append({
                    'type': 'MARKET_STRESS',
                    'message': '市場ストレスが高まっています',
                    'severity': 'HIGH',
                    'recommendation': '慎重な取引判断が必要です'
                })
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"リスク警告生成エラー: {e}")
            return []
    
    def _generate_optimization_suggestions(
        self,
        optimization_results: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        diversification_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """最適化提案生成"""
        try:
            suggestions = []
            
            # シャープレシオ改善提案
            current_sharpe = risk_metrics.get('sharpe_ratio', 0)
            if current_sharpe < self.target_sharpe_ratio:
                suggestions.append({
                    'type': 'SHARPE_IMPROVEMENT',
                    'description': 'シャープレシオの改善が必要です',
                    'current_value': current_sharpe,
                    'target_value': self.target_sharpe_ratio,
                    'improvement_method': 'リスク調整後のリターン向上'
                })
            
            # 分散投資改善提案
            diversification_score = diversification_metrics.get('overall_score', 0)
            if diversification_score < 0.7:
                suggestions.append({
                    'type': 'DIVERSIFICATION_IMPROVEMENT',
                    'description': '分散投資スコアの改善が必要です',
                    'current_value': diversification_score,
                    'target_value': 0.8,
                    'improvement_method': 'より多くの銘柄・セクターへの分散'
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"最適化提案生成エラー: {e}")
            return []
    
    def _generate_rebalancing_plan(
        self,
        portfolio_data: Dict[str, Any],
        optimization_results: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """リバランス計画生成"""
        try:
            current_weights = portfolio_data.get('weights', {})
            target_weights = optimization_results.get('weights', {})
            
            rebalancing_trades = []
            total_rebalancing_value = 0
            
            for symbol in set(current_weights.keys()) | set(target_weights.keys()):
                current_weight = current_weights.get(symbol, 0)
                target_weight = target_weights.get(symbol, 0)
                weight_diff = target_weight - current_weight
                
                if abs(weight_diff) > self.rebalancing_threshold:
                    trade_value = portfolio_data.get('total_value', 0) * abs(weight_diff)
                    total_rebalancing_value += trade_value
                    
                    rebalancing_trades.append({
                        'symbol': symbol,
                        'current_weight': current_weight,
                        'target_weight': target_weight,
                        'weight_diff': weight_diff,
                        'trade_value': trade_value,
                        'action': 'BUY' if weight_diff > 0 else 'SELL'
                    })
            
            return {
                'rebalancing_needed': len(rebalancing_trades) > 0,
                'total_trades': len(rebalancing_trades),
                'total_value': total_rebalancing_value,
                'trades': rebalancing_trades,
                'frequency': self.config.get('rebalancing_frequency', 'monthly'),
                'threshold': self.rebalancing_threshold
            }
            
        except Exception as e:
            self.logger.error(f"リバランス計画生成エラー: {e}")
            return {'rebalancing_needed': False, 'total_trades': 0, 'total_value': 0, 'trades': []}
    
    def _generate_diversification_advice(
        self,
        diversification_metrics: Dict[str, Any],
        portfolio_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分散投資アドバイス生成"""
        try:
            advice = []
            
            # セクター分散アドバイス
            sector_score = diversification_metrics.get('sector_diversification', 0)
            if sector_score < 0.6:
                advice.append({
                    'type': 'SECTOR_DIVERSIFICATION',
                    'description': 'セクター分散を改善してください',
                    'current_score': sector_score,
                    'target_score': 0.8,
                    'suggestions': [
                        '異なるセクターへの投資を検討',
                        '特定セクターへの過度な集中を避ける',
                        'セクター別のリスク分析を実施'
                    ]
                })
            
            # 相関分散アドバイス
            correlation_score = diversification_metrics.get('correlation_diversification', 0)
            if correlation_score < 0.5:
                advice.append({
                    'type': 'CORRELATION_DIVERSIFICATION',
                    'description': '相関分散を改善してください',
                    'current_score': correlation_score,
                    'target_score': 0.7,
                    'suggestions': [
                        '低相関銘柄への投資を検討',
                        '相関分析を定期的に実施',
                        '市場指数との相関を監視'
                    ]
                })
            
            return advice
            
        except Exception as e:
            self.logger.error(f"分散投資アドバイス生成エラー: {e}")
            return []
