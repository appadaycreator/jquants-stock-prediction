#!/usr/bin/env python3
"""
動的リスク管理システム
記事の手法を超える高度なリスク管理機能を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class RiskLevel(Enum):
    """リスクレベル"""
    VERY_LOW = "very_low"    # 1%以下
    LOW = "low"              # 1-3%
    MEDIUM = "medium"        # 3-5%
    HIGH = "high"           # 5-10%
    VERY_HIGH = "very_high"  # 10%以上


@dataclass
class RiskMetrics:
    """リスクメトリクス"""
    var_95: float  # 95% VaR
    var_99: float  # 99% VaR
    max_drawdown: float  # 最大ドローダウン
    sharpe_ratio: float  # シャープレシオ
    sortino_ratio: float  # ソルティノレシオ
    calmar_ratio: float  # カルマーレシオ
    volatility: float  # ボラティリティ
    beta: float  # ベータ
    correlation: float  # 市場相関
    risk_level: RiskLevel
    position_size: float  # 推奨ポジションサイズ
    stop_loss: float  # 損切り価格
    take_profit: float  # 利確価格


@dataclass
class DynamicRiskAdjustment:
    """動的リスク調整"""
    market_volatility_adjustment: float
    sector_risk_adjustment: float
    liquidity_adjustment: float
    time_decay_adjustment: float
    confidence_adjustment: float
    final_adjustment: float


class DynamicRiskManager:
    """動的リスク管理システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.risk_history = []
        self.market_regime = "normal"
        self.volatility_regime = "normal"
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "risk_limits": {
                "max_position_size": 0.1,  # 最大ポジションサイズ（10%）
                "max_portfolio_risk": 0.05,  # 最大ポートフォリオリスク（5%）
                "max_drawdown_limit": 0.15,  # 最大ドローダウン制限（15%）
                "var_limit_95": 0.02,  # 95% VaR制限（2%）
                "var_limit_99": 0.05   # 99% VaR制限（5%）
            },
            "dynamic_adjustments": {
                "volatility_sensitivity": 0.5,  # ボラティリティ感度
                "market_regime_weight": 0.3,   # 市場レジーム重み
                "confidence_weight": 0.4,      # 信頼度重み
                "liquidity_weight": 0.2,       # 流動性重み
                "time_decay_factor": 0.95      # 時間減衰係数
            },
            "stop_loss": {
                "base_stop_loss": 0.05,        # 基本損切り（5%）
                "volatility_multiplier": 2.0,  # ボラティリティ倍率
                "confidence_multiplier": 1.5,  # 信頼度倍率
                "min_stop_loss": 0.02,         # 最小損切り（2%）
                "max_stop_loss": 0.15          # 最大損切り（15%）
            },
            "take_profit": {
                "base_take_profit": 0.10,       # 基本利確（10%）
                "risk_reward_ratio": 2.0,      # リスクリワード比
                "volatility_adjustment": True, # ボラティリティ調整
                "confidence_adjustment": True  # 信頼度調整
            }
        }
    
    def calculate_risk_metrics(
        self,
        stock_data: pd.DataFrame,
        market_data: pd.DataFrame,
        current_price: float,
        position_size: float = 0.1
    ) -> RiskMetrics:
        """リスクメトリクス計算"""
        try:
            # VaR計算
            var_95, var_99 = self._calculate_var(stock_data)
            
            # 最大ドローダウン計算
            max_drawdown = self._calculate_max_drawdown(stock_data)
            
            # シャープレシオ計算
            sharpe_ratio = self._calculate_sharpe_ratio(stock_data, market_data)
            
            # ソルティノレシオ計算
            sortino_ratio = self._calculate_sortino_ratio(stock_data)
            
            # カルマーレシオ計算
            calmar_ratio = self._calculate_calmar_ratio(stock_data)
            
            # ボラティリティ計算
            volatility = self._calculate_volatility(stock_data)
            
            # ベータ計算
            beta = self._calculate_beta(stock_data, market_data)
            
            # 相関計算
            correlation = self._calculate_correlation(stock_data, market_data)
            
            # リスクレベル決定
            risk_level = self._determine_risk_level(
                var_95, max_drawdown, volatility
            )
            
            # 動的ポジションサイズ計算
            adjusted_position_size = self._calculate_dynamic_position_size(
                position_size, risk_level, volatility, beta
            )
            
            # 動的損切り・利確計算
            stop_loss, take_profit = self._calculate_dynamic_stop_take(
                current_price, volatility, risk_level
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
                risk_level=risk_level,
                position_size=adjusted_position_size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            # 履歴に追加
            self.risk_history.append(metrics)
            if len(self.risk_history) > 1000:
                self.risk_history.pop(0)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"リスクメトリクス計算エラー: {e}")
            return self._get_default_risk_metrics()
    
    def calculate_dynamic_risk_adjustment(
        self,
        stock_data: pd.DataFrame,
        market_data: pd.DataFrame,
        confidence: float,
        sector_data: Optional[pd.DataFrame] = None
    ) -> DynamicRiskAdjustment:
        """動的リスク調整計算"""
        try:
            # 市場ボラティリティ調整
            market_volatility = self._calculate_market_volatility(market_data)
            volatility_adjustment = self._calculate_volatility_adjustment(
                market_volatility
            )
            
            # セクターリスク調整
            sector_risk_adjustment = self._calculate_sector_risk_adjustment(
                sector_data
            )
            
            # 流動性調整
            liquidity_adjustment = self._calculate_liquidity_adjustment(
                stock_data
            )
            
            # 時間減衰調整
            time_decay_adjustment = self._calculate_time_decay_adjustment()
            
            # 信頼度調整
            confidence_adjustment = self._calculate_confidence_adjustment(
                confidence
            )
            
            # 最終調整係数
            final_adjustment = (
                volatility_adjustment * self.config["dynamic_adjustments"]["volatility_sensitivity"] +
                sector_risk_adjustment * self.config["dynamic_adjustments"]["market_regime_weight"] +
                confidence_adjustment * self.config["dynamic_adjustments"]["confidence_weight"] +
                liquidity_adjustment * self.config["dynamic_adjustments"]["liquidity_weight"]
            ) * time_decay_adjustment
            
            return DynamicRiskAdjustment(
                market_volatility_adjustment=volatility_adjustment,
                sector_risk_adjustment=sector_risk_adjustment,
                liquidity_adjustment=liquidity_adjustment,
                time_decay_adjustment=time_decay_adjustment,
                confidence_adjustment=confidence_adjustment,
                final_adjustment=final_adjustment
            )
            
        except Exception as e:
            self.logger.error(f"動的リスク調整計算エラー: {e}")
            return DynamicRiskAdjustment(
                market_volatility_adjustment=1.0,
                sector_risk_adjustment=1.0,
                liquidity_adjustment=1.0,
                time_decay_adjustment=1.0,
                confidence_adjustment=1.0,
                final_adjustment=1.0
            )
    
    def should_adjust_position(
        self,
        current_metrics: RiskMetrics,
        previous_metrics: Optional[RiskMetrics] = None,
        market_conditions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """ポジション調整判定"""
        try:
            adjustments = {
                "should_reduce": False,
                "should_increase": False,
                "should_close": False,
                "adjustment_reason": "",
                "new_position_size": current_metrics.position_size,
                "risk_level_change": False
            }
            
            # リスク制限チェック
            if current_metrics.var_95 > self.config["risk_limits"]["var_limit_95"]:
                adjustments["should_reduce"] = True
                adjustments["adjustment_reason"] += "VaR制限超過; "
            
            if current_metrics.max_drawdown > self.config["risk_limits"]["max_drawdown_limit"]:
                adjustments["should_reduce"] = True
                adjustments["adjustment_reason"] += "最大ドローダウン制限超過; "
            
            if current_metrics.volatility > 0.3:  # 30%以上のボラティリティ
                adjustments["should_reduce"] = True
                adjustments["adjustment_reason"] += "高ボラティリティ; "
            
            # 前回メトリクスとの比較
            if previous_metrics:
                if current_metrics.risk_level.value != previous_metrics.risk_level.value:
                    adjustments["risk_level_change"] = True
                    adjustments["adjustment_reason"] += "リスクレベル変更; "
                
                # リスク増加時の調整
                if current_metrics.var_95 > previous_metrics.var_95 * 1.2:
                    adjustments["should_reduce"] = True
                    adjustments["adjustment_reason"] += "VaR急増; "
            
            # 市場条件による調整
            if market_conditions:
                if market_conditions.get("high_volatility", False):
                    adjustments["should_reduce"] = True
                    adjustments["adjustment_reason"] += "市場高ボラティリティ; "
                
                if market_conditions.get("low_liquidity", False):
                    adjustments["should_reduce"] = True
                    adjustments["adjustment_reason"] += "流動性低下; "
            
            # ポジションサイズ調整
            if adjustments["should_reduce"]:
                adjustments["new_position_size"] = current_metrics.position_size * 0.5
            elif adjustments["should_increase"]:
                adjustments["new_position_size"] = min(
                    current_metrics.position_size * 1.2,
                    self.config["risk_limits"]["max_position_size"]
                )
            
            return adjustments
            
        except Exception as e:
            self.logger.error(f"ポジション調整判定エラー: {e}")
            return {
                "should_reduce": False,
                "should_increase": False,
                "should_close": False,
                "adjustment_reason": f"エラー: {e}",
                "new_position_size": current_metrics.position_size,
                "risk_level_change": False
            }
    
    def calculate_optimal_position_size(
        self,
        account_value: float,
        risk_metrics: RiskMetrics,
        confidence: float,
        market_conditions: Dict[str, Any] = None
    ) -> float:
        """最適ポジションサイズ計算"""
        try:
            # ケリー基準による基本ポジションサイズ
            kelly_fraction = self._calculate_kelly_fraction(risk_metrics)
            
            # リスク調整
            risk_adjusted_size = kelly_fraction * (1 - risk_metrics.var_95)
            
            # 信頼度調整
            confidence_adjusted_size = risk_adjusted_size * confidence
            
            # 市場条件調整
            if market_conditions:
                if market_conditions.get("high_volatility", False):
                    confidence_adjusted_size *= 0.7
                if market_conditions.get("low_liquidity", False):
                    confidence_adjusted_size *= 0.8
            
            # 制限適用
            max_size = self.config["risk_limits"]["max_position_size"]
            min_size = 0.01  # 最小1%
            
            optimal_size = max(min_size, min(confidence_adjusted_size, max_size))
            
            return optimal_size
            
        except Exception as e:
            self.logger.error(f"最適ポジションサイズ計算エラー: {e}")
            return 0.05  # デフォルト5%
    
    # ヘルパーメソッド群
    def _calculate_var(self, stock_data: pd.DataFrame) -> Tuple[float, float]:
        """VaR計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.05, 0.10
        
        returns = stock_data['Close'].pct_change().dropna()
        if len(returns) < 10:
            return 0.05, 0.10
        
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        return abs(var_95), abs(var_99)
    
    def _calculate_max_drawdown(self, stock_data: pd.DataFrame) -> float:
        """最大ドローダウン計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.0
        
        prices = stock_data['Close']
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        
        return abs(drawdown.min())
    
    def _calculate_sharpe_ratio(self, stock_data: pd.DataFrame, market_data: pd.DataFrame) -> float:
        """シャープレシオ計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.0
        
        stock_returns = stock_data['Close'].pct_change().dropna()
        if len(stock_returns) < 2:
            return 0.0
        
        # リスクフリーレート（仮に2%とする）
        risk_free_rate = 0.02 / 252  # 日次
        
        excess_returns = stock_returns - risk_free_rate
        sharpe = excess_returns.mean() / stock_returns.std() * np.sqrt(252)
        
        return sharpe
    
    def _calculate_sortino_ratio(self, stock_data: pd.DataFrame) -> float:
        """ソルティノレシオ計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.0
        
        returns = stock_data['Close'].pct_change().dropna()
        if len(returns) < 2:
            return 0.0
        
        # 下方偏差計算
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            return 0.0  # 負のリターンがない場合は0を返す
        
        downside_deviation = negative_returns.std()
        if downside_deviation == 0:
            return 0.0  # 下方偏差が0の場合は0を返す
        
        mean_return = returns.mean()
        if mean_return <= 0:
            return 0.0  # 平均リターンが0以下の場合は0を返す
        
        sortino = mean_return / downside_deviation * np.sqrt(252)
        
        # ソルティノレシオを0以上に制限
        return max(0.0, sortino)
    
    def _calculate_calmar_ratio(self, stock_data: pd.DataFrame) -> float:
        """カルマーレシオ計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.0
        
        returns = stock_data['Close'].pct_change().dropna()
        if len(returns) < 2:
            return 0.0
        
        annual_return = returns.mean() * 252
        max_dd = self._calculate_max_drawdown(stock_data)
        
        if max_dd == 0 or annual_return <= 0:
            return 0.0  # 最大ドローダウンが0または年率リターンが0以下の場合は0を返す
        
        calmar = annual_return / max_dd
        
        # カルマーレシオを0以上に制限
        return max(0.0, calmar)
    
    def _calculate_volatility(self, stock_data: pd.DataFrame) -> float:
        """ボラティリティ計算"""
        if 'Close' not in stock_data.columns or stock_data.empty:
            return 0.2
        
        returns = stock_data['Close'].pct_change().dropna()
        if len(returns) < 2:
            return 0.2
        
        return returns.std() * np.sqrt(252)
    
    def _calculate_beta(self, stock_data: pd.DataFrame, market_data: pd.DataFrame) -> float:
        """ベータ計算"""
        if ('Close' not in stock_data.columns or stock_data.empty or
            'Close' not in market_data.columns or market_data.empty):
            return 1.0
        
        stock_returns = stock_data['Close'].pct_change().dropna()
        market_returns = market_data['Close'].pct_change().dropna()
        
        if len(stock_returns) < 2 or len(market_returns) < 2:
            return 1.0
        
        # 共通の日付で結合
        common_dates = stock_returns.index.intersection(market_returns.index)
        if len(common_dates) < 2:
            return 1.0
        
        stock_aligned = stock_returns.loc[common_dates]
        market_aligned = market_returns.loc[common_dates]
        
        # データの長さを揃える
        min_length = min(len(stock_aligned), len(market_aligned))
        if min_length < 2:
            return 1.0
        
        stock_aligned = stock_aligned.iloc[:min_length]
        market_aligned = market_aligned.iloc[:min_length]
        
        try:
            covariance = np.cov(stock_aligned, market_aligned)[0, 1]
            market_variance = np.var(market_aligned)
            
            if market_variance == 0 or np.isnan(covariance) or np.isnan(market_variance):
                return 1.0
            
            beta = covariance / market_variance
            
            # ベータ値を0以上に制限
            return max(0.0, beta)
            
        except Exception:
            return 1.0
    
    def _calculate_correlation(self, stock_data: pd.DataFrame, market_data: pd.DataFrame) -> float:
        """相関計算"""
        if ('Close' not in stock_data.columns or stock_data.empty or
            'Close' not in market_data.columns or market_data.empty):
            return 0.0
        
        stock_returns = stock_data['Close'].pct_change().dropna()
        market_returns = market_data['Close'].pct_change().dropna()
        
        if len(stock_returns) < 2 or len(market_returns) < 2:
            return 0.0
        
        # 共通の日付で結合
        common_dates = stock_returns.index.intersection(market_returns.index)
        if len(common_dates) < 2:
            return 0.0
        
        stock_aligned = stock_returns.loc[common_dates]
        market_aligned = market_returns.loc[common_dates]
        
        correlation = np.corrcoef(stock_aligned, market_aligned)[0, 1]
        
        return correlation if not np.isnan(correlation) else 0.0
    
    def _determine_risk_level(self, var_95: float, max_drawdown: float, volatility: float) -> RiskLevel:
        """リスクレベル決定"""
        risk_score = 0
        
        # VaRスコア
        if var_95 > 0.05:  # 高リスク
            risk_score += 3
        elif var_95 > 0.03:  # 中リスク
            risk_score += 2
        elif var_95 > 0.01:  # 低リスク
            risk_score += 1
        
        # 最大ドローダウンスコア
        if max_drawdown > 0.20:  # 高リスク
            risk_score += 3
        elif max_drawdown > 0.10:  # 中リスク
            risk_score += 2
        elif max_drawdown > 0.05:  # 低リスク
            risk_score += 1
        
        # ボラティリティスコア
        if volatility > 0.30:  # 高リスク
            risk_score += 3
        elif volatility > 0.20:  # 中リスク
            risk_score += 2
        elif volatility > 0.10:  # 低リスク
            risk_score += 1
        
        # リスクレベル決定
        if risk_score >= 6:  # 非常に高いリスク
            return RiskLevel.VERY_HIGH
        elif risk_score >= 4:  # 高いリスク
            return RiskLevel.HIGH
        elif risk_score >= 2:  # 中程度のリスク
            return RiskLevel.MEDIUM
        elif risk_score >= 1:  # 低いリスク
            return RiskLevel.LOW
        else:  # 非常に低いリスク
            return RiskLevel.VERY_LOW
    
    def _calculate_dynamic_position_size(
        self, base_size: float, risk_level: RiskLevel, volatility: float, beta: float
    ) -> float:
        """動的ポジションサイズ計算"""
        # リスクレベル調整
        risk_multipliers = {
            RiskLevel.VERY_LOW: 1.2,
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 0.8,
            RiskLevel.HIGH: 0.6,
            RiskLevel.VERY_HIGH: 0.4
        }
        
        risk_adjusted_size = base_size * risk_multipliers.get(risk_level, 0.8)
        
        # ボラティリティ調整
        vol_adjustment = max(0.5, 1.0 - volatility)
        
        # ベータ調整
        beta_adjustment = max(0.7, 1.0 - abs(beta - 1.0) * 0.3)
        
        final_size = risk_adjusted_size * vol_adjustment * beta_adjustment
        
        return max(0.01, min(final_size, self.config["risk_limits"]["max_position_size"]))
    
    def _calculate_dynamic_stop_take(
        self, current_price: float, volatility: float, risk_level: RiskLevel
    ) -> Tuple[float, float]:
        """動的損切り・利確計算"""
        # 基本損切り・利確
        stop_loss_config = self.config.get("stop_loss", self._get_default_config()["stop_loss"])
        take_profit_config = self.config.get("take_profit", self._get_default_config()["take_profit"])
        base_stop = stop_loss_config["base_stop_loss"]
        base_take = take_profit_config["base_take_profit"]
        
        # ボラティリティ調整
        vol_multiplier = stop_loss_config["volatility_multiplier"]
        vol_adjusted_stop = base_stop * (1 + volatility * vol_multiplier)
        
        # リスクレベル調整
        risk_multipliers = {
            RiskLevel.VERY_LOW: 0.8,
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 1.2,
            RiskLevel.HIGH: 1.5,
            RiskLevel.VERY_HIGH: 2.0
        }
        
        risk_adjusted_stop = vol_adjusted_stop * risk_multipliers.get(risk_level, 1.0)
        
        # 制限適用
        final_stop = max(
            stop_loss_config["min_stop_loss"],
            min(risk_adjusted_stop, stop_loss_config["max_stop_loss"])
        )
        
        # 利確計算（リスクリワード比ベース）
        risk_reward_ratio = take_profit_config["risk_reward_ratio"]
        final_take = final_stop * risk_reward_ratio
        
        # 価格に適用
        stop_loss_price = current_price * (1 - final_stop)
        take_profit_price = current_price * (1 + final_take)
        
        return stop_loss_price, take_profit_price
    
    def _calculate_market_volatility(self, market_data: pd.DataFrame) -> float:
        """市場ボラティリティ計算"""
        if 'Close' not in market_data.columns or market_data.empty:
            return 0.2
        
        returns = market_data['Close'].pct_change().dropna()
        if len(returns) < 2:
            return 0.2
        
        return returns.std() * np.sqrt(252)
    
    def _calculate_volatility_adjustment(self, market_volatility: float) -> float:
        """ボラティリティ調整計算"""
        if market_volatility > 0.3:
            return 0.7  # 高ボラティリティ時は調整
        elif market_volatility > 0.2:
            return 0.8
        else:
            return 1.0
    
    def _calculate_sector_risk_adjustment(self, sector_data: Optional[pd.DataFrame]) -> float:
        """セクターリスク調整計算"""
        if sector_data is None or sector_data.empty:
            return 1.0
        
        # セクターのボラティリティ計算
        if 'Close' in sector_data.columns:
            sector_returns = sector_data['Close'].pct_change().dropna()
            if len(sector_returns) > 1:
                sector_volatility = sector_returns.std() * np.sqrt(252)
                if sector_volatility > 0.3:
                    return 0.8
                elif sector_volatility > 0.2:
                    return 0.9
        
        return 1.0
    
    def _calculate_liquidity_adjustment(self, stock_data: pd.DataFrame) -> float:
        """流動性調整計算"""
        if 'Volume' not in stock_data.columns or stock_data.empty:
            return 1.0
        
        volumes = stock_data['Volume'].dropna()
        if len(volumes) < 2:
            return 1.0
        
        avg_volume = volumes.mean()
        
        # 流動性スコア（0-1）
        if avg_volume > 1000000:
            return 1.0
        elif avg_volume > 500000:
            return 0.9
        elif avg_volume > 100000:
            return 0.8
        else:
            return 0.7
    
    def _calculate_time_decay_adjustment(self) -> float:
        """時間減衰調整計算"""
        if not self.risk_history:
            return 1.0
        
        # 最近のリスク履歴に基づく調整
        recent_risks = [m.var_95 for m in self.risk_history[-5:]]
        if len(recent_risks) < 3:
            return 1.0
        
        avg_recent_risk = np.mean(recent_risks)
        if avg_recent_risk > 0.05:
            return 0.9  # 高リスク履歴では調整
        else:
            return 1.0
    
    def _calculate_confidence_adjustment(self, confidence: float) -> float:
        """信頼度調整計算"""
        if confidence >= 0.8:
            return 1.1  # 高信頼度では少し増加
        elif confidence >= 0.7:
            return 1.0  # 標準
        elif confidence >= 0.6:
            return 0.9  # 低信頼度では減少
        else:
            return 0.8  # 低信頼度では大幅減少
    
    def _calculate_kelly_fraction(self, risk_metrics: RiskMetrics) -> float:
        """ケリー基準計算"""
        # 簡易的なケリー基準
        win_rate = 0.6  # 仮の勝率
        avg_win = 0.1   # 仮の平均勝利
        avg_loss = 0.05  # 仮の平均損失
        
        if avg_loss == 0:
            return 0.0
        
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_loss
        
        return max(0.0, min(kelly, 0.25))  # 最大25%に制限
    
    def _get_default_risk_metrics(self) -> RiskMetrics:
        """デフォルトリスクメトリクス"""
        return RiskMetrics(
            var_95=0.05,
            var_99=0.10,
            max_drawdown=0.10,
            sharpe_ratio=1.0,
            sortino_ratio=1.0,
            calmar_ratio=1.0,
            volatility=0.20,
            beta=1.0,
            correlation=0.5,
            risk_level=RiskLevel.MEDIUM,
            position_size=0.05,
            stop_loss=0.0,
            take_profit=0.0
        )
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """リスク統計情報取得"""
        if not self.risk_history:
            return {}
        
        var_95s = [m.var_95 for m in self.risk_history]
        max_drawdowns = [m.max_drawdown for m in self.risk_history]
        volatilities = [m.volatility for m in self.risk_history]
        
        return {
            "total_samples": len(self.risk_history),
            "avg_var_95": np.mean(var_95s),
            "max_var_95": np.max(var_95s),
            "avg_max_drawdown": np.mean(max_drawdowns),
            "max_drawdown": np.max(max_drawdowns),
            "avg_volatility": np.mean(volatilities),
            "max_volatility": np.max(volatilities),
            "risk_level_distribution": {
                level.value: sum(1 for m in self.risk_history if m.risk_level == level)
                for level in RiskLevel
            }
        }