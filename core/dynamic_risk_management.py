#!/usr/bin/env python3
"""
動的損切り・利確機能システム

目的: 市場データ・ボラティリティに基づく動的調整
仕様: リアルタイムリスク監視と自動損切り
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class RiskLevel(Enum):
    """リスクレベル"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PositionStatus(Enum):
    """ポジション状態"""
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"
    STOPPED = "stopped"


@dataclass
class Position:
    """ポジション情報"""
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    position_type: str  # LONG, SHORT
    entry_time: datetime
    stop_loss: float
    take_profit: float
    trailing_stop: float
    max_loss: float
    status: PositionStatus
    unrealized_pnl: float
    realized_pnl: float = 0.0


@dataclass
class RiskMetrics:
    """リスクメトリクス"""
    var_95: float
    var_99: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    volatility: float
    beta: float
    correlation: float
    risk_score: float


@dataclass
class DynamicStopLoss:
    """動的損切り設定"""
    base_stop_loss: float
    current_stop_loss: float
    trailing_distance: float
    volatility_adjustment: float
    market_regime_adjustment: float
    time_decay_adjustment: float
    final_stop_loss: float


@dataclass
class DynamicTakeProfit:
    """動的利確設定"""
    base_take_profit: float
    current_take_profit: float
    volatility_adjustment: float
    market_regime_adjustment: float
    momentum_adjustment: float
    final_take_profit: float


