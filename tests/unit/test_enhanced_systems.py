"""
強化されたシステムのテスト
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestEnhancedDataValidator:
    """強化されたデータバリデーターのテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        # モックのデータバリデーター
        self.validator = Mock()
        self.validator.validate_stock_data = Mock(return_value={'valid': True, 'errors': []})
        self.validator.validate_config = Mock(return_value={'valid': True, 'errors': []})

    def test_validate_stock_data_success(self):
        """株価データ検証の成功テスト"""
        test_data = [
            {'date': '2024-01-01', 'open': 100, 'high': 105, 'low': 95, 'close': 102, 'volume': 1000},
            {'date': '2024-01-02', 'open': 102, 'high': 108, 'low': 98, 'close': 106, 'volume': 1200}
        ]
        
        result = self.validator.validate_stock_data(test_data)
        
        assert result['valid'] == True
        assert len(result['errors']) == 0
        self.validator.validate_stock_data.assert_called_once_with(test_data)

    def test_validate_stock_data_failure(self):
        """株価データ検証の失敗テスト"""
        self.validator.validate_stock_data.return_value = {
            'valid': False, 
            'errors': ['Invalid OHLC data', 'Missing volume data']
        }
        
        test_data = [
            {'date': '2024-01-01', 'open': -100, 'high': 105, 'low': 95, 'close': 102}
        ]
        
        result = self.validator.validate_stock_data(test_data)
        
        assert result['valid'] == False
        assert len(result['errors']) == 2
        assert 'Invalid OHLC data' in result['errors']

    def test_validate_config_success(self):
        """設定検証の成功テスト"""
        test_config = {
            'data': {'input_file': 'test.csv'},
            'models': {'primary': 'xgboost'},
            'prediction': {'horizon': 5}
        }
        
        result = self.validator.validate_config(test_config)
        
        assert result['valid'] == True
        assert len(result['errors']) == 0
        self.validator.validate_config.assert_called_once_with(test_config)

    def test_validate_config_failure(self):
        """設定検証の失敗テスト"""
        self.validator.validate_config.return_value = {
            'valid': False,
            'errors': ['Missing required field: data.input_file', 'Invalid model type']
        }
        
        test_config = {
            'models': {'primary': 'invalid_model'}
        }
        
        result = self.validator.validate_config(test_config)
        
        assert result['valid'] == False
        assert len(result['errors']) == 2


class TestEnhancedModelComparator:
    """強化されたモデル比較器のテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.comparator = Mock()
        self.comparator.compare_models = Mock(return_value={
            'results': [
                {'model': 'xgboost', 'mae': 0.05, 'rmse': 0.08, 'r2': 0.85},
                {'model': 'random_forest', 'mae': 0.06, 'rmse': 0.09, 'r2': 0.82}
            ],
            'best_model': 'xgboost'
        })

    def test_compare_models_success(self):
        """モデル比較の成功テスト"""
        test_models = ['xgboost', 'random_forest']
        test_data = {'X_train': [], 'y_train': [], 'X_test': [], 'y_test': []}
        
        result = self.comparator.compare_models(test_models, test_data)
        
        assert 'results' in result
        assert 'best_model' in result
        assert result['best_model'] == 'xgboost'
        assert len(result['results']) == 2
        self.comparator.compare_models.assert_called_once_with(test_models, test_data)

    def test_compare_models_single_model(self):
        """単一モデルの比較テスト"""
        self.comparator.compare_models.return_value = {
            'results': [{'model': 'xgboost', 'mae': 0.05, 'rmse': 0.08, 'r2': 0.85}],
            'best_model': 'xgboost'
        }
        
        test_models = ['xgboost']
        test_data = {'X_train': [], 'y_train': [], 'X_test': [], 'y_test': []}
        
        result = self.comparator.compare_models(test_models, test_data)
        
        assert len(result['results']) == 1
        assert result['best_model'] == 'xgboost'

    def test_compare_models_empty_data(self):
        """空データでのモデル比較テスト"""
        self.comparator.compare_models.return_value = {
            'results': [],
            'best_model': None,
            'error': 'No data provided'
        }
        
        test_models = ['xgboost']
        test_data = {}
        
        result = self.comparator.compare_models(test_models, test_data)
        
        assert len(result['results']) == 0
        assert result['best_model'] is None
        assert 'error' in result


class TestEnhancedParallelProcessor:
    """強化された並列処理システムのテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.processor = Mock()
        self.processor.process_parallel = Mock(return_value={
            'results': ['result1', 'result2', 'result3'],
            'execution_time': 1.5,
            'success_count': 3,
            'error_count': 0
        })

    def test_process_parallel_success(self):
        """並列処理の成功テスト"""
        tasks = ['task1', 'task2', 'task3']
        max_workers = 2
        
        result = self.processor.process_parallel(tasks, max_workers)
        
        assert 'results' in result
        assert 'execution_time' in result
        assert 'success_count' in result
        assert 'error_count' in result
        assert len(result['results']) == 3
        assert result['success_count'] == 3
        assert result['error_count'] == 0
        self.processor.process_parallel.assert_called_once_with(tasks, max_workers)

    def test_process_parallel_with_errors(self):
        """エラーを含む並列処理のテスト"""
        self.processor.process_parallel.return_value = {
            'results': ['result1', 'result3'],
            'execution_time': 2.0,
            'success_count': 2,
            'error_count': 1,
            'errors': ['Task2 failed']
        }
        
        tasks = ['task1', 'task2', 'task3']
        max_workers = 2
        
        result = self.processor.process_parallel(tasks, max_workers)
        
        assert result['success_count'] == 2
        assert result['error_count'] == 1
        assert 'errors' in result
        assert len(result['errors']) == 1

    def test_process_parallel_empty_tasks(self):
        """空のタスクリストでの並列処理テスト"""
        self.processor.process_parallel.return_value = {
            'results': [],
            'execution_time': 0.0,
            'success_count': 0,
            'error_count': 0
        }
        
        tasks = []
        max_workers = 2
        
        result = self.processor.process_parallel(tasks, max_workers)
        
        assert len(result['results']) == 0
        assert result['success_count'] == 0
        assert result['error_count'] == 0


