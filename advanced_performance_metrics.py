#!/usr/bin/env python3
"""
高度なパフォーマンス指標システム
詳細なリスク分析、統計指標、パフォーマンス評価

機能:
1. 詳細なリスク指標計算
2. 統計的検定
3. リスク調整リターン
4. ストレステスト
5. パフォーマンス分解
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@dataclass
class AdvancedMetrics:
    """高度なパフォーマンス指標"""

    # 基本指標
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

    # リスク指標
    max_drawdown: float
    max_drawdown_duration: int
    var_95: float  # Value at Risk 95%
    var_99: float  # Value at Risk 99%
    cvar_95: float  # Conditional VaR 95%
    cvar_99: float  # Conditional VaR 99%
    tail_ratio: float

    # 統計指標
    skewness: float
    kurtosis: float
    jarque_bera_stat: float
    jarque_bera_pvalue: float

    # リスク調整指標
    information_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    beta: float
    tracking_error: float

    # 分散分析
    systematic_risk: float
    unsystematic_risk: float
    r_squared: float

    # ストレステスト
    worst_month: float
    worst_quarter: float
    worst_year: float
    consecutive_losses: int
    recovery_time: int

    # パフォーマンス分解
    alpha: float
    beta_return: float
    residual_return: float
    market_timing: float
    stock_selection: float


class AdvancedPerformanceAnalyzer:
    """高度なパフォーマンス分析クラス"""

    def __init__(
        self,
        risk_free_rate: float = 0.02,
        benchmark_returns: Optional[pd.Series] = None,
    ):
        self.risk_free_rate = risk_free_rate
        self.benchmark_returns = benchmark_returns

    def calculate_advanced_metrics(
        self,
        returns: pd.Series,
        equity_curve: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
    ) -> AdvancedMetrics:
        """高度な指標計算"""
        logger.info("高度なパフォーマンス指標計算開始")

        # 基本指標
        basic_metrics = self._calculate_basic_metrics(returns, equity_curve)

        # リスク指標
        risk_metrics = self._calculate_risk_metrics(returns, equity_curve)

        # 統計指標
        statistical_metrics = self._calculate_statistical_metrics(returns)

        # リスク調整指標
        risk_adjusted_metrics = self._calculate_risk_adjusted_metrics(
            returns, benchmark_returns
        )

        # 分散分析
        variance_metrics = self._calculate_variance_analysis(returns, benchmark_returns)

        # ストレステスト
        stress_metrics = self._calculate_stress_test(returns, equity_curve)

        # パフォーマンス分解
        performance_decomposition = self._calculate_performance_decomposition(
            returns, benchmark_returns
        )

        return AdvancedMetrics(
            # 基本指標
            total_return=basic_metrics["total_return"],
            annualized_return=basic_metrics["annualized_return"],
            volatility=basic_metrics["volatility"],
            sharpe_ratio=basic_metrics["sharpe_ratio"],
            sortino_ratio=basic_metrics["sortino_ratio"],
            calmar_ratio=basic_metrics["calmar_ratio"],
            # リスク指標
            max_drawdown=risk_metrics["max_drawdown"],
            max_drawdown_duration=risk_metrics["max_drawdown_duration"],
            var_95=risk_metrics["var_95"],
            var_99=risk_metrics["var_99"],
            cvar_95=risk_metrics["cvar_95"],
            cvar_99=risk_metrics["cvar_99"],
            tail_ratio=risk_metrics["tail_ratio"],
            # 統計指標
            skewness=statistical_metrics["skewness"],
            kurtosis=statistical_metrics["kurtosis"],
            jarque_bera_stat=statistical_metrics["jarque_bera_stat"],
            jarque_bera_pvalue=statistical_metrics["jarque_bera_pvalue"],
            # リスク調整指標
            information_ratio=risk_adjusted_metrics["information_ratio"],
            treynor_ratio=risk_adjusted_metrics["treynor_ratio"],
            jensen_alpha=risk_adjusted_metrics["jensen_alpha"],
            beta=risk_adjusted_metrics["beta"],
            tracking_error=risk_adjusted_metrics["tracking_error"],
            # 分散分析
            systematic_risk=variance_metrics["systematic_risk"],
            unsystematic_risk=variance_metrics["unsystematic_risk"],
            r_squared=variance_metrics["r_squared"],
            # ストレステスト
            worst_month=stress_metrics["worst_month"],
            worst_quarter=stress_metrics["worst_quarter"],
            worst_year=stress_metrics["worst_year"],
            consecutive_losses=stress_metrics["consecutive_losses"],
            recovery_time=stress_metrics["recovery_time"],
            # パフォーマンス分解
            alpha=performance_decomposition["alpha"],
            beta_return=performance_decomposition["beta_return"],
            residual_return=performance_decomposition["residual_return"],
            market_timing=performance_decomposition["market_timing"],
            stock_selection=performance_decomposition["stock_selection"],
        )

    def _calculate_basic_metrics(
        self, returns: pd.Series, equity_curve: pd.Series
    ) -> Dict[str, float]:
        """基本指標計算"""
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)

        # シャープレシオ
        excess_returns = returns - self.risk_free_rate / 252
        sharpe_ratio = (
            excess_returns.mean() / returns.std() * np.sqrt(252)
            if returns.std() > 0
            else 0
        )

        # ソルティノレシオ（下方リスク調整）
        downside_returns = returns[returns < 0]
        downside_volatility = (
            downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        )
        sortino_ratio = (
            (annualized_return - self.risk_free_rate) / downside_volatility
            if downside_volatility > 0
            else 0
        )

        # カルマーレシオ
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        max_drawdown = abs(drawdown.min())
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0

        return {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
        }

    def _calculate_risk_metrics(
        self, returns: pd.Series, equity_curve: pd.Series
    ) -> Dict[str, float]:
        """リスク指標計算"""
        # 最大ドローダウン
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        max_drawdown = abs(drawdown.min())

        # 最大ドローダウン期間
        max_dd_duration = self._calculate_max_drawdown_duration(drawdown)

        # VaR計算
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)

        # CVaR計算
        cvar_95 = (
            returns[returns <= var_95].mean()
            if len(returns[returns <= var_95]) > 0
            else 0
        )
        cvar_99 = (
            returns[returns <= var_99].mean()
            if len(returns[returns <= var_99]) > 0
            else 0
        )

        # テールレシオ
        tail_ratio = abs(var_95 / var_99) if var_99 != 0 else 0

        return {
            "max_drawdown": max_drawdown,
            "max_drawdown_duration": max_dd_duration,
            "var_95": var_95,
            "var_99": var_99,
            "cvar_95": cvar_95,
            "cvar_99": cvar_99,
            "tail_ratio": tail_ratio,
        }

    def _calculate_max_drawdown_duration(self, drawdown: pd.Series) -> int:
        """最大ドローダウン期間計算"""
        in_drawdown = drawdown < 0
        drawdown_periods = []
        current_period = 0

        for is_dd in in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0

        if current_period > 0:
            drawdown_periods.append(current_period)

        return max(drawdown_periods) if drawdown_periods else 0

    def _calculate_statistical_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """統計指標計算"""
        # 歪度・尖度
        skewness = returns.skew()
        kurtosis = returns.kurtosis()

        # Jarque-Bera検定（正規性検定）
        jb_stat, jb_pvalue = stats.jarque_bera(returns.dropna())

        return {
            "skewness": skewness,
            "kurtosis": kurtosis,
            "jarque_bera_stat": jb_stat,
            "jarque_bera_pvalue": jb_pvalue,
        }

    def _calculate_risk_adjusted_metrics(
        self, returns: pd.Series, benchmark_returns: Optional[pd.Series]
    ) -> Dict[str, float]:
        """リスク調整指標計算"""
        if benchmark_returns is None:
            return {
                "information_ratio": 0,
                "treynor_ratio": 0,
                "jensen_alpha": 0,
                "beta": 0,
                "tracking_error": 0,
            }

        # 共通期間でデータを揃える
        common_index = returns.index.intersection(benchmark_returns.index)
        if len(common_index) == 0:
            return {
                "information_ratio": 0,
                "treynor_ratio": 0,
                "jensen_alpha": 0,
                "beta": 0,
                "tracking_error": 0,
            }

        aligned_returns = returns.loc[common_index]
        aligned_benchmark = benchmark_returns.loc[common_index]

        # ベータ計算
        covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
        benchmark_variance = np.var(aligned_benchmark)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0

        # アルファ計算
        alpha = aligned_returns.mean() - (
            self.risk_free_rate / 252
            + beta * (aligned_benchmark.mean() - self.risk_free_rate / 252)
        )

        # 情報レシオ
        excess_returns = aligned_returns - aligned_benchmark
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = (
            excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            if excess_returns.std() > 0
            else 0
        )

        # トレイナーレシオ
        treynor_ratio = (
            (aligned_returns.mean() * 252 - self.risk_free_rate) / beta
            if beta > 0
            else 0
        )

        return {
            "information_ratio": information_ratio,
            "treynor_ratio": treynor_ratio,
            "jensen_alpha": alpha,
            "beta": beta,
            "tracking_error": tracking_error,
        }

    def _calculate_variance_analysis(
        self, returns: pd.Series, benchmark_returns: Optional[pd.Series]
    ) -> Dict[str, float]:
        """分散分析"""
        if benchmark_returns is None:
            return {"systematic_risk": 0, "unsystematic_risk": 0, "r_squared": 0}

        # 共通期間でデータを揃える
        common_index = returns.index.intersection(benchmark_returns.index)
        if len(common_index) == 0:
            return {"systematic_risk": 0, "unsystematic_risk": 0, "r_squared": 0}

        aligned_returns = returns.loc[common_index]
        aligned_benchmark = benchmark_returns.loc[common_index]

        # 回帰分析
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            aligned_benchmark, aligned_returns
        )

        # 分散分解
        total_variance = np.var(aligned_returns)
        systematic_risk = (slope**2) * np.var(aligned_benchmark)
        unsystematic_risk = total_variance - systematic_risk

        return {
            "systematic_risk": systematic_risk,
            "unsystematic_risk": unsystematic_risk,
            "r_squared": r_value**2,
        }

    def _calculate_stress_test(
        self, returns: pd.Series, equity_curve: pd.Series
    ) -> Dict[str, float]:
        """ストレステスト"""
        # 月次リターン
        monthly_returns = equity_curve.resample("M").last().pct_change().dropna()
        worst_month = monthly_returns.min() if len(monthly_returns) > 0 else 0

        # 四半期リターン
        quarterly_returns = equity_curve.resample("Q").last().pct_change().dropna()
        worst_quarter = quarterly_returns.min() if len(quarterly_returns) > 0 else 0

        # 年次リターン
        yearly_returns = equity_curve.resample("Y").last().pct_change().dropna()
        worst_year = yearly_returns.min() if len(yearly_returns) > 0 else 0

        # 連続損失
        consecutive_losses = self._calculate_consecutive_losses(returns)

        # 回復時間
        recovery_time = self._calculate_recovery_time(equity_curve)

        return {
            "worst_month": worst_month,
            "worst_quarter": worst_quarter,
            "worst_year": worst_year,
            "consecutive_losses": consecutive_losses,
            "recovery_time": recovery_time,
        }

    def _calculate_consecutive_losses(self, returns: pd.Series) -> int:
        """連続損失計算"""
        negative_returns = returns < 0
        max_consecutive = 0
        current_consecutive = 0

        for is_negative in negative_returns:
            if is_negative:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def _calculate_recovery_time(self, equity_curve: pd.Series) -> int:
        """回復時間計算"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak

        max_dd_idx = drawdown.idxmin()
        recovery_idx = None

        for idx in equity_curve.index[equity_curve.index > max_dd_idx]:
            if equity_curve.loc[idx] >= peak.loc[max_dd_idx]:
                recovery_idx = idx
                break

        if recovery_idx:
            return (recovery_idx - max_dd_idx).days
        else:
            return len(equity_curve) - equity_curve.index.get_loc(max_dd_idx)

    def _calculate_performance_decomposition(
        self, returns: pd.Series, benchmark_returns: Optional[pd.Series]
    ) -> Dict[str, float]:
        """パフォーマンス分解"""
        if benchmark_returns is None:
            return {
                "alpha": 0,
                "beta_return": 0,
                "residual_return": 0,
                "market_timing": 0,
                "stock_selection": 0,
            }

        # 共通期間でデータを揃える
        common_index = returns.index.intersection(benchmark_returns.index)
        if len(common_index) == 0:
            return {
                "alpha": 0,
                "beta_return": 0,
                "residual_return": 0,
                "market_timing": 0,
                "stock_selection": 0,
            }

        aligned_returns = returns.loc[common_index]
        aligned_benchmark = benchmark_returns.loc[common_index]

        # 回帰分析
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            aligned_benchmark, aligned_returns
        )

        # パフォーマンス分解
        alpha = intercept
        beta_return = slope * aligned_benchmark.mean()
        residual_return = aligned_returns.mean() - alpha - beta_return

        # 市場タイミング効果（簡易版）
        market_timing = 0  # より複雑な計算が必要

        # 銘柄選択効果
        stock_selection = alpha + residual_return

        return {
            "alpha": alpha,
            "beta_return": beta_return,
            "residual_return": residual_return,
            "market_timing": market_timing,
            "stock_selection": stock_selection,
        }


