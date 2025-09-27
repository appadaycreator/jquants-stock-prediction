#!/usr/bin/env python3
"""
リスク管理ダッシュボード用データ生成システム
現在のポジション状況、損切りライン、リスクレベルをWeb上で可視化するためのデータを生成
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from risk_management_system import (
    RiskManagementSystem,
    Position,
    RiskLevel,
    PositionStatus,
)
import os

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskDashboardDataGenerator:
    """リスク管理ダッシュボード用データ生成器"""

    def __init__(self, account_value: float = 1000000):
        self.account_value = account_value
        self.risk_system = RiskManagementSystem(account_value)
        self.setup_sample_positions()

    def setup_sample_positions(self):
        """サンプルポジションの設定"""
        # サンプルポジション追加
        self.risk_system.add_position("7203.T", 2500.0, 100, "LONG", 0.25)
        self.risk_system.add_position("6758.T", 12000.0, 50, "LONG", 0.30)
        self.risk_system.add_position("9984.T", 8000.0, 75, "LONG", 0.35)
        self.risk_system.add_position("7974.T", 15000.0, 30, "LONG", 0.20)
        self.risk_system.add_position("6861.T", 5000.0, 80, "LONG", 0.40)

        # 価格更新（シミュレーション）
        self.risk_system.update_position_price("7203.T", 2400.0)  # 4%下落
        self.risk_system.update_position_price("6758.T", 12500.0)  # 4.2%上昇
        self.risk_system.update_position_price("9984.T", 7500.0)  # 6.25%下落
        self.risk_system.update_position_price("7974.T", 15200.0)  # 1.3%上昇
        self.risk_system.update_position_price("6861.T", 4800.0)  # 4%下落

    def generate_portfolio_overview(self) -> Dict[str, Any]:
        """ポートフォリオ概要データ生成"""
        risk_report = self.risk_system.get_risk_report()

        # ポートフォリオ価値計算
        total_value = self.account_value
        total_exposure = sum(
            pos.current_price * pos.quantity
            for pos in self.risk_system.positions.values()
        )
        total_unrealized_pnl = sum(
            pos.unrealized_pnl for pos in self.risk_system.positions.values()
        )
        portfolio_value = total_value + total_unrealized_pnl

        # リスクレベル判定
        risk_score = risk_report["risk_metrics"]["risk_score"]
        if risk_score < 0.3:
            risk_level = "LOW"
            risk_color = "#10B981"  # Green
        elif risk_score < 0.6:
            risk_level = "MEDIUM"
            risk_color = "#F59E0B"  # Yellow
        elif risk_score < 0.8:
            risk_level = "HIGH"
            risk_color = "#EF4444"  # Red
        else:
            risk_level = "CRITICAL"
            risk_color = "#DC2626"  # Dark Red

        return {
            "timestamp": datetime.now().isoformat(),
            "account_value": self.account_value,
            "portfolio_value": portfolio_value,
            "total_exposure": total_exposure,
            "total_unrealized_pnl": total_unrealized_pnl,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_score": risk_score,
            "max_drawdown": risk_report["risk_metrics"]["max_drawdown"],
            "var_95": risk_report["risk_metrics"]["var_95"],
            "sharpe_ratio": risk_report["risk_metrics"]["sharpe_ratio"],
            "should_reduce_risk": risk_report["should_reduce_risk"],
        }

    def generate_positions_data(self) -> List[Dict[str, Any]]:
        """ポジション詳細データ生成"""
        positions_data = []

        for symbol, position in self.risk_system.positions.items():
            # 損切りまでの距離計算
            if position.position_type == "LONG":
                stop_distance = (
                    (position.current_price - position.stop_loss_price)
                    / position.current_price
                    * 100
                )
            else:
                stop_distance = (
                    (position.stop_loss_price - position.current_price)
                    / position.current_price
                    * 100
                )

            # 利確までの距離計算
            if position.position_type == "LONG":
                profit_distance = (
                    (position.take_profit_price - position.current_price)
                    / position.current_price
                    * 100
                )
            else:
                profit_distance = (
                    (position.current_price - position.take_profit_price)
                    / position.current_price
                    * 100
                )

            # リスクレベル判定
            if position.risk_score < 0.3:
                position_risk_level = "LOW"
                position_risk_color = "#10B981"
            elif position.risk_score < 0.6:
                position_risk_level = "MEDIUM"
                position_risk_color = "#F59E0B"
            elif position.risk_score < 0.8:
                position_risk_level = "HIGH"
                position_risk_color = "#EF4444"
            else:
                position_risk_level = "CRITICAL"
                position_risk_color = "#DC2626"

            # PnL色判定
            pnl_color = "#10B981" if position.unrealized_pnl >= 0 else "#EF4444"

            position_data = {
                "symbol": symbol,
                "company_name": self._get_company_name(symbol),
                "position_type": position.position_type,
                "entry_price": position.entry_price,
                "current_price": position.current_price,
                "quantity": position.quantity,
                "entry_time": position.entry_time.isoformat(),
                "unrealized_pnl": position.unrealized_pnl,
                "unrealized_pnl_percent": (
                    position.unrealized_pnl / (position.entry_price * position.quantity)
                )
                * 100,
                "pnl_color": pnl_color,
                "stop_loss_price": position.stop_loss_price,
                "take_profit_price": position.take_profit_price,
                "stop_distance": stop_distance,
                "profit_distance": profit_distance,
                "risk_score": position.risk_score,
                "risk_level": position_risk_level,
                "risk_color": position_risk_color,
                "status": position.status.value,
                "market_value": position.current_price * position.quantity,
                "weight": (position.current_price * position.quantity)
                / self.account_value
                * 100,
            }

            positions_data.append(position_data)

        return positions_data

    def generate_risk_metrics_chart(self) -> Dict[str, Any]:
        """リスク指標チャートデータ生成"""
        risk_report = self.risk_system.get_risk_report()

        # 過去30日間のリスク指標履歴（シミュレーション）
        dates = [
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(30, 0, -1)
        ]

        # シミュレーションデータ生成
        base_risk_score = risk_report["risk_metrics"]["risk_score"]
        risk_scores = []
        portfolio_values = []
        drawdowns = []

        for i in range(30):
            # ランダムな変動を加える
            variation = np.random.normal(0, 0.05)
            risk_score = max(0, min(1, base_risk_score + variation))
            risk_scores.append(risk_score)

            # ポートフォリオ価値の変動
            pnl_variation = np.random.normal(0, 10000)
            portfolio_value = self.account_value + pnl_variation
            portfolio_values.append(portfolio_value)

            # ドローダウンの変動
            drawdown = max(0, np.random.normal(0.05, 0.02))
            drawdowns.append(drawdown)

        return {
            "dates": dates,
            "risk_scores": risk_scores,
            "portfolio_values": portfolio_values,
            "drawdowns": drawdowns,
            "current_risk_score": base_risk_score,
            "current_portfolio_value": self.account_value
            + sum(pos.unrealized_pnl for pos in self.risk_system.positions.values()),
            "current_drawdown": risk_report["risk_metrics"]["max_drawdown"],
        }

    def generate_position_performance_chart(self) -> Dict[str, Any]:
        """ポジションパフォーマンスチャートデータ生成"""
        positions_data = []

        for symbol, position in self.risk_system.positions.items():
            # 過去30日間の価格履歴（シミュレーション）
            dates = [
                (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(30, 0, -1)
            ]

            # エントリー価格を基準とした価格変動シミュレーション
            base_price = position.entry_price
            prices = [base_price]

            for i in range(29):
                # ランダムウォークで価格変動をシミュレーション
                change = np.random.normal(0, 0.02)  # 2%の標準偏差
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)

            # 現在価格を設定
            prices[-1] = position.current_price

            # 損切り・利確ライン
            stop_loss_line = [position.stop_loss_price] * 30
            take_profit_line = [position.take_profit_price] * 30

            position_chart_data = {
                "symbol": symbol,
                "company_name": self._get_company_name(symbol),
                "dates": dates,
                "prices": prices,
                "stop_loss_line": stop_loss_line,
                "take_profit_line": take_profit_line,
                "entry_price": position.entry_price,
                "current_price": position.current_price,
                "unrealized_pnl": position.unrealized_pnl,
                "unrealized_pnl_percent": (
                    position.unrealized_pnl / (position.entry_price * position.quantity)
                )
                * 100,
                "risk_score": position.risk_score,
            }

            positions_data.append(position_chart_data)

        return {"positions": positions_data, "total_positions": len(positions_data)}

    def generate_risk_alerts(self) -> List[Dict[str, Any]]:
        """リスクアラートデータ生成"""
        risk_report = self.risk_system.get_risk_report()
        alerts = []

        # ポートフォリオレベルアラート
        if risk_report["should_reduce_risk"]:
            alerts.append(
                {
                    "id": "portfolio_risk_high",
                    "type": "WARNING",
                    "title": "ポートフォリオリスクが高すぎます",
                    "message": "リスクスコアが閾値を超えています。ポジションサイズの縮小を検討してください。",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "HIGH",
                    "color": "#EF4444",
                }
            )

        if risk_report["risk_metrics"]["max_drawdown"] > 0.15:
            alerts.append(
                {
                    "id": "max_drawdown_high",
                    "type": "WARNING",
                    "title": "最大ドローダウンが15%を超えています",
                    "message": "損失が拡大しています。損切りを厳格に実行してください。",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "HIGH",
                    "color": "#EF4444",
                }
            )

        # 個別ポジションアラート
        for symbol, position in self.risk_system.positions.items():
            if position.risk_score > 0.8:
                alerts.append(
                    {
                        "id": f"position_risk_{symbol}",
                        "type": "WARNING",
                        "title": f"{symbol}のリスクが高すぎます",
                        "message": f"{symbol}のリスクスコアが{position.risk_score:.2f}です。損切りを検討してください。",
                        "timestamp": datetime.now().isoformat(),
                        "priority": "MEDIUM",
                        "color": "#F59E0B",
                    }
                )

            if (
                position.unrealized_pnl
                < -position.entry_price * position.quantity * 0.1
            ):  # 10%以上の損失
                alerts.append(
                    {
                        "id": f"position_loss_{symbol}",
                        "type": "ALERT",
                        "title": f"{symbol}で10%以上の損失",
                        "message": f"{symbol}で{position.unrealized_pnl:,.0f}円の損失が発生しています。",
                        "timestamp": datetime.now().isoformat(),
                        "priority": "HIGH",
                        "color": "#DC2626",
                    }
                )

        return alerts

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """推奨事項データ生成"""
        risk_report = self.risk_system.get_risk_report()
        recommendations = []

        # リスク管理推奨事項
        if risk_report["risk_metrics"]["risk_score"] > 0.7:
            recommendations.append(
                {
                    "id": "reduce_position_size",
                    "type": "RISK_MANAGEMENT",
                    "title": "ポジションサイズの縮小",
                    "description": "ポートフォリオリスクが高すぎます。各ポジションのサイズを縮小してください。",
                    "priority": "HIGH",
                    "action": "ポジションサイズを20%縮小することを推奨します。",
                }
            )

        if risk_report["risk_metrics"]["max_drawdown"] > 0.15:
            recommendations.append(
                {
                    "id": "strict_stop_loss",
                    "type": "RISK_MANAGEMENT",
                    "title": "損切りラインの厳格化",
                    "description": "最大ドローダウンが15%を超えています。損切りラインを厳格に設定してください。",
                    "priority": "HIGH",
                    "action": "損切りラインを現在の80%に設定することを推奨します。",
                }
            )

        # 個別ポジション推奨事項
        for symbol, position in self.risk_system.positions.items():
            if position.risk_score > 0.6:
                recommendations.append(
                    {
                        "id": f"close_position_{symbol}",
                        "type": "POSITION_MANAGEMENT",
                        "title": f"{symbol}のポジションクローズ検討",
                        "description": f"{symbol}のリスクスコアが{position.risk_score:.2f}です。",
                        "priority": "MEDIUM",
                        "action": f"{symbol}のポジションをクローズすることを検討してください。",
                    }
                )

        return recommendations

    def _get_company_name(self, symbol: str) -> str:
        """銘柄コードから会社名を取得"""
        company_names = {
            "7203.T": "トヨタ自動車",
            "6758.T": "ソニーグループ",
            "9984.T": "ソフトバンクグループ",
            "7974.T": "任天堂",
            "6861.T": "キーエンス",
        }
        return company_names.get(symbol, symbol)

    def generate_all_data(self) -> Dict[str, Any]:
        """全データ生成"""
        logger.info("リスク管理ダッシュボード用データ生成を開始...")

        data = {
            "portfolio_overview": self.generate_portfolio_overview(),
            "positions": self.generate_positions_data(),
            "risk_metrics_chart": self.generate_risk_metrics_chart(),
            "position_performance_chart": self.generate_position_performance_chart(),
            "risk_alerts": self.generate_risk_alerts(),
            "recommendations": self.generate_recommendations(),
            "last_updated": datetime.now().isoformat(),
        }

        logger.info("データ生成完了")
        return data

    def save_data_to_files(self, output_dir: str = "web-app/public/data"):
        """データをファイルに保存"""
        os.makedirs(output_dir, exist_ok=True)

        data = self.generate_all_data()

        # 各データを個別ファイルに保存
        files_to_save = {
            "risk_dashboard_data.json": data,
            "risk_portfolio_overview.json": data["portfolio_overview"],
            "risk_positions.json": data["positions"],
            "risk_metrics_chart.json": data["risk_metrics_chart"],
            "risk_position_performance.json": data["position_performance_chart"],
            "risk_alerts.json": data["risk_alerts"],
            "risk_recommendations.json": data["recommendations"],
        }

        for filename, file_data in files_to_save.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(file_data, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"データを保存しました: {filepath}")


def main():
    """メイン実行関数"""
    logger.info("リスク管理ダッシュボード用データ生成を開始...")

    # データ生成器初期化
    generator = RiskDashboardDataGenerator(account_value=1000000)

    # データ生成と保存
    generator.save_data_to_files()

    logger.info("リスク管理ダッシュボード用データ生成完了")


if __name__ == "__main__":
    main()
