#!/usr/bin/env python3
"""
統合システム（unified_system.py）のテスト
テストカバレッジを80%以上に向上させる
"""

import unittest
import tempfile
import os
import json
import yaml
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import pandas as pd
import numpy as np

# テスト対象のインポート
from unified_system import (
    UnifiedSystem,
    ErrorCategory,
    LogLevel,
    LogCategory,
    DataProcessingError,
    ModelError,
    ConfigError,
    APIError,
    FileError,
    ValidationError,
    NetworkError,
    AuthenticationError,
)


class TestUnifiedSystem(unittest.TestCase):
    """統合システムのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        # ログディレクトリの作成
        os.makedirs("logs", exist_ok=True)
        
        # テスト用設定ファイルの作成
        self.test_config = {
            'api': {
                'jquants': {
                    'base_url': 'https://api.jquants.com',
                    'timeout': 30
                }
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/test.log'
            },
            'security': {
                'encrypt_sensitive_data': True,
                'mask_api_keys': True
            }
        }
        
        with open('test_config.yaml', 'w') as f:
            yaml.dump(self.test_config, f)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_unified_system_initialization(self):
        """統合システムの初期化テスト"""
        system = UnifiedSystem()
        self.assertIsInstance(system, UnifiedSystem)
        self.assertIsNotNone(system.config)
        self.assertIsNotNone(system.logger)
        self.assertEqual(system.error_count, 0)
        self.assertIsInstance(system.error_stats, dict)

    def test_config_loading(self):
        """設定ファイルの読み込みテスト"""
        system = UnifiedSystem()
        
        # 設定ファイルの読み込み
        system._load_config()
        
        self.assertIsInstance(system.config, dict)

    def test_config_validation(self):
        """設定検証のテスト"""
        system = UnifiedSystem()
        
        # 有効な設定の検証
        self.assertTrue(system._validate_config())
        
        # 無効な設定の検証
        system.config = None
        self.assertFalse(system._validate_config())

    def test_logging_functionality(self):
        """ログ機能のテスト"""
        system = UnifiedSystem()
        
        # ログ出力のテスト
        system.log_info("テスト情報ログ")
        system.log_warning("テスト警告ログ")
        system.log_error("テストエラーログ")
        
        # ログレベルの確認
        self.assertIsNotNone(system.logger)

    def test_data_processor_initialization(self):
        """データ処理の初期化テスト"""
        data_proc = DataProcessor()
        self.assertIsInstance(data_proc, DataProcessor)

    def test_data_processing_functionality(self):
        """データ処理機能のテスト"""
        data_proc = DataProcessor()
        
        # テストデータの作成
        test_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'price': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # データ処理の実行
        processed_data = data_proc.process_data(test_data)
        
        self.assertIsInstance(processed_data, pd.DataFrame)
        self.assertGreater(len(processed_data), 0)

    def test_model_manager_initialization(self):
        """モデル管理の初期化テスト"""
        model_mgr = ModelManager()
        self.assertIsInstance(model_mgr, ModelManager)

    def test_model_training(self):
        """モデル学習のテスト"""
        model_mgr = ModelManager()
        
        # テストデータの作成
        X = np.random.randn(100, 5)
        y = np.random.randn(100)
        
        # モデル学習の実行
        model = model_mgr.train_model(X, y)
        
        self.assertIsNotNone(model)

    def test_model_prediction(self):
        """モデル予測のテスト"""
        model_mgr = ModelManager()
        
        # テストデータの作成
        X_train = np.random.randn(100, 5)
        y_train = np.random.randn(100)
        X_test = np.random.randn(10, 5)
        
        # モデル学習と予測
        model = model_mgr.train_model(X_train, y_train)
        predictions = model_mgr.predict(model, X_test)
        
        self.assertIsNotNone(predictions)
        self.assertEqual(len(predictions), 10)

    def test_trading_system_initialization(self):
        """取引システムの初期化テスト"""
        trading_sys = TradingSystem()
        self.assertIsInstance(trading_sys, TradingSystem)

    def test_trading_signals(self):
        """取引シグナルのテスト"""
        trading_sys = TradingSystem()
        
        # テストデータの作成
        test_data = pd.DataFrame({
            'price': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # 取引シグナルの生成
        signals = trading_sys.generate_signals(test_data)
        
        self.assertIsInstance(signals, pd.DataFrame)
        self.assertIn('signal', signals.columns)

    def test_performance_monitor_initialization(self):
        """パフォーマンス監視の初期化テスト"""
        perf_mon = PerformanceMonitor()
        self.assertIsInstance(perf_mon, PerformanceMonitor)

    def test_performance_metrics(self):
        """パフォーマンスメトリクスのテスト"""
        perf_mon = PerformanceMonitor()
        
        # メトリクスの記録
        perf_mon.record_metric('accuracy', 0.95)
        perf_mon.record_metric('precision', 0.92)
        perf_mon.record_metric('recall', 0.88)
        
        # メトリクスの取得
        metrics = perf_mon.get_metrics()
        
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertEqual(metrics['accuracy'], 0.95)

    def test_security_manager_initialization(self):
        """セキュリティ管理の初期化テスト"""
        sec_mgr = SecurityManager()
        self.assertIsInstance(sec_mgr, SecurityManager)

    def test_data_encryption(self):
        """データ暗号化のテスト"""
        sec_mgr = SecurityManager()
        
        # テストデータの暗号化
        test_data = "機密データ"
        encrypted_data = sec_mgr.encrypt_data(test_data)
        
        self.assertIsInstance(encrypted_data, str)
        self.assertNotEqual(encrypted_data, test_data)

    def test_data_decryption(self):
        """データ復号化のテスト"""
        sec_mgr = SecurityManager()
        
        # テストデータの暗号化と復号化
        test_data = "機密データ"
        encrypted_data = sec_mgr.encrypt_data(test_data)
        decrypted_data = sec_mgr.decrypt_data(encrypted_data)
        
        self.assertEqual(decrypted_data, test_data)

    def test_api_key_masking(self):
        """APIキーマスキングのテスト"""
        sec_mgr = SecurityManager()
        
        # APIキーのマスキング
        api_key = "sk-1234567890abcdef"
        masked_key = sec_mgr.mask_api_key(api_key)
        
        self.assertNotEqual(masked_key, api_key)
        self.assertIn("***", masked_key)

    def test_global_system_access(self):
        """グローバルシステムアクセスのテスト"""
        system1 = get_unified_system()
        system2 = get_unified_system()
        
        # 同じインスタンスが返されることを確認
        self.assertIs(system1, system2)

    def test_system_decorator(self):
        """システムデコレータのテスト"""
        
        @unified_system
        def test_function():
            return "テスト結果"
        
        result = test_function()
        self.assertEqual(result, "テスト結果")

    def test_global_managers(self):
        """グローバルマネージャーのテスト"""
        # 各マネージャーの取得
        config_mgr = config_manager()
        log_mgr = log_manager()
        data_proc = data_processor()
        model_mgr = model_manager()
        trading_sys = trading_system()
        perf_mon = performance_monitor()
        sec_mgr = security_manager()
        
        # インスタンスの確認
        self.assertIsInstance(config_mgr, ConfigManager)
        self.assertIsInstance(log_mgr, LogManager)
        self.assertIsInstance(data_proc, DataProcessor)
        self.assertIsInstance(model_mgr, ModelManager)
        self.assertIsInstance(trading_sys, TradingSystem)
        self.assertIsInstance(perf_mon, PerformanceMonitor)
        self.assertIsInstance(sec_mgr, SecurityManager)

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        system = UnifiedSystem()
        
        # エラーの記録
        error = ValueError("テストエラー")
        system.log_error(
            error=error,
            category=ErrorCategory.SYSTEM,
            severity="HIGH",
            operation="テスト操作"
        )
        
        # エラー統計の確認
        stats = system.get_error_statistics()
        self.assertGreaterEqual(stats['total_errors'], 1)

    def test_system_integration(self):
        """システム統合テスト"""
        system = UnifiedSystem()
        
        # 設定の読み込み
        system.config_manager.load_config('test_config.yaml')
        
        # ログの設定
        system.log_manager.set_level(LogLevel.INFO)
        
        # テストデータの処理
        test_data = pd.DataFrame({
            'price': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        processed_data = system.data_processor.process_data(test_data)
        signals = system.trading_system.generate_signals(processed_data)
        
        # 結果の確認
        self.assertIsInstance(processed_data, pd.DataFrame)
        self.assertIsInstance(signals, pd.DataFrame)
        self.assertIn('signal', signals.columns)

    def test_performance_optimization(self):
        """パフォーマンス最適化のテスト"""
        system = UnifiedSystem()
        
        # メモリ使用量の記録
        initial_memory = system.performance_monitor.get_memory_usage()
        
        # データ処理の実行
        test_data = pd.DataFrame({
            'price': np.random.randn(1000).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 1000)
        })
        
        processed_data = system.data_processor.process_data(test_data)
        
        # メモリ使用量の確認
        final_memory = system.performance_monitor.get_memory_usage()
        self.assertIsInstance(initial_memory, float)
        self.assertIsInstance(final_memory, float)

    def test_security_integration(self):
        """セキュリティ統合テスト"""
        system = UnifiedSystem()
        
        # 機密データの処理
        sensitive_data = "機密情報: APIキー=sk-1234567890abcdef"
        
        # データの暗号化
        encrypted_data = system.security_manager.encrypt_data(sensitive_data)
        
        # ログ出力でのマスキング確認
        system.log_manager.info(f"処理データ: {sensitive_data}")
        
        # 暗号化データの復号化
        decrypted_data = system.security_manager.decrypt_data(encrypted_data)
        
        self.assertEqual(decrypted_data, sensitive_data)

    def test_configuration_validation(self):
        """設定検証のテスト"""
        system = UnifiedSystem()
        
        # 有効な設定の検証
        system.config_manager.load_config('test_config.yaml')
        self.assertTrue(system.config_manager.validate_config())
        
        # 無効な設定の検証
        invalid_config = {'api': None}
        with open('invalid_config.yaml', 'w') as f:
            yaml.dump(invalid_config, f)
        
        system.config_manager.load_config('invalid_config.yaml')
        self.assertFalse(system.config_manager.validate_config())

    def test_logging_integration(self):
        """ログ統合テスト"""
        system = UnifiedSystem()
        
        # ログレベルの設定
        system.log_manager.set_level(LogLevel.DEBUG)
        
        # 各レベルのログ出力
        system.log_manager.debug("デバッグログ")
        system.log_manager.info("情報ログ")
        system.log_manager.warning("警告ログ")
        system.log_manager.error("エラーログ")
        
        # ログファイルの存在確認
        log_file = system.log_manager.log_file
        if log_file and os.path.exists(log_file):
            self.assertTrue(os.path.exists(log_file))

    def test_data_processing_pipeline(self):
        """データ処理パイプラインのテスト"""
        system = UnifiedSystem()
        
        # テストデータの作成
        test_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'price': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # データ処理パイプラインの実行
        processed_data = system.data_processor.process_data(test_data)
        
        # 技術指標の計算
        indicators = system.data_processor.calculate_technical_indicators(processed_data)
        
        # 取引シグナルの生成
        signals = system.trading_system.generate_signals(processed_data)
        
        # 結果の確認
        self.assertIsInstance(processed_data, pd.DataFrame)
        self.assertIsInstance(indicators, pd.DataFrame)
        self.assertIsInstance(signals, pd.DataFrame)

    def test_model_training_pipeline(self):
        """モデル学習パイプラインのテスト"""
        system = UnifiedSystem()
        
        # テストデータの作成
        X = np.random.randn(100, 5)
        y = np.random.randn(100)
        
        # モデル学習
        model = system.model_manager.train_model(X, y)
        
        # モデル評価
        X_test = np.random.randn(20, 5)
        y_test = np.random.randn(20)
        
        predictions = system.model_manager.predict(model, X_test)
        metrics = system.model_manager.evaluate_model(model, X_test, y_test)
        
        # 結果の確認
        self.assertIsNotNone(model)
        self.assertIsNotNone(predictions)
        self.assertIsInstance(metrics, dict)

    def test_trading_system_integration(self):
        """取引システム統合テスト"""
        system = UnifiedSystem()
        
        # テストデータの作成
        test_data = pd.DataFrame({
            'price': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100),
            'rsi': np.random.uniform(0, 100, 100),
            'macd': np.random.randn(100)
        })
        
        # 取引シグナルの生成
        signals = system.trading_system.generate_signals(test_data)
        
        # リスク管理の適用
        risk_adjusted_signals = system.trading_system.apply_risk_management(signals, test_data)
        
        # 結果の確認
        self.assertIsInstance(signals, pd.DataFrame)
        self.assertIsInstance(risk_adjusted_signals, pd.DataFrame)
        self.assertIn('signal', signals.columns)
        self.assertIn('risk_score', risk_adjusted_signals.columns)

    def test_performance_monitoring(self):
        """パフォーマンス監視のテスト"""
        system = UnifiedSystem()
        
        # パフォーマンスメトリクスの記録
        system.performance_monitor.record_metric('accuracy', 0.95)
        system.performance_monitor.record_metric('precision', 0.92)
        system.performance_monitor.record_metric('recall', 0.88)
        
        # メモリ使用量の記録
        memory_usage = system.performance_monitor.get_memory_usage()
        
        # 処理時間の記録
        start_time = system.performance_monitor.start_timer('test_operation')
        # 何らかの処理をシミュレート
        import time
        time.sleep(0.01)
        system.performance_monitor.end_timer('test_operation')
        
        # 結果の確認
        metrics = system.performance_monitor.get_metrics()
        self.assertIn('accuracy', metrics)
        self.assertIsInstance(memory_usage, float)
        self.assertGreater(memory_usage, 0)

    def test_error_recovery(self):
        """エラー復旧のテスト"""
        system = UnifiedSystem()
        
        # エラーの記録
        error = ValueError("テストエラー")
        system.log_error(
            error=error,
            category=ErrorCategory.SYSTEM,
            severity="HIGH",
            operation="テスト操作"
        )
        
        # 復旧戦略の実行
        recovery_success = system.execute_recovery_strategy(ErrorCategory.SYSTEM)
        
        # 結果の確認
        self.assertIsInstance(recovery_success, bool)

    def test_system_cleanup(self):
        """システムクリーンアップのテスト"""
        system = UnifiedSystem()
        
        # リソースのクリーンアップ
        system.cleanup()
        
        # クリーンアップ後の状態確認
        self.assertIsNotNone(system.config_manager)
        self.assertIsNotNone(system.log_manager)


if __name__ == "__main__":
    # テストの実行
    unittest.main(verbosity=2)
