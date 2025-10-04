#!/usr/bin/env python3
"""
リアルタイムリスク監視システム

目的: リアルタイムリスク監視と自動損切り
仕様: 市場データ・ボラティリティに基づく動的調整
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
import asyncio
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')


class AlertLevel(Enum):
    """アラートレベル"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class RiskEventType(Enum):
    """リスクイベント種別"""
    STOP_LOSS_TRIGGERED = "stop_loss_triggered"
    TAKE_PROFIT_TRIGGERED = "take_profit_triggered"
    VAR_BREACH = "var_breach"
    DRAWDOWN_BREACH = "drawdown_breach"
    VOLATILITY_SPIKE = "volatility_spike"
    CORRELATION_BREACH = "correlation_breach"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    POSITION_LIMIT_BREACH = "position_limit_breach"


@dataclass
class RiskAlert:
    """リスクアラート"""
    timestamp: datetime
    event_type: RiskEventType
    level: AlertLevel
    symbol: str
    message: str
    data: Dict[str, Any]
    action_required: bool
    auto_execute: bool


@dataclass
class RiskThreshold:
    """リスク閾値"""
    name: str
    value: float
    operator: str  # >, <, >=, <=, ==
    alert_level: AlertLevel
    auto_action: bool
    action_type: str  # stop_loss, take_profit, close_position, reduce_size


@dataclass
class MonitoringConfig:
    """監視設定"""
    update_interval: int  # 秒
    max_workers: int
    alert_cooldown: int  # 秒
    auto_execute_enabled: bool
    notification_enabled: bool
    log_level: str


