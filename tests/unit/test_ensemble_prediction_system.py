#!/usr/bin/env python3
"""
アンサンブル予測システムのテスト
"""

import numpy as np
from core.ensemble_prediction_system import EnsemblePredictionSystem


class TestEnsemblePredictionSystem:
    """アンサンブル予測システムのテストクラス"""

    def setup_method(self):
        """テスト前の準備"""
        self.config = {
            "ensemble_method": "weighted_average",
            "model_weights": {},
            "performance_based_weights": True,
            "confidence_threshold": 0.7,
            "uncertainty_threshold": 0.3,
        }
        self.system = EnsemblePredictionSystem(self.config)

    def test_initialization(self):
        """初期化テスト"""
        assert self.system.config == self.config
        assert self.system.default_ensemble_method == "weighted_average"
        assert self.system.confidence_threshold == 0.7
        assert self.system.uncertainty_threshold == 0.3
        assert len(self.system.models) == 7

    def test_initialize_models(self):
        """モデル初期化テスト"""
        models = self.system._initialize_models()

        assert "random_forest" in models
        assert "gradient_boosting" in models
        assert "linear_regression" in models
        assert "ridge" in models
        assert "lasso" in models
        assert "svr" in models
        assert "neural_network" in models

    def test_train_ensemble_models_success(self):
        """アンサンブルモデル学習成功テスト"""
        # テストデータの準備
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)
        X_val = np.random.randn(20, 5)
        y_val = np.random.randn(20)

        result = self.system.train_ensemble_models(X_train, y_train, X_val, y_val)

        assert result["training_successful"] is True
        assert "trained_models" in result
        assert "model_performance" in result
        assert len(result["trained_models"]) > 0

    def test_train_ensemble_models_without_validation(self):
        """検証データなしでの学習テスト"""
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        result = self.system.train_ensemble_models(X_train, y_train)

        assert result["training_successful"] is True
        assert "trained_models" in result
        assert "model_performance" in result

    def test_train_ensemble_models_error(self):
        """学習エラーテスト"""
        # 無効なデータで学習
        X_train = np.array([])
        y_train = np.array([])

        result = self.system.train_ensemble_models(X_train, y_train)

        assert result["training_successful"] is False

    def test_predict_ensemble_success(self):
        """アンサンブル予測成功テスト"""
        # 事前にモデルを学習
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        training_result = self.system.train_ensemble_models(X_train, y_train)

        if training_result["training_successful"]:
            X_test = np.random.randn(10, 5)
            result = self.system.predict_ensemble(X_test)

            assert "error" not in result
            assert "ensemble_prediction" in result
            assert "individual_predictions" in result
            assert "confidence" in result
            assert "uncertainty" in result
            assert "method" in result

    def test_predict_ensemble_no_trained_models(self):
        """学習されていないモデルでの予測テスト"""
        X_test = np.random.randn(10, 5)
        result = self.system.predict_ensemble(X_test)

        assert "error" in result
        assert "モデルが学習されていません" in result["error"]

    def test_weighted_average_prediction(self):
        """重み付き平均予測テスト"""
        individual_predictions = {
            "model1": np.array([1.0, 2.0, 3.0]),
            "model2": np.array([2.0, 3.0, 4.0]),
            "model3": np.array([3.0, 4.0, 5.0]),
        }

        result = self.system._weighted_average_prediction(individual_predictions)

        assert len(result) == 3
        assert isinstance(result, np.ndarray)

    def test_stacking_prediction(self):
        """スタッキング予測テスト"""
        individual_predictions = {
            "model1": np.array([1.0, 2.0]),
            "model2": np.array([2.0, 3.0]),
        }
        X = np.random.randn(2, 5)

        result = self.system._stacking_prediction(individual_predictions, X)

        assert len(result) == 2
        assert isinstance(result, np.ndarray)

    def test_voting_prediction(self):
        """投票予測テスト"""
        individual_predictions = {
            "model1": np.array([1.0, 2.0, 3.0]),
            "model2": np.array([2.0, 3.0, 4.0]),
            "model3": np.array([3.0, 4.0, 5.0]),
        }

        result = self.system._voting_prediction(individual_predictions)

        assert len(result) == 3
        assert isinstance(result, np.ndarray)

    def test_calculate_model_weights(self):
        """モデル重み計算テスト"""
        # 性能データを設定
        self.system.model_performance = {
            "model1": {"score": 0.8},
            "model2": {"score": 0.6},
            "model3": {"score": 0.4},
        }

        weights = self.system._calculate_model_weights()

        assert "model1" in weights
        assert "model2" in weights
        assert "model3" in weights
        assert abs(sum(weights.values()) - 1.0) < 0.01

    def test_calculate_ensemble_confidence(self):
        """アンサンブル信頼度計算テスト"""
        individual_predictions = {
            "model1": np.array([1.0, 2.0]),
            "model2": np.array([1.1, 2.1]),
            "model3": np.array([0.9, 1.9]),
        }
        ensemble_prediction = np.array([1.0, 2.0])

        confidence = self.system._calculate_ensemble_confidence(
            individual_predictions, ensemble_prediction
        )

        assert 0.0 <= confidence <= 1.0

    def test_calculate_uncertainty(self):
        """不確実性計算テスト"""
        individual_predictions = {
            "model1": np.array([1.0, 2.0]),
            "model2": np.array([1.1, 2.1]),
            "model3": np.array([0.9, 1.9]),
        }

        uncertainty = self.system._calculate_uncertainty(individual_predictions)

        assert uncertainty >= 0.0

    def test_evaluate_ensemble_performance(self):
        """アンサンブル性能評価テスト"""
        # 事前にモデルを学習
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        training_result = self.system.train_ensemble_models(X_train, y_train)

        if training_result["training_successful"]:
            X_test = np.random.randn(20, 5)
            y_test = np.random.randn(20)

            result = self.system.evaluate_ensemble_performance(X_test, y_test)

            assert "error" not in result
            assert "ensemble_performance" in result
            assert "individual_performance" in result
            assert "improvement_over_best_individual" in result

    def test_get_model_importance(self):
        """モデル重要度取得テスト"""
        # 性能データを設定
        self.system.model_performance = {
            "model1": {"score": 0.8},
            "model2": {"score": 0.6},
            "model3": {"score": 0.4},
        }

        importance = self.system.get_model_importance()

        assert "model1" in importance
        assert "model2" in importance
        assert "model3" in importance
        assert abs(sum(importance.values()) - 1.0) < 0.01

    def test_optimize_ensemble(self):
        """アンサンブル最適化テスト"""
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)
        X_val = np.random.randn(20, 5)
        y_val = np.random.randn(20)

        result = self.system.optimize_ensemble(X_train, y_train, X_val, y_val)

        assert "optimization_successful" in result
        if result["optimization_successful"]:
            assert "best_method" in result
            assert "method_performance" in result

    def test_optimize_ensemble_error(self):
        """アンサンブル最適化エラーテスト"""
        # 無効なデータで最適化
        X_train = np.array([])
        y_train = np.array([])
        X_val = np.array([])
        y_val = np.array([])

        result = self.system.optimize_ensemble(X_train, y_train, X_val, y_val)

        assert result["optimization_successful"] is False
        assert "error" in result

    def test_error_handling_in_prediction(self):
        """予測時のエラーハンドリングテスト"""
        # 学習されていないモデルでの予測
        X_test = np.random.randn(10, 5)
        result = self.system.predict_ensemble(X_test)

        assert "error" in result

    def test_error_handling_in_training(self):
        """学習時のエラーハンドリングテスト"""
        # 無効なデータで学習
        X_train = None
        y_train = None

        result = self.system.train_ensemble_models(X_train, y_train)

        # エラーが発生するか、学習が失敗することを確認
        assert "error" in result or result["training_successful"] == False

    def test_ensemble_methods(self):
        """アンサンブル手法テスト"""
        # 事前にモデルを学習
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        training_result = self.system.train_ensemble_models(X_train, y_train)

        if training_result["training_successful"]:
            X_test = np.random.randn(10, 5)

            # 各手法をテスト
            for method in ["weighted_average", "stacking", "voting"]:
                result = self.system.predict_ensemble(X_test, method)
                assert "error" not in result
                assert result["method"] == method

    def test_config_validation(self):
        """設定検証テスト"""
        # 無効な設定
        invalid_config = {
            "ensemble_method": "invalid_method",
            "confidence_threshold": -1.0,
            "uncertainty_threshold": 2.0,
        }

        system = EnsemblePredictionSystem(invalid_config)

        # デフォルト値が使用されることを確認
        assert system.default_ensemble_method == "weighted_average"
        assert system.confidence_threshold == 0.7
        assert system.uncertainty_threshold == 0.3

    def test_performance_based_weights(self):
        """性能ベース重みテスト"""
        # 性能ベース重みを無効化
        self.system.performance_based_weights = False

        weights = self.system._calculate_model_weights()

        # 均等重みが使用されることを確認
        expected_weight = 1.0 / len(self.system.models)
        for weight in weights.values():
            assert abs(weight - expected_weight) < 0.01

    def test_empty_predictions_handling(self):
        """空の予測処理テスト"""
        individual_predictions = {}

        result = self.system._weighted_average_prediction(individual_predictions)

        # エラーが発生しないことを確認（空の場合はNaNが返される）
        assert isinstance(result, np.ndarray) or np.isnan(result)

    def test_single_model_prediction(self):
        """単一モデル予測テスト"""
        individual_predictions = {
            "model1": np.array([1.0, 2.0, 3.0]),
        }

        result = self.system._weighted_average_prediction(individual_predictions)

        assert len(result) == 3
        assert np.array_equal(result, individual_predictions["model1"])

    def test_model_weights_edge_cases(self):
        """モデル重みエッジケーステスト"""
        # ゼロスコアの場合
        self.system.model_performance = {
            "model1": {"score": 0.0},
            "model2": {"score": 0.0},
        }

        weights = self.system._calculate_model_weights()

        assert "model1" in weights
        assert "model2" in weights
        assert abs(sum(weights.values()) - 1.0) < 0.01

    def test_confidence_calculation_edge_cases(self):
        """信頼度計算エッジケーステスト"""
        # 単一予測の場合
        individual_predictions = {
            "model1": np.array([1.0, 2.0]),
        }
        ensemble_prediction = np.array([1.0, 2.0])

        confidence = self.system._calculate_ensemble_confidence(
            individual_predictions, ensemble_prediction
        )

        assert confidence == 0.5  # デフォルト値

    def test_uncertainty_calculation_edge_cases(self):
        """不確実性計算エッジケーステスト"""
        # 空の予測
        individual_predictions = {}

        uncertainty = self.system._calculate_uncertainty(individual_predictions)

        # 空の場合はNaNが返される可能性がある
        assert uncertainty == 0.0 or np.isnan(uncertainty)

    def test_ensemble_prediction_with_different_methods(self):
        """異なる手法でのアンサンブル予測テスト"""
        # 事前にモデルを学習
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        training_result = self.system.train_ensemble_models(X_train, y_train)

        if training_result["training_successful"]:
            X_test = np.random.randn(10, 5)

            # 各手法での予測
            methods = ["weighted_average", "stacking", "voting"]
            results = {}

            for method in methods:
                result = self.system.predict_ensemble(X_test, method)
                if "error" not in result:
                    results[method] = result["ensemble_prediction"]

            # 各手法で異なる結果が得られることを確認
            if len(results) > 1:
                predictions = list(results.values())
                # 少なくとも1つの手法で異なる結果が得られる
                assert any(
                    not np.array_equal(predictions[0], pred) for pred in predictions[1:]
                )

    def test_model_performance_tracking(self):
        """モデル性能追跡テスト"""
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)
        X_val = np.random.randn(20, 5)
        y_val = np.random.randn(20)

        result = self.system.train_ensemble_models(X_train, y_train, X_val, y_val)

        if result["training_successful"]:
            assert "model_performance" in result
            assert len(result["model_performance"]) > 0

            # 各モデルの性能データを確認
            for model_name, performance in result["model_performance"].items():
                assert "score" in performance
                assert isinstance(performance["score"], (int, float))

    def test_ensemble_prediction_consistency(self):
        """アンサンブル予測一貫性テスト"""
        # 事前にモデルを学習
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        training_result = self.system.train_ensemble_models(X_train, y_train)

        if training_result["training_successful"]:
            X_test = np.random.randn(10, 5)

            # 同じデータで複数回予測
            result1 = self.system.predict_ensemble(X_test)
            result2 = self.system.predict_ensemble(X_test)

            if "error" not in result1 and "error" not in result2:
                # 結果が一貫していることを確認
                assert np.allclose(
                    result1["ensemble_prediction"], result2["ensemble_prediction"]
                )

    def test_confidence_threshold_validation(self):
        """信頼度閾値検証テスト"""
        # 信頼度閾値を設定
        self.system.confidence_threshold = 0.8

        # 予測実行
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        training_result = self.system.train_ensemble_models(X_train, y_train)

        if training_result["training_successful"]:
            X_test = np.random.randn(10, 5)
            result = self.system.predict_ensemble(X_test)

            if "error" not in result:
                assert "confidence" in result
                assert 0.0 <= result["confidence"] <= 1.0

    def test_uncertainty_threshold_validation(self):
        """不確実性閾値検証テスト"""
        # 不確実性閾値を設定
        self.system.uncertainty_threshold = 0.5

        # 予測実行
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)

        training_result = self.system.train_ensemble_models(X_train, y_train)

        if training_result["training_successful"]:
            X_test = np.random.randn(10, 5)
            result = self.system.predict_ensemble(X_test)

            if "error" not in result:
                assert "uncertainty" in result
                assert result["uncertainty"] >= 0.0
