#!/usr/bin/env python3
"""
リアルタイム価格監視システム
1秒間隔での価格監視とアラート機能を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import threading
import time
import asyncio
from queue import Queue, Empty
import json
import requests
import websocket
from concurrent.futures import ThreadPoolExecutor
import warnings

warnings.filterwarnings("ignore")


class PriceAlertType(Enum):
    """価格アラートタイプ"""

    PRICE_BREAKOUT = "price_breakout"  # 価格ブレイクアウト
    VOLUME_SPIKE = "volume_spike"  # 出来高急増
    VOLATILITY_SPIKE = "volatility_spike"  # ボラティリティ急増
    TREND_CHANGE = "trend_change"  # トレンド変化
    SUPPORT_RESISTANCE = "support_resistance"  # サポート・レジスタンス
    MOVING_AVERAGE_CROSS = "moving_average_cross"  # 移動平均クロス


class MarketCondition(Enum):
    """市場状況"""

    NORMAL = "normal"  # 正常
    HIGH_VOLATILITY = "high_volatility"  # 高ボラティリティ
    LOW_VOLATILITY = "low_volatility"  # 低ボラティリティ
    TRENDING_UP = "trending_up"  # 上昇トレンド
    TRENDING_DOWN = "trending_down"  # 下降トレンド
    SIDEWAYS = "sideways"  # 横ばい


@dataclass
class PriceData:
    """価格データ"""

    symbol: str
    price: float
    high: float
    low: float
    volume: int
    timestamp: datetime
    change: float
    change_percent: float


@dataclass
class PriceAlert:
    """価格アラート"""

    timestamp: datetime
    symbol: str
    alert_type: PriceAlertType
    current_price: float
    threshold_price: float
    message: str
    severity: str
    metadata: Dict[str, Any]


@dataclass
class MarketSnapshot:
    """市場スナップショット"""

    timestamp: datetime
    symbol: str
    current_price: float
    market_condition: MarketCondition
    volatility: float
    trend_direction: str
    support_level: float
    resistance_level: float
    alerts: List[PriceAlert]
    technical_indicators: Dict[str, float]


class TechnicalAnalyzer:
    """テクニカル分析器"""

    def __init__(self, lookback_period: int = 20):
        """初期化"""
        self.lookback_period = lookback_period
        self.logger = logging.getLogger(__name__)

    def calculate_moving_averages(self, prices: List[float]) -> Dict[str, float]:
        """移動平均計算"""
        try:
            if len(prices) < self.lookback_period:
                return {}

            price_array = np.array(prices)

            # 短期・中期・長期移動平均
            sma_5 = np.mean(price_array[-5:])
            sma_10 = np.mean(price_array[-10:])
            sma_20 = np.mean(price_array[-20:])

            # 指数移動平均
            ema_12 = self._calculate_ema(price_array, 12)
            ema_26 = self._calculate_ema(price_array, 26)

            return {
                "sma_5": sma_5,
                "sma_10": sma_10,
                "sma_20": sma_20,
                "ema_12": ema_12,
                "ema_26": ema_26,
            }

        except Exception as e:
            self.logger.error(f"移動平均計算エラー: {e}")
            return {}

    def calculate_support_resistance(self, prices: List[float]) -> Dict[str, float]:
        """サポート・レジスタンス計算"""
        try:
            if len(prices) < 20:
                return {}

            price_array = np.array(prices)

            # ローカル高値・安値の検出
            highs = []
            lows = []

            for i in range(2, len(price_array) - 2):
                # ローカル高値
                if (
                    price_array[i] > price_array[i - 1]
                    and price_array[i] > price_array[i - 2]
                    and price_array[i] > price_array[i + 1]
                    and price_array[i] > price_array[i + 2]
                ):
                    highs.append(price_array[i])

                # ローカル安値
                if (
                    price_array[i] < price_array[i - 1]
                    and price_array[i] < price_array[i - 2]
                    and price_array[i] < price_array[i + 1]
                    and price_array[i] < price_array[i + 2]
                ):
                    lows.append(price_array[i])

            # サポート・レジスタンスレベル
            support_level = np.mean(lows) if lows else np.min(price_array)
            resistance_level = np.mean(highs) if highs else np.max(price_array)

            return {
                "support_level": support_level,
                "resistance_level": resistance_level,
                "local_highs": highs,
                "local_lows": lows,
            }

        except Exception as e:
            self.logger.error(f"サポート・レジスタンス計算エラー: {e}")
            return {}

    def calculate_volatility(self, prices: List[float]) -> float:
        """ボラティリティ計算"""
        try:
            if len(prices) < 2:
                return 0.0

            price_array = np.array(prices)
            returns = np.diff(np.log(price_array))
            volatility = np.std(returns) * np.sqrt(252)  # 年率

            return float(volatility)

        except Exception as e:
            self.logger.error(f"ボラティリティ計算エラー: {e}")
            return 0.0

    def detect_trend(self, prices: List[float]) -> str:
        """トレンド検出"""
        try:
            if len(prices) < 20:
                return "unknown"

            price_array = np.array(prices)

            # 短期・長期移動平均
            short_ma = np.mean(price_array[-5:])
            long_ma = np.mean(price_array[-20:])

            # トレンド判定
            if short_ma > long_ma * 1.02:  # 2%以上上回る
                return "uptrend"
            elif short_ma < long_ma * 0.98:  # 2%以上下回る
                return "downtrend"
            else:
                return "sideways"

        except Exception as e:
            self.logger.error(f"トレンド検出エラー: {e}")
            return "unknown"

    def detect_breakout(
        self, prices: List[float], support: float, resistance: float
    ) -> Dict[str, bool]:
        """ブレイクアウト検出"""
        try:
            if len(prices) < 2:
                return {"upward_breakout": False, "downward_breakout": False}

            current_price = prices[-1]
            previous_price = prices[-2]

            # 上向きブレイクアウト
            upward_breakout = (
                current_price > resistance and previous_price <= resistance
            )

            # 下向きブレイクアウト
            downward_breakout = current_price < support and previous_price >= support

            return {
                "upward_breakout": upward_breakout,
                "downward_breakout": downward_breakout,
            }

        except Exception as e:
            self.logger.error(f"ブレイクアウト検出エラー: {e}")
            return {"upward_breakout": False, "downward_breakout": False}

    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """指数移動平均計算"""
        try:
            if len(prices) < period:
                return float(np.mean(prices))

            alpha = 2.0 / (period + 1)
            ema = prices[0]

            for price in prices[1:]:
                ema = alpha * price + (1 - alpha) * ema

            return float(ema)

        except Exception as e:
            self.logger.error(f"EMA計算エラー: {e}")
            return float(np.mean(prices))


class RealtimePriceMonitor:
    """リアルタイム価格監視システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)

        # 監視状態
        self.is_monitoring = False
        self.monitor_thread = None
        self.price_queue = Queue()
        self.alert_queue = Queue()

        # データ管理
        self.price_data = {}  # {symbol: [PriceData]}
        self.market_snapshots = {}  # {symbol: MarketSnapshot}
        self.active_alerts = {}  # {symbol: [PriceAlert]}

        # 履歴データ
        self.price_history = []
        self.alert_history = []

        # コールバック関数
        self.price_callbacks = []
        self.alert_callbacks = []

        # 分析器
        self.technical_analyzer = TechnicalAnalyzer()

        # スレッドプール
        self.executor = ThreadPoolExecutor(max_workers=10)

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "monitoring": {
                "update_interval": 1.0,  # 更新間隔（秒）
                "max_price_history": 1000,  # 最大価格履歴数
                "max_alert_history": 10000,  # 最大アラート履歴数
                "lookback_period": 20,  # テクニカル分析期間
            },
            "alerts": {
                "price_change_threshold": 0.05,  # 価格変動閾値5%
                "volume_spike_threshold": 2.0,  # 出来高急増閾値2倍
                "volatility_threshold": 0.30,  # ボラティリティ閾値30%
                "breakout_threshold": 0.02,  # ブレイクアウト閾値2%
                "trend_change_threshold": 0.03,  # トレンド変化閾値3%
            },
            "technical_analysis": {
                "moving_average_periods": [5, 10, 20],
                "support_resistance_period": 20,
                "volatility_period": 20,
                "trend_detection_period": 20,
            },
        }

    def start_monitoring(self, symbols: List[str], update_interval: float = None):
        """監視開始"""
        try:
            if self.is_monitoring:
                self.logger.warning("監視は既に開始されています")
                return

            interval = update_interval or self.config["monitoring"]["update_interval"]

            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop, args=(interval,), daemon=True
            )
            self.monitor_thread.start()

            self.logger.info(f"リアルタイム価格監視を開始: {symbols}")

        except Exception as e:
            self.logger.error(f"監視開始エラー: {e}")
            self.is_monitoring = False

    def stop_monitoring(self):
        """監視停止"""
        try:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5.0)

            self.logger.info("リアルタイム価格監視を停止")

        except Exception as e:
            self.logger.error(f"監視停止エラー: {e}")

    def update_price_data(self, symbol: str, price_data: Dict[str, Any]):
        """価格データ更新"""
        try:
            # 価格データ作成
            price = PriceData(
                symbol=symbol,
                price=price_data["price"],
                high=price_data.get("high", price_data["price"]),
                low=price_data.get("low", price_data["price"]),
                volume=price_data.get("volume", 0),
                timestamp=datetime.now(),
                change=price_data.get("change", 0.0),
                change_percent=price_data.get("change_percent", 0.0),
            )

            # 価格データ保存
            if symbol not in self.price_data:
                self.price_data[symbol] = []

            self.price_data[symbol].append(price)

            # 履歴制限
            max_history = self.config["monitoring"]["max_price_history"]
            if len(self.price_data[symbol]) > max_history:
                self.price_data[symbol] = self.price_data[symbol][-max_history:]

            # 価格キューに追加
            self.price_queue.put(
                {"symbol": symbol, "price_data": price, "timestamp": datetime.now()}
            )

        except Exception as e:
            self.logger.error(f"価格データ更新エラー: {e}")

    def check_price_alerts(
        self, symbol: str, price_data: PriceData
    ) -> List[PriceAlert]:
        """価格アラートチェック"""
        try:
            alerts = []

            if symbol not in self.price_data or len(self.price_data[symbol]) < 2:
                return alerts

            # 価格履歴取得
            price_history = self.price_data[symbol]
            prices = [p.price for p in price_history]

            # 価格変動アラート
            if (
                abs(price_data.change_percent)
                > self.config["alerts"]["price_change_threshold"]
            ):
                alert = PriceAlert(
                    timestamp=datetime.now(),
                    symbol=symbol,
                    alert_type=PriceAlertType.PRICE_BREAKOUT,
                    current_price=price_data.price,
                    threshold_price=price_history[-2].price,
                    message=f"大きな価格変動: {price_data.change_percent:.2%}",
                    severity="HIGH"
                    if abs(price_data.change_percent) > 0.1
                    else "MEDIUM",
                    metadata={
                        "change": price_data.change,
                        "change_percent": price_data.change_percent,
                        "volume": price_data.volume,
                    },
                )
                alerts.append(alert)

            # 出来高急増アラート
            if len(price_history) >= 2:
                current_volume = price_data.volume
                previous_volume = price_history[-2].volume

                if (
                    previous_volume > 0
                    and current_volume
                    > previous_volume * self.config["alerts"]["volume_spike_threshold"]
                ):
                    alert = PriceAlert(
                        timestamp=datetime.now(),
                        symbol=symbol,
                        alert_type=PriceAlertType.VOLUME_SPIKE,
                        current_price=price_data.price,
                        threshold_price=price_history[-2].price,
                        message=f"出来高急増: {current_volume:,} (前回: {previous_volume:,})",
                        severity="HIGH",
                        metadata={
                            "current_volume": current_volume,
                            "previous_volume": previous_volume,
                            "volume_ratio": current_volume / previous_volume,
                        },
                    )
                    alerts.append(alert)

            # ボラティリティアラート
            if len(prices) >= 20:
                volatility = self.technical_analyzer.calculate_volatility(prices)
                if volatility > self.config["alerts"]["volatility_threshold"]:
                    alert = PriceAlert(
                        timestamp=datetime.now(),
                        symbol=symbol,
                        alert_type=PriceAlertType.VOLATILITY_SPIKE,
                        current_price=price_data.price,
                        threshold_price=price_history[-2].price,
                        message=f"高ボラティリティ: {volatility:.2%}",
                        severity="HIGH",
                        metadata={
                            "volatility": volatility,
                            "volatility_threshold": self.config["alerts"][
                                "volatility_threshold"
                            ],
                        },
                    )
                    alerts.append(alert)

            # ブレイクアウトアラート
            if len(prices) >= 20:
                support_resistance = (
                    self.technical_analyzer.calculate_support_resistance(prices)
                )
                if support_resistance:
                    breakout = self.technical_analyzer.detect_breakout(
                        prices,
                        support_resistance.get("support_level", 0),
                        support_resistance.get("resistance_level", 0),
                    )

                    if breakout["upward_breakout"]:
                        alert = PriceAlert(
                            timestamp=datetime.now(),
                            symbol=symbol,
                            alert_type=PriceAlertType.PRICE_BREAKOUT,
                            current_price=price_data.price,
                            threshold_price=support_resistance.get(
                                "resistance_level", 0
                            ),
                            message=f"上向きブレイクアウト: {price_data.price:.2f} > {support_resistance.get('resistance_level', 0):.2f}",
                            severity="HIGH",
                            metadata={
                                "breakout_type": "upward",
                                "resistance_level": support_resistance.get(
                                    "resistance_level", 0
                                ),
                                "support_level": support_resistance.get(
                                    "support_level", 0
                                ),
                            },
                        )
                        alerts.append(alert)

                    elif breakout["downward_breakout"]:
                        alert = PriceAlert(
                            timestamp=datetime.now(),
                            symbol=symbol,
                            alert_type=PriceAlertType.PRICE_BREAKOUT,
                            current_price=price_data.price,
                            threshold_price=support_resistance.get("support_level", 0),
                            message=f"下向きブレイクアウト: {price_data.price:.2f} < {support_resistance.get('support_level', 0):.2f}",
                            severity="HIGH",
                            metadata={
                                "breakout_type": "downward",
                                "resistance_level": support_resistance.get(
                                    "resistance_level", 0
                                ),
                                "support_level": support_resistance.get(
                                    "support_level", 0
                                ),
                            },
                        )
                        alerts.append(alert)

            # トレンド変化アラート
            if len(prices) >= 20:
                current_trend = self.technical_analyzer.detect_trend(prices)
                if len(prices) >= 40:
                    previous_trend = self.technical_analyzer.detect_trend(prices[:-20])

                    if current_trend != previous_trend:
                        alert = PriceAlert(
                            timestamp=datetime.now(),
                            symbol=symbol,
                            alert_type=PriceAlertType.TREND_CHANGE,
                            current_price=price_data.price,
                            threshold_price=price_history[-2].price,
                            message=f"トレンド変化: {previous_trend} → {current_trend}",
                            severity="MEDIUM",
                            metadata={
                                "previous_trend": previous_trend,
                                "current_trend": current_trend,
                                "trend_change": True,
                            },
                        )
                        alerts.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"価格アラートチェックエラー: {e}")
            return []

    def create_market_snapshot(
        self, symbol: str, price_data: PriceData
    ) -> MarketSnapshot:
        """市場スナップショット作成"""
        try:
            if symbol not in self.price_data or len(self.price_data[symbol]) < 20:
                return None

            price_history = self.price_data[symbol]
            prices = [p.price for p in price_history]

            # テクニカル指標計算
            moving_averages = self.technical_analyzer.calculate_moving_averages(prices)
            support_resistance = self.technical_analyzer.calculate_support_resistance(
                prices
            )
            volatility = self.technical_analyzer.calculate_volatility(prices)
            trend_direction = self.technical_analyzer.detect_trend(prices)

            # 市場状況判定
            market_condition = self._determine_market_condition(
                volatility, trend_direction
            )

            # アラート取得
            alerts = self.check_price_alerts(symbol, price_data)

            # テクニカル指標統合
            technical_indicators = {
                **moving_averages,
                **support_resistance,
                "volatility": volatility,
                "trend_direction": trend_direction,
            }

            snapshot = MarketSnapshot(
                timestamp=datetime.now(),
                symbol=symbol,
                current_price=price_data.price,
                market_condition=market_condition,
                volatility=volatility,
                trend_direction=trend_direction,
                support_level=support_resistance.get("support_level", 0),
                resistance_level=support_resistance.get("resistance_level", 0),
                alerts=alerts,
                technical_indicators=technical_indicators,
            )

            return snapshot

        except Exception as e:
            self.logger.error(f"市場スナップショット作成エラー: {e}")
            return None

    def _determine_market_condition(
        self, volatility: float, trend_direction: str
    ) -> MarketCondition:
        """市場状況判定"""
        try:
            if volatility > 0.3:
                return MarketCondition.HIGH_VOLATILITY
            elif volatility < 0.1:
                return MarketCondition.LOW_VOLATILITY
            elif trend_direction == "uptrend":
                return MarketCondition.TRENDING_UP
            elif trend_direction == "downtrend":
                return MarketCondition.TRENDING_DOWN
            else:
                return MarketCondition.SIDEWAYS

        except Exception as e:
            self.logger.error(f"市場状況判定エラー: {e}")
            return MarketCondition.NORMAL

    def _monitoring_loop(self, update_interval: float):
        """監視ループ"""
        while self.is_monitoring:
            try:
                # 価格キューから処理
                while not self.price_queue.empty():
                    try:
                        price_update = self.price_queue.get_nowait()
                        self._process_price_update(price_update)
                    except Empty:
                        break

                # アラートキューから処理
                while not self.alert_queue.empty():
                    try:
                        alert = self.alert_queue.get_nowait()
                        self._process_alert(alert)
                    except Empty:
                        break

                time.sleep(update_interval)

            except Exception as e:
                self.logger.error(f"監視ループエラー: {e}")
                time.sleep(update_interval)

    def _process_price_update(self, price_update: Dict[str, Any]):
        """価格更新処理"""
        try:
            symbol = price_update["symbol"]
            price_data = price_update["price_data"]

            # 市場スナップショット作成
            snapshot = self.create_market_snapshot(symbol, price_data)
            if snapshot:
                self.market_snapshots[symbol] = snapshot

                # アラート処理
                for alert in snapshot.alerts:
                    self._process_alert(alert)

            # コールバック実行
            for callback in self.price_callbacks:
                try:
                    callback(price_update)
                except Exception as e:
                    self.logger.error(f"価格コールバックエラー: {e}")

        except Exception as e:
            self.logger.error(f"価格更新処理エラー: {e}")

    def _process_alert(self, alert: PriceAlert):
        """アラート処理"""
        try:
            # アラート履歴に追加
            self.alert_history.append(alert)
            if len(self.alert_history) > self.config["monitoring"]["max_alert_history"]:
                self.alert_history.pop(0)

            # アクティブアラート管理
            if alert.symbol not in self.active_alerts:
                self.active_alerts[alert.symbol] = []

            self.active_alerts[alert.symbol].append(alert)

            # コールバック実行
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"アラートコールバックエラー: {e}")

            self.logger.info(
                f"アラート処理: {alert.symbol}, {alert.alert_type}, {alert.message}"
            )

        except Exception as e:
            self.logger.error(f"アラート処理エラー: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """監視状況取得"""
        try:
            total_alerts = len(self.alert_history)
            critical_alerts = len(
                [a for a in self.alert_history if a.severity == "HIGH"]
            )

            return {
                "status": "monitoring" if self.is_monitoring else "stopped",
                "monitored_symbols": list(self.price_data.keys()),
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "active_alerts": {
                    symbol: len(alerts) for symbol, alerts in self.active_alerts.items()
                },
                "last_update": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"監視状況取得エラー: {e}")
            return {"status": "error", "error": str(e)}

    def get_market_analysis(self, symbol: str) -> Dict[str, Any]:
        """市場分析取得"""
        try:
            if symbol not in self.market_snapshots:
                return {"status": "no_data"}

            snapshot = self.market_snapshots[symbol]

            return {
                "symbol": symbol,
                "current_price": snapshot.current_price,
                "market_condition": snapshot.market_condition.value,
                "volatility": snapshot.volatility,
                "trend_direction": snapshot.trend_direction,
                "support_level": snapshot.support_level,
                "resistance_level": snapshot.resistance_level,
                "technical_indicators": snapshot.technical_indicators,
                "active_alerts": len(snapshot.alerts),
                "last_update": snapshot.timestamp.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"市場分析取得エラー: {e}")
            return {"status": "error", "error": str(e)}

    def add_price_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """価格コールバック追加"""
        self.price_callbacks.append(callback)

    def add_alert_callback(self, callback: Callable[[PriceAlert], None]):
        """アラートコールバック追加"""
        self.alert_callbacks.append(callback)

    def export_alert_report(self, symbol: str = None, days: int = 7) -> Dict[str, Any]:
        """アラートレポート出力"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            if symbol:
                recent_alerts = [
                    a
                    for a in self.alert_history
                    if a.symbol == symbol and a.timestamp >= cutoff_date
                ]
            else:
                recent_alerts = [
                    a for a in self.alert_history if a.timestamp >= cutoff_date
                ]

            # アラート統計
            alert_counts = {}
            severity_counts = {}

            for alert in recent_alerts:
                alert_type = alert.alert_type.value
                severity = alert.severity

                alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            return {
                "report_period": f"{days} days",
                "symbol": symbol or "all",
                "total_alerts": len(recent_alerts),
                "alert_counts": alert_counts,
                "severity_counts": severity_counts,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"アラートレポート出力エラー: {e}")
            return {"error": str(e)}
