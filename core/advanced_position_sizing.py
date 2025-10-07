#!/usr/bin/env python3
"""
高度なポジションサイジングシステム
記事の固定1株を超える高度なポジションサイジング機能を実装
"""

import numpy as np
from typing import Dict, Any, List
from datetime import datetime
import logging


class AdvancedPositionSizing:
    """高度なポジションサイジングシステム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # ポジションサイジング設定
        self.max_position_percent = self.config.get(
            "max_position_percent", 0.2
        )  # 最大20%
        self.base_position_size = self.config.get(
            "base_position_size", 100
        )  # 基本100株
        self.risk_per_trade = self.config.get(
            "risk_per_trade", 0.02
        )  # 取引あたり2%リスク

        # 信頼度ベースの設定
        self.confidence_multiplier = self.config.get("confidence_multiplier", 2.0)
        self.min_confidence = self.config.get("min_confidence", 0.6)

        # ボラティリティベースの設定
        self.volatility_adjustment = self.config.get("volatility_adjustment", True)
        self.max_volatility = self.config.get(
            "max_volatility", 0.05
        )  # 最大5%ボラティリティ

        # 相関ベースの設定
        self.correlation_adjustment = self.config.get("correlation_adjustment", True)
        self.max_correlation = self.config.get("max_correlation", 0.7)  # 最大70%相関

    def calculate_position_size(
        self,
        account_balance: float,
        stock_price: float,
        confidence: float,
        volatility: float = 0.02,
        correlation: float = 0.0,
        risk_level: str = "MEDIUM",
        max_loss_amount: float = None,
        portfolio_correlation: float = 0.0,
    ) -> Dict[str, Any]:
        """
        高度なポジションサイズの計算
        記事の固定1株を超える高度な計算
        リスク・ボラティリティ・相関に基づく動的調整
        """
        try:
            # 基本ポジションサイズの計算
            base_size = self._calculate_base_position_size(
                account_balance, stock_price, confidence
            )

            # リスク調整
            risk_adjusted_size = self._apply_risk_adjustment(base_size, risk_level)

            # ボラティリティ調整
            if self.volatility_adjustment:
                volatility_adjusted_size = self._apply_volatility_adjustment(
                    risk_adjusted_size, volatility
                )
            else:
                volatility_adjusted_size = risk_adjusted_size

            # 相関調整
            if self.correlation_adjustment:
                correlation_adjusted_size = self._apply_correlation_adjustment(
                    volatility_adjusted_size, correlation
                )
            else:
                correlation_adjusted_size = volatility_adjusted_size

            # ポートフォリオ相関調整
            portfolio_adjusted_size = self._apply_portfolio_correlation_adjustment(
                correlation_adjusted_size, portfolio_correlation
            )

            # 最大損失額制限
            if max_loss_amount is not None:
                portfolio_adjusted_size = self._apply_max_loss_limit(
                    portfolio_adjusted_size, stock_price, max_loss_amount
                )

            # 最終調整
            final_size = self._apply_final_adjustments(
                portfolio_adjusted_size, account_balance, stock_price
            )

            # リスクメトリクス計算
            risk_metrics = self._calculate_position_risk_metrics(
                final_size, stock_price, volatility, correlation, account_balance
            )

            return {
                "position_size": final_size,
                "base_size": base_size,
                "risk_adjusted_size": risk_adjusted_size,
                "volatility_adjusted_size": volatility_adjusted_size,
                "correlation_adjusted_size": correlation_adjusted_size,
                "portfolio_adjusted_size": portfolio_adjusted_size,
                "confidence": confidence,
                "volatility": volatility,
                "correlation": correlation,
                "portfolio_correlation": portfolio_correlation,
                "risk_level": risk_level,
                "position_value": final_size * stock_price,
                "position_percent": (final_size * stock_price) / account_balance * 100,
                "max_loss_amount": max_loss_amount,
                "risk_metrics": risk_metrics,
            }

        except Exception as e:
            self.logger.error(f"ポジションサイズ計算エラー: {e}")
            return {"position_size": 0, "error": str(e)}

    def _calculate_base_position_size(
        self, account_balance: float, stock_price: float, confidence: float
    ) -> float:
        """基本ポジションサイズの計算"""
        try:
            # 信頼度に基づく基本サイズ
            confidence_factor = (confidence - 0.5) * self.confidence_multiplier
            base_size = self.base_position_size * confidence_factor

            # 資本制限
            max_position_value = account_balance * self.max_position_percent
            max_size = max_position_value / stock_price

            base_size = min(base_size, max_size)

            return max(0, base_size)

        except Exception as e:
            self.logger.error(f"基本ポジションサイズ計算エラー: {e}")
            return 0.0

    def _apply_risk_adjustment(self, base_size: float, risk_level: str) -> float:
        """リスクレベルに基づく調整"""
        try:
            risk_multipliers = {"LOW": 1.0, "MEDIUM": 0.7, "HIGH": 0.3, "CRITICAL": 0.1}

            risk_multiplier = risk_multipliers.get(risk_level, 0.5)
            adjusted_size = base_size * risk_multiplier

            return max(0, adjusted_size)

        except Exception as e:
            self.logger.error(f"リスク調整エラー: {e}")
            return base_size

    def _apply_volatility_adjustment(
        self, base_size: float, volatility: float
    ) -> float:
        """ボラティリティに基づく調整"""
        try:
            if volatility > self.max_volatility:
                # 高ボラティリティの場合はサイズを削減
                volatility_factor = self.max_volatility / volatility
                adjusted_size = base_size * volatility_factor
            else:
                # 低ボラティリティの場合はサイズを増加
                volatility_factor = 1.0 + (self.max_volatility - volatility) * 0.5
                adjusted_size = base_size * volatility_factor

            return max(0, adjusted_size)

        except Exception as e:
            self.logger.error(f"ボラティリティ調整エラー: {e}")
            return base_size

    def _apply_correlation_adjustment(
        self, base_size: float, correlation: float
    ) -> float:
        """相関に基づく調整"""
        try:
            if correlation > self.max_correlation:
                # 高相関の場合はサイズを削減
                correlation_factor = 1.0 - (correlation - self.max_correlation)
                adjusted_size = base_size * correlation_factor
            else:
                # 低相関の場合はサイズを維持
                adjusted_size = base_size

            return max(0, adjusted_size)

        except Exception as e:
            self.logger.error(f"相関調整エラー: {e}")
            return base_size

    def _apply_final_adjustments(
        self, base_size: float, account_balance: float, stock_price: float
    ) -> float:
        """最終調整の適用"""
        try:
            # 最小・最大サイズの制限
            min_size = 1  # 最小1株
            max_size = account_balance * self.max_position_percent / stock_price

            # サイズの調整
            adjusted_size = max(min_size, min(base_size, max_size))

            # 整数化
            final_size = int(adjusted_size)

            return max(0, final_size)

        except Exception as e:
            self.logger.error(f"最終調整エラー: {e}")
            return 0

    def calculate_portfolio_position_sizes(
        self, account_balance: float, stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        ポートフォリオ全体のポジションサイズ計算
        複数銘柄の最適な配分を計算
        """
        try:
            total_positions = {}
            remaining_balance = account_balance

            # 各銘柄のポジションサイズを計算
            for stock in stock_data:
                symbol = stock["symbol"]
                price = stock["price"]
                confidence = stock.get("confidence", 0.7)
                volatility = stock.get("volatility", 0.02)
                correlation = stock.get("correlation", 0.0)
                risk_level = stock.get("risk_level", "MEDIUM")

                # ポジションサイズの計算
                position_info = self.calculate_position_size(
                    remaining_balance,
                    price,
                    confidence,
                    volatility,
                    correlation,
                    risk_level,
                )

                if position_info["position_size"] > 0:
                    total_positions[symbol] = position_info
                    remaining_balance -= position_info["position_value"]

            # ポートフォリオ統計
            total_position_value = sum(
                pos["position_value"] for pos in total_positions.values()
            )
            portfolio_percent = total_position_value / account_balance * 100

            return {
                "positions": total_positions,
                "total_position_value": total_position_value,
                "remaining_balance": remaining_balance,
                "portfolio_percent": portfolio_percent,
                "diversification_score": self._calculate_diversification_score(
                    total_positions
                ),
            }

        except Exception as e:
            self.logger.error(f"ポートフォリオポジションサイズ計算エラー: {e}")
            return {"error": str(e)}

    def _calculate_diversification_score(self, positions: Dict[str, Any]) -> float:
        """分散投資スコアの計算"""
        try:
            if not positions:
                return 0.0

            # ポジション数の分散
            position_count = len(positions)
            count_score = min(position_count / 10, 1.0)  # 最大10銘柄で1.0

            # ポジションサイズの分散
            position_values = [pos["position_value"] for pos in positions.values()]
            if position_values:
                size_variance = np.var(position_values)
                size_score = max(0, 1.0 - size_variance / np.mean(position_values))
            else:
                size_score = 0.0

            # 総合スコア
            diversification_score = (count_score + size_score) / 2

            return diversification_score

        except Exception as e:
            self.logger.error(f"分散投資スコア計算エラー: {e}")
            return 0.0

    def optimize_position_sizes(
        self,
        account_balance: float,
        stock_data: List[Dict[str, Any]],
        target_return: float = 0.1,
        max_risk: float = 0.15,
    ) -> Dict[str, Any]:
        """
        ポジションサイズの最適化
        目標リターンとリスク制限に基づく最適化
        """
        try:
            # 最適化の実行
            optimized_positions = {}
            total_risk = 0.0
            expected_return = 0.0

            # 各銘柄の最適化
            for stock in stock_data:
                symbol = stock["symbol"]
                price = stock["price"]
                confidence = stock.get("confidence", 0.7)
                volatility = stock.get("volatility", 0.02)
                correlation = stock.get("correlation", 0.0)
                risk_level = stock.get("risk_level", "MEDIUM")

                # 最適化されたポジションサイズ
                position_info = self.calculate_position_size(
                    account_balance,
                    price,
                    confidence,
                    volatility,
                    correlation,
                    risk_level,
                )

                # リスク制限のチェック
                position_risk = (
                    position_info["position_size"]
                    * price
                    * volatility
                    / account_balance
                )
                if total_risk + position_risk <= max_risk:
                    optimized_positions[symbol] = position_info
                    total_risk += position_risk
                    expected_return += (
                        position_info["position_size"]
                        * price
                        * confidence
                        / account_balance
                    )

            return {
                "optimized_positions": optimized_positions,
                "total_risk": total_risk,
                "expected_return": expected_return,
                "risk_utilization": total_risk / max_risk * 100,
                "return_target_achievement": expected_return / target_return * 100,
            }

        except Exception as e:
            self.logger.error(f"ポジションサイズ最適化エラー: {e}")
            return {"error": str(e)}

    def optimize_portfolio_allocation(
        self,
        account_balance: float,
        stock_data: List[Dict[str, Any]],
        target_return: float = 0.1,
        max_risk: float = 0.15,
        diversification_target: float = 0.8,
    ) -> Dict[str, Any]:
        """
        ポートフォリオ最適化機能
        リスク・リターン・分散投資を考慮した最適化
        """
        try:
            # 銘柄のリスク・リターン分析
            stock_analysis = self._analyze_stock_risk_return(stock_data)

            # 最適化アルゴリズム（簡易版）
            optimized_allocation = self._calculate_optimal_allocation(
                stock_analysis,
                account_balance,
                target_return,
                max_risk,
                diversification_target,
            )

            # 最適化結果の検証
            validation_result = self._validate_optimization_result(
                optimized_allocation, target_return, max_risk
            )

            return {
                "optimized_allocation": optimized_allocation,
                "stock_analysis": stock_analysis,
                "validation_result": validation_result,
                "diversification_score": self._calculate_diversification_score(
                    optimized_allocation
                ),
                "risk_return_ratio": self._calculate_risk_return_ratio(
                    optimized_allocation
                ),
                "optimization_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"ポートフォリオ最適化エラー: {e}")
            return {"error": str(e)}

    def _analyze_stock_risk_return(
        self, stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """銘柄のリスク・リターン分析"""
        try:
            analysis = {}

            for stock in stock_data:
                symbol = stock["symbol"]
                price = stock["price"]
                confidence = stock.get("confidence", 0.7)
                volatility = stock.get("volatility", 0.02)
                correlation = stock.get("correlation", 0.0)
                risk_level = stock.get("risk_level", "MEDIUM")

                # 期待リターン計算
                expected_return = confidence * 0.1  # 信頼度に基づく期待リターン

                # リスクスコア計算
                risk_score = self._calculate_individual_risk_score(
                    volatility, confidence, risk_level
                )

                # シャープレシオ計算
                sharpe_ratio = expected_return / volatility if volatility > 0 else 0

                analysis[symbol] = {
                    "price": price,
                    "expected_return": expected_return,
                    "volatility": volatility,
                    "risk_score": risk_score,
                    "sharpe_ratio": sharpe_ratio,
                    "confidence": confidence,
                    "correlation": correlation,
                    "risk_level": risk_level,
                }

            return analysis

        except Exception as e:
            self.logger.error(f"リスク・リターン分析エラー: {e}")
            return {}

    def _calculate_optimal_allocation(
        self,
        stock_analysis: Dict[str, Any],
        account_balance: float,
        target_return: float,
        max_risk: float,
        diversification_target: float,
    ) -> Dict[str, Any]:
        """最適配分の計算"""
        try:
            # シャープレシオでソート
            sorted_stocks = sorted(
                stock_analysis.items(), key=lambda x: x[1]["sharpe_ratio"], reverse=True
            )

            allocation = {}
            total_allocation = 0.0
            remaining_balance = account_balance

            # 上位銘柄から配分
            for symbol, analysis in sorted_stocks:
                if remaining_balance <= 0:
                    break

                # 配分率計算（シャープレシオに基づく）
                allocation_ratio = min(0.2, analysis["sharpe_ratio"] * 0.1)  # 最大20%
                allocation_amount = account_balance * allocation_ratio

                if allocation_amount <= remaining_balance:
                    position_size = allocation_amount / analysis["price"]

                    allocation[symbol] = {
                        "position_size": position_size,
                        "allocation_amount": allocation_amount,
                        "allocation_ratio": allocation_ratio,
                        "expected_return": analysis["expected_return"],
                        "volatility": analysis["volatility"],
                        "sharpe_ratio": analysis["sharpe_ratio"],
                    }

                    total_allocation += allocation_amount
                    remaining_balance -= allocation_amount

            return {
                "allocations": allocation,
                "total_allocation": total_allocation,
                "remaining_balance": remaining_balance,
                "cash_ratio": remaining_balance / account_balance,
            }

        except Exception as e:
            self.logger.error(f"最適配分計算エラー: {e}")
            return {}

    def _validate_optimization_result(
        self, allocation: Dict[str, Any], target_return: float, max_risk: float
    ) -> Dict[str, Any]:
        """最適化結果の検証"""
        try:
            if not allocation or "allocations" not in allocation:
                return {"valid": False, "error": "配分データがありません"}

            total_risk = 0.0
            total_return = 0.0

            for symbol, data in allocation["allocations"].items():
                position_risk = (
                    data["allocation_amount"]
                    * data["volatility"]
                    / allocation["total_allocation"]
                )
                position_return = (
                    data["allocation_amount"]
                    * data["expected_return"]
                    / allocation["total_allocation"]
                )

                total_risk += position_risk
                total_return += position_return

            # 検証結果
            risk_ok = total_risk <= max_risk
            return_ok = total_return >= target_return

            return {
                "valid": risk_ok and return_ok,
                "total_risk": total_risk,
                "total_return": total_return,
                "risk_ok": risk_ok,
                "return_ok": return_ok,
                "risk_utilization": total_risk / max_risk * 100,
                "return_achievement": total_return / target_return * 100,
            }

        except Exception as e:
            self.logger.error(f"最適化結果検証エラー: {e}")
            return {"valid": False, "error": str(e)}

    def _calculate_risk_return_ratio(self, allocation: Dict[str, Any]) -> float:
        """リスク・リターン比率の計算"""
        try:
            if not allocation or "allocations" not in allocation:
                return 0.0

            total_return = 0.0
            total_risk = 0.0

            for data in allocation["allocations"].values():
                total_return += data["expected_return"] * data["allocation_ratio"]
                total_risk += data["volatility"] * data["allocation_ratio"]

            return total_return / total_risk if total_risk > 0 else 0.0

        except Exception as e:
            self.logger.error(f"リスク・リターン比率計算エラー: {e}")
            return 0.0

    def _apply_portfolio_correlation_adjustment(
        self, base_size: float, portfolio_correlation: float
    ) -> float:
        """ポートフォリオ相関に基づく調整"""
        try:
            if portfolio_correlation > 0.8:
                # 高相関の場合は大幅に削減
                correlation_factor = 1.0 - (portfolio_correlation - 0.8) * 0.5
                adjusted_size = base_size * correlation_factor
            elif portfolio_correlation > 0.6:
                # 中相関の場合は適度に削減
                correlation_factor = 1.0 - (portfolio_correlation - 0.6) * 0.3
                adjusted_size = base_size * correlation_factor
            else:
                # 低相関の場合は維持
                adjusted_size = base_size

            return max(0, adjusted_size)

        except Exception as e:
            self.logger.error(f"ポートフォリオ相関調整エラー: {e}")
            return base_size

    def _apply_max_loss_limit(
        self, base_size: float, stock_price: float, max_loss_amount: float
    ) -> float:
        """最大損失額制限の適用"""
        try:
            # 最大損失額に基づくポジションサイズ計算
            max_size_by_loss = max_loss_amount / stock_price

            # より小さい方を選択
            limited_size = min(base_size, max_size_by_loss)

            return max(0, limited_size)

        except Exception as e:
            self.logger.error(f"最大損失額制限適用エラー: {e}")
            return base_size

    def _calculate_position_risk_metrics(
        self,
        position_size: float,
        stock_price: float,
        volatility: float,
        correlation: float,
        account_balance: float,
    ) -> Dict[str, Any]:
        """ポジションリスクメトリクスの計算"""
        try:
            position_value = position_size * stock_price
            position_percent = position_value / account_balance

            # 1日あたりの最大損失（95%信頼区間）
            daily_var = position_value * volatility * 1.96

            # ポートフォリオへの影響度
            portfolio_impact = position_percent * volatility

            # リスクスコア（0-100）
            risk_score = min(
                100, (position_percent * 50) + (volatility * 1000) + (correlation * 50)
            )

            return {
                "position_value": position_value,
                "position_percent": position_percent,
                "daily_var": daily_var,
                "portfolio_impact": portfolio_impact,
                "risk_score": risk_score,
                "volatility_contribution": volatility * position_percent,
                "correlation_risk": correlation * position_percent,
            }

        except Exception as e:
            self.logger.error(f"リスクメトリクス計算エラー: {e}")
            return {
                "position_value": 0,
                "position_percent": 0,
                "daily_var": 0,
                "portfolio_impact": 0,
                "risk_score": 0,
                "volatility_contribution": 0,
                "correlation_risk": 0,
            }

    def calculate_individual_stock_limits(
        self,
        account_balance: float,
        stock_data: List[Dict[str, Any]],
        max_total_loss: float = None,
    ) -> Dict[str, Any]:
        """個別銘柄の最大損失額設定"""
        try:
            if max_total_loss is None:
                max_total_loss = account_balance * 0.1  # デフォルト10%

            individual_limits = {}
            total_allocated = 0.0

            # 各銘柄のリスクに基づく損失額配分
            for stock in stock_data:
                symbol = stock["symbol"]
                volatility = stock.get("volatility", 0.02)
                confidence = stock.get("confidence", 0.7)
                risk_level = stock.get("risk_level", "MEDIUM")

                # リスクスコア計算
                risk_score = self._calculate_individual_risk_score(
                    volatility, confidence, risk_level
                )

                # 損失額配分（リスクスコアに反比例）
                max_loss_ratio = 1.0 / (risk_score + 1.0)
                max_loss_amount = max_total_loss * max_loss_ratio

                individual_limits[symbol] = {
                    "max_loss_amount": max_loss_amount,
                    "risk_score": risk_score,
                    "volatility": volatility,
                    "confidence": confidence,
                    "risk_level": risk_level,
                    "max_loss_ratio": max_loss_ratio,
                }

                total_allocated += max_loss_amount

            return {
                "individual_limits": individual_limits,
                "total_allocated": total_allocated,
                "max_total_loss": max_total_loss,
                "utilization_rate": total_allocated / max_total_loss
                if max_total_loss > 0
                else 0,
            }

        except Exception as e:
            self.logger.error(f"個別銘柄損失額設定エラー: {e}")
            return {"error": str(e)}

    def _calculate_individual_risk_score(
        self, volatility: float, confidence: float, risk_level: str
    ) -> float:
        """個別銘柄のリスクスコア計算"""
        try:
            # リスクレベル重み
            risk_weights = {"LOW": 1.0, "MEDIUM": 2.0, "HIGH": 3.0, "CRITICAL": 5.0}

            risk_weight = risk_weights.get(risk_level, 2.0)

            # リスクスコア = ボラティリティ × リスク重み × (1 - 信頼度)
            risk_score = volatility * risk_weight * (1.0 - confidence)

            return max(0.1, risk_score)  # 最小値0.1

        except Exception as e:
            self.logger.error(f"リスクスコア計算エラー: {e}")
            return 1.0

    def get_position_sizing_recommendations(
        self, account_balance: float, stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """ポジションサイジングの推奨事項"""
        try:
            recommendations = []

            for stock in stock_data:
                symbol = stock["symbol"]
                confidence = stock.get("confidence", 0.7)
                volatility = stock.get("volatility", 0.02)
                risk_level = stock.get("risk_level", "MEDIUM")

                # 推奨事項の生成
                if confidence < self.min_confidence:
                    recommendations.append(
                        {
                            "symbol": symbol,
                            "type": "LOW_CONFIDENCE",
                            "message": "信頼度が低いため取引を控えることを推奨",
                            "confidence": confidence,
                        }
                    )
                elif volatility > self.max_volatility:
                    recommendations.append(
                        {
                            "symbol": symbol,
                            "type": "HIGH_VOLATILITY",
                            "message": "ボラティリティが高いためポジションサイズを削減",
                            "volatility": volatility,
                        }
                    )
                elif risk_level == "HIGH":
                    recommendations.append(
                        {
                            "symbol": symbol,
                            "type": "HIGH_RISK",
                            "message": "リスクレベルが高いため注意深く監視",
                            "risk_level": risk_level,
                        }
                    )
                else:
                    recommendations.append(
                        {
                            "symbol": symbol,
                            "type": "GOOD",
                            "message": "取引条件が良好",
                            "confidence": confidence,
                        }
                    )

            return {
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "high_priority": len(
                    [
                        r
                        for r in recommendations
                        if r["type"] in ["LOW_CONFIDENCE", "HIGH_VOLATILITY"]
                    ]
                ),
            }

        except Exception as e:
            self.logger.error(f"推奨事項生成エラー: {e}")
            return {"error": str(e)}
