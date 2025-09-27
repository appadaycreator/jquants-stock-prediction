#!/usr/bin/env python3
"""
個別銘柄リスク管理システム統合版
期待効果: 損失を60-80%削減
実装難易度: 🟡 中
推定工数: 2-3日

統合機能:
1. 個別銘柄の動的損切り設定
2. 個別銘柄のボラティリティベースリスク調整
3. 個別銘柄の相関分析による分散投資推奨
4. 個別銘柄の最大損失額設定
5. 横展開: ポートフォリオ全体のリスク管理にも応用
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import asyncio
import aiohttp

# 個別システムのインポート
try:
    from individual_stock_risk_management import IndividualStockRiskManager, RiskLevel
    from advanced_volatility_risk_adjustment import (
        AdvancedVolatilityRiskAdjustment,
        VolatilityRegime,
    )
    from correlation_analysis_system import (
        CorrelationAnalysisSystem,
        DiversificationLevel,
    )
    from max_loss_management_system import MaxLossManagementSystem, LossLevel
except ImportError as e:
    logging.warning(f"個別システムのインポートに失敗: {e}")

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("integrated_individual_risk_management.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class IntegratedRiskLevel(Enum):
    """統合リスクレベル"""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class IntegratedRiskProfile:
    """統合リスクプロファイル"""

    symbol: str
    timestamp: datetime
    individual_risk_score: float
    volatility_risk_score: float
    correlation_risk_score: float
    loss_risk_score: float
    integrated_risk_score: float
    risk_level: IntegratedRiskLevel
    risk_factors: List[str]
    recommended_actions: List[str]
    position_size_recommendation: float
    stop_loss_recommendation: float
    max_loss_recommendation: float
    diversification_recommendation: List[str]


@dataclass
class PortfolioRiskSummary:
    """ポートフォリオリスクサマリー"""

    timestamp: datetime
    total_stocks: int
    average_risk_score: float
    high_risk_stocks: List[str]
    critical_risk_stocks: List[str]
    portfolio_diversification_level: DiversificationLevel
    overall_risk_level: IntegratedRiskLevel
    risk_concentration: Dict[str, float]
    recommended_portfolio_actions: List[str]
    individual_risk_profiles: Dict[str, IntegratedRiskProfile]


class IntegratedIndividualRiskManagement:
    """統合個別銘柄リスク管理システム"""

    def __init__(self, account_value: float = 1000000):
        self.account_value = account_value

        # 個別システムの初期化
        self.individual_risk_manager = IndividualStockRiskManager(account_value)
        self.volatility_risk_adjuster = AdvancedVolatilityRiskAdjustment()
        self.correlation_analyzer = CorrelationAnalysisSystem()
        self.max_loss_manager = MaxLossManagementSystem(account_value)

        # 統合リスク履歴
        self.integrated_risk_history = {}
        self.portfolio_risk_history = []

        # リスク重み
        self.risk_weights = {
            "individual_risk": 0.25,
            "volatility_risk": 0.25,
            "correlation_risk": 0.25,
            "loss_risk": 0.25,
        }

    async def analyze_integrated_risk(
        self, symbol: str, current_price: float
    ) -> IntegratedRiskProfile:
        """統合リスク分析"""
        try:
            logger.info(f"統合リスク分析開始: {symbol}")

            # 個別リスク分析
            individual_risk_profile = (
                await self.individual_risk_manager.analyze_individual_stock_risk(
                    symbol, current_price
                )
            )

            # ボラティリティリスク分析
            volatility_metrics = (
                await self.volatility_risk_adjuster.analyze_volatility_risk(symbol)
            )

            # 相関リスク分析
            correlation_metrics = (
                await self.correlation_analyzer.analyze_correlation_risk([symbol])
            )

            # 最大損失リスク分析
            loss_status = self.max_loss_manager.update_position_price(
                symbol, current_price
            )

            # 統合リスクスコア計算
            integrated_risk_score = self._calculate_integrated_risk_score(
                individual_risk_profile,
                volatility_metrics,
                correlation_metrics,
                loss_status,
            )

            # 統合リスクレベル判定
            risk_level = self._determine_integrated_risk_level(integrated_risk_score)

            # リスク要因特定
            risk_factors = self._identify_risk_factors(
                individual_risk_profile,
                volatility_metrics,
                correlation_metrics,
                loss_status,
            )

            # 推奨アクション生成
            recommended_actions = self._generate_recommended_actions(
                risk_level, risk_factors, individual_risk_profile
            )

            # ポジション推奨事項
            position_recommendations = self._generate_position_recommendations(
                symbol, integrated_risk_score, individual_risk_profile
            )

            # 統合リスクプロファイル作成
            integrated_profile = IntegratedRiskProfile(
                symbol=symbol,
                timestamp=datetime.now(),
                individual_risk_score=individual_risk_profile.total_risk_score,
                volatility_risk_score=volatility_metrics.volatility_risk_score,
                correlation_risk_score=correlation_metrics.correlation_risk_score,
                loss_risk_score=(
                    abs(loss_status.loss_percent)
                    if hasattr(loss_status, "loss_percent")
                    else 0.0
                ),
                integrated_risk_score=integrated_risk_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommended_actions=recommended_actions,
                position_size_recommendation=position_recommendations["position_size"],
                stop_loss_recommendation=position_recommendations["stop_loss"],
                max_loss_recommendation=position_recommendations["max_loss"],
                diversification_recommendation=position_recommendations[
                    "diversification"
                ],
            )

            # 履歴に保存
            self.integrated_risk_history[symbol] = integrated_profile

            logger.info(
                f"統合リスク分析完了: {symbol} - リスクレベル: {risk_level.value}"
            )
            return integrated_profile

        except Exception as e:
            logger.error(f"統合リスク分析エラー: {symbol} - {e}")
            return self._create_default_integrated_risk_profile(symbol)

    def _calculate_integrated_risk_score(
        self,
        individual_risk_profile,
        volatility_metrics,
        correlation_metrics,
        loss_status,
    ) -> float:
        """統合リスクスコア計算"""
        try:
            # 個別リスクスコア
            individual_score = individual_risk_profile.total_risk_score

            # ボラティリティリスクスコア
            volatility_score = volatility_metrics.volatility_risk_score

            # 相関リスクスコア
            correlation_score = correlation_metrics.correlation_risk_score

            # 損失リスクスコア
            loss_score = (
                abs(loss_status.loss_percent)
                if hasattr(loss_status, "loss_percent")
                else 0.0
            )

            # 重み付き統合リスクスコア
            integrated_score = (
                individual_score * self.risk_weights["individual_risk"]
                + volatility_score * self.risk_weights["volatility_risk"]
                + correlation_score * self.risk_weights["correlation_risk"]
                + loss_score * self.risk_weights["loss_risk"]
            )

            return min(integrated_score, 1.0)
        except Exception as e:
            logger.error(f"統合リスクスコア計算エラー: {e}")
            return 0.5

    def _determine_integrated_risk_level(
        self, risk_score: float
    ) -> IntegratedRiskLevel:
        """統合リスクレベル判定"""
        if risk_score < 0.2:
            return IntegratedRiskLevel.VERY_LOW
        elif risk_score < 0.4:
            return IntegratedRiskLevel.LOW
        elif risk_score < 0.6:
            return IntegratedRiskLevel.MEDIUM
        elif risk_score < 0.8:
            return IntegratedRiskLevel.HIGH
        elif risk_score < 0.9:
            return IntegratedRiskLevel.VERY_HIGH
        else:
            return IntegratedRiskLevel.CRITICAL

    def _identify_risk_factors(
        self,
        individual_risk_profile,
        volatility_metrics,
        correlation_metrics,
        loss_status,
    ) -> List[str]:
        """リスク要因特定"""
        risk_factors = []

        try:
            # 個別リスク要因
            if individual_risk_profile.risk_level in [
                RiskLevel.HIGH,
                RiskLevel.CRITICAL,
            ]:
                risk_factors.append("高個別リスク")

            # ボラティリティリスク要因
            if volatility_metrics.volatility_regime in [
                VolatilityRegime.HIGH,
                VolatilityRegime.EXTREME,
            ]:
                risk_factors.append("高ボラティリティ")

            if volatility_metrics.volatility_clustering:
                risk_factors.append("ボラティリティクラスタリング")

            # 相関リスク要因
            if correlation_metrics.correlation_risk_score > 0.7:
                risk_factors.append("高相関リスク")

            if correlation_metrics.diversification_score < 0.5:
                risk_factors.append("分散投資不足")

            # 損失リスク要因
            if hasattr(loss_status, "loss_level"):
                if loss_status.loss_level in [LossLevel.SEVERE, LossLevel.CRITICAL]:
                    risk_factors.append("重大な損失")
                elif loss_status.loss_level == LossLevel.SIGNIFICANT:
                    risk_factors.append("重要な損失")

            return risk_factors
        except Exception as e:
            logger.error(f"リスク要因特定エラー: {e}")
            return ["分析エラー"]

    def _generate_recommended_actions(
        self,
        risk_level: IntegratedRiskLevel,
        risk_factors: List[str],
        individual_risk_profile,
    ) -> List[str]:
        """推奨アクション生成"""
        actions = []

        try:
            # リスクレベルに応じた推奨事項
            if risk_level == IntegratedRiskLevel.CRITICAL:
                actions.append("緊急のリスク削減が必要です")
                actions.append("ポジションサイズを大幅に削減してください")
                actions.append("損切りを即座に実行してください")
            elif risk_level == IntegratedRiskLevel.VERY_HIGH:
                actions.append("リスク削減を強く推奨します")
                actions.append("ポジションサイズを削減してください")
                actions.append("損切りを検討してください")
            elif risk_level == IntegratedRiskLevel.HIGH:
                actions.append("リスク監視を強化してください")
                actions.append("ポジションサイズの見直しを検討してください")
            elif risk_level == IntegratedRiskLevel.MEDIUM:
                actions.append("現在のリスクレベルを維持してください")
                actions.append("定期的なリスク監視を継続してください")
            else:
                actions.append("現在のリスクレベルは適切です")

            # リスク要因に応じた推奨事項
            if "高ボラティリティ" in risk_factors:
                actions.append(
                    "ボラティリティが高いため、ポジションサイズを削減してください"
                )

            if "高相関リスク" in risk_factors:
                actions.append("相関リスクが高いため、分散投資を検討してください")

            if "分散投資不足" in risk_factors:
                actions.append("異なるセクターへの分散投資を推奨します")

            if "重大な損失" in risk_factors:
                actions.append("重大な損失が発生しています。緊急対応が必要です")

            return actions
        except Exception as e:
            logger.error(f"推奨アクション生成エラー: {e}")
            return ["分析エラーにより推奨事項を生成できませんでした"]

    def _generate_position_recommendations(
        self, symbol: str, integrated_risk_score: float, individual_risk_profile
    ) -> Dict[str, Any]:
        """ポジション推奨事項生成"""
        try:
            # リスクスコアに基づくポジションサイズ調整
            base_position_size = individual_risk_profile.recommended_position_size
            risk_adjustment = 1 - (
                integrated_risk_score * 0.5
            )  # リスクが高いほどポジションサイズを削減
            adjusted_position_size = base_position_size * risk_adjustment

            # ストップロス推奨
            base_stop_loss = individual_risk_profile.dynamic_stop_loss
            stop_loss_adjustment = 1 + (
                integrated_risk_score * 0.3
            )  # リスクが高いほどストップロスを厳格化
            adjusted_stop_loss = base_stop_loss * stop_loss_adjustment

            # 最大損失推奨
            max_loss_adjustment = 1 - (
                integrated_risk_score * 0.4
            )  # リスクが高いほど最大損失を削減
            adjusted_max_loss = (
                individual_risk_profile.max_loss_amount * max_loss_adjustment
            )

            # 分散投資推奨
            diversification_recommendations = []
            if integrated_risk_score > 0.7:
                diversification_recommendations.append(
                    "異なるセクターへの分散投資を強く推奨します"
                )
            elif integrated_risk_score > 0.5:
                diversification_recommendations.append(
                    "分散投資の改善を検討してください"
                )

            return {
                "position_size": adjusted_position_size,
                "stop_loss": adjusted_stop_loss,
                "max_loss": adjusted_max_loss,
                "diversification": diversification_recommendations,
            }
        except Exception as e:
            logger.error(f"ポジション推奨事項生成エラー: {e}")
            return {
                "position_size": 0.0,
                "stop_loss": 0.0,
                "max_loss": 0.0,
                "diversification": ["分析エラー"],
            }

    async def analyze_portfolio_risk(self, symbols: List[str]) -> PortfolioRiskSummary:
        """ポートフォリオリスク分析"""
        try:
            logger.info(f"ポートフォリオリスク分析開始: {len(symbols)}銘柄")

            # 各銘柄の統合リスク分析
            individual_profiles = {}
            risk_scores = []

            for symbol in symbols:
                try:
                    # 現在価格取得
                    current_price = self._get_current_price(symbol)
                    if current_price is None:
                        current_price = 1000.0  # デフォルト価格

                    # 統合リスク分析
                    profile = await self.analyze_integrated_risk(symbol, current_price)
                    individual_profiles[symbol] = profile
                    risk_scores.append(profile.integrated_risk_score)

                except Exception as e:
                    logger.error(f"銘柄分析エラー: {symbol} - {e}")
                    continue

            # ポートフォリオ統計計算
            average_risk_score = np.mean(risk_scores) if risk_scores else 0.0
            high_risk_stocks = [
                symbol
                for symbol, profile in individual_profiles.items()
                if profile.risk_level
                in [IntegratedRiskLevel.HIGH, IntegratedRiskLevel.VERY_HIGH]
            ]
            critical_risk_stocks = [
                symbol
                for symbol, profile in individual_profiles.items()
                if profile.risk_level == IntegratedRiskLevel.CRITICAL
            ]

            # 分散投資レベル評価
            diversification_level = await self._evaluate_portfolio_diversification(
                symbols
            )

            # 統合リスクレベル判定
            overall_risk_level = self._determine_integrated_risk_level(
                average_risk_score
            )

            # リスク集中度分析
            risk_concentration = self._analyze_risk_concentration(individual_profiles)

            # ポートフォリオ推奨アクション
            portfolio_actions = self._generate_portfolio_actions(
                overall_risk_level,
                high_risk_stocks,
                critical_risk_stocks,
                diversification_level,
            )

            # ポートフォリオリスクサマリー作成
            summary = PortfolioRiskSummary(
                timestamp=datetime.now(),
                total_stocks=len(symbols),
                average_risk_score=average_risk_score,
                high_risk_stocks=high_risk_stocks,
                critical_risk_stocks=critical_risk_stocks,
                portfolio_diversification_level=diversification_level,
                overall_risk_level=overall_risk_level,
                risk_concentration=risk_concentration,
                recommended_portfolio_actions=portfolio_actions,
                individual_risk_profiles=individual_profiles,
            )

            # 履歴に保存
            self.portfolio_risk_history.append(summary)

            logger.info(
                f"ポートフォリオリスク分析完了: 平均リスクスコア {average_risk_score:.3f}"
            )
            return summary

        except Exception as e:
            logger.error(f"ポートフォリオリスク分析エラー: {e}")
            return self._create_default_portfolio_risk_summary()

    def _get_current_price(self, symbol: str) -> Optional[float]:
        """現在価格取得"""
        try:
            import yfinance as yf

            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            if not hist.empty:
                return hist["Close"].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"価格取得エラー: {symbol} - {e}")
            return None

    async def _evaluate_portfolio_diversification(
        self, symbols: List[str]
    ) -> DiversificationLevel:
        """ポートフォリオ分散投資レベル評価"""
        try:
            # 相関分析による分散投資評価
            correlation_metrics = (
                await self.correlation_analyzer.analyze_correlation_risk(symbols)
            )

            # 分散投資スコアに基づくレベル判定
            diversification_score = correlation_metrics.diversification_score

            if diversification_score >= 0.9:
                return DiversificationLevel.EXCELLENT
            elif diversification_score >= 0.7:
                return DiversificationLevel.GOOD
            elif diversification_score >= 0.5:
                return DiversificationLevel.FAIR
            elif diversification_score >= 0.3:
                return DiversificationLevel.POOR
            else:
                return DiversificationLevel.CRITICAL
        except Exception as e:
            logger.error(f"分散投資レベル評価エラー: {e}")
            return DiversificationLevel.POOR

    def _analyze_risk_concentration(
        self, individual_profiles: Dict[str, IntegratedRiskProfile]
    ) -> Dict[str, float]:
        """リスク集中度分析"""
        try:
            concentration = {
                "high_risk_concentration": 0.0,
                "critical_risk_concentration": 0.0,
                "volatility_concentration": 0.0,
                "correlation_concentration": 0.0,
            }

            if not individual_profiles:
                return concentration

            total_stocks = len(individual_profiles)

            # 高リスク集中度
            high_risk_count = sum(
                1
                for profile in individual_profiles.values()
                if profile.risk_level
                in [IntegratedRiskLevel.HIGH, IntegratedRiskLevel.VERY_HIGH]
            )
            concentration["high_risk_concentration"] = high_risk_count / total_stocks

            # 致命的リスク集中度
            critical_risk_count = sum(
                1
                for profile in individual_profiles.values()
                if profile.risk_level == IntegratedRiskLevel.CRITICAL
            )
            concentration["critical_risk_concentration"] = (
                critical_risk_count / total_stocks
            )

            # ボラティリティ集中度
            volatility_scores = [
                profile.volatility_risk_score
                for profile in individual_profiles.values()
            ]
            concentration["volatility_concentration"] = (
                np.std(volatility_scores) if volatility_scores else 0.0
            )

            # 相関集中度
            correlation_scores = [
                profile.correlation_risk_score
                for profile in individual_profiles.values()
            ]
            concentration["correlation_concentration"] = (
                np.std(correlation_scores) if correlation_scores else 0.0
            )

            return concentration
        except Exception as e:
            logger.error(f"リスク集中度分析エラー: {e}")
            return {"error": str(e)}

    def _generate_portfolio_actions(
        self,
        overall_risk_level: IntegratedRiskLevel,
        high_risk_stocks: List[str],
        critical_risk_stocks: List[str],
        diversification_level: DiversificationLevel,
    ) -> List[str]:
        """ポートフォリオ推奨アクション生成"""
        actions = []

        try:
            # 統合リスクレベルに応じた推奨事項
            if overall_risk_level == IntegratedRiskLevel.CRITICAL:
                actions.append("ポートフォリオ全体の緊急リスク削減が必要です")
                actions.append("高リスク銘柄の即座な損切りを推奨します")
            elif overall_risk_level == IntegratedRiskLevel.VERY_HIGH:
                actions.append("ポートフォリオ全体のリスク削減を強く推奨します")
                actions.append("高リスク銘柄の見直しを検討してください")
            elif overall_risk_level == IntegratedRiskLevel.HIGH:
                actions.append("ポートフォリオリスクの監視を強化してください")
                actions.append("リスク分散の改善を検討してください")

            # 高リスク銘柄への対応
            if critical_risk_stocks:
                actions.append(
                    f"致命的リスク銘柄: {', '.join(critical_risk_stocks)} の緊急対応が必要です"
                )

            if high_risk_stocks:
                actions.append(
                    f"高リスク銘柄: {', '.join(high_risk_stocks)} の見直しを推奨します"
                )

            # 分散投資レベルに応じた推奨事項
            if diversification_level == DiversificationLevel.CRITICAL:
                actions.append(
                    "分散投資が極めて不十分です。銘柄数を大幅に増やしてください"
                )
            elif diversification_level == DiversificationLevel.POOR:
                actions.append(
                    "分散投資が不十分です。異なるセクターへの投資を検討してください"
                )
            elif diversification_level == DiversificationLevel.FAIR:
                actions.append("分散投資の改善を検討してください")
            else:
                actions.append("現在の分散投資レベルは適切です")

            return actions
        except Exception as e:
            logger.error(f"ポートフォリオ推奨アクション生成エラー: {e}")
            return ["分析エラーにより推奨事項を生成できませんでした"]

    def _create_default_integrated_risk_profile(
        self, symbol: str
    ) -> IntegratedRiskProfile:
        """デフォルト統合リスクプロファイル作成"""
        return IntegratedRiskProfile(
            symbol=symbol,
            timestamp=datetime.now(),
            individual_risk_score=0.5,
            volatility_risk_score=0.5,
            correlation_risk_score=0.5,
            loss_risk_score=0.0,
            integrated_risk_score=0.5,
            risk_level=IntegratedRiskLevel.MEDIUM,
            risk_factors=["分析エラー"],
            recommended_actions=["分析エラーのため推奨事項を生成できませんでした"],
            position_size_recommendation=0.0,
            stop_loss_recommendation=0.0,
            max_loss_recommendation=0.0,
            diversification_recommendation=["分析エラー"],
        )

    def _create_default_portfolio_risk_summary(self) -> PortfolioRiskSummary:
        """デフォルトポートフォリオリスクサマリー作成"""
        return PortfolioRiskSummary(
            timestamp=datetime.now(),
            total_stocks=0,
            average_risk_score=0.5,
            high_risk_stocks=[],
            critical_risk_stocks=[],
            portfolio_diversification_level=DiversificationLevel.POOR,
            overall_risk_level=IntegratedRiskLevel.MEDIUM,
            risk_concentration={},
            recommended_portfolio_actions=["分析エラー"],
            individual_risk_profiles={},
        )

    def get_integrated_risk_summary(self) -> Dict[str, Any]:
        """統合リスクサマリー取得"""
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "analyzed_symbols": list(self.integrated_risk_history.keys()),
                "individual_risk_profiles": {},
                "portfolio_risk_history": [],
            }

            # 個別リスクプロファイル
            for symbol, profile in self.integrated_risk_history.items():
                summary["individual_risk_profiles"][symbol] = asdict(profile)

            # ポートフォリオリスク履歴
            for portfolio_summary in self.portfolio_risk_history:
                summary["portfolio_risk_history"].append(asdict(portfolio_summary))

            return summary
        except Exception as e:
            logger.error(f"統合リスクサマリー取得エラー: {e}")
            return {"error": str(e)}

    def save_integrated_risk_report(
        self, filename: str = "integrated_individual_risk_report.json"
    ):
        """統合リスクレポート保存"""
        try:
            report = self.get_integrated_risk_summary()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"統合リスクレポートを保存しました: {filename}")
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 統合個別銘柄リスク管理システム初期化
    integrated_risk_system = IntegratedIndividualRiskManagement(account_value=1000000)

    # テスト銘柄
    test_symbols = ["7203.T", "6758.T", "9984.T", "7974.T", "4063.T"]

    logger.info("統合個別銘柄リスク管理システム テスト開始")

    # 個別銘柄の統合リスク分析
    for symbol in test_symbols:
        try:
            logger.info(f"統合リスク分析開始: {symbol}")

            # 現在価格取得
            current_price = integrated_risk_system._get_current_price(symbol)
            if current_price is None:
                current_price = 1000.0  # デフォルト価格

            # 統合リスク分析
            integrated_profile = await integrated_risk_system.analyze_integrated_risk(
                symbol, current_price
            )

            logger.info(f"統合リスク分析完了: {symbol}")
            logger.info(
                f"  統合リスクスコア: {integrated_profile.integrated_risk_score:.3f}"
            )
            logger.info(f"  リスクレベル: {integrated_profile.risk_level.value}")
            logger.info(f"  リスク要因: {', '.join(integrated_profile.risk_factors)}")
            logger.info(
                f"  推奨ポジションサイズ: ¥{integrated_profile.position_size_recommendation:,.0f}"
            )
            logger.info(
                f"  推奨ストップロス: ¥{integrated_profile.stop_loss_recommendation:,.0f}"
            )
            logger.info(
                f"  推奨最大損失: ¥{integrated_profile.max_loss_recommendation:,.0f}"
            )

        except Exception as e:
            logger.error(f"統合リスク分析エラー: {symbol} - {e}")

    # ポートフォリオリスク分析
    try:
        logger.info("ポートフォリオリスク分析開始")

        portfolio_summary = await integrated_risk_system.analyze_portfolio_risk(
            test_symbols
        )

        logger.info(f"ポートフォリオリスク分析完了")
        logger.info(f"  平均リスクスコア: {portfolio_summary.average_risk_score:.3f}")
        logger.info(f"  統合リスクレベル: {portfolio_summary.overall_risk_level.value}")
        logger.info(f"  高リスク銘柄: {', '.join(portfolio_summary.high_risk_stocks)}")
        logger.info(
            f"  致命的リスク銘柄: {', '.join(portfolio_summary.critical_risk_stocks)}"
        )
        logger.info(
            f"  分散投資レベル: {portfolio_summary.portfolio_diversification_level.value}"
        )

    except Exception as e:
        logger.error(f"ポートフォリオリスク分析エラー: {e}")

    # レポート保存
    integrated_risk_system.save_integrated_risk_report()

    # 結果表示
    print("\n" + "=" * 80)
    print("🛡️ 統合個別銘柄リスク管理システム レポート")
    print("=" * 80)

    # 個別銘柄リスクプロファイル表示
    print("\n📊 個別銘柄リスクプロファイル:")
    for symbol, profile in integrated_risk_system.integrated_risk_history.items():
        risk_emoji = {
            "VERY_LOW": "🟢",
            "LOW": "🟡",
            "MEDIUM": "🟠",
            "HIGH": "🔴",
            "VERY_HIGH": "🔴",
            "CRITICAL": "⚫",
        }.get(profile.risk_level.value, "⚪")

        print(
            f"  {risk_emoji} {symbol}: {profile.risk_level.value} "
            f"(統合スコア: {profile.integrated_risk_score:.3f})"
        )
        print(f"    リスク要因: {', '.join(profile.risk_factors)}")
        print(f"    推奨アクション: {', '.join(profile.recommended_actions[:2])}")

    # ポートフォリオサマリー表示
    if integrated_risk_system.portfolio_risk_history:
        latest_portfolio = integrated_risk_system.portfolio_risk_history[-1]
        print(f"\n📈 ポートフォリオサマリー:")
        print(f"  総銘柄数: {latest_portfolio.total_stocks}")
        print(f"  平均リスクスコア: {latest_portfolio.average_risk_score:.3f}")
        print(f"  統合リスクレベル: {latest_portfolio.overall_risk_level.value}")
        print(
            f"  分散投資レベル: {latest_portfolio.portfolio_diversification_level.value}"
        )

        if latest_portfolio.high_risk_stocks:
            print(f"  高リスク銘柄: {', '.join(latest_portfolio.high_risk_stocks)}")

        if latest_portfolio.critical_risk_stocks:
            print(
                f"  致命的リスク銘柄: {', '.join(latest_portfolio.critical_risk_stocks)}"
            )

        print(f"\n💡 ポートフォリオ推奨事項:")
        for action in latest_portfolio.recommended_portfolio_actions:
            print(f"  • {action}")


if __name__ == "__main__":
    asyncio.run(main())
