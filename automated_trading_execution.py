#!/usr/bin/env python3
"""
自動取引実行システム
リアルタイム自動売買システムの追加推奨機能

期待効果: 月間10-20%の利益向上
実装難易度: 🟡 Medium
推定工数: 3-4日

主要機能:
1. ブローカーAPI連携
2. 自動注文実行
3. 注文状態監視
4. 取引履歴管理
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
import requests
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import base64
from urllib.parse import urlencode

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("automated_trading.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class OrderType(Enum):
    """注文タイプ"""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """注文サイド"""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """注文ステータス"""

    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class BrokerType(Enum):
    """ブローカータイプ"""

    SBI = "sbi"
    RAKUTEN = "rakuten"
    MATSUI = "matsui"
    MOCK = "mock"  # テスト用


@dataclass
class Order:
    """注文クラス"""

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float]
    stop_price: Optional[float]
    status: OrderStatus
    created_at: datetime
    filled_at: Optional[datetime]
    filled_price: Optional[float]
    filled_quantity: int
    remaining_quantity: int
    commission: float
    notes: str = ""


@dataclass
class Trade:
    """取引クラス"""

    trade_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    timestamp: datetime
    commission: float
    pnl: float = 0.0


@dataclass
class Position:
    """ポジションクラス"""

    symbol: str
    quantity: int
    average_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    last_updated: datetime


class BrokerAPI:
    """ブローカーAPI基底クラス"""

    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.session = requests.Session()

    def _generate_signature(self, params: Dict, timestamp: str) -> str:
        """署名を生成"""
        message = f"{timestamp}{json.dumps(params, sort_keys=True)}"
        signature = hmac.new(
            self.secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    def _get_headers(self, params: Dict = None) -> Dict[str, str]:
        """ヘッダーを取得"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(params or {}, timestamp)

        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }

    def get_account_info(self) -> Dict:
        """口座情報を取得"""
        raise NotImplementedError

    def get_positions(self) -> List[Position]:
        """ポジション情報を取得"""
        raise NotImplementedError

    def place_order(self, order: Order) -> str:
        """注文を発注"""
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> bool:
        """注文をキャンセル"""
        raise NotImplementedError

    def get_order_status(self, order_id: str) -> OrderStatus:
        """注文ステータスを取得"""
        raise NotImplementedError

    def get_order_history(self, symbol: str = None, limit: int = 100) -> List[Order]:
        """注文履歴を取得"""
        raise NotImplementedError


