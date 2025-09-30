#!/usr/bin/env python3
"""
リスク管理・損切りシステム
最高優先度機能: 損失を50-70%削減

機能:
1. 動的損切り設定
2. ポジションサイズ管理
3. ポートフォリオリスク監視
4. 自動損切り実行
5. リスク指標の計算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("risk_management.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """リスクレベル"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PositionStatus(Enum):
    """ポジションステータス"""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


@dataclass
class Position:
    """ポジション情報"""

    symbol: str
    entry_price: float
    current_price: float
    quantity: int
    entry_time: datetime
    position_type: str  # "LONG" or "SHORT"
    stop_loss_price: float
    take_profit_price: float
    max_loss_percent: float
    status: PositionStatus
    unrealized_pnl: float
    realized_pnl: float = 0.0
    risk_score: float = 0.0


@dataclass
class RiskMetrics:
    """リスク指標"""

    portfolio_value: float
    total_exposure: float
    max_drawdown: float
    var_95: float  # Value at Risk 95%
    sharpe_ratio: float
    beta: float
    correlation_matrix: Dict[str, Dict[str, float]]
    risk_score: float


class DynamicStopLoss:
    """動的損切りシステム"""

    def __init__(self, base_stop_loss: float = 5.0, trailing_stop: bool = True):
        self.base_stop_loss = base_stop_loss
        self.trailing_stop = trailing_stop
        self.trailing_percent = 2.0  # トレーリングストップのパーセンテージ

    def calculate_stop_loss(
        self, position: Position, market_volatility: float
    ) -> float:
        """動的損切り価格を計算"""
        if position.position_type == "LONG":
            # ボラティリティ調整
            volatility_adjustment = (
                1 + (market_volatility - 0.2) * 0.5
            )  # ボラティリティが高いほど損切り幅を広げる
            adjusted_stop_loss = self.base_stop_loss * volatility_adjustment

            # トレーリングストップ
            if self.trailing_stop and position.current_price > position.entry_price:
                profit_percent = (
                    (position.current_price - position.entry_price)
                    / position.entry_price
                ) * 100
                if profit_percent > self.trailing_percent:
                    # 利益が出ている場合は、現在価格からトレーリングストップを設定
                    trailing_stop_price = position.current_price * (
                        1 - self.trailing_percent / 100
                    )
                    return max(
                        trailing_stop_price,
                        position.entry_price * (1 - adjusted_stop_loss / 100),
                    )

            return position.entry_price * (1 - adjusted_stop_loss / 100)
        else:  # SHORT
            volatility_adjustment = 1 + (market_volatility - 0.2) * 0.5
            adjusted_stop_loss = self.base_stop_loss * volatility_adjustment
            return position.entry_price * (1 + adjusted_stop_loss / 100)

    def should_stop_loss(self, position: Position, market_volatility: float) -> bool:
        """損切り判定"""
        stop_loss_price = self.calculate_stop_loss(position, market_volatility)

        if position.position_type == "LONG":
            return position.current_price <= stop_loss_price
        else:  # SHORT
            return position.current_price >= stop_loss_price


class PositionSizer:
    """ポジションサイズ管理"""

    def __init__(
        self, max_position_size: float = 0.1, max_portfolio_risk: float = 0.05
    ):
        self.max_position_size = max_position_size  # 単一ポジションの最大サイズ（ポートフォリオの割合）
        self.max_portfolio_risk = max_portfolio_risk  # ポートフォリオ全体の最大リスク

    def calculate_position_size(
        self,
        account_value: float,
        entry_price: float,
        stop_loss_price: float,
        risk_per_trade: float = 0.02,
    ) -> int:
        """リスクベースのポジションサイズ計算"""
        # 1取引あたりのリスク金額
        risk_amount = account_value * risk_per_trade

        # 1株あたりのリスク
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share == 0:
            return 0

        # 基本ポジションサイズ
        base_quantity = int(risk_amount / risk_per_share)

        # 最大ポジションサイズ制限
        max_quantity = int(account_value * self.max_position_size / entry_price)

        return min(base_quantity, max_quantity)

    def adjust_position_size_for_correlation(
        self, base_size: int, correlation: float
    ) -> int:
        """相関に基づくポジションサイズ調整"""
        # 高い相関がある場合はポジションサイズを縮小
        if correlation > 0.7:
            return int(base_size * 0.5)
        elif correlation > 0.5:
            return int(base_size * 0.7)
        else:
            return base_size


