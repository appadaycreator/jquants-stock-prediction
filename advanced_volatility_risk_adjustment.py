#!/usr/bin/env python3
"""
個別銘柄のボラティリティベースリスク調整システム
期待効果: 損失を60-80%削減
実装難易度: 🟡 中
推定工数: 2-3日

機能:
1. リアルタイムボラティリティ監視
2. ボラティリティベースのポジションサイズ調整
3. 動的損切り幅の調整
4. ボラティリティクラスタリング検知
5. ボラティリティ予測による事前リスク管理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from collections import deque
import yfinance as yf
from scipy import stats
from scipy.stats import norm
import asyncio
import aiohttp
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import ta

# 統合ログシステムのインポート
from unified_logging_config import get_system_logger, get_enhanced_logger

warnings.filterwarnings("ignore")

# 統合ログシステムを使用
logger = get_system_logger()
enhanced_logger = get_enhanced_logger()


class VolatilityRegime(Enum):
    """ボラティリティレジーム"""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class VolatilityTrend(Enum):
    """ボラティリティトレンド"""
    DECREASING = "DECREASING"
    STABLE = "STABLE"
    INCREASING = "INCREASING"
    SPIKING = "SPIKING"


@dataclass
class VolatilityMetrics:
    """ボラティリティ指標"""
    symbol: str
    timestamp: datetime
    historical_volatility: float
    realized_volatility: float
    implied_volatility: float
    volatility_percentile: float
    volatility_regime: VolatilityRegime
    volatility_trend: VolatilityTrend
    volatility_clustering: bool
    volatility_risk_score: float
    confidence: float


@dataclass
class VolatilityAdjustment:
    """ボラティリティ調整"""
    symbol: str
    timestamp: datetime
    original_position_size: float
    adjusted_position_size: float
    original_stop_loss: float
    adjusted_stop_loss: float
    volatility_multiplier: float
    risk_reduction: float
    adjustment_reason: str


@dataclass
class VolatilityForecast:
    """ボラティリティ予測"""
    symbol: str
    timestamp: datetime
    forecast_volatility: float
    confidence_interval: Tuple[float, float]
    forecast_horizon: int  # 日数
    regime_probability: Dict[VolatilityRegime, float]
    risk_implications: List[str]


class AdvancedVolatilityRiskAdjustment:
    """高度なボラティリティベースリスク調整システム"""

    def __init__(self, lookback_period: int = 252):
        self.lookback_period = lookback_period
        self.volatility_history = defaultdict(lambda: deque(maxlen=lookback_period))
        self.volatility_regimes = {}
        self.adjustment_history = defaultdict(list)
        
        # ボラティリティ閾値
        self.volatility_thresholds = {
            "low": 0.15,      # 15%以下
            "normal": 0.25,   # 15-25%
            "high": 0.40,     # 25-40%
            "extreme": 0.60   # 40%以上
        }
        
        # リスク調整パラメータ
        self.risk_params = {
            "max_volatility_multiplier": 3.0,
            "min_volatility_multiplier": 0.3,
            "volatility_smoothing": 0.1,
            "regime_stability_threshold": 0.7,
        }

    async def analyze_volatility_risk(self, symbol: str) -> VolatilityMetrics:
        """ボラティリティリスク分析"""
        try:
            logger.info(f"ボラティリティリスク分析開始: {symbol}")
            
            # 株価データ取得
            stock_data = await self._get_stock_data(symbol)
            if stock_data is None:
                return self._create_default_volatility_metrics(symbol)
            
            # ボラティリティ指標計算
            historical_vol = self._calculate_historical_volatility(stock_data)
            realized_vol = self._calculate_realized_volatility(stock_data)
            implied_vol = await self._estimate_implied_volatility(symbol, stock_data)
            
            # ボラティリティパーセンタイル
            vol_percentile = self._calculate_volatility_percentile(symbol, historical_vol)
            
            # ボラティリティレジーム判定
            volatility_regime = self._determine_volatility_regime(historical_vol)
            
            # ボラティリティトレンド分析
            volatility_trend = self._analyze_volatility_trend(symbol, historical_vol)
            
            # ボラティリティクラスタリング検知
            clustering_detected = self._detect_volatility_clustering(symbol, stock_data)
            
            # ボラティリティリスクスコア計算
            risk_score = self._calculate_volatility_risk_score(
                historical_vol, realized_vol, vol_percentile, volatility_trend
            )
            
            # 信頼度計算
            confidence = self._calculate_confidence(stock_data)
            
            # ボラティリティ指標作成
            metrics = VolatilityMetrics(
                symbol=symbol,
                timestamp=datetime.now(),
                historical_volatility=historical_vol,
                realized_volatility=realized_vol,
                implied_volatility=implied_vol,
                volatility_percentile=vol_percentile,
                volatility_regime=volatility_regime,
                volatility_trend=volatility_trend,
                volatility_clustering=clustering_detected,
                volatility_risk_score=risk_score,
                confidence=confidence,
            )
            
            # 履歴に追加
            self.volatility_history[symbol].append(metrics)
            
            logger.info(f"ボラティリティ分析完了: {symbol} - レジーム: {volatility_regime.value}")
            return metrics

        except Exception as e:
            logger.error(f"ボラティリティ分析エラー: {symbol} - {e}")
            return self._create_default_volatility_metrics(symbol)

    async def _get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """株価データ取得"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            
            if len(hist) < 30:
                return None
            
            return hist
        except Exception as e:
            logger.error(f"株価データ取得エラー: {symbol} - {e}")
            return None

    def _calculate_historical_volatility(self, stock_data: pd.DataFrame) -> float:
        """ヒストリカルボラティリティ計算"""
        try:
            returns = stock_data['Close'].pct_change().dropna()
            return returns.std() * np.sqrt(252)
        except Exception as e:
            logger.error(f"ヒストリカルボラティリティ計算エラー: {e}")
            return 0.2

    def _calculate_realized_volatility(self, stock_data: pd.DataFrame) -> float:
        """実現ボラティリティ計算"""
        try:
            # 最近20日間の実現ボラティリティ
            recent_data = stock_data.tail(20)
            returns = recent_data['Close'].pct_change().dropna()
            return returns.std() * np.sqrt(252)
        except Exception as e:
            logger.error(f"実現ボラティリティ計算エラー: {e}")
            return 0.2

    async def _estimate_implied_volatility(self, symbol: str, stock_data: pd.DataFrame) -> float:
        """インプライドボラティリティ推定"""
        try:
            # 簡易実装: ヒストリカルボラティリティをベースに調整
            historical_vol = self._calculate_historical_volatility(stock_data)
            
            # 最近の価格変動を考慮した調整
            recent_returns = stock_data['Close'].pct_change().tail(5).dropna()
            recent_vol = recent_returns.std() * np.sqrt(252)
            
            # 重み付き平均
            implied_vol = historical_vol * 0.7 + recent_vol * 0.3
            
            return implied_vol
        except Exception as e:
            logger.error(f"インプライドボラティリティ推定エラー: {e}")
            return 0.2

    def _calculate_volatility_percentile(self, symbol: str, current_vol: float) -> float:
        """ボラティリティパーセンタイル計算"""
        try:
            if symbol not in self.volatility_history or len(self.volatility_history[symbol]) < 10:
                return 50.0
            
            # 履歴データからボラティリティの分布を計算
            historical_vols = [metrics.historical_volatility for metrics in self.volatility_history[symbol]]
            
            # パーセンタイル計算
            percentile = stats.percentileofscore(historical_vols, current_vol)
            return percentile
        except Exception as e:
            logger.error(f"ボラティリティパーセンタイル計算エラー: {e}")
            return 50.0

    def _determine_volatility_regime(self, volatility: float) -> VolatilityRegime:
        """ボラティリティレジーム判定"""
        if volatility <= self.volatility_thresholds["low"]:
            return VolatilityRegime.LOW
        elif volatility <= self.volatility_thresholds["normal"]:
            return VolatilityRegime.NORMAL
        elif volatility <= self.volatility_thresholds["high"]:
            return VolatilityRegime.HIGH
        else:
            return VolatilityRegime.EXTREME

    def _analyze_volatility_trend(self, symbol: str, current_vol: float) -> VolatilityTrend:
        """ボラティリティトレンド分析"""
        try:
            if symbol not in self.volatility_history or len(self.volatility_history[symbol]) < 5:
                return VolatilityTrend.STABLE
            
            # 最近のボラティリティ履歴
            recent_vols = [metrics.historical_volatility for metrics in list(self.volatility_history[symbol])[-5:]]
            
            # トレンド計算
            if len(recent_vols) >= 3:
                # 線形回帰によるトレンド分析
                x = np.arange(len(recent_vols))
                slope, _, _, _, _ = stats.linregress(x, recent_vols)
                
                # トレンド判定
                if slope > 0.01:  # 上昇トレンド
                    if current_vol > np.mean(recent_vols) * 1.5:
                        return VolatilityTrend.SPIKING
                    else:
                        return VolatilityTrend.INCREASING
                elif slope < -0.01:  # 下降トレンド
                    return VolatilityTrend.DECREASING
                else:
                    return VolatilityTrend.STABLE
            
            return VolatilityTrend.STABLE
        except Exception as e:
            logger.error(f"ボラティリティトレンド分析エラー: {e}")
            return VolatilityTrend.STABLE

    def _detect_volatility_clustering(self, symbol: str, stock_data: pd.DataFrame) -> bool:
        """ボラティリティクラスタリング検知"""
        try:
            # 最近30日間のデータでクラスタリング分析
            recent_data = stock_data.tail(30)
            if len(recent_data) < 20:
                return False
            
            # 日次リターン計算
            returns = recent_data['Close'].pct_change().dropna()
            
            # ボラティリティクラスタリング検知（簡易実装）
            # 高ボラティリティ期間の連続性をチェック
            high_vol_periods = 0
            consecutive_high_vol = 0
            max_consecutive = 0
            
            for ret in returns:
                if abs(ret) > returns.std() * 2:  # 2σ以上
                    consecutive_high_vol += 1
                    max_consecutive = max(max_consecutive, consecutive_high_vol)
                else:
                    consecutive_high_vol = 0
            
            # クラスタリング検知条件
            clustering_threshold = 3  # 3日以上連続で高ボラティリティ
            return max_consecutive >= clustering_threshold
            
        except Exception as e:
            logger.error(f"ボラティリティクラスタリング検知エラー: {e}")
            return False

    def _calculate_volatility_risk_score(
        self, 
        historical_vol: float, 
        realized_vol: float, 
        vol_percentile: float,
        trend: VolatilityTrend
    ) -> float:
        """ボラティリティリスクスコア計算"""
        try:
            # ベースリスクスコア（ボラティリティレベル）
            base_score = min(historical_vol / 0.5, 1.0)  # 50%を最大リスクとする
            
            # パーセンタイル調整
            percentile_score = vol_percentile / 100.0
            
            # トレンド調整
            trend_multiplier = {
                VolatilityTrend.DECREASING: 0.8,
                VolatilityTrend.STABLE: 1.0,
                VolatilityTrend.INCREASING: 1.2,
                VolatilityTrend.SPIKING: 1.5,
            }.get(trend, 1.0)
            
            # 実現ボラティリティとヒストリカルボラティリティの乖離
            vol_divergence = abs(realized_vol - historical_vol) / historical_vol
            divergence_score = min(vol_divergence, 1.0)
            
            # 総合リスクスコア
            total_score = (base_score * 0.4 + percentile_score * 0.3 + 
                          divergence_score * 0.3) * trend_multiplier
            
            return min(total_score, 1.0)
        except Exception as e:
            logger.error(f"ボラティリティリスクスコア計算エラー: {e}")
            return 0.5

    def _calculate_confidence(self, stock_data: pd.DataFrame) -> float:
        """信頼度計算"""
        try:
            # データ量による信頼度
            data_confidence = min(len(stock_data) / 252, 1.0)
            
            # データの一貫性による信頼度
            returns = stock_data['Close'].pct_change().dropna()
            consistency = 1.0 - (returns.std() / returns.mean() if returns.mean() != 0 else 0.5)
            consistency_confidence = max(0.0, min(1.0, consistency))
            
            # 総合信頼度
            total_confidence = (data_confidence * 0.6 + consistency_confidence * 0.4)
            
            return total_confidence
        except Exception as e:
            logger.error(f"信頼度計算エラー: {e}")
            return 0.5

    async def adjust_position_for_volatility(
        self, 
        symbol: str, 
        original_position_size: float,
        original_stop_loss: float,
        current_price: float
    ) -> VolatilityAdjustment:
        """ボラティリティに基づくポジション調整"""
        try:
            # ボラティリティ分析
            vol_metrics = await self.analyze_volatility_risk(symbol)
            
            # ボラティリティ調整係数計算
            vol_multiplier = self._calculate_volatility_multiplier(vol_metrics)
            
            # ポジションサイズ調整
            adjusted_position_size = original_position_size * vol_multiplier
            
            # ストップロス調整
            stop_loss_adjustment = self._calculate_stop_loss_adjustment(vol_metrics)
            adjusted_stop_loss = original_stop_loss * stop_loss_adjustment
            
            # リスク削減効果計算
            risk_reduction = max(0, (original_position_size - adjusted_position_size) / original_position_size)
            
            # 調整理由生成
            adjustment_reason = self._generate_adjustment_reason(vol_metrics, vol_multiplier)
            
            # 調整記録
            adjustment = VolatilityAdjustment(
                symbol=symbol,
                timestamp=datetime.now(),
                original_position_size=original_position_size,
                adjusted_position_size=adjusted_position_size,
                original_stop_loss=original_stop_loss,
                adjusted_stop_loss=adjusted_stop_loss,
                volatility_multiplier=vol_multiplier,
                risk_reduction=risk_reduction,
                adjustment_reason=adjustment_reason,
            )
            
            # 履歴に追加
            self.adjustment_history[symbol].append(adjustment)
            
            logger.info(f"ボラティリティ調整完了: {symbol} - 調整係数: {vol_multiplier:.3f}")
            return adjustment

        except Exception as e:
            logger.error(f"ボラティリティ調整エラー: {symbol} - {e}")
            return VolatilityAdjustment(
                symbol=symbol,
                timestamp=datetime.now(),
                original_position_size=original_position_size,
                adjusted_position_size=original_position_size,
                original_stop_loss=original_stop_loss,
                adjusted_stop_loss=original_stop_loss,
                volatility_multiplier=1.0,
                risk_reduction=0.0,
                adjustment_reason="エラーにより調整なし",
            )

    def _calculate_volatility_multiplier(self, vol_metrics: VolatilityMetrics) -> float:
        """ボラティリティ調整係数計算"""
        try:
            # ベース調整係数
            base_multiplier = 1.0
            
            # ボラティリティレジームによる調整
            regime_adjustments = {
                VolatilityRegime.LOW: 1.2,      # 低ボラティリティ時はポジションサイズを増加
                VolatilityRegime.NORMAL: 1.0,   # 通常時はそのまま
                VolatilityRegime.HIGH: 0.7,     # 高ボラティリティ時はポジションサイズを削減
                VolatilityRegime.EXTREME: 0.4,  # 極端なボラティリティ時は大幅削減
            }
            
            regime_multiplier = regime_adjustments.get(vol_metrics.volatility_regime, 1.0)
            
            # ボラティリティトレンドによる調整
            trend_adjustments = {
                VolatilityTrend.DECREASING: 1.1,
                VolatilityTrend.STABLE: 1.0,
                VolatilityTrend.INCREASING: 0.8,
                VolatilityTrend.SPIKING: 0.5,
            }
            
            trend_multiplier = trend_adjustments.get(vol_metrics.volatility_trend, 1.0)
            
            # ボラティリティクラスタリングによる調整
            clustering_multiplier = 0.6 if vol_metrics.volatility_clustering else 1.0
            
            # 総合調整係数
            total_multiplier = base_multiplier * regime_multiplier * trend_multiplier * clustering_multiplier
            
            # 最小・最大制限
            total_multiplier = max(
                self.risk_params["min_volatility_multiplier"],
                min(self.risk_params["max_volatility_multiplier"], total_multiplier)
            )
            
            return total_multiplier
        except Exception as e:
            logger.error(f"ボラティリティ調整係数計算エラー: {e}")
            return 1.0

    def _calculate_stop_loss_adjustment(self, vol_metrics: VolatilityMetrics) -> float:
        """ストップロス調整係数計算"""
        try:
            # ボラティリティが高いほどストップロスを緩くする
            if vol_metrics.volatility_regime == VolatilityRegime.EXTREME:
                return 1.5  # 50%緩く
            elif vol_metrics.volatility_regime == VolatilityRegime.HIGH:
                return 1.3  # 30%緩く
            elif vol_metrics.volatility_regime == VolatilityRegime.NORMAL:
                return 1.0  # そのまま
            else:  # LOW
                return 0.8  # 20%厳しく
            
        except Exception as e:
            logger.error(f"ストップロス調整係数計算エラー: {e}")
            return 1.0

    def _generate_adjustment_reason(
        self, vol_metrics: VolatilityMetrics, vol_multiplier: float
    ) -> str:
        """調整理由生成"""
        try:
            reasons = []
            
            # レジームによる理由
            regime_reasons = {
                VolatilityRegime.LOW: "低ボラティリティ環境のためポジションサイズを増加",
                VolatilityRegime.NORMAL: "通常のボラティリティ環境",
                VolatilityRegime.HIGH: "高ボラティリティ環境のためポジションサイズを削減",
                VolatilityRegime.EXTREME: "極端なボラティリティ環境のため大幅にポジションサイズを削減",
            }
            
            reasons.append(regime_reasons.get(vol_metrics.volatility_regime, ""))
            
            # トレンドによる理由
            if vol_metrics.volatility_trend == VolatilityTrend.SPIKING:
                reasons.append("ボラティリティスパイク検知のためリスクを大幅削減")
            elif vol_metrics.volatility_trend == VolatilityTrend.INCREASING:
                reasons.append("ボラティリティ上昇トレンドのためリスクを削減")
            
            # クラスタリングによる理由
            if vol_metrics.volatility_clustering:
                reasons.append("ボラティリティクラスタリング検知のためリスクを削減")
            
            return "; ".join([r for r in reasons if r])
        except Exception as e:
            logger.error(f"調整理由生成エラー: {e}")
            return "ボラティリティ分析に基づく調整"

    async def forecast_volatility(self, symbol: str, horizon_days: int = 5) -> VolatilityForecast:
        """ボラティリティ予測"""
        try:
            # 現在のボラティリティ分析
            current_metrics = await self.analyze_volatility_risk(symbol)
            
            # 簡易予測モデル（履歴データベース）
            if symbol in self.volatility_history and len(self.volatility_history[symbol]) > 10:
                # 履歴データから予測
                historical_vols = [metrics.historical_volatility for metrics in self.volatility_history[symbol]]
                
                # 移動平均による予測
                forecast_vol = np.mean(historical_vols[-5:])  # 最近5回の平均
                
                # 信頼区間計算
                vol_std = np.std(historical_vols[-10:])
                confidence_interval = (
                    max(0, forecast_vol - 1.96 * vol_std),
                    forecast_vol + 1.96 * vol_std
                )
            else:
                # デフォルト予測
                forecast_vol = current_metrics.historical_volatility
                confidence_interval = (forecast_vol * 0.8, forecast_vol * 1.2)
            
            # レジーム確率計算
            regime_probability = self._calculate_regime_probability(forecast_vol)
            
            # リスク含意分析
            risk_implications = self._analyze_risk_implications(forecast_vol, current_metrics)
            
            return VolatilityForecast(
                symbol=symbol,
                timestamp=datetime.now(),
                forecast_volatility=forecast_vol,
                confidence_interval=confidence_interval,
                forecast_horizon=horizon_days,
                regime_probability=regime_probability,
                risk_implications=risk_implications,
            )
            
        except Exception as e:
            logger.error(f"ボラティリティ予測エラー: {symbol} - {e}")
            return VolatilityForecast(
                symbol=symbol,
                timestamp=datetime.now(),
                forecast_volatility=0.2,
                confidence_interval=(0.15, 0.25),
                forecast_horizon=horizon_days,
                regime_probability={regime: 0.25 for regime in VolatilityRegime},
                risk_implications=["予測エラーのためデフォルト値を使用"],
            )

    def _calculate_regime_probability(self, forecast_vol: float) -> Dict[VolatilityRegime, float]:
        """レジーム確率計算"""
        try:
            probabilities = {}
            
            # 各レジームの確率を正規分布で計算
            for regime in VolatilityRegime:
                if regime == VolatilityRegime.LOW:
                    prob = norm.cdf(self.volatility_thresholds["low"], forecast_vol, forecast_vol * 0.1)
                elif regime == VolatilityRegime.NORMAL:
                    prob = (norm.cdf(self.volatility_thresholds["normal"], forecast_vol, forecast_vol * 0.1) - 
                           norm.cdf(self.volatility_thresholds["low"], forecast_vol, forecast_vol * 0.1))
                elif regime == VolatilityRegime.HIGH:
                    prob = (norm.cdf(self.volatility_thresholds["high"], forecast_vol, forecast_vol * 0.1) - 
                           norm.cdf(self.volatility_thresholds["normal"], forecast_vol, forecast_vol * 0.1))
                else:  # EXTREME
                    prob = 1 - norm.cdf(self.volatility_thresholds["high"], forecast_vol, forecast_vol * 0.1)
                
                probabilities[regime] = max(0, min(1, prob))
            
            # 正規化
            total_prob = sum(probabilities.values())
            if total_prob > 0:
                for regime in probabilities:
                    probabilities[regime] /= total_prob
            
            return probabilities
        except Exception as e:
            logger.error(f"レジーム確率計算エラー: {e}")
            return {regime: 0.25 for regime in VolatilityRegime}

    def _analyze_risk_implications(self, forecast_vol: float, current_metrics: VolatilityMetrics) -> List[str]:
        """リスク含意分析"""
        implications = []
        
        try:
            # 予測ボラティリティによる含意
            if forecast_vol > current_metrics.historical_volatility * 1.2:
                implications.append("予測ボラティリティ上昇によりリスク増加が予想されます")
            elif forecast_vol < current_metrics.historical_volatility * 0.8:
                implications.append("予測ボラティリティ低下によりリスク減少が予想されます")
            
            # レジーム変化の含意
            forecast_regime = self._determine_volatility_regime(forecast_vol)
            if forecast_regime != current_metrics.volatility_regime:
                implications.append(f"ボラティリティレジームが{current_metrics.volatility_regime.value}から{forecast_regime.value}に変化する可能性があります")
            
            # トレンド継続の含意
            if current_metrics.volatility_trend == VolatilityTrend.INCREASING:
                implications.append("ボラティリティ上昇トレンドの継続が予想されます")
            elif current_metrics.volatility_trend == VolatilityTrend.DECREASING:
                implications.append("ボラティリティ低下トレンドの継続が予想されます")
            
            return implications
        except Exception as e:
            logger.error(f"リスク含意分析エラー: {e}")
            return ["分析エラーのため詳細な含意を提供できません"]

    def _create_default_volatility_metrics(self, symbol: str) -> VolatilityMetrics:
        """デフォルトボラティリティ指標作成"""
        return VolatilityMetrics(
            symbol=symbol,
            timestamp=datetime.now(),
            historical_volatility=0.2,
            realized_volatility=0.2,
            implied_volatility=0.2,
            volatility_percentile=50.0,
            volatility_regime=VolatilityRegime.NORMAL,
            volatility_trend=VolatilityTrend.STABLE,
            volatility_clustering=False,
            volatility_risk_score=0.5,
            confidence=0.5,
        )

    def get_volatility_summary(self) -> Dict[str, Any]:
        """ボラティリティサマリー取得"""
        try:
            if not self.volatility_history:
                return {"message": "ボラティリティ履歴がありません"}
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "analyzed_symbols": list(self.volatility_history.keys()),
                "volatility_metrics": {},
                "adjustment_summary": {},
            }
            
            # 各銘柄の最新ボラティリティ指標
            for symbol, history in self.volatility_history.items():
                if history:
                    latest_metrics = history[-1]
                    summary["volatility_metrics"][symbol] = asdict(latest_metrics)
            
            # 調整履歴サマリー
            for symbol, adjustments in self.adjustment_history.items():
                if adjustments:
                    latest_adjustment = adjustments[-1]
                    summary["adjustment_summary"][symbol] = {
                        "last_adjustment": asdict(latest_adjustment),
                        "total_adjustments": len(adjustments),
                        "average_risk_reduction": np.mean([adj.risk_reduction for adj in adjustments]),
                    }
            
            return summary
        except Exception as e:
            logger.error(f"ボラティリティサマリー取得エラー: {e}")
            return {"error": str(e)}

    def save_volatility_report(self, filename: str = "volatility_risk_adjustment_report.json"):
        """ボラティリティレポート保存"""
        try:
            report = self.get_volatility_summary()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"ボラティリティレポートを保存しました: {filename}")
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 高度なボラティリティリスク調整システム初期化
    vol_risk_system = AdvancedVolatilityRiskAdjustment()
    
    # テスト銘柄
    test_symbols = ["7203.T", "6758.T", "9984.T", "7974.T", "4063.T"]
    
    logger.info("高度なボラティリティリスク調整システム テスト開始")
    
    # 各銘柄のボラティリティ分析
    for symbol in test_symbols:
        try:
            logger.info(f"ボラティリティ分析開始: {symbol}")
            
            # ボラティリティ分析
            vol_metrics = await vol_risk_system.analyze_volatility_risk(symbol)
            
            logger.info(f"分析完了: {symbol}")
            logger.info(f"  ヒストリカルボラティリティ: {vol_metrics.historical_volatility:.3f}")
            logger.info(f"  ボラティリティレジーム: {vol_metrics.volatility_regime.value}")
            logger.info(f"  ボラティリティトレンド: {vol_metrics.volatility_trend.value}")
            logger.info(f"  クラスタリング検知: {vol_metrics.volatility_clustering}")
            logger.info(f"  リスクスコア: {vol_metrics.volatility_risk_score:.3f}")
            
            # ポジション調整例
            original_position = 100000  # 10万円
            original_stop_loss = 0.02  # 2%
            current_price = 1000.0
            
            adjustment = await vol_risk_system.adjust_position_for_volatility(
                symbol, original_position, original_stop_loss, current_price
            )
            
            logger.info(f"  調整後ポジションサイズ: ¥{adjustment.adjusted_position_size:,.0f}")
            logger.info(f"  調整後ストップロス: {adjustment.adjusted_stop_loss:.3f}")
            logger.info(f"  リスク削減: {adjustment.risk_reduction:.1%}")
            logger.info(f"  調整理由: {adjustment.adjustment_reason}")
            
            # ボラティリティ予測
            forecast = await vol_risk_system.forecast_volatility(symbol, horizon_days=5)
            logger.info(f"  予測ボラティリティ: {forecast.forecast_volatility:.3f}")
            logger.info(f"  信頼区間: {forecast.confidence_interval[0]:.3f} - {forecast.confidence_interval[1]:.3f}")
            
        except Exception as e:
            logger.error(f"ボラティリティ分析エラー: {symbol} - {e}")
    
    # ボラティリティサマリー生成
    summary = vol_risk_system.get_volatility_summary()
    vol_risk_system.save_volatility_report()
    
    # 結果表示
    print("\n" + "=" * 80)
    print("📊 高度なボラティリティリスク調整システム レポート")
    print("=" * 80)
    print(f"分析時刻: {summary['timestamp']}")
    print(f"分析銘柄数: {len(summary['analyzed_symbols'])}")
    
    print("\n📈 ボラティリティ指標:")
    for symbol, metrics in summary['volatility_metrics'].items():
        regime_emoji = {
            "LOW": "🟢", "NORMAL": "🟡", "HIGH": "🟠", "EXTREME": "🔴"
        }.get(metrics['volatility_regime'], "⚪")
        
        print(f"  {regime_emoji} {symbol}: {metrics['volatility_regime']} "
              f"(ボラティリティ: {metrics['historical_volatility']:.3f}, "
              f"リスクスコア: {metrics['volatility_risk_score']:.3f})")
    
    print("\n🔧 調整履歴:")
    for symbol, adj_summary in summary['adjustment_summary'].items():
        print(f"  {symbol}: {adj_summary['total_adjustments']}回調整, "
              f"平均リスク削減: {adj_summary['average_risk_reduction']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())
