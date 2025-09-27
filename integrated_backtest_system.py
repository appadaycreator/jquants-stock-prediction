#!/usr/bin/env python3
"""
統合バックテストシステム
既存システムとの統合、包括的なバックテスト実行

機能:
1. 既存のリアルタイムシグナルシステムとの統合
2. 株価予測システムとの統合
3. 包括的なバックテスト実行
4. 結果の統合レポート生成
5. システム全体の最適化
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 既存システムのインポート
from realtime_trading_signals import TradingSignalSystem, SignalGenerator, RiskManager
from advanced_backtest_system import (
    BacktestEngine,
    MomentumStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
)
from advanced_strategy_framework import MultiStrategyManager, AdvancedStrategyOptimizer
from advanced_performance_metrics import (
    AdvancedPerformanceAnalyzer,
    PerformanceVisualizer,
)

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("integrated_backtest.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class IntegratedBacktestResult:
    """統合バックテスト結果"""

    # 基本情報
    start_date: datetime
    end_date: datetime
    symbols: List[str]
    initial_capital: float
    final_capital: float

    # 個別戦略結果
    strategy_results: Dict[str, Any]

    # 統合結果
    combined_return: float
    combined_sharpe: float
    combined_max_drawdown: float

    # 最適化結果
    optimized_weights: Dict[str, float]
    portfolio_performance: Dict[str, float]

    # 詳細分析
    advanced_metrics: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    stress_test_results: Dict[str, Any]


class IntegratedBacktestSystem:
    """統合バックテストシステム"""

    def __init__(self, symbols: List[str], initial_capital: float = 1000000):
        self.symbols = symbols
        self.initial_capital = initial_capital
        self.data = {}
        self.strategy_results = {}
        self.optimized_weights = {}
        self.portfolio_performance = {}

    def fetch_market_data(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        """市場データ取得"""
        logger.info("市場データ取得開始")

        data = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(
                    self._fetch_single_symbol, symbol, start_date, end_date
                ): symbol
                for symbol in self.symbols
            }

            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    symbol_data = future.result()
                    if symbol_data is not None and not symbol_data.empty:
                        data[symbol] = symbol_data
                        logger.info(f"データ取得完了: {symbol} ({len(symbol_data)}行)")
                    else:
                        logger.warning(f"データ取得失敗: {symbol}")
                except Exception as e:
                    logger.error(f"データ取得エラー {symbol}: {e}")

        self.data = data
        logger.info(f"データ取得完了: {len(data)}銘柄")
        return data

    def _fetch_single_symbol(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """単一銘柄データ取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            return data if not data.empty else None
        except Exception as e:
            logger.error(f"データ取得エラー {symbol}: {e}")
            return None

    def run_comprehensive_backtest(
        self, start_date: datetime, end_date: datetime
    ) -> IntegratedBacktestResult:
        """包括的バックテスト実行"""
        logger.info("=== 統合バックテスト開始 ===")

        # 1. データ取得
        self.fetch_market_data(start_date, end_date)

        if not self.data:
            raise ValueError("データが取得できませんでした")

        # 2. 個別戦略バックテスト
        strategy_results = self._run_individual_strategies(start_date, end_date)

        # 3. 戦略最適化
        optimized_weights = self._optimize_strategies(strategy_results)

        # 4. ポートフォリオ最適化
        portfolio_performance = self._optimize_portfolio(
            strategy_results, optimized_weights
        )

        # 5. 高度な分析
        advanced_metrics = self._calculate_advanced_metrics(strategy_results)
        risk_analysis = self._perform_risk_analysis(strategy_results)
        stress_test_results = self._perform_stress_test(strategy_results)

        # 6. 統合結果計算
        combined_metrics = self._calculate_combined_metrics(
            strategy_results, optimized_weights
        )

        result = IntegratedBacktestResult(
            start_date=start_date,
            end_date=end_date,
            symbols=list(self.data.keys()),
            initial_capital=self.initial_capital,
            final_capital=combined_metrics["final_capital"],
            strategy_results=strategy_results,
            combined_return=combined_metrics["total_return"],
            combined_sharpe=combined_metrics["sharpe_ratio"],
            combined_max_drawdown=combined_metrics["max_drawdown"],
            optimized_weights=optimized_weights,
            portfolio_performance=portfolio_performance,
            advanced_metrics=advanced_metrics,
            risk_analysis=risk_analysis,
            stress_test_results=stress_test_results,
        )

        logger.info("=== 統合バックテスト完了 ===")
        return result

    def _run_individual_strategies(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """個別戦略バックテスト実行"""
        logger.info("個別戦略バックテスト開始")

        strategy_results = {}

        # 戦略定義
        strategies = [
            MomentumStrategy({"lookback": 20, "threshold": 0.05}),
            MeanReversionStrategy({"lookback": 20, "std_threshold": 2.0}),
            BreakoutStrategy({"lookback": 20, "volume_threshold": 1.5}),
        ]

        # 各銘柄で戦略実行
        for symbol, data in self.data.items():
            logger.info(f"戦略実行中: {symbol}")
            symbol_results = {}

            for strategy in strategies:
                try:
                    from advanced_backtest_system import BacktestEngine

                    engine = BacktestEngine(initial_capital=self.initial_capital)
                    result = engine.run_backtest(data, strategy, start_date, end_date)

                    symbol_results[strategy.name] = {
                        "total_return": result.total_return,
                        "sharpe_ratio": result.sharpe_ratio,
                        "max_drawdown": result.max_drawdown,
                        "win_rate": result.win_rate,
                        "total_trades": result.total_trades,
                        "equity_curve": result.equity_curve,
                        "trades": result.trades,
                    }

                except Exception as e:
                    logger.error(f"戦略実行エラー {symbol}-{strategy.name}: {e}")
                    symbol_results[strategy.name] = None

            strategy_results[symbol] = symbol_results

        self.strategy_results = strategy_results
        return strategy_results

    def _optimize_strategies(
        self, strategy_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """戦略最適化"""
        logger.info("戦略最適化開始")

        # 各戦略の平均パフォーマンス計算
        strategy_performance = {}

        for strategy_name in ["Momentum", "MeanReversion", "Breakout"]:
            returns = []
            sharpe_ratios = []

            for symbol, results in strategy_results.items():
                if results and strategy_name in results and results[strategy_name]:
                    returns.append(results[strategy_name]["total_return"])
                    sharpe_ratios.append(results[strategy_name]["sharpe_ratio"])

            if returns:
                avg_return = np.mean(returns)
                avg_sharpe = np.mean(sharpe_ratios)
                strategy_performance[strategy_name] = {
                    "avg_return": avg_return,
                    "avg_sharpe": avg_sharpe,
                    "consistency": 1 - np.std(returns) / (abs(np.mean(returns)) + 1e-8),
                }

        # 重み計算（シャープレシオベース）
        total_sharpe = sum(sp["avg_sharpe"] for sp in strategy_performance.values())
        optimized_weights = {}

        for strategy_name, perf in strategy_performance.items():
            weight = (
                perf["avg_sharpe"] / total_sharpe
                if total_sharpe > 0
                else 1 / len(strategy_performance)
            )
            optimized_weights[strategy_name] = weight

        self.optimized_weights = optimized_weights
        logger.info(f"最適化重み: {optimized_weights}")
        return optimized_weights

    def _optimize_portfolio(
        self, strategy_results: Dict[str, Any], optimized_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """ポートフォリオ最適化"""
        logger.info("ポートフォリオ最適化開始")

        # 各銘柄の重み計算
        symbol_weights = {}
        total_performance = 0

        for symbol, results in strategy_results.items():
            symbol_performance = 0
            weight_sum = 0

            for strategy_name, weight in optimized_weights.items():
                if results and strategy_name in results and results[strategy_name]:
                    strategy_return = results[strategy_name]["total_return"]
                    symbol_performance += strategy_return * weight
                    weight_sum += weight

            if weight_sum > 0:
                symbol_weights[symbol] = symbol_performance / weight_sum
                total_performance += symbol_performance / weight_sum

        # 重み正規化
        if total_performance > 0:
            for symbol in symbol_weights:
                symbol_weights[symbol] = symbol_weights[symbol] / total_performance

        # ポートフォリオパフォーマンス計算
        portfolio_return = sum(
            (
                symbol_weights.get(symbol, 0)
                * np.mean(
                    [
                        results[strategy]["total_return"]
                        for strategy in ["Momentum", "MeanReversion", "Breakout"]
                        if results and strategy in results and results[strategy]
                    ]
                )
                if results
                else 0
            )
            for symbol, results in strategy_results.items()
        )

        portfolio_performance = {
            "symbol_weights": symbol_weights,
            "portfolio_return": portfolio_return,
            "diversification_ratio": (
                len(symbol_weights) / sum(symbol_weights.values())
                if symbol_weights
                else 0
            ),
            "concentration_risk": max(symbol_weights.values()) if symbol_weights else 0,
        }

        self.portfolio_performance = portfolio_performance
        return portfolio_performance

    def _calculate_advanced_metrics(
        self, strategy_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """高度な指標計算"""
        logger.info("高度な指標計算開始")

        # 全戦略のリターン系列を結合
        all_returns = []
        all_equity_curves = []

        for symbol, results in strategy_results.items():
            for strategy_name, result in results.items():
                if result and "equity_curve" in result:
                    returns = result["equity_curve"].pct_change().dropna()
                    all_returns.extend(returns.tolist())
                    all_equity_curves.append(result["equity_curve"])

        if not all_returns:
            return {}

        # 高度な指標計算
        returns_series = pd.Series(all_returns)

        # 基本統計
        advanced_metrics = {
            "mean_return": returns_series.mean(),
            "volatility": returns_series.std(),
            "skewness": returns_series.skew(),
            "kurtosis": returns_series.kurtosis(),
            "var_95": np.percentile(returns_series, 5),
            "var_99": np.percentile(returns_series, 1),
            "max_return": returns_series.max(),
            "min_return": returns_series.min(),
        }

        return advanced_metrics

    def _perform_risk_analysis(
        self, strategy_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """リスク分析"""
        logger.info("リスク分析開始")

        risk_metrics = {}

        # 各戦略のリスク指標計算
        for strategy_name in ["Momentum", "MeanReversion", "Breakout"]:
            strategy_risks = []

            for symbol, results in strategy_results.items():
                if results and strategy_name in results and results[strategy_name]:
                    result = results[strategy_name]
                    strategy_risks.append(
                        {
                            "max_drawdown": result["max_drawdown"],
                            "sharpe_ratio": result["sharpe_ratio"],
                            "win_rate": result["win_rate"],
                        }
                    )

            if strategy_risks:
                risk_metrics[strategy_name] = {
                    "avg_max_drawdown": np.mean(
                        [r["max_drawdown"] for r in strategy_risks]
                    ),
                    "avg_sharpe": np.mean([r["sharpe_ratio"] for r in strategy_risks]),
                    "avg_win_rate": np.mean([r["win_rate"] for r in strategy_risks]),
                    "risk_consistency": 1
                    - np.std([r["max_drawdown"] for r in strategy_risks]),
                }

        return risk_metrics

    def _perform_stress_test(self, strategy_results: Dict[str, Any]) -> Dict[str, Any]:
        """ストレステスト"""
        logger.info("ストレステスト開始")

        stress_results = {}

        # 最悪ケースシナリオ
        worst_returns = []
        worst_drawdowns = []

        for symbol, results in strategy_results.items():
            for strategy_name, result in results.items():
                if result:
                    worst_returns.append(result["total_return"])
                    worst_drawdowns.append(result["max_drawdown"])

        if worst_returns:
            stress_results = {
                "worst_case_return": min(worst_returns),
                "worst_case_drawdown": max(worst_drawdowns),
                "average_return": np.mean(worst_returns),
                "return_volatility": np.std(worst_returns),
                "downside_risk": np.mean([r for r in worst_returns if r < 0]),
            }

        return stress_results

    def _calculate_combined_metrics(
        self, strategy_results: Dict[str, Any], optimized_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """統合指標計算"""
        logger.info("統合指標計算開始")

        # 重み付きリターン計算
        weighted_returns = []
        weighted_sharpe = []
        weighted_drawdowns = []

        for symbol, results in strategy_results.items():
            for strategy_name, result in results.items():
                if result and strategy_name in optimized_weights:
                    weight = optimized_weights[strategy_name]
                    weighted_returns.append(result["total_return"] * weight)
                    weighted_sharpe.append(result["sharpe_ratio"] * weight)
                    weighted_drawdowns.append(result["max_drawdown"] * weight)

        if weighted_returns:
            combined_return = sum(weighted_returns)
            combined_sharpe = sum(weighted_sharpe)
            combined_drawdown = sum(weighted_drawdowns)
            final_capital = self.initial_capital * (1 + combined_return)
        else:
            combined_return = 0
            combined_sharpe = 0
            combined_drawdown = 0
            final_capital = self.initial_capital

        return {
            "total_return": combined_return,
            "sharpe_ratio": combined_sharpe,
            "max_drawdown": combined_drawdown,
            "final_capital": final_capital,
        }

    def generate_comprehensive_report(self, result: IntegratedBacktestResult) -> str:
        """包括的レポート生成"""
        logger.info("包括的レポート生成開始")

        report = []
        report.append("=" * 100)
        report.append("🚀 統合バックテストシステム - 包括的分析レポート")
        report.append("=" * 100)

        # 基本情報
        report.append(
            f"\n📅 テスト期間: {result.start_date.strftime('%Y-%m-%d')} - {result.end_date.strftime('%Y-%m-%d')}"
        )
        report.append(f"💰 初期資本: ¥{result.initial_capital:,}")
        report.append(f"💰 最終資本: ¥{result.final_capital:,.0f}")
        report.append(f"📈 総リターン: {result.combined_return:.2%}")
        report.append(f"📊 監視銘柄数: {len(result.symbols)}")

        # 統合パフォーマンス
        report.append(f"\n🎯 統合パフォーマンス:")
        report.append(f"  シャープレシオ: {result.combined_sharpe:.2f}")
        report.append(f"  最大ドローダウン: {result.combined_max_drawdown:.2%}")

        # 最適化結果
        if result.optimized_weights:
            report.append(f"\n⚖️ 最適化重み:")
            for strategy, weight in result.optimized_weights.items():
                report.append(f"  {strategy}: {weight:.2%}")

        # ポートフォリオパフォーマンス
        if result.portfolio_performance:
            report.append(f"\n📊 ポートフォリオ分析:")
            for key, value in result.portfolio_performance.items():
                if isinstance(value, dict):
                    report.append(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        report.append(f"    {sub_key}: {sub_value:.2%}")
                else:
                    report.append(f"  {key}: {value:.2%}")

        # 高度な指標
        if result.advanced_metrics:
            report.append(f"\n📈 高度な指標:")
            for key, value in result.advanced_metrics.items():
                report.append(f"  {key}: {value:.4f}")

        # リスク分析
        if result.risk_analysis:
            report.append(f"\n⚠️ リスク分析:")
            for strategy, risks in result.risk_analysis.items():
                report.append(f"  {strategy}:")
                for risk_key, risk_value in risks.items():
                    report.append(f"    {risk_key}: {risk_value:.4f}")

        # ストレステスト
        if result.stress_test_results:
            report.append(f"\n🔥 ストレステスト:")
            for key, value in result.stress_test_results.items():
                report.append(f"  {key}: {value:.4f}")

        # 個別戦略結果サマリー
        report.append(f"\n📋 個別戦略結果サマリー:")
        for symbol, results in result.strategy_results.items():
            report.append(f"  {symbol}:")
            for strategy_name, result_data in results.items():
                if result_data:
                    report.append(
                        f"    {strategy_name}: リターン {result_data['total_return']:.2%}, "
                        f"シャープ {result_data['sharpe_ratio']:.2f}"
                    )
                else:
                    report.append(f"    {strategy_name}: データなし")

        return "\n".join(report)

    def save_results(
        self,
        result: IntegratedBacktestResult,
        base_filename: str = "integrated_backtest",
    ):
        """結果保存"""
        logger.info("結果保存開始")

        # JSON形式で保存
        result_dict = asdict(result)

        # 日時を文字列に変換
        for key, value in result_dict.items():
            if isinstance(value, datetime):
                result_dict[key] = value.isoformat()

        with open(f"{base_filename}_results.json", "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2, default=str)

        # レポート保存
        report = self.generate_comprehensive_report(result)
        with open(f"{base_filename}_report.txt", "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(
            f"結果を保存しました: {base_filename}_results.json, {base_filename}_report.txt"
        )


def main():
    """メイン実行関数"""
    logger.info("=== 統合バックテストシステム開始 ===")

    # 設定
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

    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    initial_capital = 1000000

    # 統合バックテストシステム初期化
    system = IntegratedBacktestSystem(symbols, initial_capital)

    try:
        # 包括的バックテスト実行
        result = system.run_comprehensive_backtest(start_date, end_date)

        # レポート生成・表示
        report = system.generate_comprehensive_report(result)
        print(report)

        # 結果保存
        system.save_results(result)

        logger.info("=== 統合バックテスト完了 ===")

    except Exception as e:
        logger.error(f"統合バックテストエラー: {e}")
        raise


if __name__ == "__main__":
    main()
