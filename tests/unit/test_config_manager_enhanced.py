#!/usr/bin/env python3
"""
設定管理システムの拡張テスト
カバレッジ98%目標達成のための追加テスト
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, mock_open
from core.config_manager import ConfigManager


class TestConfigManagerEnhanced:
    """設定管理システムの拡張テストクラス"""

    def test_get_system_config(self):
        """システム設定の取得テスト"""
        config_manager = ConfigManager()
        system_config = config_manager._get_system_config()
        
        assert isinstance(system_config, dict)
        assert "name" in system_config
        assert "version" in system_config
        assert "environment" in system_config
        assert "debug" in system_config
        assert system_config["name"] == "J-Quants株価予測システム"

    def test_get_logging_config(self):
        """ログ設定の取得テスト"""
        config_manager = ConfigManager()
        logging_config = config_manager._get_logging_config()
        
        assert isinstance(logging_config, dict)
        assert "level" in logging_config
        assert "file" in logging_config
        assert "console_output" in logging_config
        assert logging_config["level"] == "INFO"

    def test_get_security_config(self):
        """セキュリティ設定の取得テスト"""
        config_manager = ConfigManager()
        security_config = config_manager._get_security_config()
        
        assert isinstance(security_config, dict)
        assert "sensitive_keys" in security_config
        assert "mask_sensitive_data" in security_config
        assert "encryption_enabled" in security_config
        assert isinstance(security_config["sensitive_keys"], list)

    def test_get_error_handling_config(self):
        """エラーハンドリング設定の取得テスト"""
        config_manager = ConfigManager()
        error_config = config_manager._get_error_handling_config()
        
        assert isinstance(error_config, dict)
        assert "unified_handler" in error_config
        assert "error_statistics" in error_config
        assert "auto_recovery" in error_config
        assert "max_recovery_attempts" in error_config

    def test_get_prediction_config(self):
        """予測設定の取得テスト"""
        config_manager = ConfigManager()
        prediction_config = config_manager._get_prediction_config()
        
        assert isinstance(prediction_config, dict)
        assert "input_file" in prediction_config
        assert "features" in prediction_config
        assert "target" in prediction_config
        assert "test_size" in prediction_config
        assert "model_selection" in prediction_config

    def test_get_performance_config(self):
        """パフォーマンス設定の取得テスト"""
        config_manager = ConfigManager()
        performance_config = config_manager._get_performance_config()
        
        assert isinstance(performance_config, dict)
        assert "memory_limit_mb" in performance_config
        assert "chunk_size" in performance_config
        assert "max_workers" in performance_config
        assert "use_cache" in performance_config

    def test_apply_environment_config_no_environments(self):
        """環境別設定が存在しない場合のテスト"""
        config_manager = ConfigManager()
        config_manager.config = {"system": {"environment": "production"}}
        
        # 環境別設定が存在しない場合
        config_manager.config["environments"] = {}
        config_manager._apply_environment_config()
        
        # エラーが発生しないことを確認
        assert "system" in config_manager.config

    def test_apply_environment_config_environment_not_found(self):
        """指定された環境が存在しない場合のテスト"""
        config_manager = ConfigManager()
        config_manager.config = {
            "system": {"environment": "nonexistent"},
            "environments": {"production": {"debug": False}}
        }
        
        config_manager._apply_environment_config()
        
        # エラーが発生しないことを確認
        assert "system" in config_manager.config

    def test_deep_merge_with_nested_dicts(self):
        """ネストした辞書の深いマージテスト"""
        config_manager = ConfigManager()
        
        base = {
            "system": {"name": "Test", "version": "1.0"},
            "logging": {"level": "INFO"}
        }
        
        override = {
            "system": {"version": "2.0", "debug": True},
            "new_section": {"key": "value"}
        }
        
        config_manager._deep_merge(base, override)
        
        assert base["system"]["name"] == "Test"  # 保持される
        assert base["system"]["version"] == "2.0"  # 上書きされる
        assert base["system"]["debug"] is True  # 新しく追加される
        assert base["logging"]["level"] == "INFO"  # 保持される
        assert base["new_section"]["key"] == "value"  # 新しく追加される

    def test_deep_merge_with_non_dict_override(self):
        """非辞書値での上書きテスト"""
        config_manager = ConfigManager()
        
        base = {"key": "original"}
        override = {"key": "overridden"}
        
        config_manager._deep_merge(base, override)
        
        assert base["key"] == "overridden"

    def test_load_config_file_error_handling(self):
        """設定ファイル読み込みエラーのハンドリングテスト"""
        with patch("builtins.open", side_effect=IOError("File not found")):
            config_manager = ConfigManager()
            
            # デフォルト設定が作成されることを確認
            assert "system" in config_manager.config
            assert config_manager.config["system"]["name"] == "J-Quants株価予測システム"

    def test_load_config_file_none_content(self):
        """設定ファイルがNoneの場合のテスト"""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("yaml.safe_load", return_value=None):
                config_manager = ConfigManager()
                
                # デフォルト設定が作成されることを確認
                assert "system" in config_manager.config

    def test_validate_config_with_api_key(self):
        """APIキーが設定されている場合の検証テスト"""
        config_manager = ConfigManager()
        config_manager.config = {
            "system": {"environment": "production"},
            "jquants": {"api_key": "test_key"}
        }
        
        result = config_manager.validate_config()
        assert result["valid"] is True

    def test_validate_config_without_api_key_production(self):
        """本番環境でAPIキーが設定されていない場合のテスト"""
        config_manager = ConfigManager()
        config_manager.config = {
            "system": {"environment": "production"},
            "jquants": {}
        }
        
        result = config_manager.validate_config()
        assert result["valid"] is False
        assert "API key" in result["errors"][0]

    def test_validate_config_test_environment(self):
        """テスト環境での検証テスト"""
        config_manager = ConfigManager()
        config_manager.config = {
            "system": {"environment": "test"},
            "jquants": {}
        }
        
        result = config_manager.validate_config()
        assert result["valid"] is True

    def test_validate_config_exception(self):
        """検証処理での例外ハンドリングテスト"""
        config_manager = ConfigManager()
        
        with patch.object(config_manager, 'config', side_effect=Exception("Test error")):
            result = config_manager.validate_config()
            assert result["valid"] is False
            assert "Test error" in result["errors"][0]

    def test_save_config_exception(self):
        """設定保存での例外ハンドリングテスト"""
        config_manager = ConfigManager()
        
        with patch("builtins.open", side_effect=IOError("Write error")):
            result = config_manager.save_config()
            assert result is False

    def test_update_configuration_exception(self):
        """設定更新での例外ハンドリングテスト"""
        config_manager = ConfigManager()
        
        with patch.object(config_manager, 'config', side_effect=Exception("Update error")):
            result = config_manager.update_configuration({"test": "value"})
            assert result is False

    def test_create_backup_exception(self):
        """バックアップ作成での例外ハンドリングテスト"""
        config_manager = ConfigManager()
        
        with patch("builtins.open", side_effect=IOError("Backup error")):
            result = config_manager.create_backup()
            assert result is False

    def test_restore_from_backup_exception(self):
        """バックアップ復元での例外ハンドリングテスト"""
        config_manager = ConfigManager()
        
        with patch("builtins.open", side_effect=IOError("Restore error")):
            result = config_manager.restore_from_backup("backup_file.json")
            assert result is False

    def test_restore_from_backup_none_config(self):
        """バックアップファイルがNoneの場合のテスト"""
        config_manager = ConfigManager()
        
        with patch("builtins.open", mock_open(read_data="")):
            with patch("json.load", return_value=None):
                result = config_manager.restore_from_backup("backup_file.json")
                assert result is False

    def test_restore_from_backup_none_data(self):
        """バックアップデータがNoneの場合のテスト"""
        config_manager = ConfigManager()
        
        with patch("builtins.open", mock_open(read_data="")):
            with patch("json.load", return_value={"config": None}):
                result = config_manager.restore_from_backup("backup_file.json")
                assert result is False

    def test_get_config_key_error(self):
        """存在しないキーでの設定取得テスト"""
        config_manager = ConfigManager()
        
        result = config_manager.get_config("nonexistent.key")
        assert result is None

    def test_get_config_type_error(self):
        """型エラーでの設定取得テスト"""
        config_manager = ConfigManager()
        config_manager.config = {"key": "string"}
        
        # 辞書としてアクセスしようとする
        result = config_manager.get_config("key.nested")
        assert result is None

    def test_set_config_create_nested(self):
        """ネストした設定の作成テスト"""
        config_manager = ConfigManager()
        config_manager.config = {}
        
        config_manager.set_config("nested.key.value", "test")
        
        assert config_manager.config["nested"]["key"]["value"] == "test"

    def test_apply_environment_config_no_environments_key(self):
        """environmentsキーが存在しない場合のテスト"""
        config_manager = ConfigManager()
        config_manager.config = {"system": {"environment": "production"}}
        
        config_manager._apply_environment_config()
        
        # エラーが発生しないことを確認
        assert "system" in config_manager.config
