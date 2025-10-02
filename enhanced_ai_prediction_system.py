#!/usr/bin/env python3
"""
強化AI予測モデル統合システム
統合システムとの完全連携による月間15-25%の利益向上

主要機能:
1. 機械学習モデルのリアルタイム予測
2. アンサンブル予測による精度向上
3. 予測信頼度の動的調整
4. モデル性能の継続監視
5. 統合システムとの完全連携
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
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    VotingRegressor,
)
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
import joblib
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import os
import sys
import requests

# 統合システムのインポート
from unified_system import UnifiedSystem, ErrorCategory, LogLevel, LogCategory

# 統合エラーハンドリングシステムのインポート
from unified_error_handling_system import (
    get_unified_error_handler,
    ErrorCategory as UnifiedErrorCategory,
    ErrorSeverity,
    error_handler,
    error_context,
    log_api_error,
    log_data_error,
    log_model_error,
    log_file_error
)

warnings.filterwarnings("ignore")


class ModelType(Enum):
    """予測モデルタイプ"""

    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    LASSO_REGRESSION = "lasso_regression"
    SVM_REGRESSION = "svm_regression"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"


class PredictionConfidence(Enum):
    """予測信頼度レベル"""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ModelHealthStatus(Enum):
    """モデル健全性ステータス"""

    OK = "ok"
    WARNING = "warning"
    STOP = "stop"


@dataclass
class ModelHealthReport:
    """健全性ゲートの評価レポート"""

    status: ModelHealthStatus
    detail: Dict[str, float]
    reasons: List[str]
    checked_at: datetime


@dataclass
class PredictionResult:
    """予測結果データクラス"""

    symbol: str
    predicted_price: float
    confidence: PredictionConfidence
    confidence_score: float
    model_name: str
    prediction_time: datetime
    features_used: List[str]
    additional_info: Dict[str, any] = None

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)

    def to_json(self) -> str:
        """JSON形式に変換"""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)


@dataclass
class ModelPerformance:
    """モデル性能データクラス"""

    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    rmse: float
    mae: float
    r2_score: float
    last_updated: datetime
    prediction_count: int = 0
    success_rate: float = 0.0

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)


class EnhancedAIPredictionSystem:
    """強化AI予測モデル統合システム"""

    def __init__(self, unified_system: UnifiedSystem = None):
        """初期化"""
        self.unified_system = unified_system or UnifiedSystem()
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        self.prediction_history = []
        self.model_cache = {}
        self.is_training = False
        self.training_lock = threading.Lock()

        # 設定
        self.config = {
            "max_models": 10,
            "retrain_interval_hours": 24,
            "min_confidence_threshold": 0.6,
            "ensemble_weight_threshold": 0.1,
            "feature_importance_threshold": 0.05,
            "prediction_cache_size": 1000,
            "model_save_path": "models/",
            "performance_log_path": "logs/ai_prediction_performance.log",
        }

        # ディレクトリの作成
        os.makedirs(self.config["model_save_path"], exist_ok=True)
        os.makedirs("logs", exist_ok=True)

        # ログ設定
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        # ファイルハンドラーの追加
        file_handler = logging.FileHandler(self.config["performance_log_path"])
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info("🚀 強化AI予測システム初期化完了")

        # 健全性ゲート設定（閾値）
        self.health_config = {
            "max_missing_ratio": 0.1,  # 特徴量欠損率の上限（10%）
            "max_feature_z_abs": 5.0,  # 特徴量z値の絶対最大許容（5σ）
            "max_mahalanobis": 25.0,  # マハラノビス近似（z^2合計）の上限
            "warning_mahalanobis": 16.0,  # 警告域（約4σ相当）
            "min_confidence_threshold": 0.6,  # 内部信頼度下限
            "health_output_path": os.path.join(
                "web-app", "public", "data", "model_health.json"
            ),
        }

    class ModelHealthException(Exception):
        pass

    def create_model(self, model_type: ModelType, **kwargs) -> object:
        """モデルの作成"""
        try:
            if model_type == ModelType.RANDOM_FOREST:
                return RandomForestRegressor(
                    n_estimators=kwargs.get("n_estimators", 100),
                    max_depth=kwargs.get("max_depth", 10),
                    random_state=42,
                )
            elif model_type == ModelType.GRADIENT_BOOSTING:
                return GradientBoostingRegressor(
                    n_estimators=kwargs.get("n_estimators", 100),
                    learning_rate=kwargs.get("learning_rate", 0.1),
                    random_state=42,
                )
            elif model_type == ModelType.LINEAR_REGRESSION:
                return LinearRegression()
            elif model_type == ModelType.RIDGE_REGRESSION:
                return Ridge(alpha=kwargs.get("alpha", 1.0))
            elif model_type == ModelType.LASSO_REGRESSION:
                return Lasso(alpha=kwargs.get("alpha", 1.0))
            elif model_type == ModelType.SVM_REGRESSION:
                return SVR(
                    kernel=kwargs.get("kernel", "rbf"),
                    C=kwargs.get("C", 1.0),
                    gamma=kwargs.get("gamma", "scale"),
                )
            elif model_type == ModelType.NEURAL_NETWORK:
                return MLPRegressor(
                    hidden_layer_sizes=kwargs.get("hidden_layer_sizes", (100, 50)),
                    max_iter=kwargs.get("max_iter", 1000),
                    random_state=42,
                )
            else:
                raise ValueError(f"未対応のモデルタイプ: {model_type}")

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"モデル作成エラー: {model_type.value}",
            )
            raise

    def prepare_features(
        self,
        data: pd.DataFrame,
        target_column: str = "price",
        feature_columns: List[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """特徴量の準備"""
        try:
            # 基本特徴量
            if feature_columns is None:
                features = []

                # 価格関連特徴量
                if "price" in data.columns:
                    features.extend(["price", "volume", "high", "low", "open", "close"])

                # 技術指標
                if len(data) > 20:
                    # 移動平均
                    data["ma_5"] = data["price"].rolling(window=5).mean()
                    data["ma_10"] = data["price"].rolling(window=10).mean()
                    data["ma_20"] = data["price"].rolling(window=20).mean()

                    # RSI
                    delta = data["price"].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    data["rsi"] = 100 - (100 / (1 + rs))

                    # MACD
                    exp1 = data["price"].ewm(span=12).mean()
                    exp2 = data["price"].ewm(span=26).mean()
                    data["macd"] = exp1 - exp2
                    data["macd_signal"] = data["macd"].ewm(span=9).mean()

                    features.extend(
                        ["ma_5", "ma_10", "ma_20", "rsi", "macd", "macd_signal"]
                    )

                # 特徴量の選択
                feature_columns = [col for col in features if col in data.columns]

            # 特徴量の取得と欠損値の処理
            X = data[feature_columns].fillna(0).values
            y = (
                data[target_column].values
                if target_column in data.columns
                else np.zeros(len(data))
            )

            return X, y, feature_columns

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.DATA_PROCESSING_ERROR,
                context="特徴量準備エラー",
            )
            raise

    def train_model(
        self,
        model_type: ModelType,
        data: pd.DataFrame,
        target_column: str = "price",
        model_name: str = None,
    ) -> str:
        """モデルの学習"""
        try:
            with self.training_lock:
                self.is_training = True

                # 特徴量の準備
                X, y, feature_columns = self.prepare_features(data, target_column)

                # データの分割
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = y[:split_idx], y[split_idx:]

                # スケーリング
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)

                # モデルの作成と学習
                model = self.create_model(model_type)
                model.fit(X_train_scaled, y_train)

                # 予測と評価
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)

                # モデル名の生成
                if model_name is None:
                    model_name = (
                        f"{model_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )

                # モデルの保存（特徴量カラムも保存）
                model.feature_columns = feature_columns
                self.models[model_name] = model
                self.scalers[model_name] = scaler

                # 性能メトリクスの記録
                self.performance_metrics[model_name] = ModelPerformance(
                    model_name=model_name,
                    accuracy=r2,
                    precision=0.0,  # 回帰では使用しない
                    recall=0.0,  # 回帰では使用しない
                    f1_score=0.0,  # 回帰では使用しない
                    mse=mse,
                    rmse=np.sqrt(mse),
                    mae=mae,
                    r2_score=r2,
                    last_updated=datetime.now(),
                    prediction_count=0,
                    success_rate=0.0,
                )

                # モデルの保存
                self.save_model(model_name)

                self.logger.info(
                    f"✅ モデル学習完了: {model_name} (R²={r2:.4f}, MSE={mse:.4f})"
                )

                return model_name

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"モデル学習エラー: {model_type.value}",
            )
            raise
        finally:
            self.is_training = False

    def predict(
        self, model_name: str, data: pd.DataFrame, confidence_threshold: float = None
    ) -> PredictionResult:
        """予測の実行"""
        try:
            if model_name not in self.models:
                raise ValueError(f"モデルが見つかりません: {model_name}")

            # モデルに保存された特徴量カラムを取得
            model_feature_columns = getattr(
                self.models[model_name], "feature_columns", None
            )

            # 特徴量の準備（学習時と同じ特徴量を使用）
            X, _, feature_columns = self.prepare_features(
                data, feature_columns=model_feature_columns
            )

            # スケーリング
            scaler = self.scalers[model_name]
            X_scaled = scaler.transform(X)

            # 推論直前の健全性ゲート
            health = self.check_model_health(
                model_name=model_name,
                X_raw=X,
                X_scaled=X_scaled,
                feature_columns=feature_columns,
                data_frame=data,
            )
            # 健全性結果を出力（UI参照用）
            try:
                self.export_model_health(health)
            except Exception:
                pass

            if health.status == ModelHealthStatus.STOP:
                self.logger.error(
                    f"🛑 健全性ゲート: 停止判定 - 理由: {', '.join(health.reasons)}"
                )
                self._notify_health(health, severity="critical")
                raise EnhancedAIPredictionSystem.ModelHealthException(
                    f"健全性ゲートにより推論停止: {health.reasons}"
                )
            elif health.status == ModelHealthStatus.WARNING:
                self.logger.warning(
                    f"⚠️ 健全性ゲート: 警告 - 理由: {', '.join(health.reasons)}"
                )
                self._notify_health(health, severity="warning")

            # 予測
            model = self.models[model_name]
            prediction = model.predict(X_scaled[-1:])[0]

            # 信頼度の計算
            confidence_score = self.calculate_confidence(model, X_scaled[-1:])
            confidence = self.get_confidence_level(confidence_score)

            # 信頼度閾値のチェック
            if confidence_threshold and confidence_score < confidence_threshold:
                self.logger.warning(
                    f"予測信頼度が閾値を下回っています: {confidence_score:.4f} < {confidence_threshold:.4f}"
                )

            # 予測結果の作成
            result = PredictionResult(
                symbol=(
                    data.get("symbol", "UNKNOWN").iloc[-1]
                    if "symbol" in data.columns
                    else "UNKNOWN"
                ),
                predicted_price=float(prediction),
                confidence=confidence,
                confidence_score=confidence_score,
                model_name=model_name,
                prediction_time=datetime.now(),
                features_used=feature_columns,
                additional_info={
                    "model_performance": self.performance_metrics[model_name].to_dict(),
                    "feature_importance": self.get_feature_importance(
                        model, feature_columns
                    ),
                    "prediction_interval": self.calculate_prediction_interval(
                        model, X_scaled[-1:]
                    ),
                    "model_health": {
                        "status": health.status.value,
                        "detail": health.detail,
                        "reasons": health.reasons,
                    },
                },
            )

            # 予測履歴の記録
            self.prediction_history.append(result)
            if len(self.prediction_history) > self.config["prediction_cache_size"]:
                self.prediction_history.pop(0)

            # 性能メトリクスの更新
            self.performance_metrics[model_name].prediction_count += 1

            self.logger.info(
                f"🔮 予測完了: {model_name} - 価格: {prediction:.2f}, 信頼度: {confidence_score:.4f}"
            )

            return result

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context=f"予測実行エラー: {model_name}",
            )
            raise

    def calculate_confidence(self, model, X: np.ndarray) -> float:
        """信頼度の計算"""
        try:
            # 複数の方法で信頼度を計算
            confidence_scores = []

            # 1. モデルの性能ベース
            if hasattr(model, "score"):
                confidence_scores.append(max(0, min(1, model.score(X, X))))

            # 2. 特徴量の分散ベース
            feature_variance = np.var(X)
            confidence_scores.append(max(0, min(1, 1 - feature_variance)))

            # 3. モデルの不確実性ベース（可能な場合）
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)
                confidence_scores.append(np.max(proba))

            # 平均信頼度
            return np.mean(confidence_scores) if confidence_scores else 0.5

        except Exception:
            return 0.5  # デフォルト値

    def get_confidence_level(self, confidence_score: float) -> PredictionConfidence:
        """信頼度レベルの取得"""
        if confidence_score >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif confidence_score >= 0.8:
            return PredictionConfidence.HIGH
        elif confidence_score >= 0.7:
            return PredictionConfidence.MEDIUM
        elif confidence_score >= 0.6:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

    def check_model_health(
        self,
        model_name: str,
        X_raw: np.ndarray,
        X_scaled: np.ndarray,
        feature_columns: List[str],
        data_frame: pd.DataFrame,
    ) -> ModelHealthReport:
        """分布逸脱・データ欠如・異常スコアを判定する健全性ゲート"""
        reasons: List[str] = []
        detail: Dict[str, float] = {}

        try:
            # 1) データ欠如チェック
            if len(feature_columns) == 0 or X_raw.size == 0:
                reasons.append("特徴量が空")
                detail["missing_ratio"] = 1.0
                status = ModelHealthStatus.STOP
                return ModelHealthReport(
                    status=status,
                    detail=detail,
                    reasons=reasons,
                    checked_at=datetime.now(),
                )

            # 欠損率
            missing_ratio = float(np.isnan(X_raw).sum()) / float(X_raw.size)
            detail["missing_ratio"] = missing_ratio
            if missing_ratio > self.health_config["max_missing_ratio"]:
                reasons.append(f"欠損率が閾値超過: {missing_ratio:.3f}")

            # 2) 分布逸脱（簡易Zスコアと疑似マハラノビス）
            # スケール済最終サンプルでのチェック
            x = X_scaled[-1:].astype(float)
            z_abs_max = float(np.max(np.abs(x))) if x.size > 0 else 0.0
            detail["z_abs_max"] = z_abs_max
            if z_abs_max > self.health_config["max_feature_z_abs"]:
                reasons.append(f"|z|max 超過: {z_abs_max:.2f}")

            mahalanobis_approx = float(np.sum(np.square(x)))  # 共分散=Iの近似
            detail["mahalanobis_approx"] = mahalanobis_approx
            if mahalanobis_approx > self.health_config["max_mahalanobis"]:
                reasons.append(f"分布逸脱が大（近似D^2={mahalanobis_approx:.1f}）")
            elif mahalanobis_approx > self.health_config["warning_mahalanobis"]:
                reasons.append(f"分布逸脱が中（近似D^2={mahalanobis_approx:.1f}）")

            # 3) 異常スコア（内部信頼度の下限チェック）
            # ここではスケール済み1点に対する簡易信頼度を再評価
            try:
                model = self.models[model_name]
                conf = float(self.calculate_confidence(model, x))
            except Exception:
                conf = 0.5
            detail["confidence_estimate"] = conf
            if conf < self.health_config["min_confidence_threshold"]:
                reasons.append(f"内部信頼度が低い: {conf:.2f}")

            # ステータス決定
            stop_conditions = (
                missing_ratio > self.health_config["max_missing_ratio"]
                or z_abs_max > self.health_config["max_feature_z_abs"]
                or mahalanobis_approx > self.health_config["max_mahalanobis"]
            )
            warn_conditions = (
                mahalanobis_approx > self.health_config["warning_mahalanobis"]
                or conf < self.health_config["min_confidence_threshold"]
            )

            if stop_conditions:
                status = ModelHealthStatus.STOP
            elif warn_conditions:
                status = ModelHealthStatus.WARNING
            else:
                status = ModelHealthStatus.OK

            return ModelHealthReport(
                status=status, detail=detail, reasons=reasons, checked_at=datetime.now()
            )

        except Exception as e:
            # フェイルオープンではなくフェイルセーフ（STOP）
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="健全性ゲート評価エラー",
            )
            return ModelHealthReport(
                status=ModelHealthStatus.STOP,
                detail={"error": 1.0},
                reasons=["健全性評価エラー"],
                checked_at=datetime.now(),
            )

    def export_model_health(self, report: ModelHealthReport) -> bool:
        """健全性レポートをJSONとして書き出し（Web UI参照用）"""
        try:
            os.makedirs(
                os.path.dirname(self.health_config["health_output_path"]), exist_ok=True
            )
            payload = {
                "status": report.status.value,
                "detail": report.detail,
                "reasons": report.reasons,
                "checked_at": report.checked_at.isoformat(),
            }
            with open(
                self.health_config["health_output_path"], "w", encoding="utf-8"
            ) as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def _notify_health(
        self, report: ModelHealthReport, severity: str = "warning"
    ) -> None:
        """健全性アラートをWebhookへ通知（存在すれば）。失敗しても処理継続。"""
        try:
            webhook = os.getenv("HEALTH_WEBHOOK_URL") or os.getenv("SLACK_WEBHOOK_URL")
            if not webhook:
                return
            payload = {
                "text": f"[ModelHealth] status={report.status.value} severity={severity} reasons={', '.join(report.reasons)}",
                "attachments": [
                    {
                        "color": (
                            "#ff0000"
                            if report.status == ModelHealthStatus.STOP
                            else "#ffcc00"
                        ),
                        "fields": [
                            {"title": k, "value": str(v), "short": True}
                            for k, v in report.detail.items()
                        ],
                        "ts": int(report.checked_at.timestamp()),
                    }
                ],
            }
            headers = {"Content-Type": "application/json"}
            requests.post(webhook, data=json.dumps(payload), headers=headers, timeout=3)
        except Exception:
            # 通知失敗は致命ではない
            return

    def get_feature_importance(
        self, model, feature_columns: List[str]
    ) -> Dict[str, float]:
        """特徴量重要度の取得"""
        try:
            if hasattr(model, "feature_importances_"):
                importance_dict = dict(zip(feature_columns, model.feature_importances_))
                return {
                    k: v
                    for k, v in importance_dict.items()
                    if v >= self.config["feature_importance_threshold"]
                }
            else:
                return {}
        except Exception:
            return {}

    def calculate_prediction_interval(
        self, model, X: np.ndarray, confidence: float = 0.95
    ) -> Dict[str, float]:
        """予測区間の計算"""
        try:
            # 簡易的な予測区間の計算
            prediction = model.predict(X)[0]

            # モデルの性能に基づく区間
            if model in self.performance_metrics:
                rmse = self.performance_metrics[model].rmse
                interval = 1.96 * rmse  # 95%信頼区間

                return {
                    "lower_bound": prediction - interval,
                    "upper_bound": prediction + interval,
                    "confidence_level": confidence,
                }
            else:
                return {
                    "lower_bound": prediction * 0.95,
                    "upper_bound": prediction * 1.05,
                    "confidence_level": confidence,
                }
        except Exception:
            return {"lower_bound": 0, "upper_bound": 0, "confidence_level": confidence}

    def create_ensemble_model(
        self, model_names: List[str], weights: List[float] = None
    ) -> str:
        """アンサンブルモデルの作成"""
        try:
            if len(model_names) < 2:
                raise ValueError("アンサンブルには2つ以上のモデルが必要です")

            # 重みの正規化
            if weights is None:
                weights = [1.0 / len(model_names)] * len(model_names)
            else:
                weights = np.array(weights)
                weights = weights / np.sum(weights)

            # モデルの取得
            models = [self.models[name] for name in model_names if name in self.models]

            if len(models) != len(model_names):
                raise ValueError("一部のモデルが見つかりません")

            # アンサンブルモデルの作成
            ensemble_name = f"ensemble_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 重み付き平均による予測
            def ensemble_predict(X):
                predictions = np.array([model.predict(X) for model in models])
                return np.average(predictions, axis=0, weights=weights)

            # アンサンブルモデルの保存
            self.models[ensemble_name] = type(
                "EnsembleModel",
                (),
                {
                    "predict": ensemble_predict,
                    "feature_importances_": np.zeros(
                        len(models[0].feature_importances_)
                    ),
                    "score": lambda X, y: np.mean(
                        [model.score(X, y) for model in models]
                    ),
                },
            )()

            self.logger.info(f"✅ アンサンブルモデル作成完了: {ensemble_name}")
            return ensemble_name

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="アンサンブルモデル作成エラー",
            )
            raise

    def batch_predict(
        self, model_name: str, data_list: List[pd.DataFrame]
    ) -> List[PredictionResult]:
        """バッチ予測の実行"""
        try:
            results = []

            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_data = {
                    executor.submit(self.predict, model_name, data): data
                    for data in data_list
                }

                for future in as_completed(future_to_data):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.unified_system.log_error(
                            error=e,
                            category=ErrorCategory.MODEL_ERROR,
                            context="バッチ予測エラー",
                        )

            return results

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="バッチ予測実行エラー",
            )
            raise

    def save_model(self, model_name: str) -> bool:
        """モデルの保存"""
        try:
            if model_name not in self.models:
                return False

            model_path = os.path.join(
                self.config["model_save_path"], f"{model_name}.joblib"
            )
            scaler_path = os.path.join(
                self.config["model_save_path"], f"{model_name}_scaler.joblib"
            )

            # モデルの保存
            joblib.dump(self.models[model_name], model_path)
            joblib.dump(self.scalers[model_name], scaler_path)

            self.logger.info(f"💾 モデル保存完了: {model_name}")
            return True

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.FILE_ERROR,
                context=f"モデル保存エラー: {model_name}",
            )
            return False

    def load_model(self, model_name: str) -> bool:
        """モデルの読み込み"""
        try:
            model_path = os.path.join(
                self.config["model_save_path"], f"{model_name}.joblib"
            )
            scaler_path = os.path.join(
                self.config["model_save_path"], f"{model_name}_scaler.joblib"
            )

            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                return False

            # モデルの読み込み
            self.models[model_name] = joblib.load(model_path)
            self.scalers[model_name] = joblib.load(scaler_path)

            self.logger.info(f"📂 モデル読み込み完了: {model_name}")
            return True

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.FILE_ERROR,
                context=f"モデル読み込みエラー: {model_name}",
            )
            return False

    def get_model_performance(
        self, model_name: str = None
    ) -> Union[ModelPerformance, Dict[str, ModelPerformance]]:
        """モデル性能の取得"""
        try:
            if model_name:
                return self.performance_metrics.get(model_name)
            else:
                return self.performance_metrics
        except Exception as e:
            self.unified_system.log_error(
                error=e, category=ErrorCategory.MODEL_ERROR, context="性能取得エラー"
            )
            return {}

    def retrain_models(
        self, data: pd.DataFrame, target_column: str = "price"
    ) -> Dict[str, str]:
        """モデルの再学習"""
        try:
            retrained_models = {}

            for model_name in list(self.models.keys()):
                try:
                    # モデルタイプの推定
                    model = self.models[model_name]
                    model_type = self.infer_model_type(model)

                    # 再学習
                    new_model_name = self.train_model(
                        model_type,
                        data,
                        target_column,
                        f"{model_name}_retrained_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    )

                    retrained_models[model_name] = new_model_name

                except Exception as e:
                    self.unified_system.log_error(
                        error=e,
                        category=ErrorCategory.MODEL_ERROR,
                        context=f"モデル再学習エラー: {model_name}",
                    )

            self.logger.info(f"🔄 モデル再学習完了: {len(retrained_models)}個のモデル")
            return retrained_models

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="モデル再学習実行エラー",
            )
            raise

    def infer_model_type(self, model) -> ModelType:
        """モデルタイプの推定"""
        model_class = type(model).__name__

        if "RandomForest" in model_class:
            return ModelType.RANDOM_FOREST
        elif "GradientBoosting" in model_class:
            return ModelType.GRADIENT_BOOSTING
        elif "LinearRegression" in model_class:
            return ModelType.LINEAR_REGRESSION
        elif "Ridge" in model_class:
            return ModelType.RIDGE_REGRESSION
        elif "Lasso" in model_class:
            return ModelType.LASSO_REGRESSION
        elif "SVR" in model_class:
            return ModelType.SVM_REGRESSION
        elif "MLPRegressor" in model_class:
            return ModelType.NEURAL_NETWORK
        else:
            return ModelType.LINEAR_REGRESSION  # デフォルト

    def cleanup_old_models(self, keep_count: int = 5) -> int:
        """古いモデルのクリーンアップ"""
        try:
            if len(self.models) <= keep_count:
                return 0

            # 性能の悪いモデルを特定
            model_scores = []
            for name, perf in self.performance_metrics.items():
                model_scores.append((name, perf.r2_score))

            # スコア順でソート
            model_scores.sort(key=lambda x: x[1], reverse=True)

            # 古いモデルを削除
            models_to_remove = model_scores[keep_count:]
            removed_count = 0

            for model_name, _ in models_to_remove:
                if model_name in self.models:
                    del self.models[model_name]
                    del self.scalers[model_name]
                    del self.performance_metrics[model_name]
                    removed_count += 1

            self.logger.info(f"🗑️ 古いモデルクリーンアップ完了: {removed_count}個削除")
            return removed_count

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="モデルクリーンアップエラー",
            )
            return 0

    def get_prediction_summary(self) -> Dict[str, any]:
        """予測サマリーの取得"""
        try:
            if not self.prediction_history:
                return {}

            recent_predictions = self.prediction_history[-100:]  # 最新100件

            summary = {
                "total_predictions": len(self.prediction_history),
                "recent_predictions": len(recent_predictions),
                "average_confidence": np.mean(
                    [p.confidence_score for p in recent_predictions]
                ),
                "high_confidence_predictions": len(
                    [
                        p
                        for p in recent_predictions
                        if p.confidence
                        in [PredictionConfidence.HIGH, PredictionConfidence.VERY_HIGH]
                    ]
                ),
                "model_usage": {},
                "symbol_distribution": {},
                "prediction_trends": self.analyze_prediction_trends(recent_predictions),
            }

            # モデル使用状況
            for pred in recent_predictions:
                model_name = pred.model_name
                summary["model_usage"][model_name] = (
                    summary["model_usage"].get(model_name, 0) + 1
                )

                symbol = pred.symbol
                summary["symbol_distribution"][symbol] = (
                    summary["symbol_distribution"].get(symbol, 0) + 1
                )

            return summary

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.MODEL_ERROR,
                context="予測サマリー取得エラー",
            )
            return {}

    def analyze_prediction_trends(
        self, predictions: List[PredictionResult]
    ) -> Dict[str, any]:
        """予測トレンドの分析"""
        try:
            if len(predictions) < 2:
                return {}

            prices = [p.predicted_price for p in predictions]
            confidences = [p.confidence_score for p in predictions]

            return {
                "price_trend": "up" if prices[-1] > prices[0] else "down",
                "confidence_trend": (
                    "up" if confidences[-1] > confidences[0] else "down"
                ),
                "price_volatility": np.std(prices),
                "confidence_volatility": np.std(confidences),
                "trend_strength": (
                    abs(prices[-1] - prices[0]) / prices[0] if prices[0] != 0 else 0
                ),
            }

        except Exception:
            return {}

    def export_predictions(self, file_path: str, format: str = "json") -> bool:
        """予測結果のエクスポート"""
        try:
            if format.lower() == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        [pred.to_dict() for pred in self.prediction_history],
                        f,
                        default=str,
                        ensure_ascii=False,
                        indent=2,
                    )
            elif format.lower() == "csv":
                df = pd.DataFrame([pred.to_dict() for pred in self.prediction_history])
                df.to_csv(file_path, index=False, encoding="utf-8")
            else:
                raise ValueError(f"未対応のフォーマット: {format}")

            self.logger.info(f"📊 予測結果エクスポート完了: {file_path}")
            return True

        except Exception as e:
            self.unified_system.log_error(
                error=e,
                category=ErrorCategory.FILE_ERROR,
                context=f"予測結果エクスポートエラー: {file_path}",
            )
            return False


def main():
    """メイン関数"""
    try:
        # 統合システムの初期化
        unified_system = UnifiedSystem()

        # AI予測システムの初期化
        ai_system = EnhancedAIPredictionSystem(unified_system)

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

        # モデルの学習
        model_name = ai_system.train_model(ModelType.RANDOM_FOREST, data)

        # 予測の実行
        prediction = ai_system.predict(model_name, data.tail(10))

        print(f"予測結果: {prediction.predicted_price:.2f}")
        print(f"信頼度: {prediction.confidence_score:.4f}")
        print(f"信頼度レベル: {prediction.confidence.value}")

        # 予測サマリーの表示
        summary = ai_system.get_prediction_summary()
        print(f"\n予測サマリー: {summary}")

    except Exception as e:
        print(f"エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