class RealtimeRiskMonitor:
    """リアルタイムリスク監視システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.monitoring_config = self._get_monitoring_config()
        
        # 監視状態
        self.is_monitoring = False
        self.monitor_thread = None
        self.executor = ThreadPoolExecutor(max_workers=self.monitoring_config.max_workers)
        
        # データストレージ
        self.positions = {}
        self.market_data = {}
        self.risk_metrics = {}
        self.risk_thresholds = {}
        self.alert_history = []
        
        # コールバック関数
        self.alert_callbacks = []
        self.action_callbacks = []
        
        # 統計情報
        self.monitoring_stats = {
            'total_alerts': 0,
            'critical_alerts': 0,
            'auto_actions': 0,
            'last_update': None
        }
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "monitoring": {
                "update_interval": 5,  # 5秒
                "max_workers": 4,
                "alert_cooldown": 60,  # 60秒
                "auto_execute_enabled": True,
                "notification_enabled": True,
                "log_level": "INFO"
            },
            "risk_thresholds": {
                "var_95": {"value": 0.02, "operator": ">", "level": "warning", "auto_action": True},
                "var_99": {"value": 0.05, "operator": ">", "level": "critical", "auto_action": True},
                "max_drawdown": {"value": 0.10, "operator": ">", "level": "critical", "auto_action": True},
                "volatility": {"value": 0.30, "operator": ">", "level": "warning", "auto_action": False},
                "correlation": {"value": 0.80, "operator": ">", "level": "warning", "auto_action": False},
                "position_size": {"value": 0.20, "operator": ">", "level": "warning", "auto_action": True}
            },
            "auto_actions": {
                "stop_loss_percentage": 0.05,
                "position_reduction_factor": 0.5,
                "max_daily_actions": 10
            }
        }
    
    def _get_monitoring_config(self) -> MonitoringConfig:
        """監視設定取得"""
        monitoring = self.config["monitoring"]
        return MonitoringConfig(
            update_interval=monitoring["update_interval"],
            max_workers=monitoring["max_workers"],
            alert_cooldown=monitoring["alert_cooldown"],
            auto_execute_enabled=monitoring["auto_execute_enabled"],
            notification_enabled=monitoring["notification_enabled"],
            log_level=monitoring["log_level"]
        )
    
    def start_monitoring(self) -> bool:
        """監視開始"""
        try:
            if self.is_monitoring:
                self.logger.warning("監視は既に開始されています")
                return False
            
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("リアルタイムリスク監視を開始しました")
            return True
            
        except Exception as e:
            self.logger.error(f"監視開始エラー: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """監視停止"""
        try:
            if not self.is_monitoring:
                self.logger.warning("監視は既に停止されています")
                return False
            
            self.is_monitoring = False
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            self.logger.info("リアルタイムリスク監視を停止しました")
            return True
            
        except Exception as e:
            self.logger.error(f"監視停止エラー: {e}")
            return False
    
    def add_position(self, symbol: str, position_data: Dict[str, Any]) -> bool:
        """ポジション追加"""
        try:
            self.positions[symbol] = {
                **position_data,
                'added_at': datetime.now(),
                'last_update': datetime.now()
            }
            
            self.logger.info(f"ポジション追加: {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"ポジション追加エラー: {e}")
            return False
    
    def update_position(self, symbol: str, position_data: Dict[str, Any]) -> bool:
        """ポジション更新"""
        try:
            if symbol not in self.positions:
                return self.add_position(symbol, position_data)
            
            self.positions[symbol].update(position_data)
            self.positions[symbol]['last_update'] = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"ポジション更新エラー: {e}")
            return False
    
    def remove_position(self, symbol: str) -> bool:
        """ポジション削除"""
        try:
            if symbol in self.positions:
                del self.positions[symbol]
                self.logger.info(f"ポジション削除: {symbol}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"ポジション削除エラー: {e}")
            return False
    
    def update_market_data(self, symbol: str, market_data: pd.DataFrame) -> bool:
        """市場データ更新"""
        try:
            self.market_data[symbol] = market_data
            return True
            
        except Exception as e:
            self.logger.error(f"市場データ更新エラー: {e}")
            return False
    
    def update_risk_metrics(self, symbol: str, risk_metrics: Dict[str, float]) -> bool:
        """リスクメトリクス更新"""
        try:
            self.risk_metrics[symbol] = {
                **risk_metrics,
                'updated_at': datetime.now()
            }
            return True
            
        except Exception as e:
            self.logger.error(f"リスクメトリクス更新エラー: {e}")
            return False
    
    def add_risk_threshold(self, name: str, threshold: RiskThreshold) -> bool:
        """リスク閾値追加"""
        try:
            self.risk_thresholds[name] = threshold
            self.logger.info(f"リスク閾値追加: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"リスク閾値追加エラー: {e}")
            return False
    
    def remove_risk_threshold(self, name: str) -> bool:
        """リスク閾値削除"""
        try:
            if name in self.risk_thresholds:
                del self.risk_thresholds[name]
                self.logger.info(f"リスク閾値削除: {name}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"リスク閾値削除エラー: {e}")
            return False
    
    def add_alert_callback(self, callback: Callable[[RiskAlert], None]) -> bool:
        """アラートコールバック追加"""
        try:
            self.alert_callbacks.append(callback)
            return True
            
        except Exception as e:
            self.logger.error(f"アラートコールバック追加エラー: {e}")
            return False
    
    def add_action_callback(self, callback: Callable[[str, Dict[str, Any]], bool]) -> bool:
        """アクションコールバック追加"""
        try:
            self.action_callbacks.append(callback)
            return True
            
        except Exception as e:
            self.logger.error(f"アクションコールバック追加エラー: {e}")
            return False
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """監視状態取得"""
        return {
            'is_monitoring': self.is_monitoring,
            'positions_count': len(self.positions),
            'market_data_count': len(self.market_data),
            'risk_thresholds_count': len(self.risk_thresholds),
            'total_alerts': self.monitoring_stats['total_alerts'],
            'critical_alerts': self.monitoring_stats['critical_alerts'],
            'auto_actions': self.monitoring_stats['auto_actions'],
            'last_update': self.monitoring_stats['last_update']
        }
    
    def get_alert_history(self, limit: int = 100) -> List[RiskAlert]:
        """アラート履歴取得"""
        return self.alert_history[-limit:]
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """リスクサマリー取得"""
        try:
            summary = {
                'total_positions': len(self.positions),
                'active_alerts': len([a for a in self.alert_history if a.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]]),
                'risk_metrics': {},
                'thresholds_status': {}
            }
            
            # リスクメトリクスサマリー
            for symbol, metrics in self.risk_metrics.items():
                summary['risk_metrics'][symbol] = {
                    'var_95': metrics.get('var_95', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0),
                    'volatility': metrics.get('volatility', 0),
                    'updated_at': metrics.get('updated_at')
                }
            
            # 閾値ステータス
            for name, threshold in self.risk_thresholds.items():
                summary['thresholds_status'][name] = {
                    'value': threshold.value,
                    'operator': threshold.operator,
                    'level': threshold.level.value,
                    'auto_action': threshold.auto_action
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"リスクサマリー取得エラー: {e}")
            return {}
    
    def _monitoring_loop(self):
        """監視ループ"""
        while self.is_monitoring:
            try:
                start_time = time.time()
                
                # リスクチェック実行
                self._check_all_risks()
                
                # 統計更新
                self.monitoring_stats['last_update'] = datetime.now()
                
                # 次の更新まで待機
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.monitoring_config.update_interval - elapsed_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"監視ループエラー: {e}")
                time.sleep(self.monitoring_config.update_interval)
    
    def _check_all_risks(self):
        """全リスクチェック"""
        try:
            # 各ポジションのリスクチェック
            for symbol, position in self.positions.items():
                self._check_position_risks(symbol, position)
            
            # ポートフォリオ全体のリスクチェック
            self._check_portfolio_risks()
            
        except Exception as e:
            self.logger.error(f"全リスクチェックエラー: {e}")
    
    def _check_position_risks(self, symbol: str, position: Dict[str, Any]):
        """個別ポジションリスクチェック"""
        try:
            # 損切りチェック
            self._check_stop_loss(symbol, position)
            
            # 利確チェック
            self._check_take_profit(symbol, position)
            
            # リスクメトリクスチェック
            if symbol in self.risk_metrics:
                self._check_risk_metrics(symbol, position, self.risk_metrics[symbol])
            
        except Exception as e:
            self.logger.error(f"個別ポジションリスクチェックエラー: {e}")
    
    def _check_portfolio_risks(self):
        """ポートフォリオ全体リスクチェック"""
        try:
            # ポートフォリオVaRチェック
            self._check_portfolio_var()
            
            # ポートフォリオドローダウンチェック
            self._check_portfolio_drawdown()
            
            # 相関リスクチェック
            self._check_correlation_risks()
            
        except Exception as e:
            self.logger.error(f"ポートフォリオ全体リスクチェックエラー: {e}")
    
    def _check_stop_loss(self, symbol: str, position: Dict[str, Any]):
        """損切りチェック"""
        try:
            current_price = position.get('current_price', 0)
            stop_loss = position.get('stop_loss', 0)
            position_type = position.get('position_type', 'LONG')
            
            if current_price == 0 or stop_loss == 0:
                return
            
            triggered = False
            
            if position_type == 'LONG' and current_price <= stop_loss:
                triggered = True
            elif position_type == 'SHORT' and current_price >= stop_loss:
                triggered = True
            
            if triggered:
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.STOP_LOSS_TRIGGERED,
                    level=AlertLevel.CRITICAL,
                    symbol=symbol,
                    message=f"損切りライン到達: {symbol}",
                    data={
                        'current_price': current_price,
                        'stop_loss': stop_loss,
                        'position_type': position_type
                    },
                    action_required=True,
                    auto_execute=True
                )
                
                self._handle_alert(alert)
                
        except Exception as e:
            self.logger.error(f"損切りチェックエラー: {e}")
    
    def _check_take_profit(self, symbol: str, position: Dict[str, Any]):
        """利確チェック"""
        try:
            current_price = position.get('current_price', 0)
            take_profit = position.get('take_profit', 0)
            position_type = position.get('position_type', 'LONG')
            
            if current_price == 0 or take_profit == 0:
                return
            
            triggered = False
            
            if position_type == 'LONG' and current_price >= take_profit:
                triggered = True
            elif position_type == 'SHORT' and current_price <= take_profit:
                triggered = True
            
            if triggered:
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.TAKE_PROFIT_TRIGGERED,
                    level=AlertLevel.INFO,
                    symbol=symbol,
                    message=f"利確ライン到達: {symbol}",
                    data={
                        'current_price': current_price,
                        'take_profit': take_profit,
                        'position_type': position_type
                    },
                    action_required=True,
                    auto_execute=True
                )
                
                self._handle_alert(alert)
                
        except Exception as e:
            self.logger.error(f"利確チェックエラー: {e}")
    
    def _check_risk_metrics(self, symbol: str, position: Dict[str, Any], risk_metrics: Dict[str, float]):
        """リスクメトリクスチェック"""
        try:
            # VaRチェック
            var_95 = risk_metrics.get('var_95', 0)
            if var_95 > 0.02:  # 2%の閾値
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.VAR_BREACH,
                    level=AlertLevel.WARNING,
                    symbol=symbol,
                    message=f"VaR超過: {symbol}",
                    data={'var_95': var_95},
                    action_required=True,
                    auto_execute=False
                )
                self._handle_alert(alert)
            
            # ドローダウンチェック
            max_drawdown = risk_metrics.get('max_drawdown', 0)
            if max_drawdown > 0.10:  # 10%の閾値
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.DRAWDOWN_BREACH,
                    level=AlertLevel.CRITICAL,
                    symbol=symbol,
                    message=f"ドローダウン超過: {symbol}",
                    data={'max_drawdown': max_drawdown},
                    action_required=True,
                    auto_execute=True
                )
                self._handle_alert(alert)
            
            # ボラティリティチェック
            volatility = risk_metrics.get('volatility', 0)
            if volatility > 0.30:  # 30%の閾値
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.VOLATILITY_SPIKE,
                    level=AlertLevel.WARNING,
                    symbol=symbol,
                    message=f"ボラティリティ急上昇: {symbol}",
                    data={'volatility': volatility},
                    action_required=False,
                    auto_execute=False
                )
                self._handle_alert(alert)
                
        except Exception as e:
            self.logger.error(f"リスクメトリクスチェックエラー: {e}")
    
    def _check_portfolio_var(self):
        """ポートフォリオVaRチェック"""
        try:
            # ポートフォリオ全体のVaR計算
            total_var = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in self.risk_metrics:
                    var_95 = self.risk_metrics[symbol].get('var_95', 0)
                    position_value = position.get('value', 0)
                    total_var += var_95 * position_value
            
            # 閾値チェック
            if total_var > 0.05:  # 5%の閾値
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.VAR_BREACH,
                    level=AlertLevel.CRITICAL,
                    symbol='PORTFOLIO',
                    message=f"ポートフォリオVaR超過",
                    data={'total_var': total_var},
                    action_required=True,
                    auto_execute=True
                )
                self._handle_alert(alert)
                
        except Exception as e:
            self.logger.error(f"ポートフォリオVaRチェックエラー: {e}")
    
    def _check_portfolio_drawdown(self):
        """ポートフォリオドローダウンチェック"""
        try:
            # ポートフォリオ全体のドローダウン計算
            total_drawdown = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in self.risk_metrics:
                    max_drawdown = self.risk_metrics[symbol].get('max_drawdown', 0)
                    position_value = position.get('value', 0)
                    total_drawdown += max_drawdown * position_value
            
            # 閾値チェック
            if total_drawdown > 0.15:  # 15%の閾値
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.DRAWDOWN_BREACH,
                    level=AlertLevel.CRITICAL,
                    symbol='PORTFOLIO',
                    message=f"ポートフォリオドローダウン超過",
                    data={'total_drawdown': total_drawdown},
                    action_required=True,
                    auto_execute=True
                )
                self._handle_alert(alert)
                
        except Exception as e:
            self.logger.error(f"ポートフォリオドローダウンチェックエラー: {e}")
    
    def _check_correlation_risks(self):
        """相関リスクチェック"""
        try:
            # 相関行列計算
            symbols = list(self.positions.keys())
            if len(symbols) < 2:
                return
            
            # 簡易的な相関チェック
            high_correlation_pairs = []
            
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols[i+1:], i+1):
                    if symbol1 in self.market_data and symbol2 in self.market_data:
                        correlation = self._calculate_correlation(
                            self.market_data[symbol1], self.market_data[symbol2]
                        )
                        
                        if correlation > 0.8:  # 80%の閾値
                            high_correlation_pairs.append((symbol1, symbol2, correlation))
            
            if high_correlation_pairs:
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    event_type=RiskEventType.CORRELATION_BREACH,
                    level=AlertLevel.WARNING,
                    symbol='PORTFOLIO',
                    message=f"高相関ペア検出: {len(high_correlation_pairs)}組",
                    data={'high_correlation_pairs': high_correlation_pairs},
                    action_required=False,
                    auto_execute=False
                )
                self._handle_alert(alert)
                
        except Exception as e:
            self.logger.error(f"相関リスクチェックエラー: {e}")
    
    def _calculate_correlation(self, data1: pd.DataFrame, data2: pd.DataFrame) -> float:
        """相関計算"""
        try:
            if 'Close' not in data1.columns or 'Close' not in data2.columns:
                return 0.0
            
            returns1 = data1['Close'].pct_change().dropna()
            returns2 = data2['Close'].pct_change().dropna()
            
            if returns1.empty or returns2.empty:
                return 0.0
            
            # 共通の期間でデータを合わせる
            common_index = returns1.index.intersection(returns2.index)
            if len(common_index) < 2:
                return 0.0
            
            returns1_aligned = returns1.loc[common_index]
            returns2_aligned = returns2.loc[common_index]
            
            correlation = returns1_aligned.corr(returns2_aligned)
            return correlation if not np.isnan(correlation) else 0.0
            
        except:
            return 0.0
    
    def _handle_alert(self, alert: RiskAlert):
        """アラート処理"""
        try:
            # アラート履歴に追加
            self.alert_history.append(alert)
            if len(self.alert_history) > 1000:
                self.alert_history.pop(0)
            
            # 統計更新
            self.monitoring_stats['total_alerts'] += 1
            if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                self.monitoring_stats['critical_alerts'] += 1
            
            # ログ出力
            self.logger.info(f"リスクアラート: {alert.message}")
            
            # コールバック実行
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"アラートコールバックエラー: {e}")
            
            # 自動実行
            if alert.auto_execute and self.monitoring_config.auto_execute_enabled:
                self._execute_auto_action(alert)
                
        except Exception as e:
            self.logger.error(f"アラート処理エラー: {e}")
    
    def _execute_auto_action(self, alert: RiskAlert):
        """自動アクション実行"""
        try:
            action_data = {
                'alert': alert,
                'timestamp': datetime.now()
            }
            
            # アクションコールバック実行
            for callback in self.action_callbacks:
                try:
                    success = callback(alert.symbol, action_data)
                    if success:
                        self.monitoring_stats['auto_actions'] += 1
                        self.logger.info(f"自動アクション実行成功: {alert.symbol}")
                        break
                except Exception as e:
                    self.logger.error(f"自動アクションコールバックエラー: {e}")
                    
        except Exception as e:
            self.logger.error(f"自動アクション実行エラー: {e}")
    
    def get_position_risk_summary(self, symbol: str) -> Dict[str, Any]:
        """ポジションリスクサマリー取得"""
        try:
            if symbol not in self.positions:
                return {}
            
            position = self.positions[symbol]
            risk_metrics = self.risk_metrics.get(symbol, {})
            
            return {
                'symbol': symbol,
                'position_data': position,
                'risk_metrics': risk_metrics,
                'alerts': [a for a in self.alert_history if a.symbol == symbol],
                'last_update': position.get('last_update')
            }
            
        except Exception as e:
            self.logger.error(f"ポジションリスクサマリー取得エラー: {e}")
            return {}
    
    def get_portfolio_risk_summary(self) -> Dict[str, Any]:
        """ポートフォリオリスクサマリー取得"""
        try:
            return {
                'total_positions': len(self.positions),
                'total_value': sum(pos.get('value', 0) for pos in self.positions.values()),
                'risk_metrics': self.risk_metrics,
                'recent_alerts': self.alert_history[-10:],
                'monitoring_stats': self.monitoring_stats
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスクサマリー取得エラー: {e}")
            return {}
    
    def clear_alert_history(self) -> bool:
        """アラート履歴クリア"""
        try:
            self.alert_history.clear()
            self.monitoring_stats['total_alerts'] = 0
            self.monitoring_stats['critical_alerts'] = 0
            self.logger.info("アラート履歴をクリアしました")
            return True
            
        except Exception as e:
            self.logger.error(f"アラート履歴クリアエラー: {e}")
            return False
    
    def reset_monitoring_stats(self) -> bool:
        """監視統計リセット"""
        try:
            self.monitoring_stats = {
                'total_alerts': 0,
                'critical_alerts': 0,
                'auto_actions': 0,
                'last_update': None
            }
            self.logger.info("監視統計をリセットしました")
            return True
            
        except Exception as e:
            self.logger.error(f"監視統計リセットエラー: {e}")
            return False
