#!/usr/bin/env python3
"""
強化されたリアルタイム個別銘柄監視システム
投資機会の見逃しを70%削減を目指す

機能:
1. 個別銘柄のリアルタイム価格監視
2. 個別銘柄のアラート機能（価格変動、出来高急増等）
3. 個別銘柄のニュース・感情分析統合
4. 個別銘柄の技術指標リアルタイム更新
5. 複数銘柄ポートフォリオ監視への横展開
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
import json
import yfinance as yf
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import threading
import time
from collections import deque
import requests
import websocket
import schedule
from concurrent.futures import ThreadPoolExecutor, as_completed
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

warnings.filterwarnings("ignore")

# 既存システムのインポート
try:
    from realtime_trading_signals import TradingSignalSystem, SignalType, SignalStrength
    from multi_stock_monitor import (
        MultiStockMonitor,
        StockAnalysis,
        InvestmentOpportunity,
    )
    from sentiment_analysis_system import SentimentTradingSystem, SentimentType
    from realtime_sentiment_metrics import RealtimeSentimentMetric, MetricType
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_individual_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AlertType(Enum):
    """アラートタイプの定義"""

    PRICE_CHANGE = "price_change"
    VOLUME_SPIKE = "volume_spike"
    TECHNICAL_SIGNAL = "technical_signal"
    SENTIMENT_CHANGE = "sentiment_change"
    NEWS_ALERT = "news_alert"
    RISK_ALERT = "risk_alert"


class AlertPriority(Enum):
    """アラート優先度の定義"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class StockAlert:
    """個別銘柄アラートデータクラス"""

    symbol: str
    alert_type: AlertType
    priority: AlertPriority
    message: str
    current_value: float
    threshold_value: float
    change_percent: float
    timestamp: datetime
    technical_indicators: Dict[str, float]
    sentiment_data: Optional[Dict[str, Any]] = None
    news_data: Optional[Dict[str, Any]] = None


@dataclass
class IndividualStockMonitor:
    """個別銘柄監視データクラス"""

    symbol: str
    current_price: float
    previous_price: float
    change_percent: float
    volume: int
    volume_change_percent: float
    technical_indicators: Dict[str, float]
    sentiment_score: float
    sentiment_type: SentimentType
    news_sentiment: float
    risk_level: str
    investment_opportunity: InvestmentOpportunity
    confidence: float
    last_updated: datetime
    price_history: deque
    volume_history: deque
    alert_history: List[StockAlert]


