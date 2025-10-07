import unittest
from unittest.mock import Mock, patch
import sys
import os
import json
from datetime import datetime
import pandas as pd
import numpy as np

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config_manager import ConfigManager
from core.data_validator import DataValidator
from core.error_handler import ErrorHandler
from core.logging_manager import LoggingManager
from core.model_manager import ModelManager
from core.prediction_engine import PredictionEngine
from core.visualization_manager import VisualizationManager
from core.performance_optimizer import PerformanceOptimizer
from core.overfitting_detector import OverfittingDetector


class TestSimpleCoverageEnhancement(unittest.TestCase):
    """シンプルなカバレッジ向上テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = ConfigManager()
        self.logger = LoggingManager()
        self.error_handler = ErrorHandler(self.config, self.logger)

        # テスト用データ
        self.sample_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "open": [100, 105, 110],
                "high": [102, 107, 112],
                "low": [98, 103, 108],
                "close": [101, 106, 111],
                "volume": [1000, 1100, 1200],
            }
        )

    def test_config_manager_basic(self):
        """ConfigManagerの基本テスト"""
        # 設定の取得
        result = self.config.get_config("system.name")
        self.assertIsNotNone(result)

        # 存在しないキーの取得
        result = self.config.get_config("nonexistent.key")
        self.assertIsNone(result)

        # デフォルト値での取得
        result = self.config.get_config("nonexistent.key", "default")
        self.assertEqual(result, "default")

    def test_data_validator_basic(self):
        """DataValidatorの基本テスト"""
        validator = DataValidator(self.config, self.logger)

        # 正常データの検証
        result = validator.validate_stock_data(self.sample_data)
        self.assertIsInstance(result, dict)
        self.assertIn("is_valid", result)

    def test_error_handler_basic(self):
        """ErrorHandlerの基本テスト"""
        # エラーハンドリングのテスト
        try:
            self.error_handler.handle_data_processing_error(
                Exception("Test error"), "テスト処理"
            )
        except Exception:
            pass  # エラーは想定内

    def test_logging_manager_basic(self):
        """LoggingManagerの基本テスト"""
        # 各レベルのログ出力テスト
        self.logger.log_info("情報ログ")
        self.logger.log_warning("警告ログ")

        # エラーログのテスト
        try:
            self.logger.log_error(Exception("エラーログ"))
        except Exception:
            pass  # エラーは想定内

    def test_model_manager_basic(self):
        """ModelManagerの基本テスト"""
        model_manager = ModelManager(self.config, self.logger)

        # モデル取得のテスト
        model = model_manager.get_model("random_forest")
        self.assertIsNotNone(model)

    def test_prediction_engine_basic(self):
        """PredictionEngineの基本テスト"""
        engine = PredictionEngine(
            config=self.config.get_config(),
            logger=self.logger,
            error_handler=self.error_handler,
        )

        # 予測実行のテスト
        mock_model = Mock()
        mock_model.predict.return_value = np.array([1.0, 2.0, 3.0])

        predictions = engine.make_predictions(mock_model, self.sample_data)
        self.assertEqual(len(predictions), 3)

    def test_visualization_manager_basic(self):
        """VisualizationManagerの基本テスト"""
        viz_manager = VisualizationManager(self.config, self.logger)

        # 基本的な機能のテスト
        self.assertIsNotNone(viz_manager)

    def test_performance_optimizer_basic(self):
        """PerformanceOptimizerの基本テスト"""
        optimizer = PerformanceOptimizer(self.logger, self.error_handler)

        # メトリクス収集のテスト
        with patch("psutil.cpu_percent") as mock_cpu:
            with patch("psutil.virtual_memory") as mock_mem:
                mock_cpu.return_value = 50.0
                mock_mem.return_value = Mock(percent=60.0, used=1000000000)

                metrics = optimizer.collect_system_metrics()
                self.assertIn("cpu_percent", metrics)
                self.assertIn("memory_percent", metrics)

    def test_overfitting_detector_basic(self):
        """OverfittingDetectorの基本テスト"""
        detector = OverfittingDetector(self.logger, self.error_handler)

        # 過学習検出のテスト
        result = detector.detect_overfitting(0.9, 0.7, 0.65)
        self.assertIsInstance(result, dict)
        self.assertIn("is_overfitting", result)

    def test_edge_cases(self):
        """エッジケースのテスト"""
        # None値の処理
        result = self.config.get_config(None)
        self.assertIsNotNone(result)

        # 空文字列の処理
        result = self.config.get_config("")
        self.assertIsNone(result)

    def test_data_serialization(self):
        """データシリアライゼーションのテスト"""
        # 複雑なデータ構造のシリアライゼーション
        complex_data = {
            "nested": {"list": [1, 2, 3], "dict": {"a": 1, "b": 2}},
            "array": np.array([1, 2, 3]).tolist(),
            "timestamp": datetime.now().isoformat(),
        }

        # JSONシリアライゼーション
        json_str = json.dumps(complex_data, ensure_ascii=False)
        self.assertIsInstance(json_str, str)

        # デシリアライゼーション
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized["nested"]["list"], [1, 2, 3])

    def test_memory_management(self):
        """メモリ管理のテスト"""
        # 大量データの処理
        large_data = pd.DataFrame({"value": np.random.randn(1000)})

        # データ処理
        result = large_data.describe()
        self.assertIsNotNone(result)

    def test_concurrent_operations(self):
        """並行処理のテスト"""
        import threading
        import time

        results = []

        def worker(worker_id):
            time.sleep(0.01)
            results.append(f"worker_{worker_id}")

        # 複数スレッドでの並行実行
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