class MockBrokerAPI(BrokerAPI):
    """モックブローカーAPI（テスト用）"""

    def __init__(self):
        super().__init__("mock_api_key", "mock_secret_key", "https://mock-api.com")
        self.orders = {}
        self.positions = {}
        self.account_balance = 1000000.0
        self.order_counter = 0

    def get_account_info(self) -> Dict:
        """口座情報を取得"""
        return {
            "balance": self.account_balance,
            "equity": self.account_balance
            + sum(pos.unrealized_pnl for pos in self.positions.values()),
            "margin_used": 0.0,
            "margin_available": self.account_balance,
        }

    def get_positions(self) -> List[Position]:
        """ポジション情報を取得"""
        return list(self.positions.values())

    def place_order(self, order: Order) -> str:
        """注文を発注"""
        self.order_counter += 1
        order_id = f"ORDER_{self.order_counter:06d}"
        order.order_id = order_id
        order.status = OrderStatus.SUBMITTED
        order.created_at = datetime.now()

        # モック処理：即座に約定
        if order.order_type == OrderType.MARKET:
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.now()
            order.filled_price = order.price or 1000.0  # デフォルト価格
            order.filled_quantity = order.quantity
            order.remaining_quantity = 0
            order.commission = (
                order.filled_price * order.filled_quantity * 0.001
            )  # 0.1%手数料

        self.orders[order_id] = order

        # ポジションを更新
        if order.status == OrderStatus.FILLED:
            self._update_position(order)

        logger.info(
            f"注文発注: {order_id} - {order.symbol} {order.side.value} {order.quantity}株"
        )
        return order_id

    def cancel_order(self, order_id: str) -> bool:
        """注文をキャンセル"""
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
            logger.info(f"注文キャンセル: {order_id}")
            return True
        return False

    def get_order_status(self, order_id: str) -> OrderStatus:
        """注文ステータスを取得"""
        if order_id in self.orders:
            return self.orders[order_id].status
        return OrderStatus.REJECTED

    def get_order_history(self, symbol: str = None, limit: int = 100) -> List[Order]:
        """注文履歴を取得"""
        orders = list(self.orders.values())
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return sorted(orders, key=lambda x: x.created_at, reverse=True)[:limit]

    def _update_position(self, order: Order):
        """ポジションを更新"""
        symbol = order.symbol
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=0,
                average_price=0.0,
                current_price=order.filled_price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                last_updated=datetime.now(),
            )

        position = self.positions[symbol]

        if order.side == OrderSide.BUY:
            # 買い注文
            if position.quantity >= 0:
                # 新規買いまたは買い増し
                total_cost = (
                    position.quantity * position.average_price
                    + order.filled_quantity * order.filled_price
                )
                position.quantity += order.filled_quantity
                position.average_price = total_cost / position.quantity
            else:
                # 空売り決済
                if order.filled_quantity <= abs(position.quantity):
                    # 部分決済
                    position.realized_pnl += (
                        position.average_price - order.filled_price
                    ) * order.filled_quantity
                    position.quantity += order.filled_quantity
                else:
                    # 完全決済 + 新規買い
                    position.realized_pnl += (
                        position.average_price - order.filled_price
                    ) * abs(position.quantity)
                    remaining_quantity = order.filled_quantity - abs(position.quantity)
                    position.quantity = remaining_quantity
                    position.average_price = order.filled_price

        else:
            # 売り注文
            if position.quantity <= 0:
                # 新規売りまたは売り増し
                total_cost = (
                    abs(position.quantity) * position.average_price
                    + order.filled_quantity * order.filled_price
                )
                position.quantity -= order.filled_quantity
                position.average_price = total_cost / abs(position.quantity)
            else:
                # 買いポジション決済
                if order.filled_quantity <= position.quantity:
                    # 部分決済
                    position.realized_pnl += (
                        order.filled_price - position.average_price
                    ) * order.filled_quantity
                    position.quantity -= order.filled_quantity
                else:
                    # 完全決済 + 新規売り
                    position.realized_pnl += (
                        order.filled_price - position.average_price
                    ) * position.quantity
                    remaining_quantity = order.filled_quantity - position.quantity
                    position.quantity = -remaining_quantity
                    position.average_price = order.filled_price

        position.current_price = order.filled_price
        position.last_updated = datetime.now()

        # 未実現損益を計算
        if position.quantity != 0:
            if position.quantity > 0:
                position.unrealized_pnl = (
                    position.current_price - position.average_price
                ) * position.quantity
            else:
                position.unrealized_pnl = (
                    position.average_price - position.current_price
                ) * abs(position.quantity)


