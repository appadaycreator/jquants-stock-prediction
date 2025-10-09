#!/usr/bin/env python3
"""
投資判断の明確化機能
曖昧な推奨を排除し、具体的なアクションを提示するシステム
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import json


class InvestmentAction(Enum):
    """投資アクションの種類"""

    BUY_MORE = "buy_more"  # 買い増し
    TAKE_PROFIT = "take_profit"  # 利確
    STOP_LOSS = "stop_loss"  # 損切り
    NEW_PURCHASE = "new_purchase"  # 新規購入


class ActionPriority(Enum):
    """アクションの優先度"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DeadlineType(Enum):
    """期限の種類"""

    IMMEDIATE = "immediate"  # 即座に実行
    THIS_WEEK = "this_week"  # 今週中
    THIS_MONTH = "this_month"  # 今月中
    NEXT_QUARTER = "next_quarter"  # 来四半期


@dataclass
class InvestmentActionDetail:
    """投資アクションの詳細情報"""

    action: InvestmentAction
    symbol: str
    current_price: float
    target_price: float
    quantity: int
    total_amount: float
    priority: ActionPriority
    deadline: datetime
    deadline_type: DeadlineType
    confidence: float
    reason: str
    risk_level: str
    expected_return: float
    max_loss: float
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    position_size_percentage: float = 0.0
    market_condition: str = ""
    technical_signals: List[str] = None
    fundamental_factors: List[str] = None

    def __post_init__(self):
        if self.technical_signals is None:
            self.technical_signals = []
        if self.fundamental_factors is None:
            self.fundamental_factors = []


@dataclass
class PositionInfo:
    """ポジション情報"""

    symbol: str
    current_quantity: int
    average_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    market_value: float
    cost_basis: float


