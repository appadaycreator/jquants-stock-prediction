#!/usr/bin/env python3
"""
高度な数量計算システム
具体的な数量と価格を計算するロジック
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging


@dataclass
class QuantityCalculationResult:
    """数量計算結果"""

    quantity: int
    total_amount: float
    unit_price: float
    commission: float
    slippage: float
    net_amount: float
    position_size_percentage: float
    risk_amount: float
    expected_return: float
    max_loss: float
    confidence_level: str
    risk_adjusted_quantity: int


class AdvancedQuantityCalculator:
    """高度な数量計算システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 基本設定
        self.total_capital = self.config.get("total_capital", 1000000)  # 100万円
        self.max_position_size = self.config.get("max_position_size", 0.1)  # 10%
        self.min_position_size = self.config.get("min_position_size", 0.01)  # 1%
        self.risk_per_trade = self.config.get("risk_per_trade", 0.02)  # 2%

        # 取引コスト
        self.commission_rate = self.config.get("commission_rate", 0.001)  # 0.1%
        self.slippage_rate = self.config.get("slippage_rate", 0.0005)  # 0.05%

        # リスク管理
        self.max_daily_loss = self.config.get("max_daily_loss", 0.05)  # 5%
        self.volatility_adjustment = self.config.get("volatility_adjustment", True)
        self.correlation_adjustment = self.config.get("correlation_adjustment", True)

        # 最小取引単位
        self.min_trade_unit = self.config.get("min_trade_unit", 100)  # 100株
        self.min_trade_amount = self.config.get("min_trade_amount", 10000)  # 1万円

    def calculate_optimal_quantity(
        self,
        symbol: str,
        current_price: float,
        target_price: float,
        confidence: float,
        volatility: float,
        existing_position: Optional[Dict[str, Any]] = None,
        portfolio_positions: List[Dict[str, Any]] = None,
        market_condition: str = "normal",
    ) -> QuantityCalculationResult:
        """最適数量の計算"""
        try:
            self.logger.info(f"最適数量計算開始: {symbol}")

            # 基本数量計算
            base_quantity = self._calculate_base_quantity(
                current_price, confidence, volatility
            )

            # リスク調整
            risk_adjusted_quantity = self._apply_risk_adjustment(
                base_quantity, current_price, volatility, confidence
            )

            # ボラティリティ調整
            if self.volatility_adjustment:
                risk_adjusted_quantity = self._apply_volatility_adjustment(
                    risk_adjusted_quantity, volatility
                )

            # 相関調整
            if self.correlation_adjustment and portfolio_positions:
                risk_adjusted_quantity = self._apply_correlation_adjustment(
                    risk_adjusted_quantity, symbol, portfolio_positions
                )

            # 市場条件調整
            risk_adjusted_quantity = self._apply_market_condition_adjustment(
                risk_adjusted_quantity, market_condition, confidence
            )

            # 既存ポジション調整
            if existing_position:
                risk_adjusted_quantity = self._apply_existing_position_adjustment(
                    risk_adjusted_quantity, existing_position
                )

            # 最小・最大制限の適用
            final_quantity = self._apply_quantity_limits(
                risk_adjusted_quantity, current_price
            )

            # 取引コストの計算
            commission = final_quantity * current_price * self.commission_rate
            slippage = final_quantity * current_price * self.slippage_rate
            total_amount = final_quantity * current_price
            net_amount = total_amount + commission + slippage

            # ポジションサイズの計算
            position_size_percentage = (total_amount / self.total_capital) * 100

            # リスク金額の計算
            risk_amount = self._calculate_risk_amount(
                final_quantity, current_price, target_price, volatility
            )

            # 期待リターンの計算
            expected_return = self._calculate_expected_return(
                final_quantity, current_price, target_price, confidence
            )

            # 最大損失の計算
            max_loss = self._calculate_max_loss(
                final_quantity, current_price, volatility
            )

            # 信頼度レベルの判定
            confidence_level = self._determine_confidence_level(confidence)

            result = QuantityCalculationResult(
                quantity=final_quantity,
                total_amount=total_amount,
                unit_price=current_price,
                commission=commission,
                slippage=slippage,
                net_amount=net_amount,
                position_size_percentage=position_size_percentage,
                risk_amount=risk_amount,
                expected_return=expected_return,
                max_loss=max_loss,
                confidence_level=confidence_level,
                risk_adjusted_quantity=risk_adjusted_quantity,
            )

            self.logger.info(f"最適数量計算完了: {symbol} - {final_quantity}株")
            return result

        except Exception as e:
            self.logger.error(f"最適数量計算エラー ({symbol}): {e}")
            return self._create_error_result()

    def _calculate_base_quantity(
        self, current_price: float, confidence: float, volatility: float
    ) -> int:
        """基本数量の計算"""
        try:
            # ケリー基準による基本数量計算
            win_rate = confidence
            avg_win = 0.1  # 平均勝利時のリターン
            avg_loss = 0.05  # 平均損失時のリターン

            kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # 最大25%に制限

            # 基本投資金額
            base_amount = self.total_capital * kelly_fraction

            # 信頼度による調整
            confidence_multiplier = 0.5 + (confidence - 0.5) * 2  # 0.5-1.5倍
            adjusted_amount = base_amount * confidence_multiplier

            # 数量計算
            quantity = int(adjusted_amount / current_price)

            return max(0, quantity)

        except Exception as e:
            self.logger.error(f"基本数量計算エラー: {e}")
            return 0

    def _apply_risk_adjustment(
        self, quantity: int, current_price: float, volatility: float, confidence: float
    ) -> int:
        """リスク調整の適用"""
        try:
            # ボラティリティに基づく調整
            volatility_factor = 1.0 / (1.0 + volatility)

            # 信頼度に基づく調整
            confidence_factor = confidence

            # リスク調整係数
            risk_factor = volatility_factor * confidence_factor

            # 調整後の数量
            adjusted_quantity = int(quantity * risk_factor)

            return max(0, adjusted_quantity)

        except Exception as e:
            self.logger.error(f"リスク調整エラー: {e}")
            return quantity

    def _apply_volatility_adjustment(self, quantity: int, volatility: float) -> int:
        """ボラティリティ調整の適用"""
        try:
            # 高ボラティリティ時は数量を減らす
            if volatility > 0.3:  # 30%以上のボラティリティ
                adjustment_factor = 0.5
            elif volatility > 0.2:  # 20%以上のボラティリティ
                adjustment_factor = 0.7
            elif volatility < 0.1:  # 10%未満のボラティリティ
                adjustment_factor = 1.2
            else:
                adjustment_factor = 1.0

            adjusted_quantity = int(quantity * adjustment_factor)
            return max(0, adjusted_quantity)

        except Exception as e:
            self.logger.error(f"ボラティリティ調整エラー: {e}")
            return quantity

    def _apply_correlation_adjustment(
        self, quantity: int, symbol: str, portfolio_positions: List[Dict[str, Any]]
    ) -> int:
        """相関調整の適用"""
        try:
            # 既存ポジションとの相関を計算
            correlation_factor = 1.0

            for position in portfolio_positions:
                if position["symbol"] != symbol:
                    # 簡易相関計算（実際の実装ではより詳細な相関分析が必要）
                    sector_correlation = self._calculate_sector_correlation(
                        symbol, position["symbol"]
                    )

                    # 高相関の場合は数量を減らす
                    if sector_correlation > 0.7:
                        correlation_factor *= 0.8
                    elif sector_correlation > 0.5:
                        correlation_factor *= 0.9

            adjusted_quantity = int(quantity * correlation_factor)
            return max(0, adjusted_quantity)

        except Exception as e:
            self.logger.error(f"相関調整エラー: {e}")
            return quantity

    def _apply_market_condition_adjustment(
        self, quantity: int, market_condition: str, confidence: float
    ) -> int:
        """市場条件調整の適用"""
        try:
            adjustment_factor = 1.0

            if market_condition == "bull_market":
                adjustment_factor = 1.2
            elif market_condition == "bear_market":
                adjustment_factor = 0.8
            elif market_condition == "high_volatility":
                adjustment_factor = 0.7
            elif market_condition == "crisis":
                adjustment_factor = 0.5

            # 信頼度による追加調整
            if confidence > 0.8:
                adjustment_factor *= 1.1
            elif confidence < 0.6:
                adjustment_factor *= 0.9

            adjusted_quantity = int(quantity * adjustment_factor)
            return max(0, adjusted_quantity)

        except Exception as e:
            self.logger.error(f"市場条件調整エラー: {e}")
            return quantity

    def _apply_existing_position_adjustment(
        self, quantity: int, existing_position: Dict[str, Any]
    ) -> int:
        """既存ポジション調整の適用"""
        try:
            current_position_size = existing_position.get("position_size_percentage", 0)

            # 既存ポジションが大きすぎる場合は数量を減らす
            if current_position_size > self.max_position_size * 0.8:
                adjustment_factor = 0.5
            elif current_position_size > self.max_position_size * 0.5:
                adjustment_factor = 0.7
            else:
                adjustment_factor = 1.0

            adjusted_quantity = int(quantity * adjustment_factor)
            return max(0, adjusted_quantity)

        except Exception as e:
            self.logger.error(f"既存ポジション調整エラー: {e}")
            return quantity

    def _apply_quantity_limits(self, quantity: int, current_price: float) -> int:
        """数量制限の適用"""
        try:
            # 最小取引単位での調整
            quantity = (quantity // self.min_trade_unit) * self.min_trade_unit

            # 最大ポジションサイズ制限
            max_quantity_by_position = int(
                (self.total_capital * self.max_position_size) / current_price
            )
            quantity = min(quantity, max_quantity_by_position)

            # 最小取引金額制限
            min_quantity_by_amount = int(self.min_trade_amount / current_price)
            if quantity < min_quantity_by_amount:
                quantity = 0

            return max(0, quantity)

        except Exception as e:
            self.logger.error(f"数量制限適用エラー: {e}")
            return 0

    def _calculate_risk_amount(
        self,
        quantity: int,
        current_price: float,
        target_price: float,
        volatility: float,
    ) -> float:
        """リスク金額の計算"""
        try:
            # VaR（Value at Risk）計算
            confidence_level = 0.95
            z_score = 1.96  # 95%信頼区間

            # 1日リスク
            daily_risk = quantity * current_price * volatility * z_score

            return daily_risk

        except Exception as e:
            self.logger.error(f"リスク金額計算エラー: {e}")
            return 0

    def _calculate_expected_return(
        self,
        quantity: int,
        current_price: float,
        target_price: float,
        confidence: float,
    ) -> float:
        """期待リターンの計算"""
        try:
            price_change = target_price - current_price
            expected_return = quantity * price_change * confidence

            return expected_return

        except Exception as e:
            self.logger.error(f"期待リターン計算エラー: {e}")
            return 0

    def _calculate_max_loss(
        self, quantity: int, current_price: float, volatility: float
    ) -> float:
        """最大損失の計算"""
        try:
            # 最大損失は3σ（99.7%信頼区間）での損失
            max_loss_percentage = volatility * 3
            max_loss = quantity * current_price * max_loss_percentage

            return max_loss

        except Exception as e:
            self.logger.error(f"最大損失計算エラー: {e}")
            return 0

    def _determine_confidence_level(self, confidence: float) -> str:
        """信頼度レベルの判定"""
        if confidence >= 0.9:
            return "VERY_HIGH"
        elif confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.7:
            return "MEDIUM"
        elif confidence >= 0.6:
            return "LOW"
        else:
            return "VERY_LOW"

    def _calculate_sector_correlation(self, symbol1: str, symbol2: str) -> float:
        """セクター相関の計算（簡易版）"""
        try:
            # 実際の実装では、より詳細な相関分析が必要
            # ここでは簡易的な実装

            # セクター分類（簡易版）
            sectors = {
                "7203": "automotive",  # トヨタ
                "6758": "technology",  # ソニー
                "9984": "retail",  # ソフトバンクG
                "9432": "telecom",  # NTT
                "6861": "technology",  # キーエンス
            }

            sector1 = sectors.get(symbol1, "other")
            sector2 = sectors.get(symbol2, "other")

            if sector1 == sector2:
                return 0.8
            elif sector1 in ["technology", "automotive"] and sector2 in [
                "technology",
                "automotive",
            ]:
                return 0.6
            else:
                return 0.3

        except Exception as e:
            self.logger.error(f"セクター相関計算エラー: {e}")
            return 0.5

    def _create_error_result(self) -> QuantityCalculationResult:
        """エラー時の結果作成"""
        return QuantityCalculationResult(
            quantity=0,
            total_amount=0,
            unit_price=0,
            commission=0,
            slippage=0,
            net_amount=0,
            position_size_percentage=0,
            risk_amount=0,
            expected_return=0,
            max_loss=0,
            confidence_level="ERROR",
            risk_adjusted_quantity=0,
        )

    def calculate_portfolio_risk(
        self, positions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """ポートフォリオリスクの計算"""
        try:
            total_value = sum(pos.get("market_value", 0) for pos in positions)
            total_risk = 0
            max_single_position_risk = 0

            for position in positions:
                market_value = position.get("market_value", 0)
                volatility = position.get("volatility", 0.2)

                # 個別リスク
                position_risk = market_value * volatility
                total_risk += position_risk

                # 最大単一ポジションリスク
                max_single_position_risk = max(max_single_position_risk, position_risk)

            # ポートフォリオ全体のリスク
            portfolio_volatility = total_risk / total_value if total_value > 0 else 0

            return {
                "total_risk": total_risk,
                "portfolio_volatility": portfolio_volatility,
                "max_single_position_risk": max_single_position_risk,
                "risk_concentration": max_single_position_risk / total_risk
                if total_risk > 0
                else 0,
            }

        except Exception as e:
            self.logger.error(f"ポートフォリオリスク計算エラー: {e}")
            return {
                "total_risk": 0,
                "portfolio_volatility": 0,
                "max_single_position_risk": 0,
                "risk_concentration": 0,
            }
