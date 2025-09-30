#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投資スタイル別パラメータ最適化システム
Investment Style Parameter Optimization System

短期・中期・長期投資スタイルに応じたパラメータを動的に調整し、投資効率を向上させる
"""

import numpy as np
import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import yaml


class InvestmentStyle(Enum):
    """投資スタイル"""

    SHORT_TERM = "short_term"  # 短期投資（1-3ヶ月）
    MEDIUM_TERM = "medium_term"  # 中期投資（3-12ヶ月）
    LONG_TERM = "long_term"  # 長期投資（1年以上）


class MarketCondition(Enum):
    """市場環境"""

    BULL_MARKET = "bull_market"  # 強気市場
    BEAR_MARKET = "bear_market"  # 弱気市場
    SIDEWAYS_MARKET = "sideways_market"  # 横ばい市場
    VOLATILE_MARKET = "volatile_market"  # 高ボラティリティ市場


@dataclass
class StyleParameters:
    """投資スタイル別パラメータ"""

    # 基本設定
    holding_period_days: int = 30
    analysis_frequency: str = "daily"
    rebalance_frequency: str = "weekly"

    # リスク管理
    volatility_tolerance: float = 0.15
    max_position_size: float = 0.1
    stop_loss_percent: float = 5.0
    take_profit_percent: float = 10.0

    # 分析重み
    momentum_weight: float = 0.5
    mean_reversion_weight: float = 0.5
    technical_weight: float = 0.6
    fundamental_weight: float = 0.4

    # 技術指標パラメータ
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0

    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    sma_short: int = 5
    sma_medium: int = 25
    sma_long: int = 50

    bollinger_period: int = 20
    bollinger_std: float = 2.0

    # 市場環境適応
    market_adaptation: bool = True
    dynamic_thresholds: bool = True

    # パフォーマンス追跡
    performance_tracking: bool = True
    optimization_frequency: str = "monthly"


@dataclass
class MarketConditionProfile:
    """市場環境プロファイル"""

    condition: MarketCondition
    volatility_multiplier: float = 1.0
    momentum_adjustment: float = 1.0
    risk_adjustment: float = 1.0
    threshold_adjustments: Dict[str, float] = field(default_factory=dict)


@dataclass
class StyleOptimizationResult:
    """スタイル最適化結果"""

    symbol: str
    current_style: InvestmentStyle
    optimized_style: InvestmentStyle
    style_confidence: float
    parameter_adjustments: Dict[str, Any]
    expected_performance_improvement: float
    optimization_timestamp: datetime
    market_condition: MarketCondition


class InvestmentStyleOptimizer:
    """投資スタイル最適化システム"""

    def __init__(self, config_file: str = "investment_style_config.yaml"):
        self.config_file = config_file
        self.style_parameters: Dict[InvestmentStyle, StyleParameters] = {}
        self.market_conditions: Dict[MarketCondition, MarketConditionProfile] = {}
        self.optimization_history: List[StyleOptimizationResult] = []
        self.logger = logging.getLogger(__name__)
        self._initialize_default_parameters()
        self._load_config()

    def _initialize_default_parameters(self) -> None:
        """デフォルトパラメータを初期化"""
        # 短期投資パラメータ
        self.style_parameters[InvestmentStyle.SHORT_TERM] = StyleParameters(
            holding_period_days=30,
            analysis_frequency="daily",
            rebalance_frequency="weekly",
            volatility_tolerance=0.20,
            max_position_size=0.15,
            stop_loss_percent=3.0,
            take_profit_percent=8.0,
            momentum_weight=0.7,
            mean_reversion_weight=0.3,
            technical_weight=0.8,
            fundamental_weight=0.2,
            rsi_period=10,
            rsi_overbought=75.0,
            rsi_oversold=25.0,
            macd_fast=8,
            macd_slow=21,
            macd_signal=5,
            sma_short=3,
            sma_medium=10,
            sma_long=20,
            bollinger_period=15,
            bollinger_std=1.5,
        )

        # 中期投資パラメータ
        self.style_parameters[InvestmentStyle.MEDIUM_TERM] = StyleParameters(
            holding_period_days=180,
            analysis_frequency="weekly",
            rebalance_frequency="monthly",
            volatility_tolerance=0.15,
            max_position_size=0.12,
            stop_loss_percent=5.0,
            take_profit_percent=12.0,
            momentum_weight=0.5,
            mean_reversion_weight=0.5,
            technical_weight=0.6,
            fundamental_weight=0.4,
            rsi_period=14,
            rsi_overbought=70.0,
            rsi_oversold=30.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9,
            sma_short=5,
            sma_medium=25,
            sma_long=50,
            bollinger_period=20,
            bollinger_std=2.0,
        )

        # 長期投資パラメータ
        self.style_parameters[InvestmentStyle.LONG_TERM] = StyleParameters(
            holding_period_days=365,
            analysis_frequency="monthly",
            rebalance_frequency="quarterly",
            volatility_tolerance=0.10,
            max_position_size=0.08,
            stop_loss_percent=8.0,
            take_profit_percent=20.0,
            momentum_weight=0.3,
            mean_reversion_weight=0.7,
            technical_weight=0.4,
            fundamental_weight=0.6,
            rsi_period=21,
            rsi_overbought=65.0,
            rsi_oversold=35.0,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9,
            sma_short=10,
            sma_medium=50,
            sma_long=200,
            bollinger_period=30,
            bollinger_std=2.5,
        )

        # 市場環境プロファイル
        self.market_conditions[MarketCondition.BULL_MARKET] = MarketConditionProfile(
            condition=MarketCondition.BULL_MARKET,
            volatility_multiplier=0.8,
            momentum_adjustment=1.2,
            risk_adjustment=0.9,
            threshold_adjustments={
                "rsi_overbought": 0.9,
                "rsi_oversold": 1.1,
                "take_profit": 1.1,
            },
        )

        self.market_conditions[MarketCondition.BEAR_MARKET] = MarketConditionProfile(
            condition=MarketCondition.BEAR_MARKET,
            volatility_multiplier=1.3,
            momentum_adjustment=0.8,
            risk_adjustment=1.2,
            threshold_adjustments={
                "rsi_overbought": 1.1,
                "rsi_oversold": 0.9,
                "stop_loss": 0.8,
            },
        )

        self.market_conditions[
            MarketCondition.SIDEWAYS_MARKET
        ] = MarketConditionProfile(
            condition=MarketCondition.SIDEWAYS_MARKET,
            volatility_multiplier=1.0,
            momentum_adjustment=0.9,
            risk_adjustment=1.0,
            threshold_adjustments={
                "mean_reversion_weight": 1.2,
                "momentum_weight": 0.8,
            },
        )

        self.market_conditions[
            MarketCondition.VOLATILE_MARKET
        ] = MarketConditionProfile(
            condition=MarketCondition.VOLATILE_MARKET,
            volatility_multiplier=1.5,
            momentum_adjustment=1.1,
            risk_adjustment=1.3,
            threshold_adjustments={
                "volatility_tolerance": 1.2,
                "stop_loss": 1.2,
                "take_profit": 1.1,
            },
        )

    def _load_config(self) -> None:
        """設定ファイルを読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                # スタイルパラメータの読み込み
                if "style_parameters" in data:
                    for style_name, params in data["style_parameters"].items():
                        style = InvestmentStyle(style_name)
                        self.style_parameters[style] = StyleParameters(**params)

                # 市場環境プロファイルの読み込み
                if "market_conditions" in data:
                    for condition_name, profile in data["market_conditions"].items():
                        condition = MarketCondition(condition_name)
                        self.market_conditions[condition] = MarketConditionProfile(
                            **profile
                        )

                self.logger.info("投資スタイル設定を読み込み完了")
            else:
                self._save_config()
                self.logger.info("デフォルト投資スタイル設定を作成")

        except Exception as e:
            self.logger.error(f"投資スタイル設定の読み込みエラー: {e}")
            self._save_config()

    def _save_config(self) -> None:
        """設定をファイルに保存"""
        try:
            data = {
                "style_parameters": {
                    style.value: {
                        "holding_period_days": params.holding_period_days,
                        "analysis_frequency": params.analysis_frequency,
                        "rebalance_frequency": params.rebalance_frequency,
                        "volatility_tolerance": params.volatility_tolerance,
                        "max_position_size": params.max_position_size,
                        "stop_loss_percent": params.stop_loss_percent,
                        "take_profit_percent": params.take_profit_percent,
                        "momentum_weight": params.momentum_weight,
                        "mean_reversion_weight": params.mean_reversion_weight,
                        "technical_weight": params.technical_weight,
                        "fundamental_weight": params.fundamental_weight,
                        "rsi_period": params.rsi_period,
                        "rsi_overbought": params.rsi_overbought,
                        "rsi_oversold": params.rsi_oversold,
                        "macd_fast": params.macd_fast,
                        "macd_slow": params.macd_slow,
                        "macd_signal": params.macd_signal,
                        "sma_short": params.sma_short,
                        "sma_medium": params.sma_medium,
                        "sma_long": params.sma_long,
                        "bollinger_period": params.bollinger_period,
                        "bollinger_std": params.bollinger_std,
                        "market_adaptation": params.market_adaptation,
                        "dynamic_thresholds": params.dynamic_thresholds,
                        "performance_tracking": params.performance_tracking,
                        "optimization_frequency": params.optimization_frequency,
                    }
                    for style, params in self.style_parameters.items()
                },
                "market_conditions": {
                    condition.value: {
                        "condition": condition.value,
                        "volatility_multiplier": profile.volatility_multiplier,
                        "momentum_adjustment": profile.momentum_adjustment,
                        "risk_adjustment": profile.risk_adjustment,
                        "threshold_adjustments": profile.threshold_adjustments,
                    }
                    for condition, profile in self.market_conditions.items()
                },
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

            self.logger.info(f"投資スタイル設定を保存: {self.config_file}")

        except Exception as e:
            self.logger.error(f"投資スタイル設定の保存エラー: {e}")

    def detect_market_condition(self, market_data: pd.DataFrame) -> MarketCondition:
        """市場環境を検出"""
        try:
            if market_data.empty or len(market_data) < 30:
                return MarketCondition.SIDEWAYS_MARKET

            # リターンの計算
            returns = market_data["Close"].pct_change().dropna()

            # ボラティリティの計算
            volatility = returns.std() * np.sqrt(252)

            # トレンドの計算
            sma_short = market_data["Close"].rolling(window=20).mean()
            sma_long = market_data["Close"].rolling(window=50).mean()
            trend = (sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1]

            # モメンタムの計算
            momentum = (
                market_data["Close"].iloc[-1] - market_data["Close"].iloc[-20]
            ) / market_data["Close"].iloc[-20]

            # 市場環境の判定
            if volatility > 0.25:  # 高ボラティリティ
                return MarketCondition.VOLATILE_MARKET
            elif trend > 0.05 and momentum > 0.1:  # 強い上昇トレンド
                return MarketCondition.BULL_MARKET
            elif trend < -0.05 and momentum < -0.1:  # 強い下降トレンド
                return MarketCondition.BEAR_MARKET
            else:  # 横ばい
                return MarketCondition.SIDEWAYS_MARKET

        except Exception as e:
            self.logger.error(f"市場環境検出エラー: {e}")
            return MarketCondition.SIDEWAYS_MARKET

    def optimize_style_parameters(
        self,
        symbol: str,
        current_style: InvestmentStyle,
        price_data: pd.DataFrame,
        market_data: pd.DataFrame,
    ) -> StyleOptimizationResult:
        """投資スタイルパラメータを最適化"""
        try:
            # 市場環境を検出
            market_condition = self.detect_market_condition(market_data)

            # 現在のスタイルパラメータを取得
            current_params = self.style_parameters[current_style]

            # 市場環境に応じた調整
            market_profile = self.market_conditions[market_condition]
            adjusted_params = self._adjust_parameters_for_market(
                current_params, market_profile
            )

            # 最適な投資スタイルを決定
            optimal_style = self._determine_optimal_style(price_data, market_condition)

            # スタイル信頼度を計算
            style_confidence = self._calculate_style_confidence(
                price_data, optimal_style
            )

            # パラメータ調整を計算
            parameter_adjustments = self._calculate_parameter_adjustments(
                current_params, adjusted_params, optimal_style
            )

            # 期待パフォーマンス改善を計算
            performance_improvement = self._calculate_performance_improvement(
                current_style, optimal_style, style_confidence
            )

            # 最適化結果を作成
            result = StyleOptimizationResult(
                symbol=symbol,
                current_style=current_style,
                optimized_style=optimal_style,
                style_confidence=style_confidence,
                parameter_adjustments=parameter_adjustments,
                expected_performance_improvement=performance_improvement,
                optimization_timestamp=datetime.now(),
                market_condition=market_condition,
            )

            # 最適化履歴に追加
            self.optimization_history.append(result)

            return result

        except Exception as e:
            self.logger.error(f"銘柄 {symbol} のスタイル最適化エラー: {e}")
            return None

    def _adjust_parameters_for_market(
        self, params: StyleParameters, market_profile: MarketConditionProfile
    ) -> StyleParameters:
        """市場環境に応じてパラメータを調整"""
        adjusted_params = StyleParameters(
            holding_period_days=params.holding_period_days,
            analysis_frequency=params.analysis_frequency,
            rebalance_frequency=params.rebalance_frequency,
            volatility_tolerance=params.volatility_tolerance
            * market_profile.volatility_multiplier,
            max_position_size=params.max_position_size / market_profile.risk_adjustment,
            stop_loss_percent=params.stop_loss_percent
            * market_profile.threshold_adjustments.get("stop_loss", 1.0),
            take_profit_percent=params.take_profit_percent
            * market_profile.threshold_adjustments.get("take_profit", 1.0),
            momentum_weight=params.momentum_weight * market_profile.momentum_adjustment,
            mean_reversion_weight=params.mean_reversion_weight
            * market_profile.threshold_adjustments.get("mean_reversion_weight", 1.0),
            technical_weight=params.technical_weight,
            fundamental_weight=params.fundamental_weight,
            rsi_period=params.rsi_period,
            rsi_overbought=params.rsi_overbought
            * market_profile.threshold_adjustments.get("rsi_overbought", 1.0),
            rsi_oversold=params.rsi_oversold
            * market_profile.threshold_adjustments.get("rsi_oversold", 1.0),
            macd_fast=params.macd_fast,
            macd_slow=params.macd_slow,
            macd_signal=params.macd_signal,
            sma_short=params.sma_short,
            sma_medium=params.sma_medium,
            sma_long=params.sma_long,
            bollinger_period=params.bollinger_period,
            bollinger_std=params.bollinger_std,
            market_adaptation=params.market_adaptation,
            dynamic_thresholds=params.dynamic_thresholds,
            performance_tracking=params.performance_tracking,
            optimization_frequency=params.optimization_frequency,
        )

        return adjusted_params

    def _determine_optimal_style(
        self, price_data: pd.DataFrame, market_condition: MarketCondition
    ) -> InvestmentStyle:
        """最適な投資スタイルを決定"""
        try:
            if price_data.empty or len(price_data) < 30:
                return InvestmentStyle.MEDIUM_TERM

            # ボラティリティの計算
            returns = price_data["Close"].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)

            # トレンドの強さを計算
            sma_short = price_data["Close"].rolling(window=20).mean()
            sma_long = price_data["Close"].rolling(window=50).mean()
            trend_strength = (
                abs(sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1]
            )

            # モメンタムの計算
            momentum = (
                price_data["Close"].iloc[-1] - price_data["Close"].iloc[-20]
            ) / price_data["Close"].iloc[-20]

            # 投資スタイルの決定ロジック
            if market_condition == MarketCondition.VOLATILE_MARKET:
                # 高ボラティリティ市場では短期投資が適している
                return InvestmentStyle.SHORT_TERM
            elif volatility > 0.25 and abs(momentum) > 0.15:
                # 高ボラティリティで強いモメンタムがある場合は短期投資
                return InvestmentStyle.SHORT_TERM
            elif volatility < 0.15 and trend_strength < 0.05:
                # 低ボラティリティでトレンドが弱い場合は長期投資
                return InvestmentStyle.LONG_TERM
            elif market_condition == MarketCondition.BULL_MARKET:
                # 強気市場では長期投資が適している
                return InvestmentStyle.LONG_TERM
            elif market_condition == MarketCondition.BEAR_MARKET:
                # 弱気市場では短期投資が適している
                return InvestmentStyle.SHORT_TERM
            else:
                # その他の場合は中期投資
                return InvestmentStyle.MEDIUM_TERM

        except Exception as e:
            self.logger.error(f"最適投資スタイル決定エラー: {e}")
            return InvestmentStyle.MEDIUM_TERM

    def _calculate_style_confidence(
        self, price_data: pd.DataFrame, style: InvestmentStyle
    ) -> float:
        """スタイル信頼度を計算"""
        try:
            if price_data.empty or len(price_data) < 30:
                return 0.5

            # スタイル別の適性指標を計算
            returns = price_data["Close"].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)

            if style == InvestmentStyle.SHORT_TERM:
                # 短期投資の適性：高ボラティリティ、強いモメンタム
                momentum = (
                    price_data["Close"].iloc[-1] - price_data["Close"].iloc[-5]
                ) / price_data["Close"].iloc[-5]
                confidence = (
                    min(volatility / 0.3, 1.0) * 0.5
                    + min(abs(momentum) / 0.1, 1.0) * 0.5
                )

            elif style == InvestmentStyle.LONG_TERM:
                # 長期投資の適性：低ボラティリティ、安定したトレンド
                sma_short = price_data["Close"].rolling(window=20).mean()
                sma_long = price_data["Close"].rolling(window=50).mean()
                trend_consistency = (
                    1.0
                    - abs(sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1]
                )
                confidence = (
                    1.0 - min(volatility / 0.2, 1.0)
                ) * 0.5 + trend_consistency * 0.5

            else:  # MEDIUM_TERM
                # 中期投資の適性：中程度のボラティリティ、バランス
                confidence = 1.0 - abs(volatility - 0.15) / 0.15

            return max(0.0, min(1.0, confidence))

        except Exception as e:
            self.logger.error(f"スタイル信頼度計算エラー: {e}")
            return 0.5

    def _calculate_parameter_adjustments(
        self,
        current_params: StyleParameters,
        adjusted_params: StyleParameters,
        optimal_style: InvestmentStyle,
    ) -> Dict[str, Any]:
        """パラメータ調整を計算"""
        optimal_params = self.style_parameters[optimal_style]

        adjustments = {
            "holding_period_change": optimal_params.holding_period_days
            - current_params.holding_period_days,
            "volatility_tolerance_change": adjusted_params.volatility_tolerance
            - current_params.volatility_tolerance,
            "max_position_size_change": optimal_params.max_position_size
            - current_params.max_position_size,
            "stop_loss_change": optimal_params.stop_loss_percent
            - current_params.stop_loss_percent,
            "take_profit_change": optimal_params.take_profit_percent
            - current_params.take_profit_percent,
            "momentum_weight_change": adjusted_params.momentum_weight
            - current_params.momentum_weight,
            "mean_reversion_weight_change": adjusted_params.mean_reversion_weight
            - current_params.mean_reversion_weight,
            "rsi_threshold_adjustment": {
                "overbought": optimal_params.rsi_overbought
                - current_params.rsi_overbought,
                "oversold": optimal_params.rsi_oversold - current_params.rsi_oversold,
            },
        }

        return adjustments

    def _calculate_performance_improvement(
        self,
        current_style: InvestmentStyle,
        optimal_style: InvestmentStyle,
        confidence: float,
    ) -> float:
        """期待パフォーマンス改善を計算"""
        # スタイル適性スコア
        style_scores = {
            InvestmentStyle.SHORT_TERM: 0.7,
            InvestmentStyle.MEDIUM_TERM: 0.8,
            InvestmentStyle.LONG_TERM: 0.6,
        }

        current_score = style_scores.get(current_style, 0.5)
        optimal_score = style_scores.get(optimal_style, 0.5)

        # 信頼度を考慮した改善度
        improvement = (optimal_score - current_score) * confidence * 0.3  # 最大30%の改善

        return max(0.0, improvement)

    def get_style_parameters(self, style: InvestmentStyle) -> StyleParameters:
        """指定スタイルのパラメータを取得"""
        return self.style_parameters.get(
            style, self.style_parameters[InvestmentStyle.MEDIUM_TERM]
        )

    def update_style_parameters(self, style: InvestmentStyle, **kwargs) -> bool:
        """スタイルパラメータを更新"""
        if style not in self.style_parameters:
            return False

        params = self.style_parameters[style]

        for key, value in kwargs.items():
            if hasattr(params, key):
                setattr(params, key, value)

        self._save_config()
        self.logger.info(f"投資スタイル {style.value} のパラメータを更新")
        return True

    def get_optimization_summary(self) -> Dict[str, Any]:
        """最適化要約を取得"""
        if not self.optimization_history:
            return {}

        total_optimizations = len(self.optimization_history)
        style_changes = sum(
            1
            for result in self.optimization_history
            if result.current_style != result.optimized_style
        )

        avg_confidence = np.mean(
            [result.style_confidence for result in self.optimization_history]
        )
        avg_improvement = np.mean(
            [
                result.expected_performance_improvement
                for result in self.optimization_history
            ]
        )

        style_distribution = {}
        for style in InvestmentStyle:
            count = sum(
                1
                for result in self.optimization_history
                if result.optimized_style == style
            )
            style_distribution[style.value] = count / total_optimizations

        market_condition_distribution = {}
        for condition in MarketCondition:
            count = sum(
                1
                for result in self.optimization_history
                if result.market_condition == condition
            )
            market_condition_distribution[condition.value] = count / total_optimizations

        return {
            "total_optimizations": total_optimizations,
            "style_changes": style_changes,
            "change_rate": (
                style_changes / total_optimizations if total_optimizations > 0 else 0
            ),
            "average_confidence": avg_confidence,
            "average_improvement": avg_improvement,
            "style_distribution": style_distribution,
            "market_condition_distribution": market_condition_distribution,
            "recent_optimizations": [
                {
                    "symbol": result.symbol,
                    "current_style": result.current_style.value,
                    "optimized_style": result.optimized_style.value,
                    "confidence": result.style_confidence,
                    "improvement": result.expected_performance_improvement,
                    "timestamp": result.optimization_timestamp.isoformat(),
                }
                for result in self.optimization_history[-10:]  # 最新10件
            ],
        }


