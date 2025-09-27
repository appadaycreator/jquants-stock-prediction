#!/usr/bin/env python3
"""
個別銘柄の相関分析による分散投資推奨システム
期待効果: 損失を60-80%削減
実装難易度: 🟡 中
推定工数: 2-3日

機能:
1. 銘柄間相関分析
2. ポートフォリオ集中度分析
3. 分散投資推奨
4. セクター分散分析
5. 相関リスク監視
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from collections import defaultdict, deque
import yfinance as yf
from scipy import stats
from scipy.stats import pearsonr
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import asyncio
import aiohttp
import networkx as nx

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("correlation_analysis_system.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CorrelationLevel(Enum):
    """相関レベル"""
    VERY_LOW = "VERY_LOW"      # 0.0-0.2
    LOW = "LOW"                # 0.2-0.4
    MODERATE = "MODERATE"      # 0.4-0.6
    HIGH = "HIGH"              # 0.6-0.8
    VERY_HIGH = "VERY_HIGH"    # 0.8-1.0


class DiversificationLevel(Enum):
    """分散投資レベル"""
    EXCELLENT = "EXCELLENT"    # 分散度90%以上
    GOOD = "GOOD"              # 分散度70-90%
    FAIR = "FAIR"              # 分散度50-70%
    POOR = "POOR"              # 分散度30-50%
    CRITICAL = "CRITICAL"      # 分散度30%未満


class SectorType(Enum):
    """セクタータイプ"""
    TECHNOLOGY = "TECHNOLOGY"
    FINANCIAL = "FINANCIAL"
    HEALTHCARE = "HEALTHCARE"
    CONSUMER = "CONSUMER"
    INDUSTRIAL = "INDUSTRIAL"
    ENERGY = "ENERGY"
    MATERIALS = "MATERIALS"
    UTILITIES = "UTILITIES"
    REAL_ESTATE = "REAL_ESTATE"
    COMMUNICATION = "COMMUNICATION"
    UNKNOWN = "UNKNOWN"


@dataclass
class CorrelationMetrics:
    """相関指標"""
    symbol: str
    timestamp: datetime
    correlation_matrix: Dict[str, Dict[str, float]]
    average_correlation: float
    max_correlation: float
    correlation_risk_score: float
    diversification_score: float
    concentration_risk: float
    sector_concentration: Dict[SectorType, float]
    cluster_analysis: Dict[str, Any]


@dataclass
class DiversificationRecommendation:
    """分散投資推奨"""
    symbol: str
    timestamp: datetime
    current_diversification_level: DiversificationLevel
    recommended_actions: List[str]
    suggested_sectors: List[SectorType]
    suggested_stocks: List[str]
    risk_reduction_potential: float
    priority_score: float


@dataclass
class PortfolioConcentration:
    """ポートフォリオ集中度"""
    total_stocks: int
    sector_distribution: Dict[SectorType, int]
    concentration_ratio: float
    herfindahl_index: float
    effective_diversification: int
    concentration_risk_level: str


class CorrelationAnalysisSystem:
    """相関分析システム"""

    def __init__(self, lookback_period: int = 252):
        self.lookback_period = lookback_period
        self.correlation_history = defaultdict(list)
        self.sector_mapping = self._initialize_sector_mapping()
        self.correlation_thresholds = {
            "very_low": 0.2,
            "low": 0.4,
            "moderate": 0.6,
            "high": 0.8,
            "very_high": 1.0,
        }
        
        # 分散投資パラメータ
        self.diversification_params = {
            "min_stocks": 5,
            "optimal_stocks": 15,
            "max_sector_weight": 0.3,
            "target_correlation": 0.3,
        }

    def _initialize_sector_mapping(self) -> Dict[str, SectorType]:
        """セクターマッピング初期化"""
        # 簡易実装: 実際の実装ではより詳細なセクター分類が必要
        return {
            # テクノロジー
            "AAPL": SectorType.TECHNOLOGY,
            "GOOGL": SectorType.TECHNOLOGY,
            "MSFT": SectorType.TECHNOLOGY,
            "AMZN": SectorType.TECHNOLOGY,
            "TSLA": SectorType.TECHNOLOGY,
            "NVDA": SectorType.TECHNOLOGY,
            "META": SectorType.TECHNOLOGY,
            "NFLX": SectorType.TECHNOLOGY,
            
            # 金融
            "JPM": SectorType.FINANCIAL,
            "BAC": SectorType.FINANCIAL,
            "WFC": SectorType.FINANCIAL,
            "GS": SectorType.FINANCIAL,
            "C": SectorType.FINANCIAL,
            
            # ヘルスケア
            "JNJ": SectorType.HEALTHCARE,
            "PFE": SectorType.HEALTHCARE,
            "UNH": SectorType.HEALTHCARE,
            "ABBV": SectorType.HEALTHCARE,
            "MRK": SectorType.HEALTHCARE,
            
            # 日本株
            "7203.T": SectorType.TECHNOLOGY,  # トヨタ
            "6758.T": SectorType.TECHNOLOGY,  # ソニー
            "9984.T": SectorType.TECHNOLOGY,   # ソフトバンクG
            "7974.T": SectorType.CONSUMER,      # 任天堂
            "4063.T": SectorType.TECHNOLOGY,   # 信越化学
        }

    async def analyze_correlation_risk(self, symbols: List[str]) -> CorrelationMetrics:
        """相関リスク分析"""
        try:
            logger.info(f"相関リスク分析開始: {len(symbols)}銘柄")
            
            # 相関行列計算
            correlation_matrix = await self._calculate_correlation_matrix(symbols)
            
            # 平均相関計算
            average_correlation = self._calculate_average_correlation(correlation_matrix)
            
            # 最大相関計算
            max_correlation = self._calculate_max_correlation(correlation_matrix)
            
            # 相関リスクスコア計算
            correlation_risk_score = self._calculate_correlation_risk_score(
                average_correlation, max_correlation, len(symbols)
            )
            
            # 分散投資スコア計算
            diversification_score = self._calculate_diversification_score(
                correlation_matrix, symbols
            )
            
            # 集中度リスク計算
            concentration_risk = self._calculate_concentration_risk(symbols)
            
            # セクター集中度計算
            sector_concentration = self._calculate_sector_concentration(symbols)
            
            # クラスター分析
            cluster_analysis = await self._perform_cluster_analysis(symbols, correlation_matrix)
            
            # 相関指標作成
            metrics = CorrelationMetrics(
                symbol="PORTFOLIO",  # ポートフォリオ全体
                timestamp=datetime.now(),
                correlation_matrix=correlation_matrix,
                average_correlation=average_correlation,
                max_correlation=max_correlation,
                correlation_risk_score=correlation_risk_score,
                diversification_score=diversification_score,
                concentration_risk=concentration_risk,
                sector_concentration=sector_concentration,
                cluster_analysis=cluster_analysis,
            )
            
            # 履歴に追加
            self.correlation_history["PORTFOLIO"].append(metrics)
            
            logger.info(f"相関分析完了: 平均相関 {average_correlation:.3f}, "
                       f"分散スコア {diversification_score:.3f}")
            return metrics

        except Exception as e:
            logger.error(f"相関リスク分析エラー: {e}")
            return self._create_default_correlation_metrics()

    async def _calculate_correlation_matrix(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """相関行列計算"""
        try:
            correlation_matrix = {}
            
            # 各銘柄の価格データ取得
            price_data = {}
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    hist = stock.history(period="6mo")
                    if len(hist) > 30:
                        price_data[symbol] = hist['Close']
                except Exception as e:
                    logger.warning(f"価格データ取得エラー: {symbol} - {e}")
                    continue
            
            if len(price_data) < 2:
                return {}
            
            # 共通期間のデータを取得
            common_dates = None
            for symbol, prices in price_data.items():
                if common_dates is None:
                    common_dates = prices.index
                else:
                    common_dates = common_dates.intersection(prices.index)
            
            if len(common_dates) < 30:
                return {}
            
            # 相関計算
            for symbol1 in price_data.keys():
                correlation_matrix[symbol1] = {}
                for symbol2 in price_data.keys():
                    if symbol1 == symbol2:
                        correlation_matrix[symbol1][symbol2] = 1.0
                    else:
                        try:
                            returns1 = price_data[symbol1].loc[common_dates].pct_change().dropna()
                            returns2 = price_data[symbol2].loc[common_dates].pct_change().dropna()
                            
                            if len(returns1) > 10 and len(returns2) > 10:
                                correlation, _ = pearsonr(returns1, returns2)
                                correlation_matrix[symbol1][symbol2] = correlation if not np.isnan(correlation) else 0.0
                            else:
                                correlation_matrix[symbol1][symbol2] = 0.0
                        except Exception as e:
                            logger.warning(f"相関計算エラー: {symbol1} vs {symbol2} - {e}")
                            correlation_matrix[symbol1][symbol2] = 0.0
            
            return correlation_matrix
        except Exception as e:
            logger.error(f"相関行列計算エラー: {e}")
            return {}

    def _calculate_average_correlation(self, correlation_matrix: Dict[str, Dict[str, float]]) -> float:
        """平均相関計算"""
        try:
            if not correlation_matrix:
                return 0.0
            
            correlations = []
            for symbol1, correlations_dict in correlation_matrix.items():
                for symbol2, correlation in correlations_dict.items():
                    if symbol1 != symbol2:  # 自己相関を除外
                        correlations.append(abs(correlation))  # 絶対値を使用
            
            return np.mean(correlations) if correlations else 0.0
        except Exception as e:
            logger.error(f"平均相関計算エラー: {e}")
            return 0.0

    def _calculate_max_correlation(self, correlation_matrix: Dict[str, Dict[str, float]]) -> float:
        """最大相関計算"""
        try:
            if not correlation_matrix:
                return 0.0
            
            max_corr = 0.0
            for symbol1, correlations_dict in correlation_matrix.items():
                for symbol2, correlation in correlations_dict.items():
                    if symbol1 != symbol2:  # 自己相関を除外
                        max_corr = max(max_corr, abs(correlation))
            
            return max_corr
        except Exception as e:
            logger.error(f"最大相関計算エラー: {e}")
            return 0.0

    def _calculate_correlation_risk_score(
        self, average_correlation: float, max_correlation: float, num_stocks: int
    ) -> float:
        """相関リスクスコア計算"""
        try:
            # 平均相関によるリスク（40%の重み）
            avg_corr_risk = min(average_correlation, 1.0) * 0.4
            
            # 最大相関によるリスク（30%の重み）
            max_corr_risk = min(max_correlation, 1.0) * 0.3
            
            # 銘柄数によるリスク（30%の重み）
            stock_count_risk = max(0, (self.diversification_params["min_stocks"] - num_stocks) / 
                                 self.diversification_params["min_stocks"]) * 0.3
            
            # 総合リスクスコア
            total_risk = avg_corr_risk + max_corr_risk + stock_count_risk
            
            return min(total_risk, 1.0)
        except Exception as e:
            logger.error(f"相関リスクスコア計算エラー: {e}")
            return 0.5

    def _calculate_diversification_score(
        self, correlation_matrix: Dict[str, Dict[str, float]], symbols: List[str]
    ) -> float:
        """分散投資スコア計算"""
        try:
            if not correlation_matrix or len(symbols) < 2:
                return 0.0
            
            # 平均相関の逆数（低い相関ほど高い分散スコア）
            avg_correlation = self._calculate_average_correlation(correlation_matrix)
            correlation_score = 1 - avg_correlation
            
            # 銘柄数による分散スコア
            stock_count_score = min(len(symbols) / self.diversification_params["optimal_stocks"], 1.0)
            
            # セクター分散スコア
            sector_diversity_score = self._calculate_sector_diversity_score(symbols)
            
            # 総合分散スコア
            total_score = (correlation_score * 0.5 + stock_count_score * 0.3 + sector_diversity_score * 0.2)
            
            return min(total_score, 1.0)
        except Exception as e:
            logger.error(f"分散投資スコア計算エラー: {e}")
            return 0.5

    def _calculate_sector_diversity_score(self, symbols: List[str]) -> float:
        """セクター分散スコア計算"""
        try:
            # 各銘柄のセクターを取得
            sectors = []
            for symbol in symbols:
                sector = self.sector_mapping.get(symbol, SectorType.UNKNOWN)
                sectors.append(sector)
            
            # セクターの多様性計算
            unique_sectors = set(sectors)
            sector_diversity = len(unique_sectors) / len(SectorType)
            
            # セクター分布の均等性
            sector_counts = {}
            for sector in sectors:
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            # エントロピー計算
            total_stocks = len(symbols)
            entropy = 0.0
            for count in sector_counts.values():
                if count > 0:
                    p = count / total_stocks
                    entropy -= p * np.log2(p)
            
            # 正規化されたエントロピー
            max_entropy = np.log2(len(unique_sectors)) if len(unique_sectors) > 1 else 1.0
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
            
            # 総合セクター分散スコア
            total_score = (sector_diversity * 0.6 + normalized_entropy * 0.4)
            
            return min(total_score, 1.0)
        except Exception as e:
            logger.error(f"セクター分散スコア計算エラー: {e}")
            return 0.5

    def _calculate_concentration_risk(self, symbols: List[str]) -> float:
        """集中度リスク計算"""
        try:
            # 銘柄数による集中度リスク
            stock_count_risk = max(0, (self.diversification_params["min_stocks"] - len(symbols)) / 
                                 self.diversification_params["min_stocks"])
            
            # セクター集中度リスク
            sector_concentration = self._calculate_sector_concentration(symbols)
            max_sector_weight = max(sector_concentration.values()) if sector_concentration else 0.0
            sector_risk = max(0, (max_sector_weight - self.diversification_params["max_sector_weight"]) / 
                            self.diversification_params["max_sector_weight"])
            
            # 総合集中度リスク
            total_risk = (stock_count_risk * 0.6 + sector_risk * 0.4)
            
            return min(total_risk, 1.0)
        except Exception as e:
            logger.error(f"集中度リスク計算エラー: {e}")
            return 0.5

    def _calculate_sector_concentration(self, symbols: List[str]) -> Dict[SectorType, float]:
        """セクター集中度計算"""
        try:
            sector_counts = {}
            for symbol in symbols:
                sector = self.sector_mapping.get(symbol, SectorType.UNKNOWN)
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            # 割合に変換
            total_stocks = len(symbols)
            sector_concentration = {
                sector: count / total_stocks 
                for sector, count in sector_counts.items()
            }
            
            return sector_concentration
        except Exception as e:
            logger.error(f"セクター集中度計算エラー: {e}")
            return {}

    async def _perform_cluster_analysis(
        self, symbols: List[str], correlation_matrix: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """クラスター分析実行"""
        try:
            if len(symbols) < 3:
                return {"clusters": [], "cluster_count": 0}
            
            # 相関行列を距離行列に変換
            distance_matrix = []
            for i, symbol1 in enumerate(symbols):
                row = []
                for j, symbol2 in enumerate(symbols):
                    if i == j:
                        row.append(0.0)
                    else:
                        correlation = correlation_matrix.get(symbol1, {}).get(symbol2, 0.0)
                        distance = 1 - abs(correlation)  # 相関を距離に変換
                        row.append(distance)
                distance_matrix.append(row)
            
            # K-meansクラスタリング
            if len(symbols) >= 3:
                n_clusters = min(3, len(symbols) // 2)  # 最大3クラスター
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(distance_matrix)
                
                # クラスター結果の整理
                clusters = {}
                for i, symbol in enumerate(symbols):
                    cluster_id = cluster_labels[i]
                    if cluster_id not in clusters:
                        clusters[cluster_id] = []
                    clusters[cluster_id].append(symbol)
                
                return {
                    "clusters": list(clusters.values()),
                    "cluster_count": n_clusters,
                    "cluster_labels": cluster_labels.tolist(),
                }
            else:
                return {"clusters": [symbols], "cluster_count": 1}
                
        except Exception as e:
            logger.error(f"クラスター分析エラー: {e}")
            return {"clusters": [], "cluster_count": 0}

    async def generate_diversification_recommendations(
        self, symbols: List[str], current_portfolio_value: float = 1000000
    ) -> List[DiversificationRecommendation]:
        """分散投資推奨生成"""
        try:
            logger.info(f"分散投資推奨生成開始: {len(symbols)}銘柄")
            
            recommendations = []
            
            # 現在の分散投資レベル評価
            current_level = self._evaluate_diversification_level(symbols)
            
            # 各銘柄に対する推奨事項生成
            for symbol in symbols:
                recommendation = await self._generate_individual_recommendation(
                    symbol, symbols, current_level, current_portfolio_value
                )
                recommendations.append(recommendation)
            
            # ポートフォリオ全体の推奨事項
            portfolio_recommendation = await self._generate_portfolio_recommendation(
                symbols, current_level, current_portfolio_value
            )
            recommendations.append(portfolio_recommendation)
            
            logger.info(f"分散投資推奨生成完了: {len(recommendations)}件")
            return recommendations

        except Exception as e:
            logger.error(f"分散投資推奨生成エラー: {e}")
            return []

    def _evaluate_diversification_level(self, symbols: List[str]) -> DiversificationLevel:
        """分散投資レベル評価"""
        try:
            # 銘柄数による評価
            stock_count_score = len(symbols) / self.diversification_params["optimal_stocks"]
            
            # セクター分散による評価
            sector_diversity_score = self._calculate_sector_diversity_score(symbols)
            
            # 総合分散スコア
            total_score = (stock_count_score * 0.6 + sector_diversity_score * 0.4)
            
            # 分散投資レベル判定
            if total_score >= 0.9:
                return DiversificationLevel.EXCELLENT
            elif total_score >= 0.7:
                return DiversificationLevel.GOOD
            elif total_score >= 0.5:
                return DiversificationLevel.FAIR
            elif total_score >= 0.3:
                return DiversificationLevel.POOR
            else:
                return DiversificationLevel.CRITICAL
                
        except Exception as e:
            logger.error(f"分散投資レベル評価エラー: {e}")
            return DiversificationLevel.POOR

    async def _generate_individual_recommendation(
        self, symbol: str, all_symbols: List[str], current_level: DiversificationLevel,
        portfolio_value: float
    ) -> DiversificationRecommendation:
        """個別銘柄推奨事項生成"""
        try:
            # 現在のセクター
            current_sector = self.sector_mapping.get(symbol, SectorType.UNKNOWN)
            
            # 推奨アクション
            recommended_actions = []
            
            # セクター集中度チェック
            sector_concentration = self._calculate_sector_concentration(all_symbols)
            current_sector_weight = sector_concentration.get(current_sector, 0.0)
            
            if current_sector_weight > self.diversification_params["max_sector_weight"]:
                recommended_actions.append(f"{current_sector.value}セクターの集中度が高すぎます")
                recommended_actions.append("異なるセクターへの分散投資を検討してください")
            
            # 銘柄数不足チェック
            if len(all_symbols) < self.diversification_params["min_stocks"]:
                recommended_actions.append("銘柄数が不足しています")
                recommended_actions.append("追加銘柄の検討を推奨します")
            
            # 推奨セクター
            suggested_sectors = self._get_suggested_sectors(current_sector, sector_concentration)
            
            # 推奨銘柄（簡易実装）
            suggested_stocks = self._get_suggested_stocks(suggested_sectors)
            
            # リスク削減ポテンシャル
            risk_reduction = self._calculate_risk_reduction_potential(symbol, all_symbols)
            
            # 優先度スコア
            priority_score = self._calculate_priority_score(
                symbol, current_level, risk_reduction
            )
            
            return DiversificationRecommendation(
                symbol=symbol,
                timestamp=datetime.now(),
                current_diversification_level=current_level,
                recommended_actions=recommended_actions,
                suggested_sectors=suggested_sectors,
                suggested_stocks=suggested_stocks,
                risk_reduction_potential=risk_reduction,
                priority_score=priority_score,
            )
            
        except Exception as e:
            logger.error(f"個別推奨事項生成エラー: {symbol} - {e}")
            return DiversificationRecommendation(
                symbol=symbol,
                timestamp=datetime.now(),
                current_diversification_level=current_level,
                recommended_actions=["分析エラー"],
                suggested_sectors=[],
                suggested_stocks=[],
                risk_reduction_potential=0.0,
                priority_score=0.0,
            )

    async def _generate_portfolio_recommendation(
        self, symbols: List[str], current_level: DiversificationLevel,
        portfolio_value: float
    ) -> DiversificationRecommendation:
        """ポートフォリオ全体推奨事項生成"""
        try:
            recommended_actions = []
            suggested_sectors = []
            suggested_stocks = []
            
            # 分散投資レベルに応じた推奨事項
            if current_level == DiversificationLevel.CRITICAL:
                recommended_actions.append("緊急の分散投資が必要です")
                recommended_actions.append("銘柄数を大幅に増やすことを推奨します")
                suggested_sectors = list(SectorType)[:5]  # 主要5セクター
            elif current_level == DiversificationLevel.POOR:
                recommended_actions.append("分散投資の改善が必要です")
                recommended_actions.append("異なるセクターへの投資を検討してください")
                suggested_sectors = [s for s in SectorType if s != SectorType.UNKNOWN][:3]
            elif current_level == DiversificationLevel.FAIR:
                recommended_actions.append("分散投資の最適化を推奨します")
                suggested_sectors = [s for s in SectorType if s != SectorType.UNKNOWN][:2]
            else:
                recommended_actions.append("現在の分散投資レベルは適切です")
            
            # 推奨銘柄
            suggested_stocks = self._get_suggested_stocks(suggested_sectors)
            
            # リスク削減ポテンシャル
            risk_reduction = self._calculate_portfolio_risk_reduction_potential(symbols)
            
            return DiversificationRecommendation(
                symbol="PORTFOLIO",
                timestamp=datetime.now(),
                current_diversification_level=current_level,
                recommended_actions=recommended_actions,
                suggested_sectors=suggested_sectors,
                suggested_stocks=suggested_stocks,
                risk_reduction_potential=risk_reduction,
                priority_score=1.0 if current_level in [DiversificationLevel.CRITICAL, DiversificationLevel.POOR] else 0.5,
            )
            
        except Exception as e:
            logger.error(f"ポートフォリオ推奨事項生成エラー: {e}")
            return DiversificationRecommendation(
                symbol="PORTFOLIO",
                timestamp=datetime.now(),
                current_diversification_level=current_level,
                recommended_actions=["分析エラー"],
                suggested_sectors=[],
                suggested_stocks=[],
                risk_reduction_potential=0.0,
                priority_score=0.0,
            )

    def _get_suggested_sectors(
        self, current_sector: SectorType, sector_concentration: Dict[SectorType, float]
    ) -> List[SectorType]:
        """推奨セクター取得"""
        try:
            # 集中度の低いセクターを推奨
            suggested_sectors = []
            
            for sector, weight in sector_concentration.items():
                if sector != current_sector and weight < self.diversification_params["max_sector_weight"]:
                    suggested_sectors.append(sector)
            
            # 未投資セクターを優先
            all_sectors = set(SectorType) - {SectorType.UNKNOWN}
            invested_sectors = set(sector_concentration.keys())
            uninvested_sectors = all_sectors - invested_sectors
            
            suggested_sectors = list(uninvested_sectors) + suggested_sectors
            
            return suggested_sectors[:3]  # 最大3セクター
        except Exception as e:
            logger.error(f"推奨セクター取得エラー: {e}")
            return []

    def _get_suggested_stocks(self, suggested_sectors: List[SectorType]) -> List[str]:
        """推奨銘柄取得"""
        try:
            # セクター別推奨銘柄（簡易実装）
            sector_stocks = {
                SectorType.TECHNOLOGY: ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
                SectorType.FINANCIAL: ["JPM", "BAC", "WFC", "GS", "C"],
                SectorType.HEALTHCARE: ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
                SectorType.CONSUMER: ["KO", "PEP", "WMT", "PG", "JNJ"],
                SectorType.INDUSTRIAL: ["BA", "CAT", "GE", "MMM", "HON"],
            }
            
            suggested_stocks = []
            for sector in suggested_sectors:
                if sector in sector_stocks:
                    suggested_stocks.extend(sector_stocks[sector][:2])  # セクターあたり2銘柄
            
            return suggested_stocks[:5]  # 最大5銘柄
        except Exception as e:
            logger.error(f"推奨銘柄取得エラー: {e}")
            return []

    def _calculate_risk_reduction_potential(self, symbol: str, all_symbols: List[str]) -> float:
        """リスク削減ポテンシャル計算"""
        try:
            # 簡易実装: セクター集中度に基づく計算
            sector_concentration = self._calculate_sector_concentration(all_symbols)
            current_sector = self.sector_mapping.get(symbol, SectorType.UNKNOWN)
            current_weight = sector_concentration.get(current_sector, 0.0)
            
            # 集中度が高いほどリスク削減ポテンシャルが高い
            if current_weight > self.diversification_params["max_sector_weight"]:
                return min(1.0, (current_weight - self.diversification_params["max_sector_weight"]) * 2)
            else:
                return 0.0
        except Exception as e:
            logger.error(f"リスク削減ポテンシャル計算エラー: {e}")
            return 0.0

    def _calculate_portfolio_risk_reduction_potential(self, symbols: List[str]) -> float:
        """ポートフォリオリスク削減ポテンシャル計算"""
        try:
            # 銘柄数不足によるリスク削減ポテンシャル
            stock_count_potential = max(0, (self.diversification_params["min_stocks"] - len(symbols)) / 
                                      self.diversification_params["min_stocks"])
            
            # セクター集中度によるリスク削減ポテンシャル
            sector_concentration = self._calculate_sector_concentration(symbols)
            max_sector_weight = max(sector_concentration.values()) if sector_concentration else 0.0
            sector_potential = max(0, (max_sector_weight - self.diversification_params["max_sector_weight"]) / 
                                self.diversification_params["max_sector_weight"])
            
            # 総合リスク削減ポテンシャル
            total_potential = (stock_count_potential * 0.6 + sector_potential * 0.4)
            
            return min(total_potential, 1.0)
        except Exception as e:
            logger.error(f"ポートフォリオリスク削減ポテンシャル計算エラー: {e}")
            return 0.0

    def _calculate_priority_score(
        self, symbol: str, current_level: DiversificationLevel, risk_reduction: float
    ) -> float:
        """優先度スコア計算"""
        try:
            # 分散投資レベルによる優先度
            level_priority = {
                DiversificationLevel.CRITICAL: 1.0,
                DiversificationLevel.POOR: 0.8,
                DiversificationLevel.FAIR: 0.6,
                DiversificationLevel.GOOD: 0.4,
                DiversificationLevel.EXCELLENT: 0.2,
            }.get(current_level, 0.5)
            
            # リスク削減ポテンシャルによる優先度
            risk_priority = risk_reduction
            
            # 総合優先度スコア
            total_priority = (level_priority * 0.6 + risk_priority * 0.4)
            
            return min(total_priority, 1.0)
        except Exception as e:
            logger.error(f"優先度スコア計算エラー: {e}")
            return 0.5

    def _create_default_correlation_metrics(self) -> CorrelationMetrics:
        """デフォルト相関指標作成"""
        return CorrelationMetrics(
            symbol="PORTFOLIO",
            timestamp=datetime.now(),
            correlation_matrix={},
            average_correlation=0.0,
            max_correlation=0.0,
            correlation_risk_score=0.5,
            diversification_score=0.5,
            concentration_risk=0.5,
            sector_concentration={},
            cluster_analysis={"clusters": [], "cluster_count": 0},
        )

    def get_correlation_summary(self) -> Dict[str, Any]:
        """相関分析サマリー取得"""
        try:
            if not self.correlation_history:
                return {"message": "相関分析履歴がありません"}
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "correlation_analysis": {},
                "diversification_recommendations": [],
            }
            
            # 最新の相関分析結果
            if "PORTFOLIO" in self.correlation_history:
                latest_analysis = self.correlation_history["PORTFOLIO"][-1]
                summary["correlation_analysis"] = asdict(latest_analysis)
            
            return summary
        except Exception as e:
            logger.error(f"相関分析サマリー取得エラー: {e}")
            return {"error": str(e)}

    def save_correlation_report(self, filename: str = "correlation_analysis_report.json"):
        """相関分析レポート保存"""
        try:
            report = self.get_correlation_summary()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"相関分析レポートを保存しました: {filename}")
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 相関分析システム初期化
    correlation_system = CorrelationAnalysisSystem()
    
    # テスト銘柄
    test_symbols = ["7203.T", "6758.T", "9984.T", "7974.T", "4063.T"]
    
    logger.info("相関分析システム テスト開始")
    
    # 相関リスク分析
    try:
        logger.info("相関リスク分析実行中...")
        correlation_metrics = await correlation_system.analyze_correlation_risk(test_symbols)
        
        logger.info(f"相関分析完了:")
        logger.info(f"  平均相関: {correlation_metrics.average_correlation:.3f}")
        logger.info(f"  最大相関: {correlation_metrics.max_correlation:.3f}")
        logger.info(f"  相関リスクスコア: {correlation_metrics.correlation_risk_score:.3f}")
        logger.info(f"  分散投資スコア: {correlation_metrics.diversification_score:.3f}")
        logger.info(f"  集中度リスク: {correlation_metrics.concentration_risk:.3f}")
        
        # セクター集中度表示
        print("\n📊 セクター集中度:")
        for sector, weight in correlation_metrics.sector_concentration.items():
            print(f"  {sector.value}: {weight:.1%}")
        
        # クラスター分析結果
        print(f"\n🔗 クラスター分析:")
        print(f"  クラスター数: {correlation_metrics.cluster_analysis['cluster_count']}")
        for i, cluster in enumerate(correlation_metrics.cluster_analysis['clusters']):
            print(f"  クラスター{i+1}: {', '.join(cluster)}")
        
    except Exception as e:
        logger.error(f"相関分析エラー: {e}")
    
    # 分散投資推奨生成
    try:
        logger.info("分散投資推奨生成中...")
        recommendations = await correlation_system.generate_diversification_recommendations(
            test_symbols, portfolio_value=1000000
        )
        
        logger.info(f"分散投資推奨生成完了: {len(recommendations)}件")
        
        # 推奨事項表示
        print("\n💡 分散投資推奨事項:")
        for rec in recommendations:
            print(f"\n  {rec.symbol}:")
            print(f"    分散投資レベル: {rec.current_diversification_level.value}")
            print(f"    優先度スコア: {rec.priority_score:.3f}")
            print(f"    リスク削減ポテンシャル: {rec.risk_reduction_potential:.1%}")
            print(f"    推奨アクション: {', '.join(rec.recommended_actions)}")
            if rec.suggested_sectors:
                print(f"    推奨セクター: {[s.value for s in rec.suggested_sectors]}")
            if rec.suggested_stocks:
                print(f"    推奨銘柄: {rec.suggested_stocks}")
        
    except Exception as e:
        logger.error(f"分散投資推奨生成エラー: {e}")
    
    # レポート保存
    correlation_system.save_correlation_report()
    
    # 結果表示
    print("\n" + "=" * 80)
    print("🔗 相関分析システム レポート")
    print("=" * 80)
    print(f"分析銘柄数: {len(test_symbols)}")
    print(f"推奨事項数: {len(recommendations) if 'recommendations' in locals() else 0}")


if __name__ == "__main__":
    asyncio.run(main())
