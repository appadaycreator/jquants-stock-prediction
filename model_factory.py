#!/usr/bin/env python3
"""
機械学習モデルファクトリー
複数のモデルを設定ファイルから選択・作成できるモジュール
"""

import logging
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pandas as pd
import numpy as np
from unified_error_handler import get_unified_error_handler


class ModelFactory:
    """機械学習モデルのファクトリークラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_handler = get_unified_error_handler("ModelFactory")
        self.available_models = {
            "random_forest": self._create_random_forest,
            "xgboost": self._create_xgboost,
            "linear_regression": self._create_linear_regression,
            "ridge": self._create_ridge,
            "lasso": self._create_lasso,
            "svr": self._create_svr,
        }

    def get_available_models(self) -> List[str]:
        """利用可能なモデル一覧を取得"""
        return list(self.available_models.keys())

    def create_model(self, model_type: str, params: Dict[str, Any] = None):
        """
        指定されたタイプのモデルを作成

        Args:
            model_type (str): モデルタイプ
            params (Dict[str, Any]): モデルパラメータ

        Returns:
            機械学習モデルインスタンス
        """
        try:
            if model_type not in self.available_models:
                error_msg = f"サポートされていないモデルタイプ: {model_type}"
                self.error_handler.log_error(
                    ValueError(error_msg),
                    "モデル作成エラー",
                    {
                        "model_type": model_type,
                        "available_models": list(self.available_models.keys()),
                        "params": params,
                    },
                )
                raise ValueError(error_msg)

            params = params or {}
            self.logger.info(f"モデル作成: {model_type}, パラメータ: {params}")

            return self.available_models[model_type](params)

        except Exception as e:
            self.error_handler.log_error(
                e,
                f"モデル作成エラー ({model_type})",
                {"model_type": model_type, "params": params},
            )
            raise

    def _create_random_forest(self, params: Dict[str, Any]):
        """ランダムフォレスト回帰モデルを作成"""
        try:
            default_params = {
                "n_estimators": 100,
                "random_state": 42,
                "max_depth": None,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
            }
            default_params.update(params)
            return RandomForestRegressor(**default_params)
        except Exception as e:
            self.error_handler.handle_model_error(e, "RandomForest", "create", params)
            raise

    def _create_xgboost(self, params: Dict[str, Any]):
        """XGBoost回帰モデルを作成"""
        try:
            default_params = {
                "n_estimators": 100,
                "random_state": 42,
                "max_depth": 6,
                "learning_rate": 0.1,
                "subsample": 1.0,
                "colsample_bytree": 1.0,
            }
            default_params.update(params)
            return xgb.XGBRegressor(**default_params)
        except Exception as e:
            self.error_handler.handle_model_error(e, "XGBoost", "create", params)
            raise

    def _create_linear_regression(self, params: Dict[str, Any]):
        """線形回帰モデルを作成"""
        try:
            default_params = {"fit_intercept": True}
            default_params.update(params)
            return LinearRegression(**default_params)
        except Exception as e:
            self.error_handler.handle_model_error(
                e, "LinearRegression", "create", params
            )
            raise

    def _create_ridge(self, params: Dict[str, Any]):
        """Ridge回帰モデルを作成"""
        try:
            default_params = {"alpha": 1.0, "random_state": 42}
            default_params.update(params)
            return Ridge(**default_params)
        except Exception as e:
            self.error_handler.handle_model_error(e, "Ridge", "create", params)
            raise

    def _create_lasso(self, params: Dict[str, Any]):
        """Lasso回帰モデルを作成"""
        try:
            default_params = {"alpha": 1.0, "random_state": 42, "max_iter": 1000}
            default_params.update(params)
            return Lasso(**default_params)
        except Exception as e:
            self.error_handler.handle_model_error(e, "Lasso", "create", params)
            raise

    def _create_svr(self, params: Dict[str, Any]):
        """サポートベクター回帰モデルを作成"""
        try:
            default_params = {"kernel": "rbf", "C": 1.0, "gamma": "scale"}
            default_params.update(params)
            return SVR(**default_params)
        except Exception as e:
            self.error_handler.handle_model_error(e, "SVR", "create", params)
            raise


class ModelEvaluator:
    """モデル評価クラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_handler = get_unified_error_handler("ModelEvaluator")
        # self.specific_error_handler = get_specific_error_handler("ModelEvaluator")  # 統合アーキテクチャでは不要

    def evaluate_model(self, model, X_test, y_test, y_pred=None) -> Dict[str, float]:
        """
        モデルの評価を行う

        Args:
            model: 学習済みモデル
            X_test: テストデータの特徴量
            y_test: テストデータの正解値
            y_pred: 予測値（Noneの場合は自動で予測）

        Returns:
            Dict[str, float]: 評価指標辞書
        """
        try:
            if y_pred is None:
                y_pred = model.predict(X_test)

            metrics = {
                "mae": mean_absolute_error(y_test, y_pred),
                "mse": mean_squared_error(y_test, y_pred),
                "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                "r2": r2_score(y_test, y_pred),
            }

            self.logger.info(f"モデル評価結果: {metrics}")
            return metrics

        except Exception as e:
            self.error_handler.handle_model_error(
                e,
                type(model).__name__,
                "evaluation",
                {
                    "X_test_shape": X_test.shape if hasattr(X_test, "shape") else None,
                    "y_test_shape": y_test.shape if hasattr(y_test, "shape") else None,
                    "y_pred_provided": y_pred is not None,
                },
            )
            raise

    def get_feature_importance(self, model, feature_names: List[str]) -> pd.DataFrame:
        """
        特徴量重要度を取得

        Args:
            model: 学習済みモデル
            feature_names: 特徴量名のリスト

        Returns:
            pd.DataFrame: 特徴量重要度DataFrame
        """
        try:
            if hasattr(model, "feature_importances_"):
                importance = model.feature_importances_
            elif hasattr(model, "coef_"):
                # 線形モデルの場合は係数の絶対値を重要度とする
                importance = np.abs(model.coef_)
            else:
                self.logger.warning(
                    f"モデル {type(model).__name__} は特徴量重要度をサポートしていません"
                )
                return pd.DataFrame()

            df = pd.DataFrame(
                {"feature": feature_names, "importance": importance}
            ).sort_values("importance", ascending=False)

            return df

        except Exception as e:
            self.error_handler.handle_model_error(
                e,
                type(model).__name__,
                "feature_importance",
                {
                    "feature_names_count": len(feature_names) if feature_names else 0,
                    "model_has_feature_importances": hasattr(
                        model, "feature_importances_"
                    ),
                    "model_has_coef": hasattr(model, "coef_"),
                },
            )
            self.logger.error(f"特徴量重要度の取得に失敗: {e}")
            return pd.DataFrame()


