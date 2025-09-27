#!/usr/bin/env python3
"""
感情トレンド予測システム
過去の感情データに基づいて将来の感情トレンドを予測

機能:
- 感情トレンドの予測
- 感情変化のパターン分析
- 予測精度の評価
- 感情予測に基づく取引戦略の提案
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
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

warnings.filterwarnings("ignore")

# 既存システムのインポート
try:
    from realtime_sentiment_metrics import RealtimeSentimentMetricsGenerator, MetricType
    from sentiment_analysis_system import SentimentTradingSystem, SentimentType
    from dynamic_risk_adjustment import DynamicRiskAdjustmentSystem
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sentiment_trend_prediction.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """予測モデルの定義"""

    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    LSTM = "lstm"
    ARIMA = "arima"


@dataclass
class SentimentPrediction:
    """感情予測"""

    timestamp: datetime
    symbol: str
    prediction_horizon: int  # 予測期間（分）
    predicted_sentiment: float
    confidence: float
    trend_direction: str  # "up", "down", "stable"
    volatility_prediction: float
    risk_level: str  # "low", "medium", "high"


@dataclass
class TrendPattern:
    """トレンドパターン"""

    pattern_name: str
    pattern_type: str  # "bullish", "bearish", "neutral"
    confidence: float
    duration: int  # パターン継続期間（分）
    expected_outcome: str


class SentimentTrendPredictor:
    """感情トレンド予測器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sentiment_metrics_generator = None
        self.sentiment_system = None
        self.risk_system = None

        # 予測モデル
        self.models = {}
        self.scalers = {}
        self.model_performance = {}

        # 履歴データ
        self.sentiment_history = {}
        self.prediction_history = deque(maxlen=1000)
        self.pattern_history = deque(maxlen=500)

        # 予測パラメータ
        self.prediction_horizons = [5, 15, 30, 60]  # 分
        self.feature_window = 20  # 特徴量計算用のウィンドウサイズ
        self.min_history_length = 50  # 最小履歴長

        self._initialize_systems()
        self._initialize_models()

    def _initialize_systems(self):
        """システムの初期化"""
        try:
            self.sentiment_metrics_generator = RealtimeSentimentMetricsGenerator()
            self.sentiment_system = SentimentTradingSystem()
            self.risk_system = DynamicRiskAdjustmentSystem()
            logger.info("感情トレンド予測システムの初期化に成功")
        except Exception as e:
            logger.error(f"システムの初期化に失敗: {e}")

    def _initialize_models(self):
        """予測モデルの初期化"""
        try:
            # 線形回帰モデル
            self.models[PredictionModel.LINEAR_REGRESSION] = LinearRegression()

            # ランダムフォレストモデル
            self.models[PredictionModel.RANDOM_FOREST] = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42
            )

            # スケーラー
            for model_name in self.models.keys():
                self.scalers[model_name] = StandardScaler()

            logger.info("予測モデルの初期化に成功")

        except Exception as e:
            logger.error(f"予測モデルの初期化に失敗: {e}")

    async def predict_sentiment_trend(
        self, symbol: str, horizon: int = 15
    ) -> SentimentPrediction:
        """感情トレンドの予測"""
        try:
            # 履歴データの取得
            history_data = await self._get_sentiment_history(symbol)

            if len(history_data) < self.min_history_length:
                logger.warning(f"シンボル {symbol} の履歴データが不足しています")
                return self._create_default_prediction(symbol, horizon)

            # 特徴量の準備
            features = self._prepare_features(history_data)

            if features is None or len(features) == 0:
                return self._create_default_prediction(symbol, horizon)

            # 予測の実行
            predictions = {}
            confidences = {}

            for model_name, model in self.models.items():
                try:
                    prediction, confidence = await self._predict_with_model(
                        model, model_name, features, horizon
                    )
                    predictions[model_name] = prediction
                    confidences[model_name] = confidence
                except Exception as e:
                    logger.error(f"モデル {model_name} の予測に失敗: {e}")
                    continue

            if not predictions:
                return self._create_default_prediction(symbol, horizon)

            # アンサンブル予測
            ensemble_prediction = self._ensemble_predictions(predictions, confidences)

            # トレンド方向の判定
            trend_direction = self._determine_trend_direction(
                ensemble_prediction, history_data
            )

            # ボラティリティ予測
            volatility_prediction = self._predict_volatility(history_data, horizon)

            # リスクレベルの判定
            risk_level = self._determine_risk_level(
                ensemble_prediction, volatility_prediction
            )

            # 予測結果の作成
            prediction = SentimentPrediction(
                timestamp=datetime.now(),
                symbol=symbol,
                prediction_horizon=horizon,
                predicted_sentiment=ensemble_prediction,
                confidence=np.mean(list(confidences.values())),
                trend_direction=trend_direction,
                volatility_prediction=volatility_prediction,
                risk_level=risk_level,
            )

            # 予測履歴の記録
            self.prediction_history.append(prediction)

            return prediction

        except Exception as e:
            logger.error(f"感情トレンドの予測に失敗: {e}")
            return self._create_default_prediction(symbol, horizon)

    async def _get_sentiment_history(self, symbol: str) -> List[Dict[str, Any]]:
        """感情履歴データの取得"""
        try:
            if symbol not in self.sentiment_history:
                self.sentiment_history[symbol] = deque(maxlen=1000)

            # 最新の感情指標を取得
            if self.sentiment_metrics_generator:
                metrics = (
                    await self.sentiment_metrics_generator.generate_realtime_metrics(
                        [symbol]
                    )
                )
                for metric in metrics:
                    self.sentiment_history[symbol].append(
                        {
                            "timestamp": metric.timestamp,
                            "sentiment_score": (
                                metric.value
                                if metric.metric_type == MetricType.SENTIMENT_SCORE
                                else 0.0
                            ),
                            "volatility": (
                                metric.value
                                if metric.metric_type == MetricType.VOLATILITY_INDEX
                                else 0.0
                            ),
                            "trend_strength": (
                                metric.value
                                if metric.metric_type == MetricType.TREND_STRENGTH
                                else 0.0
                            ),
                            "risk_level": (
                                metric.value
                                if metric.metric_type == MetricType.RISK_LEVEL
                                else 0.0
                            ),
                        }
                    )

            return list(self.sentiment_history[symbol])

        except Exception as e:
            logger.error(f"感情履歴データの取得に失敗: {e}")
            return []

    def _prepare_features(
        self, history_data: List[Dict[str, Any]]
    ) -> Optional[np.ndarray]:
        """特徴量の準備"""
        try:
            if len(history_data) < self.feature_window:
                return None

            # 最新のデータを使用
            recent_data = history_data[-self.feature_window :]

            features = []

            # 基本統計特徴量
            sentiment_scores = [d["sentiment_score"] for d in recent_data]
            volatilities = [d["volatility"] for d in recent_data]
            trend_strengths = [d["trend_strength"] for d in recent_data]
            risk_levels = [d["risk_level"] for d in recent_data]

            # 感情スコアの特徴量
            features.extend(
                [
                    np.mean(sentiment_scores),
                    np.std(sentiment_scores),
                    np.max(sentiment_scores),
                    np.min(sentiment_scores),
                    sentiment_scores[-1] - sentiment_scores[0],  # 変化量
                    np.mean(np.diff(sentiment_scores)),  # 平均変化率
                ]
            )

            # ボラティリティの特徴量
            features.extend(
                [
                    np.mean(volatilities),
                    np.std(volatilities),
                    np.max(volatilities),
                    volatilities[-1] - volatilities[0],
                ]
            )

            # トレンド強度の特徴量
            features.extend(
                [
                    np.mean(trend_strengths),
                    np.std(trend_strengths),
                    trend_strengths[-1] - trend_strengths[0],
                ]
            )

            # リスクレベルの特徴量
            features.extend(
                [np.mean(risk_levels), np.max(risk_levels), risk_levels[-1]]
            )

            # 時系列特徴量
            if len(sentiment_scores) >= 5:
                # 移動平均
                ma_3 = np.mean(sentiment_scores[-3:])
                ma_5 = np.mean(sentiment_scores[-5:])
                features.extend([ma_3, ma_5, ma_3 - ma_5])

            return np.array(features).reshape(1, -1)

        except Exception as e:
            logger.error(f"特徴量の準備に失敗: {e}")
            return None

    async def _predict_with_model(
        self, model, model_name: PredictionModel, features: np.ndarray, horizon: int
    ) -> Tuple[float, float]:
        """モデルによる予測"""
        try:
            # スケーラーの適用
            scaler = self.scalers[model_name]
            scaled_features = scaler.fit_transform(features)

            # 予測の実行
            prediction = model.predict(scaled_features)[0]

            # 信頼度の計算（簡易版）
            confidence = 0.7  # デフォルト信頼度

            # モデル性能に基づく信頼度調整
            if model_name in self.model_performance:
                performance = self.model_performance[model_name]
                confidence = performance.get("r2_score", 0.7)

            return prediction, confidence

        except Exception as e:
            logger.error(f"モデル {model_name} の予測に失敗: {e}")
            return 0.0, 0.5

    def _ensemble_predictions(
        self,
        predictions: Dict[PredictionModel, float],
        confidences: Dict[PredictionModel, float],
    ) -> float:
        """アンサンブル予測"""
        try:
            # 信頼度で重み付き平均
            weighted_sum = 0.0
            total_weight = 0.0

            for model_name, prediction in predictions.items():
                confidence = confidences.get(model_name, 0.5)
                weighted_sum += prediction * confidence
                total_weight += confidence

            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return np.mean(list(predictions.values()))

        except Exception as e:
            logger.error(f"アンサンブル予測に失敗: {e}")
            return 0.0

    def _determine_trend_direction(
        self, prediction: float, history_data: List[Dict[str, Any]]
    ) -> str:
        """トレンド方向の判定"""
        try:
            if len(history_data) < 2:
                return "stable"

            # 最近の感情スコア
            recent_sentiment = history_data[-1]["sentiment_score"]

            # 予測との比較
            if prediction > recent_sentiment + 0.1:
                return "up"
            elif prediction < recent_sentiment - 0.1:
                return "down"
            else:
                return "stable"

        except Exception as e:
            logger.error(f"トレンド方向の判定に失敗: {e}")
            return "stable"

    def _predict_volatility(
        self, history_data: List[Dict[str, Any]], horizon: int
    ) -> float:
        """ボラティリティの予測"""
        try:
            if len(history_data) < 5:
                return 0.1  # デフォルトボラティリティ

            # 最近のボラティリティを計算
            recent_volatilities = [d["volatility"] for d in history_data[-10:]]
            avg_volatility = np.mean(recent_volatilities)

            # 時系列の傾向を考慮
            if len(recent_volatilities) >= 3:
                trend = np.polyfit(
                    range(len(recent_volatilities)), recent_volatilities, 1
                )[0]
                # トレンドを予測期間に適用
                predicted_volatility = avg_volatility + (
                    trend * horizon / 60
                )  # 時間単位で調整
            else:
                predicted_volatility = avg_volatility

            return max(0.01, min(1.0, predicted_volatility))  # 0.01-1.0の範囲に制限

        except Exception as e:
            logger.error(f"ボラティリティの予測に失敗: {e}")
            return 0.1

    def _determine_risk_level(self, prediction: float, volatility: float) -> str:
        """リスクレベルの判定"""
        try:
            # 予測の絶対値とボラティリティを組み合わせてリスクを判定
            prediction_risk = abs(prediction)
            volatility_risk = volatility

            total_risk = (prediction_risk + volatility_risk) / 2

            if total_risk > 0.7:
                return "high"
            elif total_risk > 0.4:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"リスクレベルの判定に失敗: {e}")
            return "medium"

    def _create_default_prediction(
        self, symbol: str, horizon: int
    ) -> SentimentPrediction:
        """デフォルト予測の作成"""
        return SentimentPrediction(
            timestamp=datetime.now(),
            symbol=symbol,
            prediction_horizon=horizon,
            predicted_sentiment=0.0,
            confidence=0.5,
            trend_direction="stable",
            volatility_prediction=0.1,
            risk_level="medium",
        )

    async def train_models(self, symbol: str) -> Dict[str, Any]:
        """モデルの訓練"""
        try:
            # 履歴データの取得
            history_data = await self._get_sentiment_history(symbol)

            if len(history_data) < self.min_history_length:
                return {"error": "訓練データが不足しています"}

            # 訓練データの準備
            X, y = self._prepare_training_data(history_data)

            if X is None or len(X) == 0:
                return {"error": "訓練データの準備に失敗しました"}

            # 各モデルの訓練
            training_results = {}

            for model_name, model in self.models.items():
                try:
                    # スケーラーの適用
                    scaler = self.scalers[model_name]
                    X_scaled = scaler.fit_transform(X)

                    # モデルの訓練
                    model.fit(X_scaled, y)

                    # 性能評価
                    y_pred = model.predict(X_scaled)
                    mse = mean_squared_error(y, y_pred)
                    mae = mean_absolute_error(y, y_pred)
                    r2 = r2_score(y, y_pred)

                    training_results[model_name.value] = {
                        "mse": mse,
                        "mae": mae,
                        "r2_score": r2,
                        "status": "success",
                    }

                    # 性能の記録
                    self.model_performance[model_name] = {
                        "mse": mse,
                        "mae": mae,
                        "r2_score": r2,
                    }

                except Exception as e:
                    logger.error(f"モデル {model_name} の訓練に失敗: {e}")
                    training_results[model_name.value] = {
                        "error": str(e),
                        "status": "failed",
                    }

            return training_results

        except Exception as e:
            logger.error(f"モデルの訓練に失敗: {e}")
            return {"error": str(e)}

    def _prepare_training_data(
        self, history_data: List[Dict[str, Any]]
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """訓練データの準備"""
        try:
            if len(history_data) < self.feature_window + 1:
                return None, None

            X = []
            y = []

            # スライディングウィンドウでデータを準備
            for i in range(self.feature_window, len(history_data)):
                # 特徴量
                window_data = history_data[i - self.feature_window : i]
                features = self._prepare_features(window_data)

                if features is not None:
                    X.append(features.flatten())

                    # ターゲット（次の感情スコア）
                    target = history_data[i]["sentiment_score"]
                    y.append(target)

            return np.array(X), np.array(y)

        except Exception as e:
            logger.error(f"訓練データの準備に失敗: {e}")
            return None, None

    def detect_trend_patterns(self, symbol: str) -> List[TrendPattern]:
        """トレンドパターンの検出"""
        try:
            if symbol not in self.sentiment_history:
                return []

            history_data = list(self.sentiment_history[symbol])
            if len(history_data) < 20:
                return []

            patterns = []

            # 感情スコアの取得
            sentiment_scores = [d["sentiment_score"] for d in history_data]

            # パターン1: 上昇トレンド
            if self._detect_uptrend(sentiment_scores):
                patterns.append(
                    TrendPattern(
                        pattern_name="上昇トレンド",
                        pattern_type="bullish",
                        confidence=0.8,
                        duration=len(sentiment_scores),
                        expected_outcome="ポジティブ感情の継続",
                    )
                )

            # パターン2: 下降トレンド
            if self._detect_downtrend(sentiment_scores):
                patterns.append(
                    TrendPattern(
                        pattern_name="下降トレンド",
                        pattern_type="bearish",
                        confidence=0.8,
                        duration=len(sentiment_scores),
                        expected_outcome="ネガティブ感情の継続",
                    )
                )

            # パターン3: サイドウェイス
            if self._detect_sideways(sentiment_scores):
                patterns.append(
                    TrendPattern(
                        pattern_name="サイドウェイス",
                        pattern_type="neutral",
                        confidence=0.7,
                        duration=len(sentiment_scores),
                        expected_outcome="感情の安定",
                    )
                )

            # パターン4: ボラティリティの増加
            volatilities = [d["volatility"] for d in history_data]
            if self._detect_volatility_increase(volatilities):
                patterns.append(
                    TrendPattern(
                        pattern_name="ボラティリティ増加",
                        pattern_type="volatile",
                        confidence=0.6,
                        duration=len(volatilities),
                        expected_outcome="感情の不安定化",
                    )
                )

            return patterns

        except Exception as e:
            logger.error(f"トレンドパターンの検出に失敗: {e}")
            return []

    def _detect_uptrend(self, scores: List[float]) -> bool:
        """上昇トレンドの検出"""
        if len(scores) < 5:
            return False

        # 線形回帰で傾きを計算
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]

        return slope > 0.01  # 正の傾き

    def _detect_downtrend(self, scores: List[float]) -> bool:
        """下降トレンドの検出"""
        if len(scores) < 5:
            return False

        # 線形回帰で傾きを計算
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]

        return slope < -0.01  # 負の傾き

    def _detect_sideways(self, scores: List[float]) -> bool:
        """サイドウェイスの検出"""
        if len(scores) < 10:
            return False

        # 標準偏差が小さい場合
        return np.std(scores) < 0.1

    def _detect_volatility_increase(self, volatilities: List[float]) -> bool:
        """ボラティリティ増加の検出"""
        if len(volatilities) < 5:
            return False

        # 最近のボラティリティが平均より高い
        recent_vol = np.mean(volatilities[-3:])
        avg_vol = np.mean(volatilities)

        return recent_vol > avg_vol * 1.5

    def get_prediction_summary(self, symbol: str = None) -> Dict[str, Any]:
        """予測サマリーの取得"""
        try:
            if symbol:
                predictions = [p for p in self.prediction_history if p.symbol == symbol]
            else:
                predictions = list(self.prediction_history)

            if not predictions:
                return {"message": "予測履歴がありません"}

            # 最新の予測を取得
            latest_predictions = {}
            for pred in predictions:
                if pred.symbol not in latest_predictions:
                    latest_predictions[pred.symbol] = []

                latest_predictions[pred.symbol].append(
                    {
                        "predicted_sentiment": pred.predicted_sentiment,
                        "confidence": pred.confidence,
                        "trend_direction": pred.trend_direction,
                        "volatility_prediction": pred.volatility_prediction,
                        "risk_level": pred.risk_level,
                        "prediction_horizon": pred.prediction_horizon,
                        "timestamp": pred.timestamp.isoformat(),
                    }
                )

            return latest_predictions

        except Exception as e:
            logger.error(f"予測サマリーの取得に失敗: {e}")
            return {"error": str(e)}

    def visualize_predictions(self, symbol: str, save_path: str = None):
        """予測の可視化"""
        try:
            if symbol not in self.sentiment_history:
                logger.warning(f"シンボル {symbol} の履歴データがありません")
                return

            history_data = list(self.sentiment_history[symbol])
            if len(history_data) < 10:
                logger.warning(f"シンボル {symbol} の履歴データが不足しています")
                return

            # データの準備
            timestamps = [d["timestamp"] for d in history_data]
            sentiment_scores = [d["sentiment_score"] for d in history_data]
            volatilities = [d["volatility"] for d in history_data]

            # 予測データの取得
            predictions = [p for p in self.prediction_history if p.symbol == symbol]

            # プロットの作成
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f"{symbol} - 感情トレンド予測", fontsize=16)

            # 感情スコアのプロット
            axes[0, 0].plot(
                timestamps,
                sentiment_scores,
                "b-",
                linewidth=2,
                label="実際の感情スコア",
            )
            if predictions:
                pred_timestamps = [p.timestamp for p in predictions]
                pred_scores = [p.predicted_sentiment for p in predictions]
                axes[0, 0].scatter(
                    pred_timestamps, pred_scores, color="red", s=50, label="予測値"
                )
            axes[0, 0].set_title("感情スコアと予測")
            axes[0, 0].set_ylabel("感情スコア")
            axes[0, 0].legend()
            axes[0, 0].grid(True)

            # ボラティリティのプロット
            axes[0, 1].plot(
                timestamps,
                volatilities,
                "orange",
                linewidth=2,
                label="実際のボラティリティ",
            )
            if predictions:
                pred_volatilities = [p.volatility_prediction for p in predictions]
                axes[0, 1].scatter(
                    pred_timestamps,
                    pred_volatilities,
                    color="red",
                    s=50,
                    label="予測値",
                )
            axes[0, 1].set_title("ボラティリティと予測")
            axes[0, 1].set_ylabel("ボラティリティ")
            axes[0, 1].legend()
            axes[0, 1].grid(True)

            # トレンド方向の可視化
            if predictions:
                trend_colors = {"up": "green", "down": "red", "stable": "gray"}
                trend_scores = [p.predicted_sentiment for p in predictions]
                trend_directions = [p.trend_direction for p in predictions]

                for i, (score, direction) in enumerate(
                    zip(trend_scores, trend_directions)
                ):
                    axes[1, 0].scatter(
                        i, score, color=trend_colors.get(direction, "gray"), s=100
                    )

                axes[1, 0].set_title("トレンド方向の予測")
                axes[1, 0].set_ylabel("予測感情スコア")
                axes[1, 0].grid(True)

            # 信頼度の可視化
            if predictions:
                confidences = [p.confidence for p in predictions]
                axes[1, 1].plot(
                    range(len(confidences)),
                    confidences,
                    "purple",
                    linewidth=2,
                    marker="o",
                )
                axes[1, 1].set_title("予測信頼度")
                axes[1, 1].set_ylabel("信頼度")
                axes[1, 1].set_xlabel("予測回数")
                axes[1, 1].grid(True)

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches="tight")
                logger.info(f"予測グラフを保存しました: {save_path}")
            else:
                plt.show()

        except Exception as e:
            logger.error(f"予測の可視化に失敗: {e}")


