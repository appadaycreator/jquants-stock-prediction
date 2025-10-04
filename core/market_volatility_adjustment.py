#!/usr/bin/env python3
"""
市場データ・ボラティリティに基づく動的調整システム
記事の手法を超える高度な市場適応機能を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class MarketRegime(Enum):
    """市場レジーム"""
    BULL = "bull"           # 強気市場
    BEAR = "bear"           # 弱気市場
    SIDEWAYS = "sideways"   # 横ばい市場
    VOLATILE = "volatile"   # 高ボラティリティ市場
    CALM = "calm"          # 低ボラティリティ市場


class VolatilityRegime(Enum):
    """ボラティリティレジーム"""
    LOW = "low"             # 低ボラティリティ
    NORMAL = "normal"       # 通常ボラティリティ
    HIGH = "high"           # 高ボラティリティ
    EXTREME = "extreme"     # 極端なボラティリティ


@dataclass
class MarketConditions:
    """市場条件"""
    market_regime: MarketRegime
    volatility_regime: VolatilityRegime
    trend_strength: float
    momentum: float
    volatility: float
    correlation: float
    liquidity: float
    market_stress: float
    regime_confidence: float
    adjustment_factors: Dict[str, float]


@dataclass
class DynamicAdjustment:
    """動的調整"""
    confidence_adjustment: float
    position_size_adjustment: float
    risk_tolerance_adjustment: float
    stop_loss_adjustment: float
    take_profit_adjustment: float
    rebalancing_frequency_adjustment: float
    overall_adjustment: float


class MarketVolatilityAdjustment:
    """市場データ・ボラティリティに基づく動的調整システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.market_history = []
        self.regime_history = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "market_regime_detection": {
                "trend_threshold": 0.05,        # 5%のトレンド閾値
                "momentum_threshold": 0.02,     # 2%のモメンタム閾値
                "volatility_threshold": 0.25,   # 25%のボラティリティ閾値
                "lookback_period": 60,          # 60日間のルックバック
                "min_observations": 30          # 最小観測数
            },
            "volatility_regime_detection": {
                "low_threshold": 0.15,          # 15%以下は低ボラティリティ
                "high_threshold": 0.30,         # 30%以上は高ボラティリティ
                "extreme_threshold": 0.50,      # 50%以上は極端なボラティリティ
                "lookback_period": 30,          # 30日間のルックバック
                "min_observations": 20          # 最小観測数
            },
            "adjustment_factors": {
                "bull_market": {
                    "confidence_multiplier": 1.1,
                    "position_size_multiplier": 1.05,
                    "risk_tolerance_multiplier": 1.02
                },
                "bear_market": {
                    "confidence_multiplier": 0.9,
                    "position_size_multiplier": 0.8,
                    "risk_tolerance_multiplier": 0.7
                },
                "volatile_market": {
                    "confidence_multiplier": 0.8,
                    "position_size_multiplier": 0.7,
                    "risk_tolerance_multiplier": 0.6
                },
                "calm_market": {
                    "confidence_multiplier": 1.05,
                    "position_size_multiplier": 1.02,
                    "risk_tolerance_multiplier": 1.01
                }
            },
            "dynamic_thresholds": {
                "confidence_threshold_base": 0.70,
                "confidence_threshold_volatile": 0.75,
                "confidence_threshold_calm": 0.65,
                "position_size_max_base": 0.10,
                "position_size_max_volatile": 0.05,
                "position_size_max_calm": 0.15
            }
        }
    
    def analyze_market_conditions(
        self,
        market_data: pd.DataFrame,
        sector_data: Optional[Dict[str, pd.DataFrame]] = None,
        economic_indicators: Optional[Dict[str, float]] = None
    ) -> MarketConditions:
        """市場条件分析"""
        try:
            if market_data.empty:
                return self._get_default_market_conditions()
            
            # 市場レジーム検出
            market_regime = self._detect_market_regime(market_data)
            
            # ボラティリティレジーム検出
            volatility_regime = self._detect_volatility_regime(market_data)
            
            # トレンド強度計算
            trend_strength = self._calculate_trend_strength(market_data)
            
            # モメンタム計算
            momentum = self._calculate_momentum(market_data)
            
            # ボラティリティ計算
            volatility = self._calculate_market_volatility(market_data)
            
            # 相関計算
            correlation = self._calculate_market_correlation(market_data, sector_data)
            
            # 流動性計算
            liquidity = self._calculate_market_liquidity(market_data)
            
            # 市場ストレス計算
            market_stress = self._calculate_market_stress(
                market_data, economic_indicators
            )
            
            # レジーム信頼度計算
            regime_confidence = self._calculate_regime_confidence(
                market_data, market_regime, volatility_regime
            )
            
            # 調整係数計算
            adjustment_factors = self._calculate_adjustment_factors(
                market_regime, volatility_regime, market_stress
            )
            
            conditions = MarketConditions(
                market_regime=market_regime,
                volatility_regime=volatility_regime,
                trend_strength=trend_strength,
                momentum=momentum,
                volatility=volatility,
                correlation=correlation,
                liquidity=liquidity,
                market_stress=market_stress,
                regime_confidence=regime_confidence,
                adjustment_factors=adjustment_factors
            )
            
            # 履歴に追加
            self.market_history.append(conditions)
            if len(self.market_history) > 1000:
                self.market_history.pop(0)
            
            return conditions
            
        except Exception as e:
            self.logger.error(f"市場条件分析エラー: {e}")
            return self._get_default_market_conditions()
    
    def calculate_dynamic_adjustment(
        self,
        base_confidence: float,
        base_position_size: float,
        base_risk_tolerance: float,
        market_conditions: MarketConditions,
        stock_specific_factors: Optional[Dict[str, float]] = None
    ) -> DynamicAdjustment:
        """動的調整計算"""
        try:
            # 市場レジームに基づく調整
            regime_factors = market_conditions.adjustment_factors
            
            # 信頼度調整
            confidence_adjustment = self._calculate_confidence_adjustment(
                base_confidence, market_conditions, regime_factors
            )
            
            # ポジションサイズ調整
            position_size_adjustment = self._calculate_position_size_adjustment(
                base_position_size, market_conditions, regime_factors
            )
            
            # リスク許容度調整
            risk_tolerance_adjustment = self._calculate_risk_tolerance_adjustment(
                base_risk_tolerance, market_conditions, regime_factors
            )
            
            # 損切り調整
            stop_loss_adjustment = self._calculate_stop_loss_adjustment(
                market_conditions, stock_specific_factors
            )
            
            # 利確調整
            take_profit_adjustment = self._calculate_take_profit_adjustment(
                market_conditions, stock_specific_factors
            )
            
            # リバランス頻度調整
            rebalancing_frequency_adjustment = self._calculate_rebalancing_frequency_adjustment(
                market_conditions
            )
            
            # 全体的な調整係数
            overall_adjustment = self._calculate_overall_adjustment(
                confidence_adjustment,
                position_size_adjustment,
                risk_tolerance_adjustment,
                market_conditions
            )
            
            return DynamicAdjustment(
                confidence_adjustment=confidence_adjustment,
                position_size_adjustment=position_size_adjustment,
                risk_tolerance_adjustment=risk_tolerance_adjustment,
                stop_loss_adjustment=stop_loss_adjustment,
                take_profit_adjustment=take_profit_adjustment,
                rebalancing_frequency_adjustment=rebalancing_frequency_adjustment,
                overall_adjustment=overall_adjustment
            )
            
        except Exception as e:
            self.logger.error(f"動的調整計算エラー: {e}")
            return self._get_default_dynamic_adjustment()
    
    def _detect_market_regime(self, market_data: pd.DataFrame) -> MarketRegime:
        """市場レジーム検出"""
        if 'Close' not in market_data.columns or market_data.empty:
            return MarketRegime.SIDEWAYS
        
        prices = market_data['Close'].dropna()
        if len(prices) < self.config["market_regime_detection"]["min_observations"]:
            return MarketRegime.SIDEWAYS
        
        # 短期と長期の移動平均
        short_window = 20
        long_window = 60
        
        if len(prices) < long_window:
            return MarketRegime.SIDEWAYS
        
        short_ma = prices.rolling(window=short_window).mean().iloc[-1]
        long_ma = prices.rolling(window=long_window).mean().iloc[-1]
        
        # トレンド判定
        trend_ratio = short_ma / long_ma
        trend_threshold = self.config["market_regime_detection"]["trend_threshold"]
        
        if trend_ratio > 1 + trend_threshold:
            return MarketRegime.BULL
        elif trend_ratio < 1 - trend_threshold:
            return MarketRegime.BEAR
        else:
            # ボラティリティによる判定
            volatility = self._calculate_market_volatility(market_data)
            vol_threshold = self.config["market_regime_detection"]["volatility_threshold"]
            
            if volatility > vol_threshold:
                return MarketRegime.VOLATILE
            else:
                return MarketRegime.SIDEWAYS
    
    def _detect_volatility_regime(self, market_data: pd.DataFrame) -> VolatilityRegime:
        """ボラティリティレジーム検出"""
        volatility = self._calculate_market_volatility(market_data)
        
        thresholds = self.config["volatility_regime_detection"]
        
        if volatility >= thresholds["extreme_threshold"]:
            return VolatilityRegime.EXTREME
        elif volatility >= thresholds["high_threshold"]:
            return VolatilityRegime.HIGH
        elif volatility <= thresholds["low_threshold"]:
            return VolatilityRegime.LOW
        else:
            return VolatilityRegime.NORMAL
    
    def _calculate_trend_strength(self, market_data: pd.DataFrame) -> float:
        """トレンド強度計算"""
        if 'Close' not in market_data.columns or market_data.empty:
            return 0.0
        
        prices = market_data['Close'].dropna()
        if len(prices) < 20:
            return 0.0
        
        # 線形回帰によるトレンド強度
        x = np.arange(len(prices))
        y = prices.values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # R²値をトレンド強度として使用
        return r_value ** 2
    
    def _calculate_momentum(self, market_data: pd.DataFrame) -> float:
        """モメンタム計算"""
        if 'Close' not in market_data.columns or market_data.empty:
            return 0.0
        
        prices = market_data['Close'].dropna()
        if len(prices) < 10:
            return 0.0
        
        # 10日間のリターン
        momentum = (prices.iloc[-1] - prices.iloc[-10]) / prices.iloc[-10]
        
        return momentum
    
    def _calculate_market_volatility(self, market_data: pd.DataFrame) -> float:
        """市場ボラティリティ計算"""
        if 'Close' not in market_data.columns or market_data.empty:
            return 0.2
        
        prices = market_data['Close'].dropna()
        if len(prices) < 2:
            return 0.2
        
        returns = prices.pct_change().dropna()
        if len(returns) < 2:
            return 0.2
        
        volatility = returns.std() * np.sqrt(252)
        
        return volatility
    
    def _calculate_market_correlation(
        self, market_data: pd.DataFrame, sector_data: Optional[Dict[str, pd.DataFrame]]
    ) -> float:
        """市場相関計算"""
        if not sector_data:
            return 0.5
        
        correlations = []
        
        for sector_name, sector_df in sector_data.items():
            if sector_df.empty or 'Close' not in sector_df.columns:
                continue
            
            # 共通の日付で結合
            common_dates = market_data.index.intersection(sector_df.index)
            if len(common_dates) < 10:
                continue
            
            market_returns = market_data['Close'].pct_change().dropna()
            sector_returns = sector_df['Close'].pct_change().dropna()
            
            market_aligned = market_returns.loc[common_dates]
            sector_aligned = sector_returns.loc[common_dates]
            
            if len(market_aligned) > 1 and len(sector_aligned) > 1:
                correlation = np.corrcoef(market_aligned, sector_aligned)[0, 1]
                if not np.isnan(correlation):
                    correlations.append(abs(correlation))
        
        return np.mean(correlations) if correlations else 0.5
    
    def _calculate_market_liquidity(self, market_data: pd.DataFrame) -> float:
        """市場流動性計算"""
        if 'Volume' not in market_data.columns or market_data.empty:
            return 0.5
        
        volumes = market_data['Volume'].dropna()
        if len(volumes) < 2:
            return 0.5
        
        # 平均ボリュームの正規化
        avg_volume = volumes.mean()
        liquidity = min(1.0, avg_volume / 10000000)  # 1000万を上限とする
        
        return liquidity
    
    def _calculate_market_stress(
        self, market_data: pd.DataFrame, economic_indicators: Optional[Dict[str, float]]
    ) -> float:
        """市場ストレス計算"""
        stress_factors = []
        
        # ボラティリティストレス
        volatility = self._calculate_market_volatility(market_data)
        vol_stress = min(1.0, volatility / 0.5)  # 50%を上限とする
        stress_factors.append(vol_stress)
        
        # ドローダウンストレス
        if 'Close' in market_data.columns and not market_data.empty:
            prices = market_data['Close'].dropna()
            if len(prices) > 1:
                peak = prices.expanding().max()
                drawdown = (prices - peak) / peak
                max_dd = abs(drawdown.min())
                dd_stress = min(1.0, max_dd / 0.3)  # 30%を上限とする
                stress_factors.append(dd_stress)
        
        # 経済指標ストレス
        if economic_indicators:
            # VIX等の恐怖指数
            vix = economic_indicators.get('vix', 20)
            vix_stress = min(1.0, vix / 50)  # 50を上限とする
            stress_factors.append(vix_stress)
            
            # 金利変動
            rate_change = abs(economic_indicators.get('rate_change', 0))
            rate_stress = min(1.0, rate_change / 0.02)  # 2%を上限とする
            stress_factors.append(rate_stress)
        
        return np.mean(stress_factors) if stress_factors else 0.5
    
    def _calculate_regime_confidence(
        self, market_data: pd.DataFrame, market_regime: MarketRegime, volatility_regime: VolatilityRegime
    ) -> float:
        """レジーム信頼度計算"""
        if market_data.empty:
            return 0.5
        
        # データの十分性
        data_sufficiency = min(1.0, len(market_data) / 100)
        
        # レジームの一貫性
        regime_consistency = self._calculate_regime_consistency(market_data, market_regime)
        
        # ボラティリティの安定性
        vol_stability = self._calculate_volatility_stability(market_data, volatility_regime)
        
        confidence = (
            data_sufficiency * 0.3 +
            regime_consistency * 0.4 +
            vol_stability * 0.3
        )
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_regime_consistency(self, market_data: pd.DataFrame, market_regime: MarketRegime) -> float:
        """レジーム一貫性計算"""
        if 'Close' not in market_data.columns or market_data.empty:
            return 0.5
        
        prices = market_data['Close'].dropna()
        if len(prices) < 20:
            return 0.5
        
        # 短期と長期の一貫性
        short_trend = self._calculate_trend_direction(prices.tail(20))
        long_trend = self._calculate_trend_direction(prices.tail(60))
        
        consistency = 1.0 - abs(short_trend - long_trend)
        
        return max(0.0, min(1.0, consistency))
    
    def _calculate_trend_direction(self, prices: pd.Series) -> float:
        """トレンド方向計算"""
        if len(prices) < 2:
            return 0.0
        
        x = np.arange(len(prices))
        y = prices.values
        
        slope, _, _, _, _ = stats.linregress(x, y)
        
        return 1.0 if slope > 0 else -1.0
    
    def _calculate_volatility_stability(self, market_data: pd.DataFrame, volatility_regime: VolatilityRegime) -> float:
        """ボラティリティ安定性計算"""
        if 'Close' not in market_data.columns or market_data.empty:
            return 0.5
        
        prices = market_data['Close'].dropna()
        if len(prices) < 30:
            return 0.5
        
        # 短期と長期のボラティリティ
        short_vol = prices.tail(10).pct_change().std() * np.sqrt(252)
        long_vol = prices.tail(30).pct_change().std() * np.sqrt(252)
        
        if long_vol == 0:
            return 0.5
        
        # ボラティリティの安定性
        vol_ratio = short_vol / long_vol
        stability = 1.0 - abs(vol_ratio - 1.0)
        
        return max(0.0, min(1.0, stability))
    
    def _calculate_adjustment_factors(
        self, market_regime: MarketRegime, volatility_regime: VolatilityRegime, market_stress: float
    ) -> Dict[str, float]:
        """調整係数計算"""
        factors = {}
        
        # 市場レジームに基づく調整
        regime_factors = self.config["adjustment_factors"].get(market_regime.value, {})
        factors.update(regime_factors)
        
        # ボラティリティレジームに基づく調整
        if volatility_regime == VolatilityRegime.HIGH:
            factors["confidence_multiplier"] *= 0.9
            factors["position_size_multiplier"] *= 0.8
        elif volatility_regime == VolatilityRegime.LOW:
            factors["confidence_multiplier"] *= 1.05
            factors["position_size_multiplier"] *= 1.02
        
        # 市場ストレスに基づく調整
        stress_adjustment = 1.0 - market_stress * 0.2
        for key in factors:
            factors[key] *= stress_adjustment
        
        return factors
    
    def _calculate_confidence_adjustment(
        self, base_confidence: float, market_conditions: MarketConditions, regime_factors: Dict[str, float]
    ) -> float:
        """信頼度調整計算"""
        multiplier = regime_factors.get("confidence_multiplier", 1.0)
        
        # 市場条件による調整
        if market_conditions.market_regime == MarketRegime.VOLATILE:
            multiplier *= 0.9
        elif market_conditions.market_regime == MarketRegime.CALM:
            multiplier *= 1.05
        
        # ボラティリティによる調整
        if market_conditions.volatility_regime == VolatilityRegime.HIGH:
            multiplier *= 0.85
        elif market_conditions.volatility_regime == VolatilityRegime.LOW:
            multiplier *= 1.1
        
        adjusted_confidence = base_confidence * multiplier
        
        return max(0.0, min(1.0, adjusted_confidence))
    
    def _calculate_position_size_adjustment(
        self, base_position_size: float, market_conditions: MarketConditions, regime_factors: Dict[str, float]
    ) -> float:
        """ポジションサイズ調整計算"""
        multiplier = regime_factors.get("position_size_multiplier", 1.0)
        
        # 市場条件による調整
        if market_conditions.market_regime == MarketRegime.BEAR:
            multiplier *= 0.7
        elif market_conditions.market_regime == MarketRegime.BULL:
            multiplier *= 1.05
        
        # ボラティリティによる調整
        if market_conditions.volatility_regime == VolatilityRegime.HIGH:
            multiplier *= 0.6
        elif market_conditions.volatility_regime == VolatilityRegime.LOW:
            multiplier *= 1.1
        
        # 流動性による調整
        liquidity_adjustment = 0.8 + market_conditions.liquidity * 0.4
        multiplier *= liquidity_adjustment
        
        adjusted_position_size = base_position_size * multiplier
        
        # 動的閾値適用
        max_position = self._get_dynamic_position_limit(market_conditions)
        
        return max(0.01, min(adjusted_position_size, max_position))
    
    def _calculate_risk_tolerance_adjustment(
        self, base_risk_tolerance: float, market_conditions: MarketConditions, regime_factors: Dict[str, float]
    ) -> float:
        """リスク許容度調整計算"""
        multiplier = regime_factors.get("risk_tolerance_multiplier", 1.0)
        
        # 市場ストレスによる調整
        stress_adjustment = 1.0 - market_conditions.market_stress * 0.3
        multiplier *= stress_adjustment
        
        # 相関による調整
        correlation_adjustment = 1.0 - market_conditions.correlation * 0.2
        multiplier *= correlation_adjustment
        
        adjusted_risk_tolerance = base_risk_tolerance * multiplier
        
        return max(0.01, min(adjusted_risk_tolerance, 0.2))
    
    def _calculate_stop_loss_adjustment(
        self, market_conditions: MarketConditions, stock_specific_factors: Optional[Dict[str, float]]
    ) -> float:
        """損切り調整計算"""
        base_stop_loss = 0.05  # 5%
        
        # ボラティリティによる調整
        if market_conditions.volatility_regime == VolatilityRegime.HIGH:
            base_stop_loss *= 1.5
        elif market_conditions.volatility_regime == VolatilityRegime.LOW:
            base_stop_loss *= 0.8
        
        # 市場ストレスによる調整
        stress_adjustment = 1.0 + market_conditions.market_stress * 0.5
        base_stop_loss *= stress_adjustment
        
        # 銘柄固有要因による調整
        if stock_specific_factors:
            beta = stock_specific_factors.get('beta', 1.0)
            base_stop_loss *= (0.8 + beta * 0.4)
        
        return max(0.02, min(base_stop_loss, 0.15))
    
    def _calculate_take_profit_adjustment(
        self, market_conditions: MarketConditions, stock_specific_factors: Optional[Dict[str, float]]
    ) -> float:
        """利確調整計算"""
        base_take_profit = 0.10  # 10%
        
        # 市場レジームによる調整
        if market_conditions.market_regime == MarketRegime.BULL:
            base_take_profit *= 1.2
        elif market_conditions.market_regime == MarketRegime.BEAR:
            base_take_profit *= 0.8
        
        # ボラティリティによる調整
        if market_conditions.volatility_regime == VolatilityRegime.HIGH:
            base_take_profit *= 1.3
        elif market_conditions.volatility_regime == VolatilityRegime.LOW:
            base_take_profit *= 0.9
        
        return max(0.05, min(base_take_profit, 0.25))
    
    def _calculate_rebalancing_frequency_adjustment(self, market_conditions: MarketConditions) -> float:
        """リバランス頻度調整計算"""
        base_frequency = 1.0  # 基準頻度
        
        # ボラティリティによる調整
        if market_conditions.volatility_regime == VolatilityRegime.HIGH:
            base_frequency *= 1.5  # より頻繁にリバランス
        elif market_conditions.volatility_regime == VolatilityRegime.LOW:
            base_frequency *= 0.8  # より少なくリバランス
        
        # 市場ストレスによる調整
        stress_adjustment = 1.0 + market_conditions.market_stress * 0.3
        base_frequency *= stress_adjustment
        
        return max(0.5, min(base_frequency, 2.0))
    
    def _calculate_overall_adjustment(
        self, confidence_adjustment: float, position_size_adjustment: float,
        risk_tolerance_adjustment: float, market_conditions: MarketConditions
    ) -> float:
        """全体的な調整係数計算"""
        # 各調整の重み付き平均
        weights = [0.3, 0.3, 0.2, 0.2]
        adjustments = [
            confidence_adjustment,
            position_size_adjustment,
            risk_tolerance_adjustment,
            market_conditions.regime_confidence
        ]
        
        overall_adjustment = sum(w * a for w, a in zip(weights, adjustments))
        
        return max(0.5, min(overall_adjustment, 1.5))
    
    def _get_dynamic_position_limit(self, market_conditions: MarketConditions) -> float:
        """動的ポジション制限取得"""
        base_limit = self.config["dynamic_thresholds"]["position_size_max_base"]
        
        if market_conditions.volatility_regime == VolatilityRegime.HIGH:
            return self.config["dynamic_thresholds"]["position_size_max_volatile"]
        elif market_conditions.volatility_regime == VolatilityRegime.LOW:
            return self.config["dynamic_thresholds"]["position_size_max_calm"]
        else:
            return base_limit
    
    def _get_default_market_conditions(self) -> MarketConditions:
        """デフォルト市場条件"""
        return MarketConditions(
            market_regime=MarketRegime.SIDEWAYS,
            volatility_regime=VolatilityRegime.NORMAL,
            trend_strength=0.5,
            momentum=0.0,
            volatility=0.2,
            correlation=0.5,
            liquidity=0.5,
            market_stress=0.5,
            regime_confidence=0.5,
            adjustment_factors={}
        )
    
    def _get_default_dynamic_adjustment(self) -> DynamicAdjustment:
        """デフォルト動的調整"""
        return DynamicAdjustment(
            confidence_adjustment=1.0,
            position_size_adjustment=1.0,
            risk_tolerance_adjustment=1.0,
            stop_loss_adjustment=1.0,
            take_profit_adjustment=1.0,
            rebalancing_frequency_adjustment=1.0,
            overall_adjustment=1.0
        )
    
    def get_market_statistics(self) -> Dict[str, Any]:
        """市場統計情報取得"""
        if not self.market_history:
            return {}
        
        regimes = [m.market_regime.value for m in self.market_history]
        vol_regimes = [m.volatility_regime.value for m in self.market_history]
        volatilities = [m.volatility for m in self.market_history]
        stress_levels = [m.market_stress for m in self.market_history]
        
        return {
            "total_samples": len(self.market_history),
            "market_regime_distribution": {
                regime: regimes.count(regime) for regime in set(regimes)
            },
            "volatility_regime_distribution": {
                regime: vol_regimes.count(regime) for regime in set(vol_regimes)
            },
            "avg_volatility": np.mean(volatilities),
            "max_volatility": np.max(volatilities),
            "avg_market_stress": np.mean(stress_levels),
            "max_market_stress": np.max(stress_levels)
        }