class PerformanceVisualizer:
    """パフォーマンス可視化クラス"""

    def __init__(self):
        self.setup_style()

    def setup_style(self):
        """スタイル設定"""
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

    def plot_comprehensive_analysis(
        self,
        returns: pd.Series,
        equity_curve: pd.Series,
        metrics: AdvancedMetrics,
        save_path: str = None,
    ):
        """包括的分析プロット"""
        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        fig.suptitle("高度なパフォーマンス分析", fontsize=16, fontweight="bold")

        # 1. エクイティカーブ
        axes[0, 0].plot(
            equity_curve.index, equity_curve.values, linewidth=2, color="blue"
        )
        axes[0, 0].set_title("エクイティカーブ")
        axes[0, 0].set_ylabel("ポートフォリオ価値")
        axes[0, 0].grid(True, alpha=0.3)

        # 2. ドローダウン
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak * 100
        axes[0, 1].fill_between(equity_curve.index, drawdown, 0, alpha=0.7, color="red")
        axes[0, 1].set_title(f"ドローダウン (最大: {metrics.max_drawdown:.1%})")
        axes[0, 1].set_ylabel("ドローダウン (%)")
        axes[0, 1].grid(True, alpha=0.3)

        # 3. リターン分布
        axes[0, 2].hist(
            returns * 100, bins=30, alpha=0.7, color="skyblue", edgecolor="black"
        )
        axes[0, 2].axvline(
            returns.mean() * 100,
            color="red",
            linestyle="--",
            label=f"平均: {returns.mean()*100:.2f}%",
        )
        axes[0, 2].set_title("リターン分布")
        axes[0, 2].set_xlabel("リターン (%)")
        axes[0, 2].set_ylabel("頻度")
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)

        # 4. 累積リターン
        cumulative_returns = (1 + returns).cumprod() - 1
        axes[1, 0].plot(
            cumulative_returns.index,
            cumulative_returns.values * 100,
            linewidth=2,
            color="green",
        )
        axes[1, 0].set_title("累積リターン")
        axes[1, 0].set_ylabel("累積リターン (%)")
        axes[1, 0].grid(True, alpha=0.3)

        # 5. 月次リターン
        monthly_returns = equity_curve.resample("M").last().pct_change().dropna() * 100
        colors = ["green" if x > 0 else "red" for x in monthly_returns.values]
        axes[1, 1].bar(
            range(len(monthly_returns)), monthly_returns.values, color=colors, alpha=0.7
        )
        axes[1, 1].set_title("月次リターン")
        axes[1, 1].set_ylabel("リターン (%)")
        axes[1, 1].grid(True, alpha=0.3)

        # 6. リスク指標
        risk_metrics = ["VaR 95%", "VaR 99%", "CVaR 95%", "CVaR 99%"]
        risk_values = [
            metrics.var_95 * 100,
            metrics.var_99 * 100,
            metrics.cvar_95 * 100,
            metrics.cvar_99 * 100,
        ]
        bars = axes[1, 2].bar(
            risk_metrics, risk_values, color=["lightcoral", "red", "darkred", "maroon"]
        )
        axes[1, 2].set_title("リスク指標")
        axes[1, 2].set_ylabel("リターン (%)")
        axes[1, 2].tick_params(axis="x", rotation=45)
        for bar, value in zip(bars, risk_values):
            axes[1, 2].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{value:.2f}%",
                ha="center",
                va="bottom",
            )

        # 7. パフォーマンス指標
        perf_metrics = ["シャープ", "ソルティノ", "カルマー", "情報レシオ"]
        perf_values = [
            metrics.sharpe_ratio,
            metrics.sortino_ratio,
            metrics.calmar_ratio,
            metrics.information_ratio,
        ]
        bars = axes[2, 0].bar(
            perf_metrics,
            perf_values,
            color=["skyblue", "lightgreen", "orange", "purple"],
        )
        axes[2, 0].set_title("パフォーマンス指標")
        axes[2, 0].set_ylabel("レシオ")
        for bar, value in zip(bars, perf_values):
            axes[2, 0].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{value:.2f}",
                ha="center",
                va="bottom",
            )

        # 8. 統計指標
        stat_metrics = ["歪度", "尖度", "JB統計量", "JB p値"]
        stat_values = [
            metrics.skewness,
            metrics.kurtosis,
            metrics.jarque_bera_stat,
            metrics.jarque_bera_pvalue,
        ]
        bars = axes[2, 1].bar(
            stat_metrics,
            stat_values,
            color=["lightblue", "lightcoral", "lightgreen", "lightyellow"],
        )
        axes[2, 1].set_title("統計指標")
        axes[2, 1].set_ylabel("値")
        axes[2, 1].tick_params(axis="x", rotation=45)
        for bar, value in zip(bars, stat_values):
            axes[2, 1].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{value:.2f}",
                ha="center",
                va="bottom",
            )

        # 9. ストレステスト
        stress_metrics = ["最悪月", "最悪四半期", "最悪年", "連続損失", "回復時間"]
        stress_values = [
            metrics.worst_month * 100,
            metrics.worst_quarter * 100,
            metrics.worst_year * 100,
            metrics.consecutive_losses,
            metrics.recovery_time,
        ]
        bars = axes[2, 2].bar(
            stress_metrics,
            stress_values,
            color=["red", "darkred", "maroon", "orange", "yellow"],
        )
        axes[2, 2].set_title("ストレステスト")
        axes[2, 2].set_ylabel("値")
        axes[2, 2].tick_params(axis="x", rotation=45)
        for bar, value in zip(bars, stress_values):
            axes[2, 2].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{value:.1f}",
                ha="center",
                va="bottom",
            )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"包括的分析グラフを保存しました: {save_path}")

        plt.show()

    def plot_risk_analysis(
        self, returns: pd.Series, metrics: AdvancedMetrics, save_path: str = None
    ):
        """リスク分析プロット"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("リスク分析", fontsize=16, fontweight="bold")

        # 1. VaR分析
        axes[0, 0].hist(
            returns * 100, bins=50, alpha=0.7, color="skyblue", density=True
        )
        axes[0, 0].axvline(
            metrics.var_95 * 100,
            color="red",
            linestyle="--",
            label=f"VaR 95%: {metrics.var_95*100:.2f}%",
        )
        axes[0, 0].axvline(
            metrics.var_99 * 100,
            color="darkred",
            linestyle="--",
            label=f"VaR 99%: {metrics.var_99*100:.2f}%",
        )
        axes[0, 0].set_title("VaR分析")
        axes[0, 0].set_xlabel("リターン (%)")
        axes[0, 0].set_ylabel("密度")
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. テールリスク
        tail_returns = returns[returns <= metrics.var_95]
        axes[0, 1].hist(
            tail_returns * 100, bins=20, alpha=0.7, color="red", edgecolor="black"
        )
        axes[0, 1].axvline(
            metrics.cvar_95 * 100,
            color="darkred",
            linestyle="--",
            label=f"CVaR 95%: {metrics.cvar_95*100:.2f}%",
        )
        axes[0, 1].set_title("テールリスク分析")
        axes[0, 1].set_xlabel("リターン (%)")
        axes[0, 1].set_ylabel("頻度")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # 3. リスク指標比較
        risk_indicators = [
            "VaR 95%",
            "VaR 99%",
            "CVaR 95%",
            "CVaR 99%",
            "最大ドローダウン",
        ]
        risk_values = [
            abs(metrics.var_95) * 100,
            abs(metrics.var_99) * 100,
            abs(metrics.cvar_95) * 100,
            abs(metrics.cvar_99) * 100,
            metrics.max_drawdown * 100,
        ]
        bars = axes[1, 0].bar(
            risk_indicators,
            risk_values,
            color=["lightcoral", "red", "darkred", "maroon", "black"],
        )
        axes[1, 0].set_title("リスク指標比較")
        axes[1, 0].set_ylabel("リスク (%)")
        axes[1, 0].tick_params(axis="x", rotation=45)
        for bar, value in zip(bars, risk_values):
            axes[1, 0].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{value:.2f}%",
                ha="center",
                va="bottom",
            )

        # 4. リスク調整リターン
        risk_adjusted_metrics = [
            "シャープレシオ",
            "ソルティノレシオ",
            "カルマーレシオ",
            "情報レシオ",
        ]
        risk_adjusted_values = [
            metrics.sharpe_ratio,
            metrics.sortino_ratio,
            metrics.calmar_ratio,
            metrics.information_ratio,
        ]
        bars = axes[1, 1].bar(
            risk_adjusted_metrics,
            risk_adjusted_values,
            color=["skyblue", "lightgreen", "orange", "purple"],
        )
        axes[1, 1].set_title("リスク調整リターン")
        axes[1, 1].set_ylabel("レシオ")
        axes[1, 1].tick_params(axis="x", rotation=45)
        for bar, value in zip(bars, risk_adjusted_values):
            axes[1, 1].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{value:.2f}",
                ha="center",
                va="bottom",
            )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"リスク分析グラフを保存しました: {save_path}")

        plt.show()


def main():
    """メイン実行関数"""
    logger.info("=== 高度なパフォーマンス指標システム開始 ===")

    # サンプルデータ生成
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", "2023-12-31", freq="D")
    returns = np.random.normal(0.0005, 0.02, len(dates))  # 日次リターン
    equity_curve = pd.Series(1000000 * (1 + returns).cumprod(), index=dates)
    returns_series = pd.Series(returns, index=dates)

    # ベンチマークデータ（簡易版）
    benchmark_returns = np.random.normal(0.0003, 0.015, len(dates))
    benchmark_series = pd.Series(benchmark_returns, index=dates)

    # 高度な指標計算
    analyzer = AdvancedPerformanceAnalyzer(
        risk_free_rate=0.02, benchmark_returns=benchmark_series
    )
    metrics = analyzer.calculate_advanced_metrics(
        returns_series, equity_curve, benchmark_series
    )

    # 結果表示
    print("=" * 80)
    print("📊 高度なパフォーマンス指標")
    print("=" * 80)

    print(f"\n💰 基本指標:")
    print(f"  総リターン: {metrics.total_return:.2%}")
    print(f"  年率リターン: {metrics.annualized_return:.2%}")
    print(f"  ボラティリティ: {metrics.volatility:.2%}")
    print(f"  シャープレシオ: {metrics.sharpe_ratio:.2f}")
    print(f"  ソルティノレシオ: {metrics.sortino_ratio:.2f}")
    print(f"  カルマーレシオ: {metrics.calmar_ratio:.2f}")

    print(f"\n⚠️ リスク指標:")
    print(f"  最大ドローダウン: {metrics.max_drawdown:.2%}")
    print(f"  最大ドローダウン期間: {metrics.max_drawdown_duration}日")
    print(f"  VaR 95%: {metrics.var_95:.2%}")
    print(f"  VaR 99%: {metrics.var_99:.2%}")
    print(f"  CVaR 95%: {metrics.cvar_95:.2%}")
    print(f"  CVaR 99%: {metrics.cvar_99:.2%}")
    print(f"  テールレシオ: {metrics.tail_ratio:.2f}")

    print(f"\n📈 統計指標:")
    print(f"  歪度: {metrics.skewness:.2f}")
    print(f"  尖度: {metrics.kurtosis:.2f}")
    print(f"  Jarque-Bera統計量: {metrics.jarque_bera_stat:.2f}")
    print(f"  Jarque-Bera p値: {metrics.jarque_bera_pvalue:.4f}")

    print(f"\n🎯 リスク調整指標:")
    print(f"  情報レシオ: {metrics.information_ratio:.2f}")
    print(f"  トレイナーレシオ: {metrics.treynor_ratio:.2f}")
    print(f"  ジェンセンのアルファ: {metrics.jensen_alpha:.2%}")
    print(f"  ベータ: {metrics.beta:.2f}")
    print(f"  トラッキングエラー: {metrics.tracking_error:.2%}")

    print(f"\n📊 分散分析:")
    print(f"  システマティックリスク: {metrics.systematic_risk:.4f}")
    print(f"  アンシステマティックリスク: {metrics.unsystematic_risk:.4f}")
    print(f"  R²: {metrics.r_squared:.2%}")

    print(f"\n🔥 ストレステスト:")
    print(f"  最悪月: {metrics.worst_month:.2%}")
    print(f"  最悪四半期: {metrics.worst_quarter:.2%}")
    print(f"  最悪年: {metrics.worst_year:.2%}")
    print(f"  連続損失: {metrics.consecutive_losses}日")
    print(f"  回復時間: {metrics.recovery_time}日")

    print(f"\n🔍 パフォーマンス分解:")
    print(f"  アルファ: {metrics.alpha:.2%}")
    print(f"  ベータリターン: {metrics.beta_return:.2%}")
    print(f"  残差リターン: {metrics.residual_return:.2%}")
    print(f"  市場タイミング: {metrics.market_timing:.2%}")
    print(f"  銘柄選択: {metrics.stock_selection:.2%}")

    # 可視化
    visualizer = PerformanceVisualizer()
    visualizer.plot_comprehensive_analysis(
        returns_series, equity_curve, metrics, "advanced_performance_analysis.png"
    )
    visualizer.plot_risk_analysis(returns_series, metrics, "risk_analysis.png")

    # 結果保存
    metrics_dict = asdict(metrics)
    with open("advanced_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_dict, f, ensure_ascii=False, indent=2, default=str)

    logger.info("=== 高度なパフォーマンス指標計算完了 ===")


if __name__ == "__main__":
    main()
