#!/usr/bin/env python3
"""
個別銘柄バックテストの詳細化システム
期待効果: 投資戦略の精度向上
実装難易度: 🟡 中
推定工数: 3-4日

機能:
1. 個別銘柄の過去データでの戦略検証
2. 個別銘柄の季節性・周期性分析
3. 個別銘柄の業績発表前後のパフォーマンス分析
4. 個別銘柄の技術指標最適化
5. 複数銘柄の比較分析
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
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import ParameterGrid
import talib

# 既存システムのインポート
from advanced_backtest_system import (
    BacktestEngine,
    MomentumStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
    BacktestResult,
    BaseStrategy,
)
from advanced_performance_metrics import AdvancedPerformanceAnalyzer

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("individual_backtest.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class SeasonalAnalysis:
    """季節性分析結果"""
    
    monthly_returns: Dict[int, float]
    quarterly_returns: Dict[int, float]
    seasonal_patterns: Dict[str, Any]
    statistical_significance: Dict[str, float]
    best_months: List[int]
    worst_months: List[int]


@dataclass
class EarningsAnalysis:
    """業績発表分析結果"""
    
    pre_earnings_returns: Dict[str, float]
    post_earnings_returns: Dict[str, float]
    earnings_volatility: Dict[str, float]
    surprise_impact: Dict[str, float]
    trading_volume_changes: Dict[str, float]


@dataclass
class TechnicalOptimization:
    """技術指標最適化結果"""
    
    optimal_parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    parameter_sensitivity: Dict[str, float]
    optimization_history: List[Dict[str, Any]]


@dataclass
class IndividualStockResult:
    """個別銘柄分析結果"""
    
    symbol: str
    analysis_period: Tuple[datetime, datetime]
    
    # 基本分析
    basic_metrics: Dict[str, float]
    
    # 季節性分析
    seasonal_analysis: SeasonalAnalysis
    
    # 業績発表分析
    earnings_analysis: EarningsAnalysis
    
    # 技術指標最適化
    technical_optimization: TechnicalOptimization
    
    # 戦略バックテスト結果
    strategy_results: Dict[str, BacktestResult]
    
    # 比較分析
    comparison_metrics: Dict[str, Any]


class SeasonalAnalyzer:
    """季節性分析クラス"""
    
    def __init__(self):
        self.analyzer = AdvancedPerformanceAnalyzer()
    
    def analyze_seasonality(self, data: pd.DataFrame, symbol: str) -> SeasonalAnalysis:
        """季節性分析実行"""
        logger.info(f"季節性分析開始: {symbol}")
        
        # 月次リターン計算
        monthly_returns = self._calculate_monthly_returns(data)
        
        # 四半期リターン計算
        quarterly_returns = self._calculate_quarterly_returns(data)
        
        # 季節パターン分析
        seasonal_patterns = self._analyze_seasonal_patterns(monthly_returns)
        
        # 統計的有意性検定
        statistical_significance = self._test_statistical_significance(monthly_returns)
        
        # 最良・最悪月の特定
        best_months, worst_months = self._identify_best_worst_months(monthly_returns)
        
        return SeasonalAnalysis(
            monthly_returns=monthly_returns,
            quarterly_returns=quarterly_returns,
            seasonal_patterns=seasonal_patterns,
            statistical_significance=statistical_significance,
            best_months=best_months,
            worst_months=worst_months
        )
    
    def _calculate_monthly_returns(self, data: pd.DataFrame) -> Dict[int, float]:
        """月次リターン計算"""
        monthly_data = data.resample('M').last()
        monthly_returns = {}
        
        for month in range(1, 13):
            month_data = monthly_data[monthly_data.index.month == month]
            if len(month_data) > 1:
                returns = month_data['Close'].pct_change().dropna()
                monthly_returns[month] = returns.mean()
            else:
                monthly_returns[month] = 0.0
        
        return monthly_returns
    
    def _calculate_quarterly_returns(self, data: pd.DataFrame) -> Dict[int, float]:
        """四半期リターン計算"""
        quarterly_data = data.resample('Q').last()
        quarterly_returns = {}
        
        for quarter in range(1, 5):
            quarter_data = quarterly_data[quarterly_data.index.quarter == quarter]
            if len(quarter_data) > 1:
                returns = quarter_data['Close'].pct_change().dropna()
                quarterly_returns[quarter] = returns.mean()
            else:
                quarterly_returns[quarter] = 0.0
        
        return quarterly_returns
    
    def _analyze_seasonal_patterns(self, monthly_returns: Dict[int, float]) -> Dict[str, Any]:
        """季節パターン分析"""
        returns_array = np.array(list(monthly_returns.values()))
        
        # フーリエ変換による周期性検出
        fft = np.fft.fft(returns_array)
        frequencies = np.fft.fftfreq(len(returns_array))
        
        # 主要な周期性の特定
        dominant_frequencies = np.argsort(np.abs(fft))[-3:]
        
        # トレンド分析
        months = np.array(list(monthly_returns.keys()))
        returns = np.array(list(monthly_returns.values()))
        
        # 線形回帰によるトレンド分析
        slope, intercept, r_value, p_value, std_err = stats.linregress(months, returns)
        
        return {
            'dominant_frequencies': dominant_frequencies.tolist(),
            'trend_slope': slope,
            'trend_r_squared': r_value ** 2,
            'trend_p_value': p_value,
            'volatility': np.std(returns),
            'mean_return': np.mean(returns)
        }
    
    def _test_statistical_significance(self, monthly_returns: Dict[int, float]) -> Dict[str, float]:
        """統計的有意性検定"""
        returns_array = np.array(list(monthly_returns.values()))
        
        # 正規性検定（Shapiro-Wilk）
        shapiro_stat, shapiro_p = stats.shapiro(returns_array)
        
        # 等分散性検定（Levene）
        # 月を2つのグループに分割して検定
        group1 = returns_array[:6]  # 1-6月
        group2 = returns_array[6:]  # 7-12月
        levene_stat, levene_p = stats.levene(group1, group2)
        
        # 相関分析
        months = np.array(list(monthly_returns.keys()))
        correlation, corr_p = stats.pearsonr(months, returns_array)
        
        return {
            'shapiro_statistic': shapiro_stat,
            'shapiro_p_value': shapiro_p,
            'levene_statistic': levene_stat,
            'levene_p_value': levene_p,
            'correlation_coefficient': correlation,
            'correlation_p_value': corr_p
        }
    
    def _identify_best_worst_months(self, monthly_returns: Dict[int, float]) -> Tuple[List[int], List[int]]:
        """最良・最悪月の特定"""
        sorted_returns = sorted(monthly_returns.items(), key=lambda x: x[1], reverse=True)
        
        # 上位3ヶ月
        best_months = [month for month, _ in sorted_returns[:3]]
        
        # 下位3ヶ月
        worst_months = [month for month, _ in sorted_returns[-3:]]
        
        return best_months, worst_months


class EarningsAnalyzer:
    """業績発表分析クラス"""
    
    def __init__(self):
        self.earnings_dates = {}
    
    def analyze_earnings_impact(self, data: pd.DataFrame, symbol: str) -> EarningsAnalysis:
        """業績発表影響分析"""
        logger.info(f"業績発表分析開始: {symbol}")
        
        # 業績発表日推定（四半期終了後30-45日後）
        earnings_dates = self._estimate_earnings_dates(data)
        
        # 業績発表前後のリターン分析
        pre_earnings_returns = self._analyze_pre_earnings_returns(data, earnings_dates)
        post_earnings_returns = self._analyze_post_earnings_returns(data, earnings_dates)
        
        # ボラティリティ分析
        earnings_volatility = self._analyze_earnings_volatility(data, earnings_dates)
        
        # サプライズ影響分析
        surprise_impact = self._analyze_surprise_impact(data, earnings_dates)
        
        # 取引量変化分析
        volume_changes = self._analyze_volume_changes(data, earnings_dates)
        
        return EarningsAnalysis(
            pre_earnings_returns=pre_earnings_returns,
            post_earnings_returns=post_earnings_returns,
            earnings_volatility=earnings_volatility,
            surprise_impact=surprise_impact,
            trading_volume_changes=volume_changes
        )
    
    def _estimate_earnings_dates(self, data: pd.DataFrame) -> List[datetime]:
        """業績発表日推定"""
        earnings_dates = []
        
        # 四半期終了日を特定
        quarterly_ends = data.resample('Q').last().index
        
        for quarter_end in quarterly_ends:
            # 四半期終了後30-45日後に業績発表と仮定
            estimated_earnings_date = quarter_end + timedelta(days=37)
            
            # データ範囲内かチェック
            if estimated_earnings_date in data.index:
                earnings_dates.append(estimated_earnings_date)
        
        return earnings_dates
    
    def _analyze_pre_earnings_returns(self, data: pd.DataFrame, earnings_dates: List[datetime]) -> Dict[str, float]:
        """業績発表前リターン分析"""
        pre_returns = {}
        
        for earnings_date in earnings_dates:
            # 業績発表前5日、10日、20日のリターン
            for days in [5, 10, 20]:
                start_date = earnings_date - timedelta(days=days)
                
                if start_date in data.index and earnings_date in data.index:
                    start_price = data.loc[start_date, 'Close']
                    end_price = data.loc[earnings_date, 'Close']
                    return_pct = (end_price - start_price) / start_price
                    pre_returns[f'pre_{days}d'] = return_pct
        
        return pre_returns
    
    def _analyze_post_earnings_returns(self, data: pd.DataFrame, earnings_dates: List[datetime]) -> Dict[str, float]:
        """業績発表後リターン分析"""
        post_returns = {}
        
        for earnings_date in earnings_dates:
            # 業績発表後5日、10日、20日のリターン
            for days in [5, 10, 20]:
                end_date = earnings_date + timedelta(days=days)
                
                if earnings_date in data.index and end_date in data.index:
                    start_price = data.loc[earnings_date, 'Close']
                    end_price = data.loc[end_date, 'Close']
                    return_pct = (end_price - start_price) / start_price
                    post_returns[f'post_{days}d'] = return_pct
        
        return post_returns
    
    def _analyze_earnings_volatility(self, data: pd.DataFrame, earnings_dates: List[datetime]) -> Dict[str, float]:
        """業績発表期間ボラティリティ分析"""
        volatility_metrics = {}
        
        for earnings_date in earnings_dates:
            # 業績発表前後10日間のボラティリティ
            pre_start = earnings_date - timedelta(days=10)
            post_end = earnings_date + timedelta(days=10)
            
            if pre_start in data.index and post_end in data.index:
                pre_data = data.loc[pre_start:earnings_date, 'Close']
                post_data = data.loc[earnings_date:post_end, 'Close']
                
                pre_volatility = pre_data.pct_change().std()
                post_volatility = post_data.pct_change().std()
                
                volatility_metrics['pre_volatility'] = pre_volatility
                volatility_metrics['post_volatility'] = post_volatility
                volatility_metrics['volatility_change'] = post_volatility - pre_volatility
        
        return volatility_metrics
    
    def _analyze_surprise_impact(self, data: pd.DataFrame, earnings_dates: List[datetime]) -> Dict[str, float]:
        """サプライズ影響分析"""
        surprise_metrics = {}
        
        for earnings_date in earnings_dates:
            # 業績発表前後の価格変化
            pre_price = data.loc[earnings_date - timedelta(days=1), 'Close']
            post_price = data.loc[earnings_date + timedelta(days=1), 'Close']
            
            price_change = (post_price - pre_price) / pre_price
            surprise_metrics['price_change'] = price_change
            
            # 取引量変化
            pre_volume = data.loc[earnings_date - timedelta(days=1), 'Volume']
            post_volume = data.loc[earnings_date + timedelta(days=1), 'Volume']
            
            volume_change = (post_volume - pre_volume) / pre_volume
            surprise_metrics['volume_change'] = volume_change
        
        return surprise_metrics
    
    def _analyze_volume_changes(self, data: pd.DataFrame, earnings_dates: List[datetime]) -> Dict[str, float]:
        """取引量変化分析"""
        volume_metrics = {}
        
        for earnings_date in earnings_dates:
            # 業績発表前後5日間の平均取引量
            pre_start = earnings_date - timedelta(days=5)
            post_end = earnings_date + timedelta(days=5)
            
            if pre_start in data.index and post_end in data.index:
                pre_volume = data.loc[pre_start:earnings_date, 'Volume'].mean()
                post_volume = data.loc[earnings_date:post_end, 'Volume'].mean()
                
                volume_metrics['pre_volume'] = pre_volume
                volume_metrics['post_volume'] = post_volume
                volume_metrics['volume_ratio'] = post_volume / pre_volume
        
        return volume_metrics


class TechnicalOptimizer:
    """技術指標最適化クラス"""
    
    def __init__(self):
        self.optimization_history = []
    
    def optimize_technical_indicators(self, data: pd.DataFrame, symbol: str) -> TechnicalOptimization:
        """技術指標最適化"""
        logger.info(f"技術指標最適化開始: {symbol}")
        
        # パラメータグリッド定義
        param_grid = self._define_parameter_grid()
        
        # 最適化実行
        optimal_params, performance_metrics, sensitivity = self._run_optimization(data, param_grid)
        
        return TechnicalOptimization(
            optimal_parameters=optimal_params,
            performance_metrics=performance_metrics,
            parameter_sensitivity=sensitivity,
            optimization_history=self.optimization_history
        )
    
    def _define_parameter_grid(self) -> Dict[str, List]:
        """パラメータグリッド定義"""
        return {
            'sma_short': [5, 10, 15, 20],
            'sma_long': [20, 30, 50, 100],
            'rsi_period': [14, 21, 28],
            'macd_fast': [12, 15, 18],
            'macd_slow': [26, 30, 34],
            'bb_period': [20, 25, 30],
            'bb_std': [1.5, 2.0, 2.5]
        }
    
    def _run_optimization(self, data: pd.DataFrame, param_grid: Dict[str, List]) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, float]]:
        """最適化実行"""
        best_params = {}
        best_performance = 0
        all_results = []
        
        # グリッドサーチ実行
        for params in ParameterGrid(param_grid):
            try:
                # 技術指標計算
                indicators = self._calculate_technical_indicators(data, params)
                
                # パフォーマンス評価
                performance = self._evaluate_performance(data, indicators, params)
                
                all_results.append({
                    'params': params,
                    'performance': performance
                })
                
                # 最良パラメータ更新
                if performance > best_performance:
                    best_performance = performance
                    best_params = params
                    
            except Exception as e:
                logger.warning(f"パラメータ最適化エラー: {e}")
                continue
        
        # パフォーマンス指標計算
        performance_metrics = self._calculate_performance_metrics(all_results)
        
        # パラメータ感度分析
        sensitivity = self._analyze_parameter_sensitivity(all_results)
        
        return best_params, performance_metrics, sensitivity
    
    def _calculate_technical_indicators(self, data: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, pd.Series]:
        """技術指標計算"""
        indicators = {}
        
        # SMA
        indicators['sma_short'] = talib.SMA(data['Close'], timeperiod=params['sma_short'])
        indicators['sma_long'] = talib.SMA(data['Close'], timeperiod=params['sma_long'])
        
        # RSI
        indicators['rsi'] = talib.RSI(data['Close'], timeperiod=params['rsi_period'])
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(
            data['Close'],
            fastperiod=params['macd_fast'],
            slowperiod=params['macd_slow'],
            signalperiod=9
        )
        indicators['macd'] = macd
        indicators['macd_signal'] = macd_signal
        indicators['macd_histogram'] = macd_hist
        
        # ボリンジャーバンド
        bb_upper, bb_middle, bb_lower = talib.BBANDS(
            data['Close'],
            timeperiod=params['bb_period'],
            nbdevup=params['bb_std'],
            nbdevdn=params['bb_std']
        )
        indicators['bb_upper'] = bb_upper
        indicators['bb_middle'] = bb_middle
        indicators['bb_lower'] = bb_lower
        
        return indicators
    
    def _evaluate_performance(self, data: pd.DataFrame, indicators: Dict[str, pd.Series], params: Dict[str, Any]) -> float:
        """パフォーマンス評価"""
        # シグナル生成
        signals = self._generate_signals(data, indicators)
        
        # バックテスト実行
        returns = self._calculate_strategy_returns(data, signals)
        
        # シャープレシオ計算
        if returns.std() > 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        return sharpe_ratio
    
    def _generate_signals(self, data: pd.DataFrame, indicators: Dict[str, pd.Series]) -> pd.Series:
        """シグナル生成"""
        signals = pd.Series(0, index=data.index)
        
        # SMAクロスオーバー
        sma_signal = np.where(
            indicators['sma_short'] > indicators['sma_long'], 1,
            np.where(indicators['sma_short'] < indicators['sma_long'], -1, 0)
        )
        
        # RSIシグナル
        rsi_signal = np.where(
            indicators['rsi'] > 70, -1,
            np.where(indicators['rsi'] < 30, 1, 0)
        )
        
        # MACDシグナル
        macd_signal = np.where(
            indicators['macd'] > indicators['macd_signal'], 1,
            np.where(indicators['macd'] < indicators['macd_signal'], -1, 0)
        )
        
        # ボリンジャーバンドシグナル
        bb_signal = np.where(
            data['Close'] > indicators['bb_upper'], -1,
            np.where(data['Close'] < indicators['bb_lower'], 1, 0)
        )
        
        # シグナル統合
        combined_signal = (sma_signal + rsi_signal + macd_signal + bb_signal) / 4
        signals = pd.Series(combined_signal, index=data.index)
        
        return signals
    
    def _calculate_strategy_returns(self, data: pd.DataFrame, signals: pd.Series) -> pd.Series:
        """戦略リターン計算"""
        returns = data['Close'].pct_change()
        strategy_returns = signals.shift(1) * returns
        return strategy_returns.dropna()
    
    def _calculate_performance_metrics(self, all_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """パフォーマンス指標計算"""
        performances = [result['performance'] for result in all_results]
        
        return {
            'best_performance': max(performances),
            'worst_performance': min(performances),
            'mean_performance': np.mean(performances),
            'std_performance': np.std(performances),
            'median_performance': np.median(performances)
        }
    
    def _analyze_parameter_sensitivity(self, all_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """パラメータ感度分析"""
        sensitivity = {}
        
        # 各パラメータの感度計算
        param_names = list(all_results[0]['params'].keys())
        
        for param_name in param_names:
            param_values = []
            performances = []
            
            for result in all_results:
                param_values.append(result['params'][param_name])
                performances.append(result['performance'])
            
            # 相関係数計算
            correlation = np.corrcoef(param_values, performances)[0, 1]
            sensitivity[param_name] = correlation
        
        return sensitivity


class IndividualStockBacktestSystem:
    """個別銘柄バックテストシステム"""
    
    def __init__(self, initial_capital: float = 1000000):
        self.initial_capital = initial_capital
        self.seasonal_analyzer = SeasonalAnalyzer()
        self.earnings_analyzer = EarningsAnalyzer()
        self.technical_optimizer = TechnicalOptimizer()
        self.backtest_engine = BacktestEngine(initial_capital)
    
    def analyze_individual_stock(self, symbol: str, start_date: datetime, end_date: datetime) -> IndividualStockResult:
        """個別銘柄分析実行"""
        logger.info(f"個別銘柄分析開始: {symbol}")
        
        # データ取得
        data = self._fetch_stock_data(symbol, start_date, end_date)
        
        if data.empty:
            raise ValueError(f"データが取得できませんでした: {symbol}")
        
        # 基本指標計算
        basic_metrics = self._calculate_basic_metrics(data)
        
        # 季節性分析
        seasonal_analysis = self.seasonal_analyzer.analyze_seasonality(data, symbol)
        
        # 業績発表分析
        earnings_analysis = self.earnings_analyzer.analyze_earnings_impact(data, symbol)
        
        # 技術指標最適化
        technical_optimization = self.technical_optimizer.optimize_technical_indicators(data, symbol)
        
        # 戦略バックテスト
        strategy_results = self._run_strategy_backtests(data, symbol, start_date, end_date)
        
        # 比較分析
        comparison_metrics = self._calculate_comparison_metrics(data, symbol)
        
        return IndividualStockResult(
            symbol=symbol,
            analysis_period=(start_date, end_date),
            basic_metrics=basic_metrics,
            seasonal_analysis=seasonal_analysis,
            earnings_analysis=earnings_analysis,
            technical_optimization=technical_optimization,
            strategy_results=strategy_results,
            comparison_metrics=comparison_metrics
        )
    
    def _fetch_stock_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """株価データ取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            return data
        except Exception as e:
            logger.error(f"データ取得エラー {symbol}: {e}")
            return pd.DataFrame()
    
    def _calculate_basic_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """基本指標計算"""
        returns = data['Close'].pct_change().dropna()
        
        return {
            'total_return': (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1,
            'annualized_return': ((data['Close'].iloc[-1] / data['Close'].iloc[0]) ** (252 / len(data))) - 1,
            'volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(data['Close']),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'var_95': np.percentile(returns, 5),
            'var_99': np.percentile(returns, 1)
        }
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """最大ドローダウン計算"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    def _run_strategy_backtests(self, data: pd.DataFrame, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, BacktestResult]:
        """戦略バックテスト実行"""
        strategies = [
            MomentumStrategy({"lookback": 20, "threshold": 0.05}),
            MeanReversionStrategy({"lookback": 20, "std_threshold": 2.0}),
            BreakoutStrategy({"lookback": 20, "volume_threshold": 1.5})
        ]
        
        results = {}
        
        for strategy in strategies:
            try:
                result = self.backtest_engine.run_backtest(data, strategy, start_date, end_date)
                results[strategy.name] = result
            except Exception as e:
                logger.error(f"戦略バックテストエラー {symbol}-{strategy.name}: {e}")
                results[strategy.name] = None
        
        return results
    
    def _calculate_comparison_metrics(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """比較分析指標計算"""
        returns = data['Close'].pct_change().dropna()
        
        # ベンチマーク比較（日経平均を想定）
        benchmark_return = 0.05  # 仮の年率5%
        excess_return = returns.mean() * 252 - benchmark_return
        
        # 相関分析（自己相関）
        autocorrelation = returns.autocorr(lag=1)
        
        # ボラティリティクラスタリング
        volatility_clustering = returns.rolling(20).std().autocorr(lag=1)
        
        return {
            'excess_return': excess_return,
            'autocorrelation': autocorrelation,
            'volatility_clustering': volatility_clustering,
            'trend_strength': self._calculate_trend_strength(data['Close']),
            'momentum_score': self._calculate_momentum_score(returns)
        }
    
    def _calculate_trend_strength(self, prices: pd.Series) -> float:
        """トレンド強度計算"""
        # 線形回帰によるトレンド分析
        x = np.arange(len(prices))
        y = prices.values
        
        slope, _, r_value, _, _ = stats.linregress(x, y)
        return r_value ** 2  # R²値
    
    def _calculate_momentum_score(self, returns: pd.Series) -> float:
        """モメンタムスコア計算"""
        # 過去20日、60日、120日のリターン
        momentum_20 = returns.rolling(20).sum().iloc[-1] if len(returns) >= 20 else 0
        momentum_60 = returns.rolling(60).sum().iloc[-1] if len(returns) >= 60 else 0
        momentum_120 = returns.rolling(120).sum().iloc[-1] if len(returns) >= 120 else 0
        
        # 重み付きモメンタムスコア
        momentum_score = (momentum_20 * 0.5 + momentum_60 * 0.3 + momentum_120 * 0.2)
        
        return momentum_score
    
    def compare_multiple_stocks(self, symbols: List[str], start_date: datetime, end_date: datetime) -> Dict[str, IndividualStockResult]:
        """複数銘柄比較分析"""
        logger.info(f"複数銘柄比較分析開始: {len(symbols)}銘柄")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self.analyze_individual_stock, symbol, start_date, end_date): symbol
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    results[symbol] = result
                    logger.info(f"分析完了: {symbol}")
                except Exception as e:
                    logger.error(f"分析エラー {symbol}: {e}")
                    results[symbol] = None
        
        return results
    
    def generate_comprehensive_report(self, result: IndividualStockResult) -> str:
        """包括的レポート生成"""
        report = []
        report.append("=" * 100)
        report.append(f"📊 個別銘柄詳細分析レポート - {result.symbol}")
        report.append("=" * 100)
        
        # 基本情報
        report.append(f"\n📅 分析期間: {result.analysis_period[0].strftime('%Y-%m-%d')} - {result.analysis_period[1].strftime('%Y-%m-%d')}")
        
        # 基本指標
        report.append(f"\n📈 基本指標:")
        for key, value in result.basic_metrics.items():
            if isinstance(value, float):
                report.append(f"  {key}: {value:.4f}")
            else:
                report.append(f"  {key}: {value}")
        
        # 季節性分析
        report.append(f"\n🗓️ 季節性分析:")
        report.append(f"  最良月: {result.seasonal_analysis.best_months}")
        report.append(f"  最悪月: {result.seasonal_analysis.worst_months}")
        report.append(f"  トレンド強度: {result.seasonal_analysis.seasonal_patterns['trend_r_squared']:.4f}")
        
        # 業績発表分析
        report.append(f"\n📊 業績発表分析:")
        for key, value in result.earnings_analysis.pre_earnings_returns.items():
            report.append(f"  {key}: {value:.4f}")
        
        # 技術指標最適化
        report.append(f"\n⚙️ 技術指標最適化:")
        report.append(f"  最適パラメータ: {result.technical_optimization.optimal_parameters}")
        report.append(f"  最高パフォーマンス: {result.technical_optimization.performance_metrics['best_performance']:.4f}")
        
        # 戦略バックテスト結果
        report.append(f"\n🎯 戦略バックテスト結果:")
        for strategy_name, strategy_result in result.strategy_results.items():
            if strategy_result:
                report.append(f"  {strategy_name}:")
                report.append(f"    総リターン: {strategy_result.total_return:.2%}")
                report.append(f"    シャープレシオ: {strategy_result.sharpe_ratio:.2f}")
                report.append(f"    最大ドローダウン: {strategy_result.max_drawdown:.2%}")
            else:
                report.append(f"  {strategy_name}: データなし")
        
        # 比較分析
        report.append(f"\n📊 比較分析:")
        for key, value in result.comparison_metrics.items():
            report.append(f"  {key}: {value:.4f}")
        
        return "\n".join(report)
    
    def save_results(self, result: IndividualStockResult, filename: str = None):
        """結果保存"""
        if filename is None:
            filename = f"individual_analysis_{result.symbol}"
        
        # JSON形式で保存
        result_dict = asdict(result)
        
        # 日時を文字列に変換
        for key, value in result_dict.items():
            if isinstance(value, datetime):
                result_dict[key] = value.isoformat()
            elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], datetime):
                result_dict[key] = [value[0].isoformat(), value[1].isoformat()]
        
        with open(f"{filename}_results.json", "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2, default=str)
        
        # レポート保存
        report = self.generate_comprehensive_report(result)
        with open(f"{filename}_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info(f"結果を保存しました: {filename}_results.json, {filename}_report.txt")


def main():
    """メイン実行関数"""
    logger.info("=== 個別銘柄バックテスト詳細化システム開始 ===")
    
    # 設定
    symbols = [
        "7203.T",  # トヨタ自動車
        "6758.T",  # ソニーグループ
        "9984.T",  # ソフトバンクグループ
        "9432.T",  # 日本電信電話
        "6861.T",  # キーエンス
    ]
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    initial_capital = 1000000
    
    # 個別銘柄バックテストシステム初期化
    system = IndividualStockBacktestSystem(initial_capital)
    
    try:
        # 個別銘柄分析実行
        for symbol in symbols:
            logger.info(f"個別銘柄分析開始: {symbol}")
            
            result = system.analyze_individual_stock(symbol, start_date, end_date)
            
            # レポート生成・表示
            report = system.generate_comprehensive_report(result)
            print(report)
            
            # 結果保存
            system.save_results(result)
        
        # 複数銘柄比較分析
        logger.info("複数銘柄比較分析開始")
        comparison_results = system.compare_multiple_stocks(symbols, start_date, end_date)
        
        # 比較レポート生成
        comparison_report = []
        comparison_report.append("=" * 100)
        comparison_report.append("📊 複数銘柄比較分析レポート")
        comparison_report.append("=" * 100)
        
        for symbol, result in comparison_results.items():
            if result:
                comparison_report.append(f"\n{symbol}:")
                comparison_report.append(f"  総リターン: {result.basic_metrics['total_return']:.2%}")
                comparison_report.append(f"  シャープレシオ: {result.basic_metrics['sharpe_ratio']:.2f}")
                comparison_report.append(f"  最大ドローダウン: {result.basic_metrics['max_drawdown']:.2%}")
        
        comparison_report_text = "\n".join(comparison_report)
        print(comparison_report_text)
        
        # 比較レポート保存
        with open("multi_stock_comparison_report.txt", "w", encoding="utf-8") as f:
            f.write(comparison_report_text)
        
        logger.info("=== 個別銘柄バックテスト詳細化完了 ===")
        
    except Exception as e:
        logger.error(f"個別銘柄バックテストエラー: {e}")
        raise


if __name__ == "__main__":
    main()
