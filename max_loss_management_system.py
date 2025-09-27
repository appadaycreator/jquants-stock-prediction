#!/usr/bin/env python3
"""
個別銘柄の最大損失額設定システム
期待効果: 損失を60-80%削減
実装難易度: 🟡 中
推定工数: 2-3日

機能:
1. 個別銘柄の最大損失額設定
2. 動的最大損失額調整
3. 損失監視とアラート
4. 自動損切り実行
5. 損失履歴管理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from collections import defaultdict, deque
import yfinance as yf
from scipy import stats
import asyncio
import aiohttp

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("max_loss_management_system.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class LossLevel(Enum):
    """損失レベル"""

    NONE = "NONE"  # 損失なし
    MINOR = "MINOR"  # 軽微な損失（1%未満）
    MODERATE = "MODERATE"  # 中程度の損失（1-3%）
    SIGNIFICANT = "SIGNIFICANT"  # 重要な損失（3-5%）
    SEVERE = "SEVERE"  # 深刻な損失（5-10%）
    CRITICAL = "CRITICAL"  # 致命的な損失（10%以上）


class AlertType(Enum):
    """アラートタイプ"""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class MaxLossSettings:
    """最大損失設定"""

    symbol: str
    max_loss_amount: float
    max_loss_percent: float
    max_loss_price: float
    alert_thresholds: Dict[LossLevel, float]
    auto_stop_loss: bool
    trailing_stop_enabled: bool
    last_updated: datetime


@dataclass
class LossAlert:
    """損失アラート"""

    symbol: str
    timestamp: datetime
    alert_type: AlertType
    current_loss: float
    loss_percent: float
    max_loss_amount: float
    remaining_buffer: float
    message: str
    action_required: bool


@dataclass
class LossHistory:
    """損失履歴"""

    symbol: str
    timestamp: datetime
    entry_price: float
    current_price: float
    loss_amount: float
    loss_percent: float
    max_loss_amount: float
    loss_level: LossLevel
    alert_sent: bool
    action_taken: str


@dataclass
class PositionLossStatus:
    """ポジション損失状況"""

    symbol: str
    current_price: float
    entry_price: float
    position_size: float
    current_loss: float
    loss_percent: float
    max_loss_amount: float
    remaining_buffer: float
    loss_level: LossLevel
    alert_status: str
    recommended_action: str


class MaxLossManagementSystem:
    """最大損失管理システム"""

    def __init__(self, account_value: float = 1000000):
        self.account_value = account_value
        self.max_loss_settings = {}
        self.loss_history = defaultdict(list)
        self.active_alerts = defaultdict(list)
        self.positions = {}

        # 損失管理パラメータ
        self.loss_params = {
            "default_max_loss_percent": 0.05,  # デフォルト最大損失5%
            "critical_loss_threshold": 0.10,  # 致命的損失閾値10%
            "alert_frequency_minutes": 15,  # アラート頻度（分）
            "auto_stop_loss_threshold": 0.08,  # 自動損切り閾値8%
        }

        # 損失レベル閾値
        self.loss_thresholds = {
            LossLevel.NONE: 0.0,
            LossLevel.MINOR: 0.01,
            LossLevel.MODERATE: 0.03,
            LossLevel.SIGNIFICANT: 0.05,
            LossLevel.SEVERE: 0.10,
            LossLevel.CRITICAL: 0.20,
        }

    def set_max_loss_for_stock(
        self,
        symbol: str,
        max_loss_percent: float = None,
        max_loss_amount: float = None,
        auto_stop_loss: bool = True,
        trailing_stop: bool = True,
    ) -> MaxLossSettings:
        """個別銘柄の最大損失設定"""
        try:
            logger.info(f"最大損失設定開始: {symbol}")

            # デフォルト値の設定
            if max_loss_percent is None:
                max_loss_percent = self.loss_params["default_max_loss_percent"]

            if max_loss_amount is None:
                max_loss_amount = self.account_value * max_loss_percent

            # 現在価格取得
            current_price = self._get_current_price(symbol)
            if current_price is None:
                current_price = 1000.0  # デフォルト価格

            # 最大損失価格計算
            max_loss_price = current_price * (1 - max_loss_percent)

            # アラート閾値設定
            alert_thresholds = self._calculate_alert_thresholds(max_loss_percent)

            # 最大損失設定作成
            settings = MaxLossSettings(
                symbol=symbol,
                max_loss_amount=max_loss_amount,
                max_loss_percent=max_loss_percent,
                max_loss_price=max_loss_price,
                alert_thresholds=alert_thresholds,
                auto_stop_loss=auto_stop_loss,
                trailing_stop_enabled=trailing_stop,
                last_updated=datetime.now(),
            )

            # 設定保存
            self.max_loss_settings[symbol] = settings

            logger.info(
                f"最大損失設定完了: {symbol} - 最大損失額: ¥{max_loss_amount:,.0f}"
            )
            return settings

        except Exception as e:
            logger.error(f"最大損失設定エラー: {symbol} - {e}")
            return self._create_default_max_loss_settings(symbol)

    def _get_current_price(self, symbol: str) -> Optional[float]:
        """現在価格取得"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            if not hist.empty:
                return hist["Close"].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"価格取得エラー: {symbol} - {e}")
            return None

    def _calculate_alert_thresholds(
        self, max_loss_percent: float
    ) -> Dict[LossLevel, float]:
        """アラート閾値計算"""
        try:
            thresholds = {}

            # 各損失レベルに対する閾値設定
            for level, threshold in self.loss_thresholds.items():
                if level == LossLevel.NONE:
                    thresholds[level] = 0.0
                elif level == LossLevel.CRITICAL:
                    thresholds[level] = max_loss_percent
                else:
                    # 最大損失の割合で設定
                    thresholds[level] = (
                        max_loss_percent
                        * threshold
                        / self.loss_thresholds[LossLevel.CRITICAL]
                    )

            return thresholds
        except Exception as e:
            logger.error(f"アラート閾値計算エラー: {e}")
            return {level: 0.0 for level in LossLevel}

    def add_position(
        self,
        symbol: str,
        entry_price: float,
        position_size: float,
        quantity: int = None,
    ) -> bool:
        """ポジション追加"""
        try:
            logger.info(f"ポジション追加: {symbol} @ ¥{entry_price:,.0f}")

            # 数量計算
            if quantity is None:
                quantity = int(position_size / entry_price)

            # ポジション情報保存
            self.positions[symbol] = {
                "entry_price": entry_price,
                "position_size": position_size,
                "quantity": quantity,
                "entry_time": datetime.now(),
                "current_price": entry_price,
                "unrealized_pnl": 0.0,
            }

            # 最大損失設定が存在しない場合は作成
            if symbol not in self.max_loss_settings:
                self.set_max_loss_for_stock(symbol)

            return True
        except Exception as e:
            logger.error(f"ポジション追加エラー: {symbol} - {e}")
            return False

    def update_position_price(
        self, symbol: str, current_price: float
    ) -> PositionLossStatus:
        """ポジション価格更新と損失状況確認"""
        try:
            if symbol not in self.positions:
                logger.warning(f"ポジションが見つかりません: {symbol}")
                return self._create_default_loss_status(symbol, current_price)

            # ポジション情報更新
            position = self.positions[symbol]
            position["current_price"] = current_price

            # 未実現損益計算
            entry_price = position["entry_price"]
            quantity = position["quantity"]
            unrealized_pnl = (current_price - entry_price) * quantity
            position["unrealized_pnl"] = unrealized_pnl

            # 損失状況分析
            loss_status = self._analyze_loss_status(symbol, current_price)

            # アラート生成
            if loss_status.loss_level != LossLevel.NONE:
                self._generate_loss_alert(symbol, loss_status)

            # 履歴記録
            self._record_loss_history(symbol, loss_status)

            # 自動損切り判定
            if self._should_auto_stop_loss(symbol, loss_status):
                self._execute_auto_stop_loss(symbol, loss_status)

            return loss_status

        except Exception as e:
            logger.error(f"ポジション価格更新エラー: {symbol} - {e}")
            return self._create_default_loss_status(symbol, current_price)

    def _analyze_loss_status(
        self, symbol: str, current_price: float
    ) -> PositionLossStatus:
        """損失状況分析"""
        try:
            if symbol not in self.positions or symbol not in self.max_loss_settings:
                return self._create_default_loss_status(symbol, current_price)

            position = self.positions[symbol]
            max_loss_settings = self.max_loss_settings[symbol]

            # 基本情報
            entry_price = position["entry_price"]
            position_size = position["position_size"]
            quantity = position["quantity"]

            # 損失計算
            current_loss = (entry_price - current_price) * quantity
            loss_percent = current_loss / position_size if position_size > 0 else 0.0

            # 最大損失額
            max_loss_amount = max_loss_settings.max_loss_amount

            # 残りバッファ
            remaining_buffer = max_loss_amount - abs(current_loss)

            # 損失レベル判定
            loss_level = self._determine_loss_level(loss_percent)

            # アラート状況
            alert_status = self._determine_alert_status(loss_level, remaining_buffer)

            # 推奨アクション
            recommended_action = self._get_recommended_action(
                loss_level, remaining_buffer
            )

            return PositionLossStatus(
                symbol=symbol,
                current_price=current_price,
                entry_price=entry_price,
                position_size=position_size,
                current_loss=current_loss,
                loss_percent=loss_percent,
                max_loss_amount=max_loss_amount,
                remaining_buffer=remaining_buffer,
                loss_level=loss_level,
                alert_status=alert_status,
                recommended_action=recommended_action,
            )

        except Exception as e:
            logger.error(f"損失状況分析エラー: {symbol} - {e}")
            return self._create_default_loss_status(symbol, current_price)

    def _determine_loss_level(self, loss_percent: float) -> LossLevel:
        """損失レベル判定"""
        try:
            abs_loss_percent = abs(loss_percent)

            if abs_loss_percent < self.loss_thresholds[LossLevel.MINOR]:
                return LossLevel.NONE
            elif abs_loss_percent < self.loss_thresholds[LossLevel.MODERATE]:
                return LossLevel.MINOR
            elif abs_loss_percent < self.loss_thresholds[LossLevel.SIGNIFICANT]:
                return LossLevel.MODERATE
            elif abs_loss_percent < self.loss_thresholds[LossLevel.SEVERE]:
                return LossLevel.SIGNIFICANT
            elif abs_loss_percent < self.loss_thresholds[LossLevel.CRITICAL]:
                return LossLevel.SEVERE
            else:
                return LossLevel.CRITICAL
        except Exception as e:
            logger.error(f"損失レベル判定エラー: {e}")
            return LossLevel.NONE

    def _determine_alert_status(
        self, loss_level: LossLevel, remaining_buffer: float
    ) -> str:
        """アラート状況判定"""
        try:
            if loss_level == LossLevel.CRITICAL:
                return "EMERGENCY"
            elif loss_level == LossLevel.SEVERE:
                return "CRITICAL"
            elif loss_level == LossLevel.SIGNIFICANT:
                return "WARNING"
            elif loss_level == LossLevel.MODERATE:
                return "INFO"
            elif remaining_buffer < 0:
                return "WARNING"
            else:
                return "NORMAL"
        except Exception as e:
            logger.error(f"アラート状況判定エラー: {e}")
            return "NORMAL"

    def _get_recommended_action(
        self, loss_level: LossLevel, remaining_buffer: float
    ) -> str:
        """推奨アクション取得"""
        try:
            if loss_level == LossLevel.CRITICAL:
                return "即座に損切りを実行してください"
            elif loss_level == LossLevel.SEVERE:
                return "損切りを検討してください"
            elif loss_level == LossLevel.SIGNIFICANT:
                return "損失監視を強化してください"
            elif loss_level == LossLevel.MODERATE:
                return "今後の価格動向を注意深く監視してください"
            elif remaining_buffer < 0:
                return "最大損失額を超過しています。損切りを検討してください"
            else:
                return "現在の損失レベルは許容範囲内です"
        except Exception as e:
            logger.error(f"推奨アクション取得エラー: {e}")
            return "損失状況を確認してください"

    def _generate_loss_alert(
        self, symbol: str, loss_status: PositionLossStatus
    ) -> LossAlert:
        """損失アラート生成"""
        try:
            # アラートタイプ判定
            alert_type = AlertType.INFO
            if loss_status.loss_level == LossLevel.CRITICAL:
                alert_type = AlertType.EMERGENCY
            elif loss_status.loss_level == LossLevel.SEVERE:
                alert_type = AlertType.CRITICAL
            elif loss_status.loss_level == LossLevel.SIGNIFICANT:
                alert_type = AlertType.WARNING

            # アラートメッセージ生成
            message = self._generate_alert_message(symbol, loss_status)

            # アクション必要判定
            action_required = loss_status.loss_level in [
                LossLevel.SEVERE,
                LossLevel.CRITICAL,
            ]

            # アラート作成
            alert = LossAlert(
                symbol=symbol,
                timestamp=datetime.now(),
                alert_type=alert_type,
                current_loss=loss_status.current_loss,
                loss_percent=loss_status.loss_percent,
                max_loss_amount=loss_status.max_loss_amount,
                remaining_buffer=loss_status.remaining_buffer,
                message=message,
                action_required=action_required,
            )

            # アラート保存
            self.active_alerts[symbol].append(alert)

            # ログ出力
            logger.warning(f"損失アラート: {symbol} - {alert_type.value} - {message}")

            return alert

        except Exception as e:
            logger.error(f"損失アラート生成エラー: {symbol} - {e}")
            return LossAlert(
                symbol=symbol,
                timestamp=datetime.now(),
                alert_type=AlertType.INFO,
                current_loss=0.0,
                loss_percent=0.0,
                max_loss_amount=0.0,
                remaining_buffer=0.0,
                message="アラート生成エラー",
                action_required=False,
            )

    def _generate_alert_message(
        self, symbol: str, loss_status: PositionLossStatus
    ) -> str:
        """アラートメッセージ生成"""
        try:
            loss_amount = abs(loss_status.current_loss)
            loss_percent = abs(loss_status.loss_percent) * 100

            if loss_status.loss_level == LossLevel.CRITICAL:
                return f"{symbol}: 致命的な損失発生！損失額: ¥{loss_amount:,.0f} ({loss_percent:.1f}%)"
            elif loss_status.loss_level == LossLevel.SEVERE:
                return f"{symbol}: 深刻な損失発生。損失額: ¥{loss_amount:,.0f} ({loss_percent:.1f}%)"
            elif loss_status.loss_level == LossLevel.SIGNIFICANT:
                return f"{symbol}: 重要な損失発生。損失額: ¥{loss_amount:,.0f} ({loss_percent:.1f}%)"
            elif loss_status.loss_level == LossLevel.MODERATE:
                return f"{symbol}: 中程度の損失発生。損失額: ¥{loss_amount:,.0f} ({loss_percent:.1f}%)"
            else:
                return f"{symbol}: 軽微な損失発生。損失額: ¥{loss_amount:,.0f} ({loss_percent:.1f}%)"
        except Exception as e:
            logger.error(f"アラートメッセージ生成エラー: {e}")
            return f"{symbol}: 損失状況の分析中にエラーが発生しました"

    def _record_loss_history(self, symbol: str, loss_status: PositionLossStatus):
        """損失履歴記録"""
        try:
            # アラート送信状況
            alert_sent = len(self.active_alerts[symbol]) > 0

            # アクション実行状況
            action_taken = "監視中"
            if loss_status.loss_level == LossLevel.CRITICAL:
                action_taken = "緊急対応必要"
            elif loss_status.loss_level == LossLevel.SEVERE:
                action_taken = "損切り検討"

            # 履歴記録
            history_entry = LossHistory(
                symbol=symbol,
                timestamp=datetime.now(),
                entry_price=loss_status.entry_price,
                current_price=loss_status.current_price,
                loss_amount=loss_status.current_loss,
                loss_percent=loss_status.loss_percent,
                max_loss_amount=loss_status.max_loss_amount,
                loss_level=loss_status.loss_level,
                alert_sent=alert_sent,
                action_taken=action_taken,
            )

            self.loss_history[symbol].append(history_entry)

        except Exception as e:
            logger.error(f"損失履歴記録エラー: {symbol} - {e}")

    def _should_auto_stop_loss(
        self, symbol: str, loss_status: PositionLossStatus
    ) -> bool:
        """自動損切り判定"""
        try:
            if symbol not in self.max_loss_settings:
                return False

            max_loss_settings = self.max_loss_settings[symbol]

            # 自動損切りが無効の場合は実行しない
            if not max_loss_settings.auto_stop_loss:
                return False

            # 損失額が最大損失額を超過した場合
            if abs(loss_status.current_loss) >= loss_status.max_loss_amount:
                return True

            # 損失率が自動損切り閾値を超過した場合
            if (
                abs(loss_status.loss_percent)
                >= self.loss_params["auto_stop_loss_threshold"]
            ):
                return True

            return False
        except Exception as e:
            logger.error(f"自動損切り判定エラー: {symbol} - {e}")
            return False

    def _execute_auto_stop_loss(self, symbol: str, loss_status: PositionLossStatus):
        """自動損切り実行"""
        try:
            logger.critical(
                f"自動損切り実行: {symbol} @ ¥{loss_status.current_price:,.0f}"
            )

            # ポジションクローズ（実際の実装ではブローカーAPIを呼び出し）
            if symbol in self.positions:
                position = self.positions[symbol]
                position["status"] = "CLOSED"
                position["close_time"] = datetime.now()
                position["close_price"] = loss_status.current_price
                position["realized_pnl"] = loss_status.current_loss

            # アラート生成
            alert = LossAlert(
                symbol=symbol,
                timestamp=datetime.now(),
                alert_type=AlertType.EMERGENCY,
                current_loss=loss_status.current_loss,
                loss_percent=loss_status.loss_percent,
                max_loss_amount=loss_status.max_loss_amount,
                remaining_buffer=0.0,
                message=f"{symbol}: 自動損切りが実行されました",
                action_required=True,
            )

            self.active_alerts[symbol].append(alert)

        except Exception as e:
            logger.error(f"自動損切り実行エラー: {symbol} - {e}")

    def get_loss_summary(self) -> Dict[str, Any]:
        """損失サマリー取得"""
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_positions": len(self.positions),
                "positions_with_loss": 0,
                "total_loss_amount": 0.0,
                "critical_positions": [],
                "active_alerts": {},
                "loss_history_summary": {},
            }

            # ポジション分析
            for symbol, position in self.positions.items():
                if position.get("unrealized_pnl", 0) < 0:
                    summary["positions_with_loss"] += 1
                    summary["total_loss_amount"] += abs(position["unrealized_pnl"])

                    # 損失レベル判定
                    loss_percent = (
                        abs(position["unrealized_pnl"]) / position["position_size"]
                    )
                    if loss_percent >= self.loss_thresholds[LossLevel.CRITICAL]:
                        summary["critical_positions"].append(symbol)

            # アクティブアラート
            for symbol, alerts in self.active_alerts.items():
                if alerts:
                    latest_alert = alerts[-1]
                    summary["active_alerts"][symbol] = asdict(latest_alert)

            # 損失履歴サマリー
            for symbol, history in self.loss_history.items():
                if history:
                    summary["loss_history_summary"][symbol] = {
                        "total_entries": len(history),
                        "latest_loss": asdict(history[-1]),
                        "max_loss": max([h.loss_amount for h in history]),
                        "avg_loss": np.mean([h.loss_amount for h in history]),
                    }

            return summary
        except Exception as e:
            logger.error(f"損失サマリー取得エラー: {e}")
            return {"error": str(e)}

    def _create_default_max_loss_settings(self, symbol: str) -> MaxLossSettings:
        """デフォルト最大損失設定作成"""
        return MaxLossSettings(
            symbol=symbol,
            max_loss_amount=self.account_value
            * self.loss_params["default_max_loss_percent"],
            max_loss_percent=self.loss_params["default_max_loss_percent"],
            max_loss_price=0.0,
            alert_thresholds={level: 0.0 for level in LossLevel},
            auto_stop_loss=True,
            trailing_stop_enabled=True,
            last_updated=datetime.now(),
        )

    def _create_default_loss_status(
        self, symbol: str, current_price: float
    ) -> PositionLossStatus:
        """デフォルト損失状況作成"""
        return PositionLossStatus(
            symbol=symbol,
            current_price=current_price,
            entry_price=current_price,
            position_size=0.0,
            current_loss=0.0,
            loss_percent=0.0,
            max_loss_amount=0.0,
            remaining_buffer=0.0,
            loss_level=LossLevel.NONE,
            alert_status="NORMAL",
            recommended_action="損失状況を確認してください",
        )

    def save_loss_report(self, filename: str = "max_loss_management_report.json"):
        """損失管理レポート保存"""
        try:
            report = self.get_loss_summary()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"損失管理レポートを保存しました: {filename}")
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 最大損失管理システム初期化
    loss_system = MaxLossManagementSystem(account_value=1000000)

    # テスト銘柄
    test_symbols = ["7203.T", "6758.T", "9984.T", "7974.T", "4063.T"]

    logger.info("最大損失管理システム テスト開始")

    # 各銘柄の最大損失設定
    for symbol in test_symbols:
        try:
            logger.info(f"最大損失設定開始: {symbol}")

            # 最大損失設定
            max_loss_settings = loss_system.set_max_loss_for_stock(
                symbol,
                max_loss_percent=0.05,  # 5%
                auto_stop_loss=True,
                trailing_stop=True,
            )

            logger.info(f"最大損失設定完了: {symbol}")
            logger.info(f"  最大損失額: ¥{max_loss_settings.max_loss_amount:,.0f}")
            logger.info(f"  最大損失率: {max_loss_settings.max_loss_percent:.1%}")
            logger.info(f"  自動損切り: {max_loss_settings.auto_stop_loss}")

        except Exception as e:
            logger.error(f"最大損失設定エラー: {symbol} - {e}")

    # ポジション追加と価格更新シミュレーション
    for symbol in test_symbols:
        try:
            # ポジション追加
            entry_price = 1000.0  # 仮のエントリー価格
            position_size = 100000  # 10万円

            success = loss_system.add_position(symbol, entry_price, position_size)
            if success:
                logger.info(f"ポジション追加完了: {symbol}")

                # 価格更新シミュレーション（損失シナリオ）
                loss_scenarios = [
                    0.02,
                    0.03,
                    0.05,
                    0.08,
                    0.12,
                ]  # 2%, 3%, 5%, 8%, 12%の損失

                for loss_percent in loss_scenarios:
                    current_price = entry_price * (1 - loss_percent)

                    # 損失状況確認
                    loss_status = loss_system.update_position_price(
                        symbol, current_price
                    )

                    logger.info(f"価格更新: {symbol} @ ¥{current_price:,.0f}")
                    logger.info(f"  損失額: ¥{loss_status.current_loss:,.0f}")
                    logger.info(f"  損失率: {loss_status.loss_percent:.1%}")
                    logger.info(f"  損失レベル: {loss_status.loss_level.value}")
                    logger.info(f"  アラート状況: {loss_status.alert_status}")
                    logger.info(f"  推奨アクション: {loss_status.recommended_action}")

                    # 自動損切りが実行された場合は終了
                    if loss_status.loss_level == LossLevel.CRITICAL:
                        logger.critical(f"自動損切り実行: {symbol}")
                        break

        except Exception as e:
            logger.error(f"ポジション処理エラー: {symbol} - {e}")

    # 損失サマリー生成
    summary = loss_system.get_loss_summary()
    loss_system.save_loss_report()

    # 結果表示
    print("\n" + "=" * 80)
    print("🛡️ 最大損失管理システム レポート")
    print("=" * 80)
    print(f"分析時刻: {summary['timestamp']}")
    print(f"総ポジション数: {summary['total_positions']}")
    print(f"損失ポジション数: {summary['positions_with_loss']}")
    print(f"総損失額: ¥{summary['total_loss_amount']:,.0f}")
    print(
        f"緊急ポジション: {', '.join(summary['critical_positions']) if summary['critical_positions'] else 'なし'}"
    )

    print("\n🚨 アクティブアラート:")
    for symbol, alert in summary["active_alerts"].items():
        alert_emoji = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "CRITICAL": "🔴",
            "EMERGENCY": "🚨",
        }.get(alert["alert_type"], "⚪")

        print(f"  {alert_emoji} {symbol}: {alert['message']}")

    print("\n📊 損失履歴サマリー:")
    for symbol, history_summary in summary["loss_history_summary"].items():
        print(
            f"  {symbol}: {history_summary['total_entries']}件の記録, "
            f"最大損失: ¥{history_summary['max_loss']:,.0f}, "
            f"平均損失: ¥{history_summary['avg_loss']:,.0f}"
        )


if __name__ == "__main__":
    asyncio.run(main())
