"""
高頻度取引アルゴリズムシステム
High Frequency Trading Algorithm System
"""

import asyncio
import time
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue, Empty

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketData:
    """市場データクラス"""

    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: float
    ask: float
    spread: float


@dataclass
class ArbitrageOpportunity:
    """裁定取引機会クラス"""

    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit: float
    profit_percentage: float
    volume: int
    timestamp: datetime


@dataclass
class Trade:
    """取引クラス"""

    symbol: str
    side: str  # 'buy' or 'sell'
    price: float
    volume: int
    exchange: str
    timestamp: datetime
    order_id: str


class HighFrequencyTrading:
    """高頻度取引アルゴリズムクラス"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初期化

        Args:
            config: 設定辞書
        """
        self.latency_threshold = (
            config.get("latency_threshold", 0.001) if config else 0.001
        )  # 1ms
        self.profit_threshold = (
            config.get("profit_threshold", 0.001) if config else 0.001
        )  # 0.1%
        self.max_position_size = (
            config.get("max_position_size", 1000000) if config else 1000000
        )
        self.risk_limit = config.get("risk_limit", 0.02) if config else 0.02  # 2%

        # 内部状態
        self.positions: Dict[str, float] = {}
        self.pending_orders: Dict[str, Trade] = {}
        self.market_data_queue = Queue()
        self.is_running = False

        # パフォーマンス計測
        self.execution_times: List[float] = []
        self.profit_loss: float = 0.0
        self.total_trades: int = 0

        # スレッドプール
        self.executor = ThreadPoolExecutor(max_workers=4)

        logger.info("高頻度取引システムを初期化しました")

    def execute_arbitrage(
        self, price_differences: Dict[str, Dict[str, float]]
    ) -> List[Trade]:
        """
        裁定取引の実行

        Args:
            price_differences: 価格差データ {symbol: {exchange: price}}

        Returns:
            実行された取引のリスト
        """
        start_time = time.time()

        try:
            # 裁定取引機会を発見
            opportunities = self._find_arbitrage_opportunities(price_differences)

            if not opportunities:
                logger.debug("裁定取引機会が見つかりませんでした")
                return []

            # 取引を実行
            executed_trades = self._execute_trades(opportunities)

            # パフォーマンス計測
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)

            if execution_time > self.latency_threshold:
                logger.warning(
                    f"実行時間が閾値を超過: {execution_time:.4f}s > {self.latency_threshold}s"
                )

            logger.info(
                f"裁定取引を実行: {len(executed_trades)}件, 実行時間: {execution_time:.4f}s"
            )
            return executed_trades

        except Exception as e:
            logger.error(f"裁定取引実行中にエラーが発生: {e}")
            return []

    def _find_arbitrage_opportunities(
        self, price_differences: Dict[str, Dict[str, float]]
    ) -> List[ArbitrageOpportunity]:
        """
        裁定取引機会を発見

        Args:
            price_differences: 価格差データ

        Returns:
            裁定取引機会のリスト
        """
        opportunities = []

        for symbol, exchanges in price_differences.items():
            if len(exchanges) < 2:
                continue

            # 全取引所の組み合わせをチェック
            exchange_list = list(exchanges.items())

            for i in range(len(exchange_list)):
                for j in range(i + 1, len(exchange_list)):
                    exchange1, price1 = exchange_list[i]
                    exchange2, price2 = exchange_list[j]

                    # 価格差を計算
                    if price1 < price2:
                        buy_exchange, buy_price = exchange1, price1
                        sell_exchange, sell_price = exchange2, price2
                    else:
                        buy_exchange, buy_price = exchange2, price2
                        sell_exchange, sell_price = exchange1, price1

                    profit = sell_price - buy_price
                    profit_percentage = profit / buy_price

                    # 利益閾値をチェック
                    if profit_percentage >= self.profit_threshold:
                        opportunity = ArbitrageOpportunity(
                            symbol=symbol,
                            buy_exchange=buy_exchange,
                            sell_exchange=sell_exchange,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            profit=profit,
                            profit_percentage=profit_percentage,
                            volume=min(1000, self.max_position_size // int(buy_price)),
                            timestamp=datetime.now(),
                        )
                        opportunities.append(opportunity)

        # 利益率でソート
        opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)

        logger.info(f"裁定取引機会を{len(opportunities)}件発見")
        return opportunities

    def _execute_trades(self, opportunities: List[ArbitrageOpportunity]) -> List[Trade]:
        """
        取引を実行

        Args:
            opportunities: 裁定取引機会のリスト

        Returns:
            実行された取引のリスト
        """
        executed_trades = []

        for opportunity in opportunities:
            try:
                # リスクチェック
                if not self._check_risk_limits(opportunity):
                    logger.warning(
                        f"リスク制限により取引をスキップ: {opportunity.symbol}"
                    )
                    continue

                # 買い注文
                buy_trade = self._create_trade(
                    symbol=opportunity.symbol,
                    side="buy",
                    price=opportunity.buy_price,
                    volume=opportunity.volume,
                    exchange=opportunity.buy_exchange,
                )

                # 売り注文
                sell_trade = self._create_trade(
                    symbol=opportunity.symbol,
                    side="sell",
                    price=opportunity.sell_price,
                    volume=opportunity.volume,
                    exchange=opportunity.sell_exchange,
                )

                # 取引を実行（実際の実装では取引所APIを呼び出し）
                if self._submit_order(buy_trade) and self._submit_order(sell_trade):
                    executed_trades.extend([buy_trade, sell_trade])

                    # ポジション更新
                    self._update_position(opportunity.symbol, opportunity.volume)

                    # 損益計算
                    profit = opportunity.profit * opportunity.volume
                    self.profit_loss += profit
                    self.total_trades += 2

                    logger.info(
                        f"裁定取引を実行: {opportunity.symbol}, 利益: {profit:.2f}"
                    )

            except Exception as e:
                logger.error(f"取引実行中にエラー: {e}")
                continue

        return executed_trades

    def _create_trade(
        self, symbol: str, side: str, price: float, volume: int, exchange: str
    ) -> Trade:
        """取引オブジェクトを作成"""
        return Trade(
            symbol=symbol,
            side=side,
            price=price,
            volume=volume,
            exchange=exchange,
            timestamp=datetime.now(),
            order_id=f"{symbol}_{side}_{int(time.time() * 1000)}",
        )

    def _submit_order(self, trade: Trade) -> bool:
        """
        注文を送信（モック実装）

        Args:
            trade: 取引オブジェクト

        Returns:
            注文成功フラグ
        """
        # 実際の実装では取引所APIを呼び出し
        # ここではモックとして常に成功を返す
        logger.debug(
            f"注文を送信: {trade.symbol} {trade.side} {trade.volume}@{trade.price}"
        )
        return True

    def _check_risk_limits(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        リスク制限をチェック

        Args:
            opportunity: 裁定取引機会

        Returns:
            リスク制限内かどうか
        """
        # ポジションサイズチェック
        current_position = self.positions.get(opportunity.symbol, 0)
        new_position = current_position + opportunity.volume

        if abs(new_position) > self.max_position_size:
            return False

        # リスク制限チェック
        exposure = opportunity.volume * opportunity.buy_price
        if exposure > self.max_position_size * self.risk_limit:
            return False

        return True

    def _update_position(self, symbol: str, volume: int):
        """ポジションを更新"""
        current_position = self.positions.get(symbol, 0)
        self.positions[symbol] = current_position + volume

    def start_market_data_feed(self, data_source):
        """市場データフィードを開始"""
        self.is_running = True

        def feed_worker():
            while self.is_running:
                try:
                    # 市場データを取得（実際の実装ではWebSocketやAPIから取得）
                    market_data = data_source.get_latest_data()
                    if market_data:
                        self.market_data_queue.put(market_data)

                    time.sleep(0.001)  # 1ms間隔
                except Exception as e:
                    logger.error(f"市場データ取得エラー: {e}")
                    time.sleep(0.1)

        # バックグラウンドで実行
        threading.Thread(target=feed_worker, daemon=True).start()
        logger.info("市場データフィードを開始しました")

    def stop_market_data_feed(self):
        """市場データフィードを停止"""
        self.is_running = False
        logger.info("市場データフィードを停止しました")

    def get_performance_metrics(self) -> Dict:
        """パフォーマンス指標を取得"""
        metrics = {
            "total_trades": self.total_trades,
            "profit_loss": self.profit_loss,
            "positions": self.positions.copy(),
        }

        if self.execution_times:
            metrics.update(
                {
                    "avg_execution_time": np.mean(self.execution_times),
                    "max_execution_time": np.max(self.execution_times),
                    "min_execution_time": np.min(self.execution_times),
                }
            )
        else:
            metrics.update(
                {
                    "avg_execution_time": 0.0,
                    "max_execution_time": 0.0,
                    "min_execution_time": 0.0,
                }
            )

        return metrics

    def cleanup(self):
        """リソースをクリーンアップ"""
        self.stop_market_data_feed()
        self.executor.shutdown(wait=True)
        logger.info("高頻度取引システムをクリーンアップしました")


class MockDataSource:
    """モックデータソース"""

    def __init__(self):
        self.symbols = ["BTC", "ETH", "XRP"]
        self.exchanges = ["Binance", "Coinbase", "Kraken"]
        self.base_prices = {"BTC": 50000, "ETH": 3000, "XRP": 0.5}

    def get_latest_data(self) -> Optional[Dict]:
        """最新の市場データを取得（モック）"""
        import random

        symbol = random.choice(self.symbols)
        base_price = self.base_prices[symbol]

        # ランダムな価格変動
        price_variation = random.uniform(-0.01, 0.01)  # ±1%
        current_price = base_price * (1 + price_variation)

        return {
            symbol: {
                exchange: current_price * random.uniform(0.999, 1.001)
                for exchange in self.exchanges
            }
        }


def main():
    """メイン関数（テスト用）"""
    # 設定
    config = {
        "latency_threshold": 0.001,
        "profit_threshold": 0.0005,  # 0.05%
        "max_position_size": 100000,
        "risk_limit": 0.01,
    }

    # 高頻度取引システムを初期化
    hft = HighFrequencyTrading(config)

    # モックデータソース
    data_source = MockDataSource()

    try:
        # 市場データフィードを開始
        hft.start_market_data_feed(data_source)

        # テスト実行
        for i in range(10):
            # 価格差データを生成
            price_differences = data_source.get_latest_data()

            if price_differences:
                # 裁定取引を実行
                trades = hft.execute_arbitrage(price_differences)
                print(f"実行 {i+1}: {len(trades)}件の取引を実行")

            time.sleep(0.1)

        # パフォーマンス指標を表示
        metrics = hft.get_performance_metrics()
        print("\n=== パフォーマンス指標 ===")
        for key, value in metrics.items():
            print(f"{key}: {value}")

    finally:
        # クリーンアップ
        hft.cleanup()


if __name__ == "__main__":
    main()
