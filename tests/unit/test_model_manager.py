"""
ModelManagerのユニットテスト
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os

from core.model_manager import ModelManager


class TestModelManager:
    """ModelManagerのテストクラス"""

    def test_initialization_default(self):
        """デフォルト初期化テスト"""
        mm = ModelManager()
        assert mm.logger is None
        assert mm.error_handler is None

    def test_initialization_with_logger(self):
        """ロガー付き初期化テスト"""
        logger = Mock()
        mm = ModelManager(logger=logger)
        assert mm.logger == logger
        assert mm.error_handler is None

    def test_initialization_with_error_handler(self):
        """エラーハンドラー付き初期化テスト"""
        error_handler = Mock()
        mm = ModelManager(error_handler=error_handler)
        assert mm.logger is None
        assert mm.error_handler == error_handler

    def test_initialization_with_both(self):
        """ロガーとエラーハンドラー付き初期化テスト"""
        logger = Mock()
        error_handler = Mock()
        mm = ModelManager(logger=logger, error_handler=error_handler)
        assert mm.logger == logger
        assert mm.error_handler == error_handler

    def test_get_supported_models(self):
        """サポートされているモデル一覧取得テスト"""
        mm = ModelManager()
        models = mm.get_supported_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "random_forest" in models
        assert "linear_regression" in models
        assert "ridge" in models
        assert "lasso" in models

    def test_get_model_success(self):
        """モデル取得成功テスト"""
        mm = ModelManager()
        
        model = mm.get_model("random_forest")
        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_get_model_with_default(self):
        """デフォルトモデル取得テスト"""
        mm = ModelManager()

        # 存在しないモデル名を指定した場合、デフォルトのrandom_forestが返される
        model = mm.get_model("invalid_model")
        assert model is not None
        assert hasattr(model, "fit")
        assert hasattr(model, "predict")

    def test_get_model_invalid_type(self):
        """無効なモデルタイプテスト（デフォルトモデルが返される）"""
        mm = ModelManager()

        # 無効なモデル名でもデフォルトモデルが返される
        model = mm.get_model("invalid_model")
        assert model is not None

    def test_get_model_with_error_handler(self):
        """エラーハンドラー付きモデル取得テスト"""
        error_handler = Mock()
        mm = ModelManager(error_handler=error_handler)

        # 無効なモデル名でもデフォルトモデルが返される
        model = mm.get_model("invalid_model")
        assert model is not None

    def test_train_model_success(self):
        """モデル訓練成功テスト"""
        mm = ModelManager()

        # テストデータの準備
        X_train = pd.DataFrame(
            {"feature1": [1, 2, 3, 4, 5], "feature2": [2, 4, 6, 8, 10]}
        )
        y_train = pd.Series([10, 20, 30, 40, 50])

        trained_model = mm.train_model("random_forest", X_train, y_train)

        assert trained_model is not None

    def test_train_model_invalid_data(self):
        """無効データでのモデル訓練テスト"""
        mm = ModelManager()

        with pytest.raises(Exception):
            mm.train_model("random_forest", None, None)

    def test_train_model_with_logger(self):
        """ロガー付きモデル訓練テスト"""
        logger = Mock()
        mm = ModelManager(logger=logger)

        X_train = pd.DataFrame({"feature1": [1, 2, 3]})
        y_train = pd.Series([10, 20, 30])

        trained_model = mm.train_model("random_forest", X_train, y_train)

        assert trained_model is not None

    def test_make_predictions_success(self):
        """予測実行成功テスト"""
        mm = ModelManager()

        # テストデータの準備
        X_train = pd.DataFrame(
            {"feature1": [1, 2, 3, 4, 5], "feature2": [2, 4, 6, 8, 10]}
        )
        y_train = pd.Series([10, 20, 30, 40, 50])
        X_test = pd.DataFrame({"feature1": [6, 7], "feature2": [12, 14]})

        model = mm.train_model("random_forest", X_train, y_train)
        predictions = mm.make_predictions(model, X_test)

        assert predictions is not None
        assert len(predictions) == 2

    def test_make_predictions_invalid_model(self):
        """無効モデルでの予測テスト"""
        mm = ModelManager()

        X_test = pd.DataFrame({"feature1": [1, 2]})
        
        with pytest.raises(Exception):
            mm.make_predictions(None, X_test)

    def test_make_predictions_invalid_data(self):
        """無効データでの予測テスト"""
        mm = ModelManager()

        model = mm.get_model("random_forest")
        
        with pytest.raises(Exception):
            mm.make_predictions(model, None)

    def test_evaluate_model_success(self):
        """モデル評価成功テスト"""
        mm = ModelManager()

        # テストデータの準備
        X_train = pd.DataFrame(
            {"feature1": [1, 2, 3, 4, 5], "feature2": [2, 4, 6, 8, 10]}
        )
        y_train = pd.Series([10, 20, 30, 40, 50])
        X_val = pd.DataFrame({"feature1": [6, 7], "feature2": [12, 14]})
        y_val = pd.Series([60, 70])
        X_test = pd.DataFrame({"feature1": [8, 9], "feature2": [16, 18]})
        y_test = pd.Series([80, 90])

        model = mm.train_model("random_forest", X_train, y_train)

        evaluation = mm.evaluate_model(model, X_train, X_val, X_test, y_train, y_val, y_test)

        assert isinstance(evaluation, dict)
        assert "metrics" in evaluation
        assert "predictions" in evaluation
        assert "model_name" in evaluation

    def test_evaluate_model_invalid_model(self):
        """無効モデルでの評価テスト"""
        mm = ModelManager()

        X_train = pd.DataFrame({"feature1": [1, 2]})
        y_train = pd.Series([10, 20])
        X_val = pd.DataFrame({"feature1": [3, 4]})
        y_val = pd.Series([30, 40])
        X_test = pd.DataFrame({"feature1": [5, 6]})
        y_test = pd.Series([50, 60])

        with pytest.raises(Exception):
            mm.evaluate_model(None, X_train, X_val, X_test, y_train, y_val, y_test)

    def test_evaluate_model_invalid_data(self):
        """無効データでの評価テスト"""
        mm = ModelManager()

        model = mm.get_model("random_forest")
        
        with pytest.raises(Exception):
            mm.evaluate_model(model, None, None, None, None, None, None)

    def test_compare_models_success(self):
        """モデル比較成功テスト"""
        mm = ModelManager()

        # テストデータの準備
        X_train = pd.DataFrame(
            {"feature1": [1, 2, 3, 4, 5], "feature2": [2, 4, 6, 8, 10]}
        )
        y_train = pd.Series([10, 20, 30, 40, 50])
        X_val = pd.DataFrame({"feature1": [6, 7], "feature2": [12, 14]})
        y_val = pd.Series([60, 70])
        X_test = pd.DataFrame({"feature1": [8, 9], "feature2": [16, 18]})
        y_test = pd.Series([80, 90])

        results = mm.compare_models(X_train, X_val, X_test, y_train, y_val, y_test)

        assert isinstance(results, dict)
        assert "best_model" in results
        assert "results" in results
        assert "comparison_timestamp" in results

    def test_compare_models_invalid_data(self):
        """無効データでのモデル比較テスト"""
        mm = ModelManager()

        # 無効なデータでもデフォルト結果が返される
        results = mm.compare_models(None, None, None, None, None, None)
        assert isinstance(results, dict)
        assert "best_model" in results
        assert "results" in results

    def test_get_model_info_success(self):
        """モデル情報取得成功テスト"""
        mm = ModelManager()

        info = mm.get_model_info()

        assert isinstance(info, dict)
        assert "supported_models" in info
        assert "model_count" in info
        assert "timestamp" in info

    def test_get_supported_models_success(self):
        """サポートされているモデル一覧取得成功テスト"""
        mm = ModelManager()

        models = mm.get_supported_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "random_forest" in models
        assert "linear_regression" in models

    def test_get_model_definitions_success(self):
        """モデル定義取得成功テスト"""
        mm = ModelManager()

        # 内部メソッドをテストするため、直接アクセス
        definitions = mm._get_model_definitions()
        assert isinstance(definitions, dict)
        assert "random_forest" in definitions
        assert "linear_regression" in definitions
        assert "ridge" in definitions
        assert "lasso" in definitions

    def test_get_model_with_different_types(self):
        """異なるモデルタイプの取得テスト"""
        mm = ModelManager()

        # 各モデルタイプをテスト
        for model_name in ["random_forest", "linear_regression", "ridge", "lasso"]:
            model = mm.get_model(model_name)
            assert model is not None
            assert hasattr(model, "fit")
            assert hasattr(model, "predict")

    def test_train_model_with_different_types(self):
        """異なるモデルタイプでの訓練テスト"""
        mm = ModelManager()

        X_train = pd.DataFrame({"feature1": [1, 2, 3]})
        y_train = pd.Series([10, 20, 30])

        # 各モデルタイプをテスト
        for model_name in ["random_forest", "linear_regression", "ridge", "lasso"]:
            trained_model = mm.train_model(model_name, X_train, y_train)
            assert trained_model is not None
            assert hasattr(trained_model, "predict")

    def test_make_predictions_with_different_models(self):
        """異なるモデルでの予測テスト"""
        mm = ModelManager()

        X_train = pd.DataFrame({"feature1": [1, 2, 3]})
        y_train = pd.Series([10, 20, 30])
        X_test = pd.DataFrame({"feature1": [4, 5]})

        # 各モデルタイプをテスト
        for model_name in ["random_forest", "linear_regression", "ridge", "lasso"]:
            trained_model = mm.train_model(model_name, X_train, y_train)
            predictions = mm.make_predictions(trained_model, X_test)
            assert predictions is not None
            assert len(predictions) == 2

    def test_evaluate_model_with_different_models(self):
        """異なるモデルでの評価テスト"""
        mm = ModelManager()

        X_train = pd.DataFrame({"feature1": [1, 2, 3]})
        y_train = pd.Series([10, 20, 30])
        X_val = pd.DataFrame({"feature1": [4, 5]})
        y_val = pd.Series([40, 50])
        X_test = pd.DataFrame({"feature1": [6, 7]})
        y_test = pd.Series([60, 70])

        # 各モデルタイプをテスト
        for model_name in ["random_forest", "linear_regression", "ridge", "lasso"]:
            trained_model = mm.train_model(model_name, X_train, y_train)
            evaluation = mm.evaluate_model(trained_model, X_train, X_val, X_test, y_train, y_val, y_test)
            assert isinstance(evaluation, dict)
            assert "metrics" in evaluation
            assert "predictions" in evaluation

    def test_compare_models_with_different_models(self):
        """異なるモデルでの比較テスト"""
        mm = ModelManager()

        X_train = pd.DataFrame({"feature1": [1, 2, 3]})
        y_train = pd.Series([10, 20, 30])
        X_val = pd.DataFrame({"feature1": [4, 5]})
        y_val = pd.Series([40, 50])
        X_test = pd.DataFrame({"feature1": [6, 7]})
        y_test = pd.Series([60, 70])

        results = mm.compare_models(X_train, X_val, X_test, y_train, y_val, y_test)
        assert isinstance(results, dict)
        assert "best_model" in results
        assert "results" in results
        assert len(results["results"]) > 0

    def test_get_model_info_with_logger(self):
        """ロガー付きモデル情報取得テスト"""
        logger = Mock()
        mm = ModelManager(logger=logger)

        info = mm.get_model_info()

        assert info is not None
        assert isinstance(info, dict)

    def test_get_model_info_with_error_handler(self):
        """エラーハンドラー付きモデル情報取得テスト"""
        error_handler = Mock()
        mm = ModelManager(error_handler=error_handler)

        info = mm.get_model_info()
        assert info is not None
        assert isinstance(info, dict)

    def test_get_model_with_error_handling(self):
        """エラーハンドリング付きモデル取得テスト"""
        error_handler = Mock()
        mm = ModelManager(error_handler=error_handler)

        # 無効なモデルタイプでもデフォルトモデルが返される
        model = mm.get_model("invalid_model")
        assert model is not None

    def test_train_model_with_error_handling(self):
        """エラーハンドリング付きモデル訓練テスト"""
        error_handler = Mock()
        mm = ModelManager(error_handler=error_handler)

        # 無効なデータでテスト
        with pytest.raises(Exception):
            mm.train_model("random_forest", None, None)