class ClearInvestmentActions:
    """投資判断の明確化システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 設定値の取得
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.7)
        self.max_position_size = self.config.get("max_position_size", 0.1)  # 10%
        self.risk_tolerance = self.config.get("risk_tolerance", 0.05)  # 5%
        self.stop_loss_percentage = self.config.get("stop_loss_percentage", 0.05)  # 5%
        self.take_profit_percentage = self.config.get(
            "take_profit_percentage", 0.15
        )  # 15%

        # 強化された設定
        self.high_confidence_threshold = 0.8  # 高信頼度閾値
        self.ultra_high_confidence_threshold = 0.9  # 超高信頼度閾値
        self.quick_decision_threshold = 0.85  # 迅速判断閾値
        self.position_scaling_factor = 0.2  # ポジションスケーリング係数
        self.volatility_adjustment_factor = 0.1  # ボラティリティ調整係数

        # 期限設定
        self.deadline_config = {
            "immediate": timedelta(hours=1),
            "this_week": timedelta(days=7),
            "this_month": timedelta(days=30),
            "next_quarter": timedelta(days=90),
        }

        # アクション履歴
        self.action_history = []

    def analyze_position(self, position: PositionInfo, market_data: Dict[str, Any]) -> Optional[InvestmentActionDetail]:
        """ポジション分析"""
        try:
            if not market_data:
                self.logger.warning("市場データが不足しています")
                return None
            
            # 信頼度計算
            confidence = self._calculate_confidence(position, market_data)
            
            # アクション決定
            action = self._determine_action(position, market_data, confidence)
            if action is None:
                return None
            
            # ポジションサイズ計算
            position_size = self._calculate_position_size(position, market_data, confidence, action)
            
            # 目標価格計算
            target_price = self._calculate_target_price(position, market_data, action)
            
            # 優先度決定
            priority = self._determine_priority(position, market_data, confidence, action)
            
            # 期限計算
            deadline, deadline_type = self._calculate_deadline(position, market_data, confidence, action)
            
            # 期待リターン計算
            expected_return = self._calculate_expected_return(position, market_data, action)
            
            # 最大損失計算
            max_loss = self._calculate_max_loss(position, market_data, action)
            
            # 理由生成
            reason = self._generate_reason(position, market_data, action)
            
            # リスクレベル決定
            risk_level = self._determine_risk_level(position, market_data)
            
            # テクニカルシグナル取得
            technical_signals = self._get_technical_signals(market_data)
            
            # ファンダメンタル要因取得
            fundamental_factors = self._get_fundamental_factors(position, market_data)
            
            return InvestmentActionDetail(
                action=action,
                symbol=position.symbol,
                current_price=position.current_price,
                target_price=target_price,
                quantity=position_size,
                total_amount=position_size * position.current_price,
                priority=priority,
                deadline=deadline,
                deadline_type=deadline_type,
                confidence=confidence,
                reason=reason,
                risk_level=risk_level,
                expected_return=expected_return,
                max_loss=max_loss,
                stop_loss_price=position.current_price * (1 - self.stop_loss_percentage) if action == InvestmentAction.BUY_MORE else None,
                take_profit_price=position.current_price * (1 + self.take_profit_percentage) if action == InvestmentAction.TAKE_PROFIT else None,
                position_size_percentage=position_size / position.current_quantity if position.current_quantity > 0 else 0,
                market_condition=market_data.get("trend", "neutral"),
                technical_signals=technical_signals,
                fundamental_factors=fundamental_factors,
            )
        except Exception as e:
            self.logger.error(f"ポジション分析エラー: {e}")
            return None

    def generate_clear_actions(
        self,
        market_data: List[Dict[str, Any]],
        positions: List[PositionInfo],
        predictions: List[float],
        confidence_scores: List[float],
    ) -> List[InvestmentActionDetail]:
        """明確な投資アクションを生成"""
        try:
            self.logger.info("明確な投資アクションの生成を開始")

            actions = []

            # 各銘柄についてアクションを判定
            for i, data in enumerate(market_data):
                symbol = data.get("symbol", f"STOCK_{i}")
                current_price = data.get("close", 0)
                prediction = predictions[i] if i < len(predictions) else 0
                confidence = confidence_scores[i] if i < len(confidence_scores) else 0

                # 信頼度チェック
                if confidence < self.min_confidence_threshold:
                    continue

                # 既存ポジションの確認
                existing_position = self._find_position(symbol, positions)

                # アクション判定
                action = self._determine_action(
                    symbol,
                    current_price,
                    prediction,
                    confidence,
                    existing_position,
                    data,
                )

                if action:
                    actions.append(action)

            # アクションの優先度付けと期限設定
            actions = self._prioritize_actions(actions)
            actions = self._set_deadlines(actions)

            # 履歴に追加
            self.action_history.extend(actions)

            self.logger.info(f"{len(actions)}個の明確なアクションを生成")
            return actions

        except Exception as e:
            self.logger.error(f"明確なアクション生成エラー: {e}")
            return []

    def _determine_action(
        self,
        position: PositionInfo,
        market_data: Dict[str, Any],
        confidence: float,
        existing_position: Optional[PositionInfo] = None,
    ) -> Optional[InvestmentActionDetail]:
        """具体的なアクションを判定（強化版）"""
        try:
            # 価格変動率の計算
            price_change_ratio = (position.current_price - position.average_price) / position.average_price

            # 技術指標の取得
            technical_signals = self._analyze_technical_indicators(market_data)
            fundamental_factors = self._analyze_fundamental_factors(market_data)

            # 市場条件の判定
            market_condition = self._assess_market_condition(market_data)

            # 信頼度ベースの判定強化
            if confidence < self.min_confidence_threshold:
                self.logger.info(f"信頼度不足: {position.symbol} (信頼度: {confidence:.2f})")
                return None

            # アクション判定ロジック
            if position.pnl_percentage < -0.1:  # 10%以上の損失
                action = InvestmentAction.STOP_LOSS
            elif position.pnl_percentage > 0.2:  # 20%以上の利益
                action = InvestmentAction.TAKE_PROFIT
            elif price_change_ratio > 0.05:  # 5%以上の上昇
                action = InvestmentAction.BUY_MORE
            else:
                action = InvestmentAction.HOLD

            return action

        except Exception as e:
            self.logger.error(f"アクション判定エラー ({position.symbol}): {e}")
            return None

    def _determine_existing_position_action(
        self,
        symbol: str,
        current_price: float,
        prediction: float,
        confidence: float,
        position: PositionInfo,
        technical_signals: List[str],
        fundamental_factors: List[str],
        market_condition: str,
    ) -> Optional[InvestmentActionDetail]:
        """既存ポジションのアクション判定"""

        # 損切り判定
        if position.pnl_percentage <= -self.stop_loss_percentage * 100:
            return InvestmentActionDetail(
                action=InvestmentAction.STOP_LOSS,
                symbol=symbol,
                current_price=current_price,
                target_price=current_price * 0.95,  # 5%下げて売却
                quantity=position.current_quantity,
                total_amount=position.current_quantity * current_price,
                priority=ActionPriority.HIGH,
                deadline=datetime.now() + self.deadline_config["immediate"],
                deadline_type=DeadlineType.IMMEDIATE,
                confidence=confidence,
                reason=f"損切り: {position.pnl_percentage:.1f}%の損失",
                risk_level="HIGH",
                expected_return=position.pnl,
                max_loss=position.pnl,
                stop_loss_price=current_price * 0.95,
                technical_signals=technical_signals,
                fundamental_factors=fundamental_factors,
                market_condition=market_condition,
            )

        # 利確判定
        if position.pnl_percentage >= self.take_profit_percentage * 100:
            return InvestmentActionDetail(
                action=InvestmentAction.TAKE_PROFIT,
                symbol=symbol,
                current_price=current_price,
                target_price=current_price,
                quantity=position.current_quantity,
                total_amount=position.current_quantity * current_price,
                priority=ActionPriority.MEDIUM,
                deadline=datetime.now() + self.deadline_config["this_week"],
                deadline_type=DeadlineType.THIS_WEEK,
                confidence=confidence,
                reason=f"利確: {position.pnl_percentage:.1f}%の利益",
                risk_level="LOW",
                expected_return=position.pnl,
                max_loss=0,
                take_profit_price=current_price,
                technical_signals=technical_signals,
                fundamental_factors=fundamental_factors,
                market_condition=market_condition,
            )

        # 買い増し判定
        if (
            prediction > current_price * 1.05
            and confidence > 0.8  # 5%以上の上昇予測
            and position.pnl_percentage > -2  # 高信頼度
        ):  # 大きな損失がない
            additional_quantity = self._calculate_buy_more_quantity(
                current_price, confidence, position
            )

            if additional_quantity > 0:
                return InvestmentActionDetail(
                    action=InvestmentAction.BUY_MORE,
                    symbol=symbol,
                    current_price=current_price,
                    target_price=prediction,
                    quantity=additional_quantity,
                    total_amount=additional_quantity * current_price,
                    priority=ActionPriority.MEDIUM,
                    deadline=datetime.now() + self.deadline_config["this_week"],
                    deadline_type=DeadlineType.THIS_WEEK,
                    confidence=confidence,
                    reason=f"買い増し: {((prediction - current_price) / current_price * 100):.1f}%の上昇予測",
                    risk_level="MEDIUM",
                    expected_return=(prediction - current_price) * additional_quantity,
                    max_loss=(current_price - prediction) * additional_quantity,
                    stop_loss_price=current_price * 0.95,
                    take_profit_price=prediction,
                    position_size_percentage=additional_quantity
                    * current_price
                    / (position.market_value + additional_quantity * current_price),
                    technical_signals=technical_signals,
                    fundamental_factors=fundamental_factors,
                    market_condition=market_condition,
                )

        return None

    def _determine_new_position_action(
        self,
        symbol: str,
        current_price: float,
        prediction: float,
        confidence: float,
        technical_signals: List[str],
        fundamental_factors: List[str],
        market_condition: str,
    ) -> Optional[InvestmentActionDetail]:
        """新規ポジションのアクション判定"""

        # 新規購入判定
        if (
            prediction >= current_price * 1.03
            and confidence >= 0.75  # 3%以上の上昇予測
        ):  # 高信頼度
            quantity = self._calculate_new_purchase_quantity(
                current_price, confidence, market_condition
            )

            if quantity > 0:
                return InvestmentActionDetail(
                    action=InvestmentAction.NEW_PURCHASE,
                    symbol=symbol,
                    current_price=current_price,
                    target_price=prediction,
                    quantity=quantity,
                    total_amount=quantity * current_price,
                    priority=ActionPriority.MEDIUM,
                    deadline=datetime.now() + self.deadline_config["this_week"],
                    deadline_type=DeadlineType.THIS_WEEK,
                    confidence=confidence,
                    reason=f"新規購入: {((prediction - current_price) / current_price * 100):.1f}%の上昇予測",
                    risk_level="MEDIUM",
                    expected_return=(prediction - current_price) * quantity,
                    max_loss=(current_price - prediction) * quantity,
                    stop_loss_price=current_price * 0.95,
                    take_profit_price=prediction,
                    position_size_percentage=quantity
                    * current_price
                    / 1000000,  # 仮の総資産
                    technical_signals=technical_signals,
                    fundamental_factors=fundamental_factors,
                    market_condition=market_condition,
                )

        return None

    def _calculate_buy_more_quantity(
        self, current_price: float, confidence: float, position: PositionInfo
    ) -> int:
        """買い増し数量の計算（強化版）"""
        try:
            # 信頼度に基づく買い増し率（強化版）
            if confidence >= self.ultra_high_confidence_threshold:
                buy_more_ratio = min(
                    0.8, (confidence - 0.5) * 1.5
                )  # 超高信頼度で最大80%
            elif confidence >= self.high_confidence_threshold:
                buy_more_ratio = min(0.6, (confidence - 0.5) * 1.2)  # 高信頼度で最大60%
            else:
                buy_more_ratio = min(0.4, confidence - 0.5)  # 通常で最大40%

            # 現在のポジションサイズを考慮
            base_quantity = int(position.current_quantity * buy_more_ratio)

            # ボラティリティ調整
            volatility = self._calculate_volatility(position)
            volatility_adjustment = 1 - (volatility * self.volatility_adjustment_factor)
            adjusted_quantity = int(base_quantity * volatility_adjustment)

            # 最小単位（100株単位）
            return max(100, (adjusted_quantity // 100) * 100)

        except Exception as e:
            self.logger.error(f"買い増し数量計算エラー: {e}")
            return 0

    def _calculate_new_purchase_quantity(
        self, current_price: float, confidence: float, market_condition: str
    ) -> int:
        """新規購入数量の計算（強化版）"""
        try:
            # 基本購入金額（信頼度に基づく強化版）
            if confidence >= self.ultra_high_confidence_threshold:
                base_amount = 200000 * confidence  # 超高信頼度で20万円 × 信頼度
            elif confidence >= self.high_confidence_threshold:
                base_amount = 150000 * confidence  # 高信頼度で15万円 × 信頼度
            else:
                base_amount = 100000 * confidence  # 通常で10万円 × 信頼度

            # 市場条件による調整（強化版）
            market_multiplier = {
                "bull_market": 1.3,
                "sideways": 1.0,
                "bear_market": 0.7,
                "high_volatility": 0.8,
            }.get(market_condition, 1.0)

            adjusted_amount = base_amount * market_multiplier

            # リスク調整
            risk_adjustment = 1 - (self.risk_tolerance * 2)
            final_amount = adjusted_amount * risk_adjustment

            # 数量計算
            quantity = int(final_amount / current_price)

            # 最小単位（100株単位）
            return max(100, (quantity // 100) * 100)

        except Exception as e:
            self.logger.error(f"新規購入数量計算エラー: {e}")
            return 0

    def _find_position(
        self, symbol: str, positions: List[PositionInfo]
    ) -> Optional[PositionInfo]:
        """既存ポジションの検索"""
        for position in positions:
            if position.symbol == symbol:
                return position
        return None

    def _analyze_technical_indicators(self, market_data: Dict[str, Any]) -> List[str]:
        """技術指標の分析"""
        signals = []

        # RSI分析
        rsi = market_data.get("rsi", 50)
        if rsi < 30:
            signals.append("RSI過売り")
        elif rsi > 70:
            signals.append("RSI過買い")

        # MACD分析
        macd = market_data.get("macd", 0)
        if macd > 0:
            signals.append("MACD上昇")
        else:
            signals.append("MACD下降")

        # 移動平均分析
        sma_20 = market_data.get("sma_20", 0)
        current_price = market_data.get("close", 0)
        if current_price > sma_20:
            signals.append("価格 > SMA20")
        else:
            signals.append("価格 < SMA20")

        return signals

    def _analyze_fundamental_factors(self, market_data: Dict[str, Any]) -> List[str]:
        """ファンダメンタル要因の分析"""
        factors = []

        # 業績要因
        if market_data.get("revenue_growth", 0) > 0.1:
            factors.append("売上高成長")

        if market_data.get("profit_margin", 0) > 0.15:
            factors.append("高利益率")

        # バリュエーション要因
        pe_ratio = market_data.get("pe_ratio", 0)
        if pe_ratio > 0 and pe_ratio < 15:
            factors.append("割安バリュエーション")
        elif pe_ratio > 25:
            factors.append("高バリュエーション")

        return factors

    def _assess_market_condition(self, market_data: Dict[str, Any]) -> str:
        """市場条件の評価"""
        volatility = market_data.get("volatility", 0)
        trend = market_data.get("trend", 0)

        if volatility > 0.3:
            return "high_volatility"
        elif trend > 0.1:
            return "bull_market"
        elif trend < -0.1:
            return "bear_market"
        else:
            return "sideways"

    def _prioritize_actions(
        self, actions: List[InvestmentActionDetail]
    ) -> List[InvestmentActionDetail]:
        """アクションの優先度付け"""
        # 損切り > 利確 > 買い増し > 新規購入 の順
        priority_order = {
            InvestmentAction.STOP_LOSS: 1,
            InvestmentAction.TAKE_PROFIT: 2,
            InvestmentAction.BUY_MORE: 3,
            InvestmentAction.NEW_PURCHASE: 4,
        }

        return sorted(
            actions,
            key=lambda x: (
                priority_order.get(x.action, 5),
                -x.confidence,  # 信頼度の高い順
                -x.expected_return,  # 期待リターンの高い順
            ),
        )

    def _set_deadlines(
        self, actions: List[InvestmentActionDetail]
    ) -> List[InvestmentActionDetail]:
        """期限の設定"""
        for action in actions:
            if action.action == InvestmentAction.STOP_LOSS:
                action.deadline = datetime.now() + self.deadline_config["immediate"]
                action.deadline_type = DeadlineType.IMMEDIATE
            elif action.action == InvestmentAction.TAKE_PROFIT:
                action.deadline = datetime.now() + self.deadline_config["this_week"]
                action.deadline_type = DeadlineType.THIS_WEEK
            else:
                action.deadline = datetime.now() + self.deadline_config["this_week"]
                action.deadline_type = DeadlineType.THIS_WEEK

        return actions

    def get_action_summary(
        self, actions: List[InvestmentActionDetail]
    ) -> Dict[str, Any]:
        """アクションサマリーの生成"""
        summary = {
            "total_actions": len(actions),
            "action_counts": {},
            "total_amount": 0,
            "high_priority_count": 0,
            "immediate_actions": 0,
            "expected_return": 0,
            "max_risk": 0,
        }

        for action in actions:
            # アクション種別カウント
            action_type = action.action.value
            summary["action_counts"][action_type] = (
                summary["action_counts"].get(action_type, 0) + 1
            )

            # 合計金額
            summary["total_amount"] += action.total_amount

            # 高優先度カウント
            if action.priority == ActionPriority.HIGH:
                summary["high_priority_count"] += 1

            # 即座に実行が必要なアクション
            if action.deadline_type == DeadlineType.IMMEDIATE:
                summary["immediate_actions"] += 1

            # 期待リターンとリスク
            summary["expected_return"] += action.expected_return
            summary["max_risk"] = max(summary["max_risk"], abs(action.max_loss))

        return summary

    def _determine_quick_action(
        self,
        symbol: str,
        current_price: float,
        prediction: float,
        confidence: float,
        existing_position: Optional[PositionInfo],
        technical_signals: List[str],
        fundamental_factors: List[str],
        market_condition: str,
        price_change_ratio: float,
    ) -> Optional[InvestmentActionDetail]:
        """高信頼度での迅速判断"""
        try:
            # 超高信頼度での即座実行
            if confidence >= self.ultra_high_confidence_threshold:
                if existing_position:
                    # 既存ポジションの迅速処理
                    if price_change_ratio > 0.1:  # 10%以上の上昇予測
                        additional_quantity = self._calculate_buy_more_quantity(
                            current_price, confidence, existing_position
                        )
                        if additional_quantity > 0:
                            return InvestmentActionDetail(
                                action=InvestmentAction.BUY_MORE,
                                symbol=symbol,
                                current_price=current_price,
                                target_price=prediction,
                                quantity=additional_quantity,
                                total_amount=additional_quantity * current_price,
                                priority=ActionPriority.HIGH,
                                deadline=datetime.now()
                                + self.deadline_config["immediate"],
                                deadline_type=DeadlineType.IMMEDIATE,
                                confidence=confidence,
                                reason=f"超高信頼度買い増し: {price_change_ratio * 100:.1f}%上昇予測",
                                risk_level="MEDIUM",
                                expected_return=(prediction - current_price)
                                * additional_quantity,
                                max_loss=(current_price - prediction)
                                * additional_quantity,
                                technical_signals=technical_signals,
                                fundamental_factors=fundamental_factors,
                                market_condition=market_condition,
                            )
                else:
                    # 新規購入の迅速処理
                    if price_change_ratio > 0.08:  # 8%以上の上昇予測
                        quantity = self._calculate_new_purchase_quantity(
                            current_price, confidence, market_condition
                        )
                        if quantity > 0:
                            return InvestmentActionDetail(
                                action=InvestmentAction.NEW_PURCHASE,
                                symbol=symbol,
                                current_price=current_price,
                                target_price=prediction,
                                quantity=quantity,
                                total_amount=quantity * current_price,
                                priority=ActionPriority.HIGH,
                                deadline=datetime.now()
                                + self.deadline_config["immediate"],
                                deadline_type=DeadlineType.IMMEDIATE,
                                confidence=confidence,
                                reason=f"超高信頼度新規購入: {price_change_ratio * 100:.1f}%上昇予測",
                                risk_level="MEDIUM",
                                expected_return=(prediction - current_price) * quantity,
                                max_loss=(current_price - prediction) * quantity,
                                technical_signals=technical_signals,
                                fundamental_factors=fundamental_factors,
                                market_condition=market_condition,
                            )

            return None

        except Exception as e:
            self.logger.error(f"迅速判断エラー ({symbol}): {e}")
            return None

    def _calculate_volatility(self, position: PositionInfo) -> float:
        """ポジションのボラティリティ計算"""
        try:
            # 簡易的なボラティリティ計算
            if position.current_quantity > 0:
                price_volatility = (
                    abs(position.current_price - position.average_price)
                    / position.average_price
                )
                return min(1.0, price_volatility)
            return 0.0
        except Exception as e:
            self.logger.error(f"ボラティリティ計算エラー: {e}")
            return 0.0

    def get_action_urgency_score(self, action: InvestmentActionDetail) -> float:
        """アクションの緊急度スコア計算"""
        try:
            urgency_score = 0.0

            # 信頼度による重み付け
            urgency_score += action.confidence * 0.3

            # アクションタイプによる重み付け
            action_weights = {
                InvestmentAction.STOP_LOSS: 1.0,
                InvestmentAction.TAKE_PROFIT: 0.8,
                InvestmentAction.BUY_MORE: 0.6,
                InvestmentAction.NEW_PURCHASE: 0.4,
            }
            urgency_score += action_weights.get(action.action, 0.5) * 0.3

            # 期限による重み付け
            time_remaining = (action.deadline - datetime.now()).total_seconds()
            if time_remaining < 3600:  # 1時間以内
                urgency_score += 0.4
            elif time_remaining < 86400:  # 1日以内
                urgency_score += 0.2

            return min(1.0, urgency_score)

        except Exception as e:
            self.logger.error(f"緊急度スコア計算エラー: {e}")
            return 0.0

    def export_actions_to_json(
        self, actions: List[InvestmentActionDetail], filepath: str
    ) -> bool:
        """アクションをJSONファイルにエクスポート"""
        try:
            actions_data = []
            for action in actions:
                action_dict = {
                    "action": action.action.value,
                    "symbol": action.symbol,
                    "current_price": action.current_price,
                    "target_price": action.target_price,
                    "quantity": action.quantity,
                    "total_amount": action.total_amount,
                    "priority": action.priority.value,
                    "deadline": action.deadline.isoformat(),
                    "deadline_type": action.deadline_type.value,
                    "confidence": action.confidence,
                    "reason": action.reason,
                    "risk_level": action.risk_level,
                    "expected_return": action.expected_return,
                    "max_loss": action.max_loss,
                    "stop_loss_price": action.stop_loss_price,
                    "take_profit_price": action.take_profit_price,
                    "position_size_percentage": action.position_size_percentage,
                    "market_condition": action.market_condition,
                    "technical_signals": action.technical_signals,
                    "fundamental_factors": action.fundamental_factors,
                }
                actions_data.append(action_dict)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(actions_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"アクションを{filepath}にエクスポート")
            return True

        except Exception as e:
            self.logger.error(f"アクションエクスポートエラー: {e}")
            return False

    def _calculate_confidence(self, position: PositionInfo, market_data: Dict[str, Any]) -> float:
        """信頼度計算"""
        try:
            confidence = 0.5  # ベース信頼度
            
            # 市場トレンドによる調整
            trend = market_data.get("trend", "neutral")
            if trend == "bullish":
                confidence += 0.2
            elif trend == "bearish":
                confidence -= 0.2
            
            # ボラティリティによる調整
            volatility = market_data.get("volatility", 0.15)
            if volatility < 0.1:
                confidence += 0.1
            elif volatility > 0.3:
                confidence -= 0.1
            
            # 取引量による調整
            volume = market_data.get("volume", 0)
            if volume > 1000000:
                confidence += 0.1
            elif volume < 100000:
                confidence -= 0.1
            
            # RSIによる調整
            rsi = market_data.get("rsi", 50)
            if 30 <= rsi <= 70:
                confidence += 0.1
            elif rsi < 20 or rsi > 80:
                confidence -= 0.1
            
            # MACDによる調整
            macd = market_data.get("macd", "neutral")
            if macd == "bullish":
                confidence += 0.1
            elif macd == "bearish":
                confidence -= 0.1
            
            return max(0.0, min(1.0, confidence))
        except Exception as e:
            self.logger.error(f"信頼度計算エラー: {e}")
            return 0.5

    def _calculate_deadline(
        self, position: PositionInfo, market_data: Dict[str, Any], confidence: float, action: InvestmentAction
    ) -> Tuple[datetime, DeadlineType]:
        """期限計算"""
        try:
            if action == InvestmentAction.STOP_LOSS:
                return datetime.now() + timedelta(hours=1), DeadlineType.IMMEDIATE
            elif confidence >= 0.8:
                return datetime.now() + timedelta(days=7), DeadlineType.THIS_WEEK
            elif confidence >= 0.6:
                return datetime.now() + timedelta(days=30), DeadlineType.THIS_MONTH
            else:
                return datetime.now() + timedelta(days=90), DeadlineType.NEXT_QUARTER
        except Exception as e:
            self.logger.error(f"期限計算エラー: {e}")
            return datetime.now() + timedelta(days=7), DeadlineType.THIS_WEEK

    def _calculate_expected_return(
        self, position: PositionInfo, market_data: Dict[str, Any], action: InvestmentAction
    ) -> float:
        """期待リターン計算"""
        try:
            if action == InvestmentAction.BUY_MORE:
                return 0.15  # 15%の期待リターン
            elif action == InvestmentAction.TAKE_PROFIT:
                return 0.05  # 5%の期待リターン
            elif action == InvestmentAction.STOP_LOSS:
                return -0.10  # -10%の期待リターン
            else:
                return 0.0
        except Exception as e:
            self.logger.error(f"期待リターン計算エラー: {e}")
            return 0.0

    def _calculate_max_loss(
        self, position: PositionInfo, market_data: Dict[str, Any], action: InvestmentAction
    ) -> float:
        """最大損失計算"""
        try:
            if action == InvestmentAction.BUY_MORE:
                return -0.05  # -5%の最大損失
            elif action == InvestmentAction.TAKE_PROFIT:
                return -0.02  # -2%の最大損失
            elif action == InvestmentAction.STOP_LOSS:
                return -0.10  # -10%の最大損失
            else:
                return 0.0
        except Exception as e:
            self.logger.error(f"最大損失計算エラー: {e}")
            return 0.0

    def _calculate_target_price(
        self, position: PositionInfo, market_data: Dict[str, Any], action: InvestmentAction
    ) -> float:
        """目標価格計算"""
        try:
            if action == InvestmentAction.BUY_MORE:
                return position.current_price * 1.15  # 15%上昇
            elif action == InvestmentAction.TAKE_PROFIT:
                return position.current_price * 1.05  # 5%上昇
            elif action == InvestmentAction.STOP_LOSS:
                return position.current_price * 0.90  # 10%下落
            else:
                return position.current_price
        except Exception as e:
            self.logger.error(f"目標価格計算エラー: {e}")
            return position.current_price

    def _calculate_kelly_position_size(
        self, position: PositionInfo, market_data: Dict[str, Any], confidence: float
    ) -> float:
        """ケリー基準ポジションサイズ計算"""
        try:
            # ケリー基準の簡易版
            win_rate = confidence
            avg_win = 0.15  # 平均勝利
            avg_loss = 0.05  # 平均損失
            
            kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_fraction = max(0.0, min(0.25, kelly_fraction))  # 0-25%に制限
            
            return kelly_fraction * position.current_quantity
        except Exception as e:
            self.logger.error(f"ケリー基準ポジションサイズ計算エラー: {e}")
            return 0.0

    def _calculate_position_size(
        self, position: PositionInfo, market_data: Dict[str, Any], action: InvestmentAction, confidence: float
    ) -> float:
        """ポジションサイズ計算"""
        try:
            if action == InvestmentAction.BUY_MORE:
                return self._calculate_kelly_position_size(position, market_data, confidence)
            elif action == InvestmentAction.TAKE_PROFIT:
                return position.current_quantity * 0.5  # 50%決済
            elif action == InvestmentAction.STOP_LOSS:
                return position.current_quantity  # 全決済
            else:
                return 0.0
        except Exception as e:
            self.logger.error(f"ポジションサイズ計算エラー: {e}")
            return 0.0

    def _determine_priority(
        self, position: PositionInfo, market_data: Dict[str, Any], confidence: float, action: InvestmentAction
    ) -> ActionPriority:
        """優先度決定"""
        try:
            if action == InvestmentAction.STOP_LOSS:
                return ActionPriority.HIGH
            elif confidence >= 0.8:
                return ActionPriority.HIGH
            elif confidence >= 0.6:
                return ActionPriority.MEDIUM
            else:
                return ActionPriority.LOW
        except Exception as e:
            self.logger.error(f"優先度決定エラー: {e}")
            return ActionPriority.MEDIUM
