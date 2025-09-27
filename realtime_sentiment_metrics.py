#!/usr/bin/env python3
"""
リアルタイム感情指標生成システム
感情分析に基づくリアルタイム指標の生成と監視

機能:
- リアルタイム感情スコアの計算
- 感情トレンドの追跡
- 感情指標の可視化
- アラート機能
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import yfinance as yf
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import threading
import time
from collections import deque
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# 既存システムのインポート
try:
    from sentiment_analysis_system import SentimentTradingSystem, SentimentType
    from enhanced_sentiment_trading import EnhancedSentimentTradingSystem
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("realtime_sentiment_metrics.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指標タイプの定義"""
    SENTIMENT_SCORE = "sentiment_score"
    VOLATILITY_INDEX = "volatility_index"
    TREND_STRENGTH = "trend_strength"
    RISK_LEVEL = "risk_level"
    MOMENTUM = "momentum"


@dataclass
class RealtimeSentimentMetric:
    """リアルタイム感情指標"""
    timestamp: datetime
    symbol: str
    metric_type: MetricType
    value: float
    confidence: float
    trend: str  # "up", "down", "stable"
    alert_level: str  # "low", "medium", "high", "critical"


@dataclass
class SentimentTrend:
    """感情トレンド"""
    symbol: str
    timeframe: str
    trend_direction: str
    strength: float
    duration: int  # 分
    volatility: float


