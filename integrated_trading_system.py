#!/usr/bin/env python3
"""
統合トレーディングシステム
最高優先度機能を統合した完全システム

統合機能:
1. リアルタイム売買シグナル生成
2. リスク管理・損切りシステム
3. 複数銘柄同時監視・比較
4. 統合ダッシュボード
5. 自動取引推奨
"""

import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass, asdict
import warnings

warnings.filterwarnings("ignore")

# 自作モジュールのインポート
from realtime_trading_signals import TradingSignalSystem, SignalType, SignalStrength
from risk_management_system import RiskManagementSystem, PositionStatus
from multi_stock_monitor import MultiStockMonitor, InvestmentOpportunity

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("integrated_trading.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class TradingRecommendation:
    """取引推奨事項"""

    symbol: str
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float
    risk_level: str
    position_size: float
    entry_price: float
    stop_loss_price: float
    take_profit_price: float
    reason: str
    priority: int  # 1-5 (5が最高優先度)


@dataclass
class SystemStatus:
    """システムステータス"""

    timestamp: datetime
    total_symbols: int
    active_positions: int
    total_signals: int
    buy_signals: int
    sell_signals: int
    portfolio_value: float
    unrealized_pnl: float
    risk_score: float
    system_health: str


class IntegratedTradingSystem:
    """統合トレーディングシステム"""

    def __init__(self, symbols: List[str], account_value: float = 1000000):
        self.symbols = symbols
        self.account_value = account_value

        # 各システムの初期化
        self.signal_system = TradingSignalSystem(symbols, account_value)
        self.risk_system = RiskManagementSystem(account_value)
        self.monitor_system = MultiStockMonitor(symbols)

        # 統合データ
        self.trading_recommendations = []
        self.system_status = None
        self.last_analysis_time = None

    def run_comprehensive_analysis(self) -> Dict:
        """包括的分析を実行"""
        logger.info("=== 統合トレーディングシステム分析開始 ===")

        # 1. リアルタイムシグナル分析
        logger.info("1. リアルタイムシグナル分析実行中...")
        signal_results = self.signal_system.run_analysis()

        # 2. 複数銘柄監視分析
        logger.info("2. 複数銘柄監視分析実行中...")
        analysis_results = self.monitor_system.analyze_all_stocks()
        portfolio_comparison = self.monitor_system.generate_portfolio_comparison()

        # 3. リスク管理分析
        logger.info("3. リスク管理分析実行中...")
        risk_report = self.risk_system.get_risk_report()

        # 4. 統合推奨事項生成
        logger.info("4. 統合推奨事項生成中...")
        recommendations = self._generate_integrated_recommendations(
            signal_results, analysis_results, risk_report
        )

        # 5. システムステータス更新
        self.system_status = self._update_system_status(
            signal_results, analysis_results, risk_report
        )

        # 6. 統合結果の構築
        integrated_results = {
            "timestamp": datetime.now().isoformat(),
            "system_status": asdict(self.system_status),
            "signal_analysis": signal_results,
            "portfolio_analysis": asdict(portfolio_comparison),
            "risk_analysis": risk_report,
            "trading_recommendations": [asdict(rec) for rec in recommendations],
            "performance_metrics": self._calculate_performance_metrics(
                signal_results, analysis_results, risk_report
            ),
        }

        self.last_analysis_time = datetime.now()
        logger.info("=== 統合分析完了 ===")

        return integrated_results

    def _generate_integrated_recommendations(
        self, signal_results: Dict, analysis_results: Dict, risk_report: Dict
    ) -> List[TradingRecommendation]:
        """統合推奨事項を生成"""
        recommendations = []

        # シグナル分析から推奨事項を生成
        for signal_data in signal_results.get("top_signals", []):
            symbol = signal_data["symbol"]
            signal_type = signal_data["signal_type"]
            confidence = signal_data["confidence"]
            risk_level = signal_data["risk_level"]

            # 分析結果から追加情報を取得
            if symbol in analysis_results:
                analysis = analysis_results[symbol]

                # 統合信頼度計算
                integrated_confidence = (confidence + analysis.confidence) / 2

                # アクション決定
                if signal_type in [
                    "BUY",
                    "STRONG_BUY",
                ] and analysis.investment_opportunity in [
                    InvestmentOpportunity.BUY,
                    InvestmentOpportunity.STRONG_BUY,
                ]:
                    action = "BUY"
                    priority = 5 if signal_type == "STRONG_BUY" else 4
                elif signal_type in [
                    "SELL",
                    "STRONG_SELL",
                ] and analysis.investment_opportunity in [
                    InvestmentOpportunity.SELL,
                    InvestmentOpportunity.STRONG_SELL,
                ]:
                    action = "SELL"
                    priority = 5 if signal_type == "STRONG_SELL" else 4
                else:
                    action = "HOLD"
                    priority = 2

                # ポジションサイズ計算
                position_size = self.risk_system.position_sizer.calculate_position_size(
                    self.account_value,
                    signal_data["price"],
                    signal_data["price"] * 0.95,  # 仮の損切り価格
                    risk_per_trade=0.02,
                )

                # 損切り・利確価格計算
                entry_price = signal_data["price"]
                stop_loss_price = (
                    entry_price * 0.95 if action == "BUY" else entry_price * 1.05
                )
                take_profit_price = (
                    entry_price * 1.10 if action == "BUY" else entry_price * 0.90
                )

                # 推奨理由
                reason = f"シグナル: {signal_data['reason']}; 分析: {analysis.recommendation_reason}"

                recommendation = TradingRecommendation(
                    symbol=symbol,
                    action=action,
                    confidence=integrated_confidence,
                    risk_level=risk_level,
                    position_size=position_size,
                    entry_price=entry_price,
                    stop_loss_price=stop_loss_price,
                    take_profit_price=take_profit_price,
                    reason=reason,
                    priority=priority,
                )

                recommendations.append(recommendation)

        # 優先度でソート
        recommendations.sort(key=lambda x: x.priority, reverse=True)

        return recommendations[:10]  # 上位10件

    def _update_system_status(
        self, signal_results: Dict, analysis_results: Dict, risk_report: Dict
    ) -> SystemStatus:
        """システムステータスを更新"""
        # アクティブポジション数
        active_positions = len(
            [
                pos
                for pos in risk_report.get("positions", [])
                if pos["status"] == PositionStatus.OPEN.value
            ]
        )

        # シグナル統計
        total_signals = signal_results.get("signals_generated", 0)
        buy_signals = signal_results.get("summary", {}).get(
            "buy_signals", 0
        ) + signal_results.get("summary", {}).get("strong_buy_signals", 0)
        sell_signals = signal_results.get("summary", {}).get(
            "sell_signals", 0
        ) + signal_results.get("summary", {}).get("strong_sell_signals", 0)

        # ポートフォリオ価値
        portfolio_value = risk_report.get("account_value", self.account_value)
        unrealized_pnl = sum(
            pos["unrealized_pnl"] for pos in risk_report.get("positions", [])
        )

        # リスクスコア
        risk_score = risk_report.get("risk_metrics", {}).get("risk_score", 0.0)

        # システムヘルス判定
        if risk_score < 0.3 and total_signals > 0:
            system_health = "EXCELLENT"
        elif risk_score < 0.5 and total_signals > 0:
            system_health = "GOOD"
        elif risk_score < 0.7:
            system_health = "FAIR"
        else:
            system_health = "POOR"

        return SystemStatus(
            timestamp=datetime.now(),
            total_symbols=len(self.symbols),
            active_positions=active_positions,
            total_signals=total_signals,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            portfolio_value=portfolio_value,
            unrealized_pnl=unrealized_pnl,
            risk_score=risk_score,
            system_health=system_health,
        )

    def _calculate_performance_metrics(
        self, signal_results: Dict, analysis_results: Dict, risk_report: Dict
    ) -> Dict:
        """パフォーマンス指標を計算"""
        # 分析完了率
        analysis_completion_rate = len(analysis_results) / len(self.symbols)

        # シグナル品質
        signal_quality = np.mean(
            [signal["confidence"] for signal in signal_results.get("top_signals", [])]
        )

        # リスク効率
        risk_efficiency = 1 - risk_report.get("risk_metrics", {}).get("risk_score", 0.5)

        # 分散投資効果
        diversification_score = 0.0  # 複数銘柄監視から取得

        # 総合スコア
        overall_score = (
            analysis_completion_rate * 0.3
            + signal_quality * 0.3
            + risk_efficiency * 0.2
            + diversification_score * 0.2
        )

        return {
            "analysis_completion_rate": analysis_completion_rate,
            "signal_quality": signal_quality,
            "risk_efficiency": risk_efficiency,
            "diversification_score": diversification_score,
            "overall_score": overall_score,
        }

    def execute_trading_recommendations(
        self, recommendations: List[TradingRecommendation]
    ) -> Dict:
        """取引推奨事項を実行"""
        execution_results = {
            "timestamp": datetime.now().isoformat(),
            "total_recommendations": len(recommendations),
            "executed_actions": [],
            "skipped_actions": [],
            "errors": [],
        }

        for recommendation in recommendations:
            try:
                if recommendation.action == "BUY":
                    # 買いポジション追加
                    position = self.risk_system.add_position(
                        symbol=recommendation.symbol,
                        entry_price=recommendation.entry_price,
                        quantity=int(
                            recommendation.position_size / recommendation.entry_price
                        ),
                        position_type="LONG",
                    )

                    execution_results["executed_actions"].append(
                        {
                            "symbol": recommendation.symbol,
                            "action": "BUY",
                            "quantity": position.quantity,
                            "entry_price": position.entry_price,
                            "stop_loss": position.stop_loss_price,
                            "take_profit": position.take_profit_price,
                        }
                    )

                    logger.info(f"買いポジション追加: {recommendation.symbol}")

                elif recommendation.action == "SELL":
                    # 売りポジション追加
                    position = self.risk_system.add_position(
                        symbol=recommendation.symbol,
                        entry_price=recommendation.entry_price,
                        quantity=int(
                            recommendation.position_size / recommendation.entry_price
                        ),
                        position_type="SHORT",
                    )

                    execution_results["executed_actions"].append(
                        {
                            "symbol": recommendation.symbol,
                            "action": "SELL",
                            "quantity": position.quantity,
                            "entry_price": position.entry_price,
                            "stop_loss": position.stop_loss_price,
                            "take_profit": position.take_profit_price,
                        }
                    )

                    logger.info(f"売りポジション追加: {recommendation.symbol}")

                else:  # HOLD
                    execution_results["skipped_actions"].append(
                        {
                            "symbol": recommendation.symbol,
                            "action": "HOLD",
                            "reason": recommendation.reason,
                        }
                    )

            except Exception as e:
                error_msg = f"実行エラー {recommendation.symbol}: {e}"
                execution_results["errors"].append(error_msg)
                logger.error(error_msg)

        return execution_results

    def generate_dashboard_data(self) -> Dict:
        """ダッシュボード用データを生成"""
        # 最新の分析結果を取得
        if (
            not self.last_analysis_time
            or (datetime.now() - self.last_analysis_time).seconds > 300
        ):
            # 5分以上経過している場合は再分析
            analysis_results = self.run_comprehensive_analysis()
        else:
            # 既存の結果を使用
            analysis_results = self._get_cached_results()

        # ダッシュボード用データを構築
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "system_status": analysis_results.get("system_status", {}),
            "performance_metrics": analysis_results.get("performance_metrics", {}),
            "top_recommendations": analysis_results.get("trading_recommendations", [])[
                :5
            ],
            "risk_summary": {
                "risk_score": analysis_results.get("risk_analysis", {})
                .get("risk_metrics", {})
                .get("risk_score", 0),
                "should_reduce_risk": analysis_results.get("risk_analysis", {}).get(
                    "should_reduce_risk", False
                ),
                "high_risk_positions": analysis_results.get("risk_analysis", {}).get(
                    "high_risk_positions", []
                ),
            },
            "portfolio_summary": {
                "total_symbols": analysis_results.get("system_status", {}).get(
                    "total_symbols", 0
                ),
                "analyzed_symbols": analysis_results.get("portfolio_analysis", {}).get(
                    "analyzed_symbols", 0
                ),
                "diversification_score": analysis_results.get(
                    "portfolio_analysis", {}
                ).get("diversification_score", 0),
            },
        }

        return dashboard_data

    def _get_cached_results(self) -> Dict:
        """キャッシュされた結果を取得"""
        # 実際の実装では、メモリやファイルからキャッシュされた結果を取得
        return {}

    def save_integrated_results(
        self, results: Dict, filename: str = "integrated_trading_results.json"
    ):
        """統合結果を保存"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"統合結果を保存しました: {filename}")
        except Exception as e:
            logger.error(f"保存エラー: {e}")

    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """継続監視を実行"""
        logger.info(f"継続監視開始: {interval_minutes}分間隔")

        while True:
            try:
                # 包括的分析実行
                results = self.run_comprehensive_analysis()

                # 結果保存
                self.save_integrated_results(results)

                # 推奨事項実行（自動取引が有効な場合）
                recommendations = [
                    TradingRecommendation(**rec)
                    for rec in results.get("trading_recommendations", [])
                ]
                if recommendations:
                    execution_results = self.execute_trading_recommendations(
                        recommendations
                    )
                    logger.info(
                        f"推奨事項実行完了: {len(execution_results["executed_actions"])}件"
                    )

                # 待機
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("継続監視を停止しました")
                break
            except Exception as e:
                logger.error(f"継続監視エラー: {e}")
                time.sleep(60)  # エラー時は1分待機


def main():
    """メイン実行関数"""
    # 監視対象銘柄
    symbols = [
        "7203.T",  # トヨタ自動車
        "6758.T",  # ソニーグループ
        "9984.T",  # ソフトバンクグループ
        "9432.T",  # 日本電信電話
        "6861.T",  # キーエンス
        "4063.T",  # 信越化学工業
        "8035.T",  # 東京エレクトロン
        "8306.T",  # 三菱UFJフィナンシャル・グループ
        "4503.T",  # アステラス製薬
        "4519.T",  # 中外製薬
    ]

    # 統合トレーディングシステム初期化
    trading_system = IntegratedTradingSystem(symbols, account_value=1000000)

    # 包括的分析実行
    results = trading_system.run_comprehensive_analysis()

    # 結果保存
    trading_system.save_integrated_results(results)

    # 結果表示
    print("\n" + "=" * 80)
    print("🚀 統合トレーディングシステム 分析結果")
    print("=" * 80)

    system_status = results.get("system_status", {})
    print(f"分析時刻: {results["timestamp"]}")
    print(f"システムヘルス: {system_status.get("system_health", "UNKNOWN")}")
    print(f"監視銘柄数: {system_status.get("total_symbols", 0)}")
    print(f"アクティブポジション: {system_status.get("active_positions", 0)}")
    print(f"総シグナル数: {system_status.get("total_signals", 0)}")
    print(f"ポートフォリオ価値: ¥{system_status.get("portfolio_value", 0):,.0f}")
    print(f"未実現損益: ¥{system_status.get("unrealized_pnl", 0):,.0f}")
    print(f"リスクスコア: {system_status.get("risk_score", 0):.2f}")

    print("\n💡 取引推奨事項:")
    recommendations = results.get("trading_recommendations", [])
    for i, rec in enumerate(recommendations[:5], 1):
        print(
            f"  {i}. {rec["symbol"]} - {rec["action"]} "
            f"(信頼度: {rec["confidence"]:.2f}, 優先度: {rec["priority"]})"
        )
        print(
            f"     価格: ¥{rec["entry_price"]:.0f}, ポジション: ¥{rec["position_size"]:,.0f}"
        )
        print(f"     理由: {rec["reason"]}")
        print()

    print("📊 パフォーマンス指標:")
    metrics = results.get("performance_metrics", {})
    print(f"  分析完了率: {metrics.get("analysis_completion_rate", 0):.1%}")
    print(f"  シグナル品質: {metrics.get("signal_quality", 0):.2f}")
    print(f"  リスク効率: {metrics.get("risk_efficiency", 0):.2f}")
    print(f"  総合スコア: {metrics.get("overall_score", 0):.2f}")

    print("\n🛡️ リスク管理:")
    risk_analysis = results.get("risk_analysis", {})
    print(
        f"  リスクスコア: {risk_analysis.get("risk_metrics", {}).get("risk_score", 0):.2f}"
    )
    print(
        f"  リスク削減推奨: {"はい" if risk_analysis.get("should_reduce_risk", False) else "いいえ"}"
    )
    high_risk = risk_analysis.get("high_risk_positions", [])
    if high_risk:
        print(f"  高リスクポジション: {", ".join(high_risk)}")

    print("\n" + "=" * 80)
    print("✅ 統合分析完了！")
    print("📁 詳細結果: integrated_trading_results.json")
    print("🔄 継続監視を開始するには: trading_system.run_continuous_monitoring()")


if __name__ == "__main__":
    main()
