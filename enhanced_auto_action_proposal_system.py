#!/usr/bin/env python3
"""
強化された自動アクション提案システム
ワンクリック分析の完全自動化 - 自動アクション提案機能
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from pathlib import Path
import yaml

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/auto_action_proposal.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """アクションタイプ"""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    MONITOR = "monitor"
    REBALANCE = "rebalance"
    RISK_MANAGEMENT = "risk_management"
    RESEARCH = "research"
    ALERT = "alert"


class ActionPriority(Enum):
    """アクション優先度"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MarketCondition(Enum):
    """市場状況"""

    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    TRENDING = "trending"


@dataclass
class ActionProposal:
    """アクションプロポーザル"""

    action_id: str
    action_type: ActionType
    priority: ActionPriority
    title: str
    description: str
    reasoning: List[str]
    expected_impact: str
    risk_level: float
    confidence_score: float
    execution_time: str
    prerequisites: List[str]
    follow_up_actions: List[str]
    market_condition: MarketCondition
    target_symbols: List[str] = None
    target_amount: Optional[float] = None
    target_percentage: Optional[float] = None
    deadline: Optional[datetime] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.target_symbols is None:
            self.target_symbols = []


@dataclass
class AnalysisContext:
    """分析コンテキスト"""

    analysis_id: str
    analysis_type: str
    market_data: Dict[str, Any]
    technical_indicators: Dict[str, float]
    sentiment_data: Dict[str, Any]
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    portfolio_status: Dict[str, Any]
    user_preferences: Dict[str, Any]
    market_condition: MarketCondition
    volatility_level: float
    trend_direction: str
    support_resistance_levels: Dict[str, float]


