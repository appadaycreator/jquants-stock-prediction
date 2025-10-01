#!/usr/bin/env python3
"""
市場環境に応じた戦略調整システム
市場の状況（レジーム、ボラティリティ、トレンド等）に応じて投資戦略を動的に調整

主要機能:
1. 市場レジームの自動判定
2. 環境変化に応じた戦略パラメータ調整
3. リスク管理の動的調整
4. 戦略切り替えの自動化
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import yfinance as yf

# 統合システムのインポート
from unified_system import UnifiedSystem, ErrorCategory, LogLevel, LogCategory
from enhanced_ai_prediction_system import EnhancedAIPredictionSystem, PredictionResult
from investment_style_optimizer import (
    InvestmentStyleOptimizer,
    InvestmentStyle,
    MarketCondition,
)

warnings.filterwarnings("ignore")


class MarketRegime(Enum):
    """市場レジーム"""

    BULL = "bull"  # 強気市場
    BEAR = "bear"  # 弱気市場
    SIDEWAYS = "sideways"  # 横ばい市場
    VOLATILE = "volatile"  # 高ボラティリティ市場
    TRENDING = "trending"  # トレンド市場
    CRISIS = "crisis"  # 危機的状況
    RECOVERY = "recovery"  # 回復期


class MarketPhase(Enum):
    """市場フェーズ"""

    EARLY_BULL = "early_bull"  # 強気初期
    MID_BULL = "mid_bull"  # 強気中期
    LATE_BULL = "late_bull"  # 強気後期
    EARLY_BEAR = "early_bear"  # 弱気初期
    MID_BEAR = "mid_bear"  # 弱気中期
    LATE_BEAR = "late_bear"  # 弱気後期
    CONSOLIDATION = "consolidation"  # 調整期
    BREAKOUT = "breakout"  # ブレイクアウト期


@dataclass
class MarketEnvironment:
    """市場環境"""

    regime: MarketRegime
    phase: MarketPhase
    volatility_level: str  # low, medium, high, extreme
    trend_strength: float
    momentum: float
    volume_profile: str  # low, normal, high, extreme
    sentiment_score: float
    risk_level: str  # low, medium, high, extreme
    market_cap_dominance: Dict[str, float]  # セクター別時価総額比率
    correlation_structure: Dict[str, float]  # 相関構造
    liquidity_conditions: str  # tight, normal, abundant
    created_at: datetime


@dataclass
class StrategyAdjustment:
    """戦略調整"""

    strategy_name: str
    original_parameters: Dict[str, Any]
    adjusted_parameters: Dict[str, Any]
    adjustment_reason: str
    confidence_score: float
    expected_impact: str
    risk_adjustment: Dict[str, float]
    position_size_adjustment: float
    stop_loss_adjustment: float
    take_profit_adjustment: float
    created_at: datetime


class MarketRegimeDetector:
    """市場レジーム検出クラス"""

    def __init__(self, unified_system: UnifiedSystem):
        self.unified_system = unified_system
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.historical_regimes = []

    def detect_market_regime(
        self, data: pd.DataFrame, market_data: Dict[str, Any] = None
    ) -> MarketRegime:
        """市場レジームの検出"""
        try:
            if data.empty or len(data) < 50:
                return MarketRegime.SIDEWAYS

            # 基本指標の計算
            returns = data["Close"].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            trend_strength = self._calculate_trend_strength(data)
            momentum = self._calculate_momentum(data)

            # レジーム判定ロジック
            if volatility > 0.4:  # 極端なボラティリティ
                return MarketRegime.CRISIS
            elif volatility > 0.3:  # 高ボラティリティ
                return MarketRegime.VOLATILE
            elif trend_strength > 0.15:  # 強い上昇トレンド
                return MarketRegime.BULL
            elif trend_strength < -0.15:  # 強い下降トレンド
                return MarketRegime.BEAR
            elif abs(trend_strength) < 0.05:  # 横ばい
                return MarketRegime.SIDEWAYS
            else:
                return MarketRegime.TRENDING

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="市場レジーム検出エラー",
            )
            return MarketRegime.SIDEWAYS

    def detect_market_phase(
        self, data: pd.DataFrame, regime: MarketRegime
    ) -> MarketPhase:
        """市場フェーズの検出"""
        try:
            if len(data) < 20:
                return MarketPhase.CONSOLIDATION

            # 短期・中期・長期移動平均
            sma_short = data["Close"].rolling(5).mean()
            sma_medium = data["Close"].rolling(20).mean()
            sma_long = data["Close"].rolling(50).mean()

            current_price = data["Close"].iloc[-1]
            short_ma = sma_short.iloc[-1]
            medium_ma = sma_medium.iloc[-1]
            long_ma = sma_long.iloc[-1]

            # フェーズ判定
            if regime == MarketRegime.BULL:
                if current_price > short_ma > medium_ma > long_ma:
                    return MarketPhase.MID_BULL
                elif current_price > short_ma and short_ma > medium_ma:
                    return MarketPhase.EARLY_BULL
                else:
                    return MarketPhase.LATE_BULL
            elif regime == MarketRegime.BEAR:
                if current_price < short_ma < medium_ma < long_ma:
                    return MarketPhase.MID_BEAR
                elif current_price < short_ma and short_ma < medium_ma:
                    return MarketPhase.EARLY_BEAR
                else:
                    return MarketPhase.LATE_BEAR
            else:
                return MarketPhase.CONSOLIDATION

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="市場フェーズ検出エラー",
            )
            return MarketPhase.CONSOLIDATION

    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """トレンド強度の計算"""
        if len(data) < 20:
            return 0.0

        # 線形回帰によるトレンド強度
        x = np.arange(len(data))
        y = data["Close"].values
        slope = np.polyfit(x, y, 1)[0]

        # 正規化（価格の範囲で割る）
        price_range = data["Close"].max() - data["Close"].min()
        if price_range > 0:
            return slope / price_range
        return 0.0

    def _calculate_momentum(self, data: pd.DataFrame) -> float:
        """モメンタムの計算"""
        if len(data) < 10:
            return 0.0

        # 10日間のリターン
        return (data["Close"].iloc[-1] - data["Close"].iloc[-10]) / data["Close"].iloc[
            -10
        ]


class MarketEnvironmentAnalyzer:
    """市場環境分析クラス"""

    def __init__(self, unified_system: UnifiedSystem):
        self.unified_system = unified_system
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.regime_detector = MarketRegimeDetector(unified_system)

    def analyze_market_environment(
        self, data: pd.DataFrame, market_data: Dict[str, Any] = None
    ) -> MarketEnvironment:
        """市場環境の包括的分析"""
        try:
            # レジームとフェーズの検出
            regime = self.regime_detector.detect_market_regime(data, market_data)
            phase = self.regime_detector.detect_market_phase(data, regime)

            # ボラティリティレベル
            volatility_level = self._assess_volatility_level(data)

            # トレンド強度
            trend_strength = self.regime_detector._calculate_trend_strength(data)

            # モメンタム
            momentum = self.regime_detector._calculate_momentum(data)

            # ボリュームプロファイル
            volume_profile = self._assess_volume_profile(data)

            # センチメントスコア
            sentiment_score = self._calculate_sentiment_score(data, market_data)

            # リスクレベル
            risk_level = self._assess_risk_level(
                volatility_level, trend_strength, sentiment_score
            )

            # セクター別時価総額比率（簡易版）
            market_cap_dominance = self._get_sector_dominance()

            # 相関構造
            correlation_structure = self._analyze_correlation_structure(data)

            # 流動性条件
            liquidity_conditions = self._assess_liquidity_conditions(data)

            return MarketEnvironment(
                regime=regime,
                phase=phase,
                volatility_level=volatility_level,
                trend_strength=trend_strength,
                momentum=momentum,
                volume_profile=volume_profile,
                sentiment_score=sentiment_score,
                risk_level=risk_level,
                market_cap_dominance=market_cap_dominance,
                correlation_structure=correlation_structure,
                liquidity_conditions=liquidity_conditions,
                created_at=datetime.now(),
            )

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="市場環境分析エラー",
            )
            return self._get_default_environment()

    def _assess_volatility_level(self, data: pd.DataFrame) -> str:
        """ボラティリティレベルの評価"""
        if len(data) < 20:
            return "medium"

        returns = data["Close"].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)

        if volatility > 0.4:
            return "extreme"
        elif volatility > 0.25:
            return "high"
        elif volatility > 0.15:
            return "medium"
        else:
            return "low"

    def _assess_volume_profile(self, data: pd.DataFrame) -> str:
        """ボリュームプロファイルの評価"""
        if len(data) < 20:
            return "normal"

        recent_volume = data["Volume"].iloc[-5:].mean()
        historical_volume = data["Volume"].iloc[-20:].mean()
        volume_ratio = (
            recent_volume / historical_volume if historical_volume > 0 else 1.0
        )

        if volume_ratio > 2.0:
            return "extreme"
        elif volume_ratio > 1.5:
            return "high"
        elif volume_ratio > 0.8:
            return "normal"
        else:
            return "low"

    def _calculate_sentiment_score(
        self, data: pd.DataFrame, market_data: Dict[str, Any] = None
    ) -> float:
        """センチメントスコアの計算"""
        # 簡易版センチメントスコア
        if len(data) < 10:
            return 0.5

        # 価格モメンタム
        price_momentum = (data["Close"].iloc[-1] - data["Close"].iloc[-10]) / data[
            "Close"
        ].iloc[-10]

        # ボリュームモメンタム
        volume_momentum = (
            data["Volume"].iloc[-5:].mean() - data["Volume"].iloc[-15:-5].mean()
        ) / data["Volume"].iloc[-15:-5].mean()

        # 複合スコア
        sentiment = price_momentum * 0.7 + volume_momentum * 0.3
        return max(0.0, min(1.0, (sentiment + 1) / 2))  # 0-1の範囲に正規化

    def _assess_risk_level(
        self, volatility_level: str, trend_strength: float, sentiment_score: float
    ) -> str:
        """リスクレベルの評価"""
        risk_score = 0

        # ボラティリティによるリスク
        if volatility_level == "extreme":
            risk_score += 3
        elif volatility_level == "high":
            risk_score += 2
        elif volatility_level == "medium":
            risk_score += 1

        # トレンド不安定性によるリスク
        if abs(trend_strength) > 0.2:
            risk_score += 1

        # センチメントによるリスク
        if sentiment_score < 0.3 or sentiment_score > 0.8:
            risk_score += 1

        if risk_score >= 4:
            return "extreme"
        elif risk_score >= 3:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def _get_sector_dominance(self) -> Dict[str, float]:
        """セクター別時価総額比率（簡易版）"""
        return {
            "technology": 0.25,
            "financials": 0.20,
            "healthcare": 0.15,
            "consumer_discretionary": 0.12,
            "industrials": 0.10,
            "others": 0.18,
        }

    def _analyze_correlation_structure(self, data: pd.DataFrame) -> Dict[str, float]:
        """相関構造の分析"""
        if len(data) < 20:
            return {"intraday": 0.5, "interday": 0.3}

        # 日次リターンの自己相関
        returns = data["Close"].pct_change().dropna()
        autocorr_1 = returns.autocorr(lag=1) if len(returns) > 1 else 0
        autocorr_5 = returns.autocorr(lag=5) if len(returns) > 5 else 0

        return {
            "intraday": abs(autocorr_1) if not pd.isna(autocorr_1) else 0.5,
            "interday": abs(autocorr_5) if not pd.isna(autocorr_5) else 0.3,
        }

    def _assess_liquidity_conditions(self, data: pd.DataFrame) -> str:
        """流動性条件の評価"""
        if len(data) < 10:
            return "normal"

        # ボリュームの安定性
        volume_cv = data["Volume"].std() / data["Volume"].mean()

        if volume_cv > 1.0:
            return "tight"
        elif volume_cv < 0.3:
            return "abundant"
        else:
            return "normal"

    def _get_default_environment(self) -> MarketEnvironment:
        """デフォルト環境の取得"""
        return MarketEnvironment(
            regime=MarketRegime.SIDEWAYS,
            phase=MarketPhase.CONSOLIDATION,
            volatility_level="medium",
            trend_strength=0.0,
            momentum=0.0,
            volume_profile="normal",
            sentiment_score=0.5,
            risk_level="medium",
            market_cap_dominance={},
            correlation_structure={},
            liquidity_conditions="normal",
            created_at=datetime.now(),
        )


class StrategyEnvironmentAdjuster:
    """戦略環境調整クラス"""

    def __init__(self, unified_system: UnifiedSystem):
        self.unified_system = unified_system
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.adjustment_history = []

    def adjust_strategy_for_environment(
        self,
        strategy_name: str,
        original_parameters: Dict[str, Any],
        environment: MarketEnvironment,
    ) -> StrategyAdjustment:
        """環境に応じた戦略調整"""
        try:
            # 環境別の調整ルール
            adjustment_rules = self._get_adjustment_rules(environment)

            # パラメータ調整
            adjusted_parameters = self._adjust_parameters(
                original_parameters, adjustment_rules
            )

            # リスク調整
            risk_adjustment = self._calculate_risk_adjustment(environment)

            # ポジションサイズ調整
            position_size_adjustment = self._calculate_position_size_adjustment(
                environment
            )

            # ストップロス・利確調整
            (
                stop_loss_adjustment,
                take_profit_adjustment,
            ) = self._calculate_stop_take_adjustment(environment)

            # 調整理由の生成
            adjustment_reason = self._generate_adjustment_reason(
                environment, adjustment_rules
            )

            # 信頼度スコア
            confidence_score = self._calculate_adjustment_confidence(
                environment, adjustment_rules
            )

            # 期待インパクト
            expected_impact = self._assess_expected_impact(
                environment, adjusted_parameters
            )

            adjustment = StrategyAdjustment(
                strategy_name=strategy_name,
                original_parameters=original_parameters,
                adjusted_parameters=adjusted_parameters,
                adjustment_reason=adjustment_reason,
                confidence_score=confidence_score,
                expected_impact=expected_impact,
                risk_adjustment=risk_adjustment,
                position_size_adjustment=position_size_adjustment,
                stop_loss_adjustment=stop_loss_adjustment,
                take_profit_adjustment=take_profit_adjustment,
                created_at=datetime.now(),
            )

            # 履歴に追加
            self.adjustment_history.append(adjustment)

            self.logger.info(
                f"🔧 戦略調整完了: {strategy_name} - {environment.regime.value}環境"
            )

            return adjustment

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"戦略調整エラー: {strategy_name}",
            )
            return self._get_default_adjustment(strategy_name, original_parameters)

    def _get_adjustment_rules(self, environment: MarketEnvironment) -> Dict[str, Any]:
        """環境別調整ルールの取得"""
        rules = {}

        # レジーム別ルール
        if environment.regime == MarketRegime.BULL:
            rules.update(
                {
                    "momentum_weight": 1.2,
                    "trend_following": True,
                    "position_size_multiplier": 1.1,
                    "stop_loss_tightening": 0.9,
                }
            )
        elif environment.regime == MarketRegime.BEAR:
            rules.update(
                {
                    "momentum_weight": 0.8,
                    "trend_following": False,
                    "position_size_multiplier": 0.7,
                    "stop_loss_tightening": 1.2,
                }
            )
        elif environment.regime == MarketRegime.VOLATILE:
            rules.update(
                {
                    "volatility_adjustment": 1.5,
                    "position_size_multiplier": 0.6,
                    "stop_loss_tightening": 1.3,
                }
            )
        elif environment.regime == MarketRegime.CRISIS:
            rules.update(
                {
                    "crisis_mode": True,
                    "position_size_multiplier": 0.3,
                    "stop_loss_tightening": 1.5,
                    "hedging_required": True,
                }
            )

        # フェーズ別ルール
        if environment.phase == MarketPhase.EARLY_BULL:
            rules.update({"aggressive_entry": True, "momentum_weight": 1.3})
        elif environment.phase == MarketPhase.LATE_BULL:
            rules.update({"defensive_mode": True, "position_size_multiplier": 0.8})
        elif environment.phase == MarketPhase.EARLY_BEAR:
            rules.update({"short_bias": True, "defensive_mode": True})

        # リスクレベル別ルール
        if environment.risk_level == "extreme":
            rules.update(
                {
                    "max_position_size": 0.05,
                    "mandatory_hedging": True,
                    "stop_loss_tightening": 2.0,
                }
            )
        elif environment.risk_level == "high":
            rules.update({"max_position_size": 0.1, "stop_loss_tightening": 1.5})

        return rules

    def _adjust_parameters(
        self, original_parameters: Dict[str, Any], rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """パラメータの調整"""
        adjusted = original_parameters.copy()

        # モメンタム重みの調整
        if "momentum_weight" in rules:
            if "momentum_weight" in adjusted:
                adjusted["momentum_weight"] *= rules["momentum_weight"]
            else:
                adjusted["momentum_weight"] = rules["momentum_weight"]

        # ボラティリティ調整
        if "volatility_adjustment" in rules:
            if "volatility_threshold" in adjusted:
                adjusted["volatility_threshold"] *= rules["volatility_adjustment"]

        # トレンドフォロー設定
        if "trend_following" in rules:
            adjusted["trend_following"] = rules["trend_following"]

        # 危機モード
        if rules.get("crisis_mode"):
            adjusted["crisis_mode"] = True
            adjusted["max_drawdown"] = 0.05  # 5%に制限

        return adjusted

    def _calculate_risk_adjustment(
        self, environment: MarketEnvironment
    ) -> Dict[str, float]:
        """リスク調整の計算"""
        base_risk = {"max_drawdown": 0.10, "var_95": 0.05, "correlation_limit": 0.7}

        # 環境に応じた調整
        if environment.risk_level == "extreme":
            base_risk["max_drawdown"] *= 0.5
            base_risk["var_95"] *= 0.5
        elif environment.risk_level == "high":
            base_risk["max_drawdown"] *= 0.7
            base_risk["var_95"] *= 0.7

        if environment.regime == MarketRegime.CRISIS:
            base_risk["max_drawdown"] *= 0.3
            base_risk["var_95"] *= 0.3

        return base_risk

    def _calculate_position_size_adjustment(
        self, environment: MarketEnvironment
    ) -> float:
        """ポジションサイズ調整の計算"""
        base_size = 1.0

        # リスクレベルによる調整
        if environment.risk_level == "extreme":
            base_size *= 0.3
        elif environment.risk_level == "high":
            base_size *= 0.6
        elif environment.risk_level == "medium":
            base_size *= 0.8

        # レジームによる調整
        if environment.regime == MarketRegime.CRISIS:
            base_size *= 0.2
        elif environment.regime == MarketRegime.VOLATILE:
            base_size *= 0.5

        return base_size

    def _calculate_stop_take_adjustment(
        self, environment: MarketEnvironment
    ) -> Tuple[float, float]:
        """ストップロス・利確調整の計算"""
        base_stop = 1.0
        base_take = 1.0

        # ボラティリティによる調整
        if environment.volatility_level == "extreme":
            base_stop *= 1.5
            base_take *= 1.2
        elif environment.volatility_level == "high":
            base_stop *= 1.2
            base_take *= 1.1

        # リスクレベルによる調整
        if environment.risk_level == "extreme":
            base_stop *= 2.0
        elif environment.risk_level == "high":
            base_stop *= 1.5

        return base_stop, base_take

    def _generate_adjustment_reason(
        self, environment: MarketEnvironment, rules: Dict[str, Any]
    ) -> str:
        """調整理由の生成"""
        reasons = []

        reasons.append(f"市場レジーム: {environment.regime.value}")
        reasons.append(f"市場フェーズ: {environment.phase.value}")
        reasons.append(f"リスクレベル: {environment.risk_level}")

        if environment.volatility_level == "extreme":
            reasons.append("極端なボラティリティ環境のため保守的調整")
        elif environment.volatility_level == "high":
            reasons.append("高ボラティリティ環境のためリスク軽減")

        if environment.regime == MarketRegime.CRISIS:
            reasons.append("危機的状況のため最小限のリスク設定")
        elif environment.regime == MarketRegime.BULL:
            reasons.append("強気市場のため積極的設定")

        return "; ".join(reasons)

    def _calculate_adjustment_confidence(
        self, environment: MarketEnvironment, rules: Dict[str, Any]
    ) -> float:
        """調整信頼度の計算"""
        confidence = 0.7  # ベース信頼度

        # 環境の明確性による調整
        if environment.regime in [MarketRegime.BULL, MarketRegime.BEAR]:
            confidence += 0.1
        elif environment.regime == MarketRegime.CRISIS:
            confidence += 0.2

        # リスクレベルの明確性
        if environment.risk_level in ["low", "extreme"]:
            confidence += 0.1

        return min(1.0, confidence)

    def _assess_expected_impact(
        self, environment: MarketEnvironment, adjusted_parameters: Dict[str, Any]
    ) -> str:
        """期待インパクトの評価"""
        if environment.regime == MarketRegime.CRISIS:
            return "リスク大幅軽減、リターン低下"
        elif environment.regime == MarketRegime.BULL:
            return "リターン向上、リスク適度増加"
        elif environment.regime == MarketRegime.VOLATILE:
            return "リスク軽減、リターン安定化"
        else:
            return "バランス調整、リスク・リターン最適化"

    def _get_default_adjustment(
        self, strategy_name: str, original_parameters: Dict[str, Any]
    ) -> StrategyAdjustment:
        """デフォルト調整の取得"""
        return StrategyAdjustment(
            strategy_name=strategy_name,
            original_parameters=original_parameters,
            adjusted_parameters=original_parameters,
            adjustment_reason="デフォルト設定",
            confidence_score=0.5,
            expected_impact="調整なし",
            risk_adjustment={"max_drawdown": 0.10},
            position_size_adjustment=1.0,
            stop_loss_adjustment=1.0,
            take_profit_adjustment=1.0,
            created_at=datetime.now(),
        )


class MarketEnvironmentStrategySystem:
    """市場環境戦略システム"""

    def __init__(self, unified_system: UnifiedSystem = None):
        self.unified_system = unified_system or UnifiedSystem()
        self.environment_analyzer = MarketEnvironmentAnalyzer(self.unified_system)
        self.strategy_adjuster = StrategyEnvironmentAdjuster(self.unified_system)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 履歴データ
        self.environment_history = []
        self.adjustment_history = []

        self.logger.info("🌍 市場環境戦略システム初期化完了")

    def analyze_and_adjust_strategies(
        self, symbol: str, data: pd.DataFrame, strategies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """戦略の分析と調整"""
        try:
            # 市場環境の分析
            environment = self.environment_analyzer.analyze_market_environment(data)
            self.environment_history.append(environment)

            # 各戦略の調整
            adjusted_strategies = {}

            for strategy in strategies:
                strategy_name = strategy.get("name", "unknown")
                original_parameters = strategy.get("parameters", {})

                # 戦略調整
                adjustment = self.strategy_adjuster.adjust_strategy_for_environment(
                    strategy_name, original_parameters, environment
                )

                adjusted_strategies[strategy_name] = {
                    "original": original_parameters,
                    "adjusted": adjustment.adjusted_parameters,
                    "adjustment": adjustment,
                }

            self.logger.info(
                f"📊 戦略調整完了: {symbol} - {environment.regime.value}環境"
            )

            return {
                "symbol": symbol,
                "environment": environment,
                "adjusted_strategies": adjusted_strategies,
                "analysis_timestamp": datetime.now(),
            }

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"戦略分析調整エラー: {symbol}",
            )
            return {"error": str(e)}

    def get_environment_summary(self) -> Dict[str, Any]:
        """環境サマリーの取得"""
        if not self.environment_history:
            return {"status": "no_data"}

        latest_environment = self.environment_history[-1]

        return {
            "current_regime": latest_environment.regime.value,
            "current_phase": latest_environment.phase.value,
            "risk_level": latest_environment.risk_level,
            "volatility_level": latest_environment.volatility_level,
            "sentiment_score": latest_environment.sentiment_score,
            "total_analyses": len(self.environment_history),
            "last_analysis": latest_environment.created_at.isoformat(),
        }

    def export_analysis_data(self, file_path: str) -> bool:
        """分析データのエクスポート"""
        try:
            export_data = {
                "environment_history": [
                    {
                        "regime": env.regime.value,
                        "phase": env.phase.value,
                        "risk_level": env.risk_level,
                        "volatility_level": env.volatility_level,
                        "sentiment_score": env.sentiment_score,
                        "created_at": env.created_at.isoformat(),
                    }
                    for env in self.environment_history
                ],
                "adjustment_history": [
                    {
                        "strategy_name": adj.strategy_name,
                        "adjustment_reason": adj.adjustment_reason,
                        "confidence_score": adj.confidence_score,
                        "expected_impact": adj.expected_impact,
                        "created_at": adj.created_at.isoformat(),
                    }
                    for adj in self.strategy_adjuster.adjustment_history
                ],
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, default=str, ensure_ascii=False, indent=2)

            self.logger.info(f"📊 分析データエクスポート完了: {file_path}")
            return True

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.FILE_ERROR,
                context=f"分析データエクスポートエラー: {file_path}",
            )
            return False


def main():
    """メイン実行関数"""
    try:
        # 統合システムの初期化
        unified_system = UnifiedSystem()

        # 市場環境戦略システムの初期化
        env_strategy_system = MarketEnvironmentStrategySystem(unified_system)

        # サンプルデータの取得
        symbol = "7203.T"
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="6mo")

        if data.empty:
            print("データが取得できませんでした")
            return

        # サンプル戦略
        strategies = [
            {
                "name": "momentum_strategy",
                "parameters": {
                    "lookback_period": 20,
                    "momentum_threshold": 0.05,
                    "position_size": 0.1,
                },
            },
            {
                "name": "mean_reversion_strategy",
                "parameters": {
                    "lookback_period": 20,
                    "std_threshold": 2.0,
                    "position_size": 0.08,
                },
            },
        ]

        print("=== 市場環境戦略システム ===")
        print(f"銘柄: {symbol}")
        print(f"データ期間: {data.index[0].date()} - {data.index[-1].date()}")

        # 戦略の分析と調整
        result = env_strategy_system.analyze_and_adjust_strategies(
            symbol, data, strategies
        )

        if "error" not in result:
            print(f"\n📊 市場環境分析結果:")
            env = result["environment"]
            print(f"  レジーム: {env.regime.value}")
            print(f"  フェーズ: {env.phase.value}")
            print(f"  リスクレベル: {env.risk_level}")
            print(f"  ボラティリティ: {env.volatility_level}")
            print(f"  センチメント: {env.sentiment_score:.2f}")

            print(f"\n🔧 戦略調整結果:")
            for strategy_name, strategy_data in result["adjusted_strategies"].items():
                adjustment = strategy_data["adjustment"]
                print(f"  {strategy_name}:")
                print(f"    調整理由: {adjustment.adjustment_reason}")
                print(f"    信頼度: {adjustment.confidence_score:.2f}")
                print(f"    期待インパクト: {adjustment.expected_impact}")
                print(
                    f"    ポジションサイズ調整: {adjustment.position_size_adjustment:.2f}"
                )

        # 環境サマリー
        summary = env_strategy_system.get_environment_summary()
        print(f"\n📈 環境サマリー:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

        # データエクスポート
        env_strategy_system.export_analysis_data("market_environment_analysis.json")
        print(f"\n分析データをエクスポートしました: market_environment_analysis.json")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
