#!/usr/bin/env python3
"""
高度な戦略フレームワーク
複数戦略の同時実行、最適化、ポートフォリオ管理機能

機能:
1. 複数戦略の並列実行
2. 戦略パラメータ最適化
3. ポートフォリオ最適化
4. リスク管理統合
5. リアルタイム戦略切り替え
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class StrategyPerformance:
    """戦略パフォーマンス"""
    strategy_name: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    volatility: float
    beta: float
    alpha: float
    sortino_ratio: float
    calmar_ratio: float
    parameters: Dict[str, Any]

@dataclass
class PortfolioWeights:
    """ポートフォリオ重み"""
    strategy_weights: Dict[str, float]
    total_weight: float
    risk_budget: Dict[str, float]

class AdvancedStrategyOptimizer:
    """高度な戦略最適化クラス"""
    
    def __init__(self, strategies: List, data: pd.DataFrame, 
                 optimization_method: str = "genetic"):
        self.strategies = strategies
        self.data = data
        self.optimization_method = optimization_method
        self.optimization_results = {}
    
    def optimize_parameters(self, strategy, parameter_ranges: Dict[str, Tuple], 
                          objective: str = "sharpe_ratio", max_iterations: int = 100) -> Dict:
        """パラメータ最適化"""
        logger.info(f"戦略最適化開始: {strategy.name}")
        
        if self.optimization_method == "grid_search":
            return self._grid_search_optimization(strategy, parameter_ranges, objective)
        elif self.optimization_method == "genetic":
            return self._genetic_optimization(strategy, parameter_ranges, objective, max_iterations)
        else:
            return self._random_search_optimization(strategy, parameter_ranges, objective, max_iterations)
    
    def _grid_search_optimization(self, strategy, parameter_ranges: Dict[str, Tuple], 
                                objective: str) -> Dict:
        """グリッドサーチ最適化"""
        best_params = {}
        best_score = float('-inf')
        
        # パラメータの組み合わせを生成
        param_names = list(parameter_ranges.keys())
        param_values = [parameter_ranges[name] for name in param_names]
        
        for param_combination in itertools.product(*param_values):
            params = dict(zip(param_names, param_combination))
            
            try:
                # 戦略にパラメータを設定
                strategy.parameters.update(params)
                
                # バックテスト実行
                from advanced_backtest_system import BacktestEngine
                engine = BacktestEngine()
                result = engine.run_backtest(self.data, strategy, 
                                          self.data.index[0], self.data.index[-1])
                
                # スコア計算
                score = self._calculate_objective_score(result, objective)
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    
            except Exception as e:
                logger.warning(f"パラメータ組み合わせエラー: {params}, {e}")
                continue
        
        logger.info(f"最適化完了: {strategy.name}, スコア: {best_score:.4f}")
        return {
            'best_parameters': best_params,
            'best_score': best_score,
            'optimization_method': 'grid_search'
        }
    
    def _genetic_optimization(self, strategy, parameter_ranges: Dict[str, Tuple], 
                            objective: str, max_iterations: int) -> Dict:
        """遺伝的アルゴリズム最適化"""
        # 簡易版遺伝的アルゴリズム実装
        population_size = 20
        mutation_rate = 0.1
        crossover_rate = 0.8
        
        # 初期個体群生成
        population = self._generate_initial_population(parameter_ranges, population_size)
        best_individual = None
        best_score = float('-inf')
        
        for generation in range(max_iterations):
            # 評価
            scores = []
            for individual in population:
                try:
                    strategy.parameters.update(individual)
                    from advanced_backtest_system import BacktestEngine
                    engine = BacktestEngine()
                    result = engine.run_backtest(self.data, strategy, 
                                              self.data.index[0], self.data.index[-1])
                    score = self._calculate_objective_score(result, objective)
                    scores.append(score)
                    
                    if score > best_score:
                        best_score = score
                        best_individual = individual.copy()
                        
                except Exception as e:
                    scores.append(float('-inf'))
            
            # 選択、交叉、突然変異
            if generation < max_iterations - 1:
                population = self._evolve_population(population, scores, 
                                                 mutation_rate, crossover_rate, 
                                                 parameter_ranges)
        
        logger.info(f"遺伝的アルゴリズム最適化完了: {strategy.name}, スコア: {best_score:.4f}")
        return {
            'best_parameters': best_individual or {},
            'best_score': best_score,
            'optimization_method': 'genetic'
        }
    
    def _random_search_optimization(self, strategy, parameter_ranges: Dict[str, Tuple], 
                                  objective: str, max_iterations: int) -> Dict:
        """ランダムサーチ最適化"""
        best_params = {}
        best_score = float('-inf')
        
        for _ in range(max_iterations):
            # ランダムパラメータ生成
            params = {}
            for param_name, (min_val, max_val) in parameter_ranges.items():
                if isinstance(min_val, int):
                    params[param_name] = np.random.randint(min_val, max_val + 1)
                else:
                    params[param_name] = np.random.uniform(min_val, max_val)
            
            try:
                strategy.parameters.update(params)
                from advanced_backtest_system import BacktestEngine
                engine = BacktestEngine()
                result = engine.run_backtest(self.data, strategy, 
                                          self.data.index[0], self.data.index[-1])
                score = self._calculate_objective_score(result, objective)
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    
            except Exception as e:
                logger.warning(f"ランダムパラメータエラー: {params}, {e}")
                continue
        
        logger.info(f"ランダムサーチ最適化完了: {strategy.name}, スコア: {best_score:.4f}")
        return {
            'best_parameters': best_params,
            'best_score': best_score,
            'optimization_method': 'random_search'
        }
    
    def _generate_initial_population(self, parameter_ranges: Dict[str, Tuple], 
                                   population_size: int) -> List[Dict]:
        """初期個体群生成"""
        population = []
        for _ in range(population_size):
            individual = {}
            for param_name, (min_val, max_val) in parameter_ranges.items():
                if isinstance(min_val, int):
                    individual[param_name] = np.random.randint(min_val, max_val + 1)
                else:
                    individual[param_name] = np.random.uniform(min_val, max_val)
            population.append(individual)
        return population
    
    def _evolve_population(self, population: List[Dict], scores: List[float], 
                         mutation_rate: float, crossover_rate: float, 
                         parameter_ranges: Dict[str, Tuple]) -> List[Dict]:
        """個体群進化"""
        new_population = []
        
        # エリート選択（上位50%を保持）
        elite_size = len(population) // 2
        elite_indices = np.argsort(scores)[-elite_size:]
        for idx in elite_indices:
            new_population.append(population[idx].copy())
        
        # 残りを交叉・突然変異で生成
        while len(new_population) < len(population):
            # 親選択（トーナメント選択）
            parent1 = self._tournament_selection(population, scores)
            parent2 = self._tournament_selection(population, scores)
            
            # 交叉
            if np.random.random() < crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1.copy()
            
            # 突然変異
            if np.random.random() < mutation_rate:
                child = self._mutate(child, parameter_ranges)
            
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self, population: List[Dict], scores: List[float], 
                            tournament_size: int = 3) -> Dict:
        """トーナメント選択"""
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_scores = [scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_scores)]
        return population[winner_idx].copy()
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """交叉"""
        child = {}
        for key in parent1.keys():
            if np.random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child
    
    def _mutate(self, individual: Dict, parameter_ranges: Dict[str, Tuple]) -> Dict:
        """突然変異"""
        mutated = individual.copy()
        param_name = np.random.choice(list(parameter_ranges.keys()))
        min_val, max_val = parameter_ranges[param_name]
        
        if isinstance(min_val, int):
            mutated[param_name] = np.random.randint(min_val, max_val + 1)
        else:
            mutated[param_name] = np.random.uniform(min_val, max_val)
        
        return mutated
    
    def _calculate_objective_score(self, result, objective: str) -> float:
        """目的関数スコア計算"""
        if objective == "sharpe_ratio":
            return result.sharpe_ratio
        elif objective == "total_return":
            return result.total_return
        elif objective == "profit_factor":
            return result.profit_factor
        elif objective == "calmar_ratio":
            return result.annualized_return / abs(result.max_drawdown) if result.max_drawdown != 0 else 0
        else:
            return result.sharpe_ratio

class PortfolioOptimizer:
    """ポートフォリオ最適化クラス"""
    
    def __init__(self, strategies: List, strategy_performances: List[StrategyPerformance]):
        self.strategies = strategies
        self.strategy_performances = strategy_performances
        self.correlation_matrix = None
        self.risk_free_rate = 0.02  # 2%リスクフリーレート
    
    def calculate_correlation_matrix(self, returns_data: Dict[str, pd.Series]) -> pd.DataFrame:
        """相関行列計算"""
        returns_df = pd.DataFrame(returns_data)
        self.correlation_matrix = returns_df.corr()
        return self.correlation_matrix
    
    def optimize_portfolio_weights(self, method: str = "max_sharpe") -> PortfolioWeights:
        """ポートフォリオ重み最適化"""
        if method == "max_sharpe":
            return self._maximize_sharpe_ratio()
        elif method == "min_variance":
            return self._minimize_variance()
        elif method == "risk_parity":
            return self._risk_parity_allocation()
        else:
            return self._equal_weight_allocation()
    
    def _maximize_sharpe_ratio(self) -> PortfolioWeights:
        """シャープレシオ最大化"""
        n_strategies = len(self.strategy_performances)
        
        # 期待リターン
        expected_returns = np.array([sp.annualized_return for sp in self.strategy_performances])
        
        # 共分散行列（簡易版）
        cov_matrix = np.diag([sp.volatility**2 for sp in self.strategy_performances])
        
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            if portfolio_volatility == 0:
                return -float('inf')
            return -(portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        # 制約条件
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = [(0, 1) for _ in range(n_strategies)]
        
        # 初期値（等重み）
        x0 = np.array([1/n_strategies] * n_strategies)
        
        # 最適化実行
        result = minimize(negative_sharpe, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
        else:
            weights = np.array([1/n_strategies] * n_strategies)
        
        # 重みを正規化
        weights = weights / np.sum(weights)
        
        strategy_weights = {
            sp.strategy_name: weight for sp, weight in zip(self.strategy_performances, weights)
        }
        
        return PortfolioWeights(
            strategy_weights=strategy_weights,
            total_weight=1.0,
            risk_budget={name: weight for name, weight in strategy_weights.items()}
        )
    
    def _minimize_variance(self) -> PortfolioWeights:
        """分散最小化"""
        n_strategies = len(self.strategy_performances)
        
        # 共分散行列
        cov_matrix = np.diag([sp.volatility**2 for sp in self.strategy_performances])
        
        def portfolio_variance(weights):
            return np.dot(weights, np.dot(cov_matrix, weights))
        
        # 制約条件
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = [(0, 1) for _ in range(n_strategies)]
        
        # 初期値
        x0 = np.array([1/n_strategies] * n_strategies)
        
        # 最適化実行
        result = minimize(portfolio_variance, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
        else:
            weights = np.array([1/n_strategies] * n_strategies)
        
        weights = weights / np.sum(weights)
        
        strategy_weights = {
            sp.strategy_name: weight for sp, weight in zip(self.strategy_performances, weights)
        }
        
        return PortfolioWeights(
            strategy_weights=strategy_weights,
            total_weight=1.0,
            risk_budget={name: weight for name, weight in strategy_weights.items()}
        )
    
    def _risk_parity_allocation(self) -> PortfolioWeights:
        """リスクパリティ配分"""
        n_strategies = len(self.strategy_performances)
        
        # 各戦略のリスク（ボラティリティ）
        risks = [sp.volatility for sp in self.strategy_performances]
        
        # リスクパリティ重み計算
        risk_weights = [1/risk for risk in risks]
        total_risk_weight = sum(risk_weights)
        weights = [rw/total_risk_weight for rw in risk_weights]
        
        strategy_weights = {
            sp.strategy_name: weight for sp, weight in zip(self.strategy_performances, weights)
        }
        
        return PortfolioWeights(
            strategy_weights=strategy_weights,
            total_weight=1.0,
            risk_budget={name: weight for name, weight in strategy_weights.items()}
        )
    
    def _equal_weight_allocation(self) -> PortfolioWeights:
        """等重み配分"""
        n_strategies = len(self.strategy_performances)
        equal_weight = 1.0 / n_strategies
        
        strategy_weights = {
            sp.strategy_name: equal_weight for sp in self.strategy_performances
        }
        
        return PortfolioWeights(
            strategy_weights=strategy_weights,
            total_weight=1.0,
            risk_budget={name: equal_weight for name in strategy_weights.keys()}
        )

class MultiStrategyManager:
    """複数戦略管理クラス"""
    
    def __init__(self, strategies: List, data: pd.DataFrame):
        self.strategies = strategies
        self.data = data
        self.strategy_performances = []
        self.optimized_weights = None
        self.portfolio_returns = None
    
    def run_parallel_backtest(self, start_date: datetime, end_date: datetime) -> List[StrategyPerformance]:
        """並列バックテスト実行"""
        logger.info("並列バックテスト開始")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(self.strategies), 4)) as executor:
            # 各戦略のバックテストを並列実行
            future_to_strategy = {
                executor.submit(self._run_single_backtest, strategy, start_date, end_date): strategy
                for strategy in self.strategies
            }
            
            for future in as_completed(future_to_strategy):
                strategy = future_to_strategy[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.info(f"戦略完了: {strategy.name}")
                except Exception as e:
                    logger.error(f"戦略実行エラー {strategy.name}: {e}")
        
        self.strategy_performances = results
        return results
    
    def _run_single_backtest(self, strategy, start_date: datetime, end_date: datetime) -> Optional[StrategyPerformance]:
        """単一戦略バックテスト"""
        try:
            from advanced_backtest_system import BacktestEngine
            engine = BacktestEngine()
            result = engine.run_backtest(self.data, strategy, start_date, end_date)
            
            # 追加指標計算
            returns = result.equity_curve.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            
            # ベータ計算（市場リターンとの相関）
            market_returns = self.data['Close'].pct_change().dropna()
            if len(returns) > 1 and len(market_returns) > 1:
                beta = returns.corr(market_returns) if not returns.corr(market_returns) != returns.corr(market_returns) else 0
            else:
                beta = 0
            
            # アルファ計算
            alpha = result.annualized_return - (0.02 + beta * (market_returns.mean() * 252 - 0.02))
            
            # ソルティノレシオ計算
            downside_returns = returns[returns < 0]
            downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = (result.annualized_return - 0.02) / downside_volatility if downside_volatility > 0 else 0
            
            # カルマーレシオ計算
            calmar_ratio = result.annualized_return / abs(result.max_drawdown) if result.max_drawdown != 0 else 0
            
            return StrategyPerformance(
                strategy_name=strategy.name,
                total_return=result.total_return,
                sharpe_ratio=result.sharpe_ratio,
                max_drawdown=result.max_drawdown,
                win_rate=result.win_rate,
                profit_factor=result.profit_factor,
                volatility=volatility,
                beta=beta,
                alpha=alpha,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                parameters=strategy.parameters
            )
            
        except Exception as e:
            logger.error(f"バックテストエラー {strategy.name}: {e}")
            return None
    
    def optimize_portfolio(self, method: str = "max_sharpe") -> PortfolioWeights:
        """ポートフォリオ最適化"""
        if not self.strategy_performances:
            logger.error("戦略パフォーマンスデータがありません")
            return None
        
        optimizer = PortfolioOptimizer(self.strategies, self.strategy_performances)
        self.optimized_weights = optimizer.optimize_portfolio_weights(method)
        
        logger.info(f"ポートフォリオ最適化完了: {method}")
        for strategy_name, weight in self.optimized_weights.strategy_weights.items():
            logger.info(f"  {strategy_name}: {weight:.2%}")
        
        return self.optimized_weights
    
    def calculate_portfolio_performance(self) -> Dict[str, float]:
        """ポートフォリオパフォーマンス計算"""
        if not self.optimized_weights or not self.strategy_performances:
            return {}
        
        # 重み付きパフォーマンス計算
        weighted_return = sum(
            sp.annualized_return * self.optimized_weights.strategy_weights[sp.strategy_name]
            for sp in self.strategy_performances
        )
        
        weighted_volatility = sum(
            sp.volatility * self.optimized_weights.strategy_weights[sp.strategy_name]
            for sp in self.strategy_performances
        )
        
        weighted_sharpe = weighted_return / weighted_volatility if weighted_volatility > 0 else 0
        
        return {
            'portfolio_return': weighted_return,
            'portfolio_volatility': weighted_volatility,
            'portfolio_sharpe': weighted_sharpe,
            'diversification_ratio': len(self.strategies) / sum(
                self.optimized_weights.strategy_weights.values()
            ) if self.optimized_weights.strategy_weights else 0
        }
    
    def generate_optimization_report(self) -> str:
        """最適化レポート生成"""
        if not self.strategy_performances:
            return "パフォーマンスデータがありません"
        
        report = []
        report.append("=" * 80)
        report.append("📊 高度な戦略最適化レポート")
        report.append("=" * 80)
        
        # 個別戦略パフォーマンス
        report.append("\n🏆 個別戦略パフォーマンス:")
        report.append("-" * 60)
        for sp in self.strategy_performances:
            report.append(f"{sp.strategy_name}:")
            report.append(f"  年率リターン: {sp.annualized_return:.2%}")
            report.append(f"  シャープレシオ: {sp.sharpe_ratio:.2f}")
            report.append(f"  最大ドローダウン: {sp.max_drawdown:.2%}")
            report.append(f"  ボラティリティ: {sp.volatility:.2%}")
            report.append(f"  ベータ: {sp.beta:.2f}")
            report.append(f"  アルファ: {sp.alpha:.2%}")
            report.append(f"  ソルティノレシオ: {sp.sortino_ratio:.2f}")
            report.append(f"  カルマーレシオ: {sp.calmar_ratio:.2f}")
            report.append("")
        
        # ポートフォリオ最適化結果
        if self.optimized_weights:
            report.append("🎯 最適化ポートフォリオ:")
            report.append("-" * 40)
            for strategy_name, weight in self.optimized_weights.strategy_weights.items():
                report.append(f"  {strategy_name}: {weight:.2%}")
            
            portfolio_perf = self.calculate_portfolio_performance()
            if portfolio_perf:
                report.append(f"\n📈 ポートフォリオパフォーマンス:")
                report.append(f"  年率リターン: {portfolio_perf['portfolio_return']:.2%}")
                report.append(f"  ボラティリティ: {portfolio_perf['portfolio_volatility']:.2%}")
                report.append(f"  シャープレシオ: {portfolio_perf['portfolio_sharpe']:.2f}")
                report.append(f"  分散化比率: {portfolio_perf['diversification_ratio']:.2f}")
        
        return "\n".join(report)

def main():
    """メイン実行関数"""
    logger.info("=== 高度な戦略フレームワーク開始 ===")
    
    # データ取得
    symbol = "7203.T"
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date, end=end_date)
    
    if data.empty:
        logger.error("データが取得できませんでした")
        return
    
    # 戦略定義
    from advanced_backtest_system import MomentumStrategy, MeanReversionStrategy, BreakoutStrategy
    
    strategies = [
        MomentumStrategy({'lookback': 20, 'threshold': 0.05}),
        MeanReversionStrategy({'lookback': 20, 'std_threshold': 2.0}),
        BreakoutStrategy({'lookback': 20, 'volume_threshold': 1.5})
    ]
    
    # 複数戦略管理
    manager = MultiStrategyManager(strategies, data)
    
    # 並列バックテスト実行
    performances = manager.run_parallel_backtest(start_date, end_date)
    
    if performances:
        # ポートフォリオ最適化
        weights = manager.optimize_portfolio("max_sharpe")
        
        # レポート生成
        report = manager.generate_optimization_report()
        print(report)
        
        # 結果保存
        with open('strategy_optimization_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("=== 戦略最適化完了 ===")
    else:
        logger.error("有効な戦略パフォーマンスがありません")

if __name__ == "__main__":
    main()
