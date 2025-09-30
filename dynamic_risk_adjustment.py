#!/usr/bin/env python3
"""
感情分析に基づく動的リスク調整システム
感情分析結果に基づいてリスクパラメータを動的に調整

機能:
- 感情分析に基づくリスク調整
- 動的ポジションサイジング
- 感情ベースのストップロス調整
- リスク制限の自動調整
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
from collections import deque

warnings.filterwarnings("ignore")

# 既存システムのインポート
try:
    from realtime_sentiment_metrics import RealtimeSentimentMetricsGenerator, MetricType
    from sentiment_analysis_system import SentimentTradingSystem, SentimentType
    from risk_management_system import RiskManagementSystem
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("dynamic_risk_adjustment.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RiskAdjustmentType(Enum):
    """リスク調整タイプの定義"""

    POSITION_SIZE = "position_size"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    LEVERAGE = "leverage"
    MAX_DRAWDOWN = "max_drawdown"


@dataclass
class RiskAdjustment:
    """リスク調整"""

    timestamp: datetime
    symbol: str
    adjustment_type: RiskAdjustmentType
    original_value: float
    adjusted_value: float
    adjustment_factor: float
    sentiment_score: float
    confidence: float
    reason: str


@dataclass
class PositionRiskProfile:
    """ポジションリスクプロファイル"""

    symbol: str
    current_position: float
    max_position: float
    stop_loss: float
    take_profit: float
    leverage: float
    risk_per_trade: float
    max_drawdown: float
    sentiment_adjustment: float


class DynamicRiskAdjustmentSystem:
    """動的リスク調整システム"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sentiment_metrics_generator = None
        self.sentiment_system = None
        self.risk_system = None

        # リスク調整パラメータ
        self.base_risk_params = {
            "max_position_size": 0.1,  # 最大ポジションサイズ（資産の10%）
            "base_stop_loss": 0.02,  # ベースストップロス（2%）
            "base_take_profit": 0.04,  # ベーステイクプロフィット（4%）
            "max_leverage": 2.0,  # 最大レバレッジ
            "max_drawdown": 0.15,  # 最大ドローダウン（15%）
            "risk_per_trade": 0.02,  # トレードあたりのリスク（2%）
        }

        # 感情ベース調整係数
        self.sentiment_adjustment_factors = {
            "positive_sentiment": {
                "position_size": 1.2,  # ポジティブ感情時はポジションサイズを増加
                "stop_loss": 0.8,  # ストップロスを緩和
                "take_profit": 1.3,  # テイクプロフィットを拡大
                "leverage": 1.1,  # レバレッジを若干増加
            },
            "negative_sentiment": {
                "position_size": 0.6,  # ネガティブ感情時はポジションサイズを減少
                "stop_loss": 1.3,  # ストップロスを厳格化
                "take_profit": 0.7,  # テイクプロフィットを縮小
                "leverage": 0.8,  # レバレッジを減少
            },
            "neutral_sentiment": {
                "position_size": 1.0,  # ニュートラル感情時はベース値を使用
                "stop_loss": 1.0,
                "take_profit": 1.0,
                "leverage": 1.0,
            },
        }

        # 調整履歴
        self.adjustment_history = deque(maxlen=1000)
        self.position_profiles = {}

        self._initialize_systems()

    def _initialize_systems(self):
        """システムの初期化"""
        try:
            self.sentiment_metrics_generator = RealtimeSentimentMetricsGenerator()
            self.sentiment_system = SentimentTradingSystem()
            logger.info("動的リスク調整システムの初期化に成功")
        except Exception as e:
            logger.error(f"システムの初期化に失敗: {e}")

    async def adjust_risk_parameters(
        self, symbol: str, current_position: float = 0.0
    ) -> PositionRiskProfile:
        """リスクパラメータの動的調整"""
        try:
            # 現在の感情指標を取得
            sentiment_metrics = await self._get_current_sentiment_metrics(symbol)

            # 感情スコアの計算
            sentiment_score = self._calculate_overall_sentiment(sentiment_metrics)

            # 感情タイプの判定
            sentiment_type = self._determine_sentiment_type(sentiment_score)

            # リスク調整の計算
            adjustments = self._calculate_risk_adjustments(
                symbol, sentiment_type, sentiment_score
            )

            # ポジションリスクプロファイルの作成
            risk_profile = self._create_risk_profile(
                symbol, current_position, adjustments, sentiment_score
            )

            # 調整履歴の記録
            self._record_adjustments(symbol, adjustments, sentiment_score)

            # ポジションプロファイルの更新
            self.position_profiles[symbol] = risk_profile

            return risk_profile

        except Exception as e:
            logger.error(f"リスクパラメータの調整に失敗: {e}")
            return self._create_default_risk_profile(symbol, current_position)

    async def _get_current_sentiment_metrics(self, symbol: str) -> List[Dict[str, Any]]:
        """現在の感情指標を取得"""
        try:
            if self.sentiment_metrics_generator:
                metrics = (
                    await self.sentiment_metrics_generator.generate_realtime_metrics(
                        [symbol]
                    )
                )
                return [asdict(metric) for metric in metrics]
            else:
                # フォールバック: 基本的な感情分析
                return await self._fallback_sentiment_analysis(symbol)
        except Exception as e:
            logger.error(f"感情指標の取得に失敗: {e}")
            return []

    async def _fallback_sentiment_analysis(self, symbol: str) -> List[Dict[str, Any]]:
        """フォールバック感情分析"""
        try:
            # 価格ベースの簡単な感情分析
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")

            if len(hist) < 2:
                return []

            # 価格変化率ベースの感情スコア
            price_change = (hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist[
                "Close"
            ].iloc[-2]
            sentiment_score = np.tanh(price_change * 10)

            return [
                {
                    "metric_type": "sentiment_score",
                    "value": sentiment_score,
                    "confidence": 0.5,
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        except Exception as e:
            logger.error(f"フォールバック感情分析に失敗: {e}")
            return []

    def _calculate_overall_sentiment(
        self, sentiment_metrics: List[Dict[str, Any]]
    ) -> float:
        """総合感情スコアの計算"""
        try:
            if not sentiment_metrics:
                return 0.0

            # 感情スコアの重み付き平均
            sentiment_scores = []
            confidences = []

            for metric in sentiment_metrics:
                if metric.get("metric_type") == "sentiment_score":
                    sentiment_scores.append(metric.get("value", 0.0))
                    confidences.append(metric.get("confidence", 0.5))

            if not sentiment_scores:
                return 0.0

            # 信頼度で重み付き平均
            if confidences:
                weighted_sentiment = np.average(sentiment_scores, weights=confidences)
            else:
                weighted_sentiment = np.mean(sentiment_scores)

            return float(weighted_sentiment)

        except Exception as e:
            logger.error(f"総合感情スコアの計算に失敗: {e}")
            return 0.0

    def _determine_sentiment_type(self, sentiment_score: float) -> str:
        """感情タイプの判定"""
        if sentiment_score > 0.2:
            return "positive_sentiment"
        elif sentiment_score < -0.2:
            return "negative_sentiment"
        else:
            return "neutral_sentiment"

    def _calculate_risk_adjustments(
        self, symbol: str, sentiment_type: str, sentiment_score: float
    ) -> Dict[str, float]:
        """リスク調整の計算"""
        try:
            base_factors = self.sentiment_adjustment_factors.get(
                sentiment_type, self.sentiment_adjustment_factors["neutral_sentiment"]
            )

            # 感情スコアの強度に基づく調整
            sentiment_intensity = abs(sentiment_score)
            intensity_multiplier = 0.5 + (sentiment_intensity * 0.5)  # 0.5-1.0の範囲

            adjustments = {}
            for param, base_factor in base_factors.items():
                # 感情強度に基づく調整
                adjusted_factor = base_factor * intensity_multiplier

                # 極端な調整を制限
                adjusted_factor = max(0.3, min(2.0, adjusted_factor))

                adjustments[param] = adjusted_factor

            return adjustments

        except Exception as e:
            logger.error(f"リスク調整の計算に失敗: {e}")
            return self.sentiment_adjustment_factors["neutral_sentiment"]

    def _create_risk_profile(
        self,
        symbol: str,
        current_position: float,
        adjustments: Dict[str, float],
        sentiment_score: float,
    ) -> PositionRiskProfile:
        """リスクプロファイルの作成"""
        try:
            # ベースパラメータの取得
            base_params = self.base_risk_params.copy()

            # 調整の適用
            adjusted_position_size = base_params["max_position_size"] * adjustments.get(
                "position_size", 1.0
            )
            adjusted_stop_loss = base_params["base_stop_loss"] * adjustments.get(
                "stop_loss", 1.0
            )
            adjusted_take_profit = base_params["base_take_profit"] * adjustments.get(
                "take_profit", 1.0
            )
            adjusted_leverage = min(
                base_params["max_leverage"] * adjustments.get("leverage", 1.0),
                base_params["max_leverage"],
            )

            # 感情調整係数の計算
            sentiment_adjustment = sentiment_score * 0.1  # 感情スコアの10%を調整に使用

            return PositionRiskProfile(
                symbol=symbol,
                current_position=current_position,
                max_position=adjusted_position_size,
                stop_loss=adjusted_stop_loss,
                take_profit=adjusted_take_profit,
                leverage=adjusted_leverage,
                risk_per_trade=base_params["risk_per_trade"],
                max_drawdown=base_params["max_drawdown"],
                sentiment_adjustment=sentiment_adjustment,
            )

        except Exception as e:
            logger.error(f"リスクプロファイルの作成に失敗: {e}")
            return self._create_default_risk_profile(symbol, current_position)

    def _create_default_risk_profile(
        self, symbol: str, current_position: float
    ) -> PositionRiskProfile:
        """デフォルトリスクプロファイルの作成"""
        return PositionRiskProfile(
            symbol=symbol,
            current_position=current_position,
            max_position=self.base_risk_params["max_position_size"],
            stop_loss=self.base_risk_params["base_stop_loss"],
            take_profit=self.base_risk_params["base_take_profit"],
            leverage=1.0,
            risk_per_trade=self.base_risk_params["risk_per_trade"],
            max_drawdown=self.base_risk_params["max_drawdown"],
            sentiment_adjustment=0.0,
        )

    def _record_adjustments(
        self, symbol: str, adjustments: Dict[str, float], sentiment_score: float
    ):
        """調整履歴の記録"""
        try:
            timestamp = datetime.now()

            for param, factor in adjustments.items():
                adjustment = RiskAdjustment(
                    timestamp=timestamp,
                    symbol=symbol,
                    adjustment_type=RiskAdjustmentType(param),
                    original_value=self.base_risk_params.get(param, 1.0),
                    adjusted_value=self.base_risk_params.get(param, 1.0) * factor,
                    adjustment_factor=factor,
                    sentiment_score=sentiment_score,
                    confidence=0.8,  # デフォルト信頼度
                    reason=f"感情分析に基づく調整 (スコア: {sentiment_score:.2f})",
                )

                self.adjustment_history.append(adjustment)

        except Exception as e:
            logger.error(f"調整履歴の記録に失敗: {e}")

    def get_adjustment_summary(self, symbol: str = None) -> Dict[str, Any]:
        """調整サマリーの取得"""
        try:
            if symbol:
                adjustments = [a for a in self.adjustment_history if a.symbol == symbol]
            else:
                adjustments = list(self.adjustment_history)

            if not adjustments:
                return {"message": "調整履歴がありません"}

            # 最新の調整を取得
            latest_adjustments = {}
            for adj in adjustments:
                if adj.symbol not in latest_adjustments:
                    latest_adjustments[adj.symbol] = {}
                latest_adjustments[adj.symbol][adj.adjustment_type.value] = {
                    "original_value": adj.original_value,
                    "adjusted_value": adj.adjusted_value,
                    "adjustment_factor": adj.adjustment_factor,
                    "sentiment_score": adj.sentiment_score,
                    "reason": adj.reason,
                    "timestamp": adj.timestamp.isoformat(),
                }

            return latest_adjustments

        except Exception as e:
            logger.error(f"調整サマリーの取得に失敗: {e}")
            return {"error": str(e)}

    def get_position_risk_profile(self, symbol: str) -> Optional[PositionRiskProfile]:
        """ポジションリスクプロファイルの取得"""
        return self.position_profiles.get(symbol)

    def calculate_position_size(
        self, symbol: str, account_balance: float, current_price: float
    ) -> float:
        """感情分析に基づくポジションサイズの計算"""
        try:
            risk_profile = self.get_position_risk_profile(symbol)
            if not risk_profile:
                # デフォルト計算
                return account_balance * self.base_risk_params["max_position_size"]

            # 感情調整を適用
            base_position_size = account_balance * risk_profile.max_position
            sentiment_adjustment = 1.0 + risk_profile.sentiment_adjustment

            adjusted_position_size = base_position_size * sentiment_adjustment

            # 最大値の制限
            max_position = (
                account_balance * self.base_risk_params["max_position_size"] * 2.0
            )
            return min(adjusted_position_size, max_position)

        except Exception as e:
            logger.error(f"ポジションサイズの計算に失敗: {e}")
            return account_balance * self.base_risk_params["max_position_size"]

    def calculate_stop_loss(self, symbol: str, entry_price: float) -> float:
        """感情分析に基づくストップロスの計算"""
        try:
            risk_profile = self.get_position_risk_profile(symbol)
            if not risk_profile:
                # デフォルト計算
                return entry_price * (1 - self.base_risk_params["base_stop_loss"])

            # 感情調整を適用
            base_stop_loss = entry_price * (1 - risk_profile.stop_loss)
            sentiment_adjustment = 1.0 - (risk_profile.sentiment_adjustment * 0.1)

            adjusted_stop_loss = base_stop_loss * sentiment_adjustment

            # 最小値の制限（価格の5%以上）
            min_stop_loss = entry_price * 0.95
            return max(adjusted_stop_loss, min_stop_loss)

        except Exception as e:
            logger.error(f"ストップロスの計算に失敗: {e}")
            return entry_price * (1 - self.base_risk_params["base_stop_loss"])

    def calculate_take_profit(self, symbol: str, entry_price: float) -> float:
        """感情分析に基づくテイクプロフィットの計算"""
        try:
            risk_profile = self.get_position_risk_profile(symbol)
            if not risk_profile:
                # デフォルト計算
                return entry_price * (1 + self.base_risk_params["base_take_profit"])

            # 感情調整を適用
            base_take_profit = entry_price * (1 + risk_profile.take_profit)
            sentiment_adjustment = 1.0 + (risk_profile.sentiment_adjustment * 0.1)

            adjusted_take_profit = base_take_profit * sentiment_adjustment

            return adjusted_take_profit

        except Exception as e:
            logger.error(f"テイクプロフィットの計算に失敗: {e}")
            return entry_price * (1 + self.base_risk_params["base_take_profit"])

    def should_adjust_position(self, symbol: str, current_sentiment: float) -> bool:
        """ポジション調整の必要性判定"""
        try:
            risk_profile = self.get_position_risk_profile(symbol)
            if not risk_profile:
                return False

            # 感情変化の閾値
            sentiment_change_threshold = 0.3

            # 現在の感情と前回の感情の差を計算
            if hasattr(risk_profile, "last_sentiment"):
                sentiment_change = abs(current_sentiment - risk_profile.last_sentiment)
                return sentiment_change > sentiment_change_threshold

            return True  # 初回は調整

        except Exception as e:
            logger.error(f"ポジション調整判定に失敗: {e}")
            return False

    def get_risk_adjustment_recommendations(self, symbol: str) -> List[str]:
        """リスク調整の推奨事項を取得"""
        try:
            risk_profile = self.get_position_risk_profile(symbol)
            if not risk_profile:
                return ["リスクプロファイルが見つかりません"]

            recommendations = []

            # 感情調整に基づく推奨事項
            if risk_profile.sentiment_adjustment > 0.1:
                recommendations.append("ポジティブ感情が検出されています。ポジションサイズを増加することを検討してください。")
            elif risk_profile.sentiment_adjustment < -0.1:
                recommendations.append("ネガティブ感情が検出されています。リスクを削減することを検討してください。")

            # レバレッジの推奨
            if risk_profile.leverage > 1.5:
                recommendations.append("高いレバレッジが設定されています。リスク管理に注意してください。")

            # ストップロスの推奨
            if risk_profile.stop_loss > 0.05:
                recommendations.append("ストップロスが緩い設定です。リスク管理を強化することを検討してください。")

            return recommendations

        except Exception as e:
            logger.error(f"推奨事項の取得に失敗: {e}")
            return ["エラーが発生しました"]


async def main():
    """メイン関数"""
    # 動的リスク調整システムの初期化
    risk_system = DynamicRiskAdjustmentSystem()

    # テストシンボル
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]

    # 各シンボルのリスク調整を実行
    for symbol in symbols:
        logger.info(f"シンボル {symbol} のリスク調整を実行中...")

        try:
            # リスクパラメータの調整
            risk_profile = await risk_system.adjust_risk_parameters(symbol)

            logger.info(f"リスクプロファイル: {asdict(risk_profile)}")

            # ポジションサイズの計算例
            account_balance = 100000  # $100,000
            current_price = 150.0  # 仮の価格

            position_size = risk_system.calculate_position_size(
                symbol, account_balance, current_price
            )
            stop_loss = risk_system.calculate_stop_loss(symbol, current_price)
            take_profit = risk_system.calculate_take_profit(symbol, current_price)

            logger.info(f"推奨ポジションサイズ: ${position_size:,.2f}")
            logger.info(f"推奨ストップロス: ${stop_loss:.2f}")
            logger.info(f"推奨テイクプロフィット: ${take_profit:.2f}")

            # 推奨事項の表示
            recommendations = risk_system.get_risk_adjustment_recommendations(symbol)
            if recommendations:
                logger.info(f"推奨事項:")
                for rec in recommendations:
                    logger.info(f"  - {rec}")

        except Exception as e:
            logger.error(f"シンボル {symbol} の処理に失敗: {e}")

    # 調整サマリーの表示
    summary = risk_system.get_adjustment_summary()
    logger.info(f"調整サマリー: {json.dumps(summary, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(main())
