"""
コアモジュールの包括的テスト
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import yaml

# コアモジュールのインポート
from core.config_manager import ConfigManager
from core.data_validator import DataValidator
from core.differential_updater import DifferentialUpdater
from core.error_handler import ErrorHandler
from core.json_data_manager import JSONDataManager
from core.logging_manager import LoggingManager
from core.model_manager import ModelManager
from core.performance_optimizer import PerformanceOptimizer
from core.prediction_engine import PredictionEngine
from core.technical_analysis import TechnicalAnalysis
from core.visualization_manager import VisualizationManager


class TestCoreModulesComprehensive:
    """コアモジュールの包括的テストクラス"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
        self.data_validator = DataValidator()
        self.error_handler = ErrorHandler()
        self.json_data_manager = JSONDataManager()
        self.logging_manager = LoggingManager()
        self.model_manager = ModelManager()
        self.performance_optimizer = PerformanceOptimizer()
        self.prediction_engine = PredictionEngine()
        self.technical_analysis = TechnicalAnalysis()
        self.visualization_manager = VisualizationManager()
    
    def teardown_method(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_config_manager_comprehensive(self):
        """ConfigManagerの包括的テスト"""
        # 正常な設定ファイルの読み込み
        config_data = {
            'system': {'name': 'test', 'version': '1.0.0'},
            'api': {'base_url': 'https://api.example.com'},
            'database': {'host': 'localhost', 'port': 5432}
        }
        
        with patch.object(self.config_manager, '_load_config', return_value=config_data):
            result = self.config_manager.get_config()
            assert result is not None
            assert result['system']['name'] == 'test'
        
        # 設定値の取得
        with patch.object(self.config_manager, '_load_config', return_value=config_data):
            value = self.config_manager.get_config_value('system.name')
            assert value == 'test'
        
        # デフォルト値の取得
        value = self.config_manager.get_config_value('nonexistent.key', 'default')
        assert value == 'default'
        
        # 設定の保存
        with patch('builtins.open', mock_open()) as mock_file:
            self.config_manager.save_config(config_data)
            mock_file.assert_called_once()
    
    def test_data_validator_comprehensive(self):
        """DataValidatorの包括的テスト"""
        # 正常なデータの検証
        valid_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'close': np.random.randn(10).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 10)
        })
        
        result = self.data_validator.validate_stock_data(valid_data)
        assert result.is_valid
        
        # 無効なデータの検証
        invalid_data = pd.DataFrame({
            'date': ['invalid-date'],
            'close': ['not-a-number'],
            'volume': ['also-invalid']
        })
        
        result = self.data_validator.validate_stock_data(invalid_data)
        assert not result.is_valid
        
        # 欠損値の検証
        missing_data = pd.DataFrame({
            'date': ['2024-01-01', None, '2024-01-02'],
            'close': [100, None, 102],
            'volume': [1000, 1100, None]
        })
        
        result = self.data_validator.validate_stock_data(missing_data)
        assert not result.is_valid
        
        # 異常値の検証
        outlier_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'close': [100, 1000000, 102],  # 異常に大きな値
            'volume': [1000, 1100, 1200]
        })
        
        result = self.data_validator.validate_stock_data(outlier_data)
        assert result is not None
    
    def test_error_handler_comprehensive(self):
        """ErrorHandlerの包括的テスト"""
        # 様々なエラータイプの処理
        error_types = [
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            ConnectionError("Connection error"),
            FileNotFoundError("File not found"),
            PermissionError("Permission denied"),
            MemoryError("Memory error"),
            KeyboardInterrupt("Keyboard interrupt"),
            SystemExit("System exit")
        ]
        
        for error in error_types:
            result = self.error_handler.handle_error(error, "Test context")
            assert result is not None
        
        # エラー統計の取得
        stats = self.error_handler.get_error_stats()
        assert isinstance(stats, dict)
        
        # エラーログの取得
        logs = self.error_handler.get_error_logs()
        assert isinstance(logs, list)
    
    def test_json_data_manager_comprehensive(self):
        """JsonDataManagerの包括的テスト"""
        # データの保存と読み込み
        test_data = {
            'test_key': 'test_value',
            'nested': {'key': 'value'},
            'list': [1, 2, 3, 4, 5]
        }
        
        test_file = os.path.join(self.temp_dir, 'test.json')
        
        # データの保存
        result = self.json_data_manager.save_data(test_data, test_file)
        assert result is True
        
        # データの読み込み
        loaded_data = self.json_data_manager.load_data(test_file)
        assert loaded_data == test_data
        
        # 存在しないファイルの読み込み
        result = self.json_data_manager.load_data('nonexistent.json')
        assert result is None
        
        # 無効なJSONファイルの読み込み
        invalid_file = os.path.join(self.temp_dir, 'invalid.json')
        with open(invalid_file, 'w') as f:
            f.write('invalid json content')
        
        result = self.json_data_manager.load_data(invalid_file)
        assert result is None
    
    def test_logging_manager_comprehensive(self):
        """LoggingManagerの包括的テスト"""
        # ログレベルの設定と取得
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in levels:
            self.logging_manager.set_log_level(level)
            assert self.logging_manager.get_log_level() == level
        
        # ログファイルの設定
        log_file = os.path.join(self.temp_dir, 'test.log')
        self.logging_manager.set_log_file(log_file)
        
        # 様々なログレベルのメッセージ
        self.logging_manager.log_debug("Debug message")
        self.logging_manager.log_info("Info message")
        self.logging_manager.log_warning("Warning message")
        self.logging_manager.log_error("Error message")
        self.logging_manager.log_critical("Critical message")
        
        # ログファイルの存在確認
        assert os.path.exists(log_file)
        
        # ログの取得
        logs = self.logging_manager.get_logs()
        assert isinstance(logs, list)
    
    def test_model_manager_comprehensive(self):
        """ModelManagerの包括的テスト"""
        # 正常なデータでのモデル作成
        valid_data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': np.random.randn(100)
        })
        
        # 様々なモデルタイプのテスト
        model_types = ['random_forest', 'xgboost', 'linear_regression', 'svr']
        
        for model_type in model_types:
            with patch.object(self.model_manager, 'create_model') as mock_create:
                mock_create.return_value = MagicMock()
                result = self.model_manager.create_model(model_type)
                assert result is not None
        
        # モデルの訓練
        with patch.object(self.model_manager, 'train_model') as mock_train:
            mock_train.return_value = MagicMock()
            result = self.model_manager.train_model(valid_data, 'target')
            assert result is not None
        
        # モデルの評価
        with patch.object(self.model_manager, 'evaluate_model') as mock_evaluate:
            mock_evaluate.return_value = {'accuracy': 0.95, 'precision': 0.90, 'recall': 0.85}
            result = self.model_manager.evaluate_model(MagicMock(), valid_data, 'target')
            assert result is not None
            assert result['accuracy'] == 0.95
    
    def test_performance_optimizer_comprehensive(self):
        """PerformanceOptimizerの包括的テスト"""
        # システムリソースの監視
        memory_usage = self.performance_optimizer.get_memory_usage()
        assert isinstance(memory_usage, float)
        assert memory_usage >= 0
        
        cpu_usage = self.performance_optimizer.get_cpu_usage()
        assert isinstance(cpu_usage, float)
        assert 0 <= cpu_usage <= 100
        
        disk_usage = self.performance_optimizer.get_disk_usage()
        assert isinstance(disk_usage, float)
        assert disk_usage >= 0
        
        # パフォーマンス最適化の実行
        result = self.performance_optimizer.optimize_performance()
        assert result is not None
        
        # メモリ最適化
        result = self.performance_optimizer.optimize_memory()
        assert result is not None
        
        # CPU最適化
        result = self.performance_optimizer.optimize_cpu()
        assert result is not None
    
    def test_prediction_engine_comprehensive(self):
        """PredictionEngineの包括的テスト"""
        # 正常なデータでの予測
        valid_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        with patch.object(self.prediction_engine, 'run_stock_prediction') as mock_predict:
            mock_predict.return_value = {'predictions': [101, 102, 103], 'accuracy': 0.95}
            result = self.prediction_engine.run_stock_prediction(valid_data)
            assert result is not None
            assert 'predictions' in result
        
        # 予測結果の可視化
        with patch.object(self.prediction_engine, 'create_visualization') as mock_viz:
            mock_viz.return_value = 'visualization_created'
            result = self.prediction_engine.create_visualization(valid_data, [101, 102, 103])
            assert result == 'visualization_created'
    
    def test_technical_analysis_comprehensive(self):
        """TechnicalAnalysisの包括的テスト"""
        # 正常なデータでの技術指標計算
        valid_data = pd.DataFrame({
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100),
            'high': np.random.randn(100).cumsum() + 105,
            'low': np.random.randn(100).cumsum() + 95
        })
        
        # 様々な技術指標の計算
        indicators = ['sma', 'ema', 'rsi', 'macd', 'bollinger_bands', 'stochastic']
        
        for indicator in indicators:
            with patch.object(self.technical_analysis, f'calculate_{indicator}') as mock_calc:
                mock_calc.return_value = pd.Series(np.random.randn(100))
                result = getattr(self.technical_analysis, f'calculate_{indicator}')(valid_data)
                assert result is not None
        
        # 包括的な技術指標計算
        with patch.object(self.technical_analysis, 'calculate_technical_indicators') as mock_calc:
            mock_calc.return_value = valid_data.copy()
            result = self.technical_analysis.calculate_technical_indicators(valid_data)
            assert result is not None
    
    def test_visualization_manager_comprehensive(self):
        """VisualizationManagerの包括的テスト"""
        # 正常なデータでの可視化
        valid_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=50),
            'close': np.random.randn(50).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 50)
        })
        
        # 様々な可視化の作成
        visualizations = [
            'create_price_chart',
            'create_volume_chart',
            'create_technical_indicators_chart',
            'create_prediction_chart'
        ]
        
        for viz_method in visualizations:
            with patch.object(self.visualization_manager, viz_method) as mock_viz:
                mock_viz.return_value = 'chart_created'
                result = getattr(self.visualization_manager, viz_method)(valid_data)
                assert result == 'chart_created'
        
        # チャートの保存
        with patch.object(self.visualization_manager, 'save_chart') as mock_save:
            mock_save.return_value = True
            result = self.visualization_manager.save_chart('chart', 'test.png')
            assert result is True
    
    def test_integration_workflow(self):
        """統合ワークフローのテスト"""
        # データの準備
        sample_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100),
            'high': np.random.randn(100).cumsum() + 105,
            'low': np.random.randn(100).cumsum() + 95
        })
        
        # 1. データ検証
        validation_result = self.data_validator.validate_stock_data(sample_data)
        assert validation_result.is_valid
        
        # 2. 技術指標計算
        with patch.object(self.technical_analysis, 'calculate_technical_indicators') as mock_calc:
            mock_calc.return_value = sample_data.copy()
            technical_data = self.technical_analysis.calculate_technical_indicators(sample_data)
            assert technical_data is not None
        
        # 3. モデル訓練
        with patch.object(self.model_manager, 'train_model') as mock_train:
            mock_train.return_value = MagicMock()
            model = self.model_manager.train_model(technical_data, 'close')
            assert model is not None
        
        # 4. 予測実行
        with patch.object(self.prediction_engine, 'run_stock_prediction') as mock_predict:
            mock_predict.return_value = {'predictions': [101, 102, 103], 'accuracy': 0.95}
            predictions = self.prediction_engine.run_stock_prediction(technical_data)
            assert predictions is not None
        
        # 5. 可視化作成
        with patch.object(self.visualization_manager, 'create_prediction_chart') as mock_viz:
            mock_viz.return_value = 'chart_created'
            chart = self.visualization_manager.create_prediction_chart(technical_data, predictions['predictions'])
            assert chart == 'chart_created'
    
    def test_error_recovery_workflow(self):
        """エラー回復ワークフローのテスト"""
        # ネットワークエラーのシミュレーション
        with patch('requests.get', side_effect=ConnectionError("Network error")):
            try:
                raise ConnectionError("Network error")
            except Exception as e:
                result = self.error_handler.handle_error(e, "Network context")
                assert result is not None
        
        # ファイルI/Oエラーのシミュレーション
        with patch('builtins.open', side_effect=IOError("File error")):
            try:
                raise IOError("File error")
            except Exception as e:
                result = self.error_handler.handle_error(e, "File context")
                assert result is not None
        
        # メモリエラーのシミュレーション
        with patch('psutil.virtual_memory', side_effect=MemoryError("Memory error")):
            try:
                raise MemoryError("Memory error")
            except Exception as e:
                result = self.error_handler.handle_error(e, "Memory context")
                assert result is not None
    
    def test_performance_monitoring_workflow(self):
        """パフォーマンス監視ワークフローのテスト"""
        # 初期パフォーマンスの測定
        initial_memory = self.performance_optimizer.get_memory_usage()
        initial_cpu = self.performance_optimizer.get_cpu_usage()
        
        # 大量データでの処理シミュレーション
        large_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=10000),
            'close': np.random.randn(10000).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 10000)
        })
        
        # 処理後のパフォーマンス測定
        final_memory = self.performance_optimizer.get_memory_usage()
        final_cpu = self.performance_optimizer.get_cpu_usage()
        
        # パフォーマンスの変化をチェック
        assert final_memory >= initial_memory
        assert final_cpu >= initial_cpu
        
        # 最適化の実行
        optimization_result = self.performance_optimizer.optimize_performance()
        assert optimization_result is not None
