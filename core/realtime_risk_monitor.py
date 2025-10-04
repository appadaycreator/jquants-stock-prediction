#!/usr/bin/env python3
"""
リアルタイムリスク監視システム
記事の手法を超える高度なリスク監視機能を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import threading
import time
from queue import Queue, Empty
import json
import warnings
warnings.filterwarnings('ignore')


class AlertLevel(Enum):
    """アラートレベル"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class RiskEvent(Enum):
    """リスクイベント"""
    HIGH_VOLATILITY = "high_volatility"
    LARGE_DRAWDOWN = "large_drawdown"
    VAR_BREACH = "var_breach"
    CORRELATION_SPIKE = "correlation_spike"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    MARKET_CRASH = "market_crash"
    POSITION_OVERWEIGHT = "position_overweight"
    STOP_LOSS_HIT = "stop_loss_hit"
    TAKE_PROFIT_HIT = "take_profit_hit"


@dataclass
class RiskAlert:
    """リスクアラート"""
    timestamp: datetime
    event_type: RiskEvent
    alert_level: AlertLevel
    symbol: str
    message: str
    current_value: float
    threshold_value: float
    recommendation: str
    metadata: Dict[str, Any]


@dataclass
class RiskSnapshot:
    """リスクスナップショット"""
    timestamp: datetime
    symbol: str
    current_price: float
    position_size: float
    var_95: float
    var_99: float
    max_drawdown: float
    volatility: float
    beta: float
    correlation: float
    risk_level: str
    alerts: List[RiskAlert]
    recommendations: List[str]


