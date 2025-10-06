"""
ポートフォリオ最適化統合システム
全機能を統合した包括的なポートフォリオ最適化システム
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import warnings

warnings.filterwarnings("ignore")

# 統合システムのインポート
from .advanced_portfolio_optimizer import (
    AdvancedPortfolioOptimizer,
    OptimizationResult,
    RiskMetrics,
)
from .diversification_scoring_system import (
    DiversificationScoringSystem,
    DiversificationMetrics,
)
from .optimal_position_sizing_system import (
    OptimalPositionSizingSystem,
    PositionSizingResult,
    MarketConditions,
)
from .enhanced_recommendation_system import (
    EnhancedRecommendationSystem,
    PortfolioRecommendation,
)
from .sharpe_ratio_optimizer import SharpeRatioOptimizer, SharpeOptimizationResult


@dataclass
class IntegratedPortfolioOptimizationResult:
    """統合ポートフォリオ最適化結果"""

    optimization_result: OptimizationResult
    diversification_metrics: DiversificationMetrics
    position_sizing_results: Dict[str, PositionSizingResult]
    sharpe_optimization_result: SharpeOptimizationResult
    portfolio_recommendations: PortfolioRecommendation
    overall_score: float
    improvement_achieved: bool
    optimization_timestamp: str
    system_performance: Dict[str, Any]


class IntegratedPortfolioOptimizationSystem:
    """統合ポートフォリオ最適化システム"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)

        # 各システムの初期化
        self.portfolio_optimizer = AdvancedPortfolioOptimizer(
            self.config.get("portfolio_optimizer", {})
        )
        self.diversification_system = DiversificationScoringSystem(
            self.config.get("diversification", {})
        )
        self.position_sizing_system = OptimalPositionSizingSystem(
            self.config.get("position_sizing", {})
        )
        self.recommendation_system = EnhancedRecommendationSystem(
            self.config.get("recommendation", {})
        )
        self.sharpe_optimizer = SharpeRatioOptimizer(
            self.config.get("sharpe_optimizer", {})
        )

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定取得"""
        return {
            "portfolio_optimizer": {
                "max_iterations": 1000,
                "tolerance": 1e-6,
                "risk_free_rate": 0.02,
                "max_position_weight": 0.2,
                "min_position_weight": 0.01,
            },
            "diversification": {
                "max_sector_weight": 0.3,
                "max_correlation": 0.7,
                "min_effective_stocks": 5,
                "target_entropy": 0.8,
            },
            "position_sizing": {
                "risk_free_rate": 0.02,
                "transaction_cost": 0.001,
                "min_trade_amount": 10000,
                "max_trade_amount": 1000000,
                "max_position_weight": 0.2,
                "max_risk_per_trade": 0.02,
            },
            "recommendation": {
                "min_confidence": 0.7,
                "max_risk_per_trade": 0.02,
                "target_sharpe_ratio": 1.5,
                "rebalancing_threshold": 0.05,
            },
            "sharpe_optimizer": {
                "risk_free_rate": 0.02,
                "max_iterations": 1000,
                "tolerance": 1e-6,
                "max_position_weight": 0.2,
                "min_position_weight": 0.01,
            },
        }

    def optimize_portfolio_comprehensive(
        self,
        portfolio_data: Dict[str, Any],
        market_conditions: MarketConditions,
        user_preferences: Optional[Dict[str, Any]] = None,
        optimization_method: str = "max_sharpe",
    ) -> IntegratedPortfolioOptimizationResult:
        """
        包括的ポートフォリオ最適化実行

        Args:
            portfolio_data: ポートフォリオデータ
            market_conditions: 市場条件
            user_preferences: ユーザー設定
            optimization_method: 最適化手法

        Returns:
            IntegratedPortfolioOptimizationResult: 統合最適化結果
        """
        try:
            start_time = datetime.now()

            # 1. ポートフォリオ最適化
            self.logger.info("ポートフォリオ最適化を開始...")
            optimization_result = self.portfolio_optimizer.optimize_portfolio(
                portfolio_data.get("stock_data", []),
                portfolio_data.get("market_data"),
                portfolio_data.get("benchmark_data"),
                portfolio_data.get("target_return"),
                portfolio_data.get("max_risk"),
                optimization_method,
            )

            # 2. 分散投資スコア計算
            self.logger.info("分散投資スコア計算を開始...")
            diversification_metrics = (
                self.diversification_system.calculate_diversification_score(
                    optimization_result.weights,
                    portfolio_data.get("stock_data", []),
                    portfolio_data.get("market_data"),
                )
            )

            # 3. ポジションサイジング最適化
            self.logger.info("ポジションサイジング最適化を開始...")
            position_sizing_results = {}
            for symbol, weight in optimization_result.weights.items():
                if weight > 0:
                    stock_data = self._get_stock_data(
                        symbol, portfolio_data.get("stock_data", [])
                    )
                    if stock_data:
                        position_result = (
                            self.position_sizing_system.calculate_optimal_position_size(
                                symbol,
                                stock_data.get("current_price", 100.0),
                                portfolio_data.get("total_value", 1000000),
                                stock_data,
                                market_conditions,
                                portfolio_data.get("existing_portfolio"),
                                portfolio_data.get("target_return"),
                                user_preferences.get("risk_tolerance", "MEDIUM")
                                if user_preferences
                                else "MEDIUM",
                            )
                        )
                        position_sizing_results[symbol] = position_result

            # 4. シャープレシオ最適化
            self.logger.info("シャープレシオ最適化を開始...")
            sharpe_optimization_result = self.sharpe_optimizer.optimize_sharpe_ratio(
                portfolio_data,
                portfolio_data.get("market_data"),
                portfolio_data.get("benchmark_data"),
                optimization_method,
            )

            # 5. 推奨事項生成
            self.logger.info("推奨事項生成を開始...")
            risk_metrics = self._calculate_integrated_risk_metrics(
                optimization_result, portfolio_data
            )
            portfolio_recommendations = (
                self.recommendation_system.generate_portfolio_recommendations(
                    portfolio_data,
                    self._convert_market_conditions(market_conditions),
                    optimization_result.__dict__,
                    risk_metrics,
                    diversification_metrics.__dict__,
                    user_preferences,
                )
            )

            # 6. 統合結果の生成
            overall_score = self._calculate_overall_score(
                optimization_result, diversification_metrics, sharpe_optimization_result
            )

            improvement_achieved = self._evaluate_improvement_achievement(
                optimization_result, sharpe_optimization_result
            )

            system_performance = self._calculate_system_performance(
                start_time, datetime.now()
            )

            return IntegratedPortfolioOptimizationResult(
                optimization_result=optimization_result,
                diversification_metrics=diversification_metrics,
                position_sizing_results=position_sizing_results,
                sharpe_optimization_result=sharpe_optimization_result,
                portfolio_recommendations=portfolio_recommendations,
                overall_score=overall_score,
                improvement_achieved=improvement_achieved,
                optimization_timestamp=datetime.now().isoformat(),
                system_performance=system_performance,
            )

        except Exception as e:
            self.logger.error(f"包括的ポートフォリオ最適化エラー: {e}")
            raise

    def _get_stock_data(
        self, symbol: str, stock_data_list: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """銘柄データ取得"""
        for stock_data in stock_data_list:
            if stock_data.get("symbol") == symbol:
                return stock_data
        return None

    def _calculate_integrated_risk_metrics(
        self, optimization_result: OptimizationResult, portfolio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """統合リスクメトリクス計算"""
        try:
            return {
                "volatility": optimization_result.volatility,
                "max_drawdown": 0.15,  # 簡略化
                "var_95": -0.03,  # 簡略化
                "sharpe_ratio": optimization_result.sharpe_ratio,
                "sortino_ratio": optimization_result.sharpe_ratio * 1.2,  # 簡略化
                "calmar_ratio": optimization_result.expected_return / 0.15,  # 簡略化
                "portfolio_return": optimization_result.expected_return,
                "diversification_score": optimization_result.diversification_score,
            }
        except Exception as e:
            self.logger.error(f"統合リスクメトリクス計算エラー: {e}")
            return {
                "volatility": 0.2,
                "max_drawdown": 0.15,
                "var_95": -0.03,
                "sharpe_ratio": 0.5,
                "sortino_ratio": 0.6,
                "calmar_ratio": 0.5,
                "portfolio_return": 0.05,
                "diversification_score": 0.5,
            }

    def _convert_market_conditions(
        self, market_conditions: MarketConditions
    ) -> Dict[str, Any]:
        """市場条件変換"""
        return {
            "volatility_regime": market_conditions.volatility_regime,
            "trend_direction": market_conditions.trend_direction,
            "liquidity_level": market_conditions.liquidity_level,
            "market_stress": market_conditions.market_stress,
            "correlation_level": market_conditions.correlation_level,
        }

    def _calculate_overall_score(
        self,
        optimization_result: OptimizationResult,
        diversification_metrics: DiversificationMetrics,
        sharpe_optimization_result: SharpeOptimizationResult,
    ) -> float:
        """総合スコア計算"""
        try:
            # 各要素のスコア
            optimization_score = min(1.0, optimization_result.sharpe_ratio / 2.0)
            diversification_score = diversification_metrics.overall_score
            sharpe_improvement_score = min(
                1.0, sharpe_optimization_result.improvement_ratio / 0.5
            )

            # 重み付き平均
            overall_score = (
                optimization_score * 0.4
                + diversification_score * 0.3
                + sharpe_improvement_score * 0.3
            )

            return min(1.0, max(0.0, overall_score))

        except Exception as e:
            self.logger.error(f"総合スコア計算エラー: {e}")
            return 0.5

    def _evaluate_improvement_achievement(
        self,
        optimization_result: OptimizationResult,
        sharpe_optimization_result: SharpeOptimizationResult,
    ) -> bool:
        """改善達成評価"""
        try:
            # シャープレシオ改善20%以上
            sharpe_improvement = sharpe_optimization_result.improvement_ratio >= 0.20

            # 最適化収束
            optimization_convergence = optimization_result.convergence

            # 信頼度
            confidence_achieved = optimization_result.confidence >= 0.7

            return (
                sharpe_improvement and optimization_convergence and confidence_achieved
            )

        except Exception as e:
            self.logger.error(f"改善達成評価エラー: {e}")
            return False

    def _calculate_system_performance(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """システムパフォーマンス計算"""
        try:
            execution_time = (end_time - start_time).total_seconds()

            return {
                "execution_time_seconds": execution_time,
                "execution_time_minutes": execution_time / 60,
                "performance_grade": self._get_performance_grade(execution_time),
                "optimization_efficiency": self._calculate_optimization_efficiency(
                    execution_time
                ),
            }

        except Exception as e:
            self.logger.error(f"システムパフォーマンス計算エラー: {e}")
            return {
                "execution_time_seconds": 0.0,
                "execution_time_minutes": 0.0,
                "performance_grade": "UNKNOWN",
                "optimization_efficiency": 0.0,
            }

    def _get_performance_grade(self, execution_time: float) -> str:
        """パフォーマンスグレード取得"""
        if execution_time < 30:
            return "EXCELLENT"
        elif execution_time < 60:
            return "GOOD"
        elif execution_time < 120:
            return "FAIR"
        else:
            return "POOR"

    def _calculate_optimization_efficiency(self, execution_time: float) -> float:
        """最適化効率計算"""
        # 30秒を基準とした効率計算
        base_time = 30.0
        efficiency = max(0.0, min(1.0, base_time / execution_time))
        return efficiency

    def generate_comprehensive_report(
        self, result: IntegratedPortfolioOptimizationResult
    ) -> Dict[str, Any]:
        """包括的レポート生成"""
        try:
            report = {
                "executive_summary": {
                    "overall_score": result.overall_score,
                    "improvement_achieved": result.improvement_achieved,
                    "optimization_method": result.optimization_result.method,
                    "sharpe_improvement": result.sharpe_optimization_result.improvement_ratio,
                    "diversification_score": result.diversification_metrics.overall_score,
                    "execution_time": result.system_performance[
                        "execution_time_seconds"
                    ],
                },
                "optimization_results": {
                    "portfolio_weights": result.optimization_result.weights,
                    "expected_return": result.optimization_result.expected_return,
                    "volatility": result.optimization_result.volatility,
                    "sharpe_ratio": result.optimization_result.sharpe_ratio,
                    "diversification_score": result.optimization_result.diversification_score,
                    "confidence": result.optimization_result.confidence,
                },
                "diversification_analysis": {
                    "overall_score": result.diversification_metrics.overall_score,
                    "sector_diversification": result.diversification_metrics.sector_diversification,
                    "correlation_diversification": result.diversification_metrics.correlation_diversification,
                    "concentration_risk": result.diversification_metrics.concentration_risk,
                    "effective_stocks": result.diversification_metrics.effective_number_of_stocks,
                },
                "position_sizing_analysis": {
                    "total_positions": len(result.position_sizing_results),
                    "position_details": {
                        symbol: {
                            "recommended_quantity": pos.recommended_quantity,
                            "recommended_value": pos.recommended_value,
                            "position_weight": pos.position_weight,
                            "risk_amount": pos.risk_amount,
                            "confidence_score": pos.confidence_score,
                            "risk_level": pos.risk_level,
                        }
                        for symbol, pos in result.position_sizing_results.items()
                    },
                },
                "sharpe_optimization": {
                    "original_sharpe": result.sharpe_optimization_result.original_sharpe,
                    "optimized_sharpe": result.sharpe_optimization_result.optimized_sharpe,
                    "improvement_ratio": result.sharpe_optimization_result.improvement_ratio,
                    "target_achieved": result.sharpe_optimization_result.target_achieved,
                    "convergence_success": result.sharpe_optimization_result.convergence_success,
                },
                "recommendations": {
                    "overall_assessment": result.portfolio_recommendations.overall_assessment,
                    "individual_recommendations_count": len(
                        result.portfolio_recommendations.individual_recommendations
                    ),
                    "portfolio_actions_count": len(
                        result.portfolio_recommendations.portfolio_actions
                    ),
                    "risk_warnings_count": len(
                        result.portfolio_recommendations.risk_warnings
                    ),
                    "optimization_suggestions_count": len(
                        result.portfolio_recommendations.optimization_suggestions
                    ),
                },
                "system_performance": result.system_performance,
                "timestamp": result.optimization_timestamp,
            }

            return report

        except Exception as e:
            self.logger.error(f"包括的レポート生成エラー: {e}")
            return {"error": str(e)}

    def validate_optimization_results(
        self, result: IntegratedPortfolioOptimizationResult
    ) -> Dict[str, Any]:
        """最適化結果検証"""
        try:
            validation_results = {
                "validation_passed": True,
                "validation_errors": [],
                "validation_warnings": [],
                "quality_metrics": {},
            }

            # ウェイト検証
            weights = result.optimization_result.weights
            total_weight = sum(weights.values())

            if abs(total_weight - 1.0) > 0.01:
                validation_results["validation_errors"].append(
                    f"ウェイト合計が1.0ではありません: {total_weight}"
                )
                validation_results["validation_passed"] = False

            # 個別ウェイト検証
            for symbol, weight in weights.items():
                if weight < 0:
                    validation_results["validation_errors"].append(
                        f"負のウェイト: {symbol} = {weight}"
                    )
                    validation_results["validation_passed"] = False
                elif weight > 0.5:
                    validation_results["validation_warnings"].append(
                        f"高いウェイト: {symbol} = {weight}"
                    )

            # シャープレシオ検証
            if result.optimization_result.sharpe_ratio < 0:
                validation_results["validation_warnings"].append(
                    f"負のシャープレシオ: {result.optimization_result.sharpe_ratio}"
                )

            # 分散投資スコア検証
            if result.diversification_metrics.overall_score < 0.3:
                validation_results["validation_warnings"].append(
                    f"低い分散投資スコア: {result.diversification_metrics.overall_score}"
                )

            # 品質メトリクス
            validation_results["quality_metrics"] = {
                "weight_sum": total_weight,
                "max_weight": max(weights.values()) if weights else 0,
                "min_weight": min(weights.values()) if weights else 0,
                "sharpe_ratio": result.optimization_result.sharpe_ratio,
                "diversification_score": result.diversification_metrics.overall_score,
                "confidence": result.optimization_result.confidence,
                "convergence": result.optimization_result.convergence,
            }

            return validation_results

        except Exception as e:
            self.logger.error(f"最適化結果検証エラー: {e}")
            return {
                "validation_passed": False,
                "validation_errors": [f"検証エラー: {str(e)}"],
                "validation_warnings": [],
                "quality_metrics": {},
            }
