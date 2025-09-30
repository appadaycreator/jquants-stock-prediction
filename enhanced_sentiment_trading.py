#!/usr/bin/env python3
"""
拡張感情分析トレーディングシステム
既存のrealtime_trading_signals.pyと統合した感情分析システム

機能:
- リアルタイム感情分析
- ニュース・SNS統合分析
- 既存トレーディングシグナルとの統合
- 月間5-15%利益向上のための最適化
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import yfinance as yf
from dataclasses import dataclass
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

# 既存システムのインポート
try:
    from realtime_trading_signals import TradingSignalGenerator, TechnicalAnalyzer
    from sentiment_analysis_system import SentimentTradingSystem, SentimentType
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

    # フォールバック実装
    class TradingSignalGenerator:
        def __init__(self):
            pass

    class TechnicalAnalyzer:
        def __init__(self):
            pass


# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_sentiment_trading.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedTradingSignal:
    """拡張トレーディングシグナル"""

    symbol: str
    timestamp: datetime
    technical_signal: str
    sentiment_signal: str
    combined_signal: str
    confidence: float
    sentiment_score: float
    technical_score: float
    combined_score: float
    risk_level: str
    position_size: float
    stop_loss: float
    take_profit: float


class EnhancedSentimentTradingSystem:
    """拡張感情分析トレーディングシステム"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sentiment_system = None
        self.technical_analyzer = TechnicalAnalyzer()
        self.trading_generator = TradingSignalGenerator()

        # 感情分析システムの初期化
        self._initialize_sentiment_system()

        # パフォーマンス追跡
        self.performance_metrics = {
            "total_trades": 0,
            "profitable_trades": 0,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "sentiment_accuracy": 0.0,
        }

        # 感情分析履歴
        self.sentiment_history = []
        self.trade_history = []

    def _initialize_sentiment_system(self):
        """感情分析システムの初期化"""
        try:
            # APIキーの設定（環境変数から取得）
            news_api_key = self.config.get("news_api_key", "")
            twitter_credentials = {
                "twitter_api_key": self.config.get("twitter_api_key", ""),
                "twitter_api_secret": self.config.get("twitter_api_secret", ""),
                "twitter_access_token": self.config.get("twitter_access_token", ""),
                "twitter_access_token_secret": self.config.get(
                    "twitter_access_token_secret", ""
                ),
            }

            if news_api_key and all(twitter_credentials.values()):
                self.sentiment_system = SentimentTradingSystem(
                    news_api_key, twitter_credentials
                )
                logger.info("感情分析システムが正常に初期化されました")
            else:
                logger.warning("APIキーが設定されていません。感情分析機能は無効です。")

        except Exception as e:
            logger.error(f"感情分析システムの初期化に失敗: {e}")
            self.sentiment_system = None

    async def generate_enhanced_signals(
        self, symbols: List[str], lookback_days: int = 30
    ) -> List[EnhancedTradingSignal]:
        """拡張トレーディングシグナルの生成"""
        enhanced_signals = []

        try:
            for symbol in symbols:
                # 技術分析シグナルの取得
                technical_signal = await self._get_technical_signal(
                    symbol, lookback_days
                )

                # 感情分析シグナルの取得
                sentiment_signal = await self._get_sentiment_signal(symbol)

                # 統合シグナルの生成
                combined_signal = self._combine_signals(
                    technical_signal, sentiment_signal
                )

                # リスク管理パラメータの計算
                risk_params = self._calculate_risk_parameters(symbol, combined_signal)

                # 拡張シグナルの作成
                enhanced_signal = EnhancedTradingSignal(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    technical_signal=technical_signal.get("signal", "HOLD"),
                    sentiment_signal=sentiment_signal.get("signal", "HOLD"),
                    combined_signal=combined_signal.get("signal", "HOLD"),
                    confidence=combined_signal.get("confidence", 0.0),
                    sentiment_score=sentiment_signal.get("score", 0.0),
                    technical_score=technical_signal.get("score", 0.0),
                    combined_score=combined_signal.get("score", 0.0),
                    risk_level=risk_params.get("risk_level", "MEDIUM"),
                    position_size=risk_params.get("position_size", 0.0),
                    stop_loss=risk_params.get("stop_loss", 0.0),
                    take_profit=risk_params.get("take_profit", 0.0),
                )

                enhanced_signals.append(enhanced_signal)

        except Exception as e:
            logger.error(f"拡張シグナル生成エラー: {e}")

        return enhanced_signals

    async def _get_technical_signal(
        self, symbol: str, lookback_days: int
    ) -> Dict[str, Any]:
        """技術分析シグナルの取得"""
        try:
            # 株価データの取得
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                return {"signal": "HOLD", "score": 0.0, "confidence": 0.0}

            # 技術指標の計算
            current_price = hist["Close"].iloc[-1]
            sma_20 = hist["Close"].rolling(window=20).mean().iloc[-1]
            sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]

            # RSIの計算
            delta = hist["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]

            # ボリンジャーバンドの計算
            bb_middle = hist["Close"].rolling(window=20).mean()
            bb_std = hist["Close"].rolling(window=20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)

            current_bb_upper = bb_upper.iloc[-1]
            current_bb_lower = bb_lower.iloc[-1]

            # シグナルの生成
            signal_score = 0.0
            signal = "HOLD"

            # 移動平均線シグナル
            if current_price > sma_20 > sma_50:
                signal_score += 0.3
            elif current_price < sma_20 < sma_50:
                signal_score -= 0.3

            # RSIシグナル
            if current_rsi < 30:  # オーバーセル
                signal_score += 0.2
            elif current_rsi > 70:  # オーバーボート
                signal_score -= 0.2

            # ボリンジャーバンドシグナル
            if current_price < current_bb_lower:
                signal_score += 0.2
            elif current_price > current_bb_upper:
                signal_score -= 0.2

            # シグナルの決定
            if signal_score > 0.3:
                signal = "BUY"
            elif signal_score < -0.3:
                signal = "SELL"

            return {
                "signal": signal,
                "score": signal_score,
                "confidence": min(abs(signal_score), 1.0),
                "rsi": current_rsi,
                "price": current_price,
                "sma_20": sma_20,
                "sma_50": sma_50,
            }

        except Exception as e:
            logger.error(f"技術分析シグナル取得エラー ({symbol}): {e}")
            return {"signal": "HOLD", "score": 0.0, "confidence": 0.0}

    async def _get_sentiment_signal(self, symbol: str) -> Dict[str, Any]:
        """感情分析シグナルの取得"""
        try:
            if not self.sentiment_system:
                return {"signal": "HOLD", "score": 0.0, "confidence": 0.0}

            # 感情分析シグナルの生成
            sentiment_data = await self.sentiment_system.generate_sentiment_signals(
                [symbol]
            )

            if not sentiment_data:
                return {"signal": "HOLD", "score": 0.0, "confidence": 0.0}

            overall_sentiment = sentiment_data.get("overall_sentiment", {})
            score = overall_sentiment.get("score", 0.0)
            confidence = overall_sentiment.get("confidence", 0.0)

            # シグナルの決定
            if score > 0.3 and confidence > 0.6:
                signal = "BUY"
            elif score < -0.3 and confidence > 0.6:
                signal = "SELL"
            else:
                signal = "HOLD"

            return {
                "signal": signal,
                "score": score,
                "confidence": confidence,
                "type": overall_sentiment.get("type", SentimentType.NEUTRAL),
            }

        except Exception as e:
            logger.error(f"感情分析シグナル取得エラー ({symbol}): {e}")
            return {"signal": "HOLD", "score": 0.0, "confidence": 0.0}

    def _combine_signals(
        self, technical_signal: Dict[str, Any], sentiment_signal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """技術分析と感情分析の統合"""
        try:
            # 重み付きスコアの計算
            technical_weight = 0.6  # 技術分析の重み
            sentiment_weight = 0.4  # 感情分析の重み

            technical_score = technical_signal.get("score", 0.0)
            sentiment_score = sentiment_signal.get("score", 0.0)

            combined_score = (technical_score * technical_weight) + (
                sentiment_score * sentiment_weight
            )

            # 信頼度の計算
            technical_confidence = technical_signal.get("confidence", 0.0)
            sentiment_confidence = sentiment_signal.get("confidence", 0.0)
            combined_confidence = (technical_confidence * technical_weight) + (
                sentiment_confidence * sentiment_weight
            )

            # シグナルの決定
            if combined_score > 0.3 and combined_confidence > 0.6:
                signal = "BUY"
            elif combined_score < -0.3 and combined_confidence > 0.6:
                signal = "SELL"
            else:
                signal = "HOLD"

            return {
                "signal": signal,
                "score": combined_score,
                "confidence": combined_confidence,
                "technical_contribution": technical_score * technical_weight,
                "sentiment_contribution": sentiment_score * sentiment_weight,
            }

        except Exception as e:
            logger.error(f"シグナル統合エラー: {e}")
            return {"signal": "HOLD", "score": 0.0, "confidence": 0.0}

    def _calculate_risk_parameters(
        self, symbol: str, combined_signal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """リスク管理パラメータの計算"""
        try:
            # 現在価格の取得
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if hist.empty:
                return {
                    "risk_level": "MEDIUM",
                    "position_size": 0.0,
                    "stop_loss": 0.0,
                    "take_profit": 0.0,
                }

            current_price = hist["Close"].iloc[-1]
            volatility = hist["Close"].pct_change().std() * np.sqrt(252)  # 年率ボラティリティ

            # リスクレベルの決定
            confidence = combined_signal.get("confidence", 0.0)
            score = abs(combined_signal.get("score", 0.0))

            if confidence > 0.8 and score > 0.5:
                risk_level = "LOW"
                position_size = 0.1  # 10%のポジションサイズ
            elif confidence > 0.6 and score > 0.3:
                risk_level = "MEDIUM"
                position_size = 0.05  # 5%のポジションサイズ
            else:
                risk_level = "HIGH"
                position_size = 0.02  # 2%のポジションサイズ

            # ストップロスとテイクプロフィットの計算
            stop_loss_pct = volatility * 2  # ボラティリティの2倍
            take_profit_pct = stop_loss_pct * 2  # リスクリワード比1:2

            stop_loss = current_price * (1 - stop_loss_pct)
            take_profit = current_price * (1 + take_profit_pct)

            return {
                "risk_level": risk_level,
                "position_size": position_size,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "volatility": volatility,
            }

        except Exception as e:
            logger.error(f"リスクパラメータ計算エラー ({symbol}): {e}")
            return {
                "risk_level": "MEDIUM",
                "position_size": 0.0,
                "stop_loss": 0.0,
                "take_profit": 0.0,
            }

    def update_performance_metrics(self, trade_result: Dict[str, Any]):
        """パフォーマンス指標の更新"""
        try:
            self.performance_metrics["total_trades"] += 1

            if trade_result.get("profit", 0) > 0:
                self.performance_metrics["profitable_trades"] += 1

            self.performance_metrics["total_return"] += trade_result.get("return", 0)

            # シャープレシオの計算（簡易版）
            if self.performance_metrics["total_trades"] > 10:
                returns = [t.get("return", 0) for t in self.trade_history[-20:]]
                if returns:
                    avg_return = np.mean(returns)
                    std_return = np.std(returns)
                    if std_return > 0:
                        self.performance_metrics["sharpe_ratio"] = (
                            avg_return / std_return
                        )

            # 感情分析精度の計算
            if len(self.sentiment_history) > 10:
                correct_predictions = sum(
                    1
                    for h in self.sentiment_history[-20:]
                    if (h["score"] > 0 and h.get("actual_return", 0) > 0)
                    or (h["score"] < 0 and h.get("actual_return", 0) < 0)
                )
                self.performance_metrics[
                    "sentiment_accuracy"
                ] = correct_predictions / len(self.sentiment_history[-20:])

        except Exception as e:
            logger.error(f"パフォーマンス指標更新エラー: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーの取得"""
        try:
            total_trades = self.performance_metrics["total_trades"]
            profitable_trades = self.performance_metrics["profitable_trades"]

            win_rate = (
                (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            )

            return {
                "total_trades": total_trades,
                "profitable_trades": profitable_trades,
                "win_rate": win_rate,
                "total_return": self.performance_metrics["total_return"],
                "sharpe_ratio": self.performance_metrics["sharpe_ratio"],
                "sentiment_accuracy": self.performance_metrics["sentiment_accuracy"],
                "expected_monthly_return": self._calculate_expected_monthly_return(),
            }

        except Exception as e:
            logger.error(f"パフォーマンスサマリー取得エラー: {e}")
            return {}

    def _calculate_expected_monthly_return(self) -> float:
        """月間期待リターンの計算"""
        try:
            if not self.trade_history:
                return 0.0

            # 過去の取引履歴から月間リターンを推定
            recent_returns = [t.get("return", 0) for t in self.trade_history[-30:]]
            if not recent_returns:
                return 0.0

            avg_daily_return = np.mean(recent_returns)
            expected_monthly_return = avg_daily_return * 22  # 月間営業日数

            # 感情分析の精度を考慮した調整
            sentiment_accuracy = self.performance_metrics.get("sentiment_accuracy", 0.5)
            adjusted_return = expected_monthly_return * (0.5 + sentiment_accuracy)

            return min(adjusted_return, 0.15)  # 最大15%に制限

        except Exception as e:
            logger.error(f"月間期待リターン計算エラー: {e}")
            return 0.0


# 設定ファイルの例
SENTIMENT_TRADING_CONFIG = {
    "news_api_key": "your_news_api_key_here",
    "twitter_api_key": "your_twitter_api_key",
    "twitter_api_secret": "your_twitter_api_secret",
    "twitter_access_token": "your_twitter_access_token",
    "twitter_access_token_secret": "your_twitter_access_token_secret",
    "risk_management": {
        "max_position_size": 0.1,
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.04,
    },
    "sentiment_weights": {"news_weight": 0.7, "sns_weight": 0.3},
    "technical_weights": {"technical_weight": 0.6, "sentiment_weight": 0.4},
}


# 使用例
async def main():
    """メイン実行関数"""
    # 監視対象株式
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

    # 拡張感情分析トレーディングシステムの初期化
    enhanced_system = EnhancedSentimentTradingSystem(SENTIMENT_TRADING_CONFIG)

    # 拡張シグナルの生成
    enhanced_signals = await enhanced_system.generate_enhanced_signals(symbols)

    # 結果の表示
    print("=== 拡張感情分析トレーディングシステム ===")
    print(f"実行時刻: {datetime.now()}")
    print(f"生成されたシグナル数: {len(enhanced_signals)}")

    for signal in enhanced_signals:
        print(f"\n{signal.symbol}:")
        print(f"  統合シグナル: {signal.combined_signal}")
        print(f"  技術分析: {signal.technical_signal} (スコア: {signal.technical_score:.3f})")
        print(f"  感情分析: {signal.sentiment_signal} (スコア: {signal.sentiment_score:.3f})")
        print(f"  信頼度: {signal.confidence:.3f}")
        print(f"  リスクレベル: {signal.risk_level}")
        print(f"  ポジションサイズ: {signal.position_size:.1%}")
        print(f"  ストップロス: ${signal.stop_loss:.2f}")
        print(f"  テイクプロフィット: ${signal.take_profit:.2f}")

    # パフォーマンスサマリーの表示
    performance = enhanced_system.get_performance_summary()
    print(f"\n=== パフォーマンスサマリー ===")
    print(f"総取引数: {performance.get('total_trades', 0)}")
    print(f"勝率: {performance.get('win_rate', 0):.1f}%")
    print(f"総リターン: {performance.get('total_return', 0):.3f}")
    print(f"シャープレシオ: {performance.get('sharpe_ratio', 0):.3f}")
    print(f"感情分析精度: {performance.get('sentiment_accuracy', 0):.3f}")
    print(f"期待月間リターン: {performance.get('expected_monthly_return', 0):.1%}")


if __name__ == "__main__":
    asyncio.run(main())
