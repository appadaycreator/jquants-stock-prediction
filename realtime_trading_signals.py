#!/usr/bin/env python3
"""
リアルタイム売買シグナル生成システム
最高優先度機能: 月間5-15%の利益向上を目指す

機能:
1. リアルタイム株価データ取得
2. 技術指標による売買シグナル生成
3. リスク管理・損切りシステム
4. 複数銘柄同時監視
5. シグナル強度の評価
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
from dataclasses import dataclass
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("trading_signals.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """売買シグナルの種類"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


class SignalStrength(Enum):
    """シグナル強度"""

    WEAK = 1
    MEDIUM = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class TradingSignal:
    """売買シグナルデータクラス"""

    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    price: float
    confidence: float
    timestamp: datetime
    indicators: Dict[str, float]
    reason: str
    risk_level: str


class TechnicalIndicators:
    """技術指標計算クラス"""

    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """単純移動平均"""
        return data.rolling(window=window).mean()

    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """指数移動平均"""
        return data.ewm(span=window).mean()

    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """RSI（相対力指数）"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(
        data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(
        data: pd.Series, window: int = 20, std_dev: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """ボリンジャーバンド"""
        sma = TechnicalIndicators.sma(data, window)
        std = data.rolling(window=window).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    @staticmethod
    def stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_window: int = 14,
        d_window: int = 3,
    ) -> Tuple[pd.Series, pd.Series]:
        """ストキャスティクス"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        return k_percent, d_percent


class SignalGenerator:
    """売買シグナル生成クラス"""

    def __init__(self):
        self.indicators = TechnicalIndicators()

    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[TradingSignal]:
        """売買シグナルを生成"""
        signals = []

        if len(data) < 50:  # 十分なデータがない場合
            return signals

        # 技術指標を計算
        close = data["Close"]
        high = data["High"]
        low = data["Low"]
        volume = data["Volume"]

        # 移動平均
        sma_20 = self.indicators.sma(close, 20)
        sma_50 = self.indicators.sma(close, 50)
        ema_12 = self.indicators.ema(close, 12)
        ema_26 = self.indicators.ema(close, 26)

        # 技術指標
        rsi = self.indicators.rsi(close)
        macd, macd_signal, macd_hist = self.indicators.macd(close)
        bb_upper, bb_middle, bb_lower = self.indicators.bollinger_bands(close)
        stoch_k, stoch_d = self.indicators.stochastic(high, low, close)

        # 最新の値
        current_price = close.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_macd_signal = macd_signal.iloc[-1]
        current_macd_hist = macd_hist.iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        current_stoch_k = stoch_k.iloc[-1]
        current_stoch_d = stoch_d.iloc[-1]

        # シグナル生成ロジック
        signal_data = {
            "rsi": current_rsi,
            "macd": current_macd,
            "macd_signal": current_macd_signal,
            "macd_hist": current_macd_hist,
            "bb_upper": current_bb_upper,
            "bb_lower": current_bb_lower,
            "stoch_k": current_stoch_k,
            "stoch_d": current_stoch_d,
            "sma_20": sma_20.iloc[-1],
            "sma_50": sma_50.iloc[-1],
        }

        # 複数のシグナルを組み合わせて総合判断
        buy_signals = 0
        sell_signals = 0
        reasons = []

        # RSIシグナル
        if current_rsi < 30:
            buy_signals += 2
            reasons.append("RSI過小売り")
        elif current_rsi > 70:
            sell_signals += 2
            reasons.append("RSI過大買い")

        # MACDシグナル
        if current_macd > current_macd_signal and current_macd_hist > 0:
            buy_signals += 1
            reasons.append("MACD上昇")
        elif current_macd < current_macd_signal and current_macd_hist < 0:
            sell_signals += 1
            reasons.append("MACD下降")

        # ボリンジャーバンドシグナル
        if current_price <= current_bb_lower:
            buy_signals += 1
            reasons.append("ボリンジャーバンド下限")
        elif current_price >= current_bb_upper:
            sell_signals += 1
            reasons.append("ボリンジャーバンド上限")

        # ストキャスティクスシグナル
        if current_stoch_k < 20 and current_stoch_d < 20:
            buy_signals += 1
            reasons.append("ストキャスティクス過小売り")
        elif current_stoch_k > 80 and current_stoch_d > 80:
            sell_signals += 1
            reasons.append("ストキャスティクス過大買い")

        # 移動平均シグナル
        if current_price > sma_20.iloc[-1] > sma_50.iloc[-1]:
            buy_signals += 1
            reasons.append("上昇トレンド")
        elif current_price < sma_20.iloc[-1] < sma_50.iloc[-1]:
            sell_signals += 1
            reasons.append("下降トレンド")

        # 総合判断
        signal_diff = buy_signals - sell_signals

        if signal_diff >= 3:
            signal_type = SignalType.STRONG_BUY
            strength = SignalStrength.VERY_STRONG
            confidence = min(0.95, 0.6 + (signal_diff - 3) * 0.1)
        elif signal_diff >= 2:
            signal_type = SignalType.BUY
            strength = SignalStrength.STRONG
            confidence = min(0.9, 0.5 + signal_diff * 0.1)
        elif signal_diff >= 1:
            signal_type = SignalType.BUY
            strength = SignalStrength.MEDIUM
            confidence = 0.4 + signal_diff * 0.1
        elif signal_diff <= -3:
            signal_type = SignalType.STRONG_SELL
            strength = SignalStrength.VERY_STRONG
            confidence = min(0.95, 0.6 + abs(signal_diff - 3) * 0.1)
        elif signal_diff <= -2:
            signal_type = SignalType.SELL
            strength = SignalStrength.STRONG
            confidence = min(0.9, 0.5 + abs(signal_diff) * 0.1)
        elif signal_diff <= -1:
            signal_type = SignalType.SELL
            strength = SignalStrength.MEDIUM
            confidence = 0.4 + abs(signal_diff) * 0.1
        else:
            signal_type = SignalType.HOLD
            strength = SignalStrength.WEAK
            confidence = 0.3

        # リスクレベル判定
        if confidence >= 0.8:
            risk_level = "LOW"
        elif confidence >= 0.6:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        signal = TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            price=current_price,
            confidence=confidence,
            timestamp=datetime.now(),
            indicators=signal_data,
            reason="; ".join(reasons) if reasons else "シグナルなし",
            risk_level=risk_level,
        )

        signals.append(signal)
        return signals


