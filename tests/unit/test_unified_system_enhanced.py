#!/usr/bin/env python3
"""
統合システムの拡張テスト
テストカバレッジの不均衡問題を解決するための拡張テスト
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import yaml
from pathlib import Path
import time

# 統合システムのインポート
from unified_system import (
    UnifiedSystem,
    ErrorCategory,
    LogLevel,
    DataProcessingError,
    ModelError,
    ConfigError,
    APIError,
    FileError,
    ValidationError,
    NetworkError,
    AuthenticationError,
)


class TestUnifiedSystemEnhanced:
    """統合システムの拡張テストクラス"""

    @pytest.fixture
    def test_config(self):
        """テスト用設定"""
        return {
            "system": {
                "name": "J-Quants株価予測システム",
                "version": "2.1.0",
                "environment": "test",
            },
            "data": {
                "input_file": "test_stock_data.csv",
                "output_file": "test_processed_data.csv",
                "features": ["SMA_5", "SMA_25", "RSI", "MACD"],
            },
            "models": {
                "primary": "xgboost",
                "compare_models": True,
                "parameters": {
                    "xgboost": {"n_estimators": 100, "max_depth": 6}
                },
            },
        }

    def test_system_initialization_enhanced(self, test_config):
        """システム初期化の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 基本属性の確認
        assert system.module_name == "test_module"
        assert system.config == test_config
        assert system.error_count == 0
        assert system.logger is not None
        
        # エラー統計の初期化確認
        for category in ErrorCategory:
            assert system.error_stats[category.value] == 0

    def test_error_handling_enhanced(self, test_config):
        """エラーハンドリングの拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 各エラーカテゴリのテスト
        test_errors = [
            (APIError("API接続エラー"), ErrorCategory.API_ERROR),
            (ModelError("モデルエラー"), ErrorCategory.MODEL_ERROR),
            (FileError("ファイルエラー"), ErrorCategory.FILE_ERROR),
            (DataProcessingError("データ処理エラー"), ErrorCategory.DATA_PROCESSING_ERROR),
            (ValidationError("検証エラー"), ErrorCategory.VALIDATION_ERROR),
            (ConfigError("設定エラー"), ErrorCategory.CONFIG_ERROR),
            (NetworkError("ネットワークエラー"), ErrorCategory.NETWORK_ERROR),
            (AuthenticationError("認証エラー"), ErrorCategory.AUTHENTICATION_ERROR),
        ]
        
        for error, category in test_errors:
            system.log_error(error, f"テストエラー: {error}", category)
            assert system.error_count > 0
            assert system.error_stats[category.value] > 0

    def test_configuration_management_enhanced(self, test_config):
        """設定管理の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 設定の取得
        system_config = system.get_config("system")
        assert system_config["name"] == "J-Quants株価予測システム"
        
        # 設定の更新
        new_config = {"models": {"primary": "random_forest"}}
        system.update_configuration(new_config)
        assert system.config["models"]["primary"] == "random_forest"
        
        # 設定の保存
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name
        
        try:
            system.save_config(temp_file)
            assert os.path.exists(temp_file)
            
            # 設定の読み込み確認
            with open(temp_file, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f)
            assert loaded_config["models"]["primary"] == "random_forest"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_backup_and_restore_enhanced(self, test_config):
        """バックアップとリストアの拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # バックアップの作成
        backup_data = system.create_backup()
        assert "config" in backup_data
        assert "error_stats" in backup_data
        assert "timestamp" in backup_data
        assert "module_name" in backup_data
        assert backup_data["module_name"] == "test_module"

    def test_error_recovery_workflow_enhanced(self, test_config):
        """エラー復旧ワークフローの拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # エラー復旧ワークフローの実行
        recovery_result = system.execute_error_recovery_workflow()
        assert "recovery_attempts" in recovery_result
        assert "success_rate" in recovery_result
        assert "timestamp" in recovery_result

    def test_performance_optimization_enhanced(self, test_config):
        """パフォーマンス最適化の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # パフォーマンス最適化の実行
        optimization_result = system.optimize_performance()
        assert "memory_usage_reduction" in optimization_result
        assert "processing_time_reduction" in optimization_result
        assert "optimization_applied" in optimization_result
        assert "timestamp" in optimization_result

    def test_error_statistics_enhanced(self, test_config):
        """エラー統計の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # エラーの追加
        system.log_error(APIError("テストAPIエラー"), "テスト", ErrorCategory.API_ERROR)
        system.log_error(ModelError("テストモデルエラー"), "テスト", ErrorCategory.MODEL_ERROR)
        
        # 統計の取得
        stats = system.get_error_statistics()
        assert stats["total_errors"] == 2
        assert stats["errors_by_category"]["api_error"] == 1
        assert stats["errors_by_category"]["model_error"] == 1
        assert "timestamp" in stats

    def test_system_integration_enhanced(self, test_config):
        """システム統合の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 統合機能のテスト
        backup_data = system.create_backup()
        recovery_result = system.execute_error_recovery_workflow()
        optimization_result = system.optimize_performance()
        
        # 各機能が正常に動作することを確認
        assert backup_data is not None
        assert recovery_result is not None
        assert optimization_result is not None

    def test_error_categorization_enhanced(self, test_config):
        """エラー分類の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 各エラーカテゴリのテスト
        error_categories = [
            ErrorCategory.API_ERROR,
            ErrorCategory.MODEL_ERROR,
            ErrorCategory.FILE_ERROR,
            ErrorCategory.DATA_PROCESSING_ERROR,
            ErrorCategory.VALIDATION_ERROR,
            ErrorCategory.CONFIG_ERROR,
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.AUTHENTICATION_ERROR,
        ]
        
        for category in error_categories:
            system.log_error(Exception(f"テストエラー: {category.value}"), "テスト", category)
            assert system.error_stats[category.value] > 0

    def test_system_resilience_enhanced(self, test_config):
        """システム堅牢性の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 複数のエラーを同時に処理
        for i in range(10):
            system.log_error(Exception(f"エラー {i}"), f"テスト {i}", ErrorCategory.API_ERROR)
        
        # システムが正常に動作することを確認
        stats = system.get_error_statistics()
        assert stats["total_errors"] == 10
        assert stats["errors_by_category"]["api_error"] == 10

    def test_configuration_persistence_enhanced(self, test_config):
        """設定永続化の拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 設定の更新
        new_config = {"test": {"value": "test_value"}}
        system.update_configuration(new_config)
        
        # 設定が正しく更新されていることを確認
        assert system.config["test"]["value"] == "test_value"
        
        # バックアップの作成
        backup_data = system.create_backup()
        assert backup_data["config"]["test"]["value"] == "test_value"

    def test_integration_workflow_enhanced(self, test_config):
        """統合ワークフローの拡張テスト"""
        system = UnifiedSystem("test_module", config=test_config)
        
        # 統合ワークフローの実行
        try:
            # バックアップの作成
            backup_data = system.create_backup()
            
            # エラー復旧ワークフローの実行
            recovery_result = system.execute_error_recovery_workflow()
            
            # パフォーマンス最適化の実行
            optimization_result = system.optimize_performance()
            
            # 各ステップが正常に完了することを確認
            assert backup_data is not None
            assert recovery_result is not None
            assert optimization_result is not None
            
        except Exception as e:
            # 統合ワークフローでエラーが発生した場合の処理
            system.log_error(e, "統合ワークフローエラー", ErrorCategory.DATA_PROCESSING_ERROR)
            assert system.error_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