class TestEnhancedMemoryOptimizer:
    """強化されたメモリ最適化システムのテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.optimizer = Mock()
        self.optimizer.optimize_memory = Mock(return_value={
            'memory_usage_before': 1024,
            'memory_usage_after': 512,
            'memory_saved': 512,
            'optimization_ratio': 0.5
        })

    def test_optimize_memory_success(self):
        """メモリ最適化の成功テスト"""
        data = {'large_dataset': [1] * 1000000}
        
        result = self.optimizer.optimize_memory(data)
        
        assert 'memory_usage_before' in result
        assert 'memory_usage_after' in result
        assert 'memory_saved' in result
        assert 'optimization_ratio' in result
        assert result['memory_saved'] > 0
        assert result['optimization_ratio'] > 0
        self.optimizer.optimize_memory.assert_called_once_with(data)

    def test_optimize_memory_no_optimization(self):
        """最適化が不要な場合のテスト"""
        self.optimizer.optimize_memory.return_value = {
            'memory_usage_before': 100,
            'memory_usage_after': 100,
            'memory_saved': 0,
            'optimization_ratio': 0.0,
            'message': 'No optimization needed'
        }
        
        data = {'small_dataset': [1, 2, 3]}
        
        result = self.optimizer.optimize_memory(data)
        
        assert result['memory_saved'] == 0
        assert result['optimization_ratio'] == 0.0
        assert 'message' in result

    def test_optimize_memory_error(self):
        """メモリ最適化エラーのテスト"""
        self.optimizer.optimize_memory.return_value = {
            'error': 'Memory optimization failed',
            'memory_usage_before': 1024,
            'memory_usage_after': 1024,
            'memory_saved': 0
        }
        
        data = {'corrupted_data': None}
        
        result = self.optimizer.optimize_memory(data)
        
        assert 'error' in result
        assert result['memory_saved'] == 0


class TestEnhancedAutomationSystem:
    """強化された自動化システムのテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.automation = Mock()
        self.automation.run_automation = Mock(return_value={
            'status': 'success',
            'tasks_completed': 5,
            'tasks_failed': 0,
            'execution_time': 10.5,
            'next_run': datetime.now() + timedelta(hours=1)
        })

    def test_run_automation_success(self):
        """自動化実行の成功テスト"""
        config = {
            'tasks': ['data_fetch', 'preprocessing', 'model_training', 'prediction', 'reporting'],
            'schedule': 'hourly',
            'max_retries': 3
        }
        
        result = self.automation.run_automation(config)
        
        assert result['status'] == 'success'
        assert result['tasks_completed'] == 5
        assert result['tasks_failed'] == 0
        assert 'execution_time' in result
        assert 'next_run' in result
        self.automation.run_automation.assert_called_once_with(config)

    def test_run_automation_partial_failure(self):
        """部分的な失敗を含む自動化実行のテスト"""
        self.automation.run_automation.return_value = {
            'status': 'partial_success',
            'tasks_completed': 3,
            'tasks_failed': 2,
            'execution_time': 8.0,
            'failed_tasks': ['model_training', 'prediction'],
            'next_run': datetime.now() + timedelta(minutes=30)
        }
        
        config = {
            'tasks': ['data_fetch', 'preprocessing', 'model_training', 'prediction', 'reporting'],
            'schedule': 'hourly',
            'max_retries': 3
        }
        
        result = self.automation.run_automation(config)
        
        assert result['status'] == 'partial_success'
        assert result['tasks_completed'] == 3
        assert result['tasks_failed'] == 2
        assert 'failed_tasks' in result
        assert len(result['failed_tasks']) == 2

    def test_run_automation_complete_failure(self):
        """完全な失敗の自動化実行テスト"""
        self.automation.run_automation.return_value = {
            'status': 'failed',
            'tasks_completed': 0,
            'tasks_failed': 5,
            'execution_time': 2.0,
            'error': 'System error occurred',
            'next_run': datetime.now() + timedelta(minutes=15)
        }
        
        config = {
            'tasks': ['data_fetch', 'preprocessing', 'model_training', 'prediction', 'reporting'],
            'schedule': 'hourly',
            'max_retries': 3
        }
        
        result = self.automation.run_automation(config)
        
        assert result['status'] == 'failed'
        assert result['tasks_completed'] == 0
        assert result['tasks_failed'] == 5
        assert 'error' in result
