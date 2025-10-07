#!/usr/bin/env python3
"""
複数モデルのアンサンブル予測システム
記事の単一モデルを超える高度なアンサンブル予測を実装
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class EnsemblePredictionSystem:
    """複数モデルのアンサンブル予測システム"""

    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # アンサンブル設定
        self.models = self._initialize_models()
        self.ensemble_methods = ["weighted_average", "stacking", "voting"]
        # 設定検証
        ensemble_method = self.config.get("ensemble_method", "weighted_average")
        if ensemble_method not in self.ensemble_methods:
            ensemble_method = "weighted_average"
        self.default_ensemble_method = ensemble_method

        # 重み設定
        self.model_weights = self.config.get("model_weights", {})
        self.performance_based_weights = self.config.get(
            "performance_based_weights", True
        )

        # 信頼度設定（検証付き）
        confidence_threshold = self.config.get("confidence_threshold", 0.7)
        if confidence_threshold < 0 or confidence_threshold > 1:
            confidence_threshold = 0.7
        self.confidence_threshold = confidence_threshold
        
        uncertainty_threshold = self.config.get("uncertainty_threshold", 0.3)
        if uncertainty_threshold < 0 or uncertainty_threshold > 1:
            uncertainty_threshold = 0.3
        self.uncertainty_threshold = uncertainty_threshold

        # 予測履歴
        self.prediction_history = []
        self.model_performance = {}

    def _initialize_models(self) -> Dict[str, Any]:
        """モデルの初期化"""
        return {
            "random_forest": RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=10, min_samples_split=5
            ),
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=100, random_state=42, max_depth=6, learning_rate=0.1
            ),
            "linear_regression": LinearRegression(),
            "ridge": Ridge(alpha=1.0),
            "lasso": Lasso(alpha=0.1),
            "svr": SVR(kernel="rbf", C=1.0, gamma="scale"),
            "neural_network": MLPRegressor(
                hidden_layer_sizes=(100, 50), random_state=42, max_iter=500
            ),
        }

    def train_ensemble_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
    ) -> Dict[str, Any]:
        """
        アンサンブルモデルの学習
        複数モデルを並列で学習
        """
        try:
            self.logger.info("アンサンブルモデルの学習を開始")

            trained_models = {}
            model_performance = {}

            # 各モデルの学習
            for model_name, model in self.models.items():
                try:
                    # モデルの学習
                    model.fit(X_train, y_train)
                    trained_models[model_name] = model

                    # 性能評価
                    if X_val is not None and y_val is not None:
                        y_pred = model.predict(X_val)
                        mse = mean_squared_error(y_val, y_pred)
                        mae = mean_absolute_error(y_val, y_pred)
                        r2 = r2_score(y_val, y_pred)

                        model_performance[model_name] = {
                            "mse": mse,
                            "mae": mae,
                            "r2": r2,
                            "score": r2,  # スコアとしてR²を使用
                        }
                    else:
                        # 検証データがない場合は学習データで評価
                        y_pred = model.predict(X_train)
                        r2 = r2_score(y_train, y_pred)
                        model_performance[model_name] = {"score": r2}

                    self.logger.info(
                        f"{model_name}の学習完了: R² = {model_performance[model_name].get('r2', 'N/A')}"
                    )

                except Exception as e:
                    self.logger.error(f"{model_name}の学習エラー: {e}")
                    continue

            # モデル性能の保存
            self.model_performance = model_performance
            self.trained_models = trained_models

            return {
                "trained_models": trained_models,
                "model_performance": model_performance,
                "training_successful": len(trained_models) > 0,
            }

        except Exception as e:
            self.logger.error(f"アンサンブルモデル学習エラー: {e}")
            return {"error": str(e)}

    def predict_ensemble(self, X: np.ndarray, method: str = None) -> Dict[str, Any]:
        """
        アンサンブル予測の実行
        複数モデルの予測を統合
        """
        try:
            if not hasattr(self, "trained_models"):
                return {"error": "モデルが学習されていません"}

            method = method or self.default_ensemble_method

            # 各モデルの予測
            individual_predictions = {}
            for model_name, model in self.trained_models.items():
                try:
                    prediction = model.predict(X)
                    individual_predictions[model_name] = prediction
                except Exception as e:
                    self.logger.error(f"{model_name}の予測エラー: {e}")
                    continue

            if not individual_predictions:
                return {"error": "有効な予測がありません"}

            # アンサンブル予測の実行
            if method == "weighted_average":
                ensemble_prediction = self._weighted_average_prediction(
                    individual_predictions
                )
            elif method == "stacking":
                ensemble_prediction = self._stacking_prediction(
                    individual_predictions, X
                )
            elif method == "voting":
                ensemble_prediction = self._voting_prediction(individual_predictions)
            else:
                ensemble_prediction = self._weighted_average_prediction(
                    individual_predictions
                )

            # 信頼度の計算
            confidence = self._calculate_ensemble_confidence(
                individual_predictions, ensemble_prediction
            )

            # 不確実性の計算
            uncertainty = self._calculate_uncertainty(individual_predictions)

            return {
                "ensemble_prediction": ensemble_prediction,
                "individual_predictions": individual_predictions,
                "confidence": confidence,
                "uncertainty": uncertainty,
                "method": method,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"アンサンブル予測エラー: {e}")
            return {"error": str(e)}

    def _weighted_average_prediction(
        self, individual_predictions: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """重み付き平均による予測"""
        try:
            # 重みの計算
            weights = self._calculate_model_weights()

            # 重み付き平均の計算
            weighted_sum = np.zeros_like(list(individual_predictions.values())[0])
            total_weight = 0

            for model_name, prediction in individual_predictions.items():
                weight = weights.get(model_name, 1.0)
                weighted_sum += prediction * weight
                total_weight += weight

            if total_weight > 0:
                ensemble_prediction = weighted_sum / total_weight
            else:
                ensemble_prediction = np.mean(
                    list(individual_predictions.values()), axis=0
                )

            return ensemble_prediction

        except Exception as e:
            self.logger.error(f"重み付き平均予測エラー: {e}")
            return np.mean(list(individual_predictions.values()), axis=0)

    def _stacking_prediction(
        self, individual_predictions: Dict[str, np.ndarray], X: np.ndarray
    ) -> np.ndarray:
        """スタッキングによる予測"""
        try:
            # メタ特徴量の作成
            meta_features = np.column_stack(list(individual_predictions.values()))

            # メタ学習器の学習（簡易版）
            from sklearn.linear_model import LinearRegression

            meta_learner = LinearRegression()

            # 簡易的なメタ学習器の学習（実際の実装では適切なデータ分割が必要）
            meta_learner.fit(
                meta_features, np.mean(list(individual_predictions.values()), axis=0)
            )

            # メタ学習器による予測
            ensemble_prediction = meta_learner.predict(meta_features)

            return ensemble_prediction

        except Exception as e:
            self.logger.error(f"スタッキング予測エラー: {e}")
            return self._weighted_average_prediction(individual_predictions)

    def _voting_prediction(
        self, individual_predictions: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """投票による予測"""
        try:
            # 各予測の平均
            ensemble_prediction = np.mean(list(individual_predictions.values()), axis=0)

            return ensemble_prediction

        except Exception as e:
            self.logger.error(f"投票予測エラー: {e}")
            return np.mean(list(individual_predictions.values()), axis=0)

    def _calculate_model_weights(self) -> Dict[str, float]:
        """モデル重みの計算"""
        try:
            if self.performance_based_weights and self.model_performance:
                # 性能ベースの重み
                weights = {}
                total_score = sum(
                    perf.get("score", 0) for perf in self.model_performance.values()
                )

                for model_name, performance in self.model_performance.items():
                    score = performance.get("score", 0)
                    if total_score > 0:
                        weights[model_name] = score / total_score
                    else:
                        weights[model_name] = 1.0 / len(self.model_performance)

                return weights
            else:
                # 均等重み
                equal_weight = 1.0 / len(self.models)
                return {name: equal_weight for name in self.models.keys()}

        except Exception as e:
            self.logger.error(f"モデル重み計算エラー: {e}")
            return {name: 1.0 for name in self.models.keys()}

    def _calculate_ensemble_confidence(
        self,
        individual_predictions: Dict[str, np.ndarray],
        ensemble_prediction: np.ndarray,
    ) -> float:
        """アンサンブル信頼度の計算"""
        try:
            # 予測の分散を計算
            predictions_array = np.array(list(individual_predictions.values()))
            prediction_variance = np.var(predictions_array, axis=0)

            # 信頼度の計算（分散の逆数）
            if len(predictions_array) > 1:
                confidence = 1.0 / (1.0 + np.mean(prediction_variance))
            else:
                confidence = 0.5

            return min(max(confidence, 0.0), 1.0)

        except Exception as e:
            self.logger.error(f"信頼度計算エラー: {e}")
            return 0.5

    def _calculate_uncertainty(
        self, individual_predictions: Dict[str, np.ndarray]
    ) -> float:
        """不確実性の計算"""
        try:
            # 予測の標準偏差
            predictions_array = np.array(list(individual_predictions.values()))
            prediction_std = np.std(predictions_array, axis=0)

            # 不確実性の計算
            uncertainty = np.mean(prediction_std)

            return uncertainty

        except Exception as e:
            self.logger.error(f"不確実性計算エラー: {e}")
            return 0.0

    def evaluate_ensemble_performance(
        self, X_test: np.ndarray, y_test: np.ndarray
    ) -> Dict[str, Any]:
        """アンサンブル性能の評価"""
        try:
            # アンサンブル予測の実行
            ensemble_result = self.predict_ensemble(X_test)

            if "error" in ensemble_result:
                return ensemble_result

            ensemble_prediction = ensemble_result["ensemble_prediction"]

            # 性能指標の計算
            mse = mean_squared_error(y_test, ensemble_prediction)
            mae = mean_absolute_error(y_test, ensemble_prediction)
            r2 = r2_score(y_test, ensemble_prediction)

            # 個別モデルとの比較
            individual_performance = {}
            for model_name, model in self.trained_models.items():
                try:
                    individual_prediction = model.predict(X_test)
                    individual_r2 = r2_score(y_test, individual_prediction)
                    individual_performance[model_name] = {
                        "r2": individual_r2,
                        "mse": mean_squared_error(y_test, individual_prediction),
                        "mae": mean_absolute_error(y_test, individual_prediction),
                    }
                except Exception as e:
                    self.logger.error(f"{model_name}の性能評価エラー: {e}")
                    continue

            return {
                "ensemble_performance": {"mse": mse, "mae": mae, "r2": r2},
                "individual_performance": individual_performance,
                "improvement_over_best_individual": r2
                - max(perf.get("r2", 0) for perf in individual_performance.values()),
                "confidence": ensemble_result["confidence"],
                "uncertainty": ensemble_result["uncertainty"],
            }

        except Exception as e:
            self.logger.error(f"アンサンブル性能評価エラー: {e}")
            return {"error": str(e)}

    def get_model_importance(self) -> Dict[str, float]:
        """モデル重要度の取得"""
        try:
            if not self.model_performance:
                return {}

            # 性能ベースの重要度
            total_score = sum(
                perf.get("score", 0) for perf in self.model_performance.values()
            )

            importance = {}
            for model_name, performance in self.model_performance.items():
                score = performance.get("score", 0)
                if total_score > 0:
                    importance[model_name] = score / total_score
                else:
                    importance[model_name] = 1.0 / len(self.model_performance)

            return importance

        except Exception as e:
            self.logger.error(f"モデル重要度計算エラー: {e}")
            return {}

    def optimize_ensemble(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
    ) -> Dict[str, Any]:
        """アンサンブルの最適化"""
        try:
            # 各アンサンブル手法の性能比較
            ensemble_methods = ["weighted_average", "stacking", "voting"]
            method_performance = {}

            for method in ensemble_methods:
                try:
                    # モデルの学習
                    training_result = self.train_ensemble_models(
                        X_train, y_train, X_val, y_val
                    )
                    if not training_result.get("training_successful", False):
                        continue

                    # 予測の実行
                    prediction_result = self.predict_ensemble(X_val, method)
                    if "error" in prediction_result:
                        continue

                    # 性能評価
                    ensemble_prediction = prediction_result["ensemble_prediction"]
                    r2 = r2_score(y_val, ensemble_prediction)

                    method_performance[method] = {
                        "r2": r2,
                        "confidence": prediction_result["confidence"],
                        "uncertainty": prediction_result["uncertainty"],
                    }

                except Exception as e:
                    self.logger.error(f"{method}の最適化エラー: {e}")
                    continue

            # 最適な手法の選択
            if method_performance:
                best_method = max(
                    method_performance.keys(), key=lambda x: method_performance[x]["r2"]
                )

                return {
                    "best_method": best_method,
                    "method_performance": method_performance,
                    "optimization_successful": True,
                }
            else:
                return {"error": "最適化に失敗しました", "optimization_successful": False}

        except Exception as e:
            self.logger.error(f"アンサンブル最適化エラー: {e}")
            return {"error": str(e)}
