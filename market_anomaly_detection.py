#!/usr/bin/env python3
"""
市場異常検知システム
リアルタイム自動売買システムの追加推奨機能

期待効果: 損失30-50%削減
実装難易度: 🟡 Medium
推定工数: 2-3日

主要機能:
1. 異常価格変動の検知
2. 市場クラッシュ予測
3. 緊急停止機能
4. アラート通知
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import threading
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("market_anomaly.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """異常タイプ"""

    PRICE_SPIKE = "price_spike"  # 価格急騰
    PRICE_CRASH = "price_crash"  # 価格急落
    VOLUME_SPIKE = "volume_spike"  # 出来高急増
    VOLATILITY_SPIKE = "volatility_spike"  # ボラティリティ急上昇
    CORRELATION_BREAK = "correlation_break"  # 相関関係の崩壊
    MARKET_CRASH = "market_crash"  # 市場クラッシュ
    FLASH_CRASH = "flash_crash"  # フラッシュクラッシュ
    UNUSUAL_PATTERN = "unusual_pattern"  # 異常パターン


class AlertLevel(Enum):
    """アラートレベル"""

    INFO = "info"  # 情報
    WARNING = "warning"  # 警告
    CRITICAL = "critical"  # 緊急
    EMERGENCY = "emergency"  # 非常事態


@dataclass
class AnomalyDetection:
    """異常検知結果"""

    anomaly_id: str
    symbol: str
    anomaly_type: AnomalyType
    alert_level: AlertLevel
    severity_score: float  # 0-1
    description: str
    detected_at: datetime
    confidence: float
    affected_symbols: List[str]
    recommended_action: str
    technical_details: Dict


@dataclass
class MarketCondition:
    """市場状況"""

    timestamp: datetime
    overall_volatility: float
    market_stress_index: float
    correlation_breakdown: bool
    liquidity_condition: str
    risk_level: AlertLevel


class PriceAnomalyDetector:
    """価格異常検知器"""

    def __init__(self, lookback_period: int = 100):
        self.lookback_period = lookback_period
        self.price_history = {}
        self.volatility_history = {}

    def detect_price_anomalies(
        self, symbol: str, current_price: float, volume: int = None
    ) -> List[AnomalyDetection]:
        """価格異常を検知"""
        anomalies = []

        # 価格履歴を更新
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(
            {"price": current_price, "volume": volume or 0, "timestamp": datetime.now()}
        )

        # 履歴を制限
        if len(self.price_history[symbol]) > self.lookback_period:
            self.price_history[symbol] = self.price_history[symbol][
                -self.lookback_period :
            ]

        history = self.price_history[symbol]
        if len(history) < 20:  # 十分なデータがない場合はスキップ
            return anomalies

        # 価格変化率を計算
        prices = [h["price"] for h in history]
        returns = np.diff(prices) / prices[:-1]

        # 異常検知アルゴリズム
        anomalies.extend(self._detect_price_spikes(symbol, prices, returns))
        anomalies.extend(self._detect_volume_anomalies(symbol, history))
        anomalies.extend(self._detect_volatility_anomalies(symbol, returns))

        return anomalies

    def _detect_price_spikes(
        self, symbol: str, prices: List[float], returns: np.ndarray
    ) -> List[AnomalyDetection]:
        """価格スパイクを検知"""
        anomalies = []

        if len(returns) < 10:
            return anomalies

        # 統計的異常検知
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        # 最新のリターン
        latest_return = returns[-1]
        z_score = abs(latest_return - mean_return) / std_return if std_return > 0 else 0

        # 閾値設定
        spike_threshold = 3.0  # 3σ
        crash_threshold = -3.0

        if z_score > spike_threshold:
            if latest_return > 0:
                anomaly_type = AnomalyType.PRICE_SPIKE
                alert_level = (
                    AlertLevel.WARNING if z_score < 5.0 else AlertLevel.CRITICAL
                )
                description = f"価格急騰検知: {latest_return*100:.2f}%"
            else:
                anomaly_type = AnomalyType.PRICE_CRASH
                alert_level = (
                    AlertLevel.CRITICAL if z_score > 5.0 else AlertLevel.WARNING
                )
                description = f"価格急落検知: {latest_return*100:.2f}%"

            severity_score = min(1.0, z_score / 10.0)

            anomaly = AnomalyDetection(
                anomaly_id=f"price_{symbol}_{int(time.time())}",
                symbol=symbol,
                anomaly_type=anomaly_type,
                alert_level=alert_level,
                severity_score=severity_score,
                description=description,
                detected_at=datetime.now(),
                confidence=min(0.95, z_score / 5.0),
                affected_symbols=[symbol],
                recommended_action="ポジション確認とリスク管理の実行",
                technical_details={
                    "z_score": z_score,
                    "return": latest_return,
                    "mean_return": mean_return,
                    "std_return": std_return,
                },
            )
            anomalies.append(anomaly)

        return anomalies

    def _detect_volume_anomalies(
        self, symbol: str, history: List[Dict]
    ) -> List[AnomalyDetection]:
        """出来高異常を検知"""
        anomalies = []

        if len(history) < 20:
            return anomalies

        volumes = [h["volume"] for h in history if h["volume"] > 0]
        if len(volumes) < 10:
            return anomalies

        # 出来高の統計
        mean_volume = np.mean(volumes)
        std_volume = np.std(volumes)
        latest_volume = volumes[-1]

        # 出来高スパイク検知
        if std_volume > 0:
            volume_z_score = (latest_volume - mean_volume) / std_volume

            if volume_z_score > 3.0:  # 3σ以上
                severity_score = min(1.0, volume_z_score / 5.0)

                anomaly = AnomalyDetection(
                    anomaly_id=f"volume_{symbol}_{int(time.time())}",
                    symbol=symbol,
                    anomaly_type=AnomalyType.VOLUME_SPIKE,
                    alert_level=AlertLevel.WARNING,
                    severity_score=severity_score,
                    description=f"出来高急増検知: {latest_volume:,.0f} (平均: {mean_volume:,.0f})",
                    detected_at=datetime.now(),
                    confidence=min(0.9, volume_z_score / 4.0),
                    affected_symbols=[symbol],
                    recommended_action="市場の異常な動きを監視",
                    technical_details={
                        "volume_z_score": volume_z_score,
                        "latest_volume": latest_volume,
                        "mean_volume": mean_volume,
                        "std_volume": std_volume,
                    },
                )
                anomalies.append(anomaly)

        return anomalies

    def _detect_volatility_anomalies(
        self, symbol: str, returns: np.ndarray
    ) -> List[AnomalyDetection]:
        """ボラティリティ異常を検知"""
        anomalies = []

        if len(returns) < 30:
            return anomalies

        # ローリングボラティリティを計算
        window = 20
        rolling_vol = []
        for i in range(window, len(returns)):
            vol = np.std(returns[i - window : i])
            rolling_vol.append(vol)

        if len(rolling_vol) < 10:
            return anomalies

        # ボラティリティの異常検知
        mean_vol = np.mean(rolling_vol)
        std_vol = np.std(rolling_vol)
        latest_vol = rolling_vol[-1]

        if std_vol > 0:
            vol_z_score = (latest_vol - mean_vol) / std_vol

            if vol_z_score > 2.5:  # 2.5σ以上
                severity_score = min(1.0, vol_z_score / 4.0)

                anomaly = AnomalyDetection(
                    anomaly_id=f"volatility_{symbol}_{int(time.time())}",
                    symbol=symbol,
                    anomaly_type=AnomalyType.VOLATILITY_SPIKE,
                    alert_level=AlertLevel.WARNING,
                    severity_score=severity_score,
                    description=f"ボラティリティ急上昇: {latest_vol:.4f} (平均: {mean_vol:.4f})",
                    detected_at=datetime.now(),
                    confidence=min(0.85, vol_z_score / 3.0),
                    affected_symbols=[symbol],
                    recommended_action="リスク管理の強化とポジションサイズの縮小",
                    technical_details={
                        "volatility_z_score": vol_z_score,
                        "latest_volatility": latest_vol,
                        "mean_volatility": mean_vol,
                        "std_volatility": std_vol,
                    },
                )
                anomalies.append(anomaly)

        return anomalies


class MarketCrashDetector:
    """市場クラッシュ検知器"""

    def __init__(self):
        self.correlation_matrix = {}
        self.market_stress_indicators = {}
        self.crash_thresholds = {
            "market_decline": -0.05,  # 5%下落
            "volume_spike": 3.0,  # 3σ出来高増加
            "volatility_spike": 2.5,  # 2.5σボラティリティ増加
            "correlation_break": 0.3,  # 相関係数0.3以下
        }

    def detect_market_crash(
        self, market_data: Dict[str, Dict]
    ) -> List[AnomalyDetection]:
        """市場クラッシュを検知"""
        anomalies = []

        if len(market_data) < 3:
            return anomalies

        # 市場全体の状況を分析
        market_condition = self._analyze_market_condition(market_data)

        # クラッシュ指標をチェック
        crash_indicators = self._check_crash_indicators(market_data, market_condition)

        for indicator in crash_indicators:
            if indicator["severity"] > 0.7:  # 高リスク
                anomaly = AnomalyDetection(
                    anomaly_id=f"market_crash_{int(time.time())}",
                    symbol="MARKET",
                    anomaly_type=AnomalyType.MARKET_CRASH,
                    alert_level=AlertLevel.EMERGENCY,
                    severity_score=indicator["severity"],
                    description=f"市場クラッシュ検知: {indicator['description']}",
                    detected_at=datetime.now(),
                    confidence=indicator["confidence"],
                    affected_symbols=list(market_data.keys()),
                    recommended_action="緊急停止とリスク管理の実行",
                    technical_details=indicator["details"],
                )
                anomalies.append(anomaly)

        return anomalies

    def _analyze_market_condition(
        self, market_data: Dict[str, Dict]
    ) -> MarketCondition:
        """市場状況を分析"""
        symbols = list(market_data.keys())

        # 全体ボラティリティを計算
        volatilities = []
        for symbol, data in market_data.items():
            if "volatility" in data:
                volatilities.append(data["volatility"])

        overall_volatility = np.mean(volatilities) if volatilities else 0.0

        # 市場ストレス指数を計算
        stress_indicators = []
        for symbol, data in market_data.items():
            if "price_change" in data:
                stress_indicators.append(abs(data["price_change"]))

        market_stress_index = np.mean(stress_indicators) if stress_indicators else 0.0

        # 相関関係の崩壊をチェック
        correlation_breakdown = self._check_correlation_breakdown(market_data)

        # リスクレベルを決定
        if market_stress_index > 0.1 or overall_volatility > 0.05:
            risk_level = AlertLevel.CRITICAL
        elif market_stress_index > 0.05 or overall_volatility > 0.03:
            risk_level = AlertLevel.WARNING
        else:
            risk_level = AlertLevel.INFO

        return MarketCondition(
            timestamp=datetime.now(),
            overall_volatility=overall_volatility,
            market_stress_index=market_stress_index,
            correlation_breakdown=correlation_breakdown,
            liquidity_condition="normal",
            risk_level=risk_level,
        )

    def _check_correlation_breakdown(self, market_data: Dict[str, Dict]) -> bool:
        """相関関係の崩壊をチェック"""
        if len(market_data) < 2:
            return False

        # 簡易的な相関チェック
        price_changes = []
        for symbol, data in market_data.items():
            if "price_change" in data:
                price_changes.append(data["price_change"])

        if len(price_changes) < 2:
            return False

        # 価格変化の相関を計算
        correlation_matrix = np.corrcoef(price_changes)

        # 相関が低い場合（0.3以下）を崩壊とみなす
        avg_correlation = np.mean(
            correlation_matrix[np.triu_indices_from(correlation_matrix, k=1)]
        )
        return avg_correlation < 0.3

    def _check_crash_indicators(
        self, market_data: Dict[str, Dict], condition: MarketCondition
    ) -> List[Dict]:
        """クラッシュ指標をチェック"""
        indicators = []

        # 市場下落チェック
        negative_changes = 0
        total_changes = 0

        for symbol, data in market_data.items():
            if "price_change" in data:
                total_changes += 1
                if data["price_change"] < self.crash_thresholds["market_decline"]:
                    negative_changes += 1

        if total_changes > 0:
            decline_ratio = negative_changes / total_changes
            if decline_ratio > 0.5:  # 50%以上の銘柄が5%下落
                indicators.append(
                    {
                        "severity": decline_ratio,
                        "confidence": 0.8,
                        "description": f"市場全体の{decline_ratio*100:.1f}%が大幅下落",
                        "details": {
                            "decline_ratio": decline_ratio,
                            "negative_changes": negative_changes,
                            "total_changes": total_changes,
                        },
                    }
                )

        # ボラティリティスパイクチェック
        if condition.overall_volatility > 0.05:
            indicators.append(
                {
                    "severity": min(1.0, condition.overall_volatility * 10),
                    "confidence": 0.7,
                    "description": f"市場ボラティリティ急上昇: {condition.overall_volatility:.3f}",
                    "details": {
                        "overall_volatility": condition.overall_volatility,
                        "threshold": 0.05,
                    },
                }
            )

        # 相関関係の崩壊チェック
        if condition.correlation_breakdown:
            indicators.append(
                {
                    "severity": 0.8,
                    "confidence": 0.6,
                    "description": "銘柄間相関関係の崩壊",
                    "details": {"correlation_breakdown": True},
                }
            )

        return indicators


class AnomalyAlertSystem:
    """異常アラートシステム"""

    def __init__(self, email_config: Dict = None, webhook_url: str = None):
        self.email_config = email_config
        self.webhook_url = webhook_url
        self.alert_history = []

    def send_alert(self, anomaly: AnomalyDetection):
        """アラートを送信"""
        try:
            # アラート履歴に追加
            self.alert_history.append(anomaly)

            # ログ出力
            logger.warning(
                f"異常検知: {anomaly.anomaly_type.value} - {anomaly.symbol} - {anomaly.description}"
            )

            # メール送信
            if self.email_config and anomaly.alert_level in [
                AlertLevel.CRITICAL,
                AlertLevel.EMERGENCY,
            ]:
                self._send_email_alert(anomaly)

            # Webhook送信
            if self.webhook_url:
                self._send_webhook_alert(anomaly)

        except Exception as e:
            logger.error(f"アラート送信エラー: {e}")

    def _send_email_alert(self, anomaly: AnomalyDetection):
        """メールアラートを送信"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_config["from_email"]
            msg["To"] = self.email_config["to_email"]
            msg["Subject"] = f"市場異常検知アラート - {anomaly.alert_level.value.upper()}"

            body = f"""
市場異常が検知されました。

銘柄: {anomaly.symbol}
異常タイプ: {anomaly.anomaly_type.value}
アラートレベル: {anomaly.alert_level.value}
重要度: {anomaly.severity_score:.2f}
説明: {anomaly.description}
推奨アクション: {anomaly.recommended_action}
検知時刻: {anomaly.detected_at}

技術的詳細:
{json.dumps(anomaly.technical_details, indent=2, ensure_ascii=False)}
            """

            msg.attach(MIMEText(body, "plain", "utf-8"))

            server = smtplib.SMTP(
                self.email_config["smtp_server"], self.email_config["smtp_port"]
            )
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            server.send_message(msg)
            server.quit()

            logger.info(f"メールアラート送信完了: {anomaly.symbol}")

        except Exception as e:
            logger.error(f"メール送信エラー: {e}")

    def _send_webhook_alert(self, anomaly: AnomalyDetection):
        """Webhookアラートを送信"""
        try:
            payload = {
                "anomaly_id": anomaly.anomaly_id,
                "symbol": anomaly.symbol,
                "anomaly_type": anomaly.anomaly_type.value,
                "alert_level": anomaly.alert_level.value,
                "severity_score": anomaly.severity_score,
                "description": anomaly.description,
                "detected_at": anomaly.detected_at.isoformat(),
                "confidence": anomaly.confidence,
                "recommended_action": anomaly.recommended_action,
                "technical_details": anomaly.technical_details,
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Webhookアラート送信完了: {anomaly.symbol}")

        except Exception as e:
            logger.error(f"Webhook送信エラー: {e}")


class MarketAnomalyDetectionSystem:
    """市場異常検知システム"""

    def __init__(
        self, symbols: List[str], email_config: Dict = None, webhook_url: str = None
    ):
        self.symbols = symbols
        self.price_detector = PriceAnomalyDetector()
        self.crash_detector = MarketCrashDetector()
        self.alert_system = AnomalyAlertSystem(email_config, webhook_url)
        self.is_running = False
        self.detection_thread = None
        self.anomaly_history = []

        logger.info(f"市場異常検知システムを初期化しました: {symbols}")

    def start_detection(self):
        """検知を開始"""
        if not self.is_running:
            self.is_running = True
            self.detection_thread = threading.Thread(target=self._detection_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()
            logger.info("市場異常検知を開始しました")

    def stop_detection(self):
        """検知を停止"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join()
        logger.info("市場異常検知を停止しました")

    def _detection_loop(self):
        """検知ループ"""
        while self.is_running:
            try:
                # 市場データを取得（実際の実装ではAPIから取得）
                market_data = self._get_market_data()

                # 個別銘柄の異常検知
                for symbol, data in market_data.items():
                    anomalies = self.price_detector.detect_price_anomalies(
                        symbol, data.get("price", 0), data.get("volume", 0)
                    )

                    for anomaly in anomalies:
                        self._handle_anomaly(anomaly)

                # 市場全体の異常検知
                market_anomalies = self.crash_detector.detect_market_crash(market_data)
                for anomaly in market_anomalies:
                    self._handle_anomaly(anomaly)

                time.sleep(5)  # 5秒間隔でチェック

            except Exception as e:
                logger.error(f"検知ループエラー: {e}")
                time.sleep(10)

    def _get_market_data(self) -> Dict[str, Dict]:
        """市場データを取得（モック実装）"""
        # 実際の実装では、リアルタイムデータAPIから取得
        market_data = {}

        for symbol in self.symbols:
            # モックデータを生成
            base_price = 1000 + hash(symbol) % 5000
            price_change = np.random.normal(0, 0.02)  # 2%の標準偏差
            current_price = base_price * (1 + price_change)
            volume = np.random.randint(1000, 10000)
            volatility = abs(np.random.normal(0, 0.01))

            market_data[symbol] = {
                "price": current_price,
                "volume": volume,
                "price_change": price_change,
                "volatility": volatility,
            }

        return market_data

    def _handle_anomaly(self, anomaly: AnomalyDetection):
        """異常を処理"""
        # 異常履歴に追加
        self.anomaly_history.append(anomaly)

        # アラートを送信
        self.alert_system.send_alert(anomaly)

        # 緊急停止の判定
        if anomaly.alert_level == AlertLevel.EMERGENCY:
            self._trigger_emergency_stop(anomaly)

    def _trigger_emergency_stop(self, anomaly: AnomalyDetection):
        """緊急停止を実行"""
        logger.critical(f"緊急停止実行: {anomaly.description}")

        # 実際の実装では、取引システムに緊急停止を通知
        # 例: trading_system.emergency_stop()

        # 緊急停止の通知
        emergency_alert = AnomalyDetection(
            anomaly_id=f"emergency_stop_{int(time.time())}",
            symbol="SYSTEM",
            anomaly_type=AnomalyType.MARKET_CRASH,
            alert_level=AlertLevel.EMERGENCY,
            severity_score=1.0,
            description="緊急停止が実行されました",
            detected_at=datetime.now(),
            confidence=1.0,
            affected_symbols=self.symbols,
            recommended_action="全取引を停止し、リスク管理を実行",
            technical_details={
                "emergency_stop": True,
                "trigger_anomaly": anomaly.anomaly_id,
            },
        )

        self.alert_system.send_alert(emergency_alert)

    def get_anomaly_summary(self) -> Dict:
        """異常サマリーを取得"""
        recent_anomalies = [
            a
            for a in self.anomaly_history
            if (datetime.now() - a.detected_at).seconds < 3600  # 1時間以内
        ]

        anomaly_counts = {}
        for anomaly in recent_anomalies:
            anomaly_type = anomaly.anomaly_type.value
            anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1

        return {
            "total_anomalies": len(recent_anomalies),
            "anomaly_counts": anomaly_counts,
            "system_running": self.is_running,
            "last_update": datetime.now().isoformat(),
        }


def main():
    """メイン関数（テスト用）"""
    # テスト用の銘柄リスト
    symbols = ["7203", "6758", "9984", "7974", "8306"]

    # 市場異常検知システムを初期化
    anomaly_system = MarketAnomalyDetectionSystem(symbols)

    # 検知を開始
    anomaly_system.start_detection()

    try:
        print("=== 市場異常検知システムテスト ===")
        print("検知システムを開始しました...")

        # 10秒間実行
        time.sleep(10)

        # 異常サマリーを表示
        summary = anomaly_system.get_anomaly_summary()
        print(f"\n=== 異常検知サマリー ===")
        print(f"総異常数: {summary['total_anomalies']}")
        print(f"システム稼働中: {summary['system_running']}")

        if summary["anomaly_counts"]:
            print("\n異常タイプ別カウント:")
            for anomaly_type, count in summary["anomaly_counts"].items():
                print(f"  {anomaly_type}: {count}")

    finally:
        # 検知を停止
        anomaly_system.stop_detection()
        print("\n市場異常検知システムを停止しました")


if __name__ == "__main__":
    main()
