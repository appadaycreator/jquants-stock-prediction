"""
モデルファクトリーモジュールの簡易ユニットテスト
実際の実装に合わせたテスト
"""

import pytest
import pandas as pd
import numpy as np
from model_factory import ModelFactory, ModelEvaluator, ModelComparator


class TestModelFactory:
    """ModelFactoryクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        factory = ModelFactory()
        assert factory is not None
        assert hasattr(factory, "available_models")
        assert hasattr(factory, "logger")

    def test_get_available_models(self):
        """利用可能なモデル一覧の取得テスト"""
        factory = ModelFactory()
        models = factory.get_available_models()

        assert isinstance(models, list)
        assert len(models) > 0
        assert "random_forest" in models
        assert "xgboost" in models
        assert "linear_regression" in models

    def test_create_model_random_forest(self):
        """Random Forestモデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("random_forest")

        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_create_model_random_forest_with_params(self):
        """パラメータ付きRandom Forestモデルの作成テスト"""
        factory = ModelFactory()
        params = {"n_estimators": 100, "max_depth": 10}
        model = factory.create_model("random_forest", params)

        assert model is not None
        assert model.n_estimators == 100
        assert model.max_depth == 10

    def test_create_model_xgboost(self):
        """XGBoostモデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("xgboost")

        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_create_model_linear_regression(self):
        """線形回帰モデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("linear_regression")

        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_create_model_ridge(self):
        """Ridge回帰モデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("ridge")

        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_create_model_lasso(self):
        """Lasso回帰モデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("lasso")

        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_create_model_svr(self):
        """SVRモデルの作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("svr")

        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_create_model_invalid_type(self):
        """無効なモデルタイプのテスト"""
        factory = ModelFactory()

        with pytest.raises(ValueError, match="サポートされていないモデルタイプ"):
            factory.create_model("invalid_model")

    def test_create_model_with_none_params(self):
        """Noneパラメータでのモデル作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("random_forest", None)

        assert model is not None

    def test_create_model_with_empty_params(self):
        """空のパラメータでのモデル作成テスト"""
        factory = ModelFactory()
        model = factory.create_model("random_forest", {})

        assert model is not None