class RealtimeSentimentMetricsGenerator:
    """リアルタイム感情指標生成器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sentiment_system = None
        self.metrics_history = deque(maxlen=1000)
        self.trends = {}
        self.alerts = []
        self.is_running = False
        
        # 指標計算パラメータ
        self.sentiment_weights = {
            'news': 0.4,
            'social': 0.3,
            'technical': 0.2,
            'market': 0.1
        }
        
        # アラート閾値
        self.alert_thresholds = {
            'critical': 0.9,
            'high': 0.7,
            'medium': 0.5,
            'low': 0.3
        }
        
        self._initialize_sentiment_system()
    
    def _initialize_sentiment_system(self):
        """感情分析システムの初期化"""
        try:
            self.sentiment_system = SentimentTradingSystem()
            logger.info("感情分析システムの初期化に成功")
        except Exception as e:
            logger.error(f"感情分析システムの初期化に失敗: {e}")
            self.sentiment_system = None
    
    async def generate_realtime_metrics(self, symbols: List[str]) -> List[RealtimeSentimentMetric]:
        """リアルタイム感情指標の生成"""
        metrics = []
        
        for symbol in symbols:
            try:
                # 感情スコアの計算
                sentiment_score = await self._calculate_sentiment_score(symbol)
                
                # ボラティリティ指標の計算
                volatility_index = await self._calculate_volatility_index(symbol)
                
                # トレンド強度の計算
                trend_strength = await self._calculate_trend_strength(symbol)
                
                # リスクレベルの計算
                risk_level = await self._calculate_risk_level(symbol, sentiment_score, volatility_index)
                
                # モメンタムの計算
                momentum = await self._calculate_momentum(symbol)
                
                # 指標の作成
                metric_data = [
                    (MetricType.SENTIMENT_SCORE, sentiment_score),
                    (MetricType.VOLATILITY_INDEX, volatility_index),
                    (MetricType.TREND_STRENGTH, trend_strength),
                    (MetricType.RISK_LEVEL, risk_level),
                    (MetricType.MOMENTUM, momentum)
                ]
                
                for metric_type, value in metric_data:
                    confidence = self._calculate_confidence(symbol, metric_type, value)
                    trend = self._determine_trend(symbol, metric_type, value)
                    alert_level = self._determine_alert_level(metric_type, value)
                    
                    metric = RealtimeSentimentMetric(
                        timestamp=datetime.now(),
                        symbol=symbol,
                        metric_type=metric_type,
                        value=value,
                        confidence=confidence,
                        trend=trend,
                        alert_level=alert_level
                    )
                    
                    metrics.append(metric)
                    self.metrics_history.append(metric)
                
                # トレンドの更新
                await self._update_trends(symbol, metrics)
                
            except Exception as e:
                logger.error(f"シンボル {symbol} の指標生成に失敗: {e}")
        
        return metrics
    
    async def _calculate_sentiment_score(self, symbol: str) -> float:
        """感情スコアの計算"""
        try:
            if self.sentiment_system:
                # 既存システムを使用
                sentiment_data = await self.sentiment_system.analyze_sentiment(symbol)
                return sentiment_data.get('overall_sentiment', 0.0)
            else:
                # フォールバック計算
                return self._fallback_sentiment_calculation(symbol)
        except Exception as e:
            logger.error(f"感情スコアの計算に失敗: {e}")
            return 0.0
    
    def _fallback_sentiment_calculation(self, symbol: str) -> float:
        """フォールバック感情計算"""
        try:
            # 簡単な価格ベースの感情計算
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            
            if len(hist) < 2:
                return 0.0
            
            # 価格変化率ベースの感情スコア
            price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
            
            # -1から1の範囲に正規化
            sentiment = np.tanh(price_change * 10)
            return float(sentiment)
            
        except Exception as e:
            logger.error(f"フォールバック感情計算に失敗: {e}")
            return 0.0
    
    async def _calculate_volatility_index(self, symbol: str) -> float:
        """ボラティリティ指標の計算"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="30d")
            
            if len(hist) < 2:
                return 0.0
            
            # 価格の標準偏差を計算
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # 年率化
            
            return float(volatility)
            
        except Exception as e:
            logger.error(f"ボラティリティ指標の計算に失敗: {e}")
            return 0.0
    
    async def _calculate_trend_strength(self, symbol: str) -> float:
        """トレンド強度の計算"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="20d")
            
            if len(hist) < 10:
                return 0.0
            
            # 移動平均の傾きを計算
            ma_short = hist['Close'].rolling(window=5).mean()
            ma_long = hist['Close'].rolling(window=20).mean()
            
            # トレンド強度の計算
            trend_strength = (ma_short.iloc[-1] - ma_long.iloc[-1]) / ma_long.iloc[-1]
            
            return float(trend_strength)
            
        except Exception as e:
            logger.error(f"トレンド強度の計算に失敗: {e}")
            return 0.0
    
    async def _calculate_risk_level(self, symbol: str, sentiment: float, volatility: float) -> float:
        """リスクレベルの計算"""
        try:
            # 感情とボラティリティを組み合わせたリスク計算
            sentiment_risk = abs(sentiment) * 0.5  # 極端な感情はリスク
            volatility_risk = volatility * 0.5
            
            # 総合リスクスコア
            total_risk = (sentiment_risk + volatility_risk) / 2
            
            return min(total_risk, 1.0)  # 最大1.0に制限
            
        except Exception as e:
            logger.error(f"リスクレベルの計算に失敗: {e}")
            return 0.5
    
    async def _calculate_momentum(self, symbol: str) -> float:
        """モメンタムの計算"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="10d")
            
            if len(hist) < 5:
                return 0.0
            
            # 価格モメンタムの計算
            momentum = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
            
            return float(momentum)
            
        except Exception as e:
            logger.error(f"モメンタムの計算に失敗: {e}")
            return 0.0
    
    def _calculate_confidence(self, symbol: str, metric_type: MetricType, value: float) -> float:
        """信頼度の計算"""
        try:
            # 履歴データに基づく信頼度計算
            recent_metrics = [m for m in self.metrics_history 
                            if m.symbol == symbol and m.metric_type == metric_type]
            
            if len(recent_metrics) < 3:
                return 0.5  # デフォルト信頼度
            
            # 値の安定性を計算
            values = [m.value for m in recent_metrics[-10:]]
            stability = 1.0 - np.std(values) if len(values) > 1 else 0.5
            
            return min(stability, 1.0)
            
        except Exception as e:
            logger.error(f"信頼度の計算に失敗: {e}")
            return 0.5
    
    def _determine_trend(self, symbol: str, metric_type: MetricType, value: float) -> str:
        """トレンドの判定"""
        try:
            recent_metrics = [m for m in self.metrics_history 
                            if m.symbol == symbol and m.metric_type == metric_type]
            
            if len(recent_metrics) < 2:
                return "stable"
            
            # 最近の値の変化を分析
            recent_values = [m.value for m in recent_metrics[-5:]]
            
            if len(recent_values) < 2:
                return "stable"
            
            # トレンドの判定
            if recent_values[-1] > recent_values[-2]:
                return "up"
            elif recent_values[-1] < recent_values[-2]:
                return "down"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"トレンドの判定に失敗: {e}")
            return "stable"
    
    def _determine_alert_level(self, metric_type: MetricType, value: float) -> str:
        """アラートレベルの判定"""
        try:
            abs_value = abs(value)
            
            if abs_value >= self.alert_thresholds['critical']:
                return "critical"
            elif abs_value >= self.alert_thresholds['high']:
                return "high"
            elif abs_value >= self.alert_thresholds['medium']:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"アラートレベルの判定に失敗: {e}")
            return "low"
    
    async def _update_trends(self, symbol: str, metrics: List[RealtimeSentimentMetric]):
        """トレンドの更新"""
        try:
            sentiment_metrics = [m for m in metrics if m.metric_type == MetricType.SENTIMENT_SCORE]
            
            if not sentiment_metrics:
                return
            
            sentiment_value = sentiment_metrics[0].value
            
            if symbol not in self.trends:
                self.trends[symbol] = SentimentTrend(
                    symbol=symbol,
                    timeframe="realtime",
                    trend_direction="stable",
                    strength=0.0,
                    duration=0,
                    volatility=0.0
                )
            
            trend = self.trends[symbol]
            
            # トレンド方向の更新
            if sentiment_value > 0.1:
                trend.trend_direction = "positive"
            elif sentiment_value < -0.1:
                trend.trend_direction = "negative"
            else:
                trend.trend_direction = "neutral"
            
            # トレンド強度の更新
            trend.strength = abs(sentiment_value)
            
            # ボラティリティの更新
            volatility_metrics = [m for m in metrics if m.metric_type == MetricType.VOLATILITY_INDEX]
            if volatility_metrics:
                trend.volatility = volatility_metrics[0].value
            
        except Exception as e:
            logger.error(f"トレンドの更新に失敗: {e}")
    
    def get_metrics_summary(self, symbol: str = None) -> Dict[str, Any]:
        """指標サマリーの取得"""
        try:
            if symbol:
                metrics = [m for m in self.metrics_history if m.symbol == symbol]
            else:
                metrics = list(self.metrics_history)
            
            if not metrics:
                return {"error": "指標データがありません"}
            
            # 最新の指標を取得
            latest_metrics = {}
            for metric in metrics:
                if metric.symbol not in latest_metrics:
                    latest_metrics[metric.symbol] = {}
                latest_metrics[metric.symbol][metric.metric_type.value] = {
                    "value": metric.value,
                    "confidence": metric.confidence,
                    "trend": metric.trend,
                    "alert_level": metric.alert_level,
                    "timestamp": metric.timestamp.isoformat()
                }
            
            return latest_metrics
            
        except Exception as e:
            logger.error(f"指標サマリーの取得に失敗: {e}")
            return {"error": str(e)}
    
    def generate_alerts(self) -> List[Dict[str, Any]]:
        """アラートの生成"""
        alerts = []
        
        try:
            # 最新の指標をチェック
            recent_metrics = list(self.metrics_history)[-100:]  # 最新100件
            
            for metric in recent_metrics:
                if metric.alert_level in ["high", "critical"]:
                    alert = {
                        "timestamp": metric.timestamp.isoformat(),
                        "symbol": metric.symbol,
                        "metric_type": metric.metric_type.value,
                        "value": metric.value,
                        "alert_level": metric.alert_level,
                        "message": self._generate_alert_message(metric)
                    }
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"アラートの生成に失敗: {e}")
            return []
    
    def _generate_alert_message(self, metric: RealtimeSentimentMetric) -> str:
        """アラートメッセージの生成"""
        try:
            if metric.metric_type == MetricType.SENTIMENT_SCORE:
                if metric.value > 0.7:
                    return f"強いポジティブ感情が検出されました: {metric.value:.2f}"
                elif metric.value < -0.7:
                    return f"強いネガティブ感情が検出されました: {metric.value:.2f}"
            elif metric.metric_type == MetricType.VOLATILITY_INDEX:
                if metric.value > 0.3:
                    return f"高いボラティリティが検出されました: {metric.value:.2f}"
            elif metric.metric_type == MetricType.RISK_LEVEL:
                if metric.value > 0.8:
                    return f"高いリスクレベルが検出されました: {metric.value:.2f}"
            
            return f"{metric.metric_type.value}の異常値が検出されました: {metric.value:.2f}"
            
        except Exception as e:
            logger.error(f"アラートメッセージの生成に失敗: {e}")
            return "アラートが発生しました"
    
    def visualize_metrics(self, symbol: str, save_path: str = None):
        """指標の可視化"""
        try:
            symbol_metrics = [m for m in self.metrics_history if m.symbol == symbol]
            
            if not symbol_metrics:
                logger.warning(f"シンボル {symbol} の指標データがありません")
                return
            
            # データの整理
            timestamps = [m.timestamp for m in symbol_metrics]
            sentiment_scores = [m.value for m in symbol_metrics if m.metric_type == MetricType.SENTIMENT_SCORE]
            volatility_scores = [m.value for m in symbol_metrics if m.metric_type == MetricType.VOLATILITY_INDEX]
            
            # プロットの作成
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'{symbol} - リアルタイム感情指標', fontsize=16)
            
            # 感情スコアのプロット
            if sentiment_scores:
                axes[0, 0].plot(timestamps[:len(sentiment_scores)], sentiment_scores, 'b-', linewidth=2)
                axes[0, 0].set_title('感情スコア')
                axes[0, 0].set_ylabel('スコア')
                axes[0, 0].grid(True)
            
            # ボラティリティのプロット
            if volatility_scores:
                axes[0, 1].plot(timestamps[:len(volatility_scores)], volatility_scores, 'r-', linewidth=2)
                axes[0, 1].set_title('ボラティリティ指標')
                axes[0, 1].set_ylabel('ボラティリティ')
                axes[0, 1].grid(True)
            
            # リスクレベルのプロット
            risk_scores = [m.value for m in symbol_metrics if m.metric_type == MetricType.RISK_LEVEL]
            if risk_scores:
                axes[1, 0].plot(timestamps[:len(risk_scores)], risk_scores, 'orange', linewidth=2)
                axes[1, 0].set_title('リスクレベル')
                axes[1, 0].set_ylabel('リスク')
                axes[1, 0].grid(True)
            
            # モメンタムのプロット
            momentum_scores = [m.value for m in symbol_metrics if m.metric_type == MetricType.MOMENTUM]
            if momentum_scores:
                axes[1, 1].plot(timestamps[:len(momentum_scores)], momentum_scores, 'g-', linewidth=2)
                axes[1, 1].set_title('モメンタム')
                axes[1, 1].set_ylabel('モメンタム')
                axes[1, 1].grid(True)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"指標グラフを保存しました: {save_path}")
            else:
                plt.show()
                
        except Exception as e:
            logger.error(f"指標の可視化に失敗: {e}")
    
    async def start_monitoring(self, symbols: List[str], interval: int = 60):
        """監視の開始"""
        self.is_running = True
        logger.info(f"リアルタイム監視を開始: {symbols}")
        
        while self.is_running:
            try:
                # 指標の生成
                metrics = await self.generate_realtime_metrics(symbols)
                
                # アラートのチェック
                alerts = self.generate_alerts()
                if alerts:
                    logger.warning(f"アラートが発生しました: {len(alerts)}件")
                    for alert in alerts:
                        logger.warning(f"アラート: {alert['message']}")
                
                # 待機
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"監視中のエラー: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """監視の停止"""
        self.is_running = False
        logger.info("リアルタイム監視を停止しました")


async def main():
    """メイン関数"""
    # 設定
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    # 指標生成器の初期化
    metrics_generator = RealtimeSentimentMetricsGenerator()
    
    # 初期指標の生成
    logger.info("初期指標を生成中...")
    initial_metrics = await metrics_generator.generate_realtime_metrics(symbols)
    logger.info(f"初期指標を生成しました: {len(initial_metrics)}件")
    
    # 指標サマリーの表示
    summary = metrics_generator.get_metrics_summary()
    logger.info(f"指標サマリー: {json.dumps(summary, indent=2, ensure_ascii=False)}")
    
    # アラートのチェック
    alerts = metrics_generator.generate_alerts()
    if alerts:
        logger.info(f"アラート: {len(alerts)}件")
        for alert in alerts:
            logger.info(f"  - {alert['message']}")
    
    # 可視化の例
    if initial_metrics:
        symbol = initial_metrics[0].symbol
        metrics_generator.visualize_metrics(symbol, f"realtime_metrics_{symbol}.png")


if __name__ == "__main__":
    asyncio.run(main())
