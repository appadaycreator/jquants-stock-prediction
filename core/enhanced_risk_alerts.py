#!/usr/bin/env python3
"""
改善されたリスクアラート機能
個人投資家向けの直感的で分かりやすいアラートシステム
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np


class AlertSeverity(Enum):
    """アラート重要度"""
    INFO = "info"          # 情報
    WARNING = "warning"    # 警告
    CRITICAL = "critical"  # 重要
    EMERGENCY = "emergency"  # 緊急


class AlertType(Enum):
    """アラート種別"""
    HIGH_RISK = "high_risk"                    # 高リスク
    HIGH_VOLATILITY = "high_volatility"        # 高ボラティリティ
    HIGH_LOSS_POTENTIAL = "high_loss_potential"  # 高損失可能性
    PORTFOLIO_IMBALANCE = "portfolio_imbalance"  # ポートフォリオ不均衡
    MARKET_STRESS = "market_stress"            # 市場ストレス
    POSITION_SIZE_WARNING = "position_size_warning"  # ポジションサイズ警告
    STOP_LOSS_TRIGGER = "stop_loss_trigger"    # 損切りトリガー
    TAKE_PROFIT_TRIGGER = "take_profit_trigger"  # 利確トリガー
    LIQUIDITY_WARNING = "liquidity_warning"    # 流動性警告
    CORRELATION_WARNING = "correlation_warning"  # 相関警告


@dataclass
class RiskAlert:
    """リスクアラート"""
    id: str
    type: AlertType
    severity: AlertSeverity
    symbol: str
    title: str
    message: str
    recommendation: str
    action_required: bool
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    color_code: str
    icon: str


@dataclass
class AlertSummary:
    """アラートサマリー"""
    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    info_alerts: int
    emergency_alerts: int
    alerts_by_type: Dict[str, int]
    alerts_by_symbol: Dict[str, int]
    recent_alerts: List[RiskAlert]
    top_risks: List[Dict[str, Any]]


class EnhancedRiskAlerts:
    """改善されたリスクアラートシステム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.alert_history = []
        self.alert_settings = self.config.get("alert_settings", {})
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "alert_settings": {
                "high_risk_threshold": 70,      # 高リスク閾値
                "high_volatility_threshold": 0.3,  # 高ボラティリティ閾値
                "max_loss_ratio_threshold": 0.1,   # 最大損失比率閾値
                "portfolio_imbalance_threshold": 0.5,  # ポートフォリオ不均衡閾値
                "position_size_threshold": 0.2,    # ポジションサイズ閾値
                "correlation_threshold": 0.8,       # 相関閾値
                "liquidity_threshold": 100000,     # 流動性閾値
                "alert_retention_days": 30         # アラート保持日数
            },
            "notification_settings": {
                "email_enabled": True,
                "push_enabled": True,
                "sms_enabled": False,
                "webhook_enabled": False
            },
            "severity_colors": {
                "info": "#2196F3",        # 青色
                "warning": "#FF9800",     # オレンジ色
                "critical": "#F44336",    # 赤色
                "emergency": "#9C27B0"    # 紫色
            },
            "severity_icons": {
                "info": "info",
                "warning": "warning",
                "critical": "error",
                "emergency": "emergency"
            }
        }
    
    def generate_comprehensive_alerts(
        self,
        portfolio_data: Dict[str, Dict[str, Any]],
        market_data: Optional[Dict[str, Any]] = None
    ) -> List[RiskAlert]:
        """包括的アラート生成"""
        try:
            alerts = []
            
            # 各銘柄のアラート生成
            for symbol, data in portfolio_data.items():
                if not data or 'stock_data' not in data:
                    continue
                
                stock_alerts = self._generate_stock_alerts(symbol, data)
                alerts.extend(stock_alerts)
            
            # ポートフォリオ全体のアラート生成
            portfolio_alerts = self._generate_portfolio_alerts(portfolio_data, market_data)
            alerts.extend(portfolio_alerts)
            
            # 市場状況アラート生成
            if market_data:
                market_alerts = self._generate_market_alerts(market_data)
                alerts.extend(market_alerts)
            
            # アラートの重複除去と優先度調整
            alerts = self._deduplicate_and_prioritize_alerts(alerts)
            
            # アラート履歴に追加
            for alert in alerts:
                self.alert_history.append(alert)
            
            # 古いアラートの削除
            self._cleanup_old_alerts()
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"包括的アラート生成エラー: {e}")
            return []
    
    def get_alert_summary(self) -> AlertSummary:
        """アラートサマリー取得"""
        try:
            # 最近のアラート（過去7日間）
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_alerts = [
                alert for alert in self.alert_history
                if alert.created_at >= recent_cutoff
            ]
            
            # 重要度別カウント
            critical_alerts = len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL])
            warning_alerts = len([a for a in recent_alerts if a.severity == AlertSeverity.WARNING])
            info_alerts = len([a for a in recent_alerts if a.severity == AlertSeverity.INFO])
            emergency_alerts = len([a for a in recent_alerts if a.severity == AlertSeverity.EMERGENCY])
            
            # 種別別カウント
            alerts_by_type = {}
            for alert in recent_alerts:
                alert_type = alert.type.value
                alerts_by_type[alert_type] = alerts_by_type.get(alert_type, 0) + 1
            
            # 銘柄別カウント
            alerts_by_symbol = {}
            for alert in recent_alerts:
                symbol = alert.symbol
                alerts_by_symbol[symbol] = alerts_by_symbol.get(symbol, 0) + 1
            
            # トップリスク（重要度の高いアラート）
            top_risks = sorted(
                recent_alerts,
                key=lambda x: self._get_alert_priority_score(x),
                reverse=True
            )[:5]
            
            return AlertSummary(
                total_alerts=len(recent_alerts),
                critical_alerts=critical_alerts,
                warning_alerts=warning_alerts,
                info_alerts=info_alerts,
                emergency_alerts=emergency_alerts,
                alerts_by_type=alerts_by_type,
                alerts_by_symbol=alerts_by_symbol,
                recent_alerts=recent_alerts[-10:],  # 最新10件
                top_risks=[self._format_alert_for_display(alert) for alert in top_risks]
            )
            
        except Exception as e:
            self.logger.error(f"アラートサマリー取得エラー: {e}")
            return AlertSummary(
                total_alerts=0,
                critical_alerts=0,
                warning_alerts=0,
                info_alerts=0,
                emergency_alerts=0,
                alerts_by_type={},
                alerts_by_symbol={},
                recent_alerts=[],
                top_risks=[]
            )
    
    def get_personalized_recommendations(
        self,
        portfolio_data: Dict[str, Dict[str, Any]],
        user_risk_tolerance: str = "medium"
    ) -> List[Dict[str, Any]]:
        """個人化された推奨事項生成"""
        try:
            recommendations = []
            
            # ユーザーのリスク許容度に基づく推奨事項
            risk_tolerance_multiplier = self._get_risk_tolerance_multiplier(user_risk_tolerance)
            
            # ポートフォリオ分析
            portfolio_analysis = self._analyze_portfolio_risk(portfolio_data)
            
            # 高リスク銘柄の推奨事項
            if portfolio_analysis["high_risk_count"] > 0:
                recommendations.append({
                    "type": "HIGH_RISK_REDUCTION",
                    "priority": "HIGH",
                    "title": "高リスク銘柄の見直し",
                    "description": f"{portfolio_analysis['high_risk_count']}銘柄が高リスクのため、投資見直しを推奨します",
                    "action": "高リスク銘柄の売却またはポジションサイズの削減を検討してください",
                    "impact": "リスク削減効果: 高",
                    "effort": "実装難易度: 中"
                })
            
            # ポートフォリオ分散の推奨事項
            if portfolio_analysis["diversification_score"] < 0.5:
                recommendations.append({
                    "type": "DIVERSIFICATION",
                    "priority": "MEDIUM",
                    "title": "ポートフォリオの分散投資",
                    "description": "ポートフォリオの分散が不十分です",
                    "action": "異なるセクターや銘柄への分散投資を検討してください",
                    "impact": "リスク分散効果: 中",
                    "effort": "実装難易度: 低"
                })
            
            # ポジションサイズの推奨事項
            if portfolio_analysis["max_position_ratio"] > 0.2:
                recommendations.append({
                    "type": "POSITION_SIZING",
                    "priority": "MEDIUM",
                    "title": "ポジションサイズの調整",
                    "description": "特定銘柄への集中投資が過度です",
                    "action": "ポジションサイズを口座残高の10%以下に調整してください",
                    "impact": "リスク分散効果: 中",
                    "effort": "実装難易度: 低"
                })
            
            # リスク許容度に基づく調整
            for rec in recommendations:
                if user_risk_tolerance == "low":
                    rec["priority"] = "HIGH" if rec["priority"] == "MEDIUM" else rec["priority"]
                elif user_risk_tolerance == "high":
                    rec["priority"] = "MEDIUM" if rec["priority"] == "HIGH" else rec["priority"]
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"個人化推奨事項生成エラー: {e}")
            return []
    
    def create_alert_notification(
        self,
        alert: RiskAlert,
        notification_methods: List[str] = None
    ) -> Dict[str, Any]:
        """アラート通知作成"""
        try:
            if notification_methods is None:
                notification_methods = ["email", "push"]
            
            notification = {
                "alert_id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity.value,
                "symbol": alert.symbol,
                "created_at": alert.created_at.isoformat(),
                "notification_methods": notification_methods,
                "metadata": alert.metadata
            }
            
            return {
                "success": True,
                "data": notification
            }
            
        except Exception as e:
            self.logger.error(f"アラート通知作成エラー: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # プライベートメソッド群
    def _generate_stock_alerts(self, symbol: str, data: Dict[str, Any]) -> List[RiskAlert]:
        """銘柄アラート生成"""
        alerts = []
        
        try:
            stock_data = data.get('stock_data')
            current_price = data.get('current_price', 0)
            position_size = data.get('position_size', 0)
            account_balance = data.get('account_balance', 1000000.0)
            
            if stock_data is None or stock_data.empty:
                return alerts
            
            # リスク指標計算
            volatility = self._calculate_volatility(stock_data)
            var_95 = self._calculate_var_95(stock_data)
            max_drawdown = self._calculate_max_drawdown(stock_data)
            risk_score = self._calculate_risk_score(volatility, var_95, max_drawdown)
            
            # 高リスクアラート
            if risk_score > self.alert_settings["high_risk_threshold"]:
                alerts.append(self._create_alert(
                    symbol=symbol,
                    alert_type=AlertType.HIGH_RISK,
                    severity=AlertSeverity.CRITICAL,
                    title=f"{symbol}: 高リスク警告",
                    message=f"{symbol}のリスクスコアが{risk_score:.1f}と高く、投資リスクが高い状態です",
                    recommendation="投資を見送るか、ポジションサイズを大幅に削減してください",
                    metadata={"risk_score": risk_score, "volatility": volatility}
                ))
            
            # 高ボラティリティアラート
            if volatility > self.alert_settings["high_volatility_threshold"]:
                alerts.append(self._create_alert(
                    symbol=symbol,
                    alert_type=AlertType.HIGH_VOLATILITY,
                    severity=AlertSeverity.WARNING,
                    title=f"{symbol}: 高ボラティリティ警告",
                    message=f"{symbol}のボラティリティが{volatility:.1%}と高く、価格変動が激しい状態です",
                    recommendation="注意深く投資し、損切りラインを設定してください",
                    metadata={"volatility": volatility}
                ))
            
            # 高損失可能性アラート
            max_loss_amount = current_price * position_size * var_95 * 2
            max_loss_ratio = max_loss_amount / account_balance
            if max_loss_ratio > self.alert_settings["max_loss_ratio_threshold"]:
                alerts.append(self._create_alert(
                    symbol=symbol,
                    alert_type=AlertType.HIGH_LOSS_POTENTIAL,
                    severity=AlertSeverity.CRITICAL,
                    title=f"{symbol}: 高損失可能性警告",
                    message=f"{symbol}の最大損失予想額が{max_loss_amount:,.0f}円と高く、口座残高の{max_loss_ratio:.1%}に相当します",
                    recommendation="ポジションサイズを削減するか、投資を見送ってください",
                    metadata={"max_loss_amount": max_loss_amount, "max_loss_ratio": max_loss_ratio}
                ))
            
            # ポジションサイズ警告
            position_ratio = (current_price * position_size) / account_balance
            if position_ratio > self.alert_settings["position_size_threshold"]:
                alerts.append(self._create_alert(
                    symbol=symbol,
                    alert_type=AlertType.POSITION_SIZE_WARNING,
                    severity=AlertSeverity.WARNING,
                    title=f"{symbol}: ポジションサイズ警告",
                    message=f"{symbol}のポジションサイズが口座残高の{position_ratio:.1%}と大きすぎます",
                    recommendation="ポジションサイズを口座残高の10%以下に調整してください",
                    metadata={"position_ratio": position_ratio}
                ))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"銘柄アラート生成エラー {symbol}: {e}")
            return []
    
    def _generate_portfolio_alerts(
        self, 
        portfolio_data: Dict[str, Dict[str, Any]], 
        market_data: Optional[Dict[str, Any]]
    ) -> List[RiskAlert]:
        """ポートフォリオアラート生成"""
        alerts = []
        
        try:
            # ポートフォリオ分析
            portfolio_analysis = self._analyze_portfolio_risk(portfolio_data)
            
            # ポートフォリオ不均衡アラート
            if portfolio_analysis["diversification_score"] < 0.3:
                alerts.append(self._create_alert(
                    symbol="PORTFOLIO",
                    alert_type=AlertType.PORTFOLIO_IMBALANCE,
                    severity=AlertSeverity.WARNING,
                    title="ポートフォリオ不均衡警告",
                    message="ポートフォリオの分散が不十分で、特定の銘柄やセクターに集中しています",
                    recommendation="異なるセクターや銘柄への分散投資を検討してください",
                    metadata={"diversification_score": portfolio_analysis["diversification_score"]}
                ))
            
            # 高リスク銘柄集中アラート
            if portfolio_analysis["high_risk_ratio"] > 0.5:
                alerts.append(self._create_alert(
                    symbol="PORTFOLIO",
                    alert_type=AlertType.HIGH_RISK,
                    severity=AlertSeverity.CRITICAL,
                    title="高リスク銘柄集中警告",
                    message=f"ポートフォリオの{portfolio_analysis['high_risk_ratio']:.1%}が高リスク銘柄で構成されています",
                    recommendation="高リスク銘柄の売却または低リスク銘柄への分散投資を検討してください",
                    metadata={"high_risk_ratio": portfolio_analysis["high_risk_ratio"]}
                ))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"ポートフォリオアラート生成エラー: {e}")
            return []
    
    def _generate_market_alerts(self, market_data: Dict[str, Any]) -> List[RiskAlert]:
        """市場アラート生成"""
        alerts = []
        
        try:
            # 市場ボラティリティアラート
            market_volatility = market_data.get("volatility", 0)
            if market_volatility > 0.3:
                alerts.append(self._create_alert(
                    symbol="MARKET",
                    alert_type=AlertType.MARKET_STRESS,
                    severity=AlertSeverity.WARNING,
                    title="市場高ボラティリティ警告",
                    message=f"市場全体のボラティリティが{market_volatility:.1%}と高く、不安定な状況です",
                    recommendation="投資を控えるか、より保守的な投資戦略を検討してください",
                    metadata={"market_volatility": market_volatility}
                ))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"市場アラート生成エラー: {e}")
            return []
    
    def _create_alert(
        self,
        symbol: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        recommendation: str,
        metadata: Dict[str, Any] = None
    ) -> RiskAlert:
        """アラート作成"""
        alert_id = f"{symbol}_{alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return RiskAlert(
            id=alert_id,
            type=alert_type,
            severity=severity,
            symbol=symbol,
            title=title,
            message=message,
            recommendation=recommendation,
            action_required=severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            metadata=metadata or {},
            color_code=self.alert_settings.get("severity_colors", {}).get(severity.value, "#666666"),
            icon=self.alert_settings.get("severity_icons", {}).get(severity.value, "info")
        )
    
    def _deduplicate_and_prioritize_alerts(self, alerts: List[RiskAlert]) -> List[RiskAlert]:
        """アラートの重複除去と優先度調整"""
        try:
            # 重複除去（同じ銘柄・種別のアラート）
            seen = set()
            unique_alerts = []
            
            for alert in alerts:
                key = (alert.symbol, alert.type.value)
                if key not in seen:
                    seen.add(key)
                    unique_alerts.append(alert)
            
            # 優先度順にソート
            unique_alerts.sort(key=lambda x: self._get_alert_priority_score(x), reverse=True)
            
            return unique_alerts
            
        except Exception as e:
            self.logger.error(f"アラート重複除去・優先度調整エラー: {e}")
            return alerts
    
    def _get_alert_priority_score(self, alert: RiskAlert) -> int:
        """アラート優先度スコア計算"""
        severity_scores = {
            AlertSeverity.EMERGENCY: 100,
            AlertSeverity.CRITICAL: 80,
            AlertSeverity.WARNING: 60,
            AlertSeverity.INFO: 40
        }
        
        return severity_scores.get(alert.severity, 0)
    
    def _cleanup_old_alerts(self):
        """古いアラートの削除"""
        try:
            retention_days = self.alert_settings.get("alert_retention_days", 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            self.alert_history = [
                alert for alert in self.alert_history
                if alert.created_at >= cutoff_date
            ]
            
        except Exception as e:
            self.logger.error(f"古いアラート削除エラー: {e}")
    
    def _format_alert_for_display(self, alert: RiskAlert) -> Dict[str, Any]:
        """表示用アラートフォーマット"""
        return {
            "id": alert.id,
            "type": alert.type.value,
            "severity": alert.severity.value,
            "symbol": alert.symbol,
            "title": alert.title,
            "message": alert.message,
            "recommendation": alert.recommendation,
            "action_required": alert.action_required,
            "created_at": alert.created_at.isoformat(),
            "color_code": alert.color_code,
            "icon": alert.icon,
            "metadata": alert.metadata
        }
    
    def _get_risk_tolerance_multiplier(self, risk_tolerance: str) -> float:
        """リスク許容度倍率取得"""
        multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5
        }
        return multipliers.get(risk_tolerance, 1.0)
    
    def _analyze_portfolio_risk(self, portfolio_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """ポートフォリオリスク分析"""
        try:
            total_positions = len(portfolio_data)
            if total_positions == 0:
                return {
                    "high_risk_count": 0,
                    "high_risk_ratio": 0.0,
                    "diversification_score": 1.0,
                    "max_position_ratio": 0.0
                }
            
            high_risk_count = 0
            total_value = 0.0
            max_position_value = 0.0
            
            for symbol, data in portfolio_data.items():
                if not data or 'stock_data' not in data:
                    continue
                
                stock_data = data.get('stock_data')
                current_price = data.get('current_price', 0)
                position_size = data.get('position_size', 0)
                
                if stock_data is None or stock_data.empty:
                    continue
                
                # リスクスコア計算
                volatility = self._calculate_volatility(stock_data)
                var_95 = self._calculate_var_95(stock_data)
                max_drawdown = self._calculate_max_drawdown(stock_data)
                risk_score = self._calculate_risk_score(volatility, var_95, max_drawdown)
                
                if risk_score > self.alert_settings["high_risk_threshold"]:
                    high_risk_count += 1
                
                # ポジション価値計算
                position_value = current_price * position_size
                total_value += position_value
                max_position_value = max(max_position_value, position_value)
            
            # 分散スコア計算（簡易版）
            diversification_score = min(1.0, total_positions / 10.0)  # 10銘柄で満点
            
            return {
                "high_risk_count": high_risk_count,
                "high_risk_ratio": high_risk_count / total_positions,
                "diversification_score": diversification_score,
                "max_position_ratio": max_position_value / total_value if total_value > 0 else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスク分析エラー: {e}")
            return {
                "high_risk_count": 0,
                "high_risk_ratio": 0.0,
                "diversification_score": 1.0,
                "max_position_ratio": 0.0
            }
    
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
        """リスクスコア計算"""
        volatility_score = min(volatility * 200, 40)
        var_score = min(var_95 * 1000, 30)
        drawdown_score = min(max_drawdown * 200, 30)
        
        return min(100, volatility_score + var_score + drawdown_score)
