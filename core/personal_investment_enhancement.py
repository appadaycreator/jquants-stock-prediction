#!/usr/bin/env python3
"""
個人投資用統合システム
記事の手法を超える高度な個人投資システムを実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging

# 実装したモジュールのインポート
from .confidence_based_trading import ConfidenceBasedTrading
from .enhanced_risk_management import EnhancedRiskManagement
from .article_inspired_backtest import ArticleInspiredBacktest
from .advanced_position_sizing import AdvancedPositionSizing
from .ensemble_prediction_system import EnsemblePredictionSystem


class PersonalInvestmentEnhancement:
    """個人投資用統合システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 各システムの初期化
        self.confidence_trading = ConfidenceBasedTrading(config)
        self.risk_management = EnhancedRiskManagement(config)
        self.backtest_system = ArticleInspiredBacktest(config)
        self.position_sizing = AdvancedPositionSizing(config)
        self.ensemble_prediction = EnsemblePredictionSystem(config)

        # 統合設定
        self.integration_enabled = self.config.get("integration_enabled", True)
        self.auto_optimization = self.config.get("auto_optimization", True)

        # パフォーマンス追跡
        self.performance_history = []
        self.trade_history = []

    def run_comprehensive_analysis(
        self, market_data: List[Dict[str, Any]], predictions: List[float] = None
    ) -> Dict[str, Any]:
        """
        包括的な分析の実行
        記事の手法を超える高度な分析
        """
        try:
            self.logger.info("包括的な分析を開始")

            # 1. アンサンブル予測の実行
            if predictions is None:
                ensemble_result = self._run_ensemble_prediction(market_data)
                if "error" in ensemble_result:
                    return ensemble_result
                predictions = ensemble_result["ensemble_prediction"]
                confidence_scores = ensemble_result["confidence"]
            else:
                confidence_scores = [0.7] * len(predictions)  # デフォルト信頼度

            # 2. 信頼度ベースの取引判定
            trading_decisions = self._run_confidence_based_trading(
                predictions, market_data, confidence_scores
            )

            # 3. ポジションサイジングの計算
            position_sizing = self._run_position_sizing(market_data, confidence_scores)

            # 4. リスク管理の適用
            risk_management = self._run_risk_management(market_data, trading_decisions)

            # 5. バックテストの実行
            backtest_result = self._run_backtest_comparison(
                predictions, market_data, confidence_scores
            )

            # 6. 統合結果の生成
            comprehensive_result = self._generate_comprehensive_result(
                ensemble_result,
                trading_decisions,
                position_sizing,
                risk_management,
                backtest_result,
            )

            return comprehensive_result

        except Exception as e:
            self.logger.error(f"包括的分析エラー: {e}")
            return {"error": str(e)}

    def _run_ensemble_prediction(
        self, market_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """アンサンブル予測の実行"""
        try:
            # 市場データの前処理
            X = self._prepare_market_data(market_data)

            # アンサンブル予測の実行
            ensemble_result = self.ensemble_prediction.predict_ensemble(X)

            return ensemble_result

        except Exception as e:
            self.logger.error(f"アンサンブル予測エラー: {e}")
            return {"error": str(e)}

    def _run_confidence_based_trading(
        self,
        predictions: List[float],
        market_data: List[Dict[str, Any]],
        confidence_scores: List[float],
    ) -> List[Dict[str, Any]]:
        """信頼度ベースの取引判定の実行"""
        try:
            trading_decisions = []

            for i, (prediction, market_info, confidence) in enumerate(
                zip(predictions, market_data, confidence_scores)
            ):
                # 取引判定の実行
                decision = self.confidence_trading.should_trade(prediction, market_info)

                # 取引の実行
                if decision["should_trade"]:
                    trade_result = self.confidence_trading.execute_trade(
                        decision, market_info
                    )
                    trading_decisions.append(trade_result)

            return trading_decisions

        except Exception as e:
            self.logger.error(f"信頼度ベース取引エラー: {e}")
            return []

    def _run_position_sizing(
        self, market_data: List[Dict[str, Any]], confidence_scores: List[float]
    ) -> Dict[str, Any]:
        """ポジションサイジングの実行"""
        try:
            # アカウント残高の取得
            account_balance = self.config.get("account_balance", 100000)

            # 株式データの準備
            stock_data = []
            for i, (market_info, confidence) in enumerate(
                zip(market_data, confidence_scores)
            ):
                stock_data.append(
                    {
                        "symbol": f"STOCK_{i}",
                        "price": market_info.get("current_price", 100),
                        "confidence": confidence,
                        "volatility": market_info.get("volatility", 0.02),
                        "correlation": market_info.get("correlation", 0.0),
                        "risk_level": market_info.get("risk_level", "MEDIUM"),
                    }
                )

            # ポジションサイジングの計算
            position_result = self.position_sizing.calculate_portfolio_position_sizes(
                account_balance, stock_data
            )

            return position_result

        except Exception as e:
            self.logger.error(f"ポジションサイジングエラー: {e}")
            return {"error": str(e)}

    def _run_risk_management(
        self, market_data: List[Dict[str, Any]], trading_decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """リスク管理の実行"""
        try:
            risk_summary = self.risk_management.get_risk_summary()

            # 各取引に対するリスク管理の適用
            risk_managed_trades = []
            for trade in trading_decisions:
                if trade.get("executed", False):
                    # ポジションの作成
                    position = self.risk_management.create_position(
                        symbol=trade.get("symbol", "UNKNOWN"),
                        direction=trade.get("direction", "BUY"),
                        entry_price=trade.get("entry_price", 0),
                        position_size=trade.get("position_size", 0),
                        confidence=trade.get("confidence", 0.7),
                        volatility=trade.get("volatility", 0.02),
                    )

                    risk_managed_trades.append(position)

            return {
                "risk_summary": risk_summary,
                "risk_managed_trades": risk_managed_trades,
                "total_positions": len(risk_managed_trades),
            }

        except Exception as e:
            self.logger.error(f"リスク管理エラー: {e}")
            return {"error": str(e)}

    def _run_backtest_comparison(
        self,
        predictions: List[float],
        market_data: List[Dict[str, Any]],
        confidence_scores: List[float],
    ) -> Dict[str, Any]:
        """バックテスト比較の実行"""
        try:
            # 価格データの準備
            prices = []
            for market_info in market_data:
                prices.append(
                    {
                        "open": market_info.get("open", 100),
                        "high": market_info.get("high", 105),
                        "low": market_info.get("low", 95),
                        "close": market_info.get("close", 102),
                        "volume": market_info.get("volume", 1000),
                    }
                )

            # バックテスト比較の実行
            comparison_result = self.backtest_system.compare_methods(
                predictions, prices, confidence_scores
            )

            return comparison_result

        except Exception as e:
            self.logger.error(f"バックテスト比較エラー: {e}")
            return {"error": str(e)}

    def _prepare_market_data(self, market_data: List[Dict[str, Any]]) -> np.ndarray:
        """市場データの前処理"""
        try:
            # 特徴量の抽出
            features = []
            for data in market_data:
                feature_vector = [
                    data.get("open", 0),
                    data.get("high", 0),
                    data.get("low", 0),
                    data.get("close", 0),
                    data.get("volume", 0),
                    data.get("volatility", 0),
                    data.get("rsi", 50),
                    data.get("macd", 0),
                    data.get("sma_20", 0),
                    data.get("sma_50", 0),
                ]
                features.append(feature_vector)

            return np.array(features)

        except Exception as e:
            self.logger.error(f"市場データ前処理エラー: {e}")
            return np.array([])

    def _generate_comprehensive_result(
        self,
        ensemble_result: Dict[str, Any],
        trading_decisions: List[Dict[str, Any]],
        position_sizing: Dict[str, Any],
        risk_management: Dict[str, Any],
        backtest_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """統合結果の生成"""
        try:
            # パフォーマンス指標の計算
            performance_metrics = self._calculate_performance_metrics(
                trading_decisions, position_sizing, risk_management
            )

            # 推奨事項の生成
            recommendations = self._generate_recommendations(
                ensemble_result, trading_decisions, position_sizing, risk_management
            )

            # 統合結果の生成
            comprehensive_result = {
                "timestamp": datetime.now().isoformat(),
                "ensemble_prediction": ensemble_result,
                "trading_decisions": trading_decisions,
                "position_sizing": position_sizing,
                "risk_management": risk_management,
                "backtest_comparison": backtest_result,
                "performance_metrics": performance_metrics,
                "recommendations": recommendations,
                "summary": self._generate_summary(performance_metrics, recommendations),
            }

            # 履歴の保存
            self.performance_history.append(comprehensive_result)

            return comprehensive_result

        except Exception as e:
            self.logger.error(f"統合結果生成エラー: {e}")
            return {"error": str(e)}

    def _calculate_performance_metrics(
        self,
        trading_decisions: List[Dict[str, Any]],
        position_sizing: Dict[str, Any],
        risk_management: Dict[str, Any],
    ) -> Dict[str, Any]:
        """パフォーマンス指標の計算"""
        try:
            # 基本指標
            total_trades = len(trading_decisions)
            executed_trades = len(
                [t for t in trading_decisions if t.get("executed", False)]
            )

            # 信頼度統計
            confidences = [
                t.get("confidence", 0)
                for t in trading_decisions
                if t.get("executed", False)
            ]
            avg_confidence = np.mean(confidences) if confidences else 0

            # リスク指標
            risk_summary = risk_management.get("risk_summary", {})

            # ポジション指標
            position_info = position_sizing.get("positions", {})
            total_position_value = position_sizing.get("total_position_value", 0)

            return {
                "total_trades": total_trades,
                "executed_trades": executed_trades,
                "execution_rate": executed_trades / total_trades
                if total_trades > 0
                else 0,
                "avg_confidence": avg_confidence,
                "total_position_value": total_position_value,
                "risk_metrics": risk_summary,
                "position_count": len(position_info),
            }

        except Exception as e:
            self.logger.error(f"パフォーマンス指標計算エラー: {e}")
            return {"error": str(e)}

    def _generate_recommendations(
        self,
        ensemble_result: Dict[str, Any],
        trading_decisions: List[Dict[str, Any]],
        position_sizing: Dict[str, Any],
        risk_management: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """推奨事項の生成"""
        try:
            recommendations = []

            # 信頼度に関する推奨事項
            confidence = ensemble_result.get("confidence", 0)
            if confidence < 0.6:
                recommendations.append(
                    {
                        "type": "LOW_CONFIDENCE",
                        "priority": "HIGH",
                        "message": "予測の信頼度が低いため、取引を控えることを推奨します",
                        "confidence": confidence,
                    }
                )

            # リスク管理に関する推奨事項
            risk_summary = risk_management.get("risk_summary", {})
            if risk_summary.get("high_risk_positions", 0) > 0:
                recommendations.append(
                    {
                        "type": "HIGH_RISK_POSITIONS",
                        "priority": "MEDIUM",
                        "message": "高リスクポジションが検出されました。リスク管理を強化してください",
                        "high_risk_count": risk_summary.get("high_risk_positions", 0),
                    }
                )

            # ポジションサイジングに関する推奨事項
            portfolio_percent = position_sizing.get("portfolio_percent", 0)
            if portfolio_percent > 80:
                recommendations.append(
                    {
                        "type": "HIGH_POSITION_PERCENT",
                        "priority": "MEDIUM",
                        "message": "ポジション比率が高いため、リスクを考慮してください",
                        "portfolio_percent": portfolio_percent,
                    }
                )

            return recommendations

        except Exception as e:
            self.logger.error(f"推奨事項生成エラー: {e}")
            return []

    def _generate_summary(
        self, performance_metrics: Dict[str, Any], recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """サマリーの生成"""
        try:
            # 基本サマリー
            summary = {
                "total_trades": performance_metrics.get("total_trades", 0),
                "execution_rate": performance_metrics.get("execution_rate", 0),
                "avg_confidence": performance_metrics.get("avg_confidence", 0),
                "recommendation_count": len(recommendations),
                "high_priority_recommendations": len(
                    [r for r in recommendations if r.get("priority") == "HIGH"]
                ),
            }

            # 総合評価
            if summary["avg_confidence"] > 0.8 and summary["execution_rate"] > 0.7:
                summary["overall_rating"] = "EXCELLENT"
            elif summary["avg_confidence"] > 0.6 and summary["execution_rate"] > 0.5:
                summary["overall_rating"] = "GOOD"
            elif summary["avg_confidence"] > 0.4:
                summary["overall_rating"] = "FAIR"
            else:
                summary["overall_rating"] = "POOR"

            return summary

        except Exception as e:
            self.logger.error(f"サマリー生成エラー: {e}")
            return {"error": str(e)}

    def get_performance_history(self) -> List[Dict[str, Any]]:
        """パフォーマンス履歴の取得"""
        return self.performance_history

    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスの取得"""
        try:
            return {
                "confidence_trading": self.confidence_trading.get_performance_metrics(),
                "risk_management": self.risk_management.get_risk_summary(),
                "position_sizing": self.position_sizing.get_position_sizing_recommendations(
                    self.config.get("account_balance", 100000), []
                ),
                "ensemble_prediction": self.ensemble_prediction.get_model_importance(),
                "system_health": "HEALTHY" if self.integration_enabled else "DEGRADED",
            }

        except Exception as e:
            self.logger.error(f"システムステータス取得エラー: {e}")
            return {"error": str(e)}