class DynamicRiskManager:
    """動的リスク管理システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.positions: Dict[str, Position] = {}
        self.risk_metrics_history = []
        self.market_regime = "normal"
        self.volatility_regime = "normal"
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "stop_loss": {
                "base_percentage": 0.05,  # 5%の基本損切り
                "min_percentage": 0.02,   # 2%の最小損切り
                "max_percentage": 0.15,   # 15%の最大損切り
                "trailing_enabled": True,
                "trailing_percentage": 0.02,  # 2%のトレーリング
                "volatility_multiplier": 1.5,
                "time_decay_factor": 0.95
            },
            "take_profit": {
                "base_percentage": 0.10,  # 10%の基本利確
                "min_percentage": 0.05,   # 5%の最小利確
                "max_percentage": 0.30,   # 30%の最大利確
                "volatility_multiplier": 1.2,
                "momentum_multiplier": 1.3
            },
            "risk_management": {
                "max_position_size": 0.1,  # 10%の最大ポジション
                "max_portfolio_risk": 0.05,  # 5%の最大ポートフォリオリスク
                "correlation_limit": 0.7,   # 70%の相関制限
                "var_limit": 0.02,          # 2%のVaR制限
                "drawdown_limit": 0.10      # 10%のドローダウン制限
            },
            "market_regime": {
                "bull_threshold": 0.05,
                "bear_threshold": -0.05,
                "high_vol_threshold": 0.25,
                "low_vol_threshold": 0.10
            }
        }
    
    def calculate_dynamic_stop_loss(
        self,
        position: Position,
        market_data: pd.DataFrame,
        volatility_data: pd.DataFrame,
        risk_metrics: RiskMetrics
    ) -> DynamicStopLoss:
        """動的損切り計算"""
        try:
            # 基本損切り
            base_stop_loss = self._calculate_base_stop_loss(position)
            
            # ボラティリティ調整
            volatility_adjustment = self._calculate_volatility_adjustment(
                volatility_data, position
            )
            
            # 市場レジーム調整
            market_regime_adjustment = self._calculate_market_regime_adjustment(
                market_data, position
            )
            
            # 時間減衰調整
            time_decay_adjustment = self._calculate_time_decay_adjustment(position)
            
            # トレーリングストップ計算
            trailing_distance = self._calculate_trailing_distance(
                position, volatility_data
            )
            
            # 最終損切り価格計算
            current_stop_loss = self._calculate_current_stop_loss(
                position, trailing_distance
            )
            
            # 動的調整適用
            final_stop_loss = self._apply_dynamic_adjustments(
                current_stop_loss,
                volatility_adjustment,
                market_regime_adjustment,
                time_decay_adjustment
            )
            
            return DynamicStopLoss(
                base_stop_loss=base_stop_loss,
                current_stop_loss=current_stop_loss,
                trailing_distance=trailing_distance,
                volatility_adjustment=volatility_adjustment,
                market_regime_adjustment=market_regime_adjustment,
                time_decay_adjustment=time_decay_adjustment,
                final_stop_loss=final_stop_loss
            )
            
        except Exception as e:
            self.logger.error(f"動的損切り計算エラー: {e}")
            return self._get_default_stop_loss(position)
    
    def calculate_dynamic_take_profit(
        self,
        position: Position,
        market_data: pd.DataFrame,
        volatility_data: pd.DataFrame,
        momentum_data: pd.DataFrame
    ) -> DynamicTakeProfit:
        """動的利確計算"""
        try:
            # 基本利確
            base_take_profit = self._calculate_base_take_profit(position)
            
            # ボラティリティ調整
            volatility_adjustment = self._calculate_volatility_adjustment_tp(
                volatility_data, position
            )
            
            # 市場レジーム調整
            market_regime_adjustment = self._calculate_market_regime_adjustment_tp(
                market_data, position
            )
            
            # モメンタム調整
            momentum_adjustment = self._calculate_momentum_adjustment(
                momentum_data, position
            )
            
            # 現在の利確価格
            current_take_profit = self._calculate_current_take_profit(position)
            
            # 動的調整適用
            final_take_profit = self._apply_dynamic_adjustments_tp(
                current_take_profit,
                volatility_adjustment,
                market_regime_adjustment,
                momentum_adjustment
            )
            
            return DynamicTakeProfit(
                base_take_profit=base_take_profit,
                current_take_profit=current_take_profit,
                volatility_adjustment=volatility_adjustment,
                market_regime_adjustment=market_regime_adjustment,
                momentum_adjustment=momentum_adjustment,
                final_take_profit=final_take_profit
            )
            
        except Exception as e:
            self.logger.error(f"動的利確計算エラー: {e}")
            return self._get_default_take_profit(position)
    
    def monitor_positions(
        self,
        current_prices: Dict[str, float],
        market_data: Dict[str, pd.DataFrame],
        risk_metrics: Dict[str, RiskMetrics]
    ) -> List[Dict[str, Any]]:
        """ポジション監視"""
        try:
            alerts = []
            
            for symbol, position in self.positions.items():
                if position.status != PositionStatus.OPEN:
                    continue
                
                current_price = current_prices.get(symbol, position.current_price)
                
                # 価格更新
                position.current_price = current_price
                position.unrealized_pnl = self._calculate_unrealized_pnl(position)
                
                # 損切りチェック
                stop_loss_alert = self._check_stop_loss(position)
                if stop_loss_alert:
                    alerts.append(stop_loss_alert)
                
                # 利確チェック
                take_profit_alert = self._check_take_profit(position)
                if take_profit_alert:
                    alerts.append(take_profit_alert)
                
                # リスク制限チェック
                risk_alerts = self._check_risk_limits(position, risk_metrics.get(symbol))
                alerts.extend(risk_alerts)
                
                # 動的調整
                self._update_dynamic_levels(position, market_data.get(symbol))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"ポジション監視エラー: {e}")
            return []
    
    def execute_stop_loss(self, symbol: str, reason: str = "損切り") -> bool:
        """損切り実行"""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            if position.status != PositionStatus.OPEN:
                return False
            
            # ポジションクローズ
            position.status = PositionStatus.STOPPED
            position.realized_pnl = position.unrealized_pnl
            
            self.logger.info(f"損切り実行: {symbol}, 理由: {reason}, 損失: {position.realized_pnl:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"損切り実行エラー: {e}")
            return False
    
    def execute_take_profit(self, symbol: str, reason: str = "利確") -> bool:
        """利確実行"""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            if position.status != PositionStatus.OPEN:
                return False
            
            # ポジションクローズ
            position.status = PositionStatus.CLOSED
            position.realized_pnl = position.unrealized_pnl
            
            self.logger.info(f"利確実行: {symbol}, 理由: {reason}, 利益: {position.realized_pnl:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"利確実行エラー: {e}")
            return False
    
    def calculate_risk_metrics(
        self,
        portfolio_data: pd.DataFrame,
        market_data: pd.DataFrame,
        risk_free_rate: float = 0.02
    ) -> RiskMetrics:
        """リスクメトリクス計算"""
        try:
            if portfolio_data.empty:
                return self._get_default_risk_metrics()
            
            # リターン計算
            returns = portfolio_data['value'].pct_change().dropna()
            
            if returns.empty:
                return self._get_default_risk_metrics()
            
            # VaR計算
            var_95 = self._calculate_var(returns, 0.95)
            var_99 = self._calculate_var(returns, 0.99)
            
            # 最大ドローダウン計算
            max_drawdown = self._calculate_max_drawdown(portfolio_data['value'])
            
            # シャープレシオ計算
            sharpe_ratio = self._calculate_sharpe_ratio(returns, risk_free_rate)
            
            # ソルティノレシオ計算
            sortino_ratio = self._calculate_sortino_ratio(returns, risk_free_rate)
            
            # カルマーレシオ計算
            calmar_ratio = self._calculate_calmar_ratio(returns, max_drawdown)
            
            # ボラティリティ計算
            volatility = returns.std() * np.sqrt(252)
            
            # ベータ計算
            beta = self._calculate_beta(returns, market_data)
            
            # 相関計算
            correlation = self._calculate_correlation(returns, market_data)
            
            # リスクスコア計算
            risk_score = self._calculate_risk_score(
                var_95, max_drawdown, volatility, sharpe_ratio
            )
            
            metrics = RiskMetrics(
                var_95=var_95,
                var_99=var_99,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                volatility=volatility,
                beta=beta,
                correlation=correlation,
                risk_score=risk_score
            )
            
            # 履歴に追加
            self.risk_metrics_history.append(metrics)
            if len(self.risk_metrics_history) > 1000:
                self.risk_metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"リスクメトリクス計算エラー: {e}")
            return self._get_default_risk_metrics()
    
    def get_portfolio_risk_summary(self) -> Dict[str, Any]:
        """ポートフォリオリスクサマリー取得"""
        try:
            if not self.risk_metrics_history:
                return {}
            
            # 最新のリスクメトリクス
            latest_metrics = self.risk_metrics_history[-1]
            
            # 履歴統計
            var_95_history = [m.var_95 for m in self.risk_metrics_history]
            sharpe_history = [m.sharpe_ratio for m in self.risk_metrics_history]
            volatility_history = [m.volatility for m in self.risk_metrics_history]
            
            return {
                "current_risk_score": latest_metrics.risk_score,
                "current_var_95": latest_metrics.var_95,
                "current_sharpe_ratio": latest_metrics.sharpe_ratio,
                "current_volatility": latest_metrics.volatility,
                "max_drawdown": latest_metrics.max_drawdown,
                "average_var_95": np.mean(var_95_history),
                "average_sharpe_ratio": np.mean(sharpe_history),
                "average_volatility": np.mean(volatility_history),
                "risk_trend": self._calculate_risk_trend(),
                "portfolio_health": self._assess_portfolio_health(latest_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスクサマリー取得エラー: {e}")
            return {}
    
    # ヘルパーメソッド群
    def _calculate_base_stop_loss(self, position: Position) -> float:
        """基本損切り計算"""
        config = self.config["stop_loss"]
        base_percentage = config["base_percentage"]
        
        if position.position_type == "LONG":
            return position.entry_price * (1 - base_percentage)
        else:
            return position.entry_price * (1 + base_percentage)
    
    def _calculate_volatility_adjustment(
        self, volatility_data: pd.DataFrame, position: Position
    ) -> float:
        """ボラティリティ調整計算"""
        try:
            if volatility_data.empty:
                return 1.0
            
            # 現在のボラティリティ
            current_vol = volatility_data['volatility'].iloc[-1]
            
            # 平均ボラティリティ
            avg_vol = volatility_data['volatility'].mean()
            
            # ボラティリティ比率
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
            
            # 調整係数
            config = self.config["stop_loss"]
            multiplier = config["volatility_multiplier"]
            
            adjustment = 1 + (vol_ratio - 1) * multiplier
            
            return max(0.5, min(2.0, adjustment))
            
        except Exception as e:
            self.logger.error(f"ボラティリティ調整計算エラー: {e}")
            return 1.0
    
    def _calculate_market_regime_adjustment(
        self, market_data: pd.DataFrame, position: Position
    ) -> float:
        """市場レジーム調整計算"""
        try:
            if market_data.empty:
                return 1.0
            
            # 市場トレンド計算
            prices = market_data['Close']
            short_ma = prices.rolling(window=20).mean().iloc[-1]
            long_ma = prices.rolling(window=50).mean().iloc[-1]
            
            # トレンド強度
            trend_strength = (short_ma - long_ma) / long_ma if long_ma > 0 else 0
            
            # レジーム判定
            if trend_strength > 0.05:
                regime = "bull"
            elif trend_strength < -0.05:
                regime = "bear"
            else:
                regime = "normal"
            
            # 調整係数
            adjustments = {
                "bull": 1.1 if position.position_type == "LONG" else 0.9,
                "bear": 0.9 if position.position_type == "LONG" else 1.1,
                "normal": 1.0
            }
            
            return adjustments.get(regime, 1.0)
            
        except Exception as e:
            self.logger.error(f"市場レジーム調整計算エラー: {e}")
            return 1.0
    
    def _calculate_time_decay_adjustment(self, position: Position) -> float:
        """時間減衰調整計算"""
        try:
            # ポジション保有期間
            holding_period = (datetime.now() - position.entry_time).days
            
            # 時間減衰係数
            config = self.config["stop_loss"]
            decay_factor = config["time_decay_factor"]
            
            # 調整係数（時間が経つほど損切りを厳しく）
            adjustment = decay_factor ** (holding_period / 30)  # 30日で減衰
            
            return max(0.8, min(1.2, adjustment))
            
        except Exception as e:
            self.logger.error(f"時間減衰調整計算エラー: {e}")
            return 1.0
    
    def _calculate_trailing_distance(
        self, position: Position, volatility_data: pd.DataFrame
    ) -> float:
        """トレーリング距離計算"""
        try:
            config = self.config["stop_loss"]
            base_trailing = config["trailing_percentage"]
            
            if volatility_data.empty:
                return base_trailing
            
            # ボラティリティに基づく調整
            current_vol = volatility_data['volatility'].iloc[-1]
            avg_vol = volatility_data['volatility'].mean()
            
            vol_adjustment = current_vol / avg_vol if avg_vol > 0 else 1.0
            
            trailing_distance = base_trailing * vol_adjustment
            
            return max(0.01, min(0.05, trailing_distance))
            
        except Exception as e:
            self.logger.error(f"トレーリング距離計算エラー: {e}")
            return 0.02
    
    def _calculate_current_stop_loss(
        self, position: Position, trailing_distance: float
    ) -> float:
        """現在の損切り価格計算"""
        try:
            if position.position_type == "LONG":
                # ロングポジションの場合、最高値からトレーリング
                trailing_stop = position.current_price * (1 - trailing_distance)
                return max(position.stop_loss, trailing_stop)
            else:
                # ショートポジションの場合、最安値からトレーリング
                trailing_stop = position.current_price * (1 + trailing_distance)
                return min(position.stop_loss, trailing_stop)
                
        except Exception as e:
            self.logger.error(f"現在損切り価格計算エラー: {e}")
            return position.stop_loss
    
    def _apply_dynamic_adjustments(
        self,
        current_stop_loss: float,
        volatility_adjustment: float,
        market_regime_adjustment: float,
        time_decay_adjustment: float
    ) -> float:
        """動的調整適用"""
        try:
            # 重み付き調整
            weights = [0.4, 0.3, 0.3]  # ボラティリティ、レジーム、時間減衰
            adjustments = [volatility_adjustment, market_regime_adjustment, time_decay_adjustment]
            
            combined_adjustment = sum(w * a for w, a in zip(weights, adjustments))
            
            # 最終損切り価格
            final_stop_loss = current_stop_loss * combined_adjustment
            
            # 制限チェック
            config = self.config["stop_loss"]
            min_pct = config["min_percentage"]
            max_pct = config["max_percentage"]
            
            # 最小・最大制限適用
            if final_stop_loss < current_stop_loss * (1 - max_pct):
                final_stop_loss = current_stop_loss * (1 - max_pct)
            elif final_stop_loss > current_stop_loss * (1 - min_pct):
                final_stop_loss = current_stop_loss * (1 - min_pct)
            
            return final_stop_loss
            
        except Exception as e:
            self.logger.error(f"動的調整適用エラー: {e}")
            return current_stop_loss
    
    def _calculate_base_take_profit(self, position: Position) -> float:
        """基本利確計算"""
        config = self.config["take_profit"]
        base_percentage = config["base_percentage"]
        
        if position.position_type == "LONG":
            return position.entry_price * (1 + base_percentage)
        else:
            return position.entry_price * (1 - base_percentage)
    
    def _calculate_volatility_adjustment_tp(
        self, volatility_data: pd.DataFrame, position: Position
    ) -> float:
        """利確用ボラティリティ調整計算"""
        try:
            if volatility_data.empty:
                return 1.0
            
            current_vol = volatility_data['volatility'].iloc[-1]
            avg_vol = volatility_data['volatility'].mean()
            
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
            
            config = self.config["take_profit"]
            multiplier = config["volatility_multiplier"]
            
            adjustment = 1 + (vol_ratio - 1) * multiplier
            
            return max(0.8, min(1.5, adjustment))
            
        except Exception as e:
            self.logger.error(f"利確用ボラティリティ調整計算エラー: {e}")
            return 1.0
    
    def _calculate_market_regime_adjustment_tp(
        self, market_data: pd.DataFrame, position: Position
    ) -> float:
        """利確用市場レジーム調整計算"""
        try:
            if market_data.empty:
                return 1.0
            
            prices = market_data['Close']
            short_ma = prices.rolling(window=20).mean().iloc[-1]
            long_ma = prices.rolling(window=50).mean().iloc[-1]
            
            trend_strength = (short_ma - long_ma) / long_ma if long_ma > 0 else 0
            
            if trend_strength > 0.05:
                regime = "bull"
            elif trend_strength < -0.05:
                regime = "bear"
            else:
                regime = "normal"
            
            adjustments = {
                "bull": 1.2 if position.position_type == "LONG" else 0.8,
                "bear": 0.8 if position.position_type == "LONG" else 1.2,
                "normal": 1.0
            }
            
            return adjustments.get(regime, 1.0)
            
        except Exception as e:
            self.logger.error(f"利確用市場レジーム調整計算エラー: {e}")
            return 1.0
    
    def _calculate_momentum_adjustment(
        self, momentum_data: pd.DataFrame, position: Position
    ) -> float:
        """モメンタム調整計算"""
        try:
            if momentum_data.empty:
                return 1.0
            
            # モメンタム指標
            momentum = momentum_data['momentum'].iloc[-1]
            
            config = self.config["take_profit"]
            multiplier = config["momentum_multiplier"]
            
            # モメンタムに応じた調整
            if momentum > 0:
                adjustment = 1 + momentum * multiplier
            else:
                adjustment = 1 - abs(momentum) * multiplier * 0.5
            
            return max(0.7, min(1.3, adjustment))
            
        except Exception as e:
            self.logger.error(f"モメンタム調整計算エラー: {e}")
            return 1.0
    
    def _calculate_current_take_profit(self, position: Position) -> float:
        """現在の利確価格計算"""
        return position.take_profit
    
    def _apply_dynamic_adjustments_tp(
        self,
        current_take_profit: float,
        volatility_adjustment: float,
        market_regime_adjustment: float,
        momentum_adjustment: float
    ) -> float:
        """利確用動的調整適用"""
        try:
            weights = [0.3, 0.3, 0.4]  # ボラティリティ、レジーム、モメンタム
            adjustments = [volatility_adjustment, market_regime_adjustment, momentum_adjustment]
            
            combined_adjustment = sum(w * a for w, a in zip(weights, adjustments))
            
            final_take_profit = current_take_profit * combined_adjustment
            
            # 制限チェック
            config = self.config["take_profit"]
            min_pct = config["min_percentage"]
            max_pct = config["max_percentage"]
            
            if final_take_profit < current_take_profit * (1 + min_pct):
                final_take_profit = current_take_profit * (1 + min_pct)
            elif final_take_profit > current_take_profit * (1 + max_pct):
                final_take_profit = current_take_profit * (1 + max_pct)
            
            return final_take_profit
            
        except Exception as e:
            self.logger.error(f"利確用動的調整適用エラー: {e}")
            return current_take_profit
    
    def _calculate_unrealized_pnl(self, position: Position) -> float:
        """未実現損益計算"""
        try:
            if position.position_type == "LONG":
                return (position.current_price - position.entry_price) * position.quantity
            else:
                return (position.entry_price - position.current_price) * position.quantity
        except:
            return 0.0
    
    def _check_stop_loss(self, position: Position) -> Optional[Dict[str, Any]]:
        """損切りチェック"""
        try:
            if position.position_type == "LONG":
                if position.current_price <= position.stop_loss:
                    return {
                        "type": "stop_loss",
                        "symbol": position.symbol,
                        "current_price": position.current_price,
                        "stop_loss": position.stop_loss,
                        "unrealized_pnl": position.unrealized_pnl,
                        "message": f"損切りライン到達: {position.symbol}"
                    }
            else:
                if position.current_price >= position.stop_loss:
                    return {
                        "type": "stop_loss",
                        "symbol": position.symbol,
                        "current_price": position.current_price,
                        "stop_loss": position.stop_loss,
                        "unrealized_pnl": position.unrealized_pnl,
                        "message": f"損切りライン到達: {position.symbol}"
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"損切りチェックエラー: {e}")
            return None
    
    def _check_take_profit(self, position: Position) -> Optional[Dict[str, Any]]:
        """利確チェック"""
        try:
            if position.position_type == "LONG":
                if position.current_price >= position.take_profit:
                    return {
                        "type": "take_profit",
                        "symbol": position.symbol,
                        "current_price": position.current_price,
                        "take_profit": position.take_profit,
                        "unrealized_pnl": position.unrealized_pnl,
                        "message": f"利確ライン到達: {position.symbol}"
                    }
            else:
                if position.current_price <= position.take_profit:
                    return {
                        "type": "take_profit",
                        "symbol": position.symbol,
                        "current_price": position.current_price,
                        "take_profit": position.take_profit,
                        "unrealized_pnl": position.unrealized_pnl,
                        "message": f"利確ライン到達: {position.symbol}"
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"利確チェックエラー: {e}")
            return None
    
    def _check_risk_limits(
        self, position: Position, risk_metrics: Optional[RiskMetrics]
    ) -> List[Dict[str, Any]]:
        """リスク制限チェック"""
        alerts = []
        
        try:
            config = self.config["risk_management"]
            
            # VaR制限チェック
            if risk_metrics and risk_metrics.var_95 > config["var_limit"]:
                alerts.append({
                    "type": "risk_limit",
                    "symbol": position.symbol,
                    "metric": "VaR",
                    "value": risk_metrics.var_95,
                    "limit": config["var_limit"],
                    "message": f"VaR制限超過: {position.symbol}"
                })
            
            # ドローダウン制限チェック
            if risk_metrics and risk_metrics.max_drawdown > config["drawdown_limit"]:
                alerts.append({
                    "type": "risk_limit",
                    "symbol": position.symbol,
                    "metric": "Max Drawdown",
                    "value": risk_metrics.max_drawdown,
                    "limit": config["drawdown_limit"],
                    "message": f"ドローダウン制限超過: {position.symbol}"
                })
            
            # ポジションサイズ制限チェック
            if position.quantity > config["max_position_size"]:
                alerts.append({
                    "type": "position_limit",
                    "symbol": position.symbol,
                    "metric": "Position Size",
                    "value": position.quantity,
                    "limit": config["max_position_size"],
                    "message": f"ポジションサイズ制限超過: {position.symbol}"
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"リスク制限チェックエラー: {e}")
            return []
    
    def _update_dynamic_levels(
        self, position: Position, market_data: Optional[pd.DataFrame]
    ):
        """動的レベル更新"""
        try:
            if market_data is None or market_data.empty:
                return
            
            # ボラティリティデータ準備
            volatility_data = pd.DataFrame({
                'volatility': market_data['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
            })
            
            # 動的損切り更新
            dynamic_stop_loss = self.calculate_dynamic_stop_loss(
                position, market_data, volatility_data, RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            )
            
            # 動的利確更新
            momentum_data = pd.DataFrame({
                'momentum': market_data['Close'].pct_change(periods=5)
            })
            
            dynamic_take_profit = self.calculate_dynamic_take_profit(
                position, market_data, volatility_data, momentum_data
            )
            
            # レベル更新
            position.stop_loss = dynamic_stop_loss.final_stop_loss
            position.take_profit = dynamic_take_profit.final_take_profit
            
        except Exception as e:
            self.logger.error(f"動的レベル更新エラー: {e}")
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """VaR計算"""
        try:
            if returns.empty:
                return 0.0
            
            return np.percentile(returns, (1 - confidence_level) * 100)
        except:
            return 0.0
    
    def _calculate_max_drawdown(self, values: pd.Series) -> float:
        """最大ドローダウン計算"""
        try:
            if values.empty:
                return 0.0
            
            peak = values.expanding().max()
            drawdown = (values - peak) / peak
            return abs(drawdown.min())
        except:
            return 0.0
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """シャープレシオ計算"""
        try:
            if returns.empty:
                return 0.0
            
            excess_returns = returns.mean() - risk_free_rate / 252
            return excess_returns / returns.std() * np.sqrt(252) if returns.std() > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """ソルティノレシオ計算"""
        try:
            if returns.empty:
                return 0.0
            
            excess_returns = returns.mean() - risk_free_rate / 252
            downside_returns = returns[returns < 0]
            
            if downside_returns.empty:
                return 0.0
            
            downside_std = downside_returns.std()
            return excess_returns / downside_std * np.sqrt(252) if downside_std > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_calmar_ratio(self, returns: pd.Series, max_drawdown: float) -> float:
        """カルマーレシオ計算"""
        try:
            if returns.empty or max_drawdown == 0:
                return 0.0
            
            annual_return = returns.mean() * 252
            return annual_return / max_drawdown
        except:
            return 0.0
    
    def _calculate_beta(self, returns: pd.Series, market_data: pd.DataFrame) -> float:
        """ベータ計算"""
        try:
            if returns.empty or market_data.empty:
                return 1.0
            
            market_returns = market_data['Close'].pct_change().dropna()
            
            if market_returns.empty:
                return 1.0
            
            # 共通の期間でデータを合わせる
            common_index = returns.index.intersection(market_returns.index)
            if len(common_index) < 2:
                return 1.0
            
            returns_aligned = returns.loc[common_index]
            market_returns_aligned = market_returns.loc[common_index]
            
            covariance = np.cov(returns_aligned, market_returns_aligned)[0, 1]
            market_variance = np.var(market_returns_aligned)
            
            return covariance / market_variance if market_variance > 0 else 1.0
        except:
            return 1.0
    
    def _calculate_correlation(self, returns: pd.Series, market_data: pd.DataFrame) -> float:
        """相関計算"""
        try:
            if returns.empty or market_data.empty:
                return 0.0
            
            market_returns = market_data['Close'].pct_change().dropna()
            
            if market_returns.empty:
                return 0.0
            
            # 共通の期間でデータを合わせる
            common_index = returns.index.intersection(market_returns.index)
            if len(common_index) < 2:
                return 0.0
            
            returns_aligned = returns.loc[common_index]
            market_returns_aligned = market_returns.loc[common_index]
            
            correlation = returns_aligned.corr(market_returns_aligned)
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _calculate_risk_score(
        self, var_95: float, max_drawdown: float, volatility: float, sharpe_ratio: float
    ) -> float:
        """リスクスコア計算"""
        try:
            # 各指標の重み
            weights = [0.3, 0.3, 0.2, 0.2]
            
            # 正規化されたスコア
            var_score = min(1.0, abs(var_95) / 0.1)  # 10%を上限とする
            drawdown_score = min(1.0, max_drawdown / 0.2)  # 20%を上限とする
            volatility_score = min(1.0, volatility / 0.5)  # 50%を上限とする
            sharpe_score = max(0.0, min(1.0, sharpe_ratio / 2.0))  # 2.0を上限とする
            
            scores = [var_score, drawdown_score, volatility_score, sharpe_score]
            
            risk_score = sum(w * s for w, s in zip(weights, scores))
            
            return max(0.0, min(1.0, risk_score))
        except:
            return 0.5
    
    def _calculate_risk_trend(self) -> str:
        """リスクトレンド計算"""
        try:
            if len(self.risk_metrics_history) < 5:
                return "stable"
            
            recent_scores = [m.risk_score for m in self.risk_metrics_history[-5:]]
            older_scores = [m.risk_score for m in self.risk_metrics_history[-10:-5]]
            
            if not older_scores:
                return "stable"
            
            recent_avg = np.mean(recent_scores)
            older_avg = np.mean(older_scores)
            
            if recent_avg > older_avg * 1.1:
                return "increasing"
            elif recent_avg < older_avg * 0.9:
                return "decreasing"
            else:
                return "stable"
        except:
            return "stable"
    
    def _assess_portfolio_health(self, metrics: RiskMetrics) -> str:
        """ポートフォリオ健全性評価"""
        try:
            if metrics.risk_score < 0.3:
                return "excellent"
            elif metrics.risk_score < 0.5:
                return "good"
            elif metrics.risk_score < 0.7:
                return "fair"
            elif metrics.risk_score < 0.9:
                return "poor"
            else:
                return "critical"
        except:
            return "unknown"
    
    def _get_default_stop_loss(self, position: Position) -> DynamicStopLoss:
        """デフォルト損切り設定"""
        return DynamicStopLoss(
            base_stop_loss=position.stop_loss,
            current_stop_loss=position.stop_loss,
            trailing_distance=0.02,
            volatility_adjustment=1.0,
            market_regime_adjustment=1.0,
            time_decay_adjustment=1.0,
            final_stop_loss=position.stop_loss
        )
    
    def _get_default_take_profit(self, position: Position) -> DynamicTakeProfit:
        """デフォルト利確設定"""
        return DynamicTakeProfit(
            base_take_profit=position.take_profit,
            current_take_profit=position.take_profit,
            volatility_adjustment=1.0,
            market_regime_adjustment=1.0,
            momentum_adjustment=1.0,
            final_take_profit=position.take_profit
        )
    
    def _get_default_risk_metrics(self) -> RiskMetrics:
        """デフォルトリスクメトリクス"""
        return RiskMetrics(
            var_95=0.0,
            var_99=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            volatility=0.0,
            beta=1.0,
            correlation=0.0,
            risk_score=0.5
        )
