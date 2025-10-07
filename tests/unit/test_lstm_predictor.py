#!/usr/bin/env python3
"""
LSTM予測システムのテスト
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from core.lstm_predictor import LSTMPredictor


class TestLSTMPredictor:
    """LSTM予測システムのテストクラス"""

    def setup_method(self):
        """テスト前の準備"""
        self.logger = Mock()
        self.error_handler = Mock()
        self.predictor = LSTMPredictor(
            logger=self.logger, error_handler=self.error_handler
        )

    def test_initialization(self):
        """初期化テスト"""
        assert self.predictor.logger == self.logger
        assert self.predictor.error_handler == self.error_handler
        assert self.predictor.model is None
        assert self.predictor.sequence_length == 120

    def test_prepare_data_success(self):
        """データ準備成功テスト"""
        # テストデータの作成
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        prices = 100 + np.cumsum(np.random.randn(200) * 0.01)

        df = pd.DataFrame({'Close': prices}, index=dates)

        X, y = self.predictor.prepare_data(df, 'Close')

        assert X.shape[0] == 80  # 200 - 120
        assert X.shape[1] == 120  # sequence_length
        assert X.shape[2] == 1  # 特徴量数
        assert len(y) == 80
        assert X.shape[0] == len(y)

    def test_prepare_data_with_different_target_column(self):
        """異なるターゲット列でのデータ準備テスト"""
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        prices = 100 + np.cumsum(np.random.randn(200) * 0.01)

        df = pd.DataFrame({'Price': prices}, index=dates)

        X, y = self.predictor.prepare_data(df, 'Price')

        assert X.shape[0] == 80
        assert X.shape[1] == 120
        assert X.shape[2] == 1
        assert len(y) == 80

    def test_prepare_data_insufficient_data(self):
        """データ不足時のテスト"""
        # 120日未満のデータ
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        prices = 100 + np.cumsum(np.random.randn(50) * 0.01)

        df = pd.DataFrame({'Close': prices}, index=dates)

        with pytest.raises(Exception):
            self.predictor.prepare_data(df, 'Close')

    def test_prepare_data_empty_dataframe(self):
        """空のデータフレームでのテスト"""
        df = pd.DataFrame()

        with pytest.raises(Exception):
            self.predictor.prepare_data(df, 'Close')

    def test_prepare_data_missing_column(self):
        """存在しない列でのテスト"""
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        prices = 100 + np.cumsum(np.random.randn(200) * 0.01)

        df = pd.DataFrame({'Open': prices}, index=dates)

        with pytest.raises(Exception):
            self.predictor.prepare_data(df, 'Close')

    def test_build_model(self):
        """モデル構築テスト"""
        input_shape = (120, 1)
        model = self.predictor.build_model(input_shape)

        assert model is not None
        assert len(model.layers) == 5  # LSTM層2つ + Dropout層2つ + Dense層1つ

    def test_build_model_different_input_shape(self):
        """異なる入力形状でのモデル構築テスト"""
        input_shape = (60, 1)
        model = self.predictor.build_model(input_shape)

        assert model is not None
        assert model.input_shape == (None, 60, 1)

    def test_train_model_success(self):
        """モデル学習成功テスト"""
        # テストデータの準備
        np.random.seed(42)
        X = np.random.randn(100, 120, 1)
        y = np.random.randn(100)

        with patch('tensorflow.keras.models.Sequential') as mock_sequential:
            mock_model = MagicMock()
            mock_history = MagicMock()
            mock_history.history = {'loss': [0.5, 0.4], 'val_loss': [0.6, 0.5]}
            mock_model.fit.return_value = mock_history
            mock_model.evaluate.return_value = [0.4, 0.3]
            mock_sequential.return_value = mock_model

            result = self.predictor.train_model(X, y, epochs=5, batch_size=16)

            assert "model" in result
            assert "history" in result
            assert "train_loss" in result
            assert "val_loss" in result
            assert "train_mae" in result
            assert "val_mae" in result

    def test_train_model_with_different_parameters(self):
        """異なるパラメータでの学習テスト"""
        np.random.seed(42)
        X = np.random.randn(50, 120, 1)
        y = np.random.randn(50)

        with patch('tensorflow.keras.models.Sequential') as mock_sequential:
            mock_model = MagicMock()
            mock_history = MagicMock()
            mock_history.history = {'loss': [0.5], 'val_loss': [0.6]}
            mock_model.fit.return_value = mock_history
            mock_model.evaluate.return_value = [0.4, 0.3]
            mock_sequential.return_value = mock_model

            result = self.predictor.train_model(X, y, epochs=1, batch_size=8)

            assert "model" in result

    def test_train_model_error(self):
        """学習エラーテスト"""
        # 無効なデータで学習
        X = np.array([])
        y = np.array([])

        with pytest.raises(Exception):
            self.predictor.train_model(X, y)

    def test_predict_future_success(self):
        """未来予測成功テスト"""
        # モデルをモック
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[1.0]])
        self.predictor.model = mock_model

        # 最後のシーケンス
        last_sequence = np.random.randn(120)

        with patch.object(self.predictor.scaler, 'inverse_transform') as mock_inverse:
            mock_inverse.return_value = np.array([[100.0], [101.0], [102.0]])

            predictions = self.predictor.predict_future(last_sequence, days=3)

            assert len(predictions) == 3
            assert all(isinstance(p, float) for p in predictions)

    def test_predict_future_no_model(self):
        """学習されていないモデルでの予測テスト"""
        last_sequence = np.random.randn(120)

        with pytest.raises(ValueError, match="モデルが訓練されていません"):
            self.predictor.predict_future(last_sequence)

    def test_predict_future_different_days(self):
        """異なる日数での予測テスト"""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[1.0]])
        self.predictor.model = mock_model

        last_sequence = np.random.randn(120)

        with patch.object(self.predictor.scaler, 'inverse_transform') as mock_inverse:
            mock_inverse.return_value = np.array([[100.0], [101.0]])

            predictions = self.predictor.predict_future(last_sequence, days=2)

            assert len(predictions) == 2

    def test_get_prediction_confidence_success(self):
        """予測信頼度計算成功テスト"""
        predictions = [100.0, 101.0, 102.0, 103.0]
        historical_volatility = 0.02

        result = self.predictor.get_prediction_confidence(
            predictions, historical_volatility
        )

        assert "confidence" in result
        assert "risk_level" in result
        assert "prediction_volatility" in result
        assert "historical_volatility" in result
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["risk_level"] in ["低", "中", "高"]

    def test_get_prediction_confidence_high_volatility(self):
        """高ボラティリティでの信頼度テスト"""
        predictions = [100.0, 110.0, 90.0, 120.0]  # 高ボラティリティ
        historical_volatility = 0.01  # 低い履歴ボラティリティ

        result = self.predictor.get_prediction_confidence(
            predictions, historical_volatility
        )

        assert result["confidence"] < 0.5  # 低い信頼度
        assert result["risk_level"] in ["中", "高"]

    def test_get_prediction_confidence_low_volatility(self):
        """低ボラティリティでの信頼度テスト"""
        predictions = [100.0, 100.1, 100.2, 100.3]  # 低ボラティリティ
        historical_volatility = 0.05  # 高い履歴ボラティリティ

        result = self.predictor.get_prediction_confidence(
            predictions, historical_volatility
        )

        assert result["confidence"] > 0.5  # 高い信頼度
        assert result["risk_level"] in ["低", "中"]

    def test_get_prediction_confidence_error(self):
        """信頼度計算エラーテスト"""
        predictions = []
        historical_volatility = 0.02

        result = self.predictor.get_prediction_confidence(
            predictions, historical_volatility
        )

        assert result["confidence"] == 1.0  # 空の場合はデフォルト値1.0
        assert result["risk_level"] == "低"  # 空の場合は低リスク

    def test_create_visualization_data_success(self):
        """可視化データ作成成功テスト"""
        # 履歴データ
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)
        historical_data = pd.DataFrame({'Close': prices}, index=dates)

        # 予測データ
        predictions = [101.0, 102.0, 103.0]
        prediction_dates = ['2023-04-10', '2023-04-11', '2023-04-12']

        result = self.predictor.create_visualization_data(
            historical_data, predictions, prediction_dates
        )

        assert "historical" in result
        assert "predictions" in result
        assert "metadata" in result
        assert "dates" in result["historical"]
        assert "prices" in result["historical"]
        assert "dates" in result["predictions"]
        assert "prices" in result["predictions"]
        assert result["metadata"]["model_type"] == "LSTM"

    def test_create_visualization_data_error(self):
        """可視化データ作成エラーテスト"""
        # 無効なデータ
        historical_data = pd.DataFrame()
        predictions = []
        prediction_dates = []

        result = self.predictor.create_visualization_data(
            historical_data, predictions, prediction_dates
        )

        assert result == {}

    def test_run_complete_prediction_success(self):
        """完全予測パイプライン成功テスト"""
        # テストデータの作成
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        prices = 100 + np.cumsum(np.random.randn(200) * 0.01)

        df = pd.DataFrame({'Close': prices}, index=dates)

        with (
            patch.object(self.predictor, 'prepare_data') as mock_prepare,
            patch.object(self.predictor, 'train_model') as mock_train,
            patch.object(self.predictor, 'predict_future') as mock_predict,
            patch.object(
                self.predictor, 'get_prediction_confidence'
            ) as mock_confidence,
            patch.object(self.predictor, 'create_visualization_data') as mock_viz,
        ):
            # モックの設定
            mock_prepare.return_value = (
                np.random.randn(80, 120, 1),
                np.random.randn(80),
            )
            mock_train.return_value = {"model": MagicMock(), "history": {}}
            mock_predict.return_value = [101.0, 102.0, 103.0]
            mock_confidence.return_value = {"confidence": 0.8, "risk_level": "低"}
            mock_viz.return_value = {
                "historical": {},
                "predictions": {},
                "metadata": {},
            }

            result = self.predictor.run_complete_prediction(df, 'Close', 3)

            assert "predictions" in result
            assert "prediction_dates" in result
            assert "confidence" in result
            assert "training_result" in result
            assert "visualization_data" in result
            assert "model_info" in result

    def test_run_complete_prediction_error(self):
        """完全予測パイプラインエラーテスト"""
        # 無効なデータ
        df = pd.DataFrame()

        with pytest.raises(Exception):
            self.predictor.run_complete_prediction(df, 'Close', 3)

    def test_sequence_length_property(self):
        """シーケンス長プロパティテスト"""
        assert self.predictor.sequence_length == 120

        # シーケンス長を変更
        self.predictor.sequence_length = 60
        assert self.predictor.sequence_length == 60

    def test_scaler_property(self):
        """スケーラープロパティテスト"""
        assert self.predictor.scaler is not None
        assert hasattr(self.predictor.scaler, 'fit_transform')
        assert hasattr(self.predictor.scaler, 'inverse_transform')

    def test_model_property(self):
        """モデルプロパティテスト"""
        assert self.predictor.model is None

        # モデルを設定
        mock_model = MagicMock()
        self.predictor.model = mock_model
        assert self.predictor.model == mock_model

    def test_data_preprocessing_edge_cases(self):
        """データ前処理エッジケーステスト"""
        # 最小限のデータ
        dates = pd.date_range(start='2023-01-01', periods=121, freq='D')
        prices = 100 + np.cumsum(np.random.randn(121) * 0.01)

        df = pd.DataFrame({'Close': prices}, index=dates)

        X, y = self.predictor.prepare_data(df, 'Close')

        assert X.shape[0] == 1  # 121 - 120 = 1
        assert X.shape[1] == 120
        assert X.shape[2] == 1
        assert len(y) == 1

    def test_prediction_confidence_edge_cases(self):
        """予測信頼度エッジケーステスト"""
        # 単一予測値
        predictions = [100.0]
        historical_volatility = 0.02

        result = self.predictor.get_prediction_confidence(
            predictions, historical_volatility
        )

        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

        # ゼロボラティリティ
        predictions = [100.0, 100.0, 100.0, 100.0]
        historical_volatility = 0.0

        result = self.predictor.get_prediction_confidence(
            predictions, historical_volatility
        )

        assert result["confidence"] == 1.0
        assert result["risk_level"] == "低"

    def test_visualization_data_metadata(self):
        """可視化データメタデータテスト"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)
        historical_data = pd.DataFrame({'Close': prices}, index=dates)

        predictions = [101.0, 102.0]
        prediction_dates = ['2023-04-10', '2023-04-11']

        result = self.predictor.create_visualization_data(
            historical_data, predictions, prediction_dates
        )

        metadata = result["metadata"]
        assert metadata["model_type"] == "LSTM"
        assert metadata["sequence_length"] == 120
        assert metadata["prediction_days"] == 2
        assert "generated_at" in metadata

    def test_model_training_validation_split(self):
        """モデル学習検証分割テスト"""
        np.random.seed(42)
        X = np.random.randn(100, 120, 1)
        y = np.random.randn(100)

        # 実際のモデルでテスト（モックは使用しない）
        result = self.predictor.train_model(X, y)

        # 学習が成功することを確認
        assert result["training_successful"] is True

    def test_prediction_future_sequence_update(self):
        """未来予測シーケンス更新テスト"""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[1.0]])
        self.predictor.model = mock_model

        last_sequence = np.random.randn(120)

        with patch.object(self.predictor.scaler, 'inverse_transform') as mock_inverse:
            mock_inverse.return_value = np.array([[100.0], [101.0]])

            predictions = self.predictor.predict_future(last_sequence, days=2)

            # モデルが2回呼ばれることを確認
            assert mock_model.predict.call_count == 2

    def test_error_handling_in_prepare_data(self):
        """データ準備時のエラーハンドリングテスト"""
        # 無効なデータフレーム
        df = None

        with pytest.raises(Exception):
            self.predictor.prepare_data(df, 'Close')

    def test_error_handling_in_train_model(self):
        """モデル学習時のエラーハンドリングテスト"""
        # 無効なデータ
        X = None
        y = None

        with pytest.raises(Exception):
            self.predictor.train_model(X, y)

    def test_error_handling_in_predict_future(self):
        """未来予測時のエラーハンドリングテスト"""
        # 無効なシーケンス
        last_sequence = None

        with pytest.raises(Exception):
            self.predictor.predict_future(last_sequence)

    def test_logger_integration(self):
        """ロガー統合テスト"""
        # ロガーが正しく使用されることを確認
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        prices = 100 + np.cumsum(np.random.randn(200) * 0.01)

        df = pd.DataFrame({'Close': prices}, index=dates)

        self.predictor.prepare_data(df, 'Close')

        # ロガーが呼ばれることを確認
        self.logger.log_info.assert_called()

    def test_error_handler_integration(self):
        """エラーハンドラー統合テスト"""
        # エラーが発生した場合のハンドリングを確認
        df = pd.DataFrame()  # 空のデータフレーム

        with pytest.raises(Exception):
            self.predictor.prepare_data(df, 'Close')

        # エラーハンドラーが呼ばれることを確認
        self.error_handler.handle_data_processing_error.assert_called()