def main():
    """メイン実行関数"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 投資スタイル最適化システムの初期化
    optimizer = InvestmentStyleOptimizer()

    # 各投資スタイルのパラメータを表示
    print("=== 投資スタイル別パラメータ ===")
    for style in InvestmentStyle:
        params = optimizer.get_style_parameters(style)
        print(f"\n{style.value}:")
        print(f"  保有期間: {params.holding_period_days}日")
        print(f"  分析頻度: {params.analysis_frequency}")
        print(f"  リバランス頻度: {params.rebalance_frequency}")
        print(f"  ボラティリティ許容度: {params.volatility_tolerance:.1%}")
        print(f"  最大ポジションサイズ: {params.max_position_size:.1%}")
        print(f"  ストップロス: {params.stop_loss_percent:.1f}%")
        print(f"  利確: {params.take_profit_percent:.1f}%")
        print(f"  モメンタム重み: {params.momentum_weight:.1f}")
        print(f"  平均回帰重み: {params.mean_reversion_weight:.1f}")

    # 市場環境プロファイルを表示
    print("\n=== 市場環境プロファイル ===")
    for condition in MarketCondition:
        profile = optimizer.market_conditions[condition]
        print(f"\n{condition.value}:")
        print(f"  ボラティリティ倍率: {profile.volatility_multiplier:.1f}")
        print(f"  モメンタム調整: {profile.momentum_adjustment:.1f}")
        print(f"  リスク調整: {profile.risk_adjustment:.1f}")


if __name__ == "__main__":
    main()