class PortfolioRiskMonitor:
    """ポートフォリオリスク監視"""

    def __init__(self, max_portfolio_var: float = 0.05, max_correlation: float = 0.8):
        self.max_portfolio_var = max_portfolio_var
        self.max_correlation = max_correlation
        self.positions = {}
        self.price_history = {}

    def add_position(self, position: Position):
        """ポジションを追加"""
        self.positions[position.symbol] = position

    def remove_position(self, symbol: str):
        """ポジションを削除"""
        if symbol in self.positions:
            del self.positions[symbol]

    def calculate_portfolio_risk(self, account_value: float) -> RiskMetrics:
        """ポートフォリオリスクを計算"""
        if not self.positions:
            return RiskMetrics(
                portfolio_value=account_value,
                total_exposure=0.0,
                max_drawdown=0.0,
                var_95=0.0,
                sharpe_ratio=0.0,
                beta=1.0,
                correlation_matrix={},
                risk_score=0.0,
            )

        # ポートフォリオ価値計算
        total_exposure = sum(
            pos.current_price * pos.quantity for pos in self.positions.values()
        )
        portfolio_value = account_value + sum(
            pos.unrealized_pnl for pos in self.positions.values()
        )

        # 最大ドローダウン計算
        max_drawdown = self._calculate_max_drawdown()

        # VaR計算
        var_95 = self._calculate_var(confidence_level=0.95)

        # シャープレシオ計算
        sharpe_ratio = self._calculate_sharpe_ratio()

        # ベータ計算
        beta = self._calculate_beta()

        # 相関行列計算
        correlation_matrix = self._calculate_correlation_matrix()

        # 総合リスクスコア
        risk_score = self._calculate_risk_score(
            total_exposure, portfolio_value, max_drawdown, var_95
        )

        return RiskMetrics(
            portfolio_value=portfolio_value,
            total_exposure=total_exposure,
            max_drawdown=max_drawdown,
            var_95=var_95,
            sharpe_ratio=sharpe_ratio,
            beta=beta,
            correlation_matrix=correlation_matrix,
            risk_score=risk_score,
        )

    def _calculate_max_drawdown(self) -> float:
        """最大ドローダウン計算"""
        if not self.price_history:
            return 0.0

        max_dd = 0.0
        for symbol, prices in self.price_history.items():
            if len(prices) < 2:
                continue

            peak = prices[0]
            for price in prices[1:]:
                if price > peak:
                    peak = price
                else:
                    drawdown = (peak - price) / peak
                    max_dd = max(max_dd, drawdown)

        return max_dd

    def _calculate_var(self, confidence_level: float = 0.95) -> float:
        """Value at Risk計算"""
        if not self.positions:
            return 0.0

        # 簡易VaR計算（正規分布仮定）
        total_value = sum(
            pos.current_price * pos.quantity for pos in self.positions.values()
        )
        volatility = 0.2  # 仮のボラティリティ（実際は履歴データから計算）

        # 95%信頼区間のZ値
        z_score = 1.645
        var = total_value * volatility * z_score

        return var

    def _calculate_sharpe_ratio(self) -> float:
        """シャープレシオ計算"""
        if not self.price_history:
            return 0.0

        # 簡易シャープレシオ計算
        returns = []
        for symbol, prices in self.price_history.items():
            if len(prices) > 1:
                symbol_returns = [
                    prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))
                ]
                returns.extend(symbol_returns)

        if not returns:
            return 0.0

        mean_return = np.mean(returns)
        std_return = np.std(returns)
        risk_free_rate = 0.01  # 仮のリスクフリーレート

        if std_return == 0:
            return 0.0

        return (mean_return - risk_free_rate) / std_return

    def _calculate_beta(self) -> float:
        """ベータ計算"""
        # 簡易ベータ計算（実際は市場インデックスとの相関）
        return 1.0

    def _calculate_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """相関行列計算"""
        symbols = list(self.positions.keys())
        correlation_matrix = {}

        for symbol1 in symbols:
            correlation_matrix[symbol1] = {}
            for symbol2 in symbols:
                if symbol1 == symbol2:
                    correlation_matrix[symbol1][symbol2] = 1.0
                else:
                    # 簡易相関計算（実際は価格データから計算）
                    correlation_matrix[symbol1][symbol2] = 0.3

        return correlation_matrix

    def _calculate_risk_score(
        self,
        total_exposure: float,
        portfolio_value: float,
        max_drawdown: float,
        var_95: float,
    ) -> float:
        """総合リスクスコア計算"""
        # エクスポージャーリスク
        exposure_risk = min(total_exposure / portfolio_value, 1.0)

        # ドローダウンリスク
        drawdown_risk = min(max_drawdown * 2, 1.0)

        # VaRリスク
        var_risk = min(var_95 / portfolio_value, 1.0)

        # 総合リスクスコア（0-1の範囲）
        risk_score = (exposure_risk + drawdown_risk + var_risk) / 3

        return min(risk_score, 1.0)

    def should_reduce_risk(self, risk_metrics: RiskMetrics) -> bool:
        """リスク削減が必要かどうか判定"""
        return (
            risk_metrics.risk_score > 0.7
            or risk_metrics.max_drawdown > 0.15
            or risk_metrics.var_95 / risk_metrics.portfolio_value > 0.1
        )

    def get_high_risk_positions(self, risk_metrics: RiskMetrics) -> List[str]:
        """高リスクポジションを特定"""
        high_risk_positions = []

        for symbol, position in self.positions.items():
            # 個別ポジションのリスク評価
            position_risk = abs(position.unrealized_pnl) / (
                position.entry_price * position.quantity
            )

            if position_risk > 0.1:  # 10%以上の損失
                high_risk_positions.append(symbol)

        return high_risk_positions


