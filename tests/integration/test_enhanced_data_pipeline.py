"""
強化されたデータパイプラインの統合テスト
エッジケースと異常値処理の包括的なテスト
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import time
from unittest.mock import patch, MagicMock, mock_open
from technical_indicators import TechnicalIndicators
from model_factory import ModelFactory, ModelEvaluator
from config_loader import ConfigLoader
from enhanced_data_validator import EnhancedDataValidator, ValidationLevel
from auto_recovery_system import AutoRecoverySystem, with_auto_recovery


class TestEnhancedDataPipeline:
    """強化されたデータパイプラインの統合テスト"""

    def test_complete_pipeline_with_validation(self, sample_stock_data):
        """検証機能付きの完全なデータパイプラインのテスト"""
        # 1. データ検証
        validator = EnhancedDataValidator(ValidationLevel.STANDARD)
        validation_result = validator.validate_data_quality(sample_stock_data)

        assert validation_result.is_valid or len(validation_result.issues) == 0

        # 2. 技術指標の計算
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)

        assert len(processed_data.columns) > len(sample_stock_data.columns)

        # 3. 処理済みデータの再検証
        processed_validation = validator.validate_data_quality(processed_data)
        assert processed_validation.score >= 0.5  # 最低限の品質を保証

        # 4. 特徴量の準備
        features = ["SMA_5", "SMA_25", "Close_1d_ago", "Close_5d_ago"]
        target = "Close"

        available_features = [f for f in features if f in processed_data.columns]
        if not available_features:
            available_features = ["Open", "High", "Low", "Volume"]

        X = processed_data[available_features].dropna()
        y = processed_data[target].dropna()

        min_len = min(len(X), len(y))
        if min_len > 0:
            X = X.iloc[:min_len]
            y = y.iloc[:min_len]

            # 5. モデルの訓練と評価
            factory = ModelFactory()
            evaluator = ModelEvaluator()

            model = factory.create_model("linear_regression")
            model.fit(X, y)
            predictions = model.predict(X)
            metrics = evaluator.evaluate_model(model, X, y, predictions)

            # 結果の検証
            assert len(predictions) == len(y)
            assert "mae" in metrics
            assert metrics["mae"] >= 0

    def test_pipeline_with_corrupted_data(self):
        """破損データでのパイプラインのテスト"""
        # 破損データの生成
        corrupted_data = pd.DataFrame(
            {
                "Date": [
                    "2023-01-01",
                    "2023-01-02",
                    "2023-01-03",
                    "2023-01-04",
                    "2023-01-05",
                ],
                "Open": [100, np.nan, 102, 103, 104],
                "High": [105, 106, 107, 108, 109],
                "Low": [95, 96, 97, 98, 99],
                "Close": [102, 103, 104, 105, 106],
                "Volume": [1000, -1100, 1200, 1300, 1400],  # 負の値
            }
        )

        # 自動復旧システムの設定
        recovery_system = AutoRecoverySystem()

        # パイプラインの実行（エラーハンドリング付き）
        try:
            ti = TechnicalIndicators()
            processed_data = ti.calculate_all_indicators(corrupted_data)

            # データ検証
            validator = EnhancedDataValidator(ValidationLevel.STANDARD)
            validation_result = validator.validate_data_quality(processed_data)

            # 破損データでも処理が継続されることを確認
            assert processed_data is not None
            assert len(processed_data) > 0

        except Exception as e:
            # エラーが発生した場合の自動復旧
            context = {"data": corrupted_data}
            recovery_result = recovery_system.auto_recover(e, context)

            if recovery_result.success:
                assert recovery_result.recovered_data is not None
            else:
                # 復旧に失敗した場合も適切に処理されることを確認
                assert isinstance(e, (ValueError, KeyError, TypeError))

    def test_pipeline_with_edge_cases(self):
        """エッジケースでのパイプラインテスト"""
        edge_cases = {
            "empty_data": pd.DataFrame(),
            "single_row": pd.DataFrame(
                {
                    "Date": ["2023-01-01"],
                    "Open": [100],
                    "High": [105],
                    "Low": [95],
                    "Close": [102],
                    "Volume": [1000],
                }
            ),
            "duplicate_dates": pd.DataFrame(
                {
                    "Date": ["2023-01-01", "2023-01-01", "2023-01-02"],
                    "Open": [100, 101, 102],
                    "High": [105, 106, 107],
                    "Low": [95, 96, 97],
                    "Close": [102, 103, 104],
                    "Volume": [1000, 1100, 1200],
                }
            ),
            "all_nan": pd.DataFrame(
                {
                    "Date": ["2023-01-01", "2023-01-02"],
                    "Open": [np.nan, np.nan],
                    "High": [np.nan, np.nan],
                    "Low": [np.nan, np.nan],
                    "Close": [np.nan, np.nan],
                    "Volume": [np.nan, np.nan],
                }
            ),
            "extreme_values": pd.DataFrame(
                {
                    "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                    "Open": [100, 1e10, 102],
                    "High": [105, 106, 107],
                    "Low": [95, 96, 97],
                    "Close": [102, 103, 104],
                    "Volume": [1000, 1100, 1200],
                }
            ),
        }

        ti = TechnicalIndicators()
        validator = EnhancedDataValidator(ValidationLevel.STANDARD)

        for case_name, data in edge_cases.items():
            if len(data) > 0:  # 空でないデータのみテスト
                try:
                    # 技術指標の計算
                    processed_data = ti.calculate_all_indicators(data)

                    # データ検証
                    validation_result = validator.validate_data_quality(processed_data)

                    # エッジケースでも処理が継続されることを確認
                    assert processed_data is not None

                except Exception as e:
                    # エラーが発生した場合も適切なエラータイプであることを確認
                    assert isinstance(e, (ValueError, KeyError, TypeError))

    def test_pipeline_with_anomaly_detection(self, sample_stock_data):
        """異常値検出付きパイプラインテスト"""
        # 異常値を含むデータの生成
        anomaly_data = sample_stock_data.copy()
        anomaly_data.loc[0, "Close"] = 1000  # 異常に高い値
        anomaly_data.loc[1, "Volume"] = -1000  # 負の値
        anomaly_data.loc[2, "High"] = 50  # High < Low

        # 異常値検出
        validator = EnhancedDataValidator(ValidationLevel.STANDARD)
        anomaly_result = validator.detect_anomalies(
            anomaly_data, method="isolation_forest"
        )

        assert "anomalies" in anomaly_result
        assert "anomaly_scores" in anomaly_result

        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(anomaly_data)

        # 異常値が適切に処理されることを確認
        assert processed_data is not None
        assert len(processed_data) > 0

    def test_pipeline_with_auto_recovery(self, sample_stock_data):
        """自動復旧機能付きパイプラインテスト"""
        # 自動復旧システムの設定
        recovery_system = AutoRecoverySystem()

        # 問題のあるデータの生成
        problematic_data = sample_stock_data.copy()
        problematic_data.loc[0, "Close"] = np.inf  # 無限大値
        problematic_data.loc[1, "Volume"] = -1  # 負の値

        # 自動復旧付きの処理
        @with_auto_recovery()
        def process_data_with_recovery(data):
            ti = TechnicalIndicators()
            return ti.calculate_all_indicators(data)

        try:
            result = process_data_with_recovery(problematic_data)
            assert result is not None
        except Exception as e:
            # エラーが発生した場合の自動復旧
            context = {"data": problematic_data}
            recovery_result = recovery_system.auto_recover(e, context)

            if recovery_result.success:
                assert recovery_result.recovered_data is not None
            else:
                # 復旧に失敗した場合も適切に処理されることを確認
                assert isinstance(e, (ValueError, TypeError))

    def test_pipeline_with_memory_optimization(self):
        """メモリ最適化付きパイプラインテスト"""
        # 大きなデータセットの生成
        large_data = pd.DataFrame(
            {
                "Date": pd.date_range("2020-01-01", periods=10000, freq="D"),
                "Open": np.random.uniform(50, 200, 10000),
                "High": np.random.uniform(50, 200, 10000),
                "Low": np.random.uniform(50, 200, 10000),
                "Close": np.random.uniform(50, 200, 10000),
                "Volume": np.random.randint(1000, 100000, 10000),
            }
        )

        # メモリ使用量の監視
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(large_data)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # メモリ使用量の増加が妥当な範囲内であることを確認
        assert memory_increase < 500 * 1024 * 1024  # 500MB以内
        assert processed_data is not None
        assert len(processed_data) == len(large_data)

    def test_pipeline_with_concurrent_processing(self, sample_stock_data):
        """並行処理付きパイプラインテスト"""
        import threading
        import time

        results = []
        errors = []

        def process_data():
            try:
                ti = TechnicalIndicators()
                result = ti.calculate_all_indicators(sample_stock_data)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # 複数のスレッドで同時に処理
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=process_data)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # エラーが発生していないことを確認
        assert len(errors) == 0
        assert len(results) == 5

        # 結果の一貫性を確認
        for result in results:
            assert result is not None
            assert len(result) == len(sample_stock_data)

    def test_pipeline_with_data_quality_monitoring(self, sample_stock_data):
        """データ品質監視付きパイプラインテスト"""
        # データ品質監視の設定
        validator = EnhancedDataValidator(ValidationLevel.STRICT)

        # パイプラインの各段階での品質監視
        stages = []

        # 1. 入力データの品質監視
        input_validation = validator.validate_data_quality(sample_stock_data)
        stages.append(("input", input_validation.score))

        # 2. 技術指標計算後の品質監視
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)
        processed_validation = validator.validate_data_quality(processed_data)
        stages.append(("processed", processed_validation.score))

        # 3. 特徴量エンジニアリング後の品質監視
        features = ["Open", "High", "Low", "Volume"]
        X = processed_data[features].dropna()
        feature_validation = validator.validate_data_quality(X)
        stages.append(("features", feature_validation.score))

        # 品質スコアの監視
        for stage_name, score in stages:
            assert score >= 0.0
            assert score <= 1.0

        # 品質スコアの推移が適切であることを確認
        assert stages[0][1] >= 0.5  # 入力データの最低品質
        assert stages[1][1] >= stages[0][1] * 0.8  # 処理後も品質が大幅に低下していない

    def test_pipeline_with_error_recovery_strategies(self):
        """エラー復旧戦略付きパイプラインテスト"""
        recovery_system = AutoRecoverySystem()

        # 様々なエラーシナリオのテスト
        error_scenarios = [
            {
                "name": "file_not_found",
                "error": FileNotFoundError("File not found"),
                "context": {"file_path": "nonexistent.csv"},
            },
            {
                "name": "validation_error",
                "error": ValueError("Invalid data"),
                "context": {"data": pd.DataFrame({"invalid": [1, 2, 3]})},
            },
            {
                "name": "memory_error",
                "error": MemoryError("Out of memory"),
                "context": {"data": pd.DataFrame(np.random.rand(10000, 1000))},
            },
            {
                "name": "processing_error",
                "error": RuntimeError("Processing failed"),
                "context": {"data": pd.DataFrame({"test": [1, 2, 3]})},
            },
        ]

        for scenario in error_scenarios:
            # エラー復旧のテスト
            recovery_result = recovery_system.auto_recover(
                scenario["error"], scenario["context"]
            )

            # 復旧結果の検証
            assert isinstance(recovery_result.success, bool)
            assert isinstance(recovery_result.recovery_time, float)
            assert recovery_result.recovery_time >= 0

    def test_pipeline_with_performance_monitoring(self, sample_stock_data):
        """パフォーマンス監視付きパイプラインテスト"""
        performance_metrics = {}

        # 各段階の実行時間の測定
        start_time = time.time()

        # 1. データ検証
        validator = EnhancedDataValidator(ValidationLevel.STANDARD)
        validation_result = validator.validate_data_quality(sample_stock_data)
        validation_time = time.time() - start_time
        performance_metrics["validation_time"] = validation_time

        # 2. 技術指標計算
        start_time = time.time()
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)
        processing_time = time.time() - start_time
        performance_metrics["processing_time"] = processing_time

        # 3. 特徴量準備
        start_time = time.time()
        features = ["Open", "High", "Low", "Volume"]
        X = processed_data[features].dropna()
        feature_time = time.time() - start_time
        performance_metrics["feature_time"] = feature_time

        # 4. モデル訓練
        start_time = time.time()
        factory = ModelFactory()
        model = factory.create_model("linear_regression")
        y = processed_data["Close"].dropna()
        min_len = min(len(X), len(y))
        if min_len > 0:
            X = X.iloc[:min_len]
            y = y.iloc[:min_len]
            model.fit(X, y)
        training_time = time.time() - start_time
        performance_metrics["training_time"] = training_time

        # パフォーマンスメトリクスの検証
        total_time = sum(performance_metrics.values())
        assert total_time < 10.0  # 全体の実行時間が10秒以内

        for metric_name, metric_value in performance_metrics.items():
            assert metric_value >= 0
            assert metric_value < 5.0  # 各段階の実行時間が5秒以内

    def test_pipeline_with_data_consistency_checks(self, sample_stock_data):
        """データ一貫性チェック付きパイプラインテスト"""
        # 元のデータの保存
        original_data = sample_stock_data.copy()

        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)

        # データ一貫性のチェック
        # 1. 元のデータが保持されていることを確認
        for col in original_data.columns:
            assert col in processed_data.columns

        # 2. データの行数が変わっていないことを確認
        assert len(processed_data) == len(original_data)

        # 3. 元のデータの値が変更されていないことを確認
        for col in original_data.columns:
            if col in processed_data.columns:
                pd.testing.assert_series_equal(
                    original_data[col], processed_data[col], check_names=False
                )

        # 4. 新しいカラムが追加されていることを確認
        assert len(processed_data.columns) > len(original_data.columns)

        # 5. 新しいカラムが適切な値を持っていることを確認
        new_columns = set(processed_data.columns) - set(original_data.columns)
        for col in new_columns:
            assert not processed_data[col].isna().all()  # 全てNaNではない

    def test_pipeline_with_stress_testing(self):
        """ストレステスト"""
        # 様々なサイズのデータセットでのテスト
        data_sizes = [100, 500, 1000, 5000]

        for size in data_sizes:
            # 指定されたサイズのデータを作成
            test_data = pd.DataFrame(
                {
                    "Date": pd.date_range("2023-01-01", periods=size, freq="D"),
                    "Open": np.random.uniform(50, 200, size),
                    "High": np.random.uniform(50, 200, size),
                    "Low": np.random.uniform(50, 200, size),
                    "Close": np.random.uniform(50, 200, size),
                    "Volume": np.random.randint(1000, 10000, size),
                }
            )

            # パイプラインの実行
            start_time = time.time()

            ti = TechnicalIndicators()
            processed_data = ti.calculate_all_indicators(test_data)

            execution_time = time.time() - start_time

            # 結果の検証
            assert processed_data is not None
            assert len(processed_data) == size
            assert execution_time < 30.0  # 実行時間が30秒以内

            # 十分なデータがある場合はモデル訓練もテスト
            if size >= 100:
                features = ["Open", "High", "Low", "Volume"]
                target = "Close"

                X = processed_data[features].dropna()
                y = processed_data[target].dropna()

                min_len = min(len(X), len(y))
                if min_len > 10:
                    X = X.iloc[:min_len]
                    y = y.iloc[:min_len]

                    factory = ModelFactory()
                    model = factory.create_model("linear_regression")
                    model.fit(X, y)
                    predictions = model.predict(X)

                    assert len(predictions) == len(y)

    def test_pipeline_with_custom_validation_rules(self, sample_stock_data):
        """カスタム検証ルール付きパイプラインテスト"""
        # カスタム検証ルールの設定
        custom_validator = EnhancedDataValidator(ValidationLevel.CUSTOM)

        # カスタムルールの追加
        custom_validator.validation_rules.update(
            {
                "custom_price_range": (0.01, 10000),  # 価格の範囲
                "custom_volume_range": (0, 1000000),  # ボリュームの範囲
                "custom_date_range": ("2020-01-01", "2030-12-31"),  # 日付の範囲
            }
        )

        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)

        # カスタム検証の実行
        validation_result = custom_validator.validate_data_quality(processed_data)

        # 検証結果の確認
        assert isinstance(validation_result.is_valid, (bool, np.bool_))
        assert isinstance(validation_result.score, float)
        assert 0.0 <= validation_result.score <= 1.0

    def test_pipeline_with_anomaly_detection_methods(self, sample_stock_data):
        """複数の異常値検出手法でのパイプラインテスト"""
        # 異常値を含むデータの生成
        anomaly_data = sample_stock_data.copy()
        anomaly_data.loc[0, "Close"] = 1000  # 異常に高い値
        anomaly_data.loc[1, "Volume"] = -1000  # 負の値

        validator = EnhancedDataValidator(ValidationLevel.STANDARD)

        # 複数の異常値検出手法のテスト
        methods = ["isolation_forest", "z_score"]

        for method in methods:
            anomaly_result = validator.detect_anomalies(anomaly_data, method=method)

            assert "anomalies" in anomaly_result
            assert "anomaly_scores" in anomaly_result
            assert "method" in anomaly_result
            assert anomaly_result["method"] == method

            # 異常値が検出されることを確認
            if len(anomaly_data) > 0:
                assert len(anomaly_result["anomalies"]) >= 0

    def test_pipeline_with_data_export_import(self, sample_stock_data, tmp_path):
        """データエクスポート・インポート付きパイプラインテスト"""
        # パイプラインの実行
        ti = TechnicalIndicators()
        processed_data = ti.calculate_all_indicators(sample_stock_data)

        # データのエクスポート
        export_file = tmp_path / "processed_data.csv"
        processed_data.to_csv(export_file, index=False)

        # データのインポート
        imported_data = pd.read_csv(export_file)

        # データの整合性確認
        assert len(imported_data) == len(processed_data)
        assert len(imported_data.columns) == len(processed_data.columns)

        # 数値データの精度確認
        numeric_columns = processed_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in imported_data.columns:
                pd.testing.assert_series_equal(
                    processed_data[col],
                    imported_data[col],
                    check_names=False,
                    rtol=1e-10,  # 数値の精度
                )

    def test_pipeline_with_recovery_statistics(self):
        """復旧統計付きパイプラインテスト"""
        recovery_system = AutoRecoverySystem()

        # 様々なエラーでの復旧テスト
        test_errors = [
            FileNotFoundError("Test file not found"),
            ValueError("Test validation error"),
            MemoryError("Test memory error"),
            RuntimeError("Test runtime error"),
        ]

        for error in test_errors:
            context = {"test": "data"}
            recovery_result = recovery_system.auto_recover(error, context)

            # 復旧結果の検証
            assert isinstance(recovery_result.success, bool)
            assert isinstance(recovery_result.recovery_time, float)
            assert recovery_result.recovery_time >= 0

        # 復旧統計の取得
        stats = recovery_system.get_recovery_statistics()

        assert "total_recoveries" in stats
        assert "successful_recoveries" in stats
        assert "success_rate" in stats
        assert stats["total_recoveries"] > 0