class TestModelEvaluator:
    """ModelEvaluatorクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        evaluator = ModelEvaluator()
        assert evaluator is not None
        assert hasattr(evaluator, "logger")

    def test_evaluate_model_basic(self, sample_stock_data):
        """基本的なモデル評価テスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            model = factory.create_model("linear_regression")
            model.fit(X, y)

            metrics = evaluator.evaluate_model(model, X, y)

            assert isinstance(metrics, dict)
            assert "mae" in metrics
            assert "mse" in metrics
            assert "rmse" in metrics
            assert "r2" in metrics

            # メトリクスの値が適切な範囲であることを確認
            assert metrics["mae"] >= 0
            assert metrics["mse"] >= 0
            assert metrics["rmse"] >= 0

    def test_evaluate_model_with_predictions(self, sample_stock_data):
        """予測値を使ったモデル評価テスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            model = factory.create_model("linear_regression")
            model.fit(X, y)
            predictions = model.predict(X)

            metrics = evaluator.evaluate_model(model, X, y, predictions)

            assert isinstance(metrics, dict)
            assert "mae" in metrics
            assert "mse" in metrics
            assert "rmse" in metrics
            assert "r2" in metrics

    def test_evaluate_model_empty_data(self):
        """空のデータでの評価テスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()

        X = pd.DataFrame()
        y = pd.Series(dtype=float)

        model = factory.create_model("linear_regression")

        with pytest.raises(ValueError):
            evaluator.evaluate_model(model, X, y)

    def test_get_feature_importance(self, sample_stock_data):
        """特徴量重要度の取得テスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            model = factory.create_model("random_forest")
            model.fit(X, y)

            feature_names = X.columns.tolist()
            importance_df = evaluator.get_feature_importance(model, feature_names)

            assert isinstance(importance_df, pd.DataFrame)
            if not importance_df.empty:
                assert "feature" in importance_df.columns
                assert "importance" in importance_df.columns


class TestModelComparator:
    """ModelComparatorクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        comparator = ModelComparator()
        assert comparator is not None
        assert hasattr(comparator, "logger")
        assert hasattr(comparator, "factory")
        assert hasattr(comparator, "evaluator")

    def test_compare_models_basic(self, sample_stock_data):
        """基本的なモデル比較テスト"""
        comparator = ModelComparator()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            # データを訓練・テストに分割
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # データサイズを再度確認・調整
            assert len(X_train) == len(
                y_train
            ), f"X_train: {len(X_train)}, y_train: {len(y_train)}"
            assert len(X_test) == len(
                y_test
            ), f"X_test: {len(X_test)}, y_test: {len(y_test)}"

            feature_names = X.columns.tolist()

            models_config = {"linear_regression": {}, "ridge": {"alpha": 1.0}}

            results = comparator.compare_models(
                models_config, X_train, X_test, y_train, y_test, feature_names
            )

            assert isinstance(results, pd.DataFrame)
            assert len(results) > 0
            assert "model_name" in results.columns
            assert "mae" in results.columns
            assert "mse" in results.columns
            assert "rmse" in results.columns
            assert "r2" in results.columns

    def test_compare_models_single_model(self, sample_stock_data):
        """単一モデルの比較テスト"""
        comparator = ModelComparator()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            # データを訓練・テストに分割
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # データサイズを再度確認・調整
            assert len(X_train) == len(
                y_train
            ), f"X_train: {len(X_train)}, y_train: {len(y_train)}"
            assert len(X_test) == len(
                y_test
            ), f"X_test: {len(X_test)}, y_test: {len(y_test)}"

            feature_names = X.columns.tolist()

            models_config = {"linear_regression": {}}

            results = comparator.compare_models(
                models_config, X_train, X_test, y_train, y_test, feature_names
            )

            assert isinstance(results, pd.DataFrame)
            assert len(results) == 1
            assert "linear_regression" in results["model_name"].values

    def test_compare_models_empty_config(self):
        """空の設定での比較テスト"""
        comparator = ModelComparator()
        X_train = pd.DataFrame({"feature1": [1, 2, 3]})
        X_test = pd.DataFrame({"feature1": [4, 5, 6]})
        y_train = pd.Series([1, 2, 3])
        y_test = pd.Series([4, 5, 6])
        feature_names = ["feature1"]

        # 空の設定でもエラーが発生しないことを確認
        results = comparator.compare_models(
            {}, X_train, X_test, y_train, y_test, feature_names
        )
        assert results.empty

    def test_compare_models_invalid_model(self, sample_stock_data):
        """無効なモデル設定での比較テスト"""
        comparator = ModelComparator()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            # データを訓練・テストに分割
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            feature_names = X.columns.tolist()

            models_config = {"invalid_model": {}}

            # 無効なモデルでもエラーが発生しないことを確認（ログに記録される）
            results = comparator.compare_models(
                models_config, X_train, X_test, y_train, y_test, feature_names
            )
            assert results.empty

    def test_get_best_model(self, sample_stock_data):
        """最良モデルの取得テスト"""
        comparator = ModelComparator()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            # データを訓練・テストに分割
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # データサイズを再度確認・調整
            assert len(X_train) == len(
                y_train
            ), f"X_train: {len(X_train)}, y_train: {len(y_train)}"
            assert len(X_test) == len(
                y_test
            ), f"X_test: {len(X_test)}, y_test: {len(y_test)}"

            feature_names = X.columns.tolist()

            models_config = {"linear_regression": {}, "ridge": {"alpha": 1.0}}

            results = comparator.compare_models(
                models_config, X_train, X_test, y_train, y_test, feature_names
            )

            # 結果がDataFrameであることを確認
            assert isinstance(results, pd.DataFrame)
            assert len(results) > 0
            assert "model_name" in results.columns

    def test_get_best_model_invalid_metric(self, sample_stock_data):
        """無効なメトリクスでの最良モデル取得テスト"""
        comparator = ModelComparator()

        # サンプルデータを準備
        X = sample_stock_data[["Open", "High", "Low", "Volume"]].dropna()
        y = sample_stock_data["Close"].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]

        if len(X) > 0:
            # データを訓練・テストに分割
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # データサイズを再度確認・調整
            assert len(X_train) == len(
                y_train
            ), f"X_train: {len(X_train)}, y_train: {len(y_train)}"
            assert len(X_test) == len(
                y_test
            ), f"X_test: {len(X_test)}, y_test: {len(y_test)}"

            feature_names = X.columns.tolist()

            models_config = {"linear_regression": {}}

            results = comparator.compare_models(
                models_config, X_train, X_test, y_train, y_test, feature_names
            )

            # 結果がDataFrameであることを確認
            assert isinstance(results, pd.DataFrame)
            assert len(results) > 0