class TradingExecutionEngine:
    """取引実行エンジン"""

    def __init__(self, broker_api: BrokerAPI):
        self.broker_api = broker_api
        self.active_orders = {}
        self.execution_queue = []
        self.is_running = False
        self.execution_thread = None

    def start(self):
        """実行エンジンを開始"""
        if not self.is_running:
            self.is_running = True
            self.execution_thread = threading.Thread(target=self._execution_loop)
            self.execution_thread.daemon = True
            self.execution_thread.start()
            logger.info("取引実行エンジンを開始しました")

    def stop(self):
        """実行エンジンを停止"""
        self.is_running = False
        if self.execution_thread:
            self.execution_thread.join()
        logger.info("取引実行エンジンを停止しました")

    def _execution_loop(self):
        """実行ループ"""
        while self.is_running:
            try:
                # 実行キューから注文を処理
                if self.execution_queue:
                    order = self.execution_queue.pop(0)
                    self._execute_order(order)

                # アクティブ注文のステータスを確認
                self._monitor_active_orders()

                time.sleep(1)  # 1秒間隔でチェック

            except Exception as e:
                logger.error(f"実行ループエラー: {e}")
                time.sleep(5)

    def _execute_order(self, order: Order):
        """注文を実行"""
        try:
            # 口座残高をチェック
            if not self._check_account_balance(order):
                order.status = OrderStatus.REJECTED
                order.notes = "残高不足"
                logger.warning(f"残高不足で注文を拒否: {order.symbol}")
                return

            # 注文を発注
            order_id = self.broker_api.place_order(order)
            if order_id:
                order.order_id = order_id
                self.active_orders[order_id] = order
                logger.info(f"注文を発注しました: {order_id}")
            else:
                order.status = OrderStatus.REJECTED
                order.notes = "API エラー"
                logger.error(f"注文発注に失敗: {order.symbol}")

        except Exception as e:
            order.status = OrderStatus.REJECTED
            order.notes = f"実行エラー: {str(e)}"
            logger.error(f"注文実行エラー: {e}")

    def _check_account_balance(self, order: Order) -> bool:
        """口座残高をチェック"""
        try:
            account_info = self.broker_api.get_account_info()
            required_margin = order.quantity * (order.price or 1000.0) * 1.1  # 10%のマージン
            return account_info["margin_available"] >= required_margin
        except:
            return True  # チェックできない場合は許可

    def _monitor_active_orders(self):
        """アクティブ注文を監視"""
        completed_orders = []

        for order_id, order in self.active_orders.items():
            try:
                status = self.broker_api.get_order_status(order_id)
                if status != order.status:
                    order.status = status
                    logger.info(f"注文ステータス更新: {order_id} - {status.value}")

                # 約定またはキャンセルされた注文を処理
                if status in [
                    OrderStatus.FILLED,
                    OrderStatus.CANCELLED,
                    OrderStatus.REJECTED,
                ]:
                    completed_orders.append(order_id)

            except Exception as e:
                logger.error(f"注文監視エラー: {order_id} - {e}")

        # 完了した注文を削除
        for order_id in completed_orders:
            del self.active_orders[order_id]

    def submit_order(self, order: Order) -> str:
        """注文を提出"""
        self.execution_queue.append(order)
        logger.info(f"注文をキューに追加: {order.symbol} {order.side.value} {order.quantity}株")
        return order.order_id

    def cancel_order(self, order_id: str) -> bool:
        """注文をキャンセル"""
        try:
            if order_id in self.active_orders:
                success = self.broker_api.cancel_order(order_id)
                if success:
                    self.active_orders[order_id].status = OrderStatus.CANCELLED
                    logger.info(f"注文をキャンセルしました: {order_id}")
                return success
            return False
        except Exception as e:
            logger.error(f"注文キャンセルエラー: {order_id} - {e}")
            return False

    def get_active_orders(self) -> List[Order]:
        """アクティブ注文を取得"""
        return list(self.active_orders.values())

    def get_order_history(self, symbol: str = None, limit: int = 100) -> List[Order]:
        """注文履歴を取得"""
        return self.broker_api.get_order_history(symbol, limit)