class ModelComparator:
    """複数モデル比較クラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_handler = get_unified_error_handler("ModelComparator")
        # self.specific_error_handler = get_specific_error_handler("ModelComparator")  # 統合アーキテクチャでは不要
        self.factory = ModelFactory()
        self.evaluator = ModelEvaluator()

    def compare_models(
        self,
        models_config: Dict[str, Dict],
        X_train,
        X_test,
        y_train,
        y_test,
        feature_names: List[str] = None,
    ) -> pd.DataFrame:
        """
        複数モデルの性能比較

        Args:
            models_config: モデル設定辞書
            X_train: 学習用特徴量データ
            X_test: テスト用特徴量データ
            y_train: 学習用ターゲットデータ
            y_test: テスト用ターゲットデータ
            feature_names: 特徴量名リスト

        Returns:
            pd.DataFrame: 比較結果DataFrame
        """
        results = []

        # データサイズの確認
        assert len(X_train) == len(
            y_train
        ), f"X_train: {len(X_train)}, y_train: {len(y_train)}"
        assert len(X_test) == len(
            y_test
        ), f"X_test: {len(X_test)}, y_test: {len(y_test)}"

        for model_name, config in models_config.items():
            try:
                self.logger.info(f"モデル比較開始: {model_name}")

                # モデル作成・学習
                model_type = config.get("type", model_name)
                params = config.get("params", {})

                model = self.factory.create_model(model_type, params)
                model.fit(X_train, y_train)

                # 予測・評価
                y_pred = model.predict(X_test)
                metrics = self.evaluator.evaluate_model(model, X_test, y_test, y_pred)

                # 結果記録
                result = {"model_name": model_name, "model_type": model_type, **metrics}
                results.append(result)

                self.logger.info(f"モデル {model_name} 完了: MAE={metrics['mae']:.4f}")

            except Exception as e:
                self.error_handler.handle_model_error(
                    e,
                    model_name,
                    "training",
                    {
                        "model_type": model_type,
                        "params": params,
                        "X_train_shape": (
                            X_train.shape if hasattr(X_train, "shape") else None
                        ),
                        "y_train_shape": (
                            y_train.shape if hasattr(y_train, "shape") else None
                        ),
                    },
                )
                self.logger.error(f"モデル {model_name} でエラー: {e}")
                continue

        if not results:
            self.logger.warning("評価できたモデルがありません")
            return pd.DataFrame()

        df_results = pd.DataFrame(results).sort_values("mae")
        return df_results

    def get_best_model(self, results_df: pd.DataFrame, metric: str = "mae") -> str:
        """
        最良のモデル名を取得

        Args:
            results_df: 比較結果DataFrame
            metric: 評価指標名

        Returns:
            str: 最良のモデル名
        """
        if results_df.empty:
            return None

        if metric not in results_df.columns:
            self.logger.warning(f"指定された指標 {metric} が見つかりません")
            metric = "mae"  # デフォルトにフォールバック

        best_model = results_df.loc[results_df[metric].idxmin(), "model_name"]
        return best_model


def get_default_models_config() -> Dict[str, Dict]:
    """デフォルトのモデル設定を取得"""
    return {
        "random_forest": {
            "type": "random_forest",
            "params": {"n_estimators": 100, "max_depth": 10, "random_state": 42},
        },
        "xgboost": {
            "type": "xgboost",
            "params": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": 42,
            },
        },
        "linear_regression": {"type": "linear_regression", "params": {}},
        "ridge": {"type": "ridge", "params": {"alpha": 1.0, "random_state": 42}},
    }


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)

    factory = ModelFactory()
    print("利用可能なモデル:")
    for model in factory.get_available_models():
        print(f"  - {model}")

    # サンプルデータで各モデルをテスト
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split

    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 各モデルをテスト
    for model_type in factory.get_available_models():
        try:
            model = factory.create_model(model_type)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            print(f"  {model_type}: MAE = {mae:.4f}")
        except Exception as e:
            error_handler = get_unified_error_handler("main_test")
            error_handler.handle_model_error(
                e,
                model_type,
                "test",
                {
                    "X_train_shape": (
                        X_train.shape if hasattr(X_train, "shape") else None
                    ),
                    "y_train_shape": (
                        y_train.shape if hasattr(y_train, "shape") else None
                    ),
                    "X_test_shape": X_test.shape if hasattr(X_test, "shape") else None,
                    "y_test_shape": y_test.shape if hasattr(y_test, "shape") else None,
                },
            )
            print(f"  {model_type}: エラー - {e}")
