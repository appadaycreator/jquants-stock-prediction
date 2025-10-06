"""
シャープレシオ最適化システム
20%向上を目指した高度なシャープレシオ最適化システム
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from scipy.optimize import minimize
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

@dataclass
class SharpeOptimizationResult:
    """シャープレシオ最適化結果"""
    original_sharpe: float
    optimized_sharpe: float
    improvement_ratio: float
    target_achieved: bool
    optimization_method: str
    portfolio_weights: Dict[str, float]
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    optimization_timestamp: str
    convergence_success: bool
    iterations: int

@dataclass
class OptimizationConstraints:
    """最適化制約"""
    max_position_weight: float
    min_position_weight: float
    max_sector_weight: float
    max_correlation: float
    max_volatility: float
    min_liquidity: float
    max_turnover: float
    transaction_costs: float

class SharpeRatioOptimizer:
    """シャープレシオ最適化システム"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # 最適化パラメータ
        self.target_improvement = 0.20  # 20%向上目標
        self.risk_free_rate = self.config.get('risk_free_rate', 0.02)
        self.max_iterations = self.config.get('max_iterations', 1000)
        self.tolerance = self.config.get('tolerance', 1e-6)
        
        # 制約条件
        self.constraints = OptimizationConstraints(
            max_position_weight=self.config.get('max_position_weight', 0.2),
            min_position_weight=self.config.get('min_position_weight', 0.01),
            max_sector_weight=self.config.get('max_sector_weight', 0.3),
            max_correlation=self.config.get('max_correlation', 0.7),
            max_volatility=self.config.get('max_volatility', 0.5),
            min_liquidity=self.config.get('min_liquidity', 1000000),
            max_turnover=self.config.get('max_turnover', 0.5),
            transaction_costs=self.config.get('transaction_costs', 0.001)
        )
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定取得"""
        return {
            'risk_free_rate': 0.02,
            'max_iterations': 1000,
            'tolerance': 1e-6,
            'max_position_weight': 0.2,
            'min_position_weight': 0.01,
            'max_sector_weight': 0.3,
            'max_correlation': 0.7,
            'max_volatility': 0.5,
            'min_liquidity': 1000000,
            'max_turnover': 0.5,
            'transaction_costs': 0.001,
            'optimization_methods': [
                'mean_variance',
                'black_litterman',
                'risk_parity',
                'max_sharpe',
                'min_variance',
                'equal_risk_contribution'
            ],
            'rebalancing_frequency': 'monthly',
            'lookback_period': 252,
            'volatility_target': 0.15,
            'correlation_threshold': 0.5
        }
    
    def optimize_sharpe_ratio(
        self,
        portfolio_data: Dict[str, Any],
        market_data: Optional[pd.DataFrame] = None,
        benchmark_data: Optional[pd.DataFrame] = None,
        optimization_method: str = 'max_sharpe'
    ) -> SharpeOptimizationResult:
        """
        シャープレシオ最適化実行
        
        Args:
            portfolio_data: ポートフォリオデータ
            market_data: 市場データ
            benchmark_data: ベンチマークデータ
            optimization_method: 最適化手法
            
        Returns:
            SharpeOptimizationResult: 最適化結果
        """
        try:
            # データ前処理
            processed_data = self._preprocess_portfolio_data(portfolio_data)
            
            # 現在のシャープレシオ計算
            original_sharpe = self._calculate_current_sharpe_ratio(processed_data)
            
            # 最適化実行
            if optimization_method == 'max_sharpe':
                optimized_result = self._optimize_max_sharpe(processed_data)
            elif optimization_method == 'mean_variance':
                optimized_result = self._optimize_mean_variance(processed_data)
            elif optimization_method == 'black_litterman':
                optimized_result = self._optimize_black_litterman(processed_data, market_data)
            elif optimization_method == 'risk_parity':
                optimized_result = self._optimize_risk_parity(processed_data)
            elif optimization_method == 'min_variance':
                optimized_result = self._optimize_min_variance(processed_data)
            elif optimization_method == 'equal_risk_contribution':
                optimized_result = self._optimize_equal_risk_contribution(processed_data)
            else:
                optimized_result = self._optimize_max_sharpe(processed_data)
            
            # 改善率計算
            improvement_ratio = (optimized_result['sharpe_ratio'] - original_sharpe) / original_sharpe if original_sharpe > 0 else 0
            target_achieved = improvement_ratio >= self.target_improvement
            
            # リスクメトリクス計算
            risk_metrics = self._calculate_risk_metrics(optimized_result, processed_data)
            
            # パフォーマンスメトリクス計算
            performance_metrics = self._calculate_performance_metrics(optimized_result, processed_data)
            
            return SharpeOptimizationResult(
                original_sharpe=original_sharpe,
                optimized_sharpe=optimized_result['sharpe_ratio'],
                improvement_ratio=improvement_ratio,
                target_achieved=target_achieved,
                optimization_method=optimization_method,
                portfolio_weights=optimized_result['weights'],
                risk_metrics=risk_metrics,
                performance_metrics=performance_metrics,
                optimization_timestamp=datetime.now().isoformat(),
                convergence_success=optimized_result.get('convergence', False),
                iterations=optimized_result.get('iterations', 0)
            )
            
        except Exception as e:
            self.logger.error(f"シャープレシオ最適化エラー: {e}")
            raise
    
    def _preprocess_portfolio_data(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """ポートフォリオデータ前処理"""
        try:
            processed = {
                'symbols': [],
                'weights': [],
                'returns': [],
                'volatilities': [],
                'sectors': [],
                'market_caps': [],
                'liquidity_scores': [],
                'correlations': []
            }
            
            positions = portfolio_data.get('positions', {})
            
            for symbol, position_data in positions.items():
                processed['symbols'].append(symbol)
                processed['weights'].append(position_data.get('weight', 0))
                processed['sectors'].append(position_data.get('sector', 'Unknown'))
                processed['market_caps'].append(position_data.get('market_cap', 0))
                processed['liquidity_scores'].append(position_data.get('liquidity_score', 0))
                
                # リターンデータ処理
                price_data = position_data.get('price_data', [])
                if price_data and len(price_data) > 1:
                    prices = [float(p.get('close', 0)) for p in price_data if p.get('close')]
                    if len(prices) > 1:
                        returns = np.diff(np.log(prices))
                        processed['returns'].append(returns)
                        processed['volatilities'].append(np.std(returns) * np.sqrt(252))
                    else:
                        processed['returns'].append(np.array([]))
                        processed['volatilities'].append(0.2)
                else:
                    processed['returns'].append(np.array([]))
                    processed['volatilities'].append(0.2)
            
            # 相関行列計算
            valid_returns = [r for r in processed['returns'] if len(r) > 0]
            if len(valid_returns) > 1:
                min_length = min(len(r) for r in valid_returns)
                returns_matrix = np.array([r[:min_length] for r in valid_returns])
                processed['correlations'] = np.corrcoef(returns_matrix)
            else:
                processed['correlations'] = np.eye(len(processed['symbols']))
            
            return processed
            
        except Exception as e:
            self.logger.error(f"ポートフォリオデータ前処理エラー: {e}")
            raise
    
    def _calculate_current_sharpe_ratio(self, processed_data: Dict[str, Any]) -> float:
        """現在のシャープレシオ計算"""
        try:
            weights = np.array(processed_data['weights'])
            returns = processed_data['returns']
            volatilities = np.array(processed_data['volatilities'])
            correlations = processed_data['correlations']
            
            if len(weights) == 0 or len(returns) == 0:
                return 0.0
            
            # ポートフォリオリターン計算
            portfolio_returns = []
            for i, weight in enumerate(weights):
                if i < len(returns) and len(returns[i]) > 0:
                    portfolio_returns.extend(returns[i] * weight)
            
            if not portfolio_returns:
                return 0.0
            
            # ポートフォリオ統計
            portfolio_return = np.mean(portfolio_returns) * 252  # 年率化
            portfolio_volatility = np.std(portfolio_returns) * np.sqrt(252)  # 年率化
            
            # シャープレシオ計算
            if portfolio_volatility > 0:
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
            else:
                sharpe_ratio = 0.0
            
            return sharpe_ratio
            
        except Exception as e:
            self.logger.error(f"現在のシャープレシオ計算エラー: {e}")
            return 0.0
    
    def _optimize_max_sharpe(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """最大シャープレシオ最適化"""
        try:
            n_assets = len(processed_data['symbols'])
            if n_assets == 0:
                return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
            
            # 期待リターン計算
            expected_returns = self._calculate_expected_returns(processed_data)
            
            # 共分散行列計算
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # 制約条件
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # ウェイト合計=1
            ]
            
            # 境界条件
            bounds = [(self.constraints.min_position_weight, self.constraints.max_position_weight) for _ in range(n_assets)]
            
            # 初期値（等ウェイト）
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # 目的関数（負のシャープレシオを最小化）
            def negative_sharpe_ratio(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                
                if portfolio_volatility == 0:
                    return -np.inf
                
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                return -sharpe
            
            # 最適化実行
            result = minimize(
                negative_sharpe_ratio,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': self.max_iterations, 'ftol': self.tolerance}
            )
            
            if result.success:
                weights = result.x
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            else:
                weights = x0
                sharpe_ratio = self._calculate_current_sharpe_ratio(processed_data)
            
            return {
                'weights': dict(zip(processed_data['symbols'], weights)),
                'sharpe_ratio': sharpe_ratio,
                'convergence': result.success,
                'iterations': result.nit
            }
            
        except Exception as e:
            self.logger.error(f"最大シャープレシオ最適化エラー: {e}")
            return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
    
    def _optimize_mean_variance(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """平均分散最適化"""
        try:
            n_assets = len(processed_data['symbols'])
            if n_assets == 0:
                return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
            
            expected_returns = self._calculate_expected_returns(processed_data)
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # 制約条件
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
            ]
            
            # 境界条件
            bounds = [(self.constraints.min_position_weight, self.constraints.max_position_weight) for _ in range(n_assets)]
            
            # 初期値
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # 目的関数（分散最小化）
            def portfolio_variance(weights):
                return np.dot(weights, np.dot(cov_matrix, weights))
            
            # 最適化実行
            result = minimize(
                portfolio_variance,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': self.max_iterations, 'ftol': self.tolerance}
            )
            
            if result.success:
                weights = result.x
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            else:
                weights = x0
                sharpe_ratio = self._calculate_current_sharpe_ratio(processed_data)
            
            return {
                'weights': dict(zip(processed_data['symbols'], weights)),
                'sharpe_ratio': sharpe_ratio,
                'convergence': result.success,
                'iterations': result.nit
            }
            
        except Exception as e:
            self.logger.error(f"平均分散最適化エラー: {e}")
            return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
    
    def _optimize_black_litterman(
        self,
        processed_data: Dict[str, Any],
        market_data: Optional[pd.DataFrame]
    ) -> Dict[str, Any]:
        """ブラック・リッターマンモデル最適化"""
        try:
            n_assets = len(processed_data['symbols'])
            if n_assets == 0:
                return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
            
            # 市場ウェイト（等ウェイトで初期化）
            market_weights = np.array([1.0 / n_assets] * n_assets)
            
            # 期待リターン計算
            expected_returns = self._calculate_expected_returns(processed_data)
            
            # ブラック・リッターマン期待リターン計算
            bl_returns = self._calculate_black_litterman_returns(
                expected_returns, processed_data, market_weights
            )
            
            # 最大シャープレシオ最適化
            return self._optimize_max_sharpe_with_returns(processed_data, bl_returns)
            
        except Exception as e:
            self.logger.error(f"ブラック・リッターマン最適化エラー: {e}")
            return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
    
    def _optimize_risk_parity(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """リスクパリティ最適化"""
        try:
            n_assets = len(processed_data['symbols'])
            if n_assets == 0:
                return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
            
            volatilities = np.array(processed_data['volatilities'])
            
            # リスクパリティウェイト計算
            inv_vol = 1.0 / volatilities
            weights = inv_vol / np.sum(inv_vol)
            
            # シャープレシオ計算
            expected_returns = self._calculate_expected_returns(processed_data)
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            return {
                'weights': dict(zip(processed_data['symbols'], weights)),
                'sharpe_ratio': sharpe_ratio,
                'convergence': True,
                'iterations': 1
            }
            
        except Exception as e:
            self.logger.error(f"リスクパリティ最適化エラー: {e}")
            return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
    
    def _optimize_min_variance(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """最小分散最適化"""
        try:
            n_assets = len(processed_data['symbols'])
            if n_assets == 0:
                return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
            
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # 制約条件
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
            ]
            
            # 境界条件
            bounds = [(self.constraints.min_position_weight, self.constraints.max_position_weight) for _ in range(n_assets)]
            
            # 初期値
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # 目的関数（分散最小化）
            def portfolio_variance(weights):
                return np.dot(weights, np.dot(cov_matrix, weights))
            
            # 最適化実行
            result = minimize(
                portfolio_variance,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': self.max_iterations, 'ftol': self.tolerance}
            )
            
            if result.success:
                weights = result.x
                expected_returns = self._calculate_expected_returns(processed_data)
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            else:
                weights = x0
                sharpe_ratio = self._calculate_current_sharpe_ratio(processed_data)
            
            return {
                'weights': dict(zip(processed_data['symbols'], weights)),
                'sharpe_ratio': sharpe_ratio,
                'convergence': result.success,
                'iterations': result.nit
            }
            
        except Exception as e:
            self.logger.error(f"最小分散最適化エラー: {e}")
            return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
    
    def _optimize_equal_risk_contribution(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """等リスク寄与最適化"""
        try:
            n_assets = len(processed_data['symbols'])
            if n_assets == 0:
                return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
            
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # 制約条件
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
            ]
            
            # 境界条件
            bounds = [(self.constraints.min_position_weight, self.constraints.max_position_weight) for _ in range(n_assets)]
            
            # 初期値
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # 目的関数（リスク寄与の分散最小化）
            def risk_contribution_variance(weights):
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                if portfolio_volatility == 0:
                    return 0
                
                risk_contributions = []
                for i in range(n_assets):
                    risk_contribution = weights[i] * np.dot(cov_matrix[i], weights) / portfolio_volatility
                    risk_contributions.append(risk_contribution)
                
                risk_contributions = np.array(risk_contributions)
                return np.var(risk_contributions)
            
            # 最適化実行
            result = minimize(
                risk_contribution_variance,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': self.max_iterations, 'ftol': self.tolerance}
            )
            
            if result.success:
                weights = result.x
                expected_returns = self._calculate_expected_returns(processed_data)
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            else:
                weights = x0
                sharpe_ratio = self._calculate_current_sharpe_ratio(processed_data)
            
            return {
                'weights': dict(zip(processed_data['symbols'], weights)),
                'sharpe_ratio': sharpe_ratio,
                'convergence': result.success,
                'iterations': result.nit
            }
            
        except Exception as e:
            self.logger.error(f"等リスク寄与最適化エラー: {e}")
            return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
    
    def _calculate_expected_returns(self, processed_data: Dict[str, Any]) -> np.ndarray:
        """期待リターン計算"""
        try:
            returns = processed_data['returns']
            expected_returns = []
            
            for return_data in returns:
                if len(return_data) > 0:
                    expected_return = np.mean(return_data) * 252  # 年率化
                else:
                    expected_return = 0.05  # デフォルト5%
                expected_returns.append(expected_return)
            
            return np.array(expected_returns)
            
        except Exception as e:
            self.logger.error(f"期待リターン計算エラー: {e}")
            return np.array([0.05] * len(processed_data['symbols']))
    
    def _calculate_covariance_matrix(self, processed_data: Dict[str, Any]) -> np.ndarray:
        """共分散行列計算"""
        try:
            returns = processed_data['returns']
            correlations = processed_data['correlations']
            volatilities = np.array(processed_data['volatilities'])
            
            if len(returns) == 0:
                return np.eye(len(processed_data['symbols']))
            
            # 共分散行列 = 相関行列 × ボラティリティ行列
            vol_matrix = np.outer(volatilities, volatilities)
            cov_matrix = correlations * vol_matrix
            
            # 正定値確保
            cov_matrix = self._ensure_positive_definite(cov_matrix)
            
            return cov_matrix
            
        except Exception as e:
            self.logger.error(f"共分散行列計算エラー: {e}")
            return np.eye(len(processed_data['symbols']))
    
    def _ensure_positive_definite(self, matrix: np.ndarray) -> np.ndarray:
        """正定値行列確保"""
        try:
            # 固有値分解
            eigenvalues, eigenvectors = np.linalg.eigh(matrix)
            
            # 負の固有値を小さな正の値に置換
            eigenvalues = np.maximum(eigenvalues, 1e-8)
            
            # 行列再構築
            matrix_pd = np.dot(eigenvectors, np.dot(np.diag(eigenvalues), eigenvectors.T))
            
            return matrix_pd
            
        except Exception as e:
            self.logger.error(f"正定値行列確保エラー: {e}")
            return matrix
    
    def _calculate_black_litterman_returns(
        self,
        expected_returns: np.ndarray,
        processed_data: Dict[str, Any],
        market_weights: np.ndarray
    ) -> np.ndarray:
        """ブラック・リッターマン期待リターン計算"""
        try:
            # リスク回避係数
            risk_aversion = 3.0
            
            # 市場リターン
            market_return = np.dot(market_weights, expected_returns)
            
            # 共分散行列
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # ブラック・リッターマン期待リターン
            bl_returns = risk_aversion * np.dot(cov_matrix, market_weights)
            
            return bl_returns
            
        except Exception as e:
            self.logger.error(f"ブラック・リッターマン計算エラー: {e}")
            return expected_returns
    
    def _optimize_max_sharpe_with_returns(
        self,
        processed_data: Dict[str, Any],
        expected_returns: np.ndarray
    ) -> Dict[str, Any]:
        """指定された期待リターンで最大シャープレシオ最適化"""
        try:
            n_assets = len(processed_data['symbols'])
            if n_assets == 0:
                return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
            
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # 制約条件
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
            ]
            
            # 境界条件
            bounds = [(self.constraints.min_position_weight, self.constraints.max_position_weight) for _ in range(n_assets)]
            
            # 初期値
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # 目的関数（負のシャープレシオを最小化）
            def negative_sharpe_ratio(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                
                if portfolio_volatility == 0:
                    return -np.inf
                
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                return -sharpe
            
            # 最適化実行
            result = minimize(
                negative_sharpe_ratio,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': self.max_iterations, 'ftol': self.tolerance}
            )
            
            if result.success:
                weights = result.x
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            else:
                weights = x0
                sharpe_ratio = self._calculate_current_sharpe_ratio(processed_data)
            
            return {
                'weights': dict(zip(processed_data['symbols'], weights)),
                'sharpe_ratio': sharpe_ratio,
                'convergence': result.success,
                'iterations': result.nit
            }
            
        except Exception as e:
            self.logger.error(f"最大シャープレシオ最適化エラー: {e}")
            return {'weights': {}, 'sharpe_ratio': 0.0, 'convergence': False, 'iterations': 0}
    
    def _calculate_risk_metrics(
        self,
        optimization_result: Dict[str, Any],
        processed_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """リスクメトリクス計算"""
        try:
            weights = np.array(list(optimization_result['weights'].values()))
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # ポートフォリオボラティリティ
            portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            
            # VaR計算（簡略化）
            var_95 = -1.645 * portfolio_volatility
            var_99 = -2.326 * portfolio_volatility
            
            # 最大ドローダウン（簡略化）
            max_drawdown = portfolio_volatility * 2.0
            
            return {
                'portfolio_volatility': portfolio_volatility,
                'var_95': var_95,
                'var_99': var_99,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': optimization_result['sharpe_ratio']
            }
            
        except Exception as e:
            self.logger.error(f"リスクメトリクス計算エラー: {e}")
            return {
                'portfolio_volatility': 0.2,
                'var_95': -0.05,
                'var_99': -0.08,
                'max_drawdown': 0.1,
                'sharpe_ratio': 0.5
            }
    
    def _calculate_performance_metrics(
        self,
        optimization_result: Dict[str, Any],
        processed_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """パフォーマンスメトリクス計算"""
        try:
            weights = np.array(list(optimization_result['weights'].values()))
            expected_returns = self._calculate_expected_returns(processed_data)
            cov_matrix = self._calculate_covariance_matrix(processed_data)
            
            # ポートフォリオリターン
            portfolio_return = np.dot(weights, expected_returns)
            
            # ポートフォリオボラティリティ
            portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            
            # シャープレシオ
            sharpe_ratio = optimization_result['sharpe_ratio']
            
            # ソルティノレシオ（簡略化）
            sortino_ratio = sharpe_ratio * 1.2  # 簡略化
            
            # カルマーレシオ（簡略化）
            calmar_ratio = portfolio_return / 0.1  # 最大ドローダウン10%と仮定
            
            return {
                'portfolio_return': portfolio_return,
                'portfolio_volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio
            }
            
        except Exception as e:
            self.logger.error(f"パフォーマンスメトリクス計算エラー: {e}")
            return {
                'portfolio_return': 0.05,
                'portfolio_volatility': 0.2,
                'sharpe_ratio': 0.5,
                'sortino_ratio': 0.6,
                'calmar_ratio': 0.5
            }
    
    def generate_optimization_recommendations(
        self,
        optimization_result: SharpeOptimizationResult
    ) -> Dict[str, Any]:
        """最適化推奨事項生成"""
        try:
            recommendations = {
                'optimization_summary': {
                    'original_sharpe': optimization_result.original_sharpe,
                    'optimized_sharpe': optimization_result.optimized_sharpe,
                    'improvement_ratio': optimization_result.improvement_ratio,
                    'target_achieved': optimization_result.target_achieved,
                    'method': optimization_result.optimization_method
                },
                'portfolio_weights': optimization_result.portfolio_weights,
                'risk_metrics': optimization_result.risk_metrics,
                'performance_metrics': optimization_result.performance_metrics,
                'action_items': [],
                'warnings': [],
                'timestamp': optimization_result.optimization_timestamp
            }
            
            # アクションアイテム生成
            if optimization_result.target_achieved:
                recommendations['action_items'].append({
                    'type': 'SUCCESS',
                    'message': f'シャープレシオ{optimization_result.improvement_ratio:.1%}向上を達成しました',
                    'priority': 'HIGH'
                })
            else:
                recommendations['action_items'].append({
                    'type': 'IMPROVEMENT_NEEDED',
                    'message': f'シャープレシオ向上が{optimization_result.improvement_ratio:.1%}と目標に達していません',
                    'priority': 'MEDIUM'
                })
            
            if not optimization_result.convergence_success:
                recommendations['warnings'].append({
                    'type': 'CONVERGENCE_WARNING',
                    'message': '最適化が収束しませんでした。結果を慎重に検討してください',
                    'priority': 'HIGH'
                })
            
            if optimization_result.risk_metrics.get('portfolio_volatility', 0) > 0.3:
                recommendations['warnings'].append({
                    'type': 'HIGH_VOLATILITY',
                    'message': 'ポートフォリオのボラティリティが高すぎます',
                    'priority': 'HIGH'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"最適化推奨事項生成エラー: {e}")
            return {'error': str(e)}