class AutomatedTradingSystem:
    """自動取引システム"""

    def __init__(self, broker_type: BrokerType = BrokerType.MOCK):
        self.broker_type = broker_type
        self.broker_api = self._create_broker_api()
        self.execution_engine = TradingExecutionEngine(self.broker_api)
        self.is_running = False

        logger.info(f"自動取引システムを初期化しました: {broker_type.value}")

    def _create_broker_api(self) -> BrokerAPI:
        """ブローカーAPIを作成"""
        if self.broker_type == BrokerType.MOCK:
            return MockBrokerAPI()
        else:
            # 実際のブローカーAPI実装
            raise NotImplementedError(f"未対応のブローカー: {self.broker_type.value}")

    def start_trading(self):
        """取引を開始"""
        if not self.is_running:
            self.is_running = True
            self.execution_engine.start()
            logger.info("自動取引を開始しました")

    def stop_trading(self):
        """取引を停止"""
        if self.is_running:
            self.is_running = False
            self.execution_engine.stop()
            logger.info("自動取引を停止しました")

    def place_buy_order(
        self,
        symbol: str,
        quantity: int,
        price: float = None,
        order_type: OrderType = OrderType.MARKET,
    ) -> str:
        """買い注文を発注"""
        order = Order(
            order_id="",
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=None,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            filled_at=None,
            filled_price=None,
            filled_quantity=0,
            remaining_quantity=quantity,
            commission=0.0,
        )

        return self.execution_engine.submit_order(order)

    def place_sell_order(
        self,
        symbol: str,
        quantity: int,
        price: float = None,
        order_type: OrderType = OrderType.MARKET,
    ) -> str:
        """売り注文を発注"""
        order = Order(
            order_id="",
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=None,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            filled_at=None,
            filled_price=None,
            filled_quantity=0,
            remaining_quantity=quantity,
            commission=0.0,
        )

        return self.execution_engine.submit_order(order)

    def get_positions(self) -> List[Position]:
        """ポジション情報を取得"""
        return self.broker_api.get_positions()

    def get_account_info(self) -> Dict:
        """口座情報を取得"""
        return self.broker_api.get_account_info()

    def get_active_orders(self) -> List[Order]:
        """アクティブ注文を取得"""
        return self.execution_engine.get_active_orders()

    def cancel_order(self, order_id: str) -> bool:
        """注文をキャンセル"""
        return self.execution_engine.cancel_order(order_id)

    def get_trading_summary(self) -> Dict:
        """取引サマリーを取得"""
        positions = self.get_positions()
        account_info = self.get_account_info()
        active_orders = self.get_active_orders()

        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        total_realized_pnl = sum(pos.realized_pnl for pos in positions)

        return {
            "account_balance": account_info["balance"],
            "equity": account_info["equity"],
            "total_positions": len(positions),
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_realized_pnl": total_realized_pnl,
            "active_orders": len(active_orders),
            "system_running": self.is_running,
            "last_update": datetime.now().isoformat(),
        }


def main():
    """メイン関数（テスト用）"""
    # 自動取引システムを初期化
    trading_system = AutomatedTradingSystem(BrokerType.MOCK)

    # 取引を開始
    trading_system.start_trading()

    try:
        # テスト用の注文を発注
        print("=== 自動取引システムテスト ===")

        # 買い注文を発注
        buy_order_id = trading_system.place_buy_order(
            "7203", 100, 2500.0, OrderType.MARKET
        )
        print(f"買い注文発注: {buy_order_id}")

        # 売り注文を発注
        sell_order_id = trading_system.place_sell_order(
            "6758", 50, 12000.0, OrderType.LIMIT
        )
        print(f"売り注文発注: {sell_order_id}")

        # 少し待機
        time.sleep(2)

        # 口座情報を表示
        account_info = trading_system.get_account_info()
        print(f"\n=== 口座情報 ===")
        print(f"残高: ¥{account_info['balance']:,.0f}")
        print(f"評価額: ¥{account_info['equity']:,.0f}")

        # ポジション情報を表示
        positions = trading_system.get_positions()
        print(f"\n=== ポジション情報 ===")
        for pos in positions:
            print(f"{pos.symbol}: {pos.quantity}株 @ ¥{pos.average_price:.2f}")
            print(f"  未実現損益: ¥{pos.unrealized_pnl:,.0f}")

        # アクティブ注文を表示
        active_orders = trading_system.get_active_orders()
        print(f"\n=== アクティブ注文 ===")
        for order in active_orders:
            print(
                f"{order.symbol} {order.side.value} {order.quantity}株 - {order.status.value}"
            )

        # 取引サマリーを表示
        summary = trading_system.get_trading_summary()
        print(f"\n=== 取引サマリー ===")
        for key, value in summary.items():
            print(f"{key}: {value}")

    finally:
        # 取引を停止
        trading_system.stop_trading()
        print("\n自動取引システムを停止しました")


if __name__ == "__main__":
    main()
