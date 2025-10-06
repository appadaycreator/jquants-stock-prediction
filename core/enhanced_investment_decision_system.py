#!/usr/bin/env python3
"""
強化された投資判断システム
既存システムを統合し、明確な投資判断を提供
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import json

# 既存システムのインポート
from .clear_investment_actions import (
    ClearInvestmentActions,
    InvestmentActionDetail,
    PositionInfo,
)
from .advanced_quantity_calculator import (
    AdvancedQuantityCalculator,
    QuantityCalculationResult,
)
from .deadline_management import DeadlineManager, DeadlineInfo, AlertLevel
from .confidence_based_trading import ConfidenceBasedTrading
from .enhanced_confidence_system import EnhancedConfidenceSystem
from .ensemble_prediction_system import EnsemblePredictionSystem
from .enhanced_risk_management import EnhancedRiskManagement


@dataclass
class InvestmentDecisionResult:
    """投資判断結果"""

    symbol: str
    action: str
    quantity: int
    target_price: float
    current_price: float
    total_amount: float
    confidence: float
    priority: str
    deadline: datetime
    reason: str
    risk_level: str
    expected_return: float
    max_loss: float
    technical_signals: List[str]
    fundamental_factors: List[str]
    market_condition: str
    position_size_percentage: float
    commission: float
    slippage: float
    net_amount: float


class EnhancedInvestmentDecisionSystem:
    """強化された投資判断システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 各システムの初期化
        self.clear_actions = ClearInvestmentActions(config)
        self.quantity_calculator = AdvancedQuantityCalculator(config)
        self.deadline_manager = DeadlineManager(config)
        self.confidence_trading = ConfidenceBasedTrading(config)
        self.enhanced_confidence = EnhancedConfidenceSystem(config)
        self.ensemble_prediction = EnsemblePredictionSystem(config)
        self.risk_management = EnhancedRiskManagement(config)

        # 統合設定
        self.integration_enabled = self.config.get("integration_enabled", True)
        self.auto_optimization = self.config.get("auto_optimization", True)
        self.real_time_monitoring = self.config.get("real_time_monitoring", True)

        # パフォーマンス追跡
        self.decision_history = []
        self.performance_metrics = {}

        # アラートコールバックの設定
        self.deadline_manager.add_alert_callback(self._handle_deadline_alert)

    def generate_investment_decisions(
        self,
        market_data: List[Dict[str, Any]],
        positions: List[Dict[str, Any]] = None,
        predictions: List[float] = None,
        confidence_scores: List[float] = None,
    ) -> List[InvestmentDecisionResult]:
        """投資判断の生成"""
        try:
            self.logger.info("投資判断の生成を開始")

            # データの前処理
            processed_data = self._preprocess_market_data(market_data)
            position_info = self._convert_positions(positions or [])

            # 予測と信頼度の生成
            if predictions is None or confidence_scores is None:
                prediction_result = self._generate_predictions(processed_data)
                predictions = prediction_result.get("predictions", [])
                confidence_scores = prediction_result.get("confidence_scores", [])

            # 明確なアクションの生成
            clear_actions = self.clear_actions.generate_clear_actions(
                processed_data, position_info, predictions, confidence_scores
            )

            # 投資判断結果の生成
            decisions = []
            for action in clear_actions:
                decision = self._create_investment_decision(action, processed_data)
                if decision:
                    decisions.append(decision)

            # 期限管理の設定
            self._setup_deadline_management(decisions)

            # 履歴の記録
            self._record_decision_history(decisions)

            # パフォーマンス分析
            self._analyze_performance(decisions)

            self.logger.info(f"{len(decisions)}個の投資判断を生成")
            return decisions

        except Exception as e:
            self.logger.error(f"投資判断生成エラー: {e}")
            return []

    def _preprocess_market_data(
        self, market_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """市場データの前処理"""
        try:
            processed_data = []

            for data in market_data:
                processed_item = {
                    "symbol": data.get("symbol", ""),
                    "close": float(data.get("close", 0)),
                    "volume": float(data.get("volume", 0)),
                    "rsi": float(data.get("rsi", 50)),
                    "macd": float(data.get("macd", 0)),
                    "sma_20": float(data.get("sma_20", 0)),
                    "sma_50": float(data.get("sma_50", 0)),
                    "volatility": float(data.get("volatility", 0.2)),
                    "trend": float(data.get("trend", 0)),
                    "momentum": float(data.get("momentum", 0)),
                    "bollinger_upper": float(data.get("bollinger_upper", 0)),
                    "bollinger_lower": float(data.get("bollinger_lower", 0)),
                    "pe_ratio": float(data.get("pe_ratio", 0)),
                    "revenue_growth": float(data.get("revenue_growth", 0)),
                    "profit_margin": float(data.get("profit_margin", 0)),
                    "market_cap": float(data.get("market_cap", 0)),
                    "sector": data.get("sector", "unknown"),
                }
                processed_data.append(processed_item)

            return processed_data

        except Exception as e:
            self.logger.error(f"市場データ前処理エラー: {e}")
            return market_data

    def _convert_positions(self, positions: List[Dict[str, Any]]) -> List[PositionInfo]:
        """ポジション情報の変換"""
        try:
            position_info_list = []

            for pos in positions:
                position_info = PositionInfo(
                    symbol=pos.get("symbol", ""),
                    current_quantity=int(pos.get("quantity", 0)),
                    average_price=float(pos.get("average_price", 0)),
                    current_price=float(pos.get("current_price", 0)),
                    pnl=float(pos.get("pnl", 0)),
                    pnl_percentage=float(pos.get("pnl_percentage", 0)),
                    market_value=float(pos.get("market_value", 0)),
                    cost_basis=float(pos.get("cost_basis", 0)),
                )
                position_info_list.append(position_info)

            return position_info_list

        except Exception as e:
            self.logger.error(f"ポジション情報変換エラー: {e}")
            return []

    def _generate_predictions(
        self, market_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """予測の生成"""
        try:
            # アンサンブル予測の実行
            ensemble_result = self.ensemble_prediction.run_ensemble_prediction(
                market_data
            )

            if "error" in ensemble_result:
                self.logger.error(f"アンサンブル予測エラー: {ensemble_result['error']}")
                return {"predictions": [], "confidence_scores": []}

            predictions = ensemble_result.get("ensemble_prediction", [])
            confidence_scores = ensemble_result.get("confidence", [])

            return {"predictions": predictions, "confidence_scores": confidence_scores}

        except Exception as e:
            self.logger.error(f"予測生成エラー: {e}")
            return {"predictions": [], "confidence_scores": []}

    def _create_investment_decision(
        self, action: InvestmentActionDetail, market_data: List[Dict[str, Any]]
    ) -> Optional[InvestmentDecisionResult]:
        """投資判断結果の作成"""
        try:
            # 市場データの取得
            market_item = next(
                (item for item in market_data if item["symbol"] == action.symbol), {}
            )

            # 数量計算の実行
            quantity_result = self.quantity_calculator.calculate_optimal_quantity(
                symbol=action.symbol,
                current_price=action.current_price,
                target_price=action.target_price,
                confidence=action.confidence,
                volatility=market_item.get("volatility", 0.2),
                market_condition=action.market_condition,
            )

            # 投資判断結果の作成
            decision = InvestmentDecisionResult(
                symbol=action.symbol,
                action=action.action.value,
                quantity=quantity_result.quantity,
                target_price=action.target_price,
                current_price=action.current_price,
                total_amount=quantity_result.total_amount,
                confidence=action.confidence,
                priority=action.priority.value,
                deadline=action.deadline,
                reason=action.reason,
                risk_level=action.risk_level,
                expected_return=quantity_result.expected_return,
                max_loss=quantity_result.max_loss,
                technical_signals=action.technical_signals,
                fundamental_factors=action.fundamental_factors,
                market_condition=action.market_condition,
                position_size_percentage=quantity_result.position_size_percentage,
                commission=quantity_result.commission,
                slippage=quantity_result.slippage,
                net_amount=quantity_result.net_amount,
            )

            return decision

        except Exception as e:
            self.logger.error(f"投資判断結果作成エラー: {e}")
            return None

    def _setup_deadline_management(self, decisions: List[InvestmentDecisionResult]):
        """期限管理の設定"""
        try:
            for decision in decisions:
                # 期限の追加
                self.deadline_manager.add_deadline(
                    action_id=f"{decision.symbol}_{decision.action}_{int(datetime.now().timestamp())}",
                    symbol=decision.symbol,
                    action_type=decision.action,
                    deadline=decision.deadline,
                    deadline_type="this_week",
                    priority=decision.priority,
                    notes=decision.reason,
                )

            # 監視の開始
            if not self.deadline_manager.monitoring_active:
                self.deadline_manager.start_monitoring()

        except Exception as e:
            self.logger.error(f"期限管理設定エラー: {e}")

    def _handle_deadline_alert(self, alert):
        """期限アラートの処理"""
        try:
            self.logger.warning(f"期限アラート: {alert.message}")

            # アラートの処理ロジック
            if alert.level.value == "emergency":
                self._handle_emergency_alert(alert)
            elif alert.level.value == "critical":
                self._handle_critical_alert(alert)
            elif alert.level.value == "warning":
                self._handle_warning_alert(alert)

        except Exception as e:
            self.logger.error(f"期限アラート処理エラー: {e}")

    def _handle_emergency_alert(self, alert):
        """緊急アラートの処理"""
        self.logger.critical(f"緊急アラート処理: {alert.message}")
        # 緊急時の処理ロジックを実装

    def _handle_critical_alert(self, alert):
        """重要アラートの処理"""
        self.logger.warning(f"重要アラート処理: {alert.message}")
        # 重要時の処理ロジックを実装

    def _handle_warning_alert(self, alert):
        """警告アラートの処理"""
        self.logger.info(f"警告アラート処理: {alert.message}")
        # 警告時の処理ロジックを実装

    def _record_decision_history(self, decisions: List[InvestmentDecisionResult]):
        """判断履歴の記録"""
        try:
            for decision in decisions:
                history_item = {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": decision.symbol,
                    "action": decision.action,
                    "quantity": decision.quantity,
                    "target_price": decision.target_price,
                    "confidence": decision.confidence,
                    "priority": decision.priority,
                    "reason": decision.reason,
                }
                self.decision_history.append(history_item)

            # 履歴の保存（必要に応じて）
            if len(self.decision_history) > 1000:  # 履歴が多すぎる場合は古いものを削除
                self.decision_history = self.decision_history[-500:]

        except Exception as e:
            self.logger.error(f"判断履歴記録エラー: {e}")

    def _analyze_performance(self, decisions: List[InvestmentDecisionResult]):
        """パフォーマンス分析"""
        try:
            if not decisions:
                return

            # 基本統計
            total_amount = sum(d.total_amount for d in decisions)
            avg_confidence = np.mean([d.confidence for d in decisions])
            high_priority_count = sum(1 for d in decisions if d.priority == "high")

            # アクション種別の集計
            action_counts = {}
            for decision in decisions:
                action = decision.action
                action_counts[action] = action_counts.get(action, 0) + 1

            # リスク分析
            total_risk = sum(d.max_loss for d in decisions)
            avg_expected_return = np.mean([d.expected_return for d in decisions])

            self.performance_metrics = {
                "total_decisions": len(decisions),
                "total_amount": total_amount,
                "avg_confidence": avg_confidence,
                "high_priority_count": high_priority_count,
                "action_counts": action_counts,
                "total_risk": total_risk,
                "avg_expected_return": avg_expected_return,
                "risk_return_ratio": total_risk / abs(avg_expected_return)
                if avg_expected_return != 0
                else 0,
            }

        except Exception as e:
            self.logger.error(f"パフォーマンス分析エラー: {e}")

    def get_decision_summary(self) -> Dict[str, Any]:
        """判断サマリーの取得"""
        try:
            # 期限管理サマリー
            deadline_summary = self.deadline_manager.get_deadline_summary()

            # パフォーマンスメトリクス
            performance_summary = self.performance_metrics

            # 統合サマリー
            summary = {
                "system_status": {
                    "integration_enabled": self.integration_enabled,
                    "auto_optimization": self.auto_optimization,
                    "real_time_monitoring": self.real_time_monitoring,
                    "monitoring_active": self.deadline_manager.monitoring_active,
                },
                "deadline_management": deadline_summary,
                "performance_metrics": performance_summary,
                "decision_history_count": len(self.decision_history),
                "last_updated": datetime.now().isoformat(),
            }

            return summary

        except Exception as e:
            self.logger.error(f"判断サマリー取得エラー: {e}")
            return {}

    def export_decisions_to_json(
        self, decisions: List[InvestmentDecisionResult], filepath: str
    ) -> bool:
        """投資判断のJSONエクスポート"""
        try:
            export_data = {
                "decisions": [],
                "summary": self.get_decision_summary(),
                "exported_at": datetime.now().isoformat(),
            }

            for decision in decisions:
                decision_dict = {
                    "symbol": decision.symbol,
                    "action": decision.action,
                    "quantity": decision.quantity,
                    "target_price": decision.target_price,
                    "current_price": decision.current_price,
                    "total_amount": decision.total_amount,
                    "confidence": decision.confidence,
                    "priority": decision.priority,
                    "deadline": decision.deadline.isoformat(),
                    "reason": decision.reason,
                    "risk_level": decision.risk_level,
                    "expected_return": decision.expected_return,
                    "max_loss": decision.max_loss,
                    "technical_signals": decision.technical_signals,
                    "fundamental_factors": decision.fundamental_factors,
                    "market_condition": decision.market_condition,
                    "position_size_percentage": decision.position_size_percentage,
                    "commission": decision.commission,
                    "slippage": decision.slippage,
                    "net_amount": decision.net_amount,
                }
                export_data["decisions"].append(decision_dict)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"投資判断を{filepath}にエクスポート")
            return True

        except Exception as e:
            self.logger.error(f"投資判断エクスポートエラー: {e}")
            return False

    def cleanup_system(self):
        """システムのクリーンアップ"""
        try:
            # 期限監視の停止
            self.deadline_manager.stop_monitoring()

            # 期限切れデータのクリーンアップ
            self.deadline_manager.cleanup_expired_data()

            # 履歴のクリーンアップ
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-500:]

            self.logger.info("システムクリーンアップ完了")

        except Exception as e:
            self.logger.error(f"システムクリーンアップエラー: {e}")
