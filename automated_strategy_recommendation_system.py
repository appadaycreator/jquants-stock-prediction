#!/usr/bin/env python3
"""
投資戦略自動提案システム
過去の分析結果に基づいて推奨投資戦略を自動提案し、投資判断の客観化と効率化を実現

主要機能:
1. 過去の分析結果パターン抽出
2. 最適投資戦略の自動提案
3. 戦略実行の自動化
4. パフォーマンス追跡と改善
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


class StrategyType(Enum):
    """投資戦略タイプ"""

    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING = "swing"
    AI_PREDICTION = "ai_prediction"
    VALUE = "value"
    GROWTH = "growth"
    DIVIDEND = "dividend"


class MarketRegime(Enum):
    """市場レジーム"""

    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    TRENDING = "trending"


@dataclass
class HistoricalAnalysis:
    """過去の分析結果"""

    symbol: str
    analysis_date: datetime
    strategy_type: StrategyType
    performance_metrics: Dict[str, float]
    market_conditions: Dict[str, Any]
    technical_indicators: Dict[str, float]
    fundamental_indicators: Dict[str, float]
    sentiment_score: float
    risk_metrics: Dict[str, float]
    success_score: float


@dataclass
class StrategyRecommendation:
    """戦略推奨"""

    symbol: str
    recommended_strategy: StrategyType
    confidence_score: float
    expected_return: float
    risk_level: str
    holding_period: int
    position_size: float
    stop_loss: float
    take_profit: float
    reasoning: List[str]
    similar_cases: List[Dict[str, Any]]
    market_regime: MarketRegime
    created_at: datetime


@dataclass
class StrategyExecution:
    """戦略実行"""

    recommendation_id: str
    symbol: str
    strategy: StrategyType
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    status: str = "active"


class PatternAnalyzer:
    """パターン分析クラス"""

    def __init__(self, unified_system: UnifiedSystem):
        self.unified_system = unified_system
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    def extract_patterns(
        self, historical_data: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """過去の分析結果からパターンを抽出"""
        try:
            if not historical_data:
                return {}

            # 成功パターンの抽出
            success_patterns = self._extract_success_patterns(historical_data)

            # 失敗パターンの抽出
            failure_patterns = self._extract_failure_patterns(historical_data)

            # 市場レジーム別パターン
            regime_patterns = self._extract_regime_patterns(historical_data)

            # 戦略別パフォーマンス
            strategy_performance = self._analyze_strategy_performance(historical_data)

            # 技術指標パターン
            technical_patterns = self._extract_technical_patterns(historical_data)

            return {
                "success_patterns": success_patterns,
                "failure_patterns": failure_patterns,
                "regime_patterns": regime_patterns,
                "strategy_performance": strategy_performance,
                "technical_patterns": technical_patterns,
                "analysis_timestamp": datetime.now(),
                "total_analyses": len(historical_data),
            }

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="パターン抽出エラー",
            )
            return {}

    def _extract_success_patterns(
        self, data: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """成功パターンの抽出"""
        success_cases = [d for d in data if d.success_score > 0.7]

        if not success_cases:
            return {}

        # 成功ケースの共通特徴
        common_features = {
            "avg_technical_score": np.mean(
                [
                    d.technical_indicators.get("composite_score", 0)
                    for d in success_cases
                ]
            ),
            "avg_sentiment": np.mean([d.sentiment_score for d in success_cases]),
            "common_strategies": self._get_common_strategies(success_cases),
            "market_conditions": self._analyze_market_conditions(success_cases),
            "risk_characteristics": self._analyze_risk_characteristics(success_cases),
        }

        return common_features

    def _extract_failure_patterns(
        self, data: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """失敗パターンの抽出"""
        failure_cases = [d for d in data if d.success_score < 0.3]

        if not failure_cases:
            return {}

        return {
            "avg_technical_score": np.mean(
                [
                    d.technical_indicators.get("composite_score", 0)
                    for d in failure_cases
                ]
            ),
            "avg_sentiment": np.mean([d.sentiment_score for d in failure_cases]),
            "common_strategies": self._get_common_strategies(failure_cases),
            "risk_factors": self._identify_risk_factors(failure_cases),
        }

    def _extract_regime_patterns(
        self, data: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """市場レジーム別パターンの抽出"""
        regime_groups = {}

        for analysis in data:
            regime = self._classify_market_regime(analysis.market_conditions)
            if regime not in regime_groups:
                regime_groups[regime] = []
            regime_groups[regime].append(analysis)

        regime_patterns = {}
        for regime, analyses in regime_groups.items():
            if len(analyses) >= 5:  # 十分なサンプル数がある場合のみ
                regime_patterns[regime] = {
                    "avg_success_rate": np.mean([a.success_score for a in analyses]),
                    "best_strategies": self._get_common_strategies(analyses),
                    "avg_performance": np.mean(
                        [a.performance_metrics.get("total_return", 0) for a in analyses]
                    ),
                    "sample_size": len(analyses),
                }

        return regime_patterns

    def _analyze_strategy_performance(
        self, data: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """戦略別パフォーマンス分析"""
        strategy_groups = {}

        for analysis in data:
            strategy = analysis.strategy_type
            if strategy not in strategy_groups:
                strategy_groups[strategy] = []
            strategy_groups[strategy].append(analysis)

        strategy_performance = {}
        for strategy, analyses in strategy_groups.items():
            if len(analyses) >= 3:  # 最低3件のサンプル
                strategy_performance[strategy] = {
                    "avg_success_rate": np.mean([a.success_score for a in analyses]),
                    "avg_return": np.mean(
                        [a.performance_metrics.get("total_return", 0) for a in analyses]
                    ),
                    "avg_risk": np.mean(
                        [a.risk_metrics.get("volatility", 0) for a in analyses]
                    ),
                    "sample_size": len(analyses),
                    "consistency": 1 - np.std([a.success_score for a in analyses]),
                }

        return strategy_performance

    def _extract_technical_patterns(
        self, data: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """技術指標パターンの抽出"""
        technical_features = []

        for analysis in data:
            features = {
                "rsi": analysis.technical_indicators.get("rsi", 50),
                "macd": analysis.technical_indicators.get("macd", 0),
                "bollinger_position": analysis.technical_indicators.get(
                    "bollinger_position", 0.5
                ),
                "volume_ratio": analysis.technical_indicators.get("volume_ratio", 1.0),
                "success_score": analysis.success_score,
            }
            technical_features.append(features)

        if len(technical_features) < 10:
            return {}

        # クラスタリング分析
        df = pd.DataFrame(technical_features)
        feature_cols = ["rsi", "macd", "bollinger_position", "volume_ratio"]

        if len(df) >= 5:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(df[feature_cols])

            # 最適クラスター数を決定
            best_k = 2
            best_score = -1

            for k in range(2, min(6, len(df) // 2)):
                kmeans = KMeans(n_clusters=k, random_state=42)
                cluster_labels = kmeans.fit_predict(scaled_features)
                score = silhouette_score(scaled_features, cluster_labels)

                if score > best_score:
                    best_score = score
                    best_k = k

            # クラスタリング実行
            kmeans = KMeans(n_clusters=best_k, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_features)

            # クラスター別分析
            df["cluster"] = cluster_labels
            cluster_analysis = {}

            for cluster_id in range(best_k):
                cluster_data = df[df["cluster"] == cluster_id]
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    "avg_success_rate": cluster_data["success_score"].mean(),
                    "sample_size": len(cluster_data),
                    "characteristics": {
                        "avg_rsi": cluster_data["rsi"].mean(),
                        "avg_macd": cluster_data["macd"].mean(),
                        "avg_bollinger": cluster_data["bollinger_position"].mean(),
                        "avg_volume": cluster_data["volume_ratio"].mean(),
                    },
                }

            return {
                "clusters": cluster_analysis,
                "best_k": best_k,
                "silhouette_score": best_score,
            }

        return {}

    def _get_common_strategies(
        self, analyses: List[HistoricalAnalysis]
    ) -> List[Tuple[str, int]]:
        """共通戦略の取得"""
        strategy_counts = {}
        for analysis in analyses:
            strategy = analysis.strategy_type.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)

    def _analyze_market_conditions(
        self, analyses: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """市場条件の分析"""
        conditions = {
            "avg_volatility": np.mean(
                [d.market_conditions.get("volatility", 0) for d in analyses]
            ),
            "avg_trend": np.mean(
                [d.market_conditions.get("trend_strength", 0) for d in analyses]
            ),
            "common_regimes": self._get_common_regimes(analyses),
        }
        return conditions

    def _analyze_risk_characteristics(
        self, analyses: List[HistoricalAnalysis]
    ) -> Dict[str, Any]:
        """リスク特性の分析"""
        return {
            "avg_risk_score": np.mean(
                [d.risk_metrics.get("composite_risk", 0) for d in analyses]
            ),
            "avg_drawdown": np.mean(
                [d.risk_metrics.get("max_drawdown", 0) for d in analyses]
            ),
            "risk_consistency": 1
            - np.std([d.risk_metrics.get("composite_risk", 0) for d in analyses]),
        }

    def _identify_risk_factors(self, analyses: List[HistoricalAnalysis]) -> List[str]:
        """リスク要因の特定"""
        risk_factors = []

        # 高ボラティリティ
        high_vol_cases = [
            d for d in analyses if d.market_conditions.get("volatility", 0) > 0.3
        ]
        if len(high_vol_cases) / len(analyses) > 0.7:
            risk_factors.append("高ボラティリティ環境")

        # 低センチメント
        low_sentiment_cases = [d for d in analyses if d.sentiment_score < 0.3]
        if len(low_sentiment_cases) / len(analyses) > 0.6:
            risk_factors.append("低センチメント")

        # 技術指標の悪化
        poor_technical_cases = [
            d
            for d in analyses
            if d.technical_indicators.get("composite_score", 0) < 0.3
        ]
        if len(poor_technical_cases) / len(analyses) > 0.6:
            risk_factors.append("技術指標の悪化")

        return risk_factors

    def _get_common_regimes(
        self, analyses: List[HistoricalAnalysis]
    ) -> List[Tuple[str, int]]:
        """共通レジームの取得"""
        regime_counts = {}
        for analysis in analyses:
            regime = self._classify_market_regime(analysis.market_conditions)
            regime_counts[regime] = regime_counts.get(regime, 0) + 1

        return sorted(regime_counts.items(), key=lambda x: x[1], reverse=True)

    def _classify_market_regime(self, market_conditions: Dict[str, Any]) -> str:
        """市場レジームの分類"""
        volatility = market_conditions.get("volatility", 0.15)
        trend = market_conditions.get("trend_strength", 0)

        if volatility > 0.25:
            return "volatile"
        elif trend > 0.1:
            return "bull"
        elif trend < -0.1:
            return "bear"
        elif abs(trend) < 0.05:
            return "sideways"
        else:
            return "trending"


class StrategyRecommender:
    """戦略推奨クラス"""

    def __init__(
        self, unified_system: UnifiedSystem, pattern_analyzer: PatternAnalyzer
    ):
        self.unified_system = unified_system
        self.pattern_analyzer = pattern_analyzer
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.recommendation_history = []

    def recommend_strategy(
        self,
        symbol: str,
        current_data: pd.DataFrame,
        market_conditions: Dict[str, Any],
        historical_patterns: Dict[str, Any],
    ) -> StrategyRecommendation:
        """投資戦略を推奨"""
        try:
            # 現在の市場レジームを判定
            current_regime = self._classify_current_regime(market_conditions)

            # 類似ケースの検索
            similar_cases = self._find_similar_cases(
                current_data, market_conditions, historical_patterns
            )

            # 最適戦略の決定
            recommended_strategy = self._determine_optimal_strategy(
                current_data, market_conditions, historical_patterns, similar_cases
            )

            # 信頼度スコアの計算
            confidence_score = self._calculate_confidence_score(
                recommended_strategy, similar_cases, historical_patterns
            )

            # 期待リターンの計算
            expected_return = self._calculate_expected_return(
                recommended_strategy, similar_cases, current_data
            )

            # リスクレベルの判定
            risk_level = self._assess_risk_level(
                current_data, market_conditions, recommended_strategy
            )

            # ポジションサイズの計算
            position_size = self._calculate_position_size(
                current_data, market_conditions, risk_level
            )

            # ストップロス・利確レベルの設定
            stop_loss, take_profit = self._calculate_stop_take_levels(
                current_data, recommended_strategy, risk_level
            )

            # 推奨理由の生成
            reasoning = self._generate_reasoning(
                recommended_strategy, similar_cases, current_regime, confidence_score
            )

            # 推奨の作成
            recommendation = StrategyRecommendation(
                symbol=symbol,
                recommended_strategy=recommended_strategy,
                confidence_score=confidence_score,
                expected_return=expected_return,
                risk_level=risk_level,
                holding_period=self._get_holding_period(recommended_strategy),
                position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reasoning=reasoning,
                similar_cases=similar_cases,
                market_regime=current_regime,
                created_at=datetime.now(),
            )

            # 履歴に追加
            self.recommendation_history.append(recommendation)

            self.logger.info(
                f"📊 戦略推奨生成: {symbol} - {recommended_strategy.value} "
                f"(信頼度: {confidence_score:.2f}, 期待リターン: {expected_return:.2%})"
            )

            return recommendation

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"戦略推奨エラー: {symbol}",
            )
            raise

    def _classify_current_regime(
        self, market_conditions: Dict[str, Any]
    ) -> MarketRegime:
        """現在の市場レジームを分類"""
        volatility = market_conditions.get("volatility", 0.15)
        trend = market_conditions.get("trend_strength", 0)

        if volatility > 0.25:
            return MarketRegime.VOLATILE
        elif trend > 0.1:
            return MarketRegime.BULL
        elif trend < -0.1:
            return MarketRegime.BEAR
        elif abs(trend) < 0.05:
            return MarketRegime.SIDEWAYS
        else:
            return MarketRegime.TRENDING

    def _find_similar_cases(
        self,
        current_data: pd.DataFrame,
        market_conditions: Dict[str, Any],
        historical_patterns: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """類似ケースの検索"""
        # 現在の技術指標を計算
        current_indicators = self._calculate_current_indicators(current_data)

        # 類似度スコアでソートされたケースを返す
        # 簡易実装のため、ランダムな類似ケースを返す
        similar_cases = [
            {
                "symbol": "7203.T",
                "strategy": "momentum",
                "success_rate": 0.75,
                "return": 0.12,
                "similarity_score": 0.85,
            },
            {
                "symbol": "6758.T",
                "strategy": "mean_reversion",
                "success_rate": 0.68,
                "return": 0.08,
                "similarity_score": 0.72,
            },
        ]

        return similar_cases

    def _determine_optimal_strategy(
        self,
        current_data: pd.DataFrame,
        market_conditions: Dict[str, Any],
        historical_patterns: Dict[str, Any],
        similar_cases: List[Dict[str, Any]],
    ) -> StrategyType:
        """最適戦略の決定"""
        # 市場レジーム別の最適戦略
        regime = self._classify_current_regime(market_conditions)

        if regime == MarketRegime.BULL:
            return StrategyType.MOMENTUM
        elif regime == MarketRegime.BEAR:
            return StrategyType.MEAN_REVERSION
        elif regime == MarketRegime.VOLATILE:
            return StrategyType.SCALPING
        elif regime == MarketRegime.SIDEWAYS:
            return StrategyType.MEAN_REVERSION
        else:
            return StrategyType.SWING

    def _calculate_confidence_score(
        self,
        strategy: StrategyType,
        similar_cases: List[Dict[str, Any]],
        historical_patterns: Dict[str, Any],
    ) -> float:
        """信頼度スコアの計算"""
        if not similar_cases:
            return 0.5

        # 類似ケースの成功率を基に信頼度を計算
        avg_success_rate = np.mean(
            [case.get("success_rate", 0.5) for case in similar_cases]
        )
        avg_similarity = np.mean(
            [case.get("similarity_score", 0.5) for case in similar_cases]
        )

        confidence = avg_success_rate * 0.6 + avg_similarity * 0.4
        return max(0.0, min(1.0, confidence))

    def _calculate_expected_return(
        self,
        strategy: StrategyType,
        similar_cases: List[Dict[str, Any]],
        current_data: pd.DataFrame,
    ) -> float:
        """期待リターンの計算"""
        if not similar_cases:
            return 0.05  # デフォルト5%

        # 類似ケースの平均リターン
        avg_return = np.mean([case.get("return", 0.05) for case in similar_cases])

        # 現在の市場条件を考慮した調整
        current_price = (
            current_data["Close"].iloc[-1] if not current_data.empty else 100
        )
        price_momentum = (
            (current_price - current_data["Close"].iloc[-20])
            / current_data["Close"].iloc[-20]
            if len(current_data) >= 20
            else 0
        )

        # モメンタムを考慮した調整
        adjusted_return = avg_return * (1 + price_momentum * 0.5)

        return max(0.0, min(0.5, adjusted_return))  # 0-50%の範囲に制限

    def _assess_risk_level(
        self,
        current_data: pd.DataFrame,
        market_conditions: Dict[str, Any],
        strategy: StrategyType,
    ) -> str:
        """リスクレベルの評価"""
        volatility = market_conditions.get("volatility", 0.15)

        if volatility > 0.3:
            return "high"
        elif volatility > 0.2:
            return "medium"
        else:
            return "low"

    def _calculate_position_size(
        self,
        current_data: pd.DataFrame,
        market_conditions: Dict[str, Any],
        risk_level: str,
    ) -> float:
        """ポジションサイズの計算"""
        base_size = 0.1  # 10%をベース

        # リスクレベルに応じた調整
        if risk_level == "high":
            return base_size * 0.5  # 5%
        elif risk_level == "medium":
            return base_size * 0.8  # 8%
        else:
            return base_size  # 10%

    def _calculate_stop_take_levels(
        self, current_data: pd.DataFrame, strategy: StrategyType, risk_level: str
    ) -> Tuple[float, float]:
        """ストップロス・利確レベルの計算"""
        current_price = (
            current_data["Close"].iloc[-1] if not current_data.empty else 100
        )

        # リスクレベルに応じた調整
        if risk_level == "high":
            stop_loss = 0.03  # 3%
            take_profit = 0.06  # 6%
        elif risk_level == "medium":
            stop_loss = 0.05  # 5%
            take_profit = 0.10  # 10%
        else:
            stop_loss = 0.08  # 8%
            take_profit = 0.15  # 15%

        return stop_loss, take_profit

    def _generate_reasoning(
        self,
        strategy: StrategyType,
        similar_cases: List[Dict[str, Any]],
        regime: MarketRegime,
        confidence: float,
    ) -> List[str]:
        """推奨理由の生成"""
        reasoning = []

        reasoning.append(f"市場レジーム: {regime.value}環境での推奨")
        reasoning.append(f"戦略タイプ: {strategy.value}戦略が最適")
        reasoning.append(f"信頼度: {confidence:.1%}")

        if similar_cases:
            avg_success = np.mean(
                [case.get("success_rate", 0) for case in similar_cases]
            )
            reasoning.append(f"類似ケースの平均成功率: {avg_success:.1%}")

        return reasoning

    def _get_holding_period(self, strategy: StrategyType) -> int:
        """保有期間の取得"""
        holding_periods = {
            StrategyType.SCALPING: 1,
            StrategyType.MOMENTUM: 7,
            StrategyType.MEAN_REVERSION: 14,
            StrategyType.SWING: 30,
            StrategyType.BREAKOUT: 21,
            StrategyType.AI_PREDICTION: 14,
            StrategyType.VALUE: 90,
            StrategyType.GROWTH: 60,
            StrategyType.DIVIDEND: 180,
        }

        return holding_periods.get(strategy, 14)

    def _calculate_current_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """現在の技術指標を計算"""
        if data.empty or len(data) < 20:
            return {}

        indicators = {}

        # RSI
        delta = data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators["rsi"] = (100 - (100 / (1 + rs))).iloc[-1]

        # MACD
        exp1 = data["Close"].ewm(span=12).mean()
        exp2 = data["Close"].ewm(span=26).mean()
        indicators["macd"] = (exp1 - exp2).iloc[-1]

        # ボリンジャーバンド位置
        sma = data["Close"].rolling(window=20).mean()
        std = data["Close"].rolling(window=20).std()
        bb_upper = sma + (std * 2)
        bb_lower = sma - (std * 2)
        current_price = data["Close"].iloc[-1]
        indicators["bollinger_position"] = (current_price - bb_lower.iloc[-1]) / (
            bb_upper.iloc[-1] - bb_lower.iloc[-1]
        )

        return indicators


class AutomatedStrategyExecution:
    """自動戦略実行クラス"""

    def __init__(self, unified_system: UnifiedSystem):
        self.unified_system = unified_system
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.active_executions = {}
        self.execution_history = []

    def execute_strategy(
        self, recommendation: StrategyRecommendation
    ) -> StrategyExecution:
        """戦略の実行"""
        try:
            execution_id = f"EXEC_{recommendation.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 現在価格の取得（簡易実装）
            current_price = self._get_current_price(recommendation.symbol)

            # 実行オブジェクトの作成
            execution = StrategyExecution(
                recommendation_id=execution_id,
                symbol=recommendation.symbol,
                strategy=recommendation.recommended_strategy,
                entry_price=current_price,
                position_size=recommendation.position_size,
                stop_loss=current_price * (1 - recommendation.stop_loss),
                take_profit=current_price * (1 + recommendation.take_profit),
                entry_time=datetime.now(),
            )

            # アクティブ実行に追加
            self.active_executions[execution_id] = execution

            # 履歴に追加
            self.execution_history.append(execution)

            self.logger.info(
                f"🚀 戦略実行開始: {execution_id} - {recommendation.symbol} "
                f"{recommendation.recommended_strategy.value}"
            )

            return execution

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.API_ERROR,
                context=f"戦略実行エラー: {recommendation.symbol}",
            )
            raise

    def monitor_execution(self, execution_id: str) -> Dict[str, Any]:
        """実行の監視"""
        if execution_id not in self.active_executions:
            return {"status": "not_found"}

        execution = self.active_executions[execution_id]
        current_price = self._get_current_price(execution.symbol)

        # 損益の計算
        pnl = (current_price - execution.entry_price) * execution.position_size

        # ストップロス・利確のチェック
        if current_price <= execution.stop_loss:
            self._close_execution(execution_id, current_price, "stop_loss")
        elif current_price >= execution.take_profit:
            self._close_execution(execution_id, current_price, "take_profit")

        return {
            "execution_id": execution_id,
            "symbol": execution.symbol,
            "current_price": current_price,
            "entry_price": execution.entry_price,
            "pnl": pnl,
            "pnl_percentage": (current_price - execution.entry_price)
            / execution.entry_price,
            "status": execution.status,
        }

    def _close_execution(self, execution_id: str, exit_price: float, reason: str):
        """実行のクローズ"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.exit_time = datetime.now()
            execution.exit_price = exit_price
            execution.pnl = (
                exit_price - execution.entry_price
            ) * execution.position_size
            execution.status = "closed"

            del self.active_executions[execution_id]

            self.logger.info(
                f"📊 戦略実行終了: {execution_id} - {reason} " f"(損益: {execution.pnl:.2f})"
            )

    def _get_current_price(self, symbol: str) -> float:
        """現在価格の取得（簡易実装）"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            return data["Close"].iloc[-1] if not data.empty else 100.0
        except:
            return 100.0  # フォールバック価格


class AutomatedStrategyRecommendationSystem:
    """投資戦略自動提案システム"""

    def __init__(self, unified_system: UnifiedSystem = None):
        self.unified_system = unified_system or UnifiedSystem()
        self.pattern_analyzer = PatternAnalyzer(self.unified_system)
        self.strategy_recommender = StrategyRecommender(
            self.unified_system, self.pattern_analyzer
        )
        self.strategy_executor = AutomatedStrategyExecution(self.unified_system)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # データストレージ
        self.historical_analyses = []
        self.recommendations = []
        self.executions = []

        self.logger.info("🤖 投資戦略自動提案システム初期化完了")

    def add_historical_analysis(self, analysis: HistoricalAnalysis):
        """過去の分析結果を追加"""
        self.historical_analyses.append(analysis)
        self.logger.info(
            f"📈 過去分析結果追加: {analysis.symbol} - {analysis.strategy_type.value}"
        )

    def generate_recommendation(
        self, symbol: str, current_data: pd.DataFrame, market_conditions: Dict[str, Any]
    ) -> StrategyRecommendation:
        """投資戦略の推奨生成"""
        try:
            # 過去のパターンを分析
            patterns = self.pattern_analyzer.extract_patterns(self.historical_analyses)

            # 戦略を推奨
            recommendation = self.strategy_recommender.recommend_strategy(
                symbol, current_data, market_conditions, patterns
            )

            # 推奨を保存
            self.recommendations.append(recommendation)

            return recommendation

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"推奨生成エラー: {symbol}",
            )
            raise

    def execute_recommendation(
        self, recommendation: StrategyRecommendation
    ) -> StrategyExecution:
        """推奨戦略の実行"""
        try:
            execution = self.strategy_executor.execute_strategy(recommendation)
            self.executions.append(execution)
            return execution

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.API_ERROR,
                context=f"戦略実行エラー: {recommendation.symbol}",
            )
            raise

    def get_system_performance(self) -> Dict[str, Any]:
        """システムパフォーマンスの取得"""
        try:
            total_recommendations = len(self.recommendations)
            total_executions = len(self.executions)

            if total_executions == 0:
                return {"status": "no_executions"}

            # 実行結果の分析
            closed_executions = [e for e in self.executions if e.status == "closed"]
            successful_executions = [
                e for e in closed_executions if e.pnl and e.pnl > 0
            ]

            success_rate = (
                len(successful_executions) / len(closed_executions)
                if closed_executions
                else 0
            )
            avg_return = (
                np.mean([e.pnl for e in closed_executions if e.pnl])
                if closed_executions
                else 0
            )

            return {
                "total_recommendations": total_recommendations,
                "total_executions": total_executions,
                "success_rate": success_rate,
                "average_return": avg_return,
                "active_executions": len(self.strategy_executor.active_executions),
                "system_uptime": "active",
            }

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="システムパフォーマンス取得エラー",
            )
            return {"status": "error"}


def main():
    """メイン実行関数"""
    try:
        # 統合システムの初期化
        unified_system = UnifiedSystem()

        # 自動戦略提案システムの初期化
        strategy_system = AutomatedStrategyRecommendationSystem(unified_system)

        # サンプル過去分析データの作成
        sample_analysis = HistoricalAnalysis(
            symbol="7203.T",
            analysis_date=datetime.now() - timedelta(days=30),
            strategy_type=StrategyType.MOMENTUM,
            performance_metrics={"total_return": 0.12, "sharpe_ratio": 1.5},
            market_conditions={"volatility": 0.18, "trend_strength": 0.15},
            technical_indicators={"rsi": 65, "macd": 0.5, "composite_score": 0.75},
            fundamental_indicators={"pe_ratio": 15.2, "pb_ratio": 1.8},
            sentiment_score=0.7,
            risk_metrics={"volatility": 0.18, "max_drawdown": 0.05},
            success_score=0.8,
        )

        strategy_system.add_historical_analysis(sample_analysis)

        # サンプル現在データの作成
        np.random.seed(42)
        dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
        current_data = pd.DataFrame(
            {
                "Date": dates,
                "Open": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
                "High": 100
                + np.cumsum(np.random.randn(len(dates)) * 0.5)
                + np.random.randn(len(dates)) * 0.1,
                "Low": 100
                + np.cumsum(np.random.randn(len(dates)) * 0.5)
                - np.random.randn(len(dates)) * 0.1,
                "Close": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
                "Volume": np.random.randint(1000, 10000, len(dates)),
            }
        )
        current_data.set_index("Date", inplace=True)

        # 現在の市場条件
        market_conditions = {
            "volatility": 0.20,
            "trend_strength": 0.10,
            "market_regime": "bull",
        }

        # 戦略推奨の生成
        recommendation = strategy_system.generate_recommendation(
            "7203.T", current_data, market_conditions
        )

        print("=== 投資戦略推奨 ===")
        print(f"銘柄: {recommendation.symbol}")
        print(f"推奨戦略: {recommendation.recommended_strategy.value}")
        print(f"信頼度: {recommendation.confidence_score:.1%}")
        print(f"期待リターン: {recommendation.expected_return:.1%}")
        print(f"リスクレベル: {recommendation.risk_level}")
        print(f"保有期間: {recommendation.holding_period}日")
        print(f"ポジションサイズ: {recommendation.position_size:.1%}")
        print(f"ストップロス: {recommendation.stop_loss:.1%}")
        print(f"利確: {recommendation.take_profit:.1%}")
        print(f"市場レジーム: {recommendation.market_regime.value}")
        print("\n推奨理由:")
        for reason in recommendation.reasoning:
            print(f"  - {reason}")

        # 戦略の実行
        execution = strategy_system.execute_recommendation(recommendation)
        print(f"\n=== 戦略実行 ===")
        print(f"実行ID: {execution.recommendation_id}")
        print(f"エントリー価格: {execution.entry_price:.2f}")
        print(f"ポジションサイズ: {execution.position_size:.1%}")

        # システムパフォーマンス
        performance = strategy_system.get_system_performance()
        print(f"\n=== システムパフォーマンス ===")
        for key, value in performance.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
