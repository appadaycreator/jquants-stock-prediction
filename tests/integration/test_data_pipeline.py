"""
データパイプラインの統合テスト
データ取得から予測までの全体的なフローをテスト
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from unittest.mock import patch, MagicMock
from technical_indicators import TechnicalIndicators
from model_factory import ModelFactory, ModelEvaluator
from config_loader import ConfigLoader


class TestDataPipeline:
    """データパイプラインの統合テスト"""

    def test_complete_pipeline(self, sample_stock_data):
        """完全なデータパイプラインのテスト"""
        # 1. 技術指標の計算
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)

        # 技術指標が追加されていることを確認
        assert len(processed_data.columns) > len(sample_stock_data.columns)

        # 2. 特徴量の準備
        features = ["SMA_5", "SMA_25", "Close_1d_ago", "Close_5d_ago"]
        target = "Close"

        # 利用可能な特徴量のみを選択
        available_features = [f for f in features if f in processed_data.columns]
        if not available_features:
            available_features = ["Open", "High", "Low", "Volume"]

        X = processed_data[available_features].dropna()
        y = processed_data[target].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        if min_len > 0:
            X = X.iloc[:min_len]
            y = y.iloc[:min_len]

            # 3. モデルの訓練と評価
            factory = ModelFactory()
            evaluator = ModelEvaluator()

            model = factory.create_model("linear_regression")
            model.fit(X, y)

            # 4. 予測の実行
            predictions = model.predict(X)

            # 5. 評価メトリクスの計算
            metrics = evaluator.evaluate_model(model, X, y, predictions)

            # 結果の検証
            assert len(predictions) == len(y)
            assert "mae" in metrics
            assert "mse" in metrics
            assert "r2" in metrics
            assert metrics["mae"] >= 0
            assert metrics["mse"] >= 0

    def test_pipeline_with_multiple_models(self, sample_stock_data):
        """複数モデルでのパイプラインテスト"""
        # 技術指標の計算
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)

        # 特徴量の準備
        features = ["Open", "High", "Low", "Volume"]
        target = "Close"

        X = processed_data[features].dropna()
        y = processed_data[target].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        if min_len > 0:
            X = X.iloc[:min_len]
            y = y.iloc[:min_len]

            # 複数モデルの比較
            factory = ModelFactory()
            evaluator = ModelEvaluator()

            models = ["linear_regression", "ridge", "lasso"]
            results = {}

            for model_name in models:
                model = factory.create_model(model_name)
                model.fit(X, y)
                predictions = model.predict(X)
                metrics = evaluator.evaluate_model(model, X, y, predictions)
                results[model_name] = metrics

            # 結果の検証
            assert len(results) == len(models)
            for model_name, metrics in results.items():
                assert "mae" in metrics
                assert "mse" in metrics
                assert "r2" in metrics

    def test_pipeline_with_config(self, sample_stock_data):
        """設定ファイルを使ったパイプラインテスト"""
        # 一時的な設定ファイルを作成
        config_data = {
            "preprocessing": {
                "input_file": "test.csv",
                "output_file": "processed.csv",
                "features": ["SMA_5", "SMA_25", "Close_1d_ago"],
            },
            "prediction": {
                "features": ["SMA_5", "SMA_25", "Close_1d_ago"],
                "target": "Close",
                "test_size": 0.2,
                "random_state": 42,
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config_data, f)
            config_path = f.name

        try:
            # 設定の読み込み
            config = ConfigLoader(config_path)
            preprocessing_config = config.get_preprocessing_config()
            prediction_config = config.get_prediction_config()

            # 技術指標の計算
            ti = TechnicalIndicators()
            processed_data = ti.calculate_all_indicators(sample_stock_data)

            # 設定で指定された特徴量を使用
            features = prediction_config.get(
                "features", ["Open", "High", "Low", "Volume"]
            )
            target = prediction_config.get("target", "Close")

            # 利用可能な特徴量のみを選択
            available_features = [f for f in features if f in processed_data.columns]
            if not available_features:
                available_features = ["Open", "High", "Low", "Volume"]

            X = processed_data[available_features].dropna()
            y = processed_data[target].dropna()

            # データサイズを揃える
            min_len = min(len(X), len(y))
            if min_len > 0:
                X = X.iloc[:min_len]
                y = y.iloc[:min_len]

                # モデルの訓練
                factory = ModelFactory()
                model = factory.create_model("linear_regression")
                model.fit(X, y)

                # 予測の実行
                predictions = model.predict(X)

                # 結果の検証
                assert len(predictions) == len(y)
                assert len(predictions) > 0
        finally:
            os.unlink(config_path)

    def test_pipeline_error_handling(self):
        """パイプラインのエラーハンドリングテスト"""
        # 無効なデータでのテスト
        invalid_data = pd.DataFrame(
            {
                "Date": ["invalid_date"],
                "Open": [np.nan],
                "High": [np.nan],
                "Low": [np.nan],
                "Close": [np.nan],
                "Volume": [np.nan],
            }
        )

        ti = TechnicalIndicators()

        # エラーが発生しても適切に処理されることを確認
        try:
            processed_data = ti.calculate_all_indicators(invalid_data)
            # エラーが発生しない場合は、結果が空でないことを確認
            assert not processed_data.empty
        except Exception as e:
            # エラーが発生した場合は、適切なエラーメッセージであることを確認
            assert isinstance(e, (ValueError, KeyError, TypeError))

    def test_pipeline_performance(self, sample_stock_data):
        """パイプラインのパフォーマンステスト"""
        import time

        # 大きなデータセットを作成
        large_data = pd.concat([sample_stock_data] * 10, ignore_index=True)

        start_time = time.time()

        # 技術指標の計算
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(large_data)

        # 特徴量の準備
        features = ["Open", "High", "Low", "Volume"]
        target = "Close"

        X = processed_data[features].dropna()
        y = processed_data[target].dropna()

        # データサイズを揃える
        min_len = min(len(X), len(y))
        if min_len > 0:
            X = X.iloc[:min_len]
            y = y.iloc[:min_len]

            # モデルの訓練
            factory = ModelFactory()
            model = factory.create_model("linear_regression")
            model.fit(X, y)

            # 予測の実行
            predictions = model.predict(X)

        end_time = time.time()
        execution_time = end_time - start_time

        # 実行時間が妥当な範囲内であることを確認（10秒以内）
        assert execution_time < 10.0
        assert len(predictions) > 0

    def test_pipeline_data_consistency(self, sample_stock_data):
        """パイプラインのデータ一貫性テスト"""
        # 技術指標の計算
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)

        # 元のデータが保持されていることを確認
        for col in sample_stock_data.columns:
            assert col in processed_data.columns

        # データの行数が変わっていないことを確認
        assert len(processed_data) == len(sample_stock_data)

        # 元のデータの値が変更されていないことを確認
        for col in sample_stock_data.columns:
            if col in processed_data.columns:
                pd.testing.assert_series_equal(
                    sample_stock_data[col], processed_data[col], check_names=False
                )

    def test_pipeline_with_different_data_sizes(self):
        """異なるデータサイズでのパイプラインテスト"""
        data_sizes = [10, 50, 100]

        for size in data_sizes:
            # 指定されたサイズのデータを作成
            dates = pd.date_range("2023-01-01", periods=size, freq="D")
            np.random.seed(42)

            prices = 100 + np.cumsum(np.random.normal(0, 1, size))

            data = pd.DataFrame(
                {
                    "Date": dates,
                    "Open": prices,
                    "High": prices * 1.02,
                    "Low": prices * 0.98,
                    "Close": prices,
                    "Volume": np.random.randint(1000, 10000, size),
                }
            )

            # パイプラインの実行
            ti = TechnicalIndicators()
            processed_data = ti.calculate_all_indicators(data)

            # 結果の検証
            assert len(processed_data) == size
            assert len(processed_data.columns) > len(data.columns)

            # 十分なデータがある場合はモデル訓練もテスト
            if size >= 20:
                features = ["Open", "High", "Low", "Volume"]
                target = "Close"

                X = processed_data[features].dropna()
                y = processed_data[target].dropna()

                min_len = min(len(X), len(y))
                if min_len > 0:
                    X = X.iloc[:min_len]
                    y = y.iloc[:min_len]

                    factory = ModelFactory()
                    model = factory.create_model("linear_regression")
                    model.fit(X, y)
                    predictions = model.predict(X)

                    assert len(predictions) == len(y)

    def test_pipeline_with_enhanced_data_generator(self):
        """強化されたデータジェネレーターを使用したパイプラインテスト"""
        from tests.fixtures.enhanced_test_data_generator import (
            EnhancedTestDataGenerator,
        )

        generator = EnhancedTestDataGenerator(seed=42)

        # 通常のデータ
        normal_data = generator.generate_stock_data(
            start_date="2023-01-01", end_date="2023-03-31", num_stocks=3
        )

        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(normal_data)

        assert processed_data is not None
        assert len(processed_data) > 0

        # データ検証
        validation_results = generator.validate_generated_data(processed_data)
        assert validation_results["has_required_columns"] is True

    def test_pipeline_with_corrupted_data(self):
        """破損データでのパイプラインテスト"""
        from tests.fixtures.enhanced_test_data_generator import (
            EnhancedTestDataGenerator,
        )

        generator = EnhancedTestDataGenerator(seed=42)

        # 正常なデータを生成
        normal_data = generator.generate_stock_data(
            start_date="2023-01-01", end_date="2023-03-31", num_stocks=2
        )

        # 破損データを生成
        corrupted_data = generator.generate_corrupted_data(
            normal_data, corruption_types=["missing_values", "outliers"]
        )

        # パイプラインの実行（エラーハンドリングをテスト）
        ti = TechnicalIndicators()

        try:
            processed_data = ti.calculate_all_indicators(corrupted_data)
            # 破損データでも処理が継続されることを確認
            assert processed_data is not None
        except Exception as e:
            # エラーが発生した場合も適切に処理されることを確認
            assert isinstance(e, (ValueError, KeyError, TypeError))

    def test_pipeline_with_edge_cases(self):
        """エッジケースでのパイプラインテスト"""
        from tests.fixtures.enhanced_test_data_generator import (
            EnhancedTestDataGenerator,
        )

        generator = EnhancedTestDataGenerator(seed=42)
        edge_cases = generator.generate_edge_case_data()

        ti = TechnicalIndicators()

        for case_name, data in edge_cases.items():
            if len(data) > 0:  # 空でないデータのみテスト
                try:
                    processed_data = ti.calculate_all_indicators(data)
                    # エッジケースでも処理が継続されることを確認
                    assert processed_data is not None
                except Exception as e:
                    # エラーが発生した場合も適切なエラータイプであることを確認
                    assert isinstance(e, (ValueError, KeyError, TypeError))

    def test_pipeline_with_market_scenarios(self):
        """市場シナリオでのパイプラインテスト"""
        from tests.fixtures.enhanced_test_data_generator import (
            EnhancedTestDataGenerator,
        )

        generator = EnhancedTestDataGenerator(seed=42)
        scenarios = generator.generate_market_scenarios()

        ti = TechnicalIndicators()
        factory = ModelFactory()

        for scenario_name, data in scenarios.items():
            # 技術指標の計算
            processed_data = ti.calculate_all_indicators(data)
            assert processed_data is not None

            # 十分なデータがある場合はモデル訓練もテスト
            if len(processed_data) > 20:
                features = ["Open", "High", "Low", "Volume"]
                target = "Close"

                X = processed_data[features].dropna()
                y = processed_data[target].dropna()

                min_len = min(len(X), len(y))
                if min_len > 10:
                    X = X.iloc[:min_len]
                    y = y.iloc[:min_len]

                    model = factory.create_model("linear_regression")
                    model.fit(X, y)
                    predictions = model.predict(X)

                    assert len(predictions) == len(y)

    def test_pipeline_stress_test(self):
        """ストレステスト"""
        from tests.fixtures.enhanced_test_data_generator import (
            EnhancedTestDataGenerator,
        )

        generator = EnhancedTestDataGenerator(seed=42)

        # 大きなデータセットを生成
        large_data = generator.generate_stress_test_data(size=5000)

        import time

        start_time = time.time()

        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(large_data)

        end_time = time.time()
        execution_time = end_time - start_time

        # 実行時間が妥当な範囲内であることを確認（30秒以内）
        assert execution_time < 30.0
        assert processed_data is not None
        assert len(processed_data) > 0

    def test_pipeline_with_anomaly_detection(self):
        """異常値検出でのパイプラインテスト"""
        from tests.fixtures.enhanced_test_data_generator import (
            EnhancedTestDataGenerator,
        )

        generator = EnhancedTestDataGenerator(seed=42)

        # 正常なデータを生成
        normal_data = generator.generate_stock_data(
            start_date="2023-01-01", end_date="2023-03-31", num_stocks=2
        )

        # 異常値データを生成
        anomaly_data = generator.generate_anomaly_data(normal_data)

        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(anomaly_data)

        assert processed_data is not None

        # 異常値が適切に処理されることを確認
        assert len(processed_data) > 0
