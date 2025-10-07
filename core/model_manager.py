#!/usr/bin/env python3
"""
モデル管理システム
機械学習モデルの定義、学習、評価を管理
"""

import numpy as np
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime


class ModelManager:
    """機械学習モデルの管理クラス"""

    def __init__(self, logger=None, error_handler=None):
        """初期化"""
        self.logger = logger
        self.error_handler = error_handler
        self.model_definitions = self._get_model_definitions()

    def _get_model_definitions(self) -> Dict[str, Any]:
        """モデル定義の取得"""
        return {
            "random_forest": RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
            ),
            "linear_regression": LinearRegression(),
            "ridge": Ridge(alpha=1.0),
            "lasso": Lasso(alpha=0.1),
        }

    def get_model(self, model_name: str) -> Any:
        """指定されたモデルの取得"""
        return self.model_definitions.get(
            model_name, self.model_definitions["random_forest"]
        )

    def train_model(self, model_name: str, X_train, y_train) -> Any:
        """モデルの学習"""
        try:
            model = self.get_model(model_name)
            model.fit(X_train, y_train)
            return model
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, model_name, "学習")
            raise

    def make_predictions(self, model: Any, X_data) -> np.ndarray:
        """予測の実行"""
        try:
            return model.predict(X_data)
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "予測", "実行")
            raise

    def evaluate_model(
        self, model: Any, X_train, X_val, X_test, y_train, y_val, y_test
    ) -> Dict[str, Any]:
        """モデルの評価"""
        try:
            # 各データセットでの予測
            predictions = {
                "train": self.make_predictions(model, X_train),
                "val": self.make_predictions(model, X_val),
                "test": self.make_predictions(model, X_test),
            }

            # 評価指標の計算
            metrics = self._calculate_metrics(y_train, y_val, y_test, predictions)

            return {
                "predictions": predictions,
                "metrics": metrics,
                "model_name": type(model).__name__,
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "評価", "実行")
            raise

    def _calculate_metrics(
        self, y_train, y_val, y_test, predictions: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """評価指標の計算"""
        return {
            "train_mae": mean_absolute_error(y_train, predictions["train"]),
            "val_mae": mean_absolute_error(y_val, predictions["val"]),
            "test_mae": mean_absolute_error(y_test, predictions["test"]),
            "train_rmse": np.sqrt(mean_squared_error(y_train, predictions["train"])),
            "val_rmse": np.sqrt(mean_squared_error(y_val, predictions["val"])),
            "test_rmse": np.sqrt(mean_squared_error(y_test, predictions["test"])),
            "train_r2": r2_score(y_train, predictions["train"]),
            "val_r2": r2_score(y_val, predictions["val"]),
            "test_r2": r2_score(y_test, predictions["test"]),
        }

    def compare_models(
        self, X_train, X_val, X_test, y_train, y_val, y_test
    ) -> Dict[str, Any]:
        """複数モデルの比較"""
        try:
            results = self._train_and_evaluate_models(
                X_train, X_val, X_test, y_train, y_val, y_test
            )

            if results:
                best_result = self._select_best_model(results)
                return self._create_comparison_result(best_result, results)
            else:
                return self._create_fallback_result()

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_model_error(e, "モデル比較", "実行")
            return {"best_model": "random_forest", "results": []}

    def _select_best_model(self, results: List[Dict]) -> Dict:
        """最優秀モデルの選択"""
        # 検証データでのMAEが最小のモデルを選択
        best_result = min(results, key=lambda x: x["metrics"]["val_mae"])

        if self.logger:
            self.logger.log_info(
                f"🏆 最優秀モデル: {best_result['model_name']} "
                f"(検証MAE: {best_result['metrics']['val_mae']:.4f})"
            )

        return best_result

    def _train_and_evaluate_models(
        self, X_train, X_val, X_test, y_train, y_val, y_test
    ) -> List[Dict]:
        """モデルの学習と評価"""
        results = []

        for model_name in self.model_definitions.keys():
            try:
                model = self.train_model(model_name, X_train, y_train)
                evaluation = self.evaluate_model(
                    model, X_train, X_val, X_test, y_train, y_val, y_test
                )
                evaluation["model_name"] = model_name
                results.append(evaluation)
            except Exception as e:
                if self.logger:
                    self.logger.log_warning(f"モデル {model_name} の学習に失敗: {e}")
                continue

        return results

    def _create_comparison_result(
        self, best_result: Dict, results: List[Dict]
    ) -> Dict[str, Any]:
        """比較結果の作成"""
        return {
            "best_model": best_result["model_name"],
            "results": results,
            "comparison_timestamp": datetime.now().isoformat(),
        }

    def _create_fallback_result(self) -> Dict[str, Any]:
        """フォールバック結果の作成"""
        if self.logger:
            self.logger.log_warning(
                "有効なモデルが見つかりませんでした。デフォルトモデルを使用します。"
            )
        return {"best_model": "random_forest", "results": []}

    def get_supported_models(self) -> List[str]:
        """サポートされているモデル一覧の取得"""
        return list(self.model_definitions.keys())

    def get_model_info(self) -> Dict[str, Any]:
        """モデル情報の取得"""
        return {
            "supported_models": self.get_supported_models(),
            "model_count": len(self.model_definitions),
            "timestamp": datetime.now().isoformat(),
        }