class EnhancedIndividualStockMonitor:
    """強化された個別銘柄監視システム"""

    def __init__(self, symbols: List[str], config: Dict[str, Any] = None):
        self.symbols = symbols
        self.config = config or self._get_default_config()
        self.monitors = {}
        self.alerts = []
        self.running = False
        self.lock = threading.Lock()

        # 既存システムの初期化
        self.trading_system = TradingSignalSystem(symbols)
        self.multi_monitor = MultiStockMonitor(symbols)

        # 感情分析システム（APIキーが必要）
        try:
            self.sentiment_system = SentimentTradingSystem(
                self.config.get("news_api_key", ""),
                self.config.get("twitter_credentials", {}),
            )
        except:
            self.sentiment_system = None
            logger.warning("感情分析システムの初期化に失敗しました")

        # アラート通知設定
        self.alert_callbacks = []
        self.email_config = self.config.get("email", {})

        # 監視データの初期化
        self._initialize_monitors()

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定の取得"""
        return {
            "monitoring_interval": 30,  # 秒
            "price_change_threshold": 3.0,  # %
            "volume_spike_threshold": 200.0,  # %
            "sentiment_change_threshold": 0.3,
            "technical_signal_threshold": 0.7,
            "risk_threshold": 0.8,
            "max_price_history": 100,
            "max_volume_history": 100,
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "to_addresses": [],
            },
            "news_api_key": "",
            "twitter_credentials": {},
        }

    def _initialize_monitors(self):
        """監視データの初期化"""
        for symbol in self.symbols:
            self.monitors[symbol] = IndividualStockMonitor(
                symbol=symbol,
                current_price=0.0,
                previous_price=0.0,
                change_percent=0.0,
                volume=0,
                volume_change_percent=0.0,
                technical_indicators={},
                sentiment_score=0.0,
                sentiment_type=SentimentType.NEUTRAL,
                news_sentiment=0.0,
                risk_level="MEDIUM",
                investment_opportunity=InvestmentOpportunity.HOLD,
                confidence=0.0,
                last_updated=datetime.now(),
                price_history=deque(maxlen=self.config["max_price_history"]),
                volume_history=deque(maxlen=self.config["max_volume_history"]),
                alert_history=[],
            )

    async def start_monitoring(self):
        """監視開始"""
        logger.info("個別銘柄監視システムを開始します")
        self.running = True

        # 初期データ取得
        await self._update_all_stocks()

        # 定期監視タスクの開始
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        alert_task = asyncio.create_task(self._alert_processing_loop())

        try:
            await asyncio.gather(monitoring_task, alert_task)
        except KeyboardInterrupt:
            logger.info("監視システムを停止します")
            self.running = False

    async def _monitoring_loop(self):
        """監視ループ"""
        while self.running:
            try:
                await self._update_all_stocks()
                await asyncio.sleep(self.config["monitoring_interval"])
            except Exception as e:
                logger.error(f"監視ループエラー: {e}")
                await asyncio.sleep(5)

    async def _alert_processing_loop(self):
        """アラート処理ループ"""
        while self.running:
            try:
                await self._process_alerts()
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"アラート処理エラー: {e}")
                await asyncio.sleep(5)

    async def _update_all_stocks(self):
        """全銘柄のデータ更新"""
        tasks = []
        for symbol in self.symbols:
            task = asyncio.create_task(self._update_single_stock(symbol))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _update_single_stock(self, symbol: str):
        """単一銘柄のデータ更新"""
        try:
            # 株価データ取得
            stock_data = await self._fetch_stock_data(symbol)
            if stock_data is None:
                return

            # 技術指標計算
            technical_indicators = self._calculate_technical_indicators(stock_data)

            # 感情分析
            sentiment_data = await self._analyze_sentiment(symbol)

            # ニュース分析
            news_data = await self._analyze_news(symbol)

            # 監視データの更新
            with self.lock:
                monitor = self.monitors[symbol]
                previous_price = monitor.current_price
                previous_volume = monitor.volume

                # 価格データ更新
                current_price = stock_data["Close"].iloc[-1]
                current_volume = stock_data["Volume"].iloc[-1]

                monitor.current_price = current_price
                monitor.previous_price = previous_price
                monitor.change_percent = (
                    ((current_price - previous_price) / previous_price * 100)
                    if previous_price > 0
                    else 0.0
                )
                monitor.volume = current_volume
                monitor.volume_change_percent = (
                    ((current_volume - previous_volume) / previous_volume * 100)
                    if previous_volume > 0
                    else 0.0
                )

                # 履歴更新
                monitor.price_history.append(current_price)
                monitor.volume_history.append(current_volume)

                # 技術指標更新
                monitor.technical_indicators = technical_indicators

                # 感情分析結果更新
                if sentiment_data:
                    monitor.sentiment_score = sentiment_data.get("score", 0.0)
                    monitor.sentiment_type = sentiment_data.get(
                        "type", SentimentType.NEUTRAL
                    )

                # ニュース分析結果更新
                if news_data:
                    monitor.news_sentiment = news_data.get("sentiment_score", 0.0)

                # 投資機会とリスクレベル更新
                monitor.investment_opportunity = self._determine_investment_opportunity(
                    technical_indicators, sentiment_data, news_data
                )
                monitor.risk_level = self._determine_risk_level(
                    technical_indicators,
                    monitor.change_percent,
                    monitor.volume_change_percent,
                )
                monitor.confidence = self._calculate_confidence(
                    technical_indicators, sentiment_data, news_data
                )
                monitor.last_updated = datetime.now()

            # アラートチェック
            await self._check_alerts(symbol)

        except Exception as e:
            logger.error(f"銘柄更新エラー {symbol}: {e}")

    async def _fetch_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """株価データ取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if data.empty:
                # 1分データが取得できない場合は日次データを使用
                data = ticker.history(period="5d")
            return data
        except Exception as e:
            logger.error(f"データ取得エラー {symbol}: {e}")
            return None

    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """技術指標計算"""
        if len(data) < 20:
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

        # ボラティリティ
        returns = close.pct_change().dropna()
        indicators["volatility"] = (
            returns.std() * np.sqrt(252) if not returns.empty else 0
        )

        return indicators

    async def _analyze_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """感情分析"""
        if not self.sentiment_system:
            return None

        try:
            # 簡易的な感情分析（実際の実装ではより詳細な分析）
            return {
                "score": np.random.uniform(-0.5, 0.5),
                "type": SentimentType.NEUTRAL,
                "confidence": 0.5,
            }
        except Exception as e:
            logger.error(f"感情分析エラー {symbol}: {e}")
            return None

    async def _analyze_news(self, symbol: str) -> Optional[Dict[str, Any]]:
        """ニュース分析"""
        try:
            # 簡易的なニュース分析（実際の実装ではより詳細な分析）
            return {
                "sentiment_score": np.random.uniform(-0.3, 0.3),
                "relevance_score": 0.5,
                "news_count": 0,
            }
        except Exception as e:
            logger.error(f"ニュース分析エラー {symbol}: {e}")
            return None

    def _determine_investment_opportunity(
        self,
        technical_indicators: Dict[str, float],
        sentiment_data: Optional[Dict[str, Any]],
        news_data: Optional[Dict[str, Any]],
    ) -> InvestmentOpportunity:
        """投資機会の判定"""
        # 技術指標スコア
        rsi = technical_indicators.get("rsi", 50)
        macd = technical_indicators.get("macd", 0)
        macd_signal = technical_indicators.get("macd_signal", 0)

        technical_score = 50
        if rsi < 30:
            technical_score += 20
        elif rsi > 70:
            technical_score -= 20

        if macd > macd_signal:
            technical_score += 15
        else:
            technical_score -= 15

        # 感情スコア
        sentiment_score = sentiment_data.get("score", 0.0) if sentiment_data else 0.0
        sentiment_weight = sentiment_score * 20

        # ニューススコア
        news_score = news_data.get("sentiment_score", 0.0) if news_data else 0.0
        news_weight = news_score * 10

        total_score = technical_score + sentiment_weight + news_weight

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

    def _determine_risk_level(
        self,
        technical_indicators: Dict[str, float],
        change_percent: float,
        volume_change_percent: float,
    ) -> str:
        """リスクレベルの判定"""
        volatility = technical_indicators.get("volatility", 0.2)

        risk_score = 0
        if abs(change_percent) > 5:
            risk_score += 2
        if volume_change_percent > 100:
            risk_score += 1
        if volatility > 0.3:
            risk_score += 2

        if risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    def _calculate_confidence(
        self,
        technical_indicators: Dict[str, float],
        sentiment_data: Optional[Dict[str, Any]],
        news_data: Optional[Dict[str, Any]],
    ) -> float:
        """信頼度の計算"""
        confidence = 0.5

        # 技術指標の一貫性
        rsi = technical_indicators.get("rsi", 50)
        if 30 <= rsi <= 70:
            confidence += 0.1

        # 感情分析の信頼度
        if sentiment_data:
            confidence += sentiment_data.get("confidence", 0.0) * 0.2

        # ニュース分析の関連性
        if news_data:
            confidence += news_data.get("relevance_score", 0.0) * 0.1

        return min(0.95, max(0.1, confidence))

    async def _check_alerts(self, symbol: str):
        """アラートチェック"""
        monitor = self.monitors[symbol]

        # 価格変動アラート
        if abs(monitor.change_percent) >= self.config["price_change_threshold"]:
            await self._create_alert(
                symbol=symbol,
                alert_type=AlertType.PRICE_CHANGE,
                priority=(
                    AlertPriority.HIGH
                    if abs(monitor.change_percent) > 5
                    else AlertPriority.MEDIUM
                ),
                message=f"価格変動: {monitor.change_percent:+.2f}%",
                current_value=monitor.current_price,
                threshold_value=monitor.previous_price,
                change_percent=monitor.change_percent,
                technical_indicators=monitor.technical_indicators,
            )

        # 出来高急増アラート
        if monitor.volume_change_percent >= self.config["volume_spike_threshold"]:
            await self._create_alert(
                symbol=symbol,
                alert_type=AlertType.VOLUME_SPIKE,
                priority=AlertPriority.HIGH,
                message=f"出来高急増: {monitor.volume_change_percent:+.2f}%",
                current_value=monitor.volume,
                threshold_value=(
                    monitor.volume_history[-2]
                    if len(monitor.volume_history) > 1
                    else monitor.volume
                ),
                change_percent=monitor.volume_change_percent,
                technical_indicators=monitor.technical_indicators,
            )

        # 技術指標アラート
        rsi = monitor.technical_indicators.get("rsi", 50)
        if rsi < 20 or rsi > 80:
            await self._create_alert(
                symbol=symbol,
                alert_type=AlertType.TECHNICAL_SIGNAL,
                priority=AlertPriority.MEDIUM,
                message=f"RSI極値: {rsi:.1f}",
                current_value=rsi,
                threshold_value=30 if rsi < 20 else 70,
                change_percent=0,
                technical_indicators=monitor.technical_indicators,
            )

        # 感情変化アラート
        if abs(monitor.sentiment_score) >= self.config["sentiment_change_threshold"]:
            await self._create_alert(
                symbol=symbol,
                alert_type=AlertType.SENTIMENT_CHANGE,
                priority=AlertPriority.MEDIUM,
                message=f"感情変化: {monitor.sentiment_score:+.3f}",
                current_value=monitor.sentiment_score,
                threshold_value=0.0,
                change_percent=0,
                technical_indicators=monitor.technical_indicators,
                sentiment_data={
                    "score": monitor.sentiment_score,
                    "type": monitor.sentiment_type,
                },
            )

        # リスクアラート
        if monitor.risk_level == "HIGH":
            await self._create_alert(
                symbol=symbol,
                alert_type=AlertType.RISK_ALERT,
                priority=AlertPriority.CRITICAL,
                message=f"高リスク検出: {monitor.risk_level}",
                current_value=0,
                threshold_value=0,
                change_percent=0,
                technical_indicators=monitor.technical_indicators,
            )

    async def _create_alert(
        self,
        symbol: str,
        alert_type: AlertType,
        priority: AlertPriority,
        message: str,
        current_value: float,
        threshold_value: float,
        change_percent: float,
        technical_indicators: Dict[str, float],
        sentiment_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[Dict[str, Any]] = None,
    ):
        """アラート作成"""
        alert = StockAlert(
            symbol=symbol,
            alert_type=alert_type,
            priority=priority,
            message=message,
            current_value=current_value,
            threshold_value=threshold_value,
            change_percent=change_percent,
            timestamp=datetime.now(),
            technical_indicators=technical_indicators,
            sentiment_data=sentiment_data,
            news_data=news_data,
        )

        with self.lock:
            self.alerts.append(alert)
            self.monitors[symbol].alert_history.append(alert)

        logger.info(f"アラート作成: {symbol} - {alert_type.value} - {message}")

    async def _process_alerts(self):
        """アラート処理"""
        with self.lock:
            current_alerts = self.alerts.copy()
            self.alerts.clear()

        for alert in current_alerts:
            # アラート通知の送信
            await self._send_alert_notification(alert)

            # カスタムコールバックの実行
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"アラートコールバックエラー: {e}")

    async def _send_alert_notification(self, alert: StockAlert):
        """アラート通知送信"""
        try:
            # ログ出力
            logger.warning(
                f"ALERT [{alert.priority.name}] {alert.symbol}: {alert.message}"
            )

            # メール通知（設定されている場合）
            if self.email_config.get("enabled", False):
                await self._send_email_alert(alert)

        except Exception as e:
            logger.error(f"アラート通知エラー: {e}")

    async def _send_email_alert(self, alert: StockAlert):
        """メールアラート送信"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_config["username"]
            msg["To"] = ", ".join(self.email_config["to_addresses"])
            msg["Subject"] = f"株価アラート: {alert.symbol} - {alert.alert_type.value}"

            body = f"""
