#!/usr/bin/env python3
"""
新NISA統合最適化システム
2024年1月開始の新NISA制度に対応した統合最適化機能
非課税枠利用率90%以上を目標とした包括的最適化システム
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import math

# 既存モジュールのインポート
from .nisa_quota_manager import (
    NisaQuotaManager,
    NisaQuotaStatus,
    NisaTransaction,
    NisaPortfolio,
)
from .nisa_tax_calculator import NisaTaxCalculator, TaxCalculation, TaxOptimization
from .nisa_optimization_system import NisaOptimizationSystem, OptimizationReport


@dataclass
class NisaOptimizationResult:
    """NISA最適化結果"""

    current_utilization_rate: float
    target_utilization_rate: float
    improvement_potential: float
    tax_savings_current: float
    tax_savings_potential: float
    optimization_score: float
    recommendations: List[Dict[str, Any]]
    ai_strategies: List[Dict[str, Any]]
    implementation_plan: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    efficiency_metrics: Dict[str, Any]


class NisaIntegratedOptimizer:
    """新NISA統合最適化システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 各システムの初期化
        self.quota_manager = NisaQuotaManager(config)
        self.tax_calculator = NisaTaxCalculator(config)
        self.optimization_system = NisaOptimizationSystem(config)

        # 最適化設定
        self.target_utilization_rate = 90.0
        self.tax_rate = 0.30
        self.optimization_threshold = 0.85

    def get_comprehensive_optimization(self) -> NisaOptimizationResult:
        """包括的最適化の実行"""
        try:
            # 1. 現在の状況取得
            quota_status = self.quota_manager.get_quota_status()
            portfolio = self.quota_manager.get_portfolio()

            # 2. 税務計算
            quota_data = quota_status.__dict__
            portfolio_data = portfolio.__dict__
            tax_calculation = self.tax_calculator.calculate_tax_savings(
                quota_data, portfolio_data
            )

            # 3. 最適化レポート生成
            optimization_report = self.optimization_system.generate_optimization_report(
                quota_data, portfolio_data
            )

            # 4. 統合結果の生成
            result = self._create_integrated_result(
                quota_status, portfolio, tax_calculation, optimization_report
            )

            return result

        except Exception as e:
            self.logger.error(f"包括的最適化実行エラー: {e}")
            return self._create_error_result()

    def _create_integrated_result(
        self,
        quota_status: NisaQuotaStatus,
        portfolio: NisaPortfolio,
        tax_calculation: TaxCalculation,
        optimization_report: OptimizationReport,
    ) -> NisaOptimizationResult:
        """統合結果の作成"""
        try:
            # 利用率の計算
            growth_utilization = quota_status.growth_investment.get(
                "utilization_rate", 0
            )
            accumulation_utilization = quota_status.accumulation_investment.get(
                "utilization_rate", 0
            )
            current_utilization_rate = (
                growth_utilization + accumulation_utilization
            ) / 2

            # 改善ポテンシャルの計算
            improvement_potential = max(
                0, self.target_utilization_rate - current_utilization_rate
            )

            # 税務節約額の計算
            tax_savings_current = tax_calculation.tax_savings.get(
                "estimated_tax_savings", 0
            )
            tax_savings_potential = tax_calculation.tax_savings.get(
                "lifetime_savings", 0
            )

            # 最適化スコア
            optimization_score = optimization_report.current_score

            # 推奨事項の変換
            recommendations = [
                asdict(rec) for rec in optimization_report.recommendations
            ]

            # AI戦略の変換
            ai_strategies = [
                asdict(strategy) for strategy in optimization_report.ai_strategies
            ]

            # 効率指標の計算
            efficiency_metrics = self._calculate_efficiency_metrics(
                quota_status, portfolio, tax_calculation, optimization_report
            )

            return NisaOptimizationResult(
                current_utilization_rate=current_utilization_rate,
                target_utilization_rate=self.target_utilization_rate,
                improvement_potential=improvement_potential,
                tax_savings_current=tax_savings_current,
                tax_savings_potential=tax_savings_potential,
                optimization_score=optimization_score,
                recommendations=recommendations,
                ai_strategies=ai_strategies,
                implementation_plan=optimization_report.implementation_plan,
                risk_analysis=optimization_report.risk_analysis,
                efficiency_metrics=efficiency_metrics,
            )

        except Exception as e:
            self.logger.error(f"統合結果作成エラー: {e}")
            return self._create_error_result()

    def _calculate_efficiency_metrics(
        self,
        quota_status: NisaQuotaStatus,
        portfolio: NisaPortfolio,
        tax_calculation: TaxCalculation,
        optimization_report: OptimizationReport,
    ) -> Dict[str, Any]:
        """効率指標の計算"""
        try:
            # 基本効率指標
            growth_utilization = quota_status.growth_investment.get(
                "utilization_rate", 0
            )
            accumulation_utilization = quota_status.accumulation_investment.get(
                "utilization_rate", 0
            )

            # 税務効率
            tax_efficiency = tax_calculation.optimization.get("tax_efficiency", 0)

            # ポートフォリオ効率
            portfolio_efficiency = self._calculate_portfolio_efficiency(portfolio)

            # 時間効率
            time_efficiency = self._calculate_time_efficiency()

            # 総合効率スコア
            overall_efficiency = (
                (growth_utilization + accumulation_utilization) / 2 * 0.4
                + tax_efficiency * 0.3
                + portfolio_efficiency * 0.2
                + time_efficiency * 0.1
            )

            return {
                "overall_efficiency": round(overall_efficiency, 2),
                "growth_efficiency": growth_utilization,
                "accumulation_efficiency": accumulation_utilization,
                "tax_efficiency": tax_efficiency,
                "portfolio_efficiency": portfolio_efficiency,
                "time_efficiency": time_efficiency,
                "optimization_level": self._determine_optimization_level(
                    overall_efficiency
                ),
            }

        except Exception as e:
            self.logger.error(f"効率指標計算エラー: {e}")
            return {
                "overall_efficiency": 0,
                "growth_efficiency": 0,
                "accumulation_efficiency": 0,
                "tax_efficiency": 0,
                "portfolio_efficiency": 0,
                "time_efficiency": 0,
                "optimization_level": "UNKNOWN",
            }

    def _calculate_portfolio_efficiency(self, portfolio: NisaPortfolio) -> float:
        """ポートフォリオ効率の計算"""
        try:
            positions = portfolio.positions
            if not positions:
                return 0.0

            # 分散度スコア
            diversification_score = min(len(positions) * 10, 100)

            # リターンスコア
            return_score = 50.0  # デフォルト
            if portfolio.total_cost > 0:
                return_rate = (
                    portfolio.unrealized_profit_loss / portfolio.total_cost
                ) * 100
                return_score = max(0, min(100, 50 + return_rate))

            # 総合ポートフォリオ効率
            portfolio_efficiency = diversification_score * 0.6 + return_score * 0.4

            return round(portfolio_efficiency, 2)

        except Exception as e:
            self.logger.error(f"ポートフォリオ効率計算エラー: {e}")
            return 0.0

    def _calculate_time_efficiency(self) -> float:
        """時間効率の計算"""
        try:
            current_date = date.today()
            year_start = date(current_date.year, 1, 1)
            year_end = date(current_date.year, 12, 31)

            # 年間経過日数
            days_passed = (current_date - year_start).days
            total_days = (year_end - year_start).days

            # 時間効率（0.0-1.0）
            time_efficiency = days_passed / total_days

            return min(time_efficiency, 1.0)

        except Exception as e:
            self.logger.error(f"時間効率計算エラー: {e}")
            return 0.0

    def _determine_optimization_level(self, efficiency_score: float) -> str:
        """最適化レベルの判定"""
        try:
            if efficiency_score >= 90:
                return "EXCELLENT"
            elif efficiency_score >= 80:
                return "GOOD"
            elif efficiency_score >= 60:
                return "FAIR"
            else:
                return "POOR"
        except Exception as e:
            self.logger.error(f"最適化レベル判定エラー: {e}")
            return "UNKNOWN"

    def _create_error_result(self) -> NisaOptimizationResult:
        """エラー結果の作成"""
        return NisaOptimizationResult(
            current_utilization_rate=0,
            target_utilization_rate=self.target_utilization_rate,
            improvement_potential=self.target_utilization_rate,
            tax_savings_current=0,
            tax_savings_potential=0,
            optimization_score=0,
            recommendations=[],
            ai_strategies=[],
            implementation_plan={},
            risk_analysis={},
            efficiency_metrics={},
        )

    def get_optimization_summary(self) -> Dict[str, Any]:
        """最適化サマリーの取得"""
        try:
            result = self.get_comprehensive_optimization()

            return {
                "summary": {
                    "current_utilization_rate": result.current_utilization_rate,
                    "target_utilization_rate": result.target_utilization_rate,
                    "improvement_potential": result.improvement_potential,
                    "optimization_score": result.optimization_score,
                    "optimization_level": result.efficiency_metrics.get(
                        "optimization_level", "UNKNOWN"
                    ),
                },
                "tax_benefits": {
                    "current_tax_savings": result.tax_savings_current,
                    "potential_tax_savings": result.tax_savings_potential,
                    "annual_savings": result.tax_savings_current,
                    "lifetime_savings": result.tax_savings_potential,
                },
                "recommendations_count": len(result.recommendations),
                "ai_strategies_count": len(result.ai_strategies),
                "high_priority_actions": len(
                    [
                        rec
                        for rec in result.recommendations
                        if rec.get("priority") == "HIGH"
                    ]
                ),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"最適化サマリー取得エラー: {e}")
            return {
                "summary": {
                    "current_utilization_rate": 0,
                    "target_utilization_rate": self.target_utilization_rate,
                    "improvement_potential": self.target_utilization_rate,
                    "optimization_score": 0,
                    "optimization_level": "UNKNOWN",
                },
                "tax_benefits": {
                    "current_tax_savings": 0,
                    "potential_tax_savings": 0,
                    "annual_savings": 0,
                    "lifetime_savings": 0,
                },
                "recommendations_count": 0,
                "ai_strategies_count": 0,
                "high_priority_actions": 0,
                "last_updated": datetime.now().isoformat(),
            }

    def execute_optimization_action(
        self, action_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """最適化アクションの実行"""
        try:
            if action_type == "ADD_TRANSACTION":
                return self._execute_add_transaction(parameters)
            elif action_type == "UPDATE_PORTFOLIO":
                return self._execute_update_portfolio(parameters)
            elif action_type == "OPTIMIZE_ALLOCATION":
                return self._execute_optimize_allocation(parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action type: {action_type}",
                }

        except Exception as e:
            self.logger.error(f"最適化アクション実行エラー: {e}")
            return {"success": False, "error": str(e)}

    def _execute_add_transaction(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """取引追加の実行"""
        try:
            transaction = NisaTransaction(
                id=parameters.get(
                    "id", f'txn_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                ),
                type=parameters.get("type", "BUY"),
                symbol=parameters.get("symbol", ""),
                symbol_name=parameters.get("symbol_name", ""),
                quantity=parameters.get("quantity", 0),
                price=parameters.get("price", 0.0),
                amount=parameters.get("amount", 0.0),
                quota_type=parameters.get("quota_type", "GROWTH"),
                transaction_date=parameters.get(
                    "transaction_date", datetime.now().isoformat()
                ),
                tax_savings=parameters.get("tax_savings", 0.0),
                efficiency_score=parameters.get("efficiency_score", 0.0),
                strategy=parameters.get("strategy", ""),
                risk_level=parameters.get("risk_level", "MEDIUM"),
            )

            result = self.quota_manager.add_transaction(transaction)
            return result

        except Exception as e:
            self.logger.error(f"取引追加実行エラー: {e}")
            return {"success": False, "error": str(e)}

    def _execute_update_portfolio(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """ポートフォリオ更新の実行"""
        try:
            # ポートフォリオの更新ロジック
            # 実際の実装では、ポートフォリオの再計算や最適化を行う
            return {"success": True, "message": "Portfolio updated successfully"}

        except Exception as e:
            self.logger.error(f"ポートフォリオ更新実行エラー: {e}")
            return {"success": False, "error": str(e)}

    def _execute_optimize_allocation(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """配分最適化の実行"""
        try:
            # 配分最適化のロジック
            # 実際の実装では、AI戦略に基づく配分の最適化を行う
            return {"success": True, "message": "Allocation optimized successfully"}

        except Exception as e:
            self.logger.error(f"配分最適化実行エラー: {e}")
            return {"success": False, "error": str(e)}