class RiskManager:
    """リスク管理クラス"""

    def __init__(self, max_loss_percent: float = 5.0, max_position_size: float = 0.1):
        self.max_loss_percent = max_loss_percent
        self.max_position_size = max_position_size
        self.positions = {}

    def calculate_position_size(
        self, account_value: float, signal: TradingSignal
    ) -> float:
        """ポジションサイズを計算"""
        base_size = account_value * self.max_position_size

        # 信頼度に基づく調整
        confidence_multiplier = signal.confidence

        # リスクレベルに基づく調整
        if signal.risk_level == "LOW":
            risk_multiplier = 1.0
        elif signal.risk_level == "MEDIUM":
            risk_multiplier = 0.7
        else:
            risk_multiplier = 0.4

        position_size = base_size * confidence_multiplier * risk_multiplier
        return min(position_size, account_value * 0.2)  # 最大20%まで

    def should_stop_loss(
        self, entry_price: float, current_price: float, signal: TradingSignal
    ) -> bool:
        """損切り判定"""
        loss_percent = ((current_price - entry_price) / entry_price) * 100
        return loss_percent <= -self.max_loss_percent

    def should_take_profit(
        self, entry_price: float, current_price: float, signal: TradingSignal
    ) -> bool:
        """利確判定"""
        profit_percent = ((current_price - entry_price) / entry_price) * 100

        # 信頼度に基づく利確目標
        if signal.confidence >= 0.8:
            target_profit = 10.0
        elif signal.confidence >= 0.6:
            target_profit = 7.0
        else:
            target_profit = 5.0

        return profit_percent >= target_profit


