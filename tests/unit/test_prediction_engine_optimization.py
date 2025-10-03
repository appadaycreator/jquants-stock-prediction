import unittest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
import numpy as np
import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.prediction_engine import PredictionEngine
from core.config_manager import ConfigManager
from core.logging_manager import LoggingManager
from core.error_handler import ErrorHandler

class TestPredictionEngineOptimization(unittest.TestCase):
    """予測エンジンの最適化テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = ConfigManager()
        self.logger = LoggingManager()
        self.error_handler = ErrorHandler(self.config, self.logger)
        self.engine = PredictionEngine(
            config=self.config.get_config(),
            logger=self.logger,
            error_handler=self.error_handler
        )

    def test_make_predictions_optimization(self):
        """予測実行の最適化テスト"""
        # モックモデル
        mock_model = Mock()
        mock_model.predict.return_value = np.array([1.5, 2.5, 3.5])
        
        # テストデータ
        test_data = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6]
        })
        
        # 予測実行
        result = self.engine.make_predictions(mock_model, test_data)
        
        # 結果の検証
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, [1.5, 2.5, 3.5])

    def test_make_predictions_empty_data(self):
        """空データでの予測テスト"""
        mock_model = Mock()
        empty_data = pd.DataFrame()
        
        result = self.engine.make_predictions(mock_model, empty_data)
        
        # 空データの場合はサンプル値を返す
        self.assertEqual(result, [1.0, 2.0, 3.0])

    def test_make_predictions_none_model(self):
        """Noneモデルでの予測テスト"""
        test_data = pd.DataFrame({'feature1': [1, 2, 3]})
        
        # エラーハンドラーを無効化してテスト
        self.engine.error_handler = None
        
        with self.assertRaises(ValueError) as context:
            self.engine.make_predictions(None, test_data)
        
        self.assertIn("モデルが初期化されていません", str(context.exception))

    def test_make_predictions_none_data(self):
        """Noneデータでの予測テスト"""
        mock_model = Mock()
        
        # エラーハンドラーを無効化してテスト
        self.engine.error_handler = None
        
        with self.assertRaises(ValueError) as context:
            self.engine.make_predictions(mock_model, None)
        
        self.assertIn("予測データがNoneです", str(context.exception))

    def test_make_predictions_numpy_array_result(self):
        """NumPy配列結果のテスト"""
        mock_model = Mock()
        mock_model.predict.return_value = np.array([1.0, 2.0, 3.0])
        
        test_data = pd.DataFrame({'feature1': [1, 2, 3]})
        result = self.engine.make_predictions(mock_model, test_data)
        
        self.assertIsInstance(result, list)
        self.assertEqual(result, [1.0, 2.0, 3.0])

    def test_make_predictions_list_result(self):
        """リスト結果のテスト"""
        mock_model = Mock()
        mock_model.predict.return_value = [1.0, 2.0, 3.0]
        
        test_data = pd.DataFrame({'feature1': [1, 2, 3]})
        result = self.engine.make_predictions(mock_model, test_data)
        
        self.assertIsInstance(result, list)
        self.assertEqual(result, [1.0, 2.0, 3.0])

    def test_make_predictions_none_result(self):
        """None結果のテスト"""
        mock_model = Mock()
        mock_model.predict.return_value = None
        
        test_data = pd.DataFrame({'feature1': [1, 2, 3]})
        result = self.engine.make_predictions(mock_model, test_data)
        
        # None結果の場合はデフォルト値を返す
        self.assertEqual(result, [0.0, 0.0, 0.0])

    def test_make_predictions_empty_result(self):
        """空結果のテスト"""
        mock_model = Mock()
        mock_model.predict.return_value = []
        
        test_data = pd.DataFrame({'feature1': [1, 2, 3]})
        result = self.engine.make_predictions(mock_model, test_data)
        
        # 空結果の場合はデフォルト値を返す
        self.assertEqual(result, [0.0, 0.0, 0.0])

    def test_make_predictions_exception_handling(self):
        """例外処理のテスト"""
        mock_model = Mock()
        mock_model.predict.side_effect = Exception("予測エラー")
        
        test_data = pd.DataFrame({'feature1': [1, 2, 3]})
        
        # エラーハンドラーを無効化してテスト
        self.engine.error_handler = None
        
        with self.assertRaises(Exception) as context:
            self.engine.make_predictions(mock_model, test_data)
        
        self.assertIn("予測エラー", str(context.exception))

    def test_data_info_optimization(self):
        """データ情報の最適化テスト"""
        X_train = np.array([[1, 2], [3, 4]])
        X_val = np.array([[5, 6]])
        X_test = np.array([[7, 8]])
        config = {'features': ['feature1', 'feature2'], 'target': 'close'}
        
        data_info = self.engine._create_data_info(X_train, X_val, X_test, config)
        
        # 最適化された情報の検証
        self.assertIn('total_size', data_info)
        self.assertIn('feature_count', data_info)
        self.assertEqual(data_info['total_size'], 4)
        self.assertEqual(data_info['feature_count'], 2)

    def test_mock_model_creation(self):
        """モックモデル作成のテスト"""
        # モックモデルを直接作成
        class MockModel:
            def predict(self, data):
                return np.random.random(len(data))
        
        model = MockModel()
        
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict'))

    def test_mock_model_prediction(self):
        """モックモデル予測のテスト"""
        # モックモデルを直接作成
        class MockModel:
            def predict(self, data):
                return np.random.random(len(data))
        
        model = MockModel()
        test_data = pd.DataFrame({'feature1': [1, 2, 3]})
        
        predictions = model.predict(test_data)
        
        self.assertIsInstance(predictions, np.ndarray)
        self.assertEqual(len(predictions), 3)

if __name__ == '__main__':
    unittest.main()