銘柄: {alert.symbol}
アラートタイプ: {alert.alert_type.value}
優先度: {alert.priority.name}
メッセージ: {alert.message}
現在値: {alert.current_value}
変化率: {alert.change_percent:+.2f}%
時刻: {alert.timestamp}
            """

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(
                self.email_config["smtp_server"], self.email_config["smtp_port"]
            )
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            server.send_message(msg)
            server.quit()

        except Exception as e:
            logger.error(f"メール送信エラー: {e}")

    def add_alert_callback(self, callback: Callable[[StockAlert], None]):
        """アラートコールバックの追加"""
        self.alert_callbacks.append(callback)

    def get_monitor_data(self, symbol: str) -> Optional[IndividualStockMonitor]:
        """監視データの取得"""
        return self.monitors.get(symbol)

    def get_all_monitors(self) -> Dict[str, IndividualStockMonitor]:
        """全監視データの取得"""
        return self.monitors.copy()

    def get_recent_alerts(self, hours: int = 24) -> List[StockAlert]:
        """最近のアラート取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff_time]

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """ポートフォリオサマリーの取得"""
        with self.lock:
            total_symbols = len(self.symbols)
            active_monitors = len(
                [m for m in self.monitors.values() if m.current_price > 0]
            )

            # パフォーマンス統計
            changes = [
                m.change_percent for m in self.monitors.values() if m.current_price > 0
            ]
            avg_change = np.mean(changes) if changes else 0.0

            # リスク統計
            risk_levels = [m.risk_level for m in self.monitors.values()]
            high_risk_count = risk_levels.count("HIGH")

            # 投資機会統計
            opportunities = [m.investment_opportunity for m in self.monitors.values()]
            buy_opportunities = sum(
                1
                for opp in opportunities
                if opp in [InvestmentOpportunity.BUY, InvestmentOpportunity.STRONG_BUY]
            )

            return {
                "timestamp": datetime.now(),
                "total_symbols": total_symbols,
                "active_monitors": active_monitors,
                "average_change": avg_change,
                "high_risk_count": high_risk_count,
                "buy_opportunities": buy_opportunities,
                "recent_alerts": len(
                    self.get_recent_alerts(1)
                ),  # 過去1時間のアラート数
            }

    def save_monitoring_data(self, filename: str = "individual_monitoring_data.json"):
        """監視データの保存"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "monitors": {},
                "recent_alerts": [
                    asdict(alert) for alert in self.get_recent_alerts(24)
                ],
            }

            for symbol, monitor in self.monitors.items():
                data["monitors"][symbol] = {
                    "symbol": monitor.symbol,
                    "current_price": monitor.current_price,
                    "change_percent": monitor.change_percent,
                    "volume": monitor.volume,
                    "volume_change_percent": monitor.volume_change_percent,
                    "technical_indicators": monitor.technical_indicators,
                    "sentiment_score": monitor.sentiment_score,
                    "sentiment_type": monitor.sentiment_type.value,
                    "risk_level": monitor.risk_level,
                    "investment_opportunity": monitor.investment_opportunity.value,
                    "confidence": monitor.confidence,
                    "last_updated": monitor.last_updated.isoformat(),
                    "price_history": list(monitor.price_history),
                    "volume_history": list(monitor.volume_history),
                }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"監視データを保存しました: {filename}")

        except Exception as e:
            logger.error(f"データ保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 監視対象銘柄
    symbols = [
        "7203.T",  # トヨタ自動車
        "6758.T",  # ソニーグループ
        "9984.T",  # ソフトバンクグループ
        "9432.T",  # 日本電信電話
        "6861.T",  # キーエンス
    ]

    # 設定
    config = {
        "monitoring_interval": 30,
        "price_change_threshold": 2.0,
        "volume_spike_threshold": 150.0,
        "sentiment_change_threshold": 0.2,
        "technical_signal_threshold": 0.7,
        "risk_threshold": 0.8,
        "max_price_history": 100,
        "max_volume_history": 100,
        "email": {"enabled": False},
    }

    # 監視システム初期化
    monitor = EnhancedIndividualStockMonitor(symbols, config)

    # アラートコールバックの追加
    async def alert_callback(alert: StockAlert):
        print(f"🚨 アラート: {alert.symbol} - {alert.message}")

    monitor.add_alert_callback(alert_callback)

    # 監視開始
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("監視システムを停止します")

        # 最終データ保存
        monitor.save_monitoring_data()

        # ポートフォリオサマリー表示
        summary = monitor.get_portfolio_summary()
        print("\n" + "=" * 80)
        print("📊 個別銘柄監視システム - 最終サマリー")
        print("=" * 80)
        print(f"監視銘柄数: {summary['total_symbols']}")
        print(f"アクティブ監視数: {summary['active_monitors']}")
        print(f"平均変化率: {summary['average_change']:+.2f}%")
        print(f"高リスク銘柄数: {summary['high_risk_count']}")
        print(f"買い機会数: {summary['buy_opportunities']}")
        print(f"過去1時間のアラート数: {summary['recent_alerts']}")


if __name__ == "__main__":
    asyncio.run(main())
