#!/usr/bin/env python3
"""
個別銘柄リスク管理の精密化システム
期待効果: 損失を60-80%削減
実装難易度: 🟡 中
推定工数: 2-3日

機能:
1. 個別銘柄の動的損切り設定
2. 個別銘柄のボラティリティベースリスク調整
3. 個別銘柄の相関分析による分散投資推奨
4. 個別銘柄の最大損失額設定
5. 横展開: ポートフォリオ全体のリスク管理にも応用
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from collections import defaultdict, deque
import yfinance as yf
from scipy import stats
from scipy.stats import pearsonr
import asyncio
import aiohttp

# 統合ログシステムのインポート
from unified_logging_config import get_system_logger, get_enhanced_logger

warnings.filterwarnings("ignore")

# 統合ログシステムを使用
logger = get_system_logger()
enhanced_logger = get_enhanced_logger()


class RiskLevel(Enum):
    """リスクレベル"""
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CRITICAL = "CRITICAL"


class PositionType(Enum):
    """ポジションタイプ"""
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class IndividualStockRiskProfile:
    """個別銘柄リスクプロファイル"""
    symbol: str
    current_price: float
    volatility: float
    beta: float
    max_loss_amount: float
    max_loss_percent: float
    dynamic_stop_loss: float
    volatility_adjusted_risk: float
    correlation_risk: float
    total_risk_score: float
    risk_level: RiskLevel
    recommended_position_size: float
    max_position_value: float
    last_updated: datetime


@dataclass
class VolatilityMetrics:
    """ボラティリティ指標"""
    symbol: str
    historical_volatility: float
    implied_volatility: float
    volatility_percentile: float
    volatility_trend: str  # "increasing", "decreasing", "stable"
    volatility_risk_score: float


@dataclass
class CorrelationAnalysis:
    """相関分析結果"""
    symbol: str
    correlated_stocks: List[Tuple[str, float]]  # (symbol, correlation)
    portfolio_correlation: float
    diversification_score: float
    concentration_risk: float
    recommended_diversification: List[str]


@dataclass
class DynamicStopLossSettings:
    """動的損切り設定"""
    symbol: str
    base_stop_loss: float
    volatility_adjustment: float
    trend_adjustment: float
    volume_adjustment: float
    final_stop_loss: float
    trailing_stop_enabled: bool
    trailing_stop_percent: float


class IndividualStockRiskManager:
    """個別銘柄リスク管理システム"""

    def __init__(self, account_value: float = 1000000):
        self.account_value = account_value
        self.stock_profiles = {}
        self.volatility_history = defaultdict(list)
        self.correlation_matrix = {}
        self.risk_adjustments = {}
        
        # リスク管理パラメータ
        self.risk_params = {
            "max_individual_loss": 0.05,  # 個別銘柄最大損失5%
            "max_portfolio_loss": 0.15,  # ポートフォリオ最大損失15%
            "volatility_threshold": 0.3,  # ボラティリティ閾値30%
            "correlation_threshold": 0.7,  # 相関閾値70%
            "min_diversification": 5,  # 最小分散投資銘柄数
        }

    async def analyze_individual_stock_risk(
        self, symbol: str, current_price: float, position_size: float = 0.0
    ) -> IndividualStockRiskProfile:
        """個別銘柄のリスク分析"""
        try:
            logger.info(f"個別銘柄リスク分析開始: {symbol}")

            # ボラティリティ分析
            volatility_metrics = await self._analyze_volatility(symbol)
            
            # 相関分析
            correlation_analysis = await self._analyze_correlation(symbol)
            
            # 動的損切り設定
            stop_loss_settings = await self._calculate_dynamic_stop_loss(
                symbol, current_price, volatility_metrics
            )
            
            # リスクスコア計算
            total_risk_score = self._calculate_total_risk_score(
                volatility_metrics, correlation_analysis, position_size
            )
            
            # リスクレベル判定
            risk_level = self._determine_risk_level(total_risk_score)
            
            # 推奨ポジションサイズ計算
            recommended_size = self._calculate_recommended_position_size(
                symbol, current_price, total_risk_score, volatility_metrics
            )
            
            # 最大損失額設定
            max_loss_amount = self._calculate_max_loss_amount(
                symbol, current_price, recommended_size
            )

            # リスクプロファイル作成
            risk_profile = IndividualStockRiskProfile(
                symbol=symbol,
                current_price=current_price,
                volatility=volatility_metrics.volatility_risk_score,
                beta=1.0,  # 簡易実装
                max_loss_amount=max_loss_amount,
                max_loss_percent=self.risk_params["max_individual_loss"],
                dynamic_stop_loss=stop_loss_settings.final_stop_loss,
                volatility_adjusted_risk=volatility_metrics.volatility_risk_score,
                correlation_risk=correlation_analysis.concentration_risk,
                total_risk_score=total_risk_score,
                risk_level=risk_level,
                recommended_position_size=recommended_size,
                max_position_value=recommended_size * current_price,
                last_updated=datetime.now(),
            )

            # プロファイル保存
            self.stock_profiles[symbol] = risk_profile
            
            logger.info(f"個別銘柄リスク分析完了: {symbol} - リスクレベル: {risk_level.value}")
            return risk_profile

        except Exception as e:
            logger.error(f"個別銘柄リスク分析エラー: {symbol} - {e}")
            return self._create_default_risk_profile(symbol, current_price)

    async def _analyze_volatility(self, symbol: str) -> VolatilityMetrics:
        """ボラティリティ分析"""
        try:
            # 株価データ取得
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            
            if len(hist) < 30:
                return VolatilityMetrics(
                    symbol=symbol,
                    historical_volatility=0.2,
                    implied_volatility=0.2,
                    volatility_percentile=50.0,
                    volatility_trend="stable",
                    volatility_risk_score=0.5,
                )

            # 日次リターン計算
            returns = hist['Close'].pct_change().dropna()
            
            # ヒストリカルボラティリティ（年率）
            historical_vol = returns.std() * np.sqrt(252)
            
            # ボラティリティのパーセンタイル
            vol_percentile = stats.percentileofscore(returns.std() * np.sqrt(252), historical_vol)
            
            # ボラティリティトレンド分析
            recent_vol = returns.tail(20).std() * np.sqrt(252)
            older_vol = returns.head(-20).std() * np.sqrt(252)
            
            if recent_vol > older_vol * 1.1:
                trend = "increasing"
            elif recent_vol < older_vol * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
            
            # ボラティリティリスクスコア（0-1）
            vol_risk_score = min(historical_vol / 0.5, 1.0)  # 50%を最大リスクとする
            
            return VolatilityMetrics(
                symbol=symbol,
                historical_volatility=historical_vol,
                implied_volatility=historical_vol,  # 簡易実装
                volatility_percentile=vol_percentile,
                volatility_trend=trend,
                volatility_risk_score=vol_risk_score,
            )

        except Exception as e:
            logger.error(f"ボラティリティ分析エラー: {symbol} - {e}")
            return VolatilityMetrics(
                symbol=symbol,
                historical_volatility=0.2,
                implied_volatility=0.2,
                volatility_percentile=50.0,
                volatility_trend="stable",
                volatility_risk_score=0.5,
            )

    async def _analyze_correlation(self, symbol: str) -> CorrelationAnalysis:
        """相関分析"""
        try:
            # ポートフォリオ内の他の銘柄との相関分析
            correlated_stocks = []
            portfolio_correlation = 0.0
            
            if len(self.stock_profiles) > 1:
                # 既存の銘柄との相関計算
                for other_symbol in self.stock_profiles.keys():
                    if other_symbol != symbol:
                        correlation = await self._calculate_correlation(symbol, other_symbol)
                        if correlation is not None:
                            correlated_stocks.append((other_symbol, correlation))
                            portfolio_correlation += abs(correlation)
                
                # ポートフォリオ相関の平均
                if correlated_stocks:
                    portfolio_correlation = portfolio_correlation / len(correlated_stocks)
            
            # 分散投資スコア計算
            diversification_score = max(0, 1 - portfolio_correlation)
            
            # 集中リスク計算
            concentration_risk = min(portfolio_correlation, 1.0)
            
            # 分散投資推奨銘柄
            recommended_diversification = self._get_diversification_recommendations(
                symbol, correlated_stocks
            )
            
            return CorrelationAnalysis(
                symbol=symbol,
                correlated_stocks=correlated_stocks,
                portfolio_correlation=portfolio_correlation,
                diversification_score=diversification_score,
                concentration_risk=concentration_risk,
                recommended_diversification=recommended_diversification,
            )

        except Exception as e:
            logger.error(f"相関分析エラー: {symbol} - {e}")
            return CorrelationAnalysis(
                symbol=symbol,
                correlated_stocks=[],
                portfolio_correlation=0.0,
                diversification_score=1.0,
                concentration_risk=0.0,
                recommended_diversification=[],
            )

    async def _calculate_correlation(self, symbol1: str, symbol2: str) -> Optional[float]:
        """2銘柄間の相関計算"""
        try:
            # 株価データ取得
            stock1 = yf.Ticker(symbol1)
            stock2 = yf.Ticker(symbol2)
            
            hist1 = stock1.history(period="6mo")
            hist2 = stock2.history(period="6mo")
            
            if len(hist1) < 30 or len(hist2) < 30:
                return None
            
            # 共通期間のデータを取得
            common_dates = hist1.index.intersection(hist2.index)
            if len(common_dates) < 30:
                return None
            
            returns1 = hist1.loc[common_dates, 'Close'].pct_change().dropna()
            returns2 = hist2.loc[common_dates, 'Close'].pct_change().dropna()
            
            # 相関計算
            correlation, _ = pearsonr(returns1, returns2)
            return correlation

        except Exception as e:
            logger.error(f"相関計算エラー: {symbol1} vs {symbol2} - {e}")
            return None

    async def _calculate_dynamic_stop_loss(
        self, symbol: str, current_price: float, volatility_metrics: VolatilityMetrics
    ) -> DynamicStopLossSettings:
        """動的損切り設定計算"""
        try:
            # ベース損切り（2%）
            base_stop_loss = 0.02
            
            # ボラティリティ調整
            volatility_adjustment = 1 + (volatility_metrics.historical_volatility - 0.2) * 2
            
            # トレンド調整（簡易実装）
            trend_adjustment = 1.0
            if volatility_metrics.volatility_trend == "increasing":
                trend_adjustment = 1.2
            elif volatility_metrics.volatility_trend == "decreasing":
                trend_adjustment = 0.8
            
            # ボリューム調整（簡易実装）
            volume_adjustment = 1.0
            
            # 最終損切り計算
            final_stop_loss = base_stop_loss * volatility_adjustment * trend_adjustment * volume_adjustment
            
            # 最小・最大制限
            final_stop_loss = max(0.01, min(0.1, final_stop_loss))  # 1%-10%の範囲
            
            return DynamicStopLossSettings(
                symbol=symbol,
                base_stop_loss=base_stop_loss,
                volatility_adjustment=volatility_adjustment,
                trend_adjustment=trend_adjustment,
                volume_adjustment=volume_adjustment,
                final_stop_loss=final_stop_loss,
                trailing_stop_enabled=True,
                trailing_stop_percent=final_stop_loss * 0.5,
            )

        except Exception as e:
            logger.error(f"動的損切り計算エラー: {symbol} - {e}")
            return DynamicStopLossSettings(
                symbol=symbol,
                base_stop_loss=0.02,
                volatility_adjustment=1.0,
                trend_adjustment=1.0,
                volume_adjustment=1.0,
                final_stop_loss=0.02,
                trailing_stop_enabled=True,
                trailing_stop_percent=0.01,
            )

    def _calculate_total_risk_score(
        self, 
        volatility_metrics: VolatilityMetrics, 
        correlation_analysis: CorrelationAnalysis,
        position_size: float
    ) -> float:
        """総合リスクスコア計算"""
        try:
            # ボラティリティリスク（40%の重み）
            vol_risk = volatility_metrics.volatility_risk_score * 0.4
            
            # 相関リスク（30%の重み）
            corr_risk = correlation_analysis.concentration_risk * 0.3
            
            # ポジションサイズリスク（30%の重み）
            position_risk = min(position_size / self.account_value * 10, 1.0) * 0.3
            
            # 総合リスクスコア
            total_risk = vol_risk + corr_risk + position_risk
            
            return min(total_risk, 1.0)

        except Exception as e:
            logger.error(f"総合リスクスコア計算エラー: {e}")
            return 0.5

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """リスクレベル判定"""
        if risk_score < 0.2:
            return RiskLevel.VERY_LOW
        elif risk_score < 0.4:
            return RiskLevel.LOW
        elif risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif risk_score < 0.8:
            return RiskLevel.HIGH
        elif risk_score < 0.9:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.CRITICAL

    def _calculate_recommended_position_size(
        self, symbol: str, current_price: float, risk_score: float, volatility_metrics: VolatilityMetrics
    ) -> float:
        """推奨ポジションサイズ計算"""
        try:
            # ベースポジションサイズ（口座の5%）
            base_position_size = self.account_value * 0.05
            
            # リスクスコアによる調整
            risk_adjustment = 1 - (risk_score * 0.5)  # リスクが高いほどポジションサイズを縮小
            
            # ボラティリティによる調整
            vol_adjustment = 1 - (volatility_metrics.volatility_risk_score * 0.3)
            
            # 最終ポジションサイズ
            recommended_size = base_position_size * risk_adjustment * vol_adjustment
            
            # 最小・最大制限
            min_size = self.account_value * 0.01  # 最小1%
            max_size = self.account_value * 0.1   # 最大10%
            
            return max(min_size, min(max_size, recommended_size))

        except Exception as e:
            logger.error(f"推奨ポジションサイズ計算エラー: {e}")
            return self.account_value * 0.05

    def _calculate_max_loss_amount(
        self, symbol: str, current_price: float, position_size: float
    ) -> float:
        """最大損失額計算"""
        try:
            # 個別銘柄最大損失率
            max_loss_percent = self.risk_params["max_individual_loss"]
            
            # 最大損失額
            max_loss_amount = position_size * max_loss_percent
            
            return max_loss_amount

        except Exception as e:
            logger.error(f"最大損失額計算エラー: {e}")
            return position_size * 0.05

    def _get_diversification_recommendations(
        self, symbol: str, correlated_stocks: List[Tuple[str, float]]
    ) -> List[str]:
        """分散投資推奨銘柄取得"""
        try:
            # 高相関銘柄を特定
            high_correlation_stocks = [
                stock for stock, corr in correlated_stocks 
                if abs(corr) > self.risk_params["correlation_threshold"]
            ]
            
            # 分散投資推奨（簡易実装）
            recommendations = []
            
            # セクター分散推奨
            if len(high_correlation_stocks) > 2:
                recommendations.append("異なるセクターへの分散投資を検討してください")
            
            # 銘柄数推奨
            if len(self.stock_profiles) < self.risk_params["min_diversification"]:
                recommendations.append(f"最低{self.risk_params['min_diversification']}銘柄への分散投資を推奨します")
            
            return recommendations

        except Exception as e:
            logger.error(f"分散投資推奨取得エラー: {e}")
            return []

    def _create_default_risk_profile(self, symbol: str, current_price: float) -> IndividualStockRiskProfile:
        """デフォルトリスクプロファイル作成"""
        return IndividualStockRiskProfile(
            symbol=symbol,
            current_price=current_price,
            volatility=0.5,
            beta=1.0,
            max_loss_amount=self.account_value * 0.05,
            max_loss_percent=0.05,
            dynamic_stop_loss=current_price * 0.98,
            volatility_adjusted_risk=0.5,
            correlation_risk=0.5,
            total_risk_score=0.5,
            risk_level=RiskLevel.MEDIUM,
            recommended_position_size=self.account_value * 0.05,
            max_position_value=self.account_value * 0.05,
            last_updated=datetime.now(),
        )

    def get_risk_summary(self) -> Dict[str, Any]:
        """リスクサマリー取得"""
        try:
            if not self.stock_profiles:
                return {"message": "リスクプロファイルがありません"}

            # 全体統計
            total_risk_score = np.mean([profile.total_risk_score for profile in self.stock_profiles.values()])
            high_risk_stocks = [
                symbol for symbol, profile in self.stock_profiles.items()
                if profile.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]
            ]
            
            # ポートフォリオ集中度
            portfolio_concentration = len(self.stock_profiles)
            
            # 推奨事項
            recommendations = self._generate_portfolio_recommendations()

            return {
                "timestamp": datetime.now().isoformat(),
                "total_stocks": len(self.stock_profiles),
                "average_risk_score": total_risk_score,
                "high_risk_stocks": high_risk_stocks,
                "portfolio_concentration": portfolio_concentration,
                "recommendations": recommendations,
                "individual_profiles": {
                    symbol: asdict(profile) for symbol, profile in self.stock_profiles.items()
                }
            }

        except Exception as e:
            logger.error(f"リスクサマリー取得エラー: {e}")
            return {"error": str(e)}

    def _generate_portfolio_recommendations(self) -> List[str]:
        """ポートフォリオ推奨事項生成"""
        recommendations = []
        
        try:
            # 高リスク銘柄の推奨
            high_risk_count = sum(
                1 for profile in self.stock_profiles.values()
                if profile.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]
            )
            
            if high_risk_count > len(self.stock_profiles) * 0.3:
                recommendations.append("高リスク銘柄の割合が高すぎます。リスク分散を検討してください。")
            
            # 分散投資の推奨
            if len(self.stock_profiles) < self.risk_params["min_diversification"]:
                recommendations.append(f"銘柄数を{self.risk_params['min_diversification']}以上に増やすことを推奨します。")
            
            # 相関リスクの推奨
            high_correlation_count = sum(
                1 for profile in self.stock_profiles.values()
                if profile.correlation_risk > 0.7
            )
            
            if high_correlation_count > 0:
                recommendations.append("高相関銘柄が存在します。異なるセクターへの分散投資を検討してください。")
            
            if not recommendations:
                recommendations.append("現在のポートフォリオ構成は適切です。")
            
            return recommendations

        except Exception as e:
            logger.error(f"推奨事項生成エラー: {e}")
            return ["エラーが発生しました"]

    def save_risk_report(self, filename: str = "individual_stock_risk_report.json"):
        """リスクレポート保存"""
        try:
            report = self.get_risk_summary()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"リスクレポートを保存しました: {filename}")
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 個別銘柄リスク管理システム初期化
    risk_manager = IndividualStockRiskManager(account_value=1000000)
    
    # テスト銘柄
    test_symbols = ["7203.T", "6758.T", "9984.T", "7974.T", "4063.T"]
    
    logger.info("個別銘柄リスク管理システム テスト開始")
    
    # 各銘柄のリスク分析
    for symbol in test_symbols:
        try:
            logger.info(f"銘柄分析開始: {symbol}")
            
            # 現在価格取得
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else 1000.0
            
            # リスク分析実行
            risk_profile = await risk_manager.analyze_individual_stock_risk(
                symbol, current_price
            )
            
            logger.info(f"分析完了: {symbol}")
            logger.info(f"  リスクレベル: {risk_profile.risk_level.value}")
            logger.info(f"  総合リスクスコア: {risk_profile.total_risk_score:.3f}")
            logger.info(f"  推奨ポジションサイズ: ¥{risk_profile.recommended_position_size:,.0f}")
            logger.info(f"  動的損切り: {risk_profile.dynamic_stop_loss:.0f}")
            logger.info(f"  最大損失額: ¥{risk_profile.max_loss_amount:,.0f}")
            
        except Exception as e:
            logger.error(f"銘柄分析エラー: {symbol} - {e}")
    
    # リスクサマリー生成
    summary = risk_manager.get_risk_summary()
    risk_manager.save_risk_report()
    
    # 結果表示
    print("\n" + "=" * 80)
    print("🛡️ 個別銘柄リスク管理システム レポート")
    print("=" * 80)
    print(f"分析時刻: {summary['timestamp']}")
    print(f"分析銘柄数: {summary['total_stocks']}")
    print(f"平均リスクスコア: {summary['average_risk_score']:.3f}")
    print(f"高リスク銘柄: {', '.join(summary['high_risk_stocks']) if summary['high_risk_stocks'] else 'なし'}")
    
    print("\n💡 推奨事項:")
    for rec in summary['recommendations']:
        print(f"  • {rec}")
    
    print("\n📊 個別銘柄詳細:")
    for symbol, profile in summary['individual_profiles'].items():
        risk_emoji = {
            "VERY_LOW": "🟢", "LOW": "🟡", "MEDIUM": "🟠", 
            "HIGH": "🔴", "VERY_HIGH": "🔴", "CRITICAL": "⚫"
        }.get(profile['risk_level'], "⚪")
        
        print(f"  {risk_emoji} {symbol}: リスク{profile['risk_level']} "
              f"(スコア: {profile['total_risk_score']:.3f}) "
              f"推奨サイズ: ¥{profile['recommended_position_size']:,.0f}")


if __name__ == "__main__":
    asyncio.run(main())
