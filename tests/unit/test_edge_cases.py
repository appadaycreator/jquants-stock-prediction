"""
エッジケースとエラーハンドリングのテスト
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import os
import tempfile
from technical_indicators import TechnicalIndicators
from model_factory import ModelFactory, ModelEvaluator
from data_validator import DataValidator
from config_loader import ConfigLoader


class TestEdgeCases:
    """エッジケースとエラーハンドリングのテスト"""

    def test_technical_indicators_edge_cases(self):
        """技術指標のエッジケーステスト"""
        ti = TechnicalIndicators()
        
        # 最小データ（1行）
        minimal_data = pd.DataFrame({
            "Date": ["20240301"],
            "Open": [100.0],
            "High": [105.0],
            "Low": [95.0],
            "Close": [102.0],
            "Volume": [1000000]
        })
        
        result = ti.calculate_all_indicators(minimal_data)
        assert result is not None
        assert len(result) == 1
        
        # 極端な値のデータ
        extreme_data = pd.DataFrame({
            "Date": ["20240301", "20240302", "20240303"],
            "Open": [0.01, 1000000.0, 0.0],
            "High": [0.02, 1000001.0, 0.0],
            "Low": [0.01, 999999.0, 0.0],
            "Close": [0.015, 1000000.5, 0.0],
            "Volume": [1, 1000000000, 0]
        })
        
        result = ti.calculate_all_indicators(extreme_data)
        assert result is not None
        
        # NaN値が含まれるデータ
        nan_data = pd.DataFrame({
            "Date": ["20240301", "20240302", "20240303"],
            "Open": [100.0, np.nan, 102.0],
            "High": [105.0, 106.0, np.nan],
            "Low": [95.0, 96.0, 97.0],
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, 1100000, 1200000]
        })
        
        result = ti.calculate_all_indicators(nan_data)
        assert result is not None

    def test_model_factory_edge_cases(self):
        """モデルファクトリーのエッジケーステスト"""
        factory = ModelFactory()
        
        # 無効なモデル名
        with pytest.raises(ValueError):
            factory.create_model("invalid_model")
        
        # 無効なパラメータ
        with pytest.raises((ValueError, TypeError)):
            factory.create_model("random_forest", {"invalid_param": "invalid_value"})
        
        # 極端なパラメータ値
        extreme_params = {
            "n_estimators": 1,  # 最小値
            "max_depth": 1,    # 最小値
            "random_state": 0
        }
        model = factory.create_model("random_forest", extreme_params)
        assert model is not None

    def test_model_evaluation_edge_cases(self):
        """モデル評価のエッジケーステスト"""
        evaluator = ModelEvaluator()
        factory = ModelFactory()
        
        # 空のデータ
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        
        with pytest.raises(ValueError):
            evaluator.evaluate_model(factory.create_model("linear_regression"), empty_X, empty_y)
        
        # 1つのサンプルのみ
        single_X = pd.DataFrame({"feature": [1.0]})
        single_y = pd.Series([2.0])
        
        model = factory.create_model("linear_regression")
        model.fit(single_X, single_y)
        predictions = model.predict(single_X)
        
        # 1つのサンプルでも評価が可能であることを確認
        metrics = evaluator.evaluate_model(model, single_X, single_y, predictions)
        assert metrics is not None
        assert "mae" in metrics

    def test_data_validator_edge_cases(self):
        """データ検証のエッジケーステスト"""
        validator = DataValidator()
        
        # 完全に空のデータフレーム
        empty_df = pd.DataFrame()
        result = validator.validate_comprehensive(empty_df)
        assert result is not None
        assert result["is_valid"] is False
        
        # すべてNaNのデータ
        all_nan_df = pd.DataFrame({
            "Code": [np.nan, np.nan],
            "Date": [np.nan, np.nan],
            "Close": [np.nan, np.nan]
        })
        result = validator.validate_comprehensive(all_nan_df)
        assert result is not None
        
        # 無限大の値
        inf_df = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"],
            "Close": [np.inf]
        })
        result = validator.validate_comprehensive(inf_df)
        assert result is not None

    def test_config_loader_edge_cases(self):
        """設定ローダーのエッジケーステスト"""
        # 存在しないファイル
        with pytest.raises(FileNotFoundError):
            ConfigLoader("nonexistent_config.yaml")
        
        # 無効なYAMLファイル
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            with pytest.raises((ValueError, yaml.YAMLError)):
                ConfigLoader(f.name)
            
            os.unlink(f.name)

    def test_memory_usage_large_datasets(self):
        """大きなデータセットでのメモリ使用量テスト"""
        # 大きなデータセットを作成
        large_data = pd.DataFrame({
            "Date": pd.date_range("2020-01-01", periods=10000, freq="D"),
            "Open": np.random.uniform(90, 110, 10000),
            "High": np.random.uniform(95, 115, 10000),
            "Low": np.random.uniform(85, 105, 10000),
            "Close": np.random.uniform(90, 110, 10000),
            "Volume": np.random.randint(100000, 1000000, 10000)
        })
        
        # 技術指標の計算
        ti = TechnicalIndicators()
        result = ti.calculate_all_indicators(large_data)
        
        assert result is not None
        assert len(result) == 10000
        
        # メモリ使用量が適切であることを確認（実際のメモリ測定は困難なため、処理が完了することを確認）
        assert len(result.columns) > len(large_data.columns)

    def test_concurrent_access_simulation(self):
        """同時アクセスのシミュレーションテスト"""
        # 複数のモデルを同時に作成・使用
        factory = ModelFactory()
        models = []
        
        for i in range(5):
            model = factory.create_model("linear_regression")
            models.append(model)
        
        # 同じデータで複数のモデルを訓練
        X = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
        y = pd.Series([2, 4, 6, 8, 10])
        
        for model in models:
            model.fit(X, y)
            predictions = model.predict(X)
            assert len(predictions) == len(y)

    def test_unicode_and_special_characters(self):
        """Unicode文字と特殊文字のテスト"""
        # 特殊文字を含むデータ
        special_data = pd.DataFrame({
            "Code": ["1234", "5678", "特殊コード"],
            "Date": ["20240301", "20240302", "20240303"],
            "Open": [100.0, 101.0, 102.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [95.0, 96.0, 97.0],
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, 1100000, 1200000]
        })
        
        # 技術指標の計算
        ti = TechnicalIndicators()
        result = ti.calculate_all_indicators(special_data)
        assert result is not None
        
        # データ検証
        validator = DataValidator()
        validation_result = validator.validate_comprehensive(special_data)
        assert validation_result is not None

    def test_numeric_precision_edge_cases(self):
        """数値精度のエッジケーステスト"""
        # 極小値
        tiny_data = pd.DataFrame({
            "Date": ["20240301", "20240302"],
            "Open": [1e-10, 2e-10],
            "High": [3e-10, 4e-10],
            "Low": [0.5e-10, 1.5e-10],
            "Close": [2e-10, 3e-10],
            "Volume": [1, 2]
        })
        
        ti = TechnicalIndicators()
        result = ti.calculate_all_indicators(tiny_data)
        assert result is not None
        
        # 極大値
        huge_data = pd.DataFrame({
            "Date": ["20240301", "20240302"],
            "Open": [1e10, 2e10],
            "High": [3e10, 4e10],
            "Low": [0.5e10, 1.5e10],
            "Close": [2e10, 3e10],
            "Volume": [1000000000, 2000000000]
        })
        
        result = ti.calculate_all_indicators(huge_data)
        assert result is not None

    def test_time_zone_handling(self):
        """タイムゾーンハンドリングのテスト"""
        # 異なるタイムゾーンの日付
        timezone_data = pd.DataFrame({
            "Date": ["20240301", "20240302", "20240303"],
            "Open": [100.0, 101.0, 102.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [95.0, 96.0, 97.0],
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, 1100000, 1200000]
        })
        
        # 日付形式の検証
        validator = DataValidator()
        result = validator.validate_date_format(timezone_data)
        assert result is not None

    def test_corrupted_data_handling(self):
        """破損データのハンドリングテスト"""
        # 破損したデータ構造
        corrupted_data = pd.DataFrame({
            "Code": ["1234", None, ""],
            "Date": ["20240301", "invalid", "20240303"],
            "Open": [100.0, "not_a_number", 102.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [95.0, 96.0, 97.0],
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, -1000, 1200000]
        })
        
        # データ検証
        validator = DataValidator()
        result = validator.validate_comprehensive(corrupted_data)
        assert result is not None
        assert result["is_valid"] is False

    def test_resource_cleanup(self):
        """リソースクリーンアップのテスト"""
        # 大量のデータを処理してリソースが適切に解放されることを確認
        large_data = pd.DataFrame({
            "Date": pd.date_range("2020-01-01", periods=1000, freq="D"),
            "Open": np.random.uniform(90, 110, 1000),
            "High": np.random.uniform(95, 115, 1000),
            "Low": np.random.uniform(85, 105, 1000),
            "Close": np.random.uniform(90, 110, 1000),
            "Volume": np.random.randint(100000, 1000000, 1000)
        })
        
        # 複数回の処理を実行
        for _ in range(10):
            ti = TechnicalIndicators()
            result = ti.calculate_all_indicators(large_data)
            assert result is not None
            
            # 明示的にリソースを解放
            del ti
            del result

    def test_error_recovery(self):
        """エラー回復のテスト"""
        # 最初に失敗するが、リトライで成功するケース
        factory = ModelFactory()
        
        # 無効なパラメータでエラーが発生することを確認
        with pytest.raises((ValueError, TypeError)):
            factory.create_model("random_forest", {"n_estimators": -1})
        
        # 有効なパラメータで正常に動作することを確認
        model = factory.create_model("random_forest", {"n_estimators": 10})
        assert model is not None

    def test_boundary_conditions(self):
        """境界条件のテスト"""
        # 最小限のデータでの動作確認
        minimal_data = pd.DataFrame({
            "Date": ["20240301"],
            "Open": [100.0],
            "High": [100.0],
            "Low": [100.0],
            "Close": [100.0],
            "Volume": [1]
        })
        
        ti = TechnicalIndicators()
        result = ti.calculate_all_indicators(minimal_data)
        assert result is not None
        
        # 最大限のデータでの動作確認（メモリ制限内）
        max_data = pd.DataFrame({
            "Date": ["20240301"] * 1000,
            "Open": [100.0] * 1000,
            "High": [100.0] * 1000,
            "Low": [100.0] * 1000,
            "Close": [100.0] * 1000,
            "Volume": [1000000] * 1000
        })
        
        result = ti.calculate_all_indicators(max_data)
        assert result is not None
        assert len(result) == 1000