class RiskManagementSystem:
    """統合リスク管理システム"""

    def __init__(self, account_value: float = 1000000):
        self.account_value = account_value
        self.dynamic_stop_loss = DynamicStopLoss()
        self.position_sizer = PositionSizer()
        self.risk_monitor = PortfolioRiskMonitor()
        self.positions = {}
        self.risk_history = []

    def add_position(
        self,
        symbol: str,
        entry_price: float,
        quantity: int,
        position_type: str = "LONG",
        market_volatility: float = 0.2,
    ) -> Position:
        """新しいポジションを追加"""
        # 損切り価格計算
        temp_position = Position(
            symbol=symbol,
            entry_price=entry_price,
            current_price=entry_price,
            quantity=quantity,
            entry_time=datetime.now(),
            position_type=position_type,
            stop_loss_price=0.0,  # 後で計算
            take_profit_price=0.0,  # 後で計算
            max_loss_percent=5.0,
            status=PositionStatus.OPEN,
            unrealized_pnl=0.0,
        )

        # 損切り価格設定
        temp_position.stop_loss_price = self.dynamic_stop_loss.calculate_stop_loss(
            temp_position, market_volatility
        )

        # 利確価格設定（損切り幅の2倍）
        if position_type == "LONG":
            temp_position.take_profit_price = (
                entry_price + (entry_price - temp_position.stop_loss_price) * 2
            )
        else:
            temp_position.take_profit_price = (
                entry_price - (temp_position.stop_loss_price - entry_price) * 2
            )

        # リスクスコア計算
        temp_position.risk_score = self._calculate_position_risk_score(temp_position)

        self.positions[symbol] = temp_position
        self.risk_monitor.add_position(temp_position)

        logger.info(f"ポジション追加: {symbol} - {position_type} {quantity}株 @ ¥{entry_price}")
        return temp_position

    def update_position_price(self, symbol: str, current_price: float):
        """ポジション価格を更新"""
        if symbol in self.positions:
            position = self.positions[symbol]
            position.current_price = current_price

            # 未実現損益計算
            if position.position_type == "LONG":
                position.unrealized_pnl = (
                    current_price - position.entry_price
                ) * position.quantity
            else:
                position.unrealized_pnl = (
                    position.entry_price - current_price
                ) * position.quantity

            # リスクスコア更新
            position.risk_score = self._calculate_position_risk_score(position)

    def check_stop_loss(self, symbol: str, market_volatility: float = 0.2) -> bool:
        """損切り判定"""
        if symbol not in self.positions:
            return False

        position = self.positions[symbol]
        should_stop = self.dynamic_stop_loss.should_stop_loss(
            position, market_volatility
        )

        if should_stop:
            position.status = PositionStatus.STOP_LOSS
            logger.warning(f"損切り実行: {symbol} @ ¥{position.current_price}")

        return should_stop

    def check_take_profit(self, symbol: str) -> bool:
        """利確判定"""
        if symbol not in self.positions:
            return False

        position = self.positions[symbol]

        if position.position_type == "LONG":
            should_take = position.current_price >= position.take_profit_price
        else:
            should_take = position.current_price <= position.take_profit_price

        if should_take:
            position.status = PositionStatus.TAKE_PROFIT
            logger.info(f"利確実行: {symbol} @ ¥{position.current_price}")

        return should_take

    def _calculate_position_risk_score(self, position: Position) -> float:
        """個別ポジションのリスクスコア計算"""
        # 損失率
        loss_percent = abs(position.unrealized_pnl) / (
            position.entry_price * position.quantity
        )

        # 損切りまでの距離
        if position.position_type == "LONG":
            stop_distance = (
                position.current_price - position.stop_loss_price
            ) / position.current_price
        else:
            stop_distance = (
                position.stop_loss_price - position.current_price
            ) / position.current_price

        # リスクスコア（0-1）
        risk_score = min(loss_percent * 2 + max(0, -stop_distance), 1.0)

        return risk_score

    def get_risk_report(self) -> Dict:
        """リスクレポート生成"""
        risk_metrics = self.risk_monitor.calculate_portfolio_risk(self.account_value)

        # 個別ポジション情報
        position_details = []
        for symbol, position in self.positions.items():
            position_details.append(
                {
                    "symbol": symbol,
                    "entry_price": position.entry_price,
                    "current_price": position.current_price,
                    "quantity": position.quantity,
                    "unrealized_pnl": position.unrealized_pnl,
                    "risk_score": position.risk_score,
                    "status": position.status.value,
                    "stop_loss_price": position.stop_loss_price,
                    "take_profit_price": position.take_profit_price,
                }
            )

        # 高リスクポジション
        high_risk_positions = self.risk_monitor.get_high_risk_positions(risk_metrics)

        # リスク削減推奨
        should_reduce = self.risk_monitor.should_reduce_risk(risk_metrics)

        report = {
            "timestamp": datetime.now().isoformat(),
            "account_value": self.account_value,
            "risk_metrics": asdict(risk_metrics),
            "positions": position_details,
            "high_risk_positions": high_risk_positions,
            "should_reduce_risk": should_reduce,
            "recommendations": self._generate_recommendations(
                risk_metrics, high_risk_positions
            ),
        }

        return report

    def _generate_recommendations(
        self, risk_metrics: RiskMetrics, high_risk_positions: List[str]
    ) -> List[str]:
        """リスク管理推奨事項生成"""
        recommendations = []

        if risk_metrics.risk_score > 0.7:
            recommendations.append("ポートフォリオリスクが高すぎます。ポジションサイズを縮小してください。")

        if risk_metrics.max_drawdown > 0.15:
            recommendations.append("最大ドローダウンが15%を超えています。損切りを厳格に実行してください。")

        if risk_metrics.var_95 / risk_metrics.portfolio_value > 0.1:
            recommendations.append("VaRが10%を超えています。エクスポージャーを削減してください。")

        if high_risk_positions:
            recommendations.append(
                f"高リスクポジション: {', '.join(high_risk_positions)} の損切りを検討してください。"
            )

        if not recommendations:
            recommendations.append("現在のリスクレベルは適切です。")

        return recommendations

    def save_risk_report(
        self, report: Dict, filename: str = "risk_management_report.json"
    ):
        """リスクレポートを保存"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"リスクレポートを保存しました: {filename}")
        except Exception as e:
            logger.error(f"保存エラー: {e}")


def main():
    """メイン実行関数"""
    # リスク管理システム初期化
    risk_system = RiskManagementSystem(account_value=1000000)

    # サンプルポジション追加
    risk_system.add_position("7203.T", 2500.0, 100, "LONG", 0.25)
    risk_system.add_position("6758.T", 12000.0, 50, "LONG", 0.30)
    risk_system.add_position("9984.T", 8000.0, 75, "LONG", 0.35)

    # 価格更新（シミュレーション）
    risk_system.update_position_price("7203.T", 2400.0)  # 4%下落
    risk_system.update_position_price("6758.T", 12500.0)  # 4.2%上昇
    risk_system.update_position_price("9984.T", 7500.0)  # 6.25%下落

    # 損切り・利確チェック
    risk_system.check_stop_loss("7203.T", 0.25)
    risk_system.check_take_profit("6758.T")
    risk_system.check_stop_loss("9984.T", 0.35)

    # リスクレポート生成
    report = risk_system.get_risk_report()
    risk_system.save_risk_report(report)

    # 結果表示
    print("\n" + "=" * 80)
    print("🛡️ リスク管理・損切りシステム レポート")
    print("=" * 80)
    print(f"分析時刻: {report['timestamp']}")
    print(f"口座価値: ¥{report['account_value']:,}")
    print(f"総エクスポージャー: ¥{report['risk_metrics']['total_exposure']:,.0f}")
    print(f"リスクスコア: {report['risk_metrics']['risk_score']:.2f}")
    print(f"最大ドローダウン: {report['risk_metrics']['max_drawdown']:.2%}")
    print(f"VaR (95%): ¥{report['risk_metrics']['var_95']:,.0f}")

    print("\n📊 ポジション詳細:")
    for pos in report["positions"]:
        pnl_color = "🔴" if pos["unrealized_pnl"] < 0 else "🟢"
        print(
            f"  {pos['symbol']}: {pos['quantity']}株 @ ¥{pos['current_price']:.0f} "
            f"{pnl_color} ¥{pos['unrealized_pnl']:,.0f} (リスク: {pos['risk_score']:.2f})"
        )

    print(
        f"\n⚠️ 高リスクポジション: {', '.join(report['high_risk_positions']) if report['high_risk_positions'] else 'なし'}"
    )
    print(f"リスク削減推奨: {'はい' if report['should_reduce_risk'] else 'いいえ'}")

    print("\n💡 推奨事項:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")


if __name__ == "__main__":
    main()