class EnhancedAutoActionProposalSystem:
    """強化された自動アクション提案システム"""

    def __init__(self, config_file: str = "action_proposal_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.action_history = []
        self.proposal_templates = self._load_proposal_templates()
        self.market_patterns = self._load_market_patterns()

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        default_config = {
            "action_proposal": {
                "enabled": True,
                "max_proposals_per_analysis": 5,
                "min_confidence_threshold": 0.6,
                "risk_tolerance": "medium",
                "user_preferences": {
                    "preferred_actions": ["buy", "sell", "monitor"],
                    "avoid_actions": ["high_risk_trades"],
                    "max_risk_level": 0.7,
                },
                "market_conditions": {
                    "bull_market": {"aggressive_actions": True, "risk_multiplier": 1.2},
                    "bear_market": {"defensive_actions": True, "risk_multiplier": 0.8},
                    "volatile_market": {
                        "cautious_actions": True,
                        "risk_multiplier": 0.6,
                    },
                },
            }
        }

        try:
            if Path(self.config_file).exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    return {**default_config, **config}
            else:
                return default_config
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return default_config

    def _load_proposal_templates(self) -> Dict[str, Dict[str, Any]]:
        """プロポーザルテンプレートの読み込み"""
        return {
            "buy_signal": {
                "title_template": "{symbol}の買いシグナル検知",
                "description_template": "技術指標と市場分析により買いシグナルが検知されました",
                "reasoning_templates": [
                    "RSIが30を下回り、オーバーセル状態から回復",
                    "移動平均線のゴールデンクロス発生",
                    "出来高の急増により買い圧力が高まっている",
                    "サポートラインでの反発を確認",
                ],
                "expected_impact": "短期〜中期での価格上昇が期待される",
                "risk_level": 0.4,
                "execution_time": "即座〜1営業日以内",
            },
            "sell_signal": {
                "title_template": "{symbol}の売りシグナル検知",
                "description_template": "リスク管理の観点から売りシグナルが検知されました",
                "reasoning_templates": [
                    "RSIが70を上回り、オーバーボート状態",
                    "移動平均線のデッドクロス発生",
                    "レジスタンスラインでの反発を確認",
                    "出来高の減少により売り圧力が高まっている",
                ],
                "expected_impact": "損失の拡大を防ぎ、利益を確定",
                "risk_level": 0.3,
                "execution_time": "即座〜1営業日以内",
            },
            "monitor_signal": {
                "title_template": "{symbol}の監視強化推奨",
                "description_template": "重要な価格レベルに近づいているため監視を強化してください",
                "reasoning_templates": [
                    "重要なサポート・レジスタンスレベルに接近",
                    "ボラティリティの増加により価格変動が激しくなっている",
                    "市場全体の不確実性が高まっている",
                    "技術指標が中立圏で推移している",
                ],
                "expected_impact": "適切なタイミングでの判断が可能",
                "risk_level": 0.2,
                "execution_time": "継続的",
            },
            "rebalance_signal": {
                "title_template": "ポートフォリオの再バランス推奨",
                "description_template": "リスク分散の観点からポートフォリオの再バランスが推奨されます",
                "reasoning_templates": [
                    "特定の銘柄・セクターへの集中度が高まっている",
                    "リスク指標が許容範囲を超えている",
                    "市場環境の変化により最適な資産配分が変化",
                    "投資目標との乖離が生じている",
                ],
                "expected_impact": "リスクの最適化とリターンの安定化",
                "risk_level": 0.3,
                "execution_time": "1週間以内",
            },
            "risk_management": {
                "title_template": "リスク管理の強化",
                "description_template": "現在の市場環境においてリスク管理の強化が推奨されます",
                "reasoning_templates": [
                    "市場のボラティリティが異常に高まっている",
                    "ポートフォリオの最大ドローダウンが許容範囲を超えている",
                    "相関関係の変化により分散投資の効果が低下",
                    "流動性リスクが高まっている",
                ],
                "expected_impact": "損失の限定と資本の保護",
                "risk_level": 0.1,
                "execution_time": "即座",
            },
        }

    def _load_market_patterns(self) -> Dict[str, Dict[str, Any]]:
        """市場パターンの読み込み"""
        return {
            "trending_up": {
                "conditions": ["rsi > 50", "ma_trend > 0", "volume_increase"],
                "recommended_actions": ["buy", "hold"],
                "risk_adjustment": 1.1,
            },
            "trending_down": {
                "conditions": ["rsi < 50", "ma_trend < 0", "volume_increase"],
                "recommended_actions": ["sell", "monitor"],
                "risk_adjustment": 0.9,
            },
            "sideways": {
                "conditions": ["rsi_between_40_60", "low_volatility", "range_bound"],
                "recommended_actions": ["monitor", "rebalance"],
                "risk_adjustment": 1.0,
            },
            "high_volatility": {
                "conditions": ["high_volatility", "uncertainty", "news_impact"],
                "recommended_actions": ["risk_management", "monitor"],
                "risk_adjustment": 0.7,
            },
        }

    async def generate_action_proposals(
        self, context: AnalysisContext
    ) -> List[ActionProposal]:
        """分析コンテキストに基づくアクション提案の生成"""
        try:
            logger.info(f"アクション提案生成開始: {context.analysis_id}")

            proposals = []

            # 1. 技術分析に基づく提案
            technical_proposals = await self._generate_technical_proposals(context)
            proposals.extend(technical_proposals)

            # 2. リスク管理に基づく提案
            risk_proposals = await self._generate_risk_proposals(context)
            proposals.extend(risk_proposals)

            # 3. 市場環境に基づく提案
            market_proposals = await self._generate_market_proposals(context)
            proposals.extend(market_proposals)

            # 4. ポートフォリオ最適化に基づく提案
            portfolio_proposals = await self._generate_portfolio_proposals(context)
            proposals.extend(portfolio_proposals)

            # 5. 提案の優先度付けとフィルタリング
            filtered_proposals = self._filter_and_rank_proposals(proposals, context)

            # 6. 提案履歴の記録
            self._record_proposals(context.analysis_id, filtered_proposals)

            logger.info(f"アクション提案生成完了: {len(filtered_proposals)}件")
            return filtered_proposals

        except Exception as e:
            logger.error(f"アクション提案生成エラー: {e}")
            return []

    async def _generate_technical_proposals(
        self, context: AnalysisContext
    ) -> List[ActionProposal]:
        """技術分析に基づく提案の生成"""
        proposals = []

        try:
            indicators = context.technical_indicators
            market_data = context.market_data

            # RSI分析
            if "rsi" in indicators:
                rsi = indicators["rsi"]
                if rsi < 30:  # オーバーセル
                    proposal = self._create_proposal_from_template(
                        "buy_signal",
                        context,
                        {
                            "symbol": (
                                context.target_symbols[0]
                                if context.target_symbols
                                else "対象銘柄"
                            ),
                            "rsi_value": rsi,
                        },
                    )
                    proposals.append(proposal)
                elif rsi > 70:  # オーバーボート
                    proposal = self._create_proposal_from_template(
                        "sell_signal",
                        context,
                        {
                            "symbol": (
                                context.target_symbols[0]
                                if context.target_symbols
                                else "対象銘柄"
                            ),
                            "rsi_value": rsi,
                        },
                    )
                    proposals.append(proposal)

            # 移動平均線分析
            if "ma_short" in indicators and "ma_long" in indicators:
                ma_short = indicators["ma_short"]
                ma_long = indicators["ma_long"]
                current_price = market_data.get("current_price", 0)

                if ma_short > ma_long and current_price > ma_short:
                    # ゴールデンクロス
                    proposal = self._create_proposal_from_template(
                        "buy_signal",
                        context,
                        {
                            "symbol": (
                                context.target_symbols[0]
                                if context.target_symbols
                                else "対象銘柄"
                            ),
                            "ma_short": ma_short,
                            "ma_long": ma_long,
                        },
                    )
                    proposals.append(proposal)
                elif ma_short < ma_long and current_price < ma_short:
                    # デッドクロス
                    proposal = self._create_proposal_from_template(
                        "sell_signal",
                        context,
                        {
                            "symbol": (
                                context.target_symbols[0]
                                if context.target_symbols
                                else "対象銘柄"
                            ),
                            "ma_short": ma_short,
                            "ma_long": ma_long,
                        },
                    )
                    proposals.append(proposal)

            # ボラティリティ分析
            if context.volatility_level > 0.3:  # 高ボラティリティ
                proposal = self._create_proposal_from_template(
                    "monitor_signal", context, {"volatility": context.volatility_level}
                )
                proposals.append(proposal)

        except Exception as e:
            logger.error(f"技術分析提案生成エラー: {e}")

        return proposals

    async def _generate_risk_proposals(
        self, context: AnalysisContext
    ) -> List[ActionProposal]:
        """リスク管理に基づく提案の生成"""
        proposals = []

        try:
            risk_metrics = context.risk_metrics

            # 最大ドローダウンチェック
            if "max_drawdown" in risk_metrics:
                max_dd = risk_metrics["max_drawdown"]
                if max_dd > 0.1:  # 10%以上のドローダウン
                    proposal = self._create_proposal_from_template(
                        "risk_management",
                        context,
                        {"max_drawdown": max_dd, "risk_level": "high"},
                    )
                    proposals.append(proposal)

            # ボラティリティリスクチェック
            if "volatility" in risk_metrics:
                volatility = risk_metrics["volatility"]
                if volatility > 0.25:  # 25%以上のボラティリティ
                    proposal = self._create_proposal_from_template(
                        "risk_management",
                        context,
                        {"volatility": volatility, "risk_level": "high"},
                    )
                    proposals.append(proposal)

            # VaR（Value at Risk）チェック
            if "var_95" in risk_metrics:
                var_95 = risk_metrics["var_95"]
                if var_95 > 0.05:  # 5%以上のVaR
                    proposal = self._create_proposal_from_template(
                        "risk_management",
                        context,
                        {"var_95": var_95, "risk_level": "medium"},
                    )
                    proposals.append(proposal)

        except Exception as e:
            logger.error(f"リスク管理提案生成エラー: {e}")

        return proposals

    async def _generate_market_proposals(
        self, context: AnalysisContext
    ) -> List[ActionProposal]:
        """市場環境に基づく提案の生成"""
        proposals = []

        try:
            market_condition = context.market_condition

            # 市場状況に応じた提案
            if market_condition == MarketCondition.BULL:
                # 強気市場での提案
                if context.volatility_level < 0.2:  # 低ボラティリティ
                    proposal = self._create_proposal_from_template(
                        "buy_signal",
                        context,
                        {
                            "market_condition": "bull",
                            "volatility": context.volatility_level,
                        },
                    )
                    proposals.append(proposal)

            elif market_condition == MarketCondition.BEAR:
                # 弱気市場での提案
                proposal = self._create_proposal_from_template(
                    "risk_management",
                    context,
                    {"market_condition": "bear", "defensive_strategy": True},
                )
                proposals.append(proposal)

            elif market_condition == MarketCondition.VOLATILE:
                # 高ボラティリティ市場での提案
                proposal = self._create_proposal_from_template(
                    "monitor_signal",
                    context,
                    {
                        "market_condition": "volatile",
                        "volatility": context.volatility_level,
                    },
                )
                proposals.append(proposal)

            # トレンド分析
            if context.trend_direction == "up" and context.volatility_level < 0.15:
                proposal = self._create_proposal_from_template(
                    "buy_signal", context, {"trend": "up", "low_volatility": True}
                )
                proposals.append(proposal)
            elif context.trend_direction == "down" and context.volatility_level > 0.2:
                proposal = self._create_proposal_from_template(
                    "sell_signal", context, {"trend": "down", "high_volatility": True}
                )
                proposals.append(proposal)

        except Exception as e:
            logger.error(f"市場環境提案生成エラー: {e}")

        return proposals

    async def _generate_portfolio_proposals(
        self, context: AnalysisContext
    ) -> List[ActionProposal]:
        """ポートフォリオ最適化に基づく提案の生成"""
        proposals = []

        try:
            portfolio_status = context.portfolio_status

            # 集中度チェック
            if "concentration_risk" in portfolio_status:
                concentration = portfolio_status["concentration_risk"]
                if concentration > 0.3:  # 30%以上の集中度
                    proposal = self._create_proposal_from_template(
                        "rebalance_signal",
                        context,
                        {
                            "concentration_risk": concentration,
                            "rebalance_reason": "集中度が高すぎる",
                        },
                    )
                    proposals.append(proposal)

            # セクター分散チェック
            if "sector_diversification" in portfolio_status:
                sector_div = portfolio_status["sector_diversification"]
                if sector_div < 0.5:  # 50%未満のセクター分散
                    proposal = self._create_proposal_from_template(
                        "rebalance_signal",
                        context,
                        {
                            "sector_diversification": sector_div,
                            "rebalance_reason": "セクター分散が不十分",
                        },
                    )
                    proposals.append(proposal)

            # リスク調整リターンチェック
            if "risk_adjusted_return" in portfolio_status:
                risk_adj_return = portfolio_status["risk_adjusted_return"]
                if risk_adj_return < 0.05:  # 5%未満のリスク調整リターン
                    proposal = self._create_proposal_from_template(
                        "rebalance_signal",
                        context,
                        {
                            "risk_adjusted_return": risk_adj_return,
                            "rebalance_reason": "リスク調整リターンが低い",
                        },
                    )
                    proposals.append(proposal)

        except Exception as e:
            logger.error(f"ポートフォリオ提案生成エラー: {e}")

        return proposals

    def _create_proposal_from_template(
        self, template_name: str, context: AnalysisContext, variables: Dict[str, Any]
    ) -> ActionProposal:
        """テンプレートからプロポーザルを作成"""
        template = self.proposal_templates.get(template_name, {})

        # 基本情報の設定
        action_id = f"{context.analysis_id}_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        action_type = ActionType(template_name.split("_")[0])

        # 優先度の決定
        priority = self._determine_priority(action_type, context, variables)

        # リスクレベルの調整
        risk_level = template.get("risk_level", 0.5)
        risk_level = self._adjust_risk_level(risk_level, context, variables)

        # 信頼度スコアの計算
        confidence_score = self._calculate_confidence_score(
            action_type, context, variables
        )

        # プロポーザルの作成
        proposal = ActionProposal(
            action_id=action_id,
            action_type=action_type,
            priority=priority,
            title=template.get("title_template", "アクション提案").format(**variables),
            description=template.get("description_template", ""),
            reasoning=self._generate_reasoning(
                template.get("reasoning_templates", []), variables
            ),
            expected_impact=template.get("expected_impact", ""),
            risk_level=risk_level,
            confidence_score=confidence_score,
            execution_time=template.get("execution_time", ""),
            prerequisites=self._generate_prerequisites(action_type, context),
            follow_up_actions=self._generate_follow_up_actions(action_type, context),
            market_condition=context.market_condition,
            target_symbols=context.target_symbols or [],
            deadline=self._calculate_deadline(action_type, context),
        )

        return proposal

    def _determine_priority(
        self,
        action_type: ActionType,
        context: AnalysisContext,
        variables: Dict[str, Any],
    ) -> ActionPriority:
        """優先度の決定"""
        # リスク管理は常に高優先度
        if action_type == ActionType.RISK_MANAGEMENT:
            return ActionPriority.HIGH

        # 市場状況に応じた優先度調整
        if context.market_condition == MarketCondition.VOLATILE:
            if action_type in [ActionType.SELL, ActionType.MONITOR]:
                return ActionPriority.HIGH

        # 信頼度に基づく優先度
        if variables.get("confidence_score", 0.5) > 0.8:
            return ActionPriority.HIGH
        elif variables.get("confidence_score", 0.5) > 0.6:
            return ActionPriority.NORMAL
        else:
            return ActionPriority.LOW

    def _adjust_risk_level(
        self, base_risk: float, context: AnalysisContext, variables: Dict[str, Any]
    ) -> float:
        """リスクレベルの調整"""
        # 市場状況による調整
        if context.market_condition == MarketCondition.VOLATILE:
            base_risk *= 1.2
        elif context.market_condition == MarketCondition.BEAR:
            base_risk *= 1.1

        # ボラティリティによる調整
        if context.volatility_level > 0.3:
            base_risk *= 1.3
        elif context.volatility_level < 0.1:
            base_risk *= 0.8

        return min(base_risk, 1.0)  # 最大1.0に制限

    def _calculate_confidence_score(
        self,
        action_type: ActionType,
        context: AnalysisContext,
        variables: Dict[str, Any],
    ) -> float:
        """信頼度スコアの計算"""
        base_confidence = 0.7

        # 技術指標の信頼度
        if "rsi" in context.technical_indicators:
            rsi = context.technical_indicators["rsi"]
            if rsi < 30 or rsi > 70:  # 極値
                base_confidence += 0.1

        # 市場状況の信頼度
        if context.market_condition == MarketCondition.TRENDING:
            base_confidence += 0.1
        elif context.market_condition == MarketCondition.VOLATILE:
            base_confidence -= 0.1

        # ボラティリティの信頼度
        if context.volatility_level < 0.2:
            base_confidence += 0.05
        elif context.volatility_level > 0.3:
            base_confidence -= 0.1

        return max(0.0, min(1.0, base_confidence))

    def _generate_reasoning(
        self, templates: List[str], variables: Dict[str, Any]
    ) -> List[str]:
        """推論の生成"""
        reasoning = []
        for template in templates:
            try:
                reasoning.append(template.format(**variables))
            except KeyError:
                reasoning.append(template)
        return reasoning

    def _generate_prerequisites(
        self, action_type: ActionType, context: AnalysisContext
    ) -> List[str]:
        """前提条件の生成"""
        prerequisites = []

        if action_type == ActionType.BUY:
            prerequisites.extend(["十分な資金の確保", "リスク許容度の確認", "投資目標との整合性確認"])
        elif action_type == ActionType.SELL:
            prerequisites.extend(["税務影響の確認", "代替投資先の検討", "損失確定の覚悟"])
        elif action_type == ActionType.REBALANCE:
            prerequisites.extend(["現在のポートフォリオ構成の確認", "目標配分の設定", "取引コストの計算"])

        return prerequisites

    def _generate_follow_up_actions(
        self, action_type: ActionType, context: AnalysisContext
    ) -> List[str]:
        """フォローアップアクションの生成"""
        follow_ups = []

        if action_type == ActionType.BUY:
            follow_ups.extend(["価格監視の継続", "ストップロスの設定", "利益確定ポイントの設定"])
        elif action_type == ActionType.SELL:
            follow_ups.extend(["資金の再投資検討", "ポートフォリオの再評価", "次の投資機会の探索"])
        elif action_type == ActionType.MONITOR:
            follow_ups.extend(["定期的な価格チェック", "重要指標の監視", "市場ニュースの確認"])

        return follow_ups

    def _calculate_deadline(
        self, action_type: ActionType, context: AnalysisContext
    ) -> Optional[datetime]:
        """期限の計算"""
        if action_type == ActionType.RISK_MANAGEMENT:
            return datetime.now() + timedelta(hours=1)  # 1時間以内
        elif action_type in [ActionType.BUY, ActionType.SELL]:
            return datetime.now() + timedelta(days=1)  # 1日以内
        elif action_type == ActionType.REBALANCE:
            return datetime.now() + timedelta(days=7)  # 1週間以内
        else:
            return None

    def _filter_and_rank_proposals(
        self, proposals: List[ActionProposal], context: AnalysisContext
    ) -> List[ActionProposal]:
        """提案のフィルタリングとランキング"""
        # 信頼度フィルタリング
        min_confidence = self.config.get("action_proposal", {}).get(
            "min_confidence_threshold", 0.6
        )
        filtered_proposals = [
            p for p in proposals if p.confidence_score >= min_confidence
        ]

        # 重複除去
        unique_proposals = self._remove_duplicate_proposals(filtered_proposals)

        # 優先度と信頼度でソート
        sorted_proposals = sorted(
            unique_proposals,
            key=lambda p: (p.priority.value, p.confidence_score),
            reverse=True,
        )

        # 最大提案数の制限
        max_proposals = self.config.get("action_proposal", {}).get(
            "max_proposals_per_analysis", 5
        )
        return sorted_proposals[:max_proposals]

    def _remove_duplicate_proposals(
        self, proposals: List[ActionProposal]
    ) -> List[ActionProposal]:
        """重複提案の除去"""
        seen_actions = set()
        unique_proposals = []

        for proposal in proposals:
            action_key = (proposal.action_type, proposal.title)
            if action_key not in seen_actions:
                seen_actions.add(action_key)
                unique_proposals.append(proposal)

        return unique_proposals

    def _record_proposals(self, analysis_id: str, proposals: List[ActionProposal]):
        """提案履歴の記録"""
        record = {
            "analysis_id": analysis_id,
            "timestamp": datetime.now(),
            "proposal_count": len(proposals),
            "proposals": [asdict(p) for p in proposals],
        }

        self.action_history.append(record)

        # 履歴の保存（最新50件を保持）
        if len(self.action_history) > 50:
            self.action_history = self.action_history[-50:]

    def get_proposal_statistics(self) -> Dict[str, Any]:
        """提案統計の取得"""
        if not self.action_history:
            return {"total_proposals": 0, "proposal_types": {}, "success_rate": 0.0}

        total_proposals = sum(
            record["proposal_count"] for record in self.action_history
        )

        # 提案タイプ別統計
        proposal_types = {}
        for record in self.action_history:
            for proposal in record["proposals"]:
                action_type = proposal["action_type"]
                proposal_types[action_type] = proposal_types.get(action_type, 0) + 1

        return {
            "total_proposals": total_proposals,
            "proposal_types": proposal_types,
            "recent_proposals": (
                self.action_history[-10:] if self.action_history else []
            ),
        }


# 使用例
async def main():
    """使用例"""
    # アクション提案システムの初期化
    proposal_system = EnhancedAutoActionProposalSystem()

    # 分析コンテキストの作成（例）
    context = AnalysisContext(
        analysis_id="analysis_001",
        analysis_type="ultra_fast",
        market_data={"current_price": 100, "volume": 1000000},
        technical_indicators={"rsi": 25, "ma_short": 98, "ma_long": 95},
        sentiment_data={"overall_sentiment": 0.7},
        risk_metrics={"max_drawdown": 0.05, "volatility": 0.15},
        performance_metrics={"sharpe_ratio": 1.2},
        portfolio_status={"concentration_risk": 0.2},
        user_preferences={"risk_tolerance": "medium"},
        market_condition=MarketCondition.BULL,
        volatility_level=0.15,
        trend_direction="up",
        support_resistance_levels={"support": 95, "resistance": 105},
    )

    # アクション提案の生成
    proposals = await proposal_system.generate_action_proposals(context)

    # 結果の表示
    for proposal in proposals:
        print(f"提案ID: {proposal.action_id}")
        print(f"アクションタイプ: {proposal.action_type.value}")
        print(f"優先度: {proposal.priority.value}")
        print(f"タイトル: {proposal.title}")
        print(f"説明: {proposal.description}")
        print(f"信頼度: {proposal.confidence_score:.2f}")
        print(f"リスクレベル: {proposal.risk_level:.2f}")
        print("---")


if __name__ == "__main__":
    asyncio.run(main())