async def main():
    """メイン関数"""
    # 感情トレンド予測システムの初期化
    predictor = SentimentTrendPredictor()

    # テストシンボル
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]

    # 各シンボルの予測を実行
    for symbol in symbols:
        logger.info(f"シンボル {symbol} の感情トレンド予測を実行中...")

        try:
            # 感情トレンドの予測
            prediction = await predictor.predict_sentiment_trend(symbol, horizon=15)

            logger.info(f"予測結果:")
            logger.info(f"  予測感情スコア: {prediction.predicted_sentiment:.3f}")
            logger.info(f"  信頼度: {prediction.confidence:.3f}")
            logger.info(f"  トレンド方向: {prediction.trend_direction}")
            logger.info(f"  ボラティリティ予測: {prediction.volatility_prediction:.3f}")
            logger.info(f"  リスクレベル: {prediction.risk_level}")

            # トレンドパターンの検出
            patterns = predictor.detect_trend_patterns(symbol)
            if patterns:
                logger.info(f"検出されたパターン:")
                for pattern in patterns:
                    logger.info(
                        f"  - {pattern.pattern_name}: {pattern.expected_outcome}"
                    )

        except Exception as e:
            logger.error(f"シンボル {symbol} の処理に失敗: {e}")

    # 予測サマリーの表示
    summary = predictor.get_prediction_summary()
    logger.info(f"予測サマリー: {json.dumps(summary, indent=2, ensure_ascii=False)}")

    # 可視化の例
    if symbols:
        symbol = symbols[0]
        predictor.visualize_predictions(symbol, f"sentiment_predictions_{symbol}.png")


if __name__ == "__main__":
    asyncio.run(main())
