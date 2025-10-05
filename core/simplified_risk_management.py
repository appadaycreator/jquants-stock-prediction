#!/usr/bin/env python3
"""
簡素化されたリスク管理システム
個人投資家向けに複雑なリスク指標を3段階（低/中/高）に簡素化
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import json


class SimplifiedRiskLevel(Enum):
    """簡素化されたリスクレベル"""
    LOW = "low"      # 低リスク
    MEDIUM = "medium"  # 中リスク
    HIGH = "high"     # 高リスク


@dataclass
class SimplifiedRiskMetrics:
    """簡素化されたリスクメトリクス"""
    risk_level: SimplifiedRiskLevel
    max_loss_amount: float  # 最大損失予想額
    risk_score: float  # リスクスコア（0-100）
    volatility_level: str  # ボラティリティレベル
    color_code: str  # 色分けコード
    recommendation: str  # 推奨アクション
    confidence: float  # 信頼度


@dataclass
class PortfolioRiskBalance:
    """ポートフォリオリスクバランス"""
    total_risk_score: float
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    risk_distribution: Dict[str, float]  # リスク分布
    color_balance: Dict[str, str]  # 色分けバランス
    overall_recommendation: str


class SimplifiedRiskManager:
    """簡素化されたリスク管理システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.risk_history = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "risk_thresholds": {
                "low_risk_max": 30,      # 低リスク上限スコア
                "medium_risk_max": 70,    # 中リスク上限スコア
                "high_risk_min": 70       # 高リスク下限スコア
            },
            "volatility_thresholds": {
                "low": 0.15,      # 15%以下は低ボラティリティ
                "medium": 0.30,   # 30%以下は中ボラティリティ
                "high": 0.30      # 30%超は高ボラティリティ
            },
            "max_loss_calculation": {
                "var_multiplier": 2.0,    # VaR倍率
                "confidence_level": 0.95,  # 信頼度
                "position_size_factor": 0.1  # ポジションサイズ係数
            },
            "color_codes": {
                "low_risk": "#4CAF50",     # 緑色
                "medium_risk": "#FF9800",  # オレンジ色
                "high_risk": "#F44336"     # 赤色
            },
            "recommendations": {
                "low_risk": "投資推奨",
                "medium_risk": "注意深く投資",
                "high_risk": "投資見送り推奨"
            }
        }
    
    def calculate_simplified_risk_metrics(
        self,
        stock_data: pd.DataFrame,
        current_price: float,
        position_size: float = 0.0,
        account_balance: float = 1000000.0
    ) -> SimplifiedRiskMetrics:
        """簡素化されたリスクメトリクス計算"""
        try:
            if stock_data.empty or current_price <= 0:
                return self._get_default_simplified_metrics()
            
            # 基本リスク指標の計算
            volatility = self._calculate_volatility(stock_data)
            var_95 = self._calculate_var_95(stock_data)
            max_drawdown = self._calculate_max_drawdown(stock_data)
            
            # リスクスコア計算（0-100）
            risk_score = self._calculate_risk_score(volatility, var_95, max_drawdown)
            
            # リスクレベル決定
            risk_level = self._determine_risk_level(risk_score)
            
            # 最大損失予想額計算
            max_loss_amount = self._calculate_max_loss_amount(
                current_price, position_size, var_95, account_balance
            )
            
            # ボラティリティレベル決定
            volatility_level = self._determine_volatility_level(volatility)
            
            # 色分けコード取得
            color_code = self._get_color_code(risk_level)
            
            # 推奨アクション取得
            recommendation = self._get_recommendation(risk_level)
            
            # 信頼度計算
            confidence = self._calculate_confidence(volatility, var_95, max_drawdown)
            
            metrics = SimplifiedRiskMetrics(
                risk_level=risk_level,
                max_loss_amount=max_loss_amount,
                risk_score=risk_score,
                volatility_level=volatility_level,
                color_code=color_code,
                recommendation=recommendation,
                confidence=confidence
            )
            
            # 履歴に追加
            self.risk_history.append(metrics)
            if len(self.risk_history) > 1000:
                self.risk_history.pop(0)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"簡素化リスクメトリクス計算エラー: {e}")
            return self._get_default_simplified_metrics()
    
    def calculate_portfolio_risk_balance(
        self,
        portfolio_data: Dict[str, Dict[str, Any]],
        account_balance: float
    ) -> PortfolioRiskBalance:
        """ポートフォリオリスクバランス計算"""
        try:
            if not portfolio_data:
                return self._get_default_portfolio_balance()
            
            # 各銘柄のリスクレベル集計
            low_risk_count = 0
            medium_risk_count = 0
            high_risk_count = 0
            
            total_risk_score = 0.0
            risk_distribution = {"low": 0.0, "medium": 0.0, "high": 0.0}
            color_balance = {"green": 0, "orange": 0, "red": 0}
            
            for symbol, data in portfolio_data.items():
                if not data or 'stock_data' not in data:
                    continue
                
                stock_data = data['stock_data']
                current_price = data.get('current_price', 0)
                position_size = data.get('position_size', 0)
                
                # リスクメトリクス計算
                risk_metrics = self.calculate_simplified_risk_metrics(
                    stock_data, current_price, position_size, account_balance
                )
                
                # カウント集計
                if risk_metrics.risk_level == SimplifiedRiskLevel.LOW:
                    low_risk_count += 1
                    risk_distribution["low"] += 1
                    color_balance["green"] += 1
                elif risk_metrics.risk_level == SimplifiedRiskLevel.MEDIUM:
                    medium_risk_count += 1
                    risk_distribution["medium"] += 1
                    color_balance["orange"] += 1
                else:  # HIGH
                    high_risk_count += 1
                    risk_distribution["high"] += 1
                    color_balance["red"] += 1
                
                total_risk_score += risk_metrics.risk_score
            
            # 平均リスクスコア計算
            total_positions = len(portfolio_data)
            if total_positions > 0:
                avg_risk_score = total_risk_score / total_positions
                # 分布を正規化
                for key in risk_distribution:
                    risk_distribution[key] = risk_distribution[key] / total_positions
            else:
                avg_risk_score = 0.0
            
            # 全体推奨事項決定
            overall_recommendation = self._get_overall_recommendation(
                avg_risk_score, low_risk_count, medium_risk_count, high_risk_count
            )
            
            return PortfolioRiskBalance(
                total_risk_score=avg_risk_score,
                low_risk_count=low_risk_count,
                medium_risk_count=medium_risk_count,
                high_risk_count=high_risk_count,
                risk_distribution=risk_distribution,
                color_balance=color_balance,
                overall_recommendation=overall_recommendation
            )
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスクバランス計算エラー: {e}")
            return self._get_default_portfolio_balance()
    
    def get_risk_alerts(self, portfolio_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """リスクアラート取得"""
        try:
            alerts = []
            
            for symbol, data in portfolio_data.items():
                if not data or 'stock_data' not in data:
                    continue
                
                stock_data = data['stock_data']
                current_price = data.get('current_price', 0)
                position_size = data.get('position_size', 0)
                account_balance = data.get('account_balance', 1000000.0)
                
                # リスクメトリクス計算
                risk_metrics = self.calculate_simplified_risk_metrics(
                    stock_data, current_price, position_size, account_balance
                )
                
                # 高リスクアラート
                if risk_metrics.risk_level == SimplifiedRiskLevel.HIGH:
                    alerts.append({
                        'type': 'HIGH_RISK',
                        'symbol': symbol,
                        'message': f'{symbol}: 高リスク銘柄です。投資を見送ることを推奨します。',
                        'severity': 'HIGH',
                        'risk_score': risk_metrics.risk_score,
                        'max_loss_amount': risk_metrics.max_loss_amount,
                        'color_code': risk_metrics.color_code
                    })
                
                # 高ボラティリティアラート
                if risk_metrics.volatility_level == 'high':
                    alerts.append({
                        'type': 'HIGH_VOLATILITY',
                        'symbol': symbol,
                        'message': f'{symbol}: ボラティリティが高いです。注意深く投資してください。',
                        'severity': 'MEDIUM',
                        'volatility_level': risk_metrics.volatility_level,
                        'color_code': risk_metrics.color_code
                    })
                
                # 最大損失額アラート
                if risk_metrics.max_loss_amount > account_balance * 0.1:  # 口座残高の10%以上
                    alerts.append({
                        'type': 'HIGH_LOSS_POTENTIAL',
                        'symbol': symbol,
                        'message': f'{symbol}: 最大損失予想額が高いです（{risk_metrics.max_loss_amount:,.0f}円）',
                        'severity': 'HIGH',
                        'max_loss_amount': risk_metrics.max_loss_amount,
                        'loss_ratio': risk_metrics.max_loss_amount / account_balance,
                        'color_code': risk_metrics.color_code
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"リスクアラート取得エラー: {e}")
            return []
    
    def get_visual_risk_display_data(self, portfolio_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """視覚的リスク表示データ取得"""
        try:
            # ポートフォリオリスクバランス計算
            portfolio_balance = self.calculate_portfolio_risk_balance(portfolio_data, 1000000.0)
            
            # 各銘柄のリスクデータ
            stock_risk_data = []
            for symbol, data in portfolio_data.items():
                if not data or 'stock_data' not in data:
                    continue
                
                stock_data = data['stock_data']
                current_price = data.get('current_price', 0)
                position_size = data.get('position_size', 0)
                account_balance = data.get('account_balance', 1000000.0)
                
                risk_metrics = self.calculate_simplified_risk_metrics(
                    stock_data, current_price, position_size, account_balance
                )
                
                stock_risk_data.append({
                    'symbol': symbol,
                    'risk_level': risk_metrics.risk_level.value,
                    'risk_score': risk_metrics.risk_score,
                    'max_loss_amount': risk_metrics.max_loss_amount,
                    'volatility_level': risk_metrics.volatility_level,
                    'color_code': risk_metrics.color_code,
                    'recommendation': risk_metrics.recommendation,
                    'confidence': risk_metrics.confidence
                })
            
            return {
                'portfolio_balance': {
                    'total_risk_score': portfolio_balance.total_risk_score,
                    'risk_distribution': portfolio_balance.risk_distribution,
                    'color_balance': portfolio_balance.color_balance,
                    'overall_recommendation': portfolio_balance.overall_recommendation
                },
                'stock_risk_data': stock_risk_data,
                'risk_alerts': self.get_risk_alerts(portfolio_data),
                'display_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"視覚的リスク表示データ取得エラー: {e}")
            return {}
    
    # ヘルパーメソッド群
    def _calculate_volatility(self, stock_data: pd.DataFrame) -> float:
        """ボラティリティ計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.2
        
        returns = stock_data['Close'].pct_change().dropna()
        if len(returns) < 2:
            return 0.2
        
        return returns.std() * np.sqrt(252)
    
    def _calculate_var_95(self, stock_data: pd.DataFrame) -> float:
        """95% VaR計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.05
        
        returns = stock_data['Close'].pct_change().dropna()
        if len(returns) < 10:
            return 0.05
        
        var_95 = np.percentile(returns, 5)
        return abs(var_95)
    
    def _calculate_max_drawdown(self, stock_data: pd.DataFrame) -> float:
        """最大ドローダウン計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.0
        
        prices = stock_data['Close']
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        
        return abs(drawdown.min())
    
    def _calculate_risk_score(self, volatility: float, var_95: float, max_drawdown: float) -> float:
        """リスクスコア計算（0-100）"""
        # 各指標の重み付きスコア
        volatility_score = min(volatility * 200, 40)  # ボラティリティ20% = 40点
        var_score = min(var_95 * 1000, 30)  # VaR 3% = 30点
        drawdown_score = min(max_drawdown * 200, 30)  # ドローダウン15% = 30点
        
        total_score = volatility_score + var_score + drawdown_score
        
        return min(100, max(0, total_score))
    
    def _determine_risk_level(self, risk_score: float) -> SimplifiedRiskLevel:
        """リスクレベル決定"""
        thresholds = self.config["risk_thresholds"]
        
        if risk_score <= thresholds["low_risk_max"]:
            return SimplifiedRiskLevel.LOW
        elif risk_score <= thresholds["medium_risk_max"]:
            return SimplifiedRiskLevel.MEDIUM
        else:
            return SimplifiedRiskLevel.HIGH
    
    def _calculate_max_loss_amount(
        self, current_price: float, position_size: float, var_95: float, account_balance: float
    ) -> float:
        """最大損失予想額計算"""
        if position_size <= 0 or current_price <= 0:
            return 0.0
        
        # ポジション価値
        position_value = current_price * position_size
        
        # VaRに基づく最大損失額
        max_loss_ratio = var_95 * self.config["max_loss_calculation"]["var_multiplier"]
        max_loss_amount = position_value * max_loss_ratio
        
        # 口座残高に対する制限
        max_loss_limit = account_balance * self.config["max_loss_calculation"]["position_size_factor"]
        
        return min(max_loss_amount, max_loss_limit)
    
    def _determine_volatility_level(self, volatility: float) -> str:
        """ボラティリティレベル決定"""
        thresholds = self.config["volatility_thresholds"]
        
        if volatility <= thresholds["low"]:
            return "low"
        elif volatility <= thresholds["medium"]:
            return "medium"
        else:
            return "high"
    
    def _get_color_code(self, risk_level: SimplifiedRiskLevel) -> str:
        """色分けコード取得"""
        color_codes = self.config["color_codes"]
        
        if risk_level == SimplifiedRiskLevel.LOW:
            return color_codes["low_risk"]
        elif risk_level == SimplifiedRiskLevel.MEDIUM:
            return color_codes["medium_risk"]
        else:
            return color_codes["high_risk"]
    
    def _get_recommendation(self, risk_level: SimplifiedRiskLevel) -> str:
        """推奨アクション取得"""
        recommendations = self.config["recommendations"]
        
        if risk_level == SimplifiedRiskLevel.LOW:
            return recommendations["low_risk"]
        elif risk_level == SimplifiedRiskLevel.MEDIUM:
            return recommendations["medium_risk"]
        else:
            return recommendations["high_risk"]
    
    def _calculate_confidence(self, volatility: float, var_95: float, max_drawdown: float) -> float:
        """信頼度計算"""
        # リスク指標が低いほど信頼度が高い
        volatility_confidence = max(0, 1 - volatility * 2)
        var_confidence = max(0, 1 - var_95 * 10)
        drawdown_confidence = max(0, 1 - max_drawdown * 2)
        
        # 平均信頼度
        confidence = (volatility_confidence + var_confidence + drawdown_confidence) / 3
        
        return min(1.0, max(0.0, confidence))
    
    def _get_overall_recommendation(
        self, avg_risk_score: float, low_count: int, medium_count: int, high_count: int
    ) -> str:
        """全体推奨事項決定"""
        total_count = low_count + medium_count + high_count
        
        if total_count == 0:
            return "ポートフォリオが空です"
        
        high_risk_ratio = high_count / total_count
        
        if high_risk_ratio > 0.5:
            return "高リスク銘柄が多いため、リスク分散を推奨します"
        elif avg_risk_score > 60:
            return "ポートフォリオ全体のリスクが高いため、注意が必要です"
        elif low_count > medium_count + high_count:
            return "低リスク銘柄が多く、安定したポートフォリオです"
        else:
            return "バランスの取れたポートフォリオです"
    
    def _get_default_simplified_metrics(self) -> SimplifiedRiskMetrics:
        """デフォルト簡素化メトリクス"""
        return SimplifiedRiskMetrics(
            risk_level=SimplifiedRiskLevel.MEDIUM,
            max_loss_amount=0.0,
            risk_score=50.0,
            volatility_level="medium",
            color_code="#FF9800",
            recommendation="注意深く投資",
            confidence=0.5
        )
    
    def _get_default_portfolio_balance(self) -> PortfolioRiskBalance:
        """デフォルトポートフォリオバランス"""
        return PortfolioRiskBalance(
            total_risk_score=0.0,
            low_risk_count=0,
            medium_risk_count=0,
            high_risk_count=0,
            risk_distribution={"low": 0.0, "medium": 0.0, "high": 0.0},
            color_balance={"green": 0, "orange": 0, "red": 0},
            overall_recommendation="ポートフォリオが空です"
        )
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """リスク統計情報取得"""
        if not self.risk_history:
            return {}
        
        risk_scores = [m.risk_score for m in self.risk_history]
        risk_levels = [m.risk_level.value for m in self.risk_history]
        
        return {
            "total_samples": len(self.risk_history),
            "avg_risk_score": np.mean(risk_scores),
            "max_risk_score": np.max(risk_scores),
            "min_risk_score": np.min(risk_scores),
            "risk_level_distribution": {
                level: risk_levels.count(level)
                for level in ["low", "medium", "high"]
            }
        }
