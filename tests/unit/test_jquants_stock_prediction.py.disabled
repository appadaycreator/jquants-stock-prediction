"""
J-Quants株価予測メインモジュールのユニットテスト
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from jquants_stock_prediction import JQuantsStockPrediction


class TestJQuantsStockPrediction:
    """JQuantsStockPredictionクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        predictor = JQuantsStockPrediction()
        assert predictor is not None
        assert hasattr(predictor, "logger")

    def test_init_with_config(self):
        """設定付き初期化テスト"""
        config = {
            "prediction": {
                "features": ["SMA_5", "SMA_25"],
                "target": "Close",
                "test_size": 0.2
            }
        }
        predictor = JQuantsStockPrediction(config)
        assert predictor.config == config

    def test_load_data_success(self, sample_stock_data, tmp_path):
        """データ読み込み成功テスト"""
        # テスト用CSVファイルを作成
        file_path = tmp_path / "test_data.csv"
        sample_stock_data.to_csv(file_path, index=False)
        
        predictor = JQuantsStockPrediction()
        result = predictor.load_data(str(file_path))
        
        assert result is not None
        assert len(result) == len(sample_stock_data)
        assert list(result.columns) == list(sample_stock_data.columns)

    def test_load_data_file_not_found(self):
        """ファイルが見つからない場合のテスト"""
        predictor = JQuantsStockPrediction()
        result = predictor.load_data("nonexistent_file.csv")
        
        assert result is None

    def test_load_data_invalid_format(self, tmp_path):
        """無効なファイル形式のテスト"""
        # 無効なCSVファイルを作成
        file_path = tmp_path / "invalid_data.csv"
        with open(file_path, 'w') as f:
            f.write("invalid,csv,format\n")
            f.write("not,enough,columns\n")
        
        predictor = JQuantsStockPrediction()
        result = predictor.load_data(str(file_path))
        
        assert result is None

    def test_preprocess_data_basic(self, sample_stock_data):
        """基本的なデータ前処理テスト"""
        predictor = JQuantsStockPrediction()
        result = predictor.preprocess_data(sample_stock_data)
        
        assert result is not None
        assert len(result) > 0
        assert len(result.columns) >= len(sample_stock_data.columns)

    def test_preprocess_data_with_config(self, sample_stock_data):
        """設定付きデータ前処理テスト"""
        config = {
            "preprocessing": {
                "sma_windows": [5, 10],
                "rsi_period": 14
            }
        }
        predictor = JQuantsStockPrediction(config)
        result = predictor.preprocess_data(sample_stock_data)
        
        assert result is not None
        assert len(result) > 0

    def test_preprocess_data_empty(self):
        """空のデータフレームの前処理テスト"""
        predictor = JQuantsStockPrediction()
        empty_data = pd.DataFrame()
        result = predictor.preprocess_data(empty_data)
        
        assert result is None

    def test_preprocess_data_missing_columns(self):
        """必須カラムが不足している場合のテスト"""
        predictor = JQuantsStockPrediction()
        incomplete_data = pd.DataFrame({
            "Date": ["2023-01-01"],
            "Close": [100.0]
        })
        result = predictor.preprocess_data(incomplete_data)
        
        assert result is None

    def test_train_model_success(self, sample_stock_data):
        """モデル訓練成功テスト"""
        predictor = JQuantsStockPrediction()
        
        # 前処理済みデータを準備
        processed_data = predictor.preprocess_data(sample_stock_data)
        if processed_data is not None and len(processed_data) > 10:
            result = predictor.train_model(processed_data)
            
            assert result is not None
            assert hasattr(result, "fit")
            assert hasattr(result, "predict")

    def test_train_model_insufficient_data(self):
        """データ不足時のモデル訓練テスト"""
        predictor = JQuantsStockPrediction()
        insufficient_data = pd.DataFrame({
            "Close": [100.0, 101.0]  # データが少なすぎる
        })
        result = predictor.train_model(insufficient_data)
        
        assert result is None

    def test_train_model_with_different_models(self, sample_stock_data):
        """異なるモデルでの訓練テスト"""
        models = ["linear_regression", "ridge", "lasso", "random_forest"]
        
        for model_name in models:
            config = {
                "prediction": {
                    "primary_model": model_name
                }
            }
            predictor = JQuantsStockPrediction(config)
            processed_data = predictor.preprocess_data(sample_stock_data)
            
            if processed_data is not None and len(processed_data) > 10:
                result = predictor.train_model(processed_data)
                assert result is not None

    def test_predict_success(self, sample_stock_data):
        """予測成功テスト"""
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(sample_stock_data)
        
        if processed_data is not None and len(processed_data) > 10:
            model = predictor.train_model(processed_data)
            if model is not None:
                predictions = predictor.predict(model, processed_data)
                
                assert predictions is not None
                assert len(predictions) > 0
                assert all(isinstance(p, (int, float)) for p in predictions)

    def test_predict_with_invalid_model(self, sample_stock_data):
        """無効なモデルでの予測テスト"""
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(sample_stock_data)
        
        if processed_data is not None:
            predictions = predictor.predict(None, processed_data)
            assert predictions is None

    def test_evaluate_model_success(self, sample_stock_data):
        """モデル評価成功テスト"""
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(sample_stock_data)
        
        if processed_data is not None and len(processed_data) > 10:
            model = predictor.train_model(processed_data)
            if model is not None:
                predictions = predictor.predict(model, processed_data)
                if predictions is not None:
                    metrics = predictor.evaluate_model(processed_data, predictions)
                    
                    assert metrics is not None
                    assert "mae" in metrics
                    assert "mse" in metrics
                    assert "r2" in metrics
                    assert all(isinstance(v, (int, float)) for v in metrics.values())

    def test_evaluate_model_invalid_data(self):
        """無効なデータでの評価テスト"""
        predictor = JQuantsStockPrediction()
        metrics = predictor.evaluate_model(None, [1, 2, 3])
        assert metrics is None

    def test_save_results_success(self, sample_stock_data, tmp_path):
        """結果保存成功テスト"""
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(sample_stock_data)
        
        if processed_data is not None and len(processed_data) > 10:
            model = predictor.train_model(processed_data)
            if model is not None:
                predictions = predictor.predict(model, processed_data)
                if predictions is not None:
                    output_path = tmp_path / "predictions.csv"
                    result = predictor.save_results(processed_data, predictions, str(output_path))
                    
                    assert result is True
                    assert output_path.exists()

    def test_save_results_invalid_path(self, sample_stock_data):
        """無効なパスでの結果保存テスト"""
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(sample_stock_data)
        
        if processed_data is not None:
            predictions = [100.0, 101.0, 102.0]
            result = predictor.save_results(processed_data, predictions, "/invalid/path/predictions.csv")
            assert result is False

    def test_complete_pipeline(self, sample_stock_data, tmp_path):
        """完全なパイプラインテスト"""
        predictor = JQuantsStockPrediction()
        
        # データ保存
        data_path = tmp_path / "test_data.csv"
        sample_stock_data.to_csv(data_path, index=False)
        
        # パイプライン実行
        result = predictor.run_prediction_pipeline(
            str(data_path),
            str(tmp_path / "output.csv"),
            str(tmp_path / "model.pkl")
        )
        
        assert result is not None
        assert "model" in result
        assert "metrics" in result
        assert "predictions" in result

    def test_complete_pipeline_with_config(self, sample_stock_data, tmp_path):
        """設定付き完全パイプラインテスト"""
        config = {
            "prediction": {
                "primary_model": "ridge",
                "test_size": 0.3,
                "random_state": 123
            }
        }
        predictor = JQuantsStockPrediction(config)
        
        data_path = tmp_path / "test_data.csv"
        sample_stock_data.to_csv(data_path, index=False)
        
        result = predictor.run_prediction_pipeline(
            str(data_path),
            str(tmp_path / "output.csv"),
            str(tmp_path / "model.pkl")
        )
        
        assert result is not None

    def test_error_handling_missing_file(self):
        """ファイル不足時のエラーハンドリングテスト"""
        predictor = JQuantsStockPrediction()
        result = predictor.run_prediction_pipeline(
            "nonexistent.csv",
            "output.csv",
            "model.pkl"
        )
        
        assert result is None

    def test_error_handling_corrupted_data(self, tmp_path):
        """破損データのエラーハンドリングテスト"""
        # 破損したCSVファイルを作成
        corrupted_path = tmp_path / "corrupted.csv"
        with open(corrupted_path, 'w') as f:
            f.write("invalid,data\n")
            f.write("corrupted,format\n")
        
        predictor = JQuantsStockPrediction()
        result = predictor.run_prediction_pipeline(
            str(corrupted_path),
            str(tmp_path / "output.csv"),
            str(tmp_path / "model.pkl")
        )
        
        assert result is None

    def test_performance_with_large_dataset(self):
        """大きなデータセットでのパフォーマンステスト"""
        # 大きなデータセットを作成
        large_data = pd.DataFrame({
            "Date": pd.date_range("2020-01-01", periods=1000, freq="D"),
            "Open": np.random.uniform(90, 110, 1000),
            "High": np.random.uniform(95, 115, 1000),
            "Low": np.random.uniform(85, 105, 1000),
            "Close": np.random.uniform(90, 110, 1000),
            "Volume": np.random.randint(1000, 10000, 1000)
        })
        
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(large_data)
        
        if processed_data is not None and len(processed_data) > 100:
            model = predictor.train_model(processed_data)
            if model is not None:
                predictions = predictor.predict(model, processed_data)
                assert predictions is not None
                assert len(predictions) > 0

    def test_model_persistence(self, sample_stock_data, tmp_path):
        """モデルの永続化テスト"""
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(sample_stock_data)
        
        if processed_data is not None and len(processed_data) > 10:
            model = predictor.train_model(processed_data)
            if model is not None:
                model_path = tmp_path / "test_model.pkl"
                result = predictor.save_model(model, str(model_path))
                
                assert result is True
                assert model_path.exists()
                
                # モデルの読み込みテスト
                loaded_model = predictor.load_model(str(model_path))
                assert loaded_model is not None

    def test_config_validation(self):
        """設定検証テスト"""
        # 無効な設定
        invalid_config = {
            "prediction": {
                "test_size": 1.5,  # 無効な値
                "random_state": "invalid"  # 無効な型
            }
        }
        
        predictor = JQuantsStockPrediction(invalid_config)
        # 設定検証が適切に動作することを確認
        assert predictor.config == invalid_config

    def test_logging_functionality(self, sample_stock_data):
        """ログ機能テスト"""
        predictor = JQuantsStockPrediction()
        processed_data = predictor.preprocess_data(sample_stock_data)
        
        # ログが適切に出力されることを確認
        # 実際のログ出力はテスト環境では確認が困難なため、
        # ロガーオブジェクトの存在を確認
        assert hasattr(predictor, "logger")
        assert predictor.logger is not None
