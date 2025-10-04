#!/usr/bin/env python3
"""
高度なリスクメトリクス計算システム

目的: VaR・最大ドローダウン・シャープレシオの高精度計算
仕様: リアルタイムリスク監視と自動損切り対応
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class RiskMetricType(Enum):
    """リスクメトリクス種別"""
    VAR = "var"
    CVAR = "cvar"
    MAX_DRAWDOWN = "max_drawdown"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    CALMAR_RATIO = "calmar_ratio"
    INFORMATION_RATIO = "information_ratio"
    TREYNOR_RATIO = "treynor_ratio"
    JENSEN_ALPHA = "jensen_alpha"
    BETA = "beta"
    CORRELATION = "correlation"
    VOLATILITY = "volatility"
    SKEWNESS = "skewness"
    KURTOSIS = "kurtosis"


@dataclass
class RiskMetricsResult:
    """リスクメトリクス結果"""
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    information_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    beta: float
    correlation: float
    volatility: float
    skewness: float
    kurtosis: float
    risk_score: float
    confidence_level: float


@dataclass
class PortfolioRiskProfile:
    """ポートフォリオリスクプロファイル"""
    total_value: float
    total_risk: float
    risk_per_position: Dict[str, float]
    correlation_matrix: pd.DataFrame
    risk_contribution: Dict[str, float]
    diversification_ratio: float
    concentration_risk: float
    liquidity_risk: float


class AdvancedRiskMetrics:
    """高度なリスクメトリクス計算システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.risk_history = []
        self.market_data_cache = {}
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "var": {
                "confidence_levels": [0.95, 0.99],
                "method": "historical",  # historical, parametric, monte_carlo
                "lookback_period": 252,  # 1年
                "min_observations": 30
            },
            "drawdown": {
                "method": "rolling",  # rolling, peak_to_trough
                "window": 252,
                "min_periods": 30
            },
            "ratios": {
                "risk_free_rate": 0.02,  # 2%
                "benchmark_return": 0.08,  # 8%
                "annualization_factor": 252
            },
            "volatility": {
                "method": "garch",  # simple, ewma, garch
                "window": 20,
                "decay_factor": 0.94
            },
            "correlation": {
                "method": "pearson",  # pearson, spearman, kendall
                "min_periods": 30,
                "rolling_window": 60
            }
        }
    
    def calculate_comprehensive_risk_metrics(
        self,
        portfolio_data: pd.DataFrame,
        market_data: pd.DataFrame,
        benchmark_data: Optional[pd.DataFrame] = None,
        risk_free_rate: float = 0.02
    ) -> RiskMetricsResult:
        """包括的リスクメトリクス計算"""
        try:
            # データ検証
            if portfolio_data.empty:
                return self._get_default_risk_metrics()
            
            # リターン計算
            returns = self._calculate_returns(portfolio_data)
            if returns.empty:
                return self._get_default_risk_metrics()
            
            # VaR計算
            var_95 = self._calculate_var(returns, 0.95)
            var_99 = self._calculate_var(returns, 0.99)
            
            # CVaR計算
            cvar_95 = self._calculate_cvar(returns, 0.95)
            cvar_99 = self._calculate_cvar(returns, 0.99)
            
            # 最大ドローダウン計算
            max_drawdown = self._calculate_max_drawdown(portfolio_data)
            
            # シャープレシオ計算
            sharpe_ratio = self._calculate_sharpe_ratio(returns, risk_free_rate)
            
            # ソルティノレシオ計算
            sortino_ratio = self._calculate_sortino_ratio(returns, risk_free_rate)
            
            # カルマーレシオ計算
            calmar_ratio = self._calculate_calmar_ratio(returns, max_drawdown)
            
            # 情報レシオ計算
            information_ratio = self._calculate_information_ratio(returns, benchmark_data)
            
            # トレイノーレシオ計算
            treynor_ratio = self._calculate_treynor_ratio(returns, market_data, risk_free_rate)
            
            # ジェンセンのアルファ計算
            jensen_alpha = self._calculate_jensen_alpha(returns, market_data, risk_free_rate)
            
            # ベータ計算
            beta = self._calculate_beta(returns, market_data)
            
            # 相関計算
            correlation = self._calculate_correlation(returns, market_data)
            
            # ボラティリティ計算
            volatility = self._calculate_volatility(returns)
            
            # 歪度計算
            skewness = self._calculate_skewness(returns)
            
            # 尖度計算
            kurtosis = self._calculate_kurtosis(returns)
            
            # リスクスコア計算
            risk_score = self._calculate_comprehensive_risk_score(
                var_95, max_drawdown, volatility, sharpe_ratio, skewness, kurtosis
            )
            
            # 信頼度計算
            confidence_level = self._calculate_confidence_level(
                var_95, max_drawdown, volatility, sharpe_ratio
            )
            
            result = RiskMetricsResult(
                var_95=var_95,
                var_99=var_99,
                cvar_95=cvar_95,
                cvar_99=cvar_99,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                information_ratio=information_ratio,
                treynor_ratio=treynor_ratio,
                jensen_alpha=jensen_alpha,
                beta=beta,
                correlation=correlation,
                volatility=volatility,
                skewness=skewness,
                kurtosis=kurtosis,
                risk_score=risk_score,
                confidence_level=confidence_level
            )
            
            # 履歴に追加
            self.risk_history.append(result)
            if len(self.risk_history) > 1000:
                self.risk_history.pop(0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"包括的リスクメトリクス計算エラー: {e}")
            return self._get_default_risk_metrics()
    
    def calculate_portfolio_risk_profile(
        self,
        positions: Dict[str, Dict[str, Any]],
        market_data: Dict[str, pd.DataFrame],
        correlation_data: Optional[pd.DataFrame] = None
    ) -> PortfolioRiskProfile:
        """ポートフォリオリスクプロファイル計算"""
        try:
            # 総価値計算
            total_value = sum(pos.get('value', 0) for pos in positions.values())
            
            if total_value == 0:
                return self._get_default_portfolio_risk_profile()
            
            # 個別リスク計算
            risk_per_position = {}
            for symbol, position in positions.items():
                if symbol in market_data:
                    returns = market_data[symbol]['Close'].pct_change().dropna()
                    if not returns.empty:
                        risk_per_position[symbol] = returns.std() * np.sqrt(252)
                    else:
                        risk_per_position[symbol] = 0.0
                else:
                    risk_per_position[symbol] = 0.0
            
            # 相関行列計算
            correlation_matrix = self._calculate_correlation_matrix(
                positions, market_data, correlation_data
            )
            
            # リスク寄与度計算
            risk_contribution = self._calculate_risk_contribution(
                positions, risk_per_position, correlation_matrix
            )
            
            # 総リスク計算
            total_risk = self._calculate_portfolio_total_risk(
                positions, risk_per_position, correlation_matrix
            )
            
            # 分散投資比率計算
            diversification_ratio = self._calculate_diversification_ratio(
                risk_per_position, total_risk
            )
            
            # 集中度リスク計算
            concentration_risk = self._calculate_concentration_risk(positions)
            
            # 流動性リスク計算
            liquidity_risk = self._calculate_liquidity_risk(positions, market_data)
            
            return PortfolioRiskProfile(
                total_value=total_value,
                total_risk=total_risk,
                risk_per_position=risk_per_position,
                correlation_matrix=correlation_matrix,
                risk_contribution=risk_contribution,
                diversification_ratio=diversification_ratio,
                concentration_risk=concentration_risk,
                liquidity_risk=liquidity_risk
            )
            
        except Exception as e:
            self.logger.error(f"ポートフォリオリスクプロファイル計算エラー: {e}")
            return self._get_default_portfolio_risk_profile()
    
    def calculate_rolling_risk_metrics(
        self,
        portfolio_data: pd.DataFrame,
        window: int = 252,
        min_periods: int = 30
    ) -> pd.DataFrame:
        """ローリングリスクメトリクス計算"""
        try:
            if portfolio_data.empty:
                return pd.DataFrame()
            
            # リターン計算
            returns = portfolio_data['value'].pct_change().dropna()
            
            if returns.empty:
                return pd.DataFrame()
            
            # ローリング計算
            rolling_metrics = pd.DataFrame(index=returns.index)
            
            # ローリングVaR
            rolling_metrics['var_95'] = returns.rolling(
                window=window, min_periods=min_periods
            ).apply(lambda x: self._calculate_var(x, 0.95))
            
            # ローリング最大ドローダウン
            rolling_metrics['max_drawdown'] = portfolio_data['value'].rolling(
                window=window, min_periods=min_periods
            ).apply(lambda x: self._calculate_max_drawdown_series(x))
            
            # ローリングシャープレシオ
            rolling_metrics['sharpe_ratio'] = returns.rolling(
                window=window, min_periods=min_periods
            ).apply(lambda x: self._calculate_sharpe_ratio(x, 0.02))
            
            # ローリングボラティリティ
            rolling_metrics['volatility'] = returns.rolling(
                window=window, min_periods=min_periods
            ).std() * np.sqrt(252)
            
            # ローリング歪度
            rolling_metrics['skewness'] = returns.rolling(
                window=window, min_periods=min_periods
            ).skew()
            
            # ローリング尖度
            rolling_metrics['kurtosis'] = returns.rolling(
                window=window, min_periods=min_periods
            ).kurt()
            
            return rolling_metrics.dropna()
            
        except Exception as e:
            self.logger.error(f"ローリングリスクメトリクス計算エラー: {e}")
            return pd.DataFrame()
    
    def calculate_stress_test_metrics(
        self,
        portfolio_data: pd.DataFrame,
        stress_scenarios: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """ストレステストメトリクス計算"""
        try:
            if portfolio_data.empty:
                return {}
            
            stress_results = {}
            
            for i, scenario in enumerate(stress_scenarios):
                scenario_name = scenario.get('name', f'scenario_{i+1}')
                
                # シナリオ適用
                stressed_returns = self._apply_stress_scenario(
                    portfolio_data, scenario
                )
                
                if stressed_returns.empty:
                    continue
                
                # ストレス下でのリスクメトリクス計算
                stress_var = self._calculate_var(stressed_returns, 0.95)
                stress_drawdown = self._calculate_max_drawdown_series(stressed_returns)
                stress_volatility = stressed_returns.std() * np.sqrt(252)
                
                stress_results[scenario_name] = {
                    'var_95': stress_var,
                    'max_drawdown': stress_drawdown,
                    'volatility': stress_volatility,
                    'scenario': scenario
                }
            
            return stress_results
            
        except Exception as e:
            self.logger.error(f"ストレステストメトリクス計算エラー: {e}")
            return {}
    
    def calculate_risk_budget(
        self,
        portfolio_data: pd.DataFrame,
        target_risk: float = 0.10,
        max_position_risk: float = 0.05
    ) -> Dict[str, Any]:
        """リスクバジェット計算"""
        try:
            if portfolio_data.empty:
                return {}
            
            # リターン計算
            returns = portfolio_data['value'].pct_change().dropna()
            
            if returns.empty:
                return {}
            
            # 現在のリスク計算
            current_risk = returns.std() * np.sqrt(252)
            
            # リスクバジェット比率
            risk_budget_ratio = target_risk / current_risk if current_risk > 0 else 1.0
            
            # ポジション制限計算
            position_limit = min(max_position_risk, target_risk / len(portfolio_data.columns))
            
            # リスク調整係数
            risk_adjustment_factor = min(1.0, risk_budget_ratio)
            
            return {
                'current_risk': current_risk,
                'target_risk': target_risk,
                'risk_budget_ratio': risk_budget_ratio,
                'position_limit': position_limit,
                'risk_adjustment_factor': risk_adjustment_factor,
                'recommendations': self._generate_risk_recommendations(
                    current_risk, target_risk, risk_budget_ratio
                )
            }
            
        except Exception as e:
            self.logger.error(f"リスクバジェット計算エラー: {e}")
            return {}
    
    # ヘルパーメソッド群
    def _calculate_returns(self, data: pd.DataFrame) -> pd.Series:
        """リターン計算"""
        try:
            if 'value' in data.columns:
                return data['value'].pct_change().dropna()
            elif 'Close' in data.columns:
                return data['Close'].pct_change().dropna()
            else:
                # 最初の数値カラムを使用
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    return data[numeric_cols[0]].pct_change().dropna()
                else:
                    return pd.Series(dtype=float)
        except:
            return pd.Series(dtype=float)
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """VaR計算"""
        try:
            if returns.empty:
                return 0.0
            
            method = self.config["var"]["method"]
            
            if method == "historical":
                return self._calculate_historical_var(returns, confidence_level)
            elif method == "parametric":
                return self._calculate_parametric_var(returns, confidence_level)
            elif method == "monte_carlo":
                return self._calculate_monte_carlo_var(returns, confidence_level)
            else:
                return self._calculate_historical_var(returns, confidence_level)
                
        except Exception as e:
            self.logger.error(f"VaR計算エラー: {e}")
            return 0.0
    
    def _calculate_historical_var(self, returns: pd.Series, confidence_level: float) -> float:
        """ヒストリカルVaR計算"""
        try:
            return np.percentile(returns, (1 - confidence_level) * 100)
        except:
            return 0.0
    
    def _calculate_parametric_var(self, returns: pd.Series, confidence_level: float) -> float:
        """パラメトリックVaR計算"""
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            z_score = stats.norm.ppf(1 - confidence_level)
            return mean_return + z_score * std_return
        except:
            return 0.0
    
    def _calculate_monte_carlo_var(self, returns: pd.Series, confidence_level: float) -> float:
        """モンテカルロVaR計算"""
        try:
            # 簡易的なモンテカルロシミュレーション
            n_simulations = 10000
            mean_return = returns.mean()
            std_return = returns.std()
            
            simulated_returns = np.random.normal(mean_return, std_return, n_simulations)
            return np.percentile(simulated_returns, (1 - confidence_level) * 100)
        except:
            return 0.0
    
    def _calculate_cvar(self, returns: pd.Series, confidence_level: float) -> float:
        """CVaR計算"""
        try:
            var_threshold = self._calculate_var(returns, confidence_level)
            tail_returns = returns[returns <= var_threshold]
            
            if tail_returns.empty:
                return var_threshold
            
            return tail_returns.mean()
        except:
            return 0.0
    
    def _calculate_max_drawdown(self, data: pd.DataFrame) -> float:
        """最大ドローダウン計算"""
        try:
            if 'value' in data.columns:
                values = data['value']
            elif 'Close' in data.columns:
                values = data['Close']
            else:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    values = data[numeric_cols[0]]
                else:
                    return 0.0
            
            if values.empty:
                return 0.0
            
            return self._calculate_max_drawdown_series(values)
        except:
            return 0.0
    
    def _calculate_max_drawdown_series(self, values: pd.Series) -> float:
        """シリーズの最大ドローダウン計算"""
        try:
            if values.empty:
                return 0.0
            
            peak = values.expanding().max()
            drawdown = (values - peak) / peak
            return abs(drawdown.min())
        except:
            return 0.0
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """シャープレシオ計算"""
        try:
            if returns.empty:
                return 0.0
            
            excess_returns = returns.mean() - risk_free_rate / 252
            return excess_returns / returns.std() * np.sqrt(252) if returns.std() > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """ソルティノレシオ計算"""
        try:
            if returns.empty:
                return 0.0
            
            excess_returns = returns.mean() - risk_free_rate / 252
            downside_returns = returns[returns < 0]
            
            if downside_returns.empty:
                return 0.0
            
            downside_std = downside_returns.std()
            return excess_returns / downside_std * np.sqrt(252) if downside_std > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_calmar_ratio(self, returns: pd.Series, max_drawdown: float) -> float:
        """カルマーレシオ計算"""
        try:
            if returns.empty or max_drawdown == 0:
                return 0.0
            
            annual_return = returns.mean() * 252
            return annual_return / max_drawdown
        except:
            return 0.0
    
    def _calculate_information_ratio(
        self, returns: pd.Series, benchmark_data: Optional[pd.DataFrame]
    ) -> float:
        """情報レシオ計算"""
        try:
            if returns.empty or benchmark_data is None or benchmark_data.empty:
                return 0.0
            
            benchmark_returns = benchmark_data['Close'].pct_change().dropna()
            
            if benchmark_returns.empty:
                return 0.0
            
            # 共通の期間でデータを合わせる
            common_index = returns.index.intersection(benchmark_returns.index)
            if len(common_index) < 2:
                return 0.0
            
            returns_aligned = returns.loc[common_index]
            benchmark_returns_aligned = benchmark_returns.loc[common_index]
            
            active_returns = returns_aligned - benchmark_returns_aligned
            tracking_error = active_returns.std()
            
            return active_returns.mean() / tracking_error if tracking_error > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_treynor_ratio(
        self, returns: pd.Series, market_data: pd.DataFrame, risk_free_rate: float
    ) -> float:
        """トレイノーレシオ計算"""
        try:
            if returns.empty or market_data.empty:
                return 0.0
            
            beta = self._calculate_beta(returns, market_data)
            if beta == 0:
                return 0.0
            
            excess_returns = returns.mean() - risk_free_rate / 252
            return excess_returns / beta
        except:
            return 0.0
    
    def _calculate_jensen_alpha(
        self, returns: pd.Series, market_data: pd.DataFrame, risk_free_rate: float
    ) -> float:
        """ジェンセンのアルファ計算"""
        try:
            if returns.empty or market_data.empty:
                return 0.0
            
            market_returns = market_data['Close'].pct_change().dropna()
            
            if market_returns.empty:
                return 0.0
            
            # 共通の期間でデータを合わせる
            common_index = returns.index.intersection(market_returns.index)
            if len(common_index) < 2:
                return 0.0
            
            returns_aligned = returns.loc[common_index]
            market_returns_aligned = market_returns.loc[common_index]
            
            # 線形回帰でアルファとベータを計算
            X = market_returns_aligned.values.reshape(-1, 1)
            y = returns_aligned.values
            
            # リスクフリーレートを差し引く
            risk_free_daily = risk_free_rate / 252
            y_excess = y - risk_free_daily
            X_excess = X - risk_free_daily
            
            # 回帰分析
            slope, intercept = np.polyfit(X_excess.flatten(), y_excess, 1)
            
            return intercept
        except:
            return 0.0
    
    def _calculate_beta(self, returns: pd.Series, market_data: pd.DataFrame) -> float:
        """ベータ計算"""
        try:
            if returns.empty or market_data.empty:
                return 1.0
            
            market_returns = market_data['Close'].pct_change().dropna()
            
            if market_returns.empty:
                return 1.0
            
            # 共通の期間でデータを合わせる
            common_index = returns.index.intersection(market_returns.index)
            if len(common_index) < 2:
                return 1.0
            
            returns_aligned = returns.loc[common_index]
            market_returns_aligned = market_returns.loc[common_index]
            
            covariance = np.cov(returns_aligned, market_returns_aligned)[0, 1]
            market_variance = np.var(market_returns_aligned)
            
            return covariance / market_variance if market_variance > 0 else 1.0
        except:
            return 1.0
    
    def _calculate_correlation(self, returns: pd.Series, market_data: pd.DataFrame) -> float:
        """相関計算"""
        try:
            if returns.empty or market_data.empty:
                return 0.0
            
            market_returns = market_data['Close'].pct_change().dropna()
            
            if market_returns.empty:
                return 0.0
            
            # 共通の期間でデータを合わせる
            common_index = returns.index.intersection(market_returns.index)
            if len(common_index) < 2:
                return 0.0
            
            returns_aligned = returns.loc[common_index]
            market_returns_aligned = market_returns.loc[common_index]
            
            correlation = returns_aligned.corr(market_returns_aligned)
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _calculate_volatility(self, returns: pd.Series) -> float:
        """ボラティリティ計算"""
        try:
            if returns.empty:
                return 0.0
            
            method = self.config["volatility"]["method"]
            
            if method == "simple":
                return returns.std() * np.sqrt(252)
            elif method == "ewma":
                return self._calculate_ewma_volatility(returns)
            elif method == "garch":
                return self._calculate_garch_volatility(returns)
            else:
                return returns.std() * np.sqrt(252)
        except:
            return 0.0
    
    def _calculate_ewma_volatility(self, returns: pd.Series) -> float:
        """EWMAボラティリティ計算"""
        try:
            if returns.empty:
                return 0.0
            
            decay_factor = self.config["volatility"]["decay_factor"]
            window = self.config["volatility"]["window"]
            
            # 簡易的なEWMA計算
            weights = np.array([decay_factor ** i for i in range(window)])
            weights = weights / weights.sum()
            
            if len(returns) < window:
                return returns.std() * np.sqrt(252)
            
            recent_returns = returns.tail(window)
            ewma_variance = np.average(recent_returns ** 2, weights=weights)
            
            return np.sqrt(ewma_variance * 252)
        except:
            return returns.std() * np.sqrt(252)
    
    def _calculate_garch_volatility(self, returns: pd.Series) -> float:
        """GARCHボラティリティ計算"""
        try:
            if returns.empty:
                return 0.0
            
            # 簡易的なGARCH(1,1)モデル
            # 実際の実装では、より高度なGARCHライブラリを使用
            return returns.std() * np.sqrt(252)
        except:
            return returns.std() * np.sqrt(252)
    
    def _calculate_skewness(self, returns: pd.Series) -> float:
        """歪度計算"""
        try:
            if returns.empty:
                return 0.0
            
            return returns.skew()
        except:
            return 0.0
    
    def _calculate_kurtosis(self, returns: pd.Series) -> float:
        """尖度計算"""
        try:
            if returns.empty:
                return 0.0
            
            return returns.kurt()
        except:
            return 0.0
    
    def _calculate_comprehensive_risk_score(
        self,
        var_95: float,
        max_drawdown: float,
        volatility: float,
        sharpe_ratio: float,
        skewness: float,
        kurtosis: float
    ) -> float:
        """包括的リスクスコア計算"""
        try:
            # 各指標の重み
            weights = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
            
            # 正規化されたスコア
            var_score = min(1.0, abs(var_95) / 0.1)  # 10%を上限とする
            drawdown_score = min(1.0, max_drawdown / 0.2)  # 20%を上限とする
            volatility_score = min(1.0, volatility / 0.5)  # 50%を上限とする
            sharpe_score = max(0.0, min(1.0, sharpe_ratio / 2.0))  # 2.0を上限とする
            skewness_score = min(1.0, abs(skewness) / 2.0)  # 2.0を上限とする
            kurtosis_score = min(1.0, abs(kurtosis) / 5.0)  # 5.0を上限とする
            
            scores = [var_score, drawdown_score, volatility_score, sharpe_score, skewness_score, kurtosis_score]
            
            risk_score = sum(w * s for w, s in zip(weights, scores))
            
            return max(0.0, min(1.0, risk_score))
        except:
            return 0.5
    
    def _calculate_confidence_level(
        self,
        var_95: float,
        max_drawdown: float,
        volatility: float,
        sharpe_ratio: float
    ) -> float:
        """信頼度計算"""
        try:
            # リスク指標の重み
            weights = [0.3, 0.3, 0.2, 0.2]
            
            # 正規化された信頼度
            var_confidence = max(0.0, 1.0 - abs(var_95) / 0.05)  # 5%を基準
            drawdown_confidence = max(0.0, 1.0 - max_drawdown / 0.1)  # 10%を基準
            volatility_confidence = max(0.0, 1.0 - volatility / 0.3)  # 30%を基準
            sharpe_confidence = max(0.0, min(1.0, sharpe_ratio / 1.0))  # 1.0を基準
            
            confidences = [var_confidence, drawdown_confidence, volatility_confidence, sharpe_confidence]
            
            confidence_level = sum(w * c for w, c in zip(weights, confidences))
            
            return max(0.0, min(1.0, confidence_level))
        except:
            return 0.5
    
    def _calculate_correlation_matrix(
        self,
        positions: Dict[str, Dict[str, Any]],
        market_data: Dict[str, pd.DataFrame],
        correlation_data: Optional[pd.DataFrame]
    ) -> pd.DataFrame:
        """相関行列計算"""
        try:
            if correlation_data is not None:
                return correlation_data
            
            # 各ポジションのリターン計算
            returns_data = {}
            for symbol, position in positions.items():
                if symbol in market_data:
                    returns = market_data[symbol]['Close'].pct_change().dropna()
                    if not returns.empty:
                        returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return pd.DataFrame()
            
            # 相関行列計算
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            return correlation_matrix
        except:
            return pd.DataFrame()
    
    def _calculate_risk_contribution(
        self,
        positions: Dict[str, Dict[str, Any]],
        risk_per_position: Dict[str, float],
        correlation_matrix: pd.DataFrame
    ) -> Dict[str, float]:
        """リスク寄与度計算"""
        try:
            if not risk_per_position or correlation_matrix.empty:
                return {}
            
            # 各ポジションの重み計算
            total_value = sum(pos.get('value', 0) for pos in positions.values())
            if total_value == 0:
                return {}
            
            weights = {symbol: pos.get('value', 0) / total_value for symbol, pos in positions.items()}
            
            # リスク寄与度計算
            risk_contribution = {}
            for symbol, weight in weights.items():
                if symbol in risk_per_position:
                    risk_contribution[symbol] = weight * risk_per_position[symbol]
                else:
                    risk_contribution[symbol] = 0.0
            
            return risk_contribution
        except:
            return {}
    
    def _calculate_portfolio_total_risk(
        self,
        positions: Dict[str, Dict[str, Any]],
        risk_per_position: Dict[str, float],
        correlation_matrix: pd.DataFrame
    ) -> float:
        """ポートフォリオ総リスク計算"""
        try:
            if not risk_per_position or correlation_matrix.empty:
                return 0.0
            
            # 各ポジションの重み計算
            total_value = sum(pos.get('value', 0) for pos in positions.values())
            if total_value == 0:
                return 0.0
            
            weights = {symbol: pos.get('value', 0) / total_value for symbol, pos in positions.items()}
            
            # ポートフォリオ分散計算
            portfolio_variance = 0.0
            for symbol1, weight1 in weights.items():
                for symbol2, weight2 in weights.items():
                    if symbol1 in risk_per_position and symbol2 in risk_per_position:
                        if symbol1 == symbol2:
                            portfolio_variance += weight1 * weight2 * (risk_per_position[symbol1] ** 2)
                        else:
                            correlation = correlation_matrix.loc[symbol1, symbol2] if symbol1 in correlation_matrix.index and symbol2 in correlation_matrix.columns else 0.0
                            portfolio_variance += weight1 * weight2 * risk_per_position[symbol1] * risk_per_position[symbol2] * correlation
            
            return np.sqrt(portfolio_variance)
        except:
            return 0.0
    
    def _calculate_diversification_ratio(
        self, risk_per_position: Dict[str, float], total_risk: float
    ) -> float:
        """分散投資比率計算"""
        try:
            if not risk_per_position or total_risk == 0:
                return 0.0
            
            # 重み付き平均リスク
            weighted_avg_risk = np.mean(list(risk_per_position.values()))
            
            return weighted_avg_risk / total_risk if total_risk > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_concentration_risk(self, positions: Dict[str, Dict[str, Any]]) -> float:
        """集中度リスク計算"""
        try:
            if not positions:
                return 0.0
            
            # 各ポジションの価値
            values = [pos.get('value', 0) for pos in positions.values()]
            total_value = sum(values)
            
            if total_value == 0:
                return 0.0
            
            # 重み計算
            weights = [v / total_value for v in values]
            
            # ハーフィンダール指数（集中度指標）
            hhi = sum(w ** 2 for w in weights)
            
            return hhi
        except:
            return 0.0
    
    def _calculate_liquidity_risk(
        self, positions: Dict[str, Dict[str, Any]], market_data: Dict[str, pd.DataFrame]
    ) -> float:
        """流動性リスク計算"""
        try:
            if not positions or not market_data:
                return 0.0
            
            liquidity_scores = []
            
            for symbol, position in positions.items():
                if symbol in market_data:
                    # ボリュームデータを使用した流動性評価
                    volume_data = market_data[symbol].get('Volume', pd.Series())
                    if not volume_data.empty:
                        avg_volume = volume_data.mean()
                        liquidity_score = min(1.0, avg_volume / 1000000)  # 100万を上限とする
                        liquidity_scores.append(liquidity_score)
                    else:
                        liquidity_scores.append(0.5)  # デフォルト値
                else:
                    liquidity_scores.append(0.5)  # デフォルト値
            
            return np.mean(liquidity_scores) if liquidity_scores else 0.0
        except:
            return 0.0
    
    def _apply_stress_scenario(
        self, portfolio_data: pd.DataFrame, scenario: Dict[str, float]
    ) -> pd.Series:
        """ストレスシナリオ適用"""
        try:
            if portfolio_data.empty:
                return pd.Series(dtype=float)
            
            # リターン計算
            returns = portfolio_data['value'].pct_change().dropna()
            
            if returns.empty:
                return pd.Series(dtype=float)
            
            # シナリオ適用
            stress_factor = scenario.get('stress_factor', 1.0)
            stressed_returns = returns * stress_factor
            
            return stressed_returns
        except:
            return pd.Series(dtype=float)
    
    def _generate_risk_recommendations(
        self, current_risk: float, target_risk: float, risk_budget_ratio: float
    ) -> List[str]:
        """リスク推奨事項生成"""
        recommendations = []
        
        if current_risk > target_risk:
            recommendations.append("リスクを削減することを推奨します")
            if risk_budget_ratio < 0.8:
                recommendations.append("ポジションサイズを縮小してください")
        elif current_risk < target_risk * 0.8:
            recommendations.append("リスクを増加させる余地があります")
            recommendations.append("新規ポジションの検討を推奨します")
        else:
            recommendations.append("現在のリスクレベルは適切です")
        
        return recommendations
    
    def _get_default_risk_metrics(self) -> RiskMetricsResult:
        """デフォルトリスクメトリクス"""
        return RiskMetricsResult(
            var_95=0.0,
            var_99=0.0,
            cvar_95=0.0,
            cvar_99=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            information_ratio=0.0,
            treynor_ratio=0.0,
            jensen_alpha=0.0,
            beta=1.0,
            correlation=0.0,
            volatility=0.0,
            skewness=0.0,
            kurtosis=0.0,
            risk_score=0.5,
            confidence_level=0.5
        )
    
    def _get_default_portfolio_risk_profile(self) -> PortfolioRiskProfile:
        """デフォルトポートフォリオリスクプロファイル"""
        return PortfolioRiskProfile(
            total_value=0.0,
            total_risk=0.0,
            risk_per_position={},
            correlation_matrix=pd.DataFrame(),
            risk_contribution={},
            diversification_ratio=0.0,
            concentration_risk=0.0,
            liquidity_risk=0.0
        )
