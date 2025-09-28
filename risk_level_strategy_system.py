#!/usr/bin/env python3
"""
リスクレベル別投資戦略提案システム
投資家のリスク許容度に応じて最適な投資戦略を提案

主要機能:
1. リスクプロファイルの自動判定
2. リスクレベル別戦略提案
3. 動的リスク管理
4. ポートフォリオ最適化
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


class RiskLevel(Enum):
    """リスクレベル"""

    CONSERVATIVE = "conservative"  # 保守的
    MODERATE = "moderate"  # 中程度
    AGGRESSIVE = "aggressive"  # 積極的
    VERY_AGGRESSIVE = "very_aggressive"  # 非常に積極的


class RiskTolerance(Enum):
    """リスク許容度"""

    VERY_LOW = "very_low"  # 非常に低い
    LOW = "low"  # 低い
    MEDIUM = "medium"  # 中程度
    HIGH = "high"  # 高い
    VERY_HIGH = "very_high"  # 非常に高い


@dataclass
class RiskProfile:
    """リスクプロファイル"""

    risk_level: RiskLevel
    risk_tolerance: RiskTolerance
    max_drawdown: float
    volatility_tolerance: float
    investment_horizon: int  # 投資期間（月）
    liquidity_needs: str  # 流動性ニーズ
    income_requirements: float  # 収入要件
    age_factor: float  # 年齢要因
    experience_level: str  # 経験レベル
    created_at: datetime


@dataclass
class RiskBasedStrategy:
    """リスクベース戦略"""

    strategy_name: str
    risk_level: RiskLevel
    expected_return: float
    expected_volatility: float
    max_drawdown: float
    sharpe_ratio: float
    asset_allocation: Dict[str, float]
    rebalancing_frequency: str
    risk_management_rules: List[str]
    position_sizing_rules: List[str]
    stop_loss_rules: List[str]
    diversification_rules: List[str]
    created_at: datetime


@dataclass
class PortfolioRecommendation:
    """ポートフォリオ推奨"""

    risk_profile: RiskProfile
    recommended_strategies: List[RiskBasedStrategy]
    total_allocation: Dict[str, float]
    expected_performance: Dict[str, float]
    risk_metrics: Dict[str, float]
    rebalancing_schedule: Dict[str, Any]
    monitoring_rules: List[str]
    created_at: datetime


class RiskProfileAnalyzer:
    """リスクプロファイル分析クラス"""

    def __init__(self, unified_system: UnifiedSystem):
        self.unified_system = unified_system
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    def analyze_risk_profile(
        self,
        age: int,
        income: float,
        investment_amount: float,
        investment_horizon: int,
        risk_questionnaire: Dict[str, Any] = None,
    ) -> RiskProfile:
        """リスクプロファイルの分析"""
        try:
            # 基本リスク要因の計算
            age_factor = self._calculate_age_factor(age)
            income_factor = self._calculate_income_factor(income, investment_amount)
            horizon_factor = self._calculate_horizon_factor(investment_horizon)

            # リスク許容度の計算
            risk_tolerance = self._calculate_risk_tolerance(
                age_factor, income_factor, horizon_factor, risk_questionnaire
            )

            # リスクレベルの決定
            risk_level = self._determine_risk_level(
                risk_tolerance, age_factor, horizon_factor
            )

            # リスク制限の設定
            max_drawdown = self._calculate_max_drawdown(risk_level, age_factor)
            volatility_tolerance = self._calculate_volatility_tolerance(risk_level)

            # 流動性ニーズの評価
            liquidity_needs = self._assess_liquidity_needs(
                age, income, investment_amount
            )

            # 収入要件の計算
            income_requirements = self._calculate_income_requirements(
                investment_amount, investment_horizon, risk_level
            )

            # 経験レベルの推定
            experience_level = self._estimate_experience_level(
                age, income, investment_amount
            )
            
            return RiskProfile(
                risk_level=risk_level,
                risk_tolerance=risk_tolerance,
                max_drawdown=max_drawdown,
                volatility_tolerance=volatility_tolerance,
                investment_horizon=investment_horizon,
                liquidity_needs=liquidity_needs,
                income_requirements=income_requirements,
                age_factor=age_factor,
                experience_level=experience_level,
                created_at=datetime.now(),
            )

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="リスクプロファイル分析エラー",
            )
            return self._get_default_risk_profile()
    
    def _calculate_age_factor(self, age: int) -> float:
        """年齢要因の計算"""
        if age < 30:
            return 1.0  # 高いリスク許容度
        elif age < 40:
            return 0.9
        elif age < 50:
            return 0.8
        elif age < 60:
            return 0.6
        else:
            return 0.4  # 低いリスク許容度
    
    def _calculate_income_factor(self, income: float, investment_amount: float) -> float:
        """収入要因の計算"""
        if investment_amount == 0:
            return 0.5
        
        investment_ratio = investment_amount / income
        if investment_ratio < 0.1:
            return 1.0  # 低い投資比率
        elif investment_ratio < 0.3:
            return 0.8
        elif investment_ratio < 0.5:
            return 0.6
        else:
            return 0.4  # 高い投資比率
    
    def _calculate_horizon_factor(self, investment_horizon: int) -> float:
        """投資期間要因の計算"""
        if investment_horizon >= 10:
            return 1.0  # 長期投資
        elif investment_horizon >= 5:
            return 0.8
        elif investment_horizon >= 2:
            return 0.6
        else:
            return 0.4  # 短期投資
    
    def _calculate_risk_tolerance(
        self, 
        age_factor: float, 
        income_factor: float, 
        horizon_factor: float,
        questionnaire: Dict[str, Any] = None
    ) -> RiskTolerance:
        """リスク許容度の計算"""
        # 基本スコア
        base_score = (age_factor + income_factor + horizon_factor) / 3
        
        # アンケート結果の反映
        if questionnaire:
            questionnaire_score = self._process_risk_questionnaire(questionnaire)
            base_score = (base_score + questionnaire_score) / 2
        
        # リスク許容度の決定
        if base_score >= 0.8:
            return RiskTolerance.VERY_HIGH
        elif base_score >= 0.6:
            return RiskTolerance.HIGH
        elif base_score >= 0.4:
            return RiskTolerance.MEDIUM
        elif base_score >= 0.2:
            return RiskTolerance.LOW
        else:
            return RiskTolerance.VERY_LOW
    
    def _process_risk_questionnaire(self, questionnaire: Dict[str, Any]) -> float:
        """リスクアンケートの処理"""
        score = 0.5  # デフォルトスコア
        
        # 損失許容度
        if "loss_tolerance" in questionnaire:
            loss_tolerance = questionnaire["loss_tolerance"]
            if loss_tolerance == "high":
                score += 0.2
            elif loss_tolerance == "medium":
                score += 0.1
            else:
                score -= 0.1
        
        # 投資経験
        if "investment_experience" in questionnaire:
            experience = questionnaire["investment_experience"]
            if experience == "extensive":
                score += 0.2
            elif experience == "moderate":
                score += 0.1
            else:
                score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _determine_risk_level(
        self, 
        risk_tolerance: RiskTolerance, 
        age_factor: float, 
        horizon_factor: float
    ) -> RiskLevel:
        """リスクレベルの決定"""
        # リスク許容度と年齢・期間要因の組み合わせ
        if risk_tolerance == RiskTolerance.VERY_HIGH and age_factor > 0.7:
            return RiskLevel.VERY_AGGRESSIVE
        elif risk_tolerance in [RiskTolerance.HIGH, RiskTolerance.VERY_HIGH]:
            return RiskLevel.AGGRESSIVE
        elif risk_tolerance == RiskTolerance.MEDIUM:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.CONSERVATIVE
    
    def _calculate_max_drawdown(self, risk_level: RiskLevel, age_factor: float) -> float:
        """最大ドローダウンの計算"""
        base_drawdowns = {
            RiskLevel.CONSERVATIVE: 0.05,
            RiskLevel.MODERATE: 0.10,
            RiskLevel.AGGRESSIVE: 0.15,
            RiskLevel.VERY_AGGRESSIVE: 0.20
        }
        
        base_drawdown = base_drawdowns[risk_level]
        
        # 年齢要因による調整
        if age_factor < 0.5:  # 高齢者
            base_drawdown *= 0.7
        
        return base_drawdown
    
    def _calculate_volatility_tolerance(self, risk_level: RiskLevel) -> float:
        """ボラティリティ許容度の計算"""
        volatility_tolerances = {
            RiskLevel.CONSERVATIVE: 0.10,
            RiskLevel.MODERATE: 0.15,
            RiskLevel.AGGRESSIVE: 0.25,
            RiskLevel.VERY_AGGRESSIVE: 0.35
        }
        
        return volatility_tolerances[risk_level]
    
    def _assess_liquidity_needs(self, age: int, income: float, investment_amount: float) -> str:
        """流動性ニーズの評価"""
        if age > 60:
            return "high"  # 高齢者は高い流動性ニーズ
        elif investment_amount / income > 0.5:
            return "medium"  # 投資比率が高い場合
        else:
            return "low"
    
    def _calculate_income_requirements(
        self, 
        investment_amount: float, 
        investment_horizon: int, 
        risk_level: RiskLevel
    ) -> float:
        """収入要件の計算"""
        # 年率リターンの期待値
        expected_returns = {
            RiskLevel.CONSERVATIVE: 0.04,
            RiskLevel.MODERATE: 0.06,
            RiskLevel.AGGRESSIVE: 0.08,
            RiskLevel.VERY_AGGRESSIVE: 0.10
        }
        
        expected_return = expected_returns[risk_level]
        
        # 複利計算による収入要件
        if investment_horizon > 0:
            return investment_amount * (expected_return / 12)  # 月次収入
        else:
            return 0.0
    
    def _estimate_experience_level(self, age: int, income: float, investment_amount: float) -> str:
        """経験レベルの推定"""
        # 年齢と収入による経験レベルの推定
        if age > 50 and income > 1000000:
            return "expert"
        elif age > 35 and income > 500000:
            return "intermediate"
        else:
            return "beginner"
    
    def _get_default_risk_profile(self) -> RiskProfile:
        """デフォルトリスクプロファイルの取得"""
        return RiskProfile(
            risk_level=RiskLevel.MODERATE,
            risk_tolerance=RiskTolerance.MEDIUM,
            max_drawdown=0.10,
            volatility_tolerance=0.15,
            investment_horizon=60,
            liquidity_needs="medium",
            income_requirements=0.0,
            age_factor=0.7,
            experience_level="intermediate",
            created_at=datetime.now()
        )


class RiskBasedStrategyGenerator:
    """リスクベース戦略生成クラス"""

    def __init__(self, unified_system: UnifiedSystem):
        self.unified_system = unified_system
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    def generate_strategies_for_risk_level(
        self, risk_profile: RiskProfile
    ) -> List[RiskBasedStrategy]:
        """リスクレベル別戦略の生成"""
        try:
            strategies = []

            if risk_profile.risk_level == RiskLevel.CONSERVATIVE:
                strategies = self._generate_conservative_strategies(risk_profile)
            elif risk_profile.risk_level == RiskLevel.MODERATE:
                strategies = self._generate_moderate_strategies(risk_profile)
            elif risk_profile.risk_level == RiskLevel.AGGRESSIVE:
                strategies = self._generate_aggressive_strategies(risk_profile)
            elif risk_profile.risk_level == RiskLevel.VERY_AGGRESSIVE:
                strategies = self._generate_very_aggressive_strategies(risk_profile)

            self.logger.info(
                f"📊 リスクベース戦略生成完了: {risk_profile.risk_level.value} - {len(strategies)}戦略"
            )

            return strategies

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="リスクベース戦略生成エラー",
            )
            return []

    def _generate_conservative_strategies(
        self, risk_profile: RiskProfile
    ) -> List[RiskBasedStrategy]:
        """保守的戦略の生成"""
        strategies = []

        # 債券中心戦略
        bond_strategy = RiskBasedStrategy(
            strategy_name="Conservative Bond Strategy",
            risk_level=RiskLevel.CONSERVATIVE,
            expected_return=0.04,
            expected_volatility=0.05,
            max_drawdown=0.03,
            sharpe_ratio=0.8,
            asset_allocation={"government_bonds": 0.60, "corporate_bonds": 0.25, "cash": 0.15},
            rebalancing_frequency="quarterly",
            risk_management_rules=[
                "最大ドローダウン3%でリスク管理",
                "債券の信用格付けを監視",
                "金利変動リスクをヘッジ",
            ],
            position_sizing_rules=[
                "単一債券への投資は5%以下",
                "セクター分散を実施",
                "満期分散を実施",
            ],
            stop_loss_rules=[
                "個別債券で-2%で損切り",
                "ポートフォリオ全体で-3%で損切り",
            ],
            diversification_rules=[
                "最低10銘柄以上に分散",
                "複数セクターに分散",
                "満期の分散化",
            ],
            created_at=datetime.now(),
        )
        strategies.append(bond_strategy)

        # 配当重視戦略
        dividend_strategy = RiskBasedStrategy(
            strategy_name="Conservative Dividend Strategy",
            risk_level=RiskLevel.CONSERVATIVE,
            expected_return=0.05,
            expected_volatility=0.08,
            max_drawdown=0.05,
            sharpe_ratio=0.6,
            asset_allocation={"dividend_stocks": 0.70, "government_bonds": 0.20, "cash": 0.10},
            rebalancing_frequency="semi-annually",
            risk_management_rules=[
                "配当利回り3%以上を維持",
                "配当カバレッジ比率を監視",
                "業績悪化銘柄を除外",
            ],
            position_sizing_rules=[
                "単一銘柄への投資は3%以下",
                "セクター分散を実施",
                "時価総額分散を実施",
            ],
            stop_loss_rules=[
                "個別銘柄で-5%で損切り",
                "配当カット銘柄は即座に売却",
            ],
            diversification_rules=[
                "最低20銘柄以上に分散",
                "複数セクターに分散",
                "時価総額分散を実施",
            ],
            created_at=datetime.now(),
        )
        strategies.append(dividend_strategy)

        return strategies

    def _generate_moderate_strategies(self, risk_profile: RiskProfile) -> List[RiskBasedStrategy]:
        """中程度戦略の生成"""
        strategies = []

        # バランス戦略
        balanced_strategy = RiskBasedStrategy(
            strategy_name="Balanced Strategy",
            risk_level=RiskLevel.MODERATE,
            expected_return=0.07,
            expected_volatility=0.12,
            max_drawdown=0.08,
            sharpe_ratio=0.6,
            asset_allocation={"stocks": 0.60, "bonds": 0.30, "cash": 0.10},
            rebalancing_frequency="quarterly",
            risk_management_rules=[
                "最大ドローダウン8%でリスク管理",
                "バランス比率の維持",
                "市場環境に応じた調整",
            ],
            position_sizing_rules=[
                "単一銘柄への投資は5%以下",
                "セクター分散を実施",
                "時価総額分散を実施",
            ],
            stop_loss_rules=[
                "個別銘柄で-8%で損切り",
                "ポートフォリオ全体で-8%で損切り",
            ],
            diversification_rules=[
                "最低15銘柄以上に分散",
                "複数セクターに分散",
                "資産クラス分散を実施",
            ],
            created_at=datetime.now(),
        )
        strategies.append(balanced_strategy)

        return strategies

    def _generate_aggressive_strategies(self, risk_profile: RiskProfile) -> List[RiskBasedStrategy]:
        """積極的戦略の生成"""
        strategies = []

        # 成長株戦略
        growth_strategy = RiskBasedStrategy(
            strategy_name="Growth Stock Strategy",
            risk_level=RiskLevel.AGGRESSIVE,
            expected_return=0.10,
            expected_volatility=0.20,
            max_drawdown=0.15,
            sharpe_ratio=0.5,
            asset_allocation={"growth_stocks": 0.80, "bonds": 0.15, "cash": 0.05},
            rebalancing_frequency="monthly",
            risk_management_rules=[
                "最大ドローダウン15%でリスク管理",
                "成長性指標を監視",
                "市場環境に応じた調整",
            ],
            position_sizing_rules=[
                "単一銘柄への投資は8%以下",
                "セクター分散を実施",
                "時価総額分散を実施",
            ],
            stop_loss_rules=[
                "個別銘柄で-12%で損切り",
                "ポートフォリオ全体で-15%で損切り",
            ],
            diversification_rules=[
                "最低12銘柄以上に分散",
                "複数セクターに分散",
                "成長段階分散を実施",
            ],
            created_at=datetime.now(),
        )
        strategies.append(growth_strategy)

        return strategies

    def _generate_very_aggressive_strategies(self, risk_profile: RiskProfile) -> List[RiskBasedStrategy]:
        """非常に積極的戦略の生成"""
        strategies = []

        # ハイリスク・ハイリターン戦略
        high_risk_strategy = RiskBasedStrategy(
            strategy_name="High Risk High Return Strategy",
            risk_level=RiskLevel.VERY_AGGRESSIVE,
            expected_return=0.15,
            expected_volatility=0.30,
            max_drawdown=0.25,
            sharpe_ratio=0.5,
            asset_allocation={"high_risk_stocks": 0.70, "emerging_markets": 0.20, "cash": 0.10},
            rebalancing_frequency="weekly",
            risk_management_rules=[
                "最大ドローダウン25%でリスク管理",
                "高ボラティリティ銘柄を活用",
                "市場環境に応じた積極的調整",
            ],
            position_sizing_rules=[
                "単一銘柄への投資は10%以下",
                "セクター分散を実施",
                "リスク分散を実施",
            ],
            stop_loss_rules=[
                "個別銘柄で-15%で損切り",
                "ポートフォリオ全体で-25%で損切り",
            ],
            diversification_rules=[
                "最低8銘柄以上に分散",
                "複数セクターに分散",
                "リスク分散を実施",
            ],
            created_at=datetime.now(),
        )
        strategies.append(high_risk_strategy)

        return strategies


class RiskLevelStrategySystem:
    """リスクレベル戦略システム"""
    
    def __init__(self, unified_system: UnifiedSystem = None):
        self.unified_system = unified_system or UnifiedSystem()
        self.risk_analyzer = RiskProfileAnalyzer(self.unified_system)
        self.strategy_generator = RiskBasedStrategyGenerator(self.unified_system)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 履歴データ
        self.risk_profiles = []
        self.strategy_recommendations = []

        self.logger.info("🎯 リスクレベル戦略システム初期化完了")

    def create_portfolio_recommendation(
        self,
        age: int,
        income: float,
        investment_amount: float,
        investment_horizon: int,
        risk_questionnaire: Dict[str, Any] = None
    ) -> PortfolioRecommendation:
        """ポートフォリオ推奨の作成"""
        try:
            # リスクプロファイルの分析
            risk_profile = self.risk_analyzer.analyze_risk_profile(
                age, income, investment_amount, investment_horizon, risk_questionnaire
            )
            self.risk_profiles.append(risk_profile)
            
            # リスクレベル別戦略の生成
            strategies = self.strategy_generator.generate_strategies_for_risk_level(risk_profile)
            
            # ポートフォリオ推奨の作成
            recommendation = self._create_portfolio_recommendation(risk_profile, strategies)
            self.strategy_recommendations.append(recommendation)
            
            self.logger.info(
                f"📊 ポートフォリオ推奨作成完了: {risk_profile.risk_level.value}"
            )
            
            return recommendation
            
        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="ポートフォリオ推奨作成エラー"
            )
            return self._get_default_recommendation()

    def _create_portfolio_recommendation(
        self,
        risk_profile: RiskProfile,
        strategies: List[RiskBasedStrategy],
    ) -> PortfolioRecommendation:
        """ポートフォリオ推奨の作成"""
        # 総合資産配分の計算
        total_allocation = self._calculate_total_allocation(strategies)

        # 期待パフォーマンスの計算
        expected_performance = self._calculate_expected_performance(strategies)

        # リスク指標の計算
        risk_metrics = self._calculate_risk_metrics(strategies, risk_profile)

        # リバランススケジュールの設定
        rebalancing_schedule = self._create_rebalancing_schedule(risk_profile)

        # モニタリングルールの設定
        monitoring_rules = self._create_monitoring_rules(risk_profile)

        return PortfolioRecommendation(
            risk_profile=risk_profile,
            recommended_strategies=strategies,
            total_allocation=total_allocation,
            expected_performance=expected_performance,
            risk_metrics=risk_metrics,
            rebalancing_schedule=rebalancing_schedule,
            monitoring_rules=monitoring_rules,
            created_at=datetime.now(),
        )

    def _calculate_total_allocation(self, strategies: List[RiskBasedStrategy]) -> Dict[str, float]:
        """総合資産配分の計算"""
        total_allocation = {}

        for strategy in strategies:
            for asset_class, allocation in strategy.asset_allocation.items():
                if asset_class in total_allocation:
                    total_allocation[asset_class] += allocation
                else:
                    total_allocation[asset_class] = allocation
        
        # 正規化
        total = sum(total_allocation.values())
        if total > 0:
            for asset_class in total_allocation:
                total_allocation[asset_class] /= total

        return total_allocation

    def _calculate_expected_performance(self, strategies: List[RiskBasedStrategy]) -> Dict[str, float]:
        """期待パフォーマンスの計算"""
        if not strategies:
            return {}

        # 重み付き平均の計算
        total_weight = len(strategies)

        expected_return = sum(s.expected_return for s in strategies) / total_weight
        expected_volatility = sum(s.expected_volatility for s in strategies) / total_weight
        max_drawdown = max(s.max_drawdown for s in strategies)
        sharpe_ratio = sum(s.sharpe_ratio for s in strategies) / total_weight

        return {
            "expected_return": expected_return,
            "expected_volatility": expected_volatility,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
        }

    def _calculate_risk_metrics(
        self,
        strategies: List[RiskBasedStrategy],
        risk_profile: RiskProfile,
    ) -> Dict[str, float]:
        """リスク指標の計算"""
        return {
            "max_drawdown_limit": risk_profile.max_drawdown,
            "volatility_limit": risk_profile.volatility_tolerance,
            "var_95": risk_profile.max_drawdown * 0.8,
            "expected_shortfall": risk_profile.max_drawdown * 0.6,
            "risk_score": self._calculate_risk_score(risk_profile),
        }

    def _calculate_risk_score(self, risk_profile: RiskProfile) -> float:
        """リスクスコアの計算"""
        # リスクレベルによる基本スコア
        risk_scores = {
            RiskLevel.CONSERVATIVE: 0.2,
            RiskLevel.MODERATE: 0.5,
            RiskLevel.AGGRESSIVE: 0.8,
            RiskLevel.VERY_AGGRESSIVE: 1.0,
        }

        base_score = risk_scores[risk_profile.risk_level]

        # 年齢要因による調整
        age_adjustment = risk_profile.age_factor * 0.3

        # 投資期間による調整
        horizon_adjustment = min(1.0, risk_profile.investment_horizon / 120) * 0.2
        
        return min(1.0, base_score + age_adjustment + horizon_adjustment)

    def _create_rebalancing_schedule(self, risk_profile: RiskProfile) -> Dict[str, Any]:
        """リバランススケジュールの作成"""
        if risk_profile.risk_level == RiskLevel.CONSERVATIVE:
            frequency = "quarterly"
        elif risk_profile.risk_level == RiskLevel.MODERATE:
            frequency = "quarterly"
        elif risk_profile.risk_level == RiskLevel.AGGRESSIVE:
            frequency = "monthly"
        else:
            frequency = "weekly"
        
        return {
            "frequency": frequency,
            "threshold": 0.05,  # 5%の乖離でリバランス
            "max_deviation": 0.10,  # 最大10%の乖離まで許容
            "rebalancing_method": "threshold_based",
        }

    def _create_monitoring_rules(self, risk_profile: RiskProfile) -> List[str]:
        """モニタリングルールの作成"""
        rules = []

        # 基本モニタリングルール
        rules.append("日次パフォーマンス監視")
        rules.append("週次リスク指標監視")
        rules.append("月次リバランスチェック")

        # リスクレベル別ルール
        if risk_profile.risk_level in [RiskLevel.AGGRESSIVE, RiskLevel.VERY_AGGRESSIVE]:
            rules.append("日次ボラティリティ監視")
            rules.append("リアルタイムリスク監視")

        if risk_profile.risk_level == RiskLevel.CONSERVATIVE:
            rules.append("月次収益性監視")
            rules.append("四半期リスク評価")

        return rules

    def _get_default_recommendation(self) -> PortfolioRecommendation:
        """デフォルト推奨の取得"""
        default_profile = self.risk_analyzer._get_default_risk_profile()
        default_strategies = self.strategy_generator._generate_moderate_strategies(default_profile)

        return PortfolioRecommendation(
            risk_profile=default_profile,
            recommended_strategies=default_strategies,
            total_allocation={"stocks": 0.6, "bonds": 0.3, "cash": 0.1},
            expected_performance={"expected_return": 0.07, "expected_volatility": 0.12},
            risk_metrics={"max_drawdown_limit": 0.10},
            rebalancing_schedule={"frequency": "quarterly"},
            monitoring_rules=["月次監視"],
            created_at=datetime.now(),
        )

    def get_system_summary(self) -> Dict[str, Any]:
        """システムサマリーの取得"""
        return {
            "total_risk_profiles": len(self.risk_profiles),
            "total_recommendations": len(self.strategy_recommendations),
            "system_status": "active",
            "last_analysis": datetime.now().isoformat(),
        }

    def export_recommendations(self, file_path: str) -> bool:
        """推奨データのエクスポート"""
        try:
            export_data = {
                "risk_profiles": [
                    {
                        "risk_level": profile.risk_level.value,
                        "risk_tolerance": profile.risk_tolerance.value,
                        "max_drawdown": profile.max_drawdown,
                        "volatility_tolerance": profile.volatility_tolerance,
                        "investment_horizon": profile.investment_horizon,
                        "created_at": profile.created_at.isoformat(),
                    }
                    for profile in self.risk_profiles
                ],
                "recommendations": [
                    {
                        "risk_level": rec.risk_profile.risk_level.value,
                        "strategy_count": len(rec.recommended_strategies),
                        "expected_return": rec.expected_performance.get(
                            "expected_return", 0
                        ),
                        "expected_volatility": rec.expected_performance.get(
                            "expected_volatility", 0
                        ),
                        "created_at": rec.created_at.isoformat(),
                    }
                    for rec in self.strategy_recommendations
                ],
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, default=str, ensure_ascii=False, indent=2)

            self.logger.info(f"📊 推奨データエクスポート完了: {file_path}")
            return True

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.FILE_ERROR,
                context=f"推奨データエクスポートエラー: {file_path}",
            )
            return False


def main():
    """メイン実行関数"""
    try:
        # 統合システムの初期化
        unified_system = UnifiedSystem()

        # リスクレベル戦略システムの初期化
        risk_strategy_system = RiskLevelStrategySystem(unified_system)

        print("=== リスクレベル別投資戦略提案システム ===")

        # サンプル投資家プロファイル
        investor_profiles = [
            {
                "name": "保守的投資家",
                "age": 65,
                "income": 5000000,
                "investment_amount": 10000000,
                "investment_horizon": 5,
                "risk_questionnaire": {
                    "loss_tolerance": "low",
                    "investment_experience": "moderate",
                },
            },
            {
                "name": "中程度投資家",
                "age": 45,
                "income": 8000000,
                "investment_amount": 15000000,
                "investment_horizon": 10,
                "risk_questionnaire": {
                    "loss_tolerance": "medium",
                    "investment_experience": "moderate",
                },
            },
            {
                "name": "積極的投資家",
                "age": 35,
                "income": 12000000,
                "investment_amount": 20000000,
                "investment_horizon": 15,
                "risk_questionnaire": {
                    "loss_tolerance": "high",
                    "investment_experience": "extensive",
                },
            },
        ]

        # 各投資家プロファイルの分析
        for profile in investor_profiles:
            print(f"\n📊 {profile['name']}の分析:")
            print(f"  年齢: {profile['age']}歳")
            print(f"  年収: ¥{profile['income']:,}")
            print(f"  投資金額: ¥{profile['investment_amount']:,}")
            print(f"  投資期間: {profile['investment_horizon']}年")

            # ポートフォリオ推奨の作成
            recommendation = risk_strategy_system.create_portfolio_recommendation(
                profile["age"],
                profile["income"],
                profile["investment_amount"],
                profile["investment_horizon"],
                profile["risk_questionnaire"],
            )

            # 結果の表示
            risk_profile = recommendation.risk_profile
            print(f"  リスクレベル: {risk_profile.risk_level.value}")
            print(f"  リスク許容度: {risk_profile.risk_tolerance.value}")
            print(f"  最大ドローダウン: {risk_profile.max_drawdown:.1%}")
            print(f"  ボラティリティ許容度: {risk_profile.volatility_tolerance:.1%}")

            # 推奨戦略
            print(f"  推奨戦略数: {len(recommendation.recommended_strategies)}")
            for strategy in recommendation.recommended_strategies:
                print(f"    - {strategy.strategy_name}")
                print(f"      期待リターン: {strategy.expected_return:.1%}")
                print(f"      期待ボラティリティ: {strategy.expected_volatility:.1%}")
                print(f"      最大ドローダウン: {strategy.max_drawdown:.1%}")

            # 資産配分
            print(f"  資産配分:")
            for asset_class, allocation in recommendation.total_allocation.items():
                print(f"    {asset_class}: {allocation:.1%}")

            # 期待パフォーマンス
            perf = recommendation.expected_performance
            print(f"  期待パフォーマンス:")
            print(f"    期待リターン: {perf.get('expected_return', 0):.1%}")
            print(f"    期待ボラティリティ: {perf.get('expected_volatility', 0):.1%}")
            print(f"    シャープレシオ: {perf.get('sharpe_ratio', 0):.2f}")

        # システムサマリー
        summary = risk_strategy_system.get_system_summary()
        print(f"\n📈 システムサマリー:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

        # データエクスポート
        risk_strategy_system.export_recommendations("risk_level_recommendations.json")
        print(f"\n推奨データをエクスポートしました: risk_level_recommendations.json")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