class MultiStockMonitor:
    """複数銘柄同時監視クラス"""

    def __init__(
        self,
        symbols: List[str],
        signal_generator: SignalGenerator,
        risk_manager: RiskManager,
    ):
        self.symbols = symbols
        self.signal_generator = signal_generator
        self.risk_manager = risk_manager
        self.monitoring_data = {}

    def fetch_stock_data(
        self, symbol: str, period: str = "1mo"
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

    def monitor_all_stocks(self) -> Dict[str, List[TradingSignal]]:
        """全銘柄を監視してシグナルを生成"""
        all_signals = {}

        for symbol in self.symbols:
            try:
                logger.info(f"監視中: {symbol}")
                data = self.fetch_stock_data(symbol)

                if data is not None:
                    signals = self.signal_generator.generate_signals(data, symbol)
                    all_signals[symbol] = signals

                    if signals:
                        signal = signals[0]
                        logger.info(
                            f"{symbol}: {signal.signal_type.value} (信頼度: {signal.confidence:.2f})"
                        )
                else:
                    all_signals[symbol] = []

            except Exception as e:
                logger.error(f"監視エラー {symbol}: {e}")
                all_signals[symbol] = []

        return all_signals

    def get_top_signals(
        self, all_signals: Dict[str, List[TradingSignal]], limit: int = 5
    ) -> List[TradingSignal]:
        """上位シグナルを取得"""
        all_signals_list = []
        for symbol, signals in all_signals.items():
            all_signals_list.extend(signals)

        # 信頼度でソート
        sorted_signals = sorted(
            all_signals_list, key=lambda x: x.confidence, reverse=True
        )
        return sorted_signals[:limit]


class TradingSignalSystem:
    """統合売買シグナルシステム"""

    def __init__(self, symbols: List[str], account_value: float = 1000000):
        self.symbols = symbols
        self.account_value = account_value
        self.signal_generator = SignalGenerator()
        self.risk_manager = RiskManager()
        self.monitor = MultiStockMonitor(
            symbols, self.signal_generator, self.risk_manager
        )

    def run_analysis(self) -> Dict:
        """分析を実行して結果を返す"""
        logger.info("=== リアルタイム売買シグナル分析開始 ===")

        # 全銘柄の監視
        all_signals = self.monitor.monitor_all_stocks()

        # 上位シグナルの取得
        top_signals = self.monitor.get_top_signals(all_signals, limit=10)

        # 結果の整理
        results = {
            "timestamp": datetime.now().isoformat(),
            "account_value": self.account_value,
            "total_symbols": len(self.symbols),
            "signals_generated": sum(len(signals) for signals in all_signals.values()),
            "top_signals": [],
            "summary": {
                "buy_signals": 0,
                "sell_signals": 0,
                "hold_signals": 0,
                "strong_buy_signals": 0,
                "strong_sell_signals": 0,
            },
        }

        for signal in top_signals:
            signal_data = {
                "symbol": signal.symbol,
                "signal_type": signal.signal_type.value,
                "strength": signal.strength.value,
                "price": signal.price,
                "confidence": signal.confidence,
                "risk_level": signal.risk_level,
                "reason": signal.reason,
                "indicators": signal.indicators,
                "position_size": self.risk_manager.calculate_position_size(
                    self.account_value, signal
                ),
            }
            results["top_signals"].append(signal_data)

            # サマリー更新
            if signal.signal_type == SignalType.BUY:
                results["summary"]["buy_signals"] += 1
            elif signal.signal_type == SignalType.SELL:
                results["summary"]["sell_signals"] += 1
            elif signal.signal_type == SignalType.STRONG_BUY:
                results["summary"]["strong_buy_signals"] += 1
            elif signal.signal_type == SignalType.STRONG_SELL:
                results["summary"]["strong_sell_signals"] += 1
            else:
                results["summary"]["hold_signals"] += 1

        logger.info("=== 分析完了 ===")
        logger.info(f"生成されたシグナル数: {results['signals_generated']}")
        logger.info(
            f"買いシグナル: {results['summary']['buy_signals'] + results['summary']['strong_buy_signals']}"
        )
        logger.info(
            f"売りシグナル: {results['summary']['sell_signals'] + results['summary']['strong_sell_signals']}"
        )

        return results

    def save_results(
        self, results: Dict, filename: str = "trading_signals_results.json"
    ):
        """結果をJSONファイルに保存"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"結果を保存しました: {filename}")
        except Exception as e:
            logger.error(f"保存エラー: {e}")


def main():
    """メイン実行関数"""
    # 監視対象銘柄（例：主要日本株）
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

    # システム初期化
    trading_system = TradingSignalSystem(symbols, account_value=1000000)

    # 分析実行
    results = trading_system.run_analysis()

    # 結果保存
    trading_system.save_results(results)

    # 結果表示
    print("\n" + "=" * 80)
    print("🎯 リアルタイム売買シグナル分析結果")
    print("=" * 80)
    print(f"分析時刻: {results['timestamp']}")
    print(f"監視銘柄数: {results['total_symbols']}")
    print(f"生成シグナル数: {results['signals_generated']}")
    print(f"口座価値: ¥{results['account_value']:,}")

    print("\n📊 シグナルサマリー:")
    summary = results["summary"]
    print(f"  強気買い: {summary['strong_buy_signals']}")
    print(f"  買い: {summary['buy_signals']}")
    print(f"  売り: {summary['sell_signals']}")
    print(f"  強気売り: {summary['strong_sell_signals']}")
    print(f"  ホールド: {summary['hold_signals']}")

    print("\n🏆 上位シグナル:")
    for i, signal in enumerate(results["top_signals"][:5], 1):
        print(
            f"  {i}. {signal['symbol']} - {signal['signal_type']} "
            f"(信頼度: {signal['confidence']:.2f}, リスク: {signal['risk_level']})"
        )
        print(
            f"     価格: ¥{signal['price']:.2f}, 推奨ポジション: ¥{signal['position_size']:,.0f}"
        )
        print(f"     理由: {signal['reason']}")
        print()


if __name__ == "__main__":
    main()