class RealtimeRiskMonitor:
    """リアルタイムリスク監視システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # 監視状態
        self.is_monitoring = False
        self.monitor_thread = None
        self.alert_queue = Queue()
        self.data_queue = Queue()
        
        # 履歴データ
        self.risk_history = []
        self.alert_history = []
        self.snapshot_history = []
        
        # コールバック関数
        self.alert_callbacks = []
        self.data_callbacks = []
        
        # 監視対象
        self.monitored_symbols = set()
        self.risk_thresholds = {}
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "monitoring": {
                "update_interval": 1.0,  # 更新間隔（秒）
                "max_history": 10000,   # 最大履歴数
                "alert_retention": 1000  # アラート保持数
            },
            "risk_thresholds": {
                "var_95_warning": 0.03,    # 3%で警告
                "var_95_critical": 0.05,   # 5%で重要
                "var_99_warning": 0.05,    # 5%で警告
                "var_99_critical": 0.08,   # 8%で重要
                "max_drawdown_warning": 0.10,  # 10%で警告
                "max_drawdown_critical": 0.15,  # 15%で重要
                "volatility_warning": 0.25,    # 25%で警告
                "volatility_critical": 0.40,    # 40%で重要
                "correlation_warning": 0.8,     # 80%で警告
                "correlation_critical": 0.9     # 90%で重要
            },
            "position_limits": {
                "max_position_size": 0.1,     # 最大ポジションサイズ
                "max_portfolio_risk": 0.05,    # 最大ポートフォリオリスク
                "concentration_limit": 0.2    # 集中度制限
            },
            "market_conditions": {
                "high_volatility_threshold": 0.30,
                "low_liquidity_threshold": 100000,
                "market_crash_threshold": -0.05
            }
        }
    
    def start_monitoring(self, symbols: List[str], update_interval: float = None):
        """監視開始"""
        try:
            if self.is_monitoring:
                self.logger.warning("監視は既に開始されています")
                return
            
            self.monitored_symbols = set(symbols)
            interval = update_interval or self.config["monitoring"]["update_interval"]
            
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(interval,),
                daemon=True
            )
            self.monitor_thread.start()
            
            self.logger.info(f"リアルタイムリスク監視を開始: {symbols}")
            
        except Exception as e:
            self.logger.error(f"監視開始エラー: {e}")
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """監視停止"""
        try:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5.0)
            
            self.logger.info("リアルタイムリスク監視を停止")
            
        except Exception as e:
            self.logger.error(f"監視停止エラー: {e}")
    
    def add_alert_callback(self, callback: Callable[[RiskAlert], None]):
        """アラートコールバック追加"""
        self.alert_callbacks.append(callback)
    
    def add_data_callback(self, callback: Callable[[RiskSnapshot], None]):
        """データコールバック追加"""
        self.data_callbacks.append(callback)
    
    def update_risk_data(
        self,
        symbol: str,
        current_price: float,
        position_size: float,
        risk_metrics: Dict[str, float],
        market_data: Optional[Dict[str, Any]] = None
    ):
        """リスクデータ更新"""
        try:
            # リスクスナップショット作成
            snapshot = self._create_risk_snapshot(
                symbol, current_price, position_size, risk_metrics, market_data
            )
            
            # アラートチェック
            alerts = self._check_risk_alerts(snapshot)
            snapshot.alerts = alerts
            
            # 推奨事項生成
            recommendations = self._generate_recommendations(snapshot, alerts)
            snapshot.recommendations = recommendations
            
            # 履歴に追加
            self._add_to_history(snapshot, alerts)
            
            # コールバック実行
            self._execute_callbacks(snapshot, alerts)
            
            # データキューに追加
            self.data_queue.put(snapshot)
            
        except Exception as e:
            self.logger.error(f"リスクデータ更新エラー: {e}")
    
    def get_current_risk_status(self, symbol: str = None) -> Dict[str, Any]:
        """現在のリスク状況取得"""
        try:
            if symbol:
                # 特定銘柄の状況
                recent_snapshots = [
                    s for s in self.snapshot_history
                    if s.symbol == symbol
                ][-10:]  # 最近10件
            else:
                # 全銘柄の状況
                recent_snapshots = self.snapshot_history[-50:]  # 最近50件
            
            if not recent_snapshots:
                return {"status": "no_data"}
            
            # 統計計算
            total_alerts = sum(len(s.alerts) for s in recent_snapshots)
            critical_alerts = sum(
                1 for s in recent_snapshots
                for a in s.alerts
                if a.alert_level == AlertLevel.CRITICAL
            )
            
            avg_volatility = np.mean([s.volatility for s in recent_snapshots])
            avg_var_95 = np.mean([s.var_95 for s in recent_snapshots])
            max_drawdown = max([s.max_drawdown for s in recent_snapshots])
            
            return {
                "status": "monitoring",
                "total_snapshots": len(recent_snapshots),
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "avg_volatility": avg_volatility,
                "avg_var_95": avg_var_95,
                "max_drawdown": max_drawdown,
                "last_update": recent_snapshots[-1].timestamp.isoformat() if recent_snapshots else None
            }
            
        except Exception as e:
            self.logger.error(f"リスク状況取得エラー: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_risk_alerts(self, symbol: str = None, level: AlertLevel = None) -> List[RiskAlert]:
        """リスクアラート取得"""
        try:
            alerts = []
            
            for alert in self.alert_history:
                if symbol and alert.symbol != symbol:
                    continue
                if level and alert.alert_level != level:
                    continue
                
                alerts.append(alert)
            
            # 時系列でソート
            alerts.sort(key=lambda x: x.timestamp, reverse=True)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"アラート取得エラー: {e}")
            return []
    
    def get_risk_trends(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """リスクトレンド取得"""
        try:
            # 指定期間のデータ取得
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_snapshots = [
                s for s in self.snapshot_history
                if s.symbol == symbol and s.timestamp >= cutoff_date
            ]
            
            if len(recent_snapshots) < 2:
                return {"status": "insufficient_data"}
            
            # トレンド計算
            timestamps = [s.timestamp for s in recent_snapshots]
            volatilities = [s.volatility for s in recent_snapshots]
            var_95s = [s.var_95 for s in recent_snapshots]
            max_drawdowns = [s.max_drawdown for s in recent_snapshots]
            
            # 線形回帰によるトレンド
            volatility_trend = self._calculate_trend(volatilities)
            var_trend = self._calculate_trend(var_95s)
            drawdown_trend = self._calculate_trend(max_drawdowns)
            
            return {
                "period_days": days,
                "data_points": len(recent_snapshots),
                "volatility_trend": volatility_trend,
                "var_trend": var_trend,
                "drawdown_trend": drawdown_trend,
                "current_volatility": volatilities[-1],
                "current_var_95": var_95s[-1],
                "current_max_drawdown": max_drawdowns[-1],
                "trend_direction": self._determine_overall_trend([
                    volatility_trend, var_trend, drawdown_trend
                ])
            }
            
        except Exception as e:
            self.logger.error(f"リスクトレンド取得エラー: {e}")
            return {"status": "error", "error": str(e)}
    
    def _monitoring_loop(self, update_interval: float):
        """監視ループ"""
        while self.is_monitoring:
            try:
                # データキューから処理
                while not self.data_queue.empty():
                    try:
                        snapshot = self.data_queue.get_nowait()
                        self._process_snapshot(snapshot)
                    except Empty:
                        break
                
                # アラートキューから処理
                while not self.alert_queue.empty():
                    try:
                        alert = self.alert_queue.get_nowait()
                        self._process_alert(alert)
                    except Empty:
                        break
                
                time.sleep(update_interval)
                
            except Exception as e:
                self.logger.error(f"監視ループエラー: {e}")
                time.sleep(update_interval)
    
    def _create_risk_snapshot(
        self,
        symbol: str,
        current_price: float,
        position_size: float,
        risk_metrics: Dict[str, float],
        market_data: Optional[Dict[str, Any]]
    ) -> RiskSnapshot:
        """リスクスナップショット作成"""
        return RiskSnapshot(
            timestamp=datetime.now(),
            symbol=symbol,
            current_price=current_price,
            position_size=position_size,
            var_95=risk_metrics.get('var_95', 0.0),
            var_99=risk_metrics.get('var_99', 0.0),
            max_drawdown=risk_metrics.get('max_drawdown', 0.0),
            volatility=risk_metrics.get('volatility', 0.0),
            beta=risk_metrics.get('beta', 1.0),
            correlation=risk_metrics.get('correlation', 0.0),
            risk_level=risk_metrics.get('risk_level', 'MEDIUM'),
            alerts=[],
            recommendations=[]
        )
    
    def _check_risk_alerts(self, snapshot: RiskSnapshot) -> List[RiskAlert]:
        """リスクアラートチェック"""
        alerts = []
        thresholds = self.config["risk_thresholds"]
        
        # VaR 95% チェック
        if snapshot.var_95 >= thresholds["var_95_critical"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.VAR_BREACH,
                alert_level=AlertLevel.CRITICAL,
                symbol=snapshot.symbol,
                message=f"VaR 95% が制限値を超過: {snapshot.var_95:.3f}",
                current_value=snapshot.var_95,
                threshold_value=thresholds["var_95_critical"],
                recommendation="ポジションサイズを削減してください",
                metadata={"var_type": "95%"}
            ))
        elif snapshot.var_95 >= thresholds["var_95_warning"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.VAR_BREACH,
                alert_level=AlertLevel.WARNING,
                symbol=snapshot.symbol,
                message=f"VaR 95% が警告レベル: {snapshot.var_95:.3f}",
                current_value=snapshot.var_95,
                threshold_value=thresholds["var_95_warning"],
                recommendation="リスクを監視してください",
                metadata={"var_type": "95%"}
            ))
        
        # 最大ドローダウンチェック
        if snapshot.max_drawdown >= thresholds["max_drawdown_critical"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.LARGE_DRAWDOWN,
                alert_level=AlertLevel.CRITICAL,
                symbol=snapshot.symbol,
                message=f"最大ドローダウンが制限値を超過: {snapshot.max_drawdown:.3f}",
                current_value=snapshot.max_drawdown,
                threshold_value=thresholds["max_drawdown_critical"],
                recommendation="緊急のリスク管理が必要です",
                metadata={}
            ))
        elif snapshot.max_drawdown >= thresholds["max_drawdown_warning"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.LARGE_DRAWDOWN,
                alert_level=AlertLevel.WARNING,
                symbol=snapshot.symbol,
                message=f"最大ドローダウンが警告レベル: {snapshot.max_drawdown:.3f}",
                current_value=snapshot.max_drawdown,
                threshold_value=thresholds["max_drawdown_warning"],
                recommendation="ドローダウンを監視してください",
                metadata={}
            ))
        
        # ボラティリティチェック
        if snapshot.volatility >= thresholds["volatility_critical"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.HIGH_VOLATILITY,
                alert_level=AlertLevel.CRITICAL,
                symbol=snapshot.symbol,
                message=f"ボラティリティが制限値を超過: {snapshot.volatility:.3f}",
                current_value=snapshot.volatility,
                threshold_value=thresholds["volatility_critical"],
                recommendation="ポジションサイズを削減してください",
                metadata={}
            ))
        elif snapshot.volatility >= thresholds["volatility_warning"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.HIGH_VOLATILITY,
                alert_level=AlertLevel.WARNING,
                symbol=snapshot.symbol,
                message=f"ボラティリティが警告レベル: {snapshot.volatility:.3f}",
                current_value=snapshot.volatility,
                threshold_value=thresholds["volatility_warning"],
                recommendation="ボラティリティを監視してください",
                metadata={}
            ))
        
        # 相関チェック
        if snapshot.correlation >= thresholds["correlation_critical"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.CORRELATION_SPIKE,
                alert_level=AlertLevel.CRITICAL,
                symbol=snapshot.symbol,
                message=f"市場相関が制限値を超過: {snapshot.correlation:.3f}",
                current_value=snapshot.correlation,
                threshold_value=thresholds["correlation_critical"],
                recommendation="分散投資を検討してください",
                metadata={}
            ))
        elif snapshot.correlation >= thresholds["correlation_warning"]:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.CORRELATION_SPIKE,
                alert_level=AlertLevel.WARNING,
                symbol=snapshot.symbol,
                message=f"市場相関が警告レベル: {snapshot.correlation:.3f}",
                current_value=snapshot.correlation,
                threshold_value=thresholds["correlation_warning"],
                recommendation="相関を監視してください",
                metadata={}
            ))
        
        # ポジションサイズチェック
        max_position = self.config["position_limits"]["max_position_size"]
        if snapshot.position_size > max_position:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                event_type=RiskEvent.POSITION_OVERWEIGHT,
                alert_level=AlertLevel.WARNING,
                symbol=snapshot.symbol,
                message=f"ポジションサイズが制限を超過: {snapshot.position_size:.3f}",
                current_value=snapshot.position_size,
                threshold_value=max_position,
                recommendation="ポジションサイズを削減してください",
                metadata={}
            ))
        
        return alerts
    
    def _generate_recommendations(self, snapshot: RiskSnapshot, alerts: List[RiskAlert]) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # アラートに基づく推奨事項
        for alert in alerts:
            if alert.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                recommendations.append(alert.recommendation)
        
        # リスクレベルに基づく推奨事項
        if snapshot.risk_level == "HIGH":
            recommendations.append("高リスク銘柄のため、ポジションサイズを削減することを検討してください")
        elif snapshot.risk_level == "VERY_HIGH":
            recommendations.append("非常に高リスク銘柄のため、ポジションの見直しを強く推奨します")
        
        # ボラティリティに基づく推奨事項
        if snapshot.volatility > 0.3:
            recommendations.append("高ボラティリティ環境のため、損切り設定を厳格にしてください")
        
        # 相関に基づく推奨事項
        if snapshot.correlation > 0.8:
            recommendations.append("市場相関が高いため、分散投資を検討してください")
        
        return list(set(recommendations))  # 重複除去
    
    def _add_to_history(self, snapshot: RiskSnapshot, alerts: List[RiskAlert]):
        """履歴に追加"""
        # スナップショット履歴
        self.snapshot_history.append(snapshot)
        if len(self.snapshot_history) > self.config["monitoring"]["max_history"]:
            self.snapshot_history.pop(0)
        
        # アラート履歴
        self.alert_history.extend(alerts)
        if len(self.alert_history) > self.config["monitoring"]["alert_retention"]:
            self.alert_history = self.alert_history[-self.config["monitoring"]["alert_retention"]:]
    
    def _execute_callbacks(self, snapshot: RiskSnapshot, alerts: List[RiskAlert]):
        """コールバック実行"""
        # データコールバック
        for callback in self.data_callbacks:
            try:
                callback(snapshot)
            except Exception as e:
                self.logger.error(f"データコールバックエラー: {e}")
        
        # アラートコールバック
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"アラートコールバックエラー: {e}")
    
    def _process_snapshot(self, snapshot: RiskSnapshot):
        """スナップショット処理"""
        # 必要に応じて追加の処理を実装
        pass
    
    def _process_alert(self, alert: RiskAlert):
        """アラート処理"""
        # 必要に応じて追加の処理を実装
        pass
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """トレンド計算"""
        if len(values) < 2:
            return {"slope": 0.0, "direction": "flat", "strength": 0.0}
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # NaNチェック
        if np.any(np.isnan(y)):
            return {"slope": 0.0, "direction": "flat", "strength": 0.0}
        
        # 線形回帰
        try:
            slope, intercept = np.polyfit(x, y, 1)
        except:
            return {"slope": 0.0, "direction": "flat", "strength": 0.0}
        
        # 方向判定（閾値を下げる）
        if slope > 0.001:  # より敏感に
            direction = "increasing"
        elif slope < -0.001:
            direction = "decreasing"
        else:
            direction = "flat"
        
        # 強度計算
        try:
            r_squared = np.corrcoef(x, y)[0, 1] ** 2
            if np.isnan(r_squared):
                r_squared = 0.0
            strength = abs(slope) * r_squared
        except:
            r_squared = 0.0
            strength = 0.0
        
        return {
            "slope": slope,
            "direction": direction,
            "strength": strength,
            "r_squared": r_squared
        }
    
    def _determine_overall_trend(self, trends: List[Dict[str, Any]]) -> str:
        """全体的なトレンド判定"""
        increasing_count = sum(1 for t in trends if t["direction"] == "increasing")
        decreasing_count = sum(1 for t in trends if t["direction"] == "decreasing")
        
        if increasing_count > decreasing_count:
            return "increasing"
        elif decreasing_count > increasing_count:
            return "decreasing"
        else:
            return "mixed"
    
    def export_risk_report(self, symbol: str = None, days: int = 7) -> Dict[str, Any]:
        """リスクレポート出力"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if symbol:
                snapshots = [
                    s for s in self.snapshot_history
                    if s.symbol == symbol and s.timestamp >= cutoff_date
                ]
                alerts = [
                    a for a in self.alert_history
                    if a.symbol == symbol and a.timestamp >= cutoff_date
                ]
            else:
                snapshots = [
                    s for s in self.snapshot_history
                    if s.timestamp >= cutoff_date
                ]
                alerts = [
                    a for a in self.alert_history
                    if a.timestamp >= cutoff_date
                ]
            
            # 統計計算
            if snapshots:
                avg_volatility = np.mean([s.volatility for s in snapshots])
                max_volatility = max([s.volatility for s in snapshots])
                avg_var_95 = np.mean([s.var_95 for s in snapshots])
                max_var_95 = max([s.var_95 for s in snapshots])
                avg_drawdown = np.mean([s.max_drawdown for s in snapshots])
                max_drawdown = max([s.max_drawdown for s in snapshots])
            else:
                avg_volatility = max_volatility = 0.0
                avg_var_95 = max_var_95 = 0.0
                avg_drawdown = max_drawdown = 0.0
            
            # アラート統計
            alert_counts = {}
            for alert in alerts:
                level = alert.alert_level.value
                alert_counts[level] = alert_counts.get(level, 0) + 1
            
            return {
                "report_period": f"{days} days",
                "symbol": symbol or "all",
                "total_snapshots": len(snapshots),
                "total_alerts": len(alerts),
                "alert_counts": alert_counts,
                "risk_metrics": {
                    "avg_volatility": avg_volatility,
                    "max_volatility": max_volatility,
                    "avg_var_95": avg_var_95,
                    "max_var_95": max_var_95,
                    "avg_drawdown": avg_drawdown,
                    "max_drawdown": max_drawdown
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"リスクレポート出力エラー: {e}")
            return {"error": str(e)}