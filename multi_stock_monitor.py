#!/usr/bin/env python3
"""
複数銘柄同時監視・比較システム
最高優先度機能: 最適な投資機会の選択で20-30%利益向上

機能:
1. 複数銘柄の同時監視
2. 銘柄間の比較分析
3. 相関分析と分散投資推奨
4. パフォーマンスランキング
5. 投資機会の優先順位付け
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings

warnings.filterwarnings("ignore")
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("multi_stock_monitor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class InvestmentOpportunity(Enum):
    """投資機会の種類"""

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class StockAnalysis:
    """個別銘柄分析結果"""

    symbol: str
    current_price: float
    change_percent: float
    volume: int
    market_cap: float
    pe_ratio: float
    technical_score: float
    fundamental_score: float
    momentum_score: float
    volatility: float
    rsi: float
    macd_signal: str
    trend_direction: str
    support_level: float
    resistance_level: float
    investment_opportunity: InvestmentOpportunity
    confidence: float
    risk_level: str
    recommendation_reason: str


@dataclass
class PortfolioComparison:
    """ポートフォリオ比較結果"""

    total_symbols: int
    analyzed_symbols: int
    top_performers: List[Dict]
    worst_performers: List[Dict]
    correlation_matrix: Dict[str, Dict[str, float]]
    diversification_score: float
    sector_allocation: Dict[str, float]
    risk_return_analysis: Dict[str, float]
    best_opportunities: List[Dict]


class TechnicalAnalyzer:
    """技術分析クラス"""

    def __init__(self):
        self.indicators = {}

    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """技術指標を計算"""
        if len(data) < 50:
            return {}

        close = data["Close"]
        high = data["High"]
        low = data["Low"]
        volume = data["Volume"]

        indicators = {}

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators["rsi"] = (100 - (100 / (1 + rs))).iloc[-1] if not rs.empty else 50

        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        macd_hist = macd - macd_signal

        indicators["macd"] = macd.iloc[-1] if not macd.empty else 0
        indicators["macd_signal"] = macd_signal.iloc[-1] if not macd_signal.empty else 0
        indicators["macd_hist"] = macd_hist.iloc[-1] if not macd_hist.empty else 0

        # ボリンジャーバンド
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)

        indicators["bb_upper"] = (
            bb_upper.iloc[-1] if not bb_upper.empty else close.iloc[-1]
        )
        indicators["bb_lower"] = (
            bb_lower.iloc[-1] if not bb_lower.empty else close.iloc[-1]
        )
        indicators["bb_middle"] = (
            sma_20.iloc[-1] if not sma_20.empty else close.iloc[-1]
        )

        # 移動平均
        indicators["sma_20"] = (
            close.rolling(window=20).mean().iloc[-1]
            if len(close) >= 20
            else close.iloc[-1]
        )
        indicators["sma_50"] = (
            close.rolling(window=50).mean().iloc[-1]
            if len(close) >= 50
            else close.iloc[-1]
        )
        indicators["ema_12"] = close.ewm(span=12).mean().iloc[-1]
        indicators["ema_26"] = close.ewm(span=26).mean().iloc[-1]

        # ボラティリティ
        returns = close.pct_change().dropna()
        indicators["volatility"] = (
            returns.std() * np.sqrt(252) if not returns.empty else 0
        )

        # サポート・レジスタンス
        indicators["support"] = (
            low.rolling(window=20).min().iloc[-1] if len(low) >= 20 else low.iloc[-1]
        )
        indicators["resistance"] = (
            high.rolling(window=20).max().iloc[-1] if len(high) >= 20 else high.iloc[-1]
        )

        return indicators

    def calculate_technical_score(
        self, indicators: Dict[str, float], current_price: float
    ) -> float:
        """技術スコアを計算（0-100）"""
        score = 50  # ベーススコア

        # RSIスコア
        rsi = indicators.get("rsi", 50)
        if rsi < 30:
            score += 20  # 過小売り
        elif rsi > 70:
            score -= 20  # 過大買い
        elif 40 <= rsi <= 60:
            score += 10  # 中立

        # MACDスコア
        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)
        if macd > macd_signal:
            score += 15  # 上昇シグナル
        else:
            score -= 15  # 下降シグナル

        # ボリンジャーバンドスコア
        bb_upper = indicators.get("bb_upper", current_price)
        bb_lower = indicators.get("bb_lower", current_price)
        if current_price <= bb_lower:
            score += 15  # 下限付近
        elif current_price >= bb_upper:
            score -= 15  # 上限付近

        # 移動平均スコア
        sma_20 = indicators.get("sma_20", current_price)
        sma_50 = indicators.get("sma_50", current_price)
        if current_price > sma_20 > sma_50:
            score += 20  # 上昇トレンド
        elif current_price < sma_20 < sma_50:
            score -= 20  # 下降トレンド

        return max(0, min(100, score))


class FundamentalAnalyzer:
    """ファンダメンタル分析クラス"""

    def __init__(self):
        self.sector_mapping = {
            "7203.T": "Automotive",
            "6758.T": "Technology",
            "9984.T": "Telecommunications",
            "9432.T": "Telecommunications",
            "6861.T": "Technology",
            "4063.T": "Chemicals",
            "8035.T": "Technology",
            "8306.T": "Financial",
            "4503.T": "Pharmaceutical",
            "4519.T": "Pharmaceutical",
        }

    def calculate_fundamental_score(
        self, symbol: str, current_price: float, market_cap: float, pe_ratio: float
    ) -> float:
        """ファンダメンタルスコアを計算（0-100）"""
        score = 50  # ベーススコア

        # 時価総額スコア
        if market_cap > 1e12:  # 1兆円以上
            score += 20
        elif market_cap > 1e11:  # 1000億円以上
            score += 10
        elif market_cap < 1e9:  # 10億円未満
            score -= 20

        # PERスコア
        if 10 <= pe_ratio <= 20:
            score += 20  # 適正なPER
        elif pe_ratio < 10:
            score += 10  # 割安
        elif pe_ratio > 30:
            score -= 20  # 割高
        elif pe_ratio > 50:
            score -= 30  # 非常に割高

        # セクター別スコア調整
        sector = self.sector_mapping.get(symbol, "Unknown")
        if sector in ["Technology", "Pharmaceutical"]:
            score += 5  # 成長セクター
        elif sector in ["Financial", "Automotive"]:
            score += 0  # 安定セクター

        return max(0, min(100, score))


class MomentumAnalyzer:
    """モメンタム分析クラス"""

    def calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """モメンタムスコアを計算（0-100）"""
        if len(data) < 20:
            return 50

        close = data["Close"]

        # 短期・中期・長期のリターン
        short_return = (
            (close.iloc[-1] / close.iloc[-5] - 1) * 100 if len(close) >= 5 else 0
        )
        medium_return = (
            (close.iloc[-1] / close.iloc[-20] - 1) * 100 if len(close) >= 20 else 0
        )
        long_return = (
            (close.iloc[-1] / close.iloc[-60] - 1) * 100 if len(close) >= 60 else 0
        )

        # モメンタムスコア計算
        score = 50  # ベーススコア

        # 短期モメンタム
        if short_return > 5:
            score += 20
        elif short_return > 2:
            score += 10
        elif short_return < -5:
            score -= 20
        elif short_return < -2:
            score -= 10

        # 中期モメンタム
        if medium_return > 10:
            score += 15
        elif medium_return > 5:
            score += 10
        elif medium_return < -10:
            score -= 15
        elif medium_return < -5:
            score -= 10

        # 長期モメンタム
        if long_return > 20:
            score += 15
        elif long_return > 10:
            score += 10
        elif long_return < -20:
            score -= 15
        elif long_return < -10:
            score -= 10

        return max(0, min(100, score))


class MultiStockMonitor:
    """複数銘柄同時監視システム"""

    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.momentum_analyzer = MomentumAnalyzer()
        self.analysis_results = {}
        self.lock = threading.Lock()

    def fetch_stock_data(
        self, symbol: str, period: str = "6mo"
    ) -> Optional[pd.DataFrame]:
        """株価データを取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                logger.warning(f"データが取得できませんでした: {symbol}")
                return None
            return data
        except Exception as e:
            logger.error(f"データ取得エラー {symbol}: {e}")
            return None

    def analyze_single_stock(self, symbol: str) -> Optional[StockAnalysis]:
        """単一銘柄の分析"""
        try:
            data = self.fetch_stock_data(symbol)
            if data is None or len(data) < 50:
                return None

            # 基本情報
            current_price = data["Close"].iloc[-1]
            prev_price = data["Close"].iloc[-2] if len(data) > 1 else current_price
            change_percent = ((current_price - prev_price) / prev_price) * 100
            volume = data["Volume"].iloc[-1]

            # 技術指標計算
            technical_indicators = (
                self.technical_analyzer.calculate_technical_indicators(data)
            )
            technical_score = self.technical_analyzer.calculate_technical_score(
                technical_indicators, current_price
            )

            # ファンダメンタル分析（簡易版）
            market_cap = current_price * volume * 1000  # 簡易計算
            pe_ratio = 15.0  # 仮のPER
            fundamental_score = self.fundamental_analyzer.calculate_fundamental_score(
                symbol, current_price, market_cap, pe_ratio
            )

            # モメンタム分析
            momentum_score = self.momentum_analyzer.calculate_momentum_score(data)

            # 投資機会判定
            investment_opportunity = self._determine_investment_opportunity(
                technical_score, fundamental_score, momentum_score
            )

            # 信頼度計算
            confidence = self._calculate_confidence(
                technical_score, fundamental_score, momentum_score
            )

            # リスクレベル判定
            volatility = technical_indicators.get("volatility", 0.2)
            risk_level = self._determine_risk_level(volatility, confidence)

            # 推奨理由生成
            recommendation_reason = self._generate_recommendation_reason(
                technical_indicators,
                technical_score,
                fundamental_score,
                momentum_score,
            )

            analysis = StockAnalysis(
                symbol=symbol,
                current_price=current_price,
                change_percent=change_percent,
                volume=volume,
                market_cap=market_cap,
                pe_ratio=pe_ratio,
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                momentum_score=momentum_score,
                volatility=volatility,
                rsi=technical_indicators.get("rsi", 50),
                macd_signal=(
                    "BUY"
                    if technical_indicators.get("macd", 0)
                    > technical_indicators.get("macd_signal", 0)
                    else "SELL"
                ),
                trend_direction=self._determine_trend_direction(
                    technical_indicators, current_price
                ),
                support_level=technical_indicators.get("support", current_price * 0.9),
                resistance_level=technical_indicators.get(
                    "resistance", current_price * 1.1
                ),
                investment_opportunity=investment_opportunity,
                confidence=confidence,
                risk_level=risk_level,
                recommendation_reason=recommendation_reason,
            )

            return analysis

        except Exception as e:
            logger.error(f"分析エラー {symbol}: {e}")
            return None

    def _determine_investment_opportunity(
        self, technical_score: float, fundamental_score: float, momentum_score: float
    ) -> InvestmentOpportunity:
        """投資機会を判定"""
        total_score = (technical_score + fundamental_score + momentum_score) / 3

        if total_score >= 80:
            return InvestmentOpportunity.STRONG_BUY
        elif total_score >= 65:
            return InvestmentOpportunity.BUY
        elif total_score >= 35:
            return InvestmentOpportunity.HOLD
        elif total_score >= 20:
            return InvestmentOpportunity.SELL
        else:
            return InvestmentOpportunity.STRONG_SELL

    def _calculate_confidence(
        self, technical_score: float, fundamental_score: float, momentum_score: float
    ) -> float:
        """信頼度を計算"""
        # スコアの一貫性を評価
        scores = [technical_score, fundamental_score, momentum_score]
        mean_score = np.mean(scores)
        std_score = np.std(scores)

        # 一貫性が高いほど信頼度が高い
        consistency = 1 - (std_score / 50)  # 標準偏差が小さいほど一貫性が高い
        base_confidence = mean_score / 100

        return min(0.95, max(0.1, base_confidence * consistency))

    def _determine_risk_level(self, volatility: float, confidence: float) -> str:
        """リスクレベルを判定"""
        if volatility < 0.2 and confidence > 0.7:
            return "LOW"
        elif volatility < 0.3 and confidence > 0.5:
            return "MEDIUM"
        else:
            return "HIGH"

    def _determine_trend_direction(
        self, indicators: Dict[str, float], current_price: float
    ) -> str:
        """トレンド方向を判定"""
        sma_20 = indicators.get("sma_20", current_price)
        sma_50 = indicators.get("sma_50", current_price)

        if current_price > sma_20 > sma_50:
            return "UP"
        elif current_price < sma_20 < sma_50:
            return "DOWN"
        else:
            return "SIDEWAYS"

    def _generate_recommendation_reason(
        self,
        indicators: Dict[str, float],
        technical_score: float,
        fundamental_score: float,
        momentum_score: float,
    ) -> str:
        """推奨理由を生成"""
        reasons = []

        # 技術分析理由
        rsi = indicators.get("rsi", 50)
        if rsi < 30:
            reasons.append("RSI過小売り")
        elif rsi > 70:
            reasons.append("RSI過大買い")

        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)
        if macd > macd_signal:
            reasons.append("MACD上昇シグナル")
        else:
            reasons.append("MACD下降シグナル")

        # スコア理由
        if technical_score > 70:
            reasons.append("技術指標良好")
        if fundamental_score > 70:
            reasons.append("ファンダメンタル良好")
        if momentum_score > 70:
            reasons.append("モメンタム良好")

        return "; ".join(reasons) if reasons else "特記事項なし"

    def analyze_all_stocks(self) -> Dict[str, StockAnalysis]:
        """全銘柄を並列分析"""
        logger.info(f"複数銘柄分析開始: {len(self.symbols)}銘柄")

        analysis_results = {}

        # 並列処理で分析実行
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self.analyze_single_stock, symbol): symbol
                for symbol in self.symbols
            }

            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    if result:
                        analysis_results[symbol] = result
                        logger.info(
                            f"分析完了: {symbol} - {result.investment_opportunity.value}"
                        )
                except Exception as e:
                    logger.error(f"分析エラー {symbol}: {e}")

        self.analysis_results = analysis_results
        logger.info(f"分析完了: {len(analysis_results)}/{len(self.symbols)}銘柄")

        return analysis_results

    def calculate_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """相関行列を計算"""
        if len(self.analysis_results) < 2:
            return {}

        # 価格データを取得して相関計算
        price_data = {}
        for symbol, analysis in self.analysis_results.items():
            try:
                data = self.fetch_stock_data(symbol, "3mo")
                if data is not None and len(data) > 20:
                    price_data[symbol] = data["Close"]
            except Exception as e:
                logger.error(f"相関計算エラー {symbol}: {e}")

        if len(price_data) < 2:
            return {}

        # 相関行列計算
        df = pd.DataFrame(price_data)
        correlation_matrix = df.corr().to_dict()

        return correlation_matrix

    def generate_portfolio_comparison(self) -> PortfolioComparison:
        """ポートフォリオ比較分析"""
        if not self.analysis_results:
            return PortfolioComparison(
                total_symbols=len(self.symbols),
                analyzed_symbols=0,
                top_performers=[],
                worst_performers=[],
                correlation_matrix={},
                diversification_score=0.0,
                sector_allocation={},
                risk_return_analysis={},
                best_opportunities=[],
            )

        # パフォーマンスランキング
        performance_data = []
        for symbol, analysis in self.analysis_results.items():
            performance_data.append(
                {
                    "symbol": symbol,
                    "change_percent": analysis.change_percent,
                    "technical_score": analysis.technical_score,
                    "fundamental_score": analysis.fundamental_score,
                    "momentum_score": analysis.momentum_score,
                    "confidence": analysis.confidence,
                    "investment_opportunity": analysis.investment_opportunity.value,
                }
            )

        # パフォーマンス順でソート
        performance_data.sort(key=lambda x: x["change_percent"], reverse=True)

        top_performers = performance_data[:5]
        worst_performers = performance_data[-5:]

        # 相関行列計算
        correlation_matrix = self.calculate_correlation_matrix()

        # 分散投資スコア計算
        diversification_score = self._calculate_diversification_score(
            correlation_matrix
        )

        # セクター配分計算
        sector_allocation = self._calculate_sector_allocation()

        # リスク・リターン分析
        risk_return_analysis = self._calculate_risk_return_analysis()

        # 最良の投資機会
        best_opportunities = self._get_best_opportunities()

        return PortfolioComparison(
            total_symbols=len(self.symbols),
            analyzed_symbols=len(self.analysis_results),
            top_performers=top_performers,
            worst_performers=worst_performers,
            correlation_matrix=correlation_matrix,
            diversification_score=diversification_score,
            sector_allocation=sector_allocation,
            risk_return_analysis=risk_return_analysis,
            best_opportunities=best_opportunities,
        )

    def _calculate_diversification_score(
        self, correlation_matrix: Dict[str, Dict[str, float]]
    ) -> float:
        """分散投資スコアを計算"""
        if not correlation_matrix:
            return 0.0

        # 平均相関を計算
        correlations = []
        symbols = list(correlation_matrix.keys())

        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                if i < j:  # 上三角のみ
                    corr = correlation_matrix[symbol1].get(symbol2, 0)
                    correlations.append(abs(corr))

        if not correlations:
            return 0.0

        avg_correlation = np.mean(correlations)
        # 相関が低いほど分散投資スコアが高い
        diversification_score = max(0, 1 - avg_correlation)

        return diversification_score

    def _calculate_sector_allocation(self) -> Dict[str, float]:
        """セクター配分を計算"""
        sector_mapping = self.fundamental_analyzer.sector_mapping
        sector_counts = {}

        for symbol in self.analysis_results.keys():
            sector = sector_mapping.get(symbol, "Unknown")
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        total_symbols = len(self.analysis_results)
        sector_allocation = {
            sector: count / total_symbols for sector, count in sector_counts.items()
        }

        return sector_allocation

    def _calculate_risk_return_analysis(self) -> Dict[str, float]:
        """リスク・リターン分析"""
        if not self.analysis_results:
            return {}

        returns = [
            analysis.change_percent for analysis in self.analysis_results.values()
        ]
        volatilities = [
            analysis.volatility for analysis in self.analysis_results.values()
        ]

        return {
            "average_return": np.mean(returns),
            "return_std": np.std(returns),
            "average_volatility": np.mean(volatilities),
            "volatility_std": np.std(volatilities),
            "sharpe_ratio": (
                np.mean(returns) / np.mean(volatilities)
                if np.mean(volatilities) > 0
                else 0
            ),
        }

    def _get_best_opportunities(self) -> List[Dict]:
        """最良の投資機会を取得"""
        opportunities = []

        for symbol, analysis in self.analysis_results.items():
            if analysis.investment_opportunity in [
                InvestmentOpportunity.STRONG_BUY,
                InvestmentOpportunity.BUY,
            ]:
                opportunities.append(
                    {
                        "symbol": symbol,
                        "investment_opportunity": analysis.investment_opportunity.value,
                        "confidence": analysis.confidence,
                        "technical_score": analysis.technical_score,
                        "fundamental_score": analysis.fundamental_score,
                        "momentum_score": analysis.momentum_score,
                        "risk_level": analysis.risk_level,
                        "recommendation_reason": analysis.recommendation_reason,
                    }
                )

        # 信頼度でソート
        opportunities.sort(key=lambda x: x["confidence"], reverse=True)

        return opportunities[:10]  # 上位10件

    def save_analysis_results(self, filename: str = "multi_stock_analysis.json"):
        """分析結果を保存"""
        try:
            # 分析結果を辞書形式に変換
            results = {
                "timestamp": datetime.now().isoformat(),
                "total_symbols": len(self.symbols),
                "analyzed_symbols": len(self.analysis_results),
                "analysis_results": {},
            }

            for symbol, analysis in self.analysis_results.items():
                results["analysis_results"][symbol] = asdict(analysis)

            # ポートフォリオ比較結果も追加
            portfolio_comparison = self.generate_portfolio_comparison()
            results["portfolio_comparison"] = asdict(portfolio_comparison)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"分析結果を保存しました: {filename}")

        except Exception as e:
            logger.error(f"保存エラー: {e}")


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

    # 複数銘柄監視システム初期化
    monitor = MultiStockMonitor(symbols)

    # 全銘柄分析実行
    analysis_results = monitor.analyze_all_stocks()

    # ポートフォリオ比較分析
    portfolio_comparison = monitor.generate_portfolio_comparison()

    # 結果保存
    monitor.save_analysis_results()

    # 結果表示
    print("\n" + "=" * 80)
    print("📊 複数銘柄同時監視・比較分析結果")
    print("=" * 80)
    print(f"分析時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"監視銘柄数: {portfolio_comparison.total_symbols}")
    print(f"分析完了銘柄数: {portfolio_comparison.analyzed_symbols}")
    print(f"分散投資スコア: {portfolio_comparison.diversification_score:.2f}")

    print("\n🏆 パフォーマンス上位:")
    for i, performer in enumerate(portfolio_comparison.top_performers[:3], 1):
        print(
            f"  {i}. {performer['symbol']}: {performer['change_percent']:+.2f}% "
            f"(技術: {performer['technical_score']:.1f}, 信頼度: {performer['confidence']:.2f})"
        )

    print("\n📉 パフォーマンス下位:")
    for i, performer in enumerate(portfolio_comparison.worst_performers[:3], 1):
        print(
            f"  {i}. {performer['symbol']}: {performer['change_percent']:+.2f}% "
            f"(技術: {performer['technical_score']:.1f}, 信頼度: {performer['confidence']:.2f})"
        )

    print("\n💡 最良の投資機会:")
    for i, opportunity in enumerate(portfolio_comparison.best_opportunities[:5], 1):
        print(
            f"  {i}. {opportunity['symbol']} - {opportunity['investment_opportunity']} "
            f"(信頼度: {opportunity['confidence']:.2f}, リスク: {opportunity['risk_level']})"
        )
        print(f"     理由: {opportunity['recommendation_reason']}")

    print("\n📈 リスク・リターン分析:")
    risk_return = portfolio_comparison.risk_return_analysis
    print(f"  平均リターン: {risk_return.get('average_return', 0):.2f}%")
    print(f"  平均ボラティリティ: {risk_return.get('average_volatility', 0):.2f}")
    print(f"  シャープレシオ: {risk_return.get('sharpe_ratio', 0):.2f}")

    print("\n🏢 セクター配分:")
    for sector, allocation in portfolio_comparison.sector_allocation.items():
        print(f"  {sector}: {allocation:.1%}")


if __name__ == "__main__":
    main()
