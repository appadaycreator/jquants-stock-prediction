"""
分散投資スコア計算システム
ポートフォリオの分散投資効果を定量的に評価するシステム
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from scipy.stats import entropy
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DiversificationMetrics:
    """分散投資メトリクス"""
    overall_score: float
    sector_diversification: float
    correlation_diversification: float
    concentration_risk: float
    geographic_diversification: float
    market_cap_diversification: float
    liquidity_diversification: float
    risk_contribution_diversification: float
    entropy_score: float
    herfindahl_index: float
    effective_number_of_stocks: float
    diversification_ratio: float

@dataclass
class SectorAnalysis:
    """セクター分析"""
    sector_weights: Dict[str, float]
    sector_returns: Dict[str, float]
    sector_volatilities: Dict[str, float]
    sector_correlations: Dict[str, Dict[str, float]]
    sector_concentration: float
    sector_entropy: float

@dataclass
class CorrelationAnalysis:
    """相関分析"""
    correlation_matrix: np.ndarray
    average_correlation: float
    max_correlation: float
    min_correlation: float
    correlation_entropy: float
    correlation_clusters: List[List[int]]

class DiversificationScoringSystem:
    """分散投資スコア計算システム"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # 分散投資パラメータ
        self.max_sector_weight = self.config.get('max_sector_weight', 0.3)
        self.max_correlation = self.config.get('max_correlation', 0.7)
        self.min_effective_stocks = self.config.get('min_effective_stocks', 5)
        self.target_entropy = self.config.get('target_entropy', 0.8)
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定取得"""
        return {
            'max_sector_weight': 0.3,
            'max_correlation': 0.7,
            'min_effective_stocks': 5,
            'target_entropy': 0.8,
            'correlation_threshold': 0.5,
            'sector_threshold': 0.2,
            'geographic_regions': ['Japan', 'US', 'Europe', 'Asia', 'Other'],
            'market_cap_categories': ['Large', 'Mid', 'Small', 'Micro'],
            'liquidity_categories': ['High', 'Medium', 'Low']
        }
    
    def calculate_diversification_score(
        self,
        portfolio_weights: Dict[str, float],
        stock_data: List[Dict[str, Any]],
        market_data: Optional[pd.DataFrame] = None
    ) -> DiversificationMetrics:
        """
        分散投資スコア計算
        
        Args:
            portfolio_weights: ポートフォリオウェイト
            stock_data: 銘柄データ
            market_data: 市場データ
            
        Returns:
            DiversificationMetrics: 分散投資メトリクス
        """
        try:
            # データ前処理
            processed_data = self._preprocess_portfolio_data(portfolio_weights, stock_data)
            
            # セクター分散分析
            sector_analysis = self._analyze_sector_diversification(processed_data)
            
            # 相関分散分析
            correlation_analysis = self._analyze_correlation_diversification(processed_data)
            
            # 集中度リスク分析
            concentration_risk = self._analyze_concentration_risk(processed_data)
            
            # 地理的分散分析
            geographic_diversification = self._analyze_geographic_diversification(processed_data)
            
            # 時価総額分散分析
            market_cap_diversification = self._analyze_market_cap_diversification(processed_data)
            
            # 流動性分散分析
            liquidity_diversification = self._analyze_liquidity_diversification(processed_data)
            
            # リスク寄与分散分析
            risk_contribution_diversification = self._analyze_risk_contribution_diversification(
                processed_data, correlation_analysis
            )
            
            # エントロピースコア計算
            entropy_score = self._calculate_entropy_score(processed_data)
            
            # ハーフィンダール指数計算
            herfindahl_index = self._calculate_herfindahl_index(processed_data)
            
            # 実効銘柄数計算
            effective_number_of_stocks = self._calculate_effective_number_of_stocks(processed_data)
            
            # 分散投資比率計算
            diversification_ratio = self._calculate_diversification_ratio(processed_data, correlation_analysis)
            
            # 総合分散投資スコア計算
            overall_score = self._calculate_overall_diversification_score(
                sector_analysis.sector_entropy,
                correlation_analysis.correlation_entropy,
                concentration_risk,
                geographic_diversification,
                market_cap_diversification,
                liquidity_diversification,
                risk_contribution_diversification,
                entropy_score,
                effective_number_of_stocks
            )
            
            return DiversificationMetrics(
                overall_score=overall_score,
                sector_diversification=sector_analysis.sector_entropy,
                correlation_diversification=correlation_analysis.correlation_entropy,
                concentration_risk=concentration_risk,
                geographic_diversification=geographic_diversification,
                market_cap_diversification=market_cap_diversification,
                liquidity_diversification=liquidity_diversification,
                risk_contribution_diversification=risk_contribution_diversification,
                entropy_score=entropy_score,
                herfindahl_index=herfindahl_index,
                effective_number_of_stocks=effective_number_of_stocks,
                diversification_ratio=diversification_ratio
            )
            
        except Exception as e:
            self.logger.error(f"分散投資スコア計算エラー: {e}")
            raise
    
    def _preprocess_portfolio_data(
        self,
        portfolio_weights: Dict[str, float],
        stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """ポートフォリオデータ前処理"""
        try:
            processed = {
                'symbols': [],
                'weights': [],
                'sectors': [],
                'geographic_regions': [],
                'market_caps': [],
                'liquidity_scores': [],
                'returns': [],
                'volatilities': [],
                'correlations': []
            }
            
            # 銘柄データとウェイトのマッチング
            stock_dict = {stock['symbol']: stock for stock in stock_data}
            
            for symbol, weight in portfolio_weights.items():
                if symbol not in stock_dict or weight <= 0:
                    continue
                
                stock = stock_dict[symbol]
                
                processed['symbols'].append(symbol)
                processed['weights'].append(weight)
                processed['sectors'].append(stock.get('sector', 'Unknown'))
                processed['geographic_regions'].append(stock.get('region', 'Japan'))
                processed['market_caps'].append(stock.get('market_cap', 0))
                processed['liquidity_scores'].append(stock.get('liquidity_score', 0))
                
                # リターンデータ処理
                price_data = stock.get('price_data', [])
                if price_data and len(price_data) > 1:
                    prices = [float(p.get('close', 0)) for p in price_data if p.get('close')]
                    if len(prices) > 1:
                        returns = np.diff(np.log(prices))
                        processed['returns'].append(returns)
                        processed['volatilities'].append(np.std(returns) * np.sqrt(252))
                    else:
                        processed['returns'].append(np.array([]))
                        processed['volatilities'].append(0.0)
                else:
                    processed['returns'].append(np.array([]))
                    processed['volatilities'].append(0.0)
            
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
    
    def _analyze_sector_diversification(self, processed_data: Dict[str, Any]) -> SectorAnalysis:
        """セクター分散分析"""
        try:
            sectors = processed_data['sectors']
            weights = processed_data['weights']
            
            # セクター別ウェイト計算
            sector_weights = {}
            for sector, weight in zip(sectors, weights):
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
            
            # セクター別リターン・ボラティリティ計算
            sector_returns = {}
            sector_volatilities = {}
            sector_correlations = {}
            
            for sector in sector_weights.keys():
                sector_indices = [i for i, s in enumerate(sectors) if s == sector]
                
                if len(sector_indices) > 0:
                    # セクター内リターン計算
                    sector_return_data = [processed_data['returns'][i] for i in sector_indices if len(processed_data['returns'][i]) > 0]
                    if sector_return_data:
                        sector_returns[sector] = np.mean([np.mean(r) for r in sector_return_data])
                        sector_volatilities[sector] = np.mean([np.std(r) * np.sqrt(252) for r in sector_return_data])
                    else:
                        sector_returns[sector] = 0.0
                        sector_volatilities[sector] = 0.0
                    
                    # セクター内相関計算
                    if len(sector_indices) > 1:
                        sector_corr_data = []
                        for i in sector_indices:
                            for j in sector_indices:
                                if i != j and len(processed_data['returns'][i]) > 0 and len(processed_data['returns'][j]) > 0:
                                    corr = np.corrcoef(processed_data['returns'][i], processed_data['returns'][j])[0, 1]
                                    if not np.isnan(corr):
                                        sector_corr_data.append(corr)
                        sector_correlations[sector] = np.mean(sector_corr_data) if sector_corr_data else 0.0
                    else:
                        sector_correlations[sector] = 0.0
            
            # セクター集中度計算
            sector_weights_array = np.array(list(sector_weights.values()))
            sector_concentration = np.sum(sector_weights_array ** 2)
            
            # セクターエントロピー計算
            sector_weights_normalized = sector_weights_array / np.sum(sector_weights_array)
            sector_entropy = entropy(sector_weights_normalized)
            max_entropy = np.log(len(sector_weights))
            sector_entropy_normalized = sector_entropy / max_entropy if max_entropy > 0 else 0.0
            
            return SectorAnalysis(
                sector_weights=sector_weights,
                sector_returns=sector_returns,
                sector_volatilities=sector_volatilities,
                sector_correlations=sector_correlations,
                sector_concentration=sector_concentration,
                sector_entropy=sector_entropy_normalized
            )
            
        except Exception as e:
            self.logger.error(f"セクター分散分析エラー: {e}")
            return SectorAnalysis(
                sector_weights={},
                sector_returns={},
                sector_volatilities={},
                sector_correlations={},
                sector_concentration=1.0,
                sector_entropy=0.0
            )
    
    def _analyze_correlation_diversification(self, processed_data: Dict[str, Any]) -> CorrelationAnalysis:
        """相関分散分析"""
        try:
            correlation_matrix = processed_data['correlations']
            
            # 上三角行列の相関係数取得
            upper_triangle = correlation_matrix[np.triu_indices_from(correlation_matrix, k=1)]
            
            # 相関統計計算
            average_correlation = np.mean(upper_triangle)
            max_correlation = np.max(upper_triangle)
            min_correlation = np.min(upper_triangle)
            
            # 相関エントロピー計算
            correlation_entropy = self._calculate_correlation_entropy(correlation_matrix)
            
            # 相関クラスタリング
            correlation_clusters = self._perform_correlation_clustering(correlation_matrix)
            
            return CorrelationAnalysis(
                correlation_matrix=correlation_matrix,
                average_correlation=average_correlation,
                max_correlation=max_correlation,
                min_correlation=min_correlation,
                correlation_entropy=correlation_entropy,
                correlation_clusters=correlation_clusters
            )
            
        except Exception as e:
            self.logger.error(f"相関分散分析エラー: {e}")
            return CorrelationAnalysis(
                correlation_matrix=np.eye(len(processed_data['symbols'])),
                average_correlation=0.0,
                max_correlation=0.0,
                min_correlation=0.0,
                correlation_entropy=0.0,
                correlation_clusters=[]
            )
    
    def _calculate_correlation_entropy(self, correlation_matrix: np.ndarray) -> float:
        """相関エントロピー計算"""
        try:
            # 相関行列の固有値計算
            eigenvalues = np.linalg.eigvals(correlation_matrix)
            eigenvalues = np.real(eigenvalues)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            
            if len(eigenvalues) == 0:
                return 0.0
            
            # 固有値を正規化
            eigenvalues_normalized = eigenvalues / np.sum(eigenvalues)
            
            # エントロピー計算
            entropy_value = -np.sum(eigenvalues_normalized * np.log(eigenvalues_normalized + 1e-10))
            max_entropy = np.log(len(eigenvalues))
            
            return entropy_value / max_entropy if max_entropy > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"相関エントロピー計算エラー: {e}")
            return 0.0
    
    def _perform_correlation_clustering(self, correlation_matrix: np.ndarray) -> List[List[int]]:
        """相関クラスタリング"""
        try:
            n_assets = correlation_matrix.shape[0]
            
            if n_assets <= 2:
                return [[i] for i in range(n_assets)]
            
            # 距離行列計算（1 - 相関係数）
            distance_matrix = 1 - np.abs(correlation_matrix)
            
            # K-meansクラスタリング
            n_clusters = min(3, n_assets // 2)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(distance_matrix)
            
            # クラスター結果整理
            clusters = [[] for _ in range(n_clusters)]
            for i, label in enumerate(cluster_labels):
                clusters[label].append(i)
            
            return clusters
            
        except Exception as e:
            self.logger.error(f"相関クラスタリングエラー: {e}")
            return [[i] for i in range(correlation_matrix.shape[0])]
    
    def _analyze_concentration_risk(self, processed_data: Dict[str, Any]) -> float:
        """集中度リスク分析"""
        try:
            weights = np.array(processed_data['weights'])
            
            # ハーフィンダール指数計算
            herfindahl_index = np.sum(weights ** 2)
            
            # 最大ウェイト
            max_weight = np.max(weights)
            
            # 上位5銘柄の集中度
            sorted_weights = np.sort(weights)[::-1]
            top5_concentration = np.sum(sorted_weights[:5])
            
            # 集中度リスクスコア（0-1、低いほど良い）
            concentration_risk = (herfindahl_index + max_weight + top5_concentration) / 3.0
            
            return min(1.0, concentration_risk)
            
        except Exception as e:
            self.logger.error(f"集中度リスク分析エラー: {e}")
            return 1.0
    
    def _analyze_geographic_diversification(self, processed_data: Dict[str, Any]) -> float:
        """地理的分散分析"""
        try:
            regions = processed_data['geographic_regions']
            weights = processed_data['weights']
            
            # 地域別ウェイト計算
            region_weights = {}
            for region, weight in zip(regions, weights):
                region_weights[region] = region_weights.get(region, 0) + weight
            
            # 地域エントロピー計算
            region_weights_array = np.array(list(region_weights.values()))
            region_weights_normalized = region_weights_array / np.sum(region_weights_array)
            
            region_entropy = entropy(region_weights_normalized)
            max_entropy = np.log(len(region_weights))
            
            return region_entropy / max_entropy if max_entropy > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"地理的分散分析エラー: {e}")
            return 0.0
    
    def _analyze_market_cap_diversification(self, processed_data: Dict[str, Any]) -> float:
        """時価総額分散分析"""
        try:
            market_caps = processed_data['market_caps']
            weights = processed_data['weights']
            
            # 時価総額カテゴリ分類
            market_cap_categories = []
            for market_cap in market_caps:
                if market_cap > 1e12:  # 1兆円以上
                    category = 'Large'
                elif market_cap > 1e11:  # 1000億円以上
                    category = 'Mid'
                elif market_cap > 1e10:  # 100億円以上
                    category = 'Small'
                else:
                    category = 'Micro'
                market_cap_categories.append(category)
            
            # カテゴリ別ウェイト計算
            category_weights = {}
            for category, weight in zip(market_cap_categories, weights):
                category_weights[category] = category_weights.get(category, 0) + weight
            
            # カテゴリエントロピー計算
            category_weights_array = np.array(list(category_weights.values()))
            category_weights_normalized = category_weights_array / np.sum(category_weights_array)
            
            category_entropy = entropy(category_weights_normalized)
            max_entropy = np.log(len(category_weights))
            
            return category_entropy / max_entropy if max_entropy > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"時価総額分散分析エラー: {e}")
            return 0.0
    
    def _analyze_liquidity_diversification(self, processed_data: Dict[str, Any]) -> float:
        """流動性分散分析"""
        try:
            liquidity_scores = processed_data['liquidity_scores']
            weights = processed_data['weights']
            
            # 流動性カテゴリ分類
            liquidity_categories = []
            for score in liquidity_scores:
                if score > 1e6:  # 高流動性
                    category = 'High'
                elif score > 1e5:  # 中流動性
                    category = 'Medium'
                else:  # 低流動性
                    category = 'Low'
                liquidity_categories.append(category)
            
            # カテゴリ別ウェイト計算
            category_weights = {}
            for category, weight in zip(liquidity_categories, weights):
                category_weights[category] = category_weights.get(category, 0) + weight
            
            # カテゴリエントロピー計算
            category_weights_array = np.array(list(category_weights.values()))
            category_weights_normalized = category_weights_array / np.sum(category_weights_array)
            
            category_entropy = entropy(category_weights_normalized)
            max_entropy = np.log(len(category_weights))
            
            return category_entropy / max_entropy if max_entropy > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"流動性分散分析エラー: {e}")
            return 0.0
    
    def _analyze_risk_contribution_diversification(
        self,
        processed_data: Dict[str, Any],
        correlation_analysis: CorrelationAnalysis
    ) -> float:
        """リスク寄与分散分析"""
        try:
            weights = np.array(processed_data['weights'])
            volatilities = np.array(processed_data['volatilities'])
            correlation_matrix = correlation_analysis.correlation_matrix
            
            # ポートフォリオボラティリティ計算
            portfolio_variance = np.dot(weights, np.dot(correlation_matrix, weights * volatilities))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            if portfolio_volatility == 0:
                return 0.0
            
            # 各銘柄のリスク寄与計算
            risk_contributions = []
            for i in range(len(weights)):
                # 銘柄iのリスク寄与
                risk_contribution = weights[i] * np.dot(correlation_matrix[i], weights * volatilities) / portfolio_volatility
                risk_contributions.append(risk_contribution)
            
            # リスク寄与の分散度計算
            risk_contributions_array = np.array(risk_contributions)
            risk_contributions_normalized = risk_contributions_array / np.sum(risk_contributions_array)
            
            # エントロピー計算
            risk_entropy = entropy(risk_contributions_normalized)
            max_entropy = np.log(len(risk_contributions))
            
            return risk_entropy / max_entropy if max_entropy > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"リスク寄与分散分析エラー: {e}")
            return 0.0
    
    def _calculate_entropy_score(self, processed_data: Dict[str, Any]) -> float:
        """エントロピースコア計算"""
        try:
            weights = np.array(processed_data['weights'])
            weights_normalized = weights / np.sum(weights)
            
            # エントロピー計算
            entropy_value = entropy(weights_normalized)
            max_entropy = np.log(len(weights))
            
            return entropy_value / max_entropy if max_entropy > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"エントロピースコア計算エラー: {e}")
            return 0.0
    
    def _calculate_herfindahl_index(self, processed_data: Dict[str, Any]) -> float:
        """ハーフィンダール指数計算"""
        try:
            weights = np.array(processed_data['weights'])
            herfindahl_index = np.sum(weights ** 2)
            
            return herfindahl_index
            
        except Exception as e:
            self.logger.error(f"ハーフィンダール指数計算エラー: {e}")
            return 1.0
    
    def _calculate_effective_number_of_stocks(self, processed_data: Dict[str, Any]) -> float:
        """実効銘柄数計算"""
        try:
            weights = np.array(processed_data['weights'])
            weights_normalized = weights / np.sum(weights)
            
            # エントロピーベース実効銘柄数
            entropy_value = entropy(weights_normalized)
            effective_number = np.exp(entropy_value)
            
            return effective_number
            
        except Exception as e:
            self.logger.error(f"実効銘柄数計算エラー: {e}")
            return 1.0
    
    def _calculate_diversification_ratio(
        self,
        processed_data: Dict[str, Any],
        correlation_analysis: CorrelationAnalysis
    ) -> float:
        """分散投資比率計算"""
        try:
            weights = np.array(processed_data['weights'])
            volatilities = np.array(processed_data['volatilities'])
            correlation_matrix = correlation_analysis.correlation_matrix
            
            # 等ウェイトポートフォリオのボラティリティ
            equal_weights = np.ones(len(weights)) / len(weights)
            equal_weight_volatility = np.sqrt(np.dot(equal_weights, np.dot(correlation_matrix, equal_weights * volatilities)))
            
            # 実際のポートフォリオボラティリティ
            actual_volatility = np.sqrt(np.dot(weights, np.dot(correlation_matrix, weights * volatilities)))
            
            # 分散投資比率
            diversification_ratio = equal_weight_volatility / actual_volatility if actual_volatility > 0 else 1.0
            
            return diversification_ratio
            
        except Exception as e:
            self.logger.error(f"分散投資比率計算エラー: {e}")
            return 1.0
    
    def _calculate_overall_diversification_score(
        self,
        sector_entropy: float,
        correlation_entropy: float,
        concentration_risk: float,
        geographic_diversification: float,
        market_cap_diversification: float,
        liquidity_diversification: float,
        risk_contribution_diversification: float,
        entropy_score: float,
        effective_number_of_stocks: float
    ) -> float:
        """総合分散投資スコア計算"""
        try:
            # 各要素の重み
            weights = {
                'sector': 0.25,
                'correlation': 0.20,
                'concentration': 0.15,
                'geographic': 0.10,
                'market_cap': 0.10,
                'liquidity': 0.10,
                'risk_contribution': 0.10
            }
            
            # 集中度リスクは逆転（低いほど良い）
            concentration_score = 1.0 - concentration_risk
            
            # 実効銘柄数による調整
            effective_stocks_score = min(1.0, effective_number_of_stocks / 10.0)
            
            # 総合スコア計算
            overall_score = (
                sector_entropy * weights['sector'] +
                correlation_entropy * weights['correlation'] +
                concentration_score * weights['concentration'] +
                geographic_diversification * weights['geographic'] +
                market_cap_diversification * weights['market_cap'] +
                liquidity_diversification * weights['liquidity'] +
                risk_contribution_diversification * weights['risk_contribution']
            )
            
            # 実効銘柄数による調整
            overall_score = overall_score * effective_stocks_score
            
            return min(1.0, max(0.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"総合分散投資スコア計算エラー: {e}")
            return 0.5
    
    def generate_diversification_recommendations(
        self,
        diversification_metrics: DiversificationMetrics,
        current_portfolio: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """分散投資推奨事項生成"""
        try:
            recommendations = {
                'overall_assessment': {
                    'score': diversification_metrics.overall_score,
                    'grade': self._get_diversification_grade(diversification_metrics.overall_score),
                    'status': self._get_diversification_status(diversification_metrics.overall_score)
                },
                'detailed_analysis': {
                    'sector_diversification': {
                        'score': diversification_metrics.sector_diversification,
                        'recommendation': self._get_sector_recommendation(diversification_metrics.sector_diversification)
                    },
                    'correlation_diversification': {
                        'score': diversification_metrics.correlation_diversification,
                        'recommendation': self._get_correlation_recommendation(diversification_metrics.correlation_diversification)
                    },
                    'concentration_risk': {
                        'score': diversification_metrics.concentration_risk,
                        'recommendation': self._get_concentration_recommendation(diversification_metrics.concentration_risk)
                    }
                },
                'action_items': [],
                'warnings': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # アクションアイテム生成
            if diversification_metrics.overall_score < 0.6:
                recommendations['action_items'].append({
                    'type': 'DIVERSIFICATION',
                    'message': '分散投資スコアが低いです。より多くの銘柄・セクターへの分散を検討してください。',
                    'priority': 'HIGH'
                })
            
            if diversification_metrics.sector_diversification < 0.5:
                recommendations['action_items'].append({
                    'type': 'SECTOR_DIVERSIFICATION',
                    'message': 'セクター分散が不十分です。異なるセクターへの投資を検討してください。',
                    'priority': 'MEDIUM'
                })
            
            if diversification_metrics.concentration_risk > 0.3:
                recommendations['warnings'].append({
                    'type': 'CONCENTRATION_WARNING',
                    'message': '集中度リスクが高いです。特定銘柄への過度な集中を避けてください。',
                    'priority': 'HIGH'
                })
            
            if diversification_metrics.effective_number_of_stocks < 5:
                recommendations['action_items'].append({
                    'type': 'PORTFOLIO_SIZE',
                    'message': '実効銘柄数が少ないです。より多くの銘柄への分散を検討してください。',
                    'priority': 'MEDIUM'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"分散投資推奨事項生成エラー: {e}")
            return {'error': str(e)}
    
    def _get_diversification_grade(self, score: float) -> str:
        """分散投資グレード取得"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.5:
            return 'C'
        else:
            return 'D'
    
    def _get_diversification_status(self, score: float) -> str:
        """分散投資ステータス取得"""
        if score >= 0.8:
            return 'EXCELLENT'
        elif score >= 0.6:
            return 'GOOD'
        elif score >= 0.4:
            return 'FAIR'
        else:
            return 'POOR'
    
    def _get_sector_recommendation(self, score: float) -> str:
        """セクター推奨事項取得"""
        if score >= 0.8:
            return 'セクター分散は良好です。'
        elif score >= 0.6:
            return 'セクター分散を改善する余地があります。'
        else:
            return 'セクター分散が不十分です。異なるセクターへの投資を検討してください。'
    
    def _get_correlation_recommendation(self, score: float) -> str:
        """相関推奨事項取得"""
        if score >= 0.8:
            return '相関分散は良好です。'
        elif score >= 0.6:
            return '相関分散を改善する余地があります。'
        else:
            return '相関分散が不十分です。低相関銘柄への投資を検討してください。'
    
    def _get_concentration_recommendation(self, score: float) -> str:
        """集中度推奨事項取得"""
        if score <= 0.2:
            return '集中度リスクは低いです。'
        elif score <= 0.4:
            return '集中度リスクに注意が必要です。'
        else:
            return '集中度リスクが高いです。特定銘柄への過度な集中を避けてください。'
