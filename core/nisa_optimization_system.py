#!/usr/bin/env python3
"""
新NISA最適化提案システム
2024年1月開始の新NISA制度に対応した最適化提案機能
非課税枠利用率90%以上を目標としたAI最適化システム
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class OptimizationRecommendation:
    """最適化推奨事項"""

    type: str
    priority: str
    title: str
    description: str
    expected_impact: float
    implementation_difficulty: str
    timeframe: str
    required_action: str
    potential_savings: float


@dataclass
class AIInvestmentStrategy:
    """AI投資戦略"""

    strategy_name: str
    description: str
    risk_level: str
    expected_return: float
    timeframe: str
    confidence: float
    growth_quota_allocation: Dict[str, Any]
    accumulation_quota_allocation: Dict[str, Any]
    optimization_score: float


@dataclass
class OptimizationReport:
    """最適化レポート"""

    current_score: float
    target_score: float
    improvement_potential: float
    recommendations: List[OptimizationRecommendation]
    ai_strategies: List[AIInvestmentStrategy]
    risk_analysis: Dict[str, Any]
    tax_optimization: Dict[str, Any]
    implementation_plan: Dict[str, Any]


class NisaOptimizationSystem:
    """新NISA最適化提案システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 最適化設定
        self.target_utilization_rate = 90.0  # 目標利用率90%
        self.optimization_threshold = 0.85  # 最適化閾値85%
        self.tax_rate = 0.30  # 税率30%

        # NISA制度の基本設定
        self.growth_annual_limit = 2400000  # 成長投資枠年間240万円
        self.accumulation_annual_limit = 400000  # つみたて投資枠年間40万円

        # AI戦略データベース
        self.ai_strategies = self._initialize_ai_strategies()

    def _initialize_ai_strategies(self) -> List[Dict[str, Any]]:
        """AI戦略の初期化"""
        return [
            {
                "name": "バランス型投資戦略",
                "description": "成長株と安定株のバランスを取った投資戦略",
                "risk_level": "MEDIUM",
                "expected_return": 8.0,
                "timeframe": "3-5年",
                "confidence": 0.85,
                "growth_allocation": {"growth_stocks": 0.6, "value_stocks": 0.4},
                "accumulation_allocation": {"index_funds": 0.7, "bond_funds": 0.3},
            },
            {
                "name": "アグレッシブ成長戦略",
                "description": "高成長株に重点を置いた投資戦略",
                "risk_level": "HIGH",
                "expected_return": 12.0,
                "timeframe": "5-10年",
                "confidence": 0.75,
                "growth_allocation": {"growth_stocks": 0.8, "tech_stocks": 0.2},
                "accumulation_allocation": {"growth_funds": 0.9, "index_funds": 0.1},
            },
            {
                "name": "保守的安定戦略",
                "description": "安定性を重視した投資戦略",
                "risk_level": "LOW",
                "expected_return": 5.0,
                "timeframe": "10-20年",
                "confidence": 0.90,
                "growth_allocation": {"value_stocks": 0.7, "dividend_stocks": 0.3},
                "accumulation_allocation": {"bond_funds": 0.6, "index_funds": 0.4},
            },
        ]

    def generate_optimization_report(
        self, quota_status: Dict[str, Any], portfolio: Dict[str, Any]
    ) -> OptimizationReport:
        """最適化レポートの生成"""
        try:
            # 現在のスコア計算
            current_score = self._calculate_current_score(quota_status, portfolio)

            # 目標スコアの設定
            target_score = 90.0

            # 改善ポテンシャルの計算
            improvement_potential = max(0, target_score - current_score)

            # 推奨事項の生成
            recommendations = self._generate_recommendations(quota_status, portfolio)

            # AI戦略の提案
            ai_strategies = self._generate_ai_strategies(quota_status, portfolio)

            # リスク分析
            risk_analysis = self._analyze_risk(portfolio)

            # 税務最適化
            tax_optimization = self._calculate_tax_optimization(quota_status, portfolio)

            # 実装計画
            implementation_plan = self._create_implementation_plan(
                recommendations, ai_strategies
            )

            return OptimizationReport(
                current_score=current_score,
                target_score=target_score,
                improvement_potential=improvement_potential,
                recommendations=recommendations,
                ai_strategies=ai_strategies,
                risk_analysis=risk_analysis,
                tax_optimization=tax_optimization,
                implementation_plan=implementation_plan,
            )

        except Exception as e:
            self.logger.error(f"最適化レポート生成エラー: {e}")
            return OptimizationReport(
                current_score=0,
                target_score=90,
                improvement_potential=90,
                recommendations=[],
                ai_strategies=[],
                risk_analysis={},
                tax_optimization={},
                implementation_plan={},
            )

    def _calculate_current_score(
        self, quota_status: Dict[str, Any], portfolio: Dict[str, Any]
    ) -> float:
        """現在のスコア計算"""
        try:
            # 利用率スコア
            growth_utilization = quota_status.get("growth_investment", {}).get(
                "utilization_rate", 0
            )
            accumulation_utilization = quota_status.get(
                "accumulation_investment", {}
            ).get("utilization_rate", 0)
            utilization_score = (growth_utilization + accumulation_utilization) / 2

            # ポートフォリオスコア
            portfolio_score = self._calculate_portfolio_score(portfolio)

            # 税務効率スコア
            tax_efficiency_score = self._calculate_tax_efficiency_score(
                quota_status, portfolio
            )

            # 総合スコア
            total_score = (
                utilization_score * 0.4
                + portfolio_score * 0.3
                + tax_efficiency_score * 0.3
            )

            return round(total_score, 2)

        except Exception as e:
            self.logger.error(f"現在スコア計算エラー: {e}")
            return 0.0

    def _calculate_portfolio_score(self, portfolio: Dict[str, Any]) -> float:
        """ポートフォリオスコアの計算"""
        try:
            positions = portfolio.get("positions", [])
            if not positions:
                return 0.0

            # 分散度スコア
            diversification_score = min(len(positions) * 10, 100)

            # リターンスコア
            unrealized_profit_loss = portfolio.get("unrealized_profit_loss", 0)
            total_cost = portfolio.get("total_cost", 0)
            return_score = 50.0  # デフォルトスコア

            if total_cost > 0:
                return_rate = (unrealized_profit_loss / total_cost) * 100
                return_score = max(0, min(100, 50 + return_rate))

            # 総合ポートフォリオスコア
            portfolio_score = diversification_score * 0.6 + return_score * 0.4

            return round(portfolio_score, 2)

        except Exception as e:
            self.logger.error(f"ポートフォリオスコア計算エラー: {e}")
            return 0.0

    def _calculate_tax_efficiency_score(
        self, quota_status: Dict[str, Any], portfolio: Dict[str, Any]
    ) -> float:
        """税務効率スコアの計算"""
        try:
            growth_used = quota_status.get("growth_investment", {}).get(
                "used_amount", 0
            )
            accumulation_used = quota_status.get("accumulation_investment", {}).get(
                "used_amount", 0
            )
            total_used = growth_used + accumulation_used

            # 税務節約額
            tax_savings = total_used * self.tax_rate

            # 税務効率スコア
            total_limit = self.growth_annual_limit + self.accumulation_annual_limit
            tax_efficiency = (total_used / total_limit) * 100 if total_limit > 0 else 0

            return round(tax_efficiency, 2)

        except Exception as e:
            self.logger.error(f"税務効率スコア計算エラー: {e}")
            return 0.0

    def _generate_recommendations(
        self, quota_status: Dict[str, Any], portfolio: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """推奨事項の生成"""
        try:
            recommendations = []

            # 成長投資枠の推奨事項
            growth_utilization = quota_status.get("growth_investment", {}).get(
                "utilization_rate", 0
            )
            if growth_utilization < 80:
                recommendations.append(
                    OptimizationRecommendation(
                        type="GROWTH_QUOTA_OPTIMIZATION",
                        priority="HIGH",
                        title="成長投資枠の活用促進",
                        description="成長投資枠の活用率を向上させることで、年間最大72万円の税務節約が可能です",
                        expected_impact=72.0,
                        implementation_difficulty="MEDIUM",
                        timeframe="1-3ヶ月",
                        required_action="成長株への投資を増やす",
                        potential_savings=72.0,
                    )
                )

            # つみたて投資枠の推奨事項
            accumulation_utilization = quota_status.get(
                "accumulation_investment", {}
            ).get("utilization_rate", 0)
            if accumulation_utilization < 80:
                recommendations.append(
                    OptimizationRecommendation(
                        type="ACCUMULATION_QUOTA_OPTIMIZATION",
                        priority="MEDIUM",
                        title="つみたて投資枠の活用促進",
                        description="つみたて投資枠の活用率を向上させることで、年間最大12万円の税務節約が可能です",
                        expected_impact=12.0,
                        implementation_difficulty="LOW",
                        timeframe="3-6ヶ月",
                        required_action="積立投資の開始・増額",
                        potential_savings=12.0,
                    )
                )

            # ポートフォリオ分散の推奨事項
            positions = portfolio.get("positions", [])
            if len(positions) < 5:
                recommendations.append(
                    OptimizationRecommendation(
                        type="PORTFOLIO_DIVERSIFICATION",
                        priority="MEDIUM",
                        title="ポートフォリオの分散投資",
                        description="銘柄数を増やすことで、リスクを軽減し、安定したリターンを得られます",
                        expected_impact=15.0,
                        implementation_difficulty="MEDIUM",
                        timeframe="6-12ヶ月",
                        required_action="新規銘柄への投資",
                        potential_savings=0.0,
                    )
                )

            return recommendations

        except Exception as e:
            self.logger.error(f"推奨事項生成エラー: {e}")
            return []

    def _generate_ai_strategies(
        self, quota_status: Dict[str, Any], portfolio: Dict[str, Any]
    ) -> List[AIInvestmentStrategy]:
        """AI戦略の生成"""
        try:
            strategies = []

            # 現在のリスクプロファイルの分析
            risk_profile = self._analyze_risk_profile(portfolio)

            # リスクプロファイルに基づく戦略の選択
            for strategy_data in self.ai_strategies:
                if self._is_strategy_suitable(
                    strategy_data, risk_profile, quota_status
                ):
                    strategy = AIInvestmentStrategy(
                        strategy_name=strategy_data["name"],
                        description=strategy_data["description"],
                        risk_level=strategy_data["risk_level"],
                        expected_return=strategy_data["expected_return"],
                        timeframe=strategy_data["timeframe"],
                        confidence=strategy_data["confidence"],
                        growth_quota_allocation=strategy_data["growth_allocation"],
                        accumulation_quota_allocation=strategy_data[
                            "accumulation_allocation"
                        ],
                        optimization_score=self._calculate_strategy_score(
                            strategy_data, quota_status, portfolio
                        ),
                    )
                    strategies.append(strategy)

            # スコア順にソート
            strategies.sort(key=lambda x: x.optimization_score, reverse=True)

            return strategies[:3]  # 上位3つの戦略を返す

        except Exception as e:
            self.logger.error(f"AI戦略生成エラー: {e}")
            return []

    def _analyze_risk_profile(self, portfolio: Dict[str, Any]) -> str:
        """リスクプロファイルの分析"""
        try:
            positions = portfolio.get("positions", [])
            if not positions:
                return "CONSERVATIVE"

            # 簡易リスク分析
            position_count = len(positions)
            if position_count >= 10:
                return "AGGRESSIVE"
            elif position_count >= 5:
                return "BALANCED"
            else:
                return "CONSERVATIVE"

        except Exception as e:
            self.logger.error(f"リスクプロファイル分析エラー: {e}")
            return "CONSERVATIVE"

    def _is_strategy_suitable(
        self,
        strategy_data: Dict[str, Any],
        risk_profile: str,
        quota_status: Dict[str, Any],
    ) -> bool:
        """戦略の適合性判定"""
        try:
            strategy_risk = strategy_data["risk_level"]

            # リスクプロファイルとの適合性
            if risk_profile == "AGGRESSIVE" and strategy_risk in ["HIGH", "MEDIUM"]:
                return True
            elif risk_profile == "BALANCED" and strategy_risk in ["MEDIUM", "LOW"]:
                return True
            elif risk_profile == "CONSERVATIVE" and strategy_risk == "LOW":
                return True

            return False

        except Exception as e:
            self.logger.error(f"戦略適合性判定エラー: {e}")
            return False

    def _calculate_strategy_score(
        self,
        strategy_data: Dict[str, Any],
        quota_status: Dict[str, Any],
        portfolio: Dict[str, Any],
    ) -> float:
        """戦略スコアの計算"""
        try:
            # 基本スコア
            base_score = strategy_data["confidence"] * 100

            # 期待リターンスコア
            expected_return = strategy_data["expected_return"]
            return_score = min(
                expected_return * 5, 100
            )  # 期待リターンを5倍してスコア化

            # リスクスコア
            risk_level = strategy_data["risk_level"]
            risk_scores = {"LOW": 80, "MEDIUM": 70, "HIGH": 60}
            risk_score = risk_scores.get(risk_level, 50)

            # 総合スコア
            total_score = base_score * 0.4 + return_score * 0.3 + risk_score * 0.3

            return round(total_score, 2)

        except Exception as e:
            self.logger.error(f"戦略スコア計算エラー: {e}")
            return 0.0

    def _analyze_risk(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """リスク分析"""
        try:
            positions = portfolio.get("positions", [])

            # 分散度スコア
            diversification_score = min(len(positions) * 10, 100)

            # セクター集中度（簡易版）
            sector_concentration = 100 / len(positions) if positions else 0

            # リスクレベル
            if diversification_score >= 80 and sector_concentration <= 20:
                risk_level = "LOW"
            elif diversification_score >= 60 and sector_concentration <= 40:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"

            return {
                "diversification_score": diversification_score,
                "sector_concentration": sector_concentration,
                "risk_level": risk_level,
                "recommendations": self._get_risk_recommendations(
                    risk_level, diversification_score
                ),
            }

        except Exception as e:
            self.logger.error(f"リスク分析エラー: {e}")
            return {
                "diversification_score": 0,
                "sector_concentration": 0,
                "risk_level": "UNKNOWN",
                "recommendations": [],
            }

    def _get_risk_recommendations(
        self, risk_level: str, diversification_score: float
    ) -> List[str]:
        """リスク推奨事項の取得"""
        try:
            recommendations = []

            if risk_level == "HIGH":
                recommendations.append(
                    "ポートフォリオの分散を図ることで、リスクを軽減できます"
                )
                recommendations.append("異なるセクターへの投資を検討してください")
            elif risk_level == "MEDIUM":
                recommendations.append(
                    "さらなる分散投資を検討することで、リスクを軽減できます"
                )
            else:
                recommendations.append("現在のポートフォリオは良好な分散状態です")

            if diversification_score < 60:
                recommendations.append("銘柄数を増やすことで、リスクを軽減できます")

            return recommendations

        except Exception as e:
            self.logger.error(f"リスク推奨事項取得エラー: {e}")
            return []

    def _calculate_tax_optimization(
        self, quota_status: Dict[str, Any], portfolio: Dict[str, Any]
    ) -> Dict[str, Any]:
        """税務最適化の計算"""
        try:
            growth_used = quota_status.get("growth_investment", {}).get(
                "used_amount", 0
            )
            accumulation_used = quota_status.get("accumulation_investment", {}).get(
                "used_amount", 0
            )
            total_used = growth_used + accumulation_used

            # 現在の税務節約額
            current_tax_savings = total_used * self.tax_rate

            # 潜在的な税務節約額
            growth_available = quota_status.get("growth_investment", {}).get(
                "available_amount", 0
            )
            accumulation_available = quota_status.get(
                "accumulation_investment", {}
            ).get("available_amount", 0)
            potential_tax_savings = (
                growth_available + accumulation_available
            ) * self.tax_rate

            # 最適化スコア
            total_limit = self.growth_annual_limit + self.accumulation_annual_limit
            optimization_score = (
                (total_used / total_limit) * 100 if total_limit > 0 else 0
            )

            return {
                "current_tax_savings": current_tax_savings,
                "potential_tax_savings": potential_tax_savings,
                "optimization_score": optimization_score,
                "tax_rate": self.tax_rate,
                "recommendations": self._get_tax_recommendations(quota_status),
            }

        except Exception as e:
            self.logger.error(f"税務最適化計算エラー: {e}")
            return {
                "current_tax_savings": 0,
                "potential_tax_savings": 0,
                "optimization_score": 0,
                "tax_rate": self.tax_rate,
                "recommendations": [],
            }

    def _get_tax_recommendations(self, quota_status: Dict[str, Any]) -> List[str]:
        """税務推奨事項の取得"""
        try:
            recommendations = []

            growth_utilization = quota_status.get("growth_investment", {}).get(
                "utilization_rate", 0
            )
            accumulation_utilization = quota_status.get(
                "accumulation_investment", {}
            ).get("utilization_rate", 0)

            if growth_utilization < 80:
                recommendations.append(
                    "成長投資枠の活用を増やすことで、年間最大72万円の税務節約が可能です"
                )

            if accumulation_utilization < 80:
                recommendations.append(
                    "つみたて投資枠の活用を増やすことで、年間最大12万円の税務節約が可能です"
                )

            if growth_utilization < 50 and accumulation_utilization < 50:
                recommendations.append(
                    "両枠の活用率が低いため、積極的な投資戦略の見直しを推奨します"
                )

            return recommendations

        except Exception as e:
            self.logger.error(f"税務推奨事項取得エラー: {e}")
            return []

    def _create_implementation_plan(
        self,
        recommendations: List[OptimizationRecommendation],
        ai_strategies: List[AIInvestmentStrategy],
    ) -> Dict[str, Any]:
        """実装計画の作成"""
        try:
            # 優先度別の実装計画
            high_priority = [r for r in recommendations if r.priority == "HIGH"]
            medium_priority = [r for r in recommendations if r.priority == "MEDIUM"]
            low_priority = [r for r in recommendations if r.priority == "LOW"]

            # 推奨AI戦略
            recommended_strategy = ai_strategies[0] if ai_strategies else None

            return {
                "high_priority_actions": [asdict(r) for r in high_priority],
                "medium_priority_actions": [asdict(r) for r in medium_priority],
                "low_priority_actions": [asdict(r) for r in low_priority],
                "recommended_strategy": (
                    asdict(recommended_strategy) if recommended_strategy else None
                ),
                "implementation_timeline": self._create_timeline(recommendations),
                "success_metrics": self._define_success_metrics(),
            }

        except Exception as e:
            self.logger.error(f"実装計画作成エラー: {e}")
            return {}

    def _create_timeline(
        self, recommendations: List[OptimizationRecommendation]
    ) -> Dict[str, Any]:
        """実装タイムラインの作成"""
        try:
            timeline = {
                "immediate": [],  # 1ヶ月以内
                "short_term": [],  # 1-3ヶ月
                "medium_term": [],  # 3-6ヶ月
                "long_term": [],  # 6ヶ月以上
            }

            for rec in recommendations:
                if "1ヶ月" in rec.timeframe or "immediate" in rec.timeframe.lower():
                    timeline["immediate"].append(rec.title)
                elif "1-3ヶ月" in rec.timeframe or "3ヶ月" in rec.timeframe:
                    timeline["short_term"].append(rec.title)
                elif "3-6ヶ月" in rec.timeframe or "6ヶ月" in rec.timeframe:
                    timeline["medium_term"].append(rec.title)
                else:
                    timeline["long_term"].append(rec.title)

            return timeline

        except Exception as e:
            self.logger.error(f"タイムライン作成エラー: {e}")
            return {}

    def _define_success_metrics(self) -> Dict[str, Any]:
        """成功指標の定義"""
        try:
            return {
                "target_utilization_rate": self.target_utilization_rate,
                "target_tax_savings": 84.0,  # 年間最大84万円
                "target_portfolio_diversification": 80.0,
                "target_risk_level": "MEDIUM",
                "kpis": [
                    "NISA枠利用率90%以上",
                    "年間税務節約額84万円以上",
                    "ポートフォリオ分散度80%以上",
                    "リスクレベルMEDIUM以下",
                ],
            }

        except Exception as e:
            self.logger.error(f"成功指標定義エラー: {e}")
            return {}
