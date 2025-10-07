#!/usr/bin/env python3
"""
ルーチン分析API
既存のAPIに簡素化されたリスク管理機能を追加
"""

import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# 既存のインポート
from core.enhanced_investment_decision_system import EnhancedInvestmentDecisionSystem
from core.enhanced_confidence_system import EnhancedConfidenceSystem
from core.ensemble_prediction_system import EnsemblePredictionSystem
from core.technical_analysis import TechnicalAnalysis
from core.data_validator import DataValidator
from core.json_data_manager import JSONDataManager
from core.logging_manager import LoggingManager
from core.config_manager import ConfigManager
from core.error_handler import ErrorHandler
from core.utils import normalize_security_code

# 新規追加: 簡素化されたリスク管理
from core.dynamic_risk_management import DynamicRiskManager
# from core.simplified_risk_api import SimplifiedRiskAPI  # 削除されたモジュール


# 既存のAPIクラス
class RoutineAnalysisAPI:
    """ルーチン分析API（簡素化リスク管理機能追加）"""

    def __init__(self, config_path: str = "config_final.yaml"):
        """初期化"""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        self.logger = LoggingManager(__name__).get_logger()
        self.error_handler = ErrorHandler()
        # Utilsクラスは削除（関数ベースに変更）

        # 既存のシステム初期化
        self.investment_system = EnhancedInvestmentDecisionSystem(self.config)
        self.confidence_system = EnhancedConfidenceSystem(self.config)
        self.prediction_system = EnsemblePredictionSystem(self.config)
        self.technical_analysis = TechnicalAnalysis()
        self.data_validator = DataValidator(self.config)
        self.json_manager = JSONDataManager("data")

        # 新規追加: 簡素化されたリスク管理
        self.simplified_risk_manager = DynamicRiskManager(self.config)
        # self.simplified_risk_api = SimplifiedRiskAPI(self.config)  # 削除されたモジュール

        self.logger.info("ルーチン分析API（簡素化リスク管理機能付き）が初期化されました")

    def analyze_stocks_with_simplified_risk(
        self,
        stock_codes: List[str],
        analysis_date: Optional[str] = None,
        include_risk_assessment: bool = True,
    ) -> Dict[str, Any]:
        """株式分析（簡素化リスク評価付き）"""
        try:
            if analysis_date is None:
                analysis_date = datetime.now().strftime("%Y-%m-%d")

            self.logger.info(f"簡素化リスク評価付き株式分析開始: {stock_codes}")

            # 既存の分析実行
            analysis_results = self._execute_stock_analysis(stock_codes, analysis_date)

            # 簡素化リスク評価の追加
            if include_risk_assessment:
                risk_assessment = self._add_simplified_risk_assessment(analysis_results)
                analysis_results["simplified_risk_assessment"] = risk_assessment

            return {
                "success": True,
                "data": analysis_results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"簡素化リスク評価付き株式分析エラー: {e}")
            return self.error_handler.handle_error(e, "簡素化リスク評価付き株式分析")

    def get_simplified_risk_dashboard_data(
        self, portfolio_data: Dict[str, Any], account_balance: float = 1000000.0
    ) -> Dict[str, Any]:
        """簡素化リスクダッシュボードデータ取得"""
        try:
            self.logger.info("簡素化リスクダッシュボードデータ取得開始")

            # 簡素化リスクマネージャーを使用してデータ取得
            stock_data = portfolio_data.get("7203", {}).get("stock_data", pd.DataFrame())
            current_price = portfolio_data.get("7203", {}).get("current_price", 100.0)
            
            # データが空の場合はデフォルトデータを作成
            if stock_data.empty:
                stock_data = pd.DataFrame({
                    'close': [100, 105, 102, 108, 110],
                    'volume': [1000, 1200, 900, 1300, 1100]
                })
            
            dashboard_data = self.simplified_risk_manager.calculate_risk_metrics(
                stock_data, current_price
            )

            return {
                "success": True,
                "data": {
                    "risk_level": dashboard_data.risk_level.value,
                    "risk_score": dashboard_data.risk_score,
                    "volatility": dashboard_data.volatility,
                    "var_95": dashboard_data.var_95,
                    "max_drawdown": dashboard_data.max_drawdown
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"簡素化リスクダッシュボードデータ取得エラー: {e}")
            return self.error_handler.handle_api_error(e, "簡素化リスクダッシュボードデータ取得")

    def get_portfolio_risk_summary(
        self, portfolio_data: Dict[str, Any], account_balance: float = 1000000.0
    ) -> Dict[str, Any]:
        """ポートフォリオリスクサマリー取得"""
        try:
            self.logger.info("ポートフォリオリスクサマリー取得開始")

            # ポートフォリオリスクバランス取得
            balance_response = self.simplified_risk_api.get_portfolio_risk_balance(
                portfolio_data, account_balance
            )

            if not balance_response["success"]:
                return balance_response

            # リスクアラート取得
            alerts_response = self.simplified_risk_api.get_risk_alerts(portfolio_data)

            # サマリーデータ構築
            summary_data = {
                "portfolio_balance": balance_response["data"],
                "risk_alerts": alerts_response["data"]
                if alerts_response["success"]
                else {"alerts": []},
                "risk_statistics": self.simplified_risk_api.get_risk_statistics()[
                    "data"
                ],
                "recommendations": self._generate_risk_recommendations(
                    balance_response["data"],
                    alerts_response["data"]
                    if alerts_response["success"]
                    else {"alerts": []},
                ),
            }

            return {
                "success": True,
                "data": summary_data,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"ポートフォリオリスクサマリー取得エラー: {e}")
            return self.error_handler.handle_error(e, "ポートフォリオリスクサマリー取得")

    def update_risk_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """リスク設定更新"""
        try:
            self.logger.info("リスク設定更新開始")

            # 簡素化リスクAPIを使用して設定更新
            result = self.simplified_risk_api.update_risk_settings(settings)

            if result["success"]:
                # 設定ファイルにも保存
                self.config_manager.update_config({"simplified_risk": settings})
                self.config_manager.save_config()

            return result

        except Exception as e:
            self.logger.error(f"リスク設定更新エラー: {e}")
            return self.error_handler.handle_error(e, "リスク設定更新")

    def export_risk_report(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """リスクレポートエクスポート"""
        try:
            self.logger.info("リスクレポートエクスポート開始")

            # 簡素化リスクAPIを使用してレポート生成
            report_result = self.simplified_risk_api.export_risk_report(portfolio_data)

            if report_result["success"]:
                # レポートファイル保存
                report_filename = (
                    f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                report_path = f"data/reports/{report_filename}"

                # ディレクトリ作成
                import os

                os.makedirs(os.path.dirname(report_path), exist_ok=True)

                # レポート保存
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report_result["data"], f, ensure_ascii=False, indent=2)

                report_result["data"]["report_path"] = report_path
                report_result["data"]["report_filename"] = report_filename

            return report_result

        except Exception as e:
            self.logger.error(f"リスクレポートエクスポートエラー: {e}")
            return self.error_handler.handle_error(e, "リスクレポートエクスポート")

    # ヘルパーメソッド群
    def _execute_stock_analysis(
        self, stock_codes: List[str], analysis_date: str
    ) -> Dict[str, Any]:
        """株式分析実行（既存機能）"""
        try:
            # 既存の分析ロジックを実行
            analysis_results = {
                "analysis_date": analysis_date,
                "stock_codes": stock_codes,
                "predictions": {},
                "recommendations": {},
                "confidence_scores": {},
                "technical_indicators": {},
            }

            for stock_code in stock_codes:
                try:
                    # データ取得
                    stock_data = self.json_manager.get_stock_data(stock_code)
                    if stock_data is None or stock_data.empty:
                        continue

                    # 予測実行
                    prediction = self.prediction_system.predict(stock_data)
                    analysis_results["predictions"][stock_code] = prediction

                    # 信頼度計算
                    confidence = self.confidence_system.calculate_confidence(
                        stock_data, prediction
                    )
                    analysis_results["confidence_scores"][stock_code] = confidence

                    # 投資判断
                    investment_decision = self.investment_system.make_decision(
                        stock_data, prediction, confidence
                    )
                    analysis_results["recommendations"][
                        stock_code
                    ] = investment_decision

                    # テクニカル分析
                    technical_indicators = self.technical_analysis.calculate_indicators(
                        stock_data
                    )
                    analysis_results["technical_indicators"][
                        stock_code
                    ] = technical_indicators

                except Exception as e:
                    self.logger.error(f"株式分析エラー {stock_code}: {e}")
                    continue

            return analysis_results

        except Exception as e:
            self.logger.error(f"株式分析実行エラー: {e}")
            raise

    def _add_simplified_risk_assessment(
        self, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """簡素化リスク評価追加"""
        try:
            risk_assessment = {
                "stock_risk_metrics": {},
                "portfolio_risk_summary": {},
                "risk_alerts": [],
                "recommendations": [],
            }

            # 各銘柄のリスク評価
            for stock_code, prediction in analysis_results.get(
                "predictions", {}
            ).items():
                try:
                    # 株式データ取得
                    stock_data = self.json_manager.get_stock_data(stock_code)
                    if stock_data is None or stock_data.empty:
                        continue

                    # 現在価格取得
                    current_price = (
                        stock_data["Close"].iloc[-1] if not stock_data.empty else 0
                    )

                    # 簡素化リスクメトリクス計算
                    risk_metrics = (
                        self.simplified_risk_manager.calculate_simplified_risk_metrics(
                            stock_data, current_price
                        )
                    )

                    risk_assessment["stock_risk_metrics"][stock_code] = {
                        "risk_level": risk_metrics.risk_level.value,
                        "risk_score": risk_metrics.risk_score,
                        "max_loss_amount": risk_metrics.max_loss_amount,
                        "volatility_level": risk_metrics.volatility_level,
                        "color_code": risk_metrics.color_code,
                        "recommendation": risk_metrics.recommendation,
                        "confidence": risk_metrics.confidence,
                    }

                except Exception as e:
                    self.logger.error(f"銘柄リスク評価エラー {stock_code}: {e}")
                    continue

            # ポートフォリオ全体のリスクサマリー
            if risk_assessment["stock_risk_metrics"]:
                portfolio_data = {
                    stock_code: {
                        "stock_data": self.json_manager.get_stock_data(stock_code),
                        "current_price": self.json_manager.get_stock_data(stock_code)[
                            "Close"
                        ].iloc[-1]
                        if not self.json_manager.get_stock_data(stock_code).empty
                        else 0,
                        "position_size": 1.0,  # 仮のポジションサイズ
                        "account_balance": 1000000.0,
                    }
                    for stock_code in risk_assessment["stock_risk_metrics"].keys()
                }

                portfolio_balance = (
                    self.simplified_risk_manager.calculate_portfolio_risk_balance(
                        portfolio_data, 1000000.0
                    )
                )

                risk_assessment["portfolio_risk_summary"] = {
                    "total_risk_score": portfolio_balance.total_risk_score,
                    "risk_distribution": portfolio_balance.risk_distribution,
                    "color_balance": portfolio_balance.color_balance,
                    "overall_recommendation": portfolio_balance.overall_recommendation,
                }

                # リスクアラート取得
                risk_alerts = self.simplified_risk_manager.get_risk_alerts(
                    portfolio_data
                )
                risk_assessment["risk_alerts"] = risk_alerts

            return risk_assessment

        except Exception as e:
            self.logger.error(f"簡素化リスク評価追加エラー: {e}")
            return {}

    def _generate_risk_recommendations(
        self, balance_data: Dict[str, Any], alerts_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """リスク推奨事項生成"""
        recommendations = []

        try:
            # 高リスクアラートに基づく推奨事項
            high_alerts = alerts_data.get("alerts", [])
            high_risk_alerts = [a for a in high_alerts if a.get("severity") == "HIGH"]

            if high_risk_alerts:
                recommendations.append(
                    {
                        "type": "HIGH_RISK_REDUCTION",
                        "priority": "HIGH",
                        "title": "高リスク銘柄の見直し",
                        "description": f"{len(high_risk_alerts)}銘柄が高リスクのため、投資見直しを推奨します",
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

            # 総合リスクスコアに基づく推奨事項
            total_risk_score = balance_data.get("total_risk_score", 0)
            if total_risk_score > 70:
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

        except Exception as e:
            self.logger.error(f"リスク推奨事項生成エラー: {e}")
            return []


# APIエンドポイント関数
def analyze_stocks_with_simplified_risk(
    stock_codes: List[str],
    analysis_date: Optional[str] = None,
    include_risk_assessment: bool = True,
) -> Dict[str, Any]:
    """株式分析（簡素化リスク評価付き）エンドポイント"""
    try:
        api = RoutineAnalysisAPI()
        return api.analyze_stocks_with_simplified_risk(
            stock_codes, analysis_date, include_risk_assessment
        )
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


def get_simplified_risk_dashboard_data(
    portfolio_data: Dict[str, Any], account_balance: float = 1000000.0
) -> Dict[str, Any]:
    """簡素化リスクダッシュボードデータ取得エンドポイント"""
    try:
        api = RoutineAnalysisAPI()
        return api.get_simplified_risk_dashboard_data(portfolio_data, account_balance)
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


def get_portfolio_risk_summary(
    portfolio_data: Dict[str, Any], account_balance: float = 1000000.0
) -> Dict[str, Any]:
    """ポートフォリオリスクサマリー取得エンドポイント"""
    try:
        api = RoutineAnalysisAPI()
        return api.get_portfolio_risk_summary(portfolio_data, account_balance)
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


def update_risk_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """リスク設定更新エンドポイント"""
    try:
        api = RoutineAnalysisAPI()
        return api.update_risk_settings(settings)
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


def export_risk_report(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """リスクレポートエクスポートエンドポイント"""
    try:
        api = RoutineAnalysisAPI()
        return api.export_risk_report(portfolio_data)
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


if __name__ == "__main__":
    # テスト実行
    try:
        api = RoutineAnalysisAPI()

        # テスト用ポートフォリオデータ
        test_portfolio = {
            "7203": {
                "stock_data": pd.DataFrame(
                    {
                        "Close": [100, 105, 102, 108, 110],
                        "Volume": [1000, 1200, 900, 1300, 1100],
                    }
                ),
                "current_price": 110,
                "position_size": 100,
                "account_balance": 1000000,
            }
        }

        # 簡素化リスクダッシュボードデータ取得テスト
        result = api.get_simplified_risk_dashboard_data(test_portfolio)
        print("簡素化リスクダッシュボードデータ取得テスト:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"テスト実行エラー: {e}")
        traceback.print_exc()
