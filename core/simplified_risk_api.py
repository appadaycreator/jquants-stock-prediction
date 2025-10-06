#!/usr/bin/env python3
"""
簡素化されたリスク管理API
Webアプリケーション用の簡素化されたリスク管理エンドポイント
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from .simplified_risk_management import SimplifiedRiskManager, SimplifiedRiskLevel


class SimplifiedRiskAPI:
    """簡素化されたリスク管理API"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.risk_manager = SimplifiedRiskManager(config)

    def get_simplified_risk_assessment(
        self,
        stock_data: Dict[str, Any],
        current_price: float,
        position_size: float = 0.0,
        account_balance: float = 1000000.0,
    ) -> Dict[str, Any]:
        """簡素化されたリスク評価取得"""
        try:
            # データフレーム変換
            df = (
                pd.DataFrame(stock_data) if isinstance(stock_data, dict) else stock_data
            )

            # リスクメトリクス計算
            risk_metrics = self.risk_manager.calculate_simplified_risk_metrics(
                df, current_price, position_size, account_balance
            )

            return {
                "success": True,
                "data": {
                    "risk_level": risk_metrics.risk_level.value,
                    "risk_score": risk_metrics.risk_score,
                    "max_loss_amount": risk_metrics.max_loss_amount,
                    "volatility_level": risk_metrics.volatility_level,
                    "color_code": risk_metrics.color_code,
                    "recommendation": risk_metrics.recommendation,
                    "confidence": risk_metrics.confidence,
                    "display_text": self._get_display_text(risk_metrics),
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            self.logger.error(f"簡素化リスク評価取得エラー: {e}")
            return {"success": False, "error": str(e), "data": None}

    def get_portfolio_risk_balance(
        self,
        portfolio_data: Dict[str, Dict[str, Any]],
        account_balance: float = 1000000.0,
    ) -> Dict[str, Any]:
        """ポートフォリオリスクバランス取得"""
        try:
            # ポートフォリオリスクバランス計算
            balance = self.risk_manager.calculate_portfolio_risk_balance(
                portfolio_data, account_balance
            )

            return {
                "success": True,
                "data": {
                    "total_risk_score": balance.total_risk_score,
                    "risk_distribution": balance.risk_distribution,
                    "color_balance": balance.color_balance,
                    "overall_recommendation": balance.overall_recommendation,
                    "risk_counts": {
                        "low": balance.low_risk_count,
                        "medium": balance.medium_risk_count,
                        "high": balance.high_risk_count,
                    },
                    "risk_summary": self._get_risk_summary(balance),
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            self.logger.error(f"ポートフォリオリスクバランス取得エラー: {e}")
            return {"success": False, "error": str(e), "data": None}

    def get_risk_alerts(
        self, portfolio_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """リスクアラート取得"""
        try:
            alerts = self.risk_manager.get_risk_alerts(portfolio_data)

            # アラートの重要度別分類
            high_priority = [a for a in alerts if a.get("severity") == "HIGH"]
            medium_priority = [a for a in alerts if a.get("severity") == "MEDIUM"]
            low_priority = [a for a in alerts if a.get("severity") == "LOW"]

            return {
                "success": True,
                "data": {
                    "alerts": alerts,
                    "alert_counts": {
                        "high": len(high_priority),
                        "medium": len(medium_priority),
                        "low": len(low_priority),
                        "total": len(alerts),
                    },
                    "high_priority_alerts": high_priority,
                    "medium_priority_alerts": medium_priority,
                    "low_priority_alerts": low_priority,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            self.logger.error(f"リスクアラート取得エラー: {e}")
            return {"success": False, "error": str(e), "data": None}

    def get_visual_risk_display(
        self, portfolio_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """視覚的リスク表示データ取得"""
        try:
            display_data = self.risk_manager.get_visual_risk_display_data(
                portfolio_data
            )

            if not display_data:
                return {"success": False, "error": "表示データが取得できませんでした", "data": None}

            # 視覚化用のデータ加工
            visual_data = self._process_visual_data(display_data)

            return {"success": True, "data": visual_data}

        except Exception as e:
            self.logger.error(f"視覚的リスク表示データ取得エラー: {e}")
            return {"success": False, "error": str(e), "data": None}

    def get_risk_statistics(self) -> Dict[str, Any]:
        """リスク統計情報取得"""
        try:
            stats = self.risk_manager.get_risk_statistics()

            return {"success": True, "data": stats}

        except Exception as e:
            self.logger.error(f"リスク統計情報取得エラー: {e}")
            return {"success": False, "error": str(e), "data": None}

    def update_risk_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """リスク設定更新"""
        try:
            # 設定の検証
            if not self._validate_risk_settings(settings):
                return {"success": False, "error": "無効な設定です", "data": None}

            # 設定更新
            self.risk_manager.config.update(settings)

            return {
                "success": True,
                "data": {
                    "message": "リスク設定が更新されました",
                    "updated_settings": settings,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            self.logger.error(f"リスク設定更新エラー: {e}")
            return {"success": False, "error": str(e), "data": None}

    def export_risk_report(
        self, portfolio_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """リスクレポートエクスポート"""
        try:
            # ポートフォリオリスクバランス取得
            balance_response = self.get_portfolio_risk_balance(portfolio_data)
            if not balance_response["success"]:
                return balance_response

            # リスクアラート取得
            alerts_response = self.get_risk_alerts(portfolio_data)
            if not alerts_response["success"]:
                return alerts_response

            # レポート生成
            report = {
                "report_type": "simplified_risk_report",
                "generated_at": datetime.now().isoformat(),
                "portfolio_summary": balance_response["data"],
                "risk_alerts": alerts_response["data"],
                "recommendations": self._generate_recommendations(
                    balance_response["data"], alerts_response["data"]
                ),
            }

            return {"success": True, "data": report}

        except Exception as e:
            self.logger.error(f"リスクレポートエクスポートエラー: {e}")
            return {"success": False, "error": str(e), "data": None}

    # ヘルパーメソッド群
    def _get_display_text(self, risk_metrics) -> str:
        """表示テキスト生成"""
        risk_level_text = {
            SimplifiedRiskLevel.LOW: "低リスク",
            SimplifiedRiskLevel.MEDIUM: "中リスク",
            SimplifiedRiskLevel.HIGH: "高リスク",
        }

        volatility_text = {"low": "低", "medium": "中", "high": "高"}

        return (
            f"リスクレベル: {risk_level_text[risk_metrics.risk_level]} "
            f"(スコア: {risk_metrics.risk_score:.1f}) | "
            f"最大損失予想額: {risk_metrics.max_loss_amount:,.0f}円 | "
            f"ボラティリティ: {volatility_text[risk_metrics.volatility_level]} | "
            f"推奨: {risk_metrics.recommendation}"
        )

    def _get_risk_summary(self, balance) -> str:
        """リスクサマリー生成"""
        total_positions = (
            balance.low_risk_count + balance.medium_risk_count + balance.high_risk_count
        )

        if total_positions == 0:
            return "ポートフォリオが空です"

        high_risk_ratio = balance.high_risk_count / total_positions

        if high_risk_ratio > 0.5:
            return f"高リスク銘柄が{balance.high_risk_count}銘柄（{high_risk_ratio:.1%}）と多いため、リスク分散を推奨します"
        elif balance.total_risk_score > 60:
            return f"ポートフォリオ全体のリスクスコアが{balance.total_risk_score:.1f}と高いため、注意が必要です"
        elif (
            balance.low_risk_count > balance.medium_risk_count + balance.high_risk_count
        ):
            return f"低リスク銘柄が{balance.low_risk_count}銘柄と多く、安定したポートフォリオです"
        else:
            return "バランスの取れたポートフォリオです"

    def _process_visual_data(self, display_data: Dict[str, Any]) -> Dict[str, Any]:
        """視覚化データ加工"""
        try:
            # チャート用データ準備
            chart_data = {
                "risk_distribution_chart": {
                    "labels": ["低リスク", "中リスク", "高リスク"],
                    "data": [
                        display_data["portfolio_balance"]["risk_distribution"]["low"],
                        display_data["portfolio_balance"]["risk_distribution"][
                            "medium"
                        ],
                        display_data["portfolio_balance"]["risk_distribution"]["high"],
                    ],
                    "colors": ["#4CAF50", "#FF9800", "#F44336"],
                },
                "color_balance_chart": {
                    "labels": ["緑", "オレンジ", "赤"],
                    "data": [
                        display_data["portfolio_balance"]["color_balance"]["green"],
                        display_data["portfolio_balance"]["color_balance"]["orange"],
                        display_data["portfolio_balance"]["color_balance"]["red"],
                    ],
                    "colors": ["#4CAF50", "#FF9800", "#F44336"],
                },
            }

            # 銘柄別リスクデータ
            stock_risk_chart = []
            for stock in display_data["stock_risk_data"]:
                stock_risk_chart.append(
                    {
                        "symbol": stock["symbol"],
                        "risk_score": stock["risk_score"],
                        "max_loss_amount": stock["max_loss_amount"],
                        "color": stock["color_code"],
                        "recommendation": stock["recommendation"],
                    }
                )

            return {
                "portfolio_summary": display_data["portfolio_balance"],
                "stock_risk_data": display_data["stock_risk_data"],
                "risk_alerts": display_data["risk_alerts"],
                "chart_data": chart_data,
                "stock_risk_chart": stock_risk_chart,
                "display_timestamp": display_data["display_timestamp"],
            }

        except Exception as e:
            self.logger.error(f"視覚化データ加工エラー: {e}")
            return display_data

    def _validate_risk_settings(self, settings: Dict[str, Any]) -> bool:
        """リスク設定検証"""
        try:
            # 必須フィールドのチェック
            required_fields = [
                "risk_thresholds",
                "volatility_thresholds",
                "color_codes",
            ]
            for field in required_fields:
                if field not in settings:
                    return False

            # リスク閾値の検証
            risk_thresholds = settings.get("risk_thresholds", {})
            if not all(
                key in risk_thresholds
                for key in ["low_risk_max", "medium_risk_max", "high_risk_min"]
            ):
                return False

            # 値の範囲チェック
            if not (0 <= risk_thresholds.get("low_risk_max", 0) <= 100):
                return False
            if not (0 <= risk_thresholds.get("medium_risk_max", 0) <= 100):
                return False
            if not (0 <= risk_thresholds.get("high_risk_min", 0) <= 100):
                return False

            return True

        except Exception:
            return False

    def _generate_recommendations(
        self, balance_data: Dict[str, Any], alerts_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """推奨事項生成"""
        recommendations = []

        # 高リスクアラートに基づく推奨事項
        high_alerts = alerts_data.get("high_priority_alerts", [])
        if high_alerts:
            recommendations.append(
                {
                    "type": "HIGH_RISK_REDUCTION",
                    "priority": "HIGH",
                    "title": "高リスク銘柄の見直し",
                    "description": f"{len(high_alerts)}銘柄が高リスクのため、投資見直しを推奨します",
                    "action": "高リスク銘柄の売却またはポジションサイズの削減を検討してください",
                }
            )

        # ポートフォリオバランスに基づく推奨事項
        risk_distribution = balance_data.get("risk_distribution", {})
        high_risk_ratio = risk_distribution.get("high", 0)

        if high_risk_ratio > 0.3:  # 30%以上が高リスク
            recommendations.append(
                {
                    "type": "PORTFOLIO_DIVERSIFICATION",
                    "priority": "MEDIUM",
                    "title": "ポートフォリオの分散投資",
                    "description": "高リスク銘柄の割合が高いため、低リスク銘柄への分散投資を推奨します",
                    "action": "低リスク・中リスク銘柄の追加投資を検討してください",
                }
            )

        # ボラティリティに基づく推奨事項
        if balance_data.get("total_risk_score", 0) > 70:
            recommendations.append(
                {
                    "type": "RISK_MANAGEMENT",
                    "priority": "HIGH",
                    "title": "リスク管理の強化",
                    "description": "ポートフォリオ全体のリスクが高いため、リスク管理の強化が必要です",
                    "action": "損切りラインの設定、ポジションサイズの削減、現金比率の増加を検討してください",
                }
            )

        return recommendations
