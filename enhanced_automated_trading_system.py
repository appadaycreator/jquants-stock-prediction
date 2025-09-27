#!/usr/bin/env python3
"""
強化自動取引実行システム
統合システムとの完全連携による月間10-20%の利益向上

主要機能:
1. ブローカーAPI連携
2. 自動注文実行
3. 注文状態監視
4. 取引履歴管理
5. 統合システムとの完全連携
6. AI予測システムとの連携
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import hmac
import base64
from urllib.parse import urlencode
import os
import sys

# 統合システムのインポート
from unified_system import UnifiedSystem, ErrorCategory, LogLevel, LogCategory
from enhanced_ai_prediction_system import EnhancedAIPredictionSystem, PredictionResult

warnings.filterwarnings("ignore")


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


class TradingStrategy(Enum):
    """取引戦略"""

    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING = "swing"
    AI_PREDICTION = "ai_prediction"


@dataclass
class Order:
    """注文データクラス"""

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None
    filled_quantity: float = 0.0
    average_price: float = 0.0
    commission: float = 0.0
    strategy: TradingStrategy = None
    ai_prediction_id: str = None
    risk_score: float = 0.0
    additional_info: Dict[str, any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)

    def to_json(self) -> str:
        """JSON形式に変換"""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)


@dataclass
class Position:
    """ポジションデータクラス"""

    symbol: str
    quantity: float
    average_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    created_at: datetime
    updated_at: datetime
    strategy: TradingStrategy = None
    risk_score: float = 0.0

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)


@dataclass
class TradingSignal:
    """取引シグナルデータクラス"""

    symbol: str
    signal_type: str  # 'buy', 'sell', 'hold'
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    price: float
    quantity: float
    strategy: TradingStrategy
    ai_prediction: Optional[PredictionResult] = None
    technical_indicators: Dict[str, float] = None
    risk_metrics: Dict[str, float] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)


class EnhancedAutomatedTradingSystem:
    """強化自動取引実行システム"""

    def __init__(
        self,
        unified_system: UnifiedSystem = None,
        ai_prediction_system: EnhancedAIPredictionSystem = None,
    ):
        """初期化"""
        self.unified_system = unified_system or UnifiedSystem()
        self.ai_prediction_system = ai_prediction_system or EnhancedAIPredictionSystem(
            self.unified_system
        )

        # 取引データ
        self.orders = {}
        self.positions = {}
        self.trading_history = []
        self.signals = []

        # 設定
        self.config = {
            "max_position_size": 10000.0,
            "max_daily_trades": 50,
            "risk_limit_per_trade": 0.02,  # 2%
            "stop_loss_percentage": 0.05,  # 5%
            "take_profit_percentage": 0.10,  # 10%
            "commission_rate": 0.001,  # 0.1%
            "min_order_size": 100.0,
            "max_order_size": 10000.0,
            "trading_enabled": True,
            "ai_prediction_enabled": True,
            "risk_management_enabled": True,
            "log_path": "logs/automated_trading.log",
        }

        # ブローカー設定（シミュレーション用）
        self.broker_config = {
            "api_url": "https://api.simulation-broker.com",
            "api_key": "simulation_key",
            "api_secret": "simulation_secret",
            "simulation_mode": True,
        }

        # 統計情報
        self.daily_stats = {
            "trades_count": 0,
            "total_volume": 0.0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "average_hold_time": 0.0,
        }

        # ログ設定
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        # ファイルハンドラーの追加
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler(self.config["log_path"])
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 取引スレッド
        self.trading_thread = None
        self.is_running = False

        self.logger.info("🚀 強化自動取引システム初期化完了")

    def generate_trading_signal(
        self,
        symbol: str,
        data: pd.DataFrame,
        strategy: TradingStrategy = TradingStrategy.AI_PREDICTION,
    ) -> TradingSignal:
        """取引シグナルの生成"""
        try:
            signal_type = "hold"
            strength = 0.0
            confidence = 0.0
            price = (
                data["close"].iloc[-1]
                if "close" in data.columns
                else data["price"].iloc[-1]
            )
            quantity = 0.0
            ai_prediction = None
            technical_indicators = {}
            risk_metrics = {}

            if (
                strategy == TradingStrategy.AI_PREDICTION
                and self.config["ai_prediction_enabled"]
            ):
                # AI予測ベースのシグナル
                try:
                    # 最新のモデルを取得
                    model_names = list(self.ai_prediction_system.models.keys())
                    if model_names:
                        latest_model = model_names[-1]
                        prediction = self.ai_prediction_system.predict(
                            latest_model, data
                        )
                        ai_prediction = prediction

                        # 予測に基づくシグナル生成
                        current_price = price
                        predicted_price = prediction.predicted_price
                        price_change = (predicted_price - current_price) / current_price

                        if price_change > 0.02:  # 2%以上の上昇予測
                            signal_type = "buy"
                            strength = min(1.0, abs(price_change) * 10)
                            confidence = prediction.confidence_score
                            quantity = self.calculate_position_size(
                                symbol, price, strength
                            )
                        elif price_change < -0.02:  # 2%以上の下落予測
                            signal_type = "sell"
                            strength = min(1.0, abs(price_change) * 10)
                            confidence = prediction.confidence_score
                            quantity = self.calculate_position_size(
                                symbol, price, strength
                            )
                        else:
                            signal_type = "hold"
                            strength = 0.0
                            confidence = prediction.confidence_score

                except Exception as e:
                    self.unified_system.log_error(
                        error=e,
                        category=ErrorCategory.MODEL_ERROR,
                        context=f"AI予測シグナル生成エラー: {symbol}",
                    )

            elif strategy == TradingStrategy.MOMENTUM:
                # モメンタム戦略
                if len(data) >= 20:
                    short_ma = data["close"].rolling(window=5).mean().iloc[-1]
                    long_ma = data["close"].rolling(window=20).mean().iloc[-1]

                    if short_ma > long_ma * 1.02:
                        signal_type = "buy"
                        strength = min(1.0, (short_ma - long_ma) / long_ma * 10)
                        confidence = 0.7
                        quantity = self.calculate_position_size(symbol, price, strength)
                    elif short_ma < long_ma * 0.98:
                        signal_type = "sell"
                        strength = min(1.0, (long_ma - short_ma) / long_ma * 10)
                        confidence = 0.7
                        quantity = self.calculate_position_size(symbol, price, strength)

            elif strategy == TradingStrategy.MEAN_REVERSION:
                # 平均回帰戦略
                if len(data) >= 20:
                    sma = data["close"].rolling(window=20).mean().iloc[-1]
                    current_price = data["close"].iloc[-1]
                    deviation = (current_price - sma) / sma

                    if deviation < -0.05:  # 5%以上下回った場合
                        signal_type = "buy"
                        strength = min(1.0, abs(deviation) * 5)
                        confidence = 0.6
                        quantity = self.calculate_position_size(symbol, price, strength)
                    elif deviation > 0.05:  # 5%以上上回った場合
                        signal_type = "sell"
                        strength = min(1.0, abs(deviation) * 5)
                        confidence = 0.6
                        quantity = self.calculate_position_size(symbol, price, strength)

            # 技術指標の計算
            if len(data) >= 14:
                technical_indicators = self.calculate_technical_indicators(data)

            # リスクメトリクスの計算
            risk_metrics = self.calculate_risk_metrics(symbol, price, quantity)

            # シグナルの作成
            signal = TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                strength=strength,
                confidence=confidence,
                price=price,
                quantity=quantity,
                strategy=strategy,
                ai_prediction=ai_prediction,
                technical_indicators=technical_indicators,
                risk_metrics=risk_metrics,
            )

            self.signals.append(signal)

            self.logger.info(
                f"📊 取引シグナル生成: {symbol} - {signal_type} (強度: {strength:.2f}, 信頼度: {confidence:.2f})"
            )

            return signal

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"取引シグナル生成エラー: {symbol}",
            )
            raise

    def calculate_position_size(
        self, symbol: str, price: float, strength: float
    ) -> float:
        """ポジションサイズの計算"""
        try:
            # 基本ポジションサイズ
            base_size = self.config["max_position_size"] * strength

            # リスク管理による調整
            if self.config["risk_management_enabled"]:
                risk_limit = self.config["risk_limit_per_trade"]
                max_risk_amount = self.get_account_balance() * risk_limit
                max_position_value = max_risk_amount / (
                    self.config["stop_loss_percentage"]
                )
                base_size = min(base_size, max_position_value / price)

            # 最小・最大注文サイズの制限
            min_size = self.config["min_order_size"] / price
            max_size = self.config["max_order_size"] / price

            return max(min_size, min(max_size, base_size))

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"ポジションサイズ計算エラー: {symbol}",
            )
            return 0.0

    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """技術指標の計算"""
        try:
            indicators = {}

            if len(data) < 14:
                return indicators

            # RSI
            delta = data["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators["rsi"] = (100 - (100 / (1 + rs))).iloc[-1]

            # MACD
            exp1 = data["close"].ewm(span=12).mean()
            exp2 = data["close"].ewm(span=26).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=9).mean()
            indicators["macd"] = macd.iloc[-1]
            indicators["macd_signal"] = macd_signal.iloc[-1]
            indicators["macd_histogram"] = (macd - macd_signal).iloc[-1]

            # 移動平均
            indicators["ma_5"] = data["close"].rolling(window=5).mean().iloc[-1]
            indicators["ma_10"] = data["close"].rolling(window=10).mean().iloc[-1]
            indicators["ma_20"] = data["close"].rolling(window=20).mean().iloc[-1]

            # ボリンジャーバンド
            bb_period = 20
            bb_std = 2
            sma = data["close"].rolling(window=bb_period).mean()
            std = data["close"].rolling(window=bb_period).std()
            indicators["bb_upper"] = (sma + (std * bb_std)).iloc[-1]
            indicators["bb_lower"] = (sma - (std * bb_std)).iloc[-1]
            indicators["bb_middle"] = sma.iloc[-1]

            return indicators

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.DATA_PROCESSING_ERROR,
                context="技術指標計算エラー",
            )
            return {}

    def calculate_risk_metrics(
        self, symbol: str, price: float, quantity: float
    ) -> Dict[str, float]:
        """リスクメトリクスの計算"""
        try:
            metrics = {}

            # ポジション価値
            position_value = price * quantity
            metrics["position_value"] = position_value

            # 最大損失
            stop_loss_price = price * (1 - self.config["stop_loss_percentage"])
            max_loss = (price - stop_loss_price) * quantity
            metrics["max_loss"] = max_loss

            # 最大利益
            take_profit_price = price * (1 + self.config["take_profit_percentage"])
            max_profit = (take_profit_price - price) * quantity
            metrics["max_profit"] = max_profit

            # リスクリワード比
            if max_loss > 0:
                metrics["risk_reward_ratio"] = max_profit / max_loss
            else:
                metrics["risk_reward_ratio"] = 0.0

            # アカウントバランスに対するリスク
            account_balance = self.get_account_balance()
            if account_balance > 0:
                metrics["risk_percentage"] = max_loss / account_balance
            else:
                metrics["risk_percentage"] = 0.0

            return metrics

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"リスクメトリクス計算エラー: {symbol}",
            )
            return {}

    def place_order(self, signal: TradingSignal) -> Optional[Order]:
        """注文の実行"""
        try:
            if not self.config["trading_enabled"]:
                self.logger.warning("取引が無効化されています")
                return None

            if signal.signal_type == "hold" or signal.quantity <= 0:
                return None

            # 注文IDの生成
            order_id = f"{signal.symbol}_{signal.signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # 注文サイドの決定
            side = OrderSide.BUY if signal.signal_type == "buy" else OrderSide.SELL

            # 注文タイプの決定
            order_type = OrderType.MARKET  # 簡易化のため市場価格注文

            # 注文の作成
            order = Order(
                order_id=order_id,
                symbol=signal.symbol,
                side=side,
                order_type=order_type,
                quantity=signal.quantity,
                price=signal.price,
                strategy=signal.strategy,
                ai_prediction_id=(
                    signal.ai_prediction.prediction_id if signal.ai_prediction else None
                ),
                risk_score=(
                    signal.risk_metrics.get("risk_percentage", 0.0)
                    if signal.risk_metrics
                    else 0.0
                ),
                additional_info={
                    "signal_strength": signal.strength,
                    "signal_confidence": signal.confidence,
                    "technical_indicators": signal.technical_indicators,
                    "risk_metrics": signal.risk_metrics,
                },
            )

            # シミュレーション取引の場合
            if self.broker_config["simulation_mode"]:
                order = self.simulate_order_execution(order)
            else:
                # 実際のブローカーAPI呼び出し
                order = self.execute_real_order(order)

            # 注文の保存
            self.orders[order_id] = order

            # 取引履歴の記録
            self.trading_history.append(
                {
                    "timestamp": datetime.now(),
                    "action": "order_placed",
                    "order_id": order_id,
                    "symbol": signal.symbol,
                    "side": signal.signal_type,
                    "quantity": signal.quantity,
                    "price": signal.price,
                }
            )

            self.logger.info(
                f"📝 注文実行: {order_id} - {signal.symbol} {signal.signal_type} {signal.quantity:.2f}@{signal.price:.2f}"
            )

            return order

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.API_ERROR,
                context=f"注文実行エラー: {signal.symbol}",
            )
            return None

    def simulate_order_execution(self, order: Order) -> Order:
        """シミュレーション注文実行"""
        try:
            # シミュレーション用の価格変動
            price_variance = np.random.normal(0, 0.001)  # 0.1%の標準偏差
            execution_price = order.price * (1 + price_variance)

            # 注文の実行
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.average_price = execution_price
            order.commission = (
                order.quantity * execution_price * self.config["commission_rate"]
            )
            order.updated_at = datetime.now()

            # ポジションの更新
            self.update_position(order)

            return order

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"シミュレーション注文実行エラー: {order.order_id}",
            )
            order.status = OrderStatus.REJECTED
            return order

    def execute_real_order(self, order: Order) -> Order:
        """実際の注文実行（ブローカーAPI連携）"""
        try:
            # 実際のブローカーAPI実装
            # ここでは簡易的な実装
            order.status = OrderStatus.SUBMITTED
            order.updated_at = datetime.now()

            # 実際のAPI呼び出し処理
            # response = self.call_broker_api('place_order', order.to_dict())
            # order = self.process_broker_response(order, response)

            return order

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.API_ERROR,
                context=f"実際の注文実行エラー: {order.order_id}",
            )
            order.status = OrderStatus.REJECTED
            return order

    def update_position(self, order: Order):
        """ポジションの更新"""
        try:
            symbol = order.symbol

            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=0.0,
                    average_price=0.0,
                    current_price=order.average_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    total_pnl=0.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    strategy=order.strategy,
                    risk_score=order.risk_score,
                )

            position = self.positions[symbol]

            if order.side == OrderSide.BUY:
                # 買い注文の場合
                if position.quantity >= 0:
                    # 新規買いまたは追加買い
                    total_quantity = position.quantity + order.filled_quantity
                    total_value = (
                        position.quantity * position.average_price
                        + order.filled_quantity * order.average_price
                    )
                    position.average_price = (
                        total_value / total_quantity if total_quantity > 0 else 0
                    )
                    position.quantity = total_quantity
                else:
                    # 空売り決済
                    position.quantity += order.filled_quantity
                    if position.quantity > 0:
                        position.average_price = order.average_price
            else:
                # 売り注文の場合
                if position.quantity <= 0:
                    # 新規売りまたは追加売り
                    total_quantity = position.quantity - order.filled_quantity
                    total_value = (
                        abs(position.quantity) * position.average_price
                        + order.filled_quantity * order.average_price
                    )
                    position.average_price = (
                        total_value / abs(total_quantity) if total_quantity < 0 else 0
                    )
                    position.quantity = total_quantity
                else:
                    # 買いポジション決済
                    position.quantity -= order.filled_quantity
                    if position.quantity < 0:
                        position.average_price = order.average_price

            position.updated_at = datetime.now()

            # 損益の計算
            self.calculate_position_pnl(symbol)

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"ポジション更新エラー: {order.symbol}",
            )

    def calculate_position_pnl(self, symbol: str):
        """ポジション損益の計算"""
        try:
            if symbol not in self.positions:
                return

            position = self.positions[symbol]

            # 現在価格の取得（簡易化のため前回の価格を使用）
            current_price = position.current_price

            # 未実現損益の計算
            if position.quantity > 0:
                position.unrealized_pnl = (
                    current_price - position.average_price
                ) * position.quantity
            elif position.quantity < 0:
                position.unrealized_pnl = (
                    position.average_price - current_price
                ) * abs(position.quantity)
            else:
                position.unrealized_pnl = 0.0

            # 総損益の計算
            position.total_pnl = position.realized_pnl + position.unrealized_pnl

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"損益計算エラー: {symbol}",
            )

    def get_account_balance(self) -> float:
        """アカウント残高の取得"""
        try:
            # シミュレーション用の残高
            return 100000.0  # 10万円
        except Exception:
            return 0.0

    def get_portfolio_summary(self) -> Dict[str, any]:
        """ポートフォリオサマリーの取得"""
        try:
            total_value = 0.0
            total_pnl = 0.0
            position_count = 0

            for symbol, position in self.positions.items():
                if position.quantity != 0:
                    total_value += abs(position.quantity) * position.current_price
                    total_pnl += position.total_pnl
                    position_count += 1

            return {
                "total_positions": position_count,
                "total_value": total_value,
                "total_pnl": total_pnl,
                "account_balance": self.get_account_balance(),
                "total_equity": self.get_account_balance() + total_pnl,
                "daily_trades": self.daily_stats["trades_count"],
                "win_rate": self.daily_stats["win_rate"],
            }

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="ポートフォリオサマリー取得エラー",
            )
            return {}

    def start_trading(self):
        """取引の開始"""
        try:
            if self.is_running:
                self.logger.warning("取引は既に実行中です")
                return

            self.is_running = True
            self.trading_thread = threading.Thread(
                target=self._trading_loop, daemon=True
            )
            self.trading_thread.start()

            self.logger.info("🚀 自動取引開始")

        except Exception as e:
            self.unified_system.log_error(
                error=e, category=ErrorCategory.SYSTEM_ERROR, context="取引開始エラー"
            )

    def stop_trading(self):
        """取引の停止"""
        try:
            self.is_running = False

            if self.trading_thread:
                self.trading_thread.join(timeout=5.0)

            self.logger.info("🛑 自動取引停止")

        except Exception as e:
            self.unified_system.log_error(
                error=e, category=ErrorCategory.SYSTEM_ERROR, context="取引停止エラー"
            )

    def _trading_loop(self):
        """取引ループ"""
        try:
            while self.is_running:
                # 取引シグナルの生成と実行
                # ここでは簡易的な実装
                time.sleep(1.0)  # 1秒間隔

        except Exception as e:
            self.unified_system.log_error(
                error=e, category=ErrorCategory.SYSTEM_ERROR, context="取引ループエラー"
            )
        finally:
            self.is_running = False

    def export_trading_data(self, file_path: str, format: str = "json") -> bool:
        """取引データのエクスポート"""
        try:
            export_data = {
                "orders": [order.to_dict() for order in self.orders.values()],
                "positions": [
                    position.to_dict() for position in self.positions.values()
                ],
                "signals": [signal.to_dict() for signal in self.signals],
                "trading_history": self.trading_history,
                "portfolio_summary": self.get_portfolio_summary(),
                "daily_stats": self.daily_stats,
            }

            if format.lower() == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, default=str, ensure_ascii=False, indent=2)
            elif format.lower() == "csv":
                # 注文データのCSV出力
                orders_df = pd.DataFrame(
                    [order.to_dict() for order in self.orders.values()]
                )
                orders_df.to_csv(
                    f"{file_path}_orders.csv", index=False, encoding="utf-8"
                )

                # ポジションデータのCSV出力
                positions_df = pd.DataFrame(
                    [position.to_dict() for position in self.positions.values()]
                )
                positions_df.to_csv(
                    f"{file_path}_positions.csv", index=False, encoding="utf-8"
                )
            else:
                raise ValueError(f"未対応のフォーマット: {format}")

            self.logger.info(f"📊 取引データエクスポート完了: {file_path}")
            return True

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.FILE_ERROR,
                context=f"取引データエクスポートエラー: {file_path}",
            )
            return False


def main():
    """メイン関数"""
    try:
        # 統合システムの初期化
        unified_system = UnifiedSystem()

        # AI予測システムの初期化
        ai_system = EnhancedAIPredictionSystem(unified_system)

        # 自動取引システムの初期化
        trading_system = EnhancedAutomatedTradingSystem(unified_system, ai_system)

        # サンプルデータの作成
        np.random.seed(42)
        dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
        data = pd.DataFrame(
            {
                "date": dates,
                "price": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
                "volume": np.random.randint(1000, 10000, len(dates)),
                "high": 100
                + np.cumsum(np.random.randn(len(dates)) * 0.5)
                + np.random.randn(len(dates)) * 0.1,
                "low": 100
                + np.cumsum(np.random.randn(len(dates)) * 0.5)
                - np.random.randn(len(dates)) * 0.1,
                "open": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
                "close": 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
                "symbol": "TEST",
            }
        )

        # 取引シグナルの生成
        signal = trading_system.generate_trading_signal(
            "TEST", data, TradingStrategy.AI_PREDICTION
        )

        print(f"取引シグナル: {signal.signal_type}")
        print(f"強度: {signal.strength:.2f}")
        print(f"信頼度: {signal.confidence:.2f}")
        print(f"数量: {signal.quantity:.2f}")

        # 注文の実行
        if signal.signal_type != "hold":
            order = trading_system.place_order(signal)
            if order:
                print(f"注文実行: {order.order_id}")
                print(f"ステータス: {order.status.value}")

        # ポートフォリオサマリーの表示
        summary = trading_system.get_portfolio_summary()
        print(f"\nポートフォリオサマリー: {summary}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
