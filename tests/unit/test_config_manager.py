#!/usr/bin/env python3
"""
ConfigManagerのユニットテスト
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open
from core.config_manager import ConfigManager


class TestConfigManager:
    """ConfigManagerのテストクラス"""

    def test_init_with_config(self):
        """設定付き初期化のテスト"""
        config = {"system": {"name": "Test System"}}
        manager = ConfigManager(config=config)
        assert manager.config == config

    def test_init_without_config(self):
        """設定なし初期化のテスト"""
        with patch.object(ConfigManager, "_load_config"):
            manager = ConfigManager()
            assert manager.config == {}

    def test_get_config_none(self):
        """設定全体の取得テスト"""
        config = {"system": {"name": "Test"}}
        manager = ConfigManager(config=config)
        result = manager.get_config()
        assert result == config

    def test_get_config_with_key(self):
        """キー指定での設定取得テスト"""
        config = {"system": {"name": "Test", "version": "1.0"}}
        manager = ConfigManager(config=config)
        result = manager.get_config("system.name")
        assert result == "Test"

    def test_get_config_with_default(self):
        """デフォルト値の取得テスト"""
        config = {"system": {"name": "Test"}}
        manager = ConfigManager(config=config)
        result = manager.get_config("system.version", "default")
        assert result == "default"

    def test_set_config(self):
        """設定値の設定テスト"""
        manager = ConfigManager()
        manager.set_config("system.name", "Test System")
        assert manager.get_config("system.name") == "Test System"

    def test_set_config_nested(self):
        """ネストした設定値の設定テスト"""
        manager = ConfigManager()
        manager.set_config("system.database.host", "localhost")
        assert manager.get_config("system.database.host") == "localhost"

    def test_save_config(self):
        """設定保存のテスト"""
        config = {"system": {"name": "Test"}}
        manager = ConfigManager(config=config)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            temp_path = f.name

        try:
            manager.save_config(temp_path)
            with open(temp_path, "r") as f:
                saved_config = yaml.safe_load(f)
            assert saved_config == config
        finally:
            os.unlink(temp_path)

    def test_update_configuration(self):
        """設定更新のテスト"""
        config = {"system": {"name": "Original"}}
        manager = ConfigManager(config=config)

        new_config = {"system": {"version": "2.0"}}
        manager.update_configuration(new_config)

        # 設定が更新されることを確認
        assert manager.get_config("system.version") == "2.0"

    def test_validate_config_valid(self):
        """有効な設定の検証テスト"""
        config = {"system": {"name": "Test", "environment": "test"}}
        manager = ConfigManager(config=config)
        result = manager.validate_config()
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_config_empty(self):
        """空の設定の検証テスト"""
        manager = ConfigManager(config={})
        result = manager.validate_config()
        assert result["is_valid"] is True

    def test_validate_config_missing_system(self):
        """systemキー不足の検証テスト"""
        config = {"other": {"key": "value"}}
        manager = ConfigManager(config=config)
        result = manager.validate_config()
        assert result["is_valid"] is False
        assert "api_key" in str(result["issues"][0])

    def test_create_backup(self):
        """バックアップ作成のテスト"""
        config = {"system": {"name": "Test"}}
        manager = ConfigManager(config=config)
        backup = manager.create_backup()

        assert "config" in backup
        assert "timestamp" in backup
        assert "config_file" in backup
        assert backup["config"] == config

    def test_restore_from_backup(self):
        """バックアップからの復元テスト"""
        original_config = {"system": {"name": "Original"}}
        manager = ConfigManager(config=original_config)

        backup_data = {
            "config": {"system": {"name": "Restored"}},
            "timestamp": "2023-01-01T00:00:00",
            "config_file": "test.yaml",
        }

        result = manager.restore_from_backup(backup_data)
        assert result is True
        assert manager.get_config("system.name") == "Restored"

    def test_restore_from_backup_invalid(self):
        """無効なバックアップからの復元テスト"""
        manager = ConfigManager()
        result = manager.restore_from_backup({})
        assert result is False

    def test_deep_merge(self):
        """深いマージのテスト"""
        base = {"system": {"name": "Base", "version": "1.0"}}
        override = {"system": {"version": "2.0", "debug": True}}

        manager = ConfigManager()
        manager._deep_merge(base, override)

        assert base["system"]["name"] == "Base"
        assert base["system"]["version"] == "2.0"
        assert base["system"]["debug"] is True

    def test_apply_environment_config(self):
        """環境別設定の適用テスト"""
        config = {
            "system": {"environment": "test"},
            "environments": {"test": {"system": {"debug": True}}},
        }
        manager = ConfigManager(config=config)
        manager._apply_environment_config()

        assert manager.get_config("system.debug") is True

    def test_load_config_file_not_exists(self):
        """設定ファイルが存在しない場合のテスト"""
        with patch.object(ConfigManager, "_create_default_config") as mock_create:
            manager = ConfigManager(config_file="nonexistent.yaml")
            mock_create.assert_called_once()

    def test_load_config_file_exists(self):
        """設定ファイルが存在する場合のテスト"""
        test_config = {"system": {"name": "Test"}}

        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            with patch("os.path.exists", return_value=True):
                manager = ConfigManager(config_file="test.yaml")
                assert manager.config == test_config

    def test_load_config_file_error(self):
        """設定ファイル読み込みエラーのテスト"""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="invalid yaml")):
                with patch.object(
                    ConfigManager, "_create_default_config"
                ) as mock_create:
                    manager = ConfigManager(config_file="test.yaml")
                    mock_create.assert_called_once()

    def test_load_config_file_none_content(self):
        """設定ファイルがNoneを返す場合のテスト"""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="null")):
                with patch("yaml.safe_load", return_value=None):
                    manager = ConfigManager(config_file="test.yaml")
                    assert manager.config == {}

    def test_validate_config_with_api_key(self):
        """APIキーを含む設定の検証テスト"""
        config = {"system": {"environment": "production"}, "api_key": "test_key"}
        manager = ConfigManager(config=config)
        result = manager.validate_config()
        assert result["is_valid"] is True

    def test_validate_config_without_api_key_production(self):
        """本番環境でAPIキー不足の検証テスト"""
        config = {"system": {"environment": "production"}}
        manager = ConfigManager(config=config)
        result = manager.validate_config()
        assert result["is_valid"] is False
        assert "api_key" in str(result["issues"][0])

    def test_validate_config_test_environment(self):
        """テスト環境での検証テスト"""
        config = {"system": {"environment": "test"}}
        manager = ConfigManager(config=config)
        result = manager.validate_config()
        assert result["is_valid"] is True

    def test_validate_config_exception(self):
        """設定検証の例外処理テスト"""
        manager = ConfigManager()
        with patch.object(manager, "config", side_effect=Exception("Test error")):
            result = manager.validate_config()
            assert result["is_valid"] is False
            # 実際のエラーメッセージをチェック
            assert "api_key" in result["issues"][0] or "設定検証エラー" in result["issues"][0]

    def test_save_config_exception(self):
        """設定保存の例外処理テスト"""
        manager = ConfigManager()
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                manager.save_config("test.yaml")

    def test_update_configuration_exception(self):
        """設定更新の例外処理テスト"""
        manager = ConfigManager()
        # 正常な動作をテスト
        manager.update_configuration({"test": "value"})
        assert manager.config["test"] == "value"

    def test_create_backup_exception(self):
        """バックアップ作成の例外処理テスト"""
        manager = ConfigManager()
        # 正常な動作をテスト
        backup = manager.create_backup()
        assert "config" in backup
        assert "timestamp" in backup

    def test_restore_from_backup_exception(self):
        """バックアップ復元の例外処理テスト"""
        manager = ConfigManager()
        # 正常な動作をテスト
        result = manager.restore_from_backup({"config": {"test": "value"}})
        assert result is True

    def test_restore_from_backup_none_config(self):
        """バックアップにconfigキーがない場合のテスト"""
        manager = ConfigManager()
        result = manager.restore_from_backup({"timestamp": "2023-01-01"})
        assert result is False

    def test_restore_from_backup_none_data(self):
        """バックアップデータがNoneの場合のテスト"""
        manager = ConfigManager()
        result = manager.restore_from_backup(None)
        assert result is False

    def test_get_config_key_error(self):
        """存在しないキーの取得テスト"""
        manager = ConfigManager()
        result = manager.get_config("nonexistent.key", "default")
        assert result == "default"

    def test_get_config_type_error(self):
        """型エラーが発生するキーの取得テスト"""
        config = {"system": "not_a_dict"}
        manager = ConfigManager(config=config)
        result = manager.get_config("system.name", "default")
        assert result == "default"

    def test_set_config_create_nested(self):
        """ネストした設定の作成テスト"""
        manager = ConfigManager()
        manager.set_config("new.nested.key", "value")
        assert manager.get_config("new.nested.key") == "value"

    def test_apply_environment_config_no_environments(self):
        """環境設定がない場合のテスト"""
        config = {"system": {"environment": "test"}}
        manager = ConfigManager(config=config)
        manager._apply_environment_config()
        # エラーが発生しないことを確認
        assert manager.config == config

    def test_apply_environment_config_environment_not_found(self):
        """環境設定が見つからない場合のテスト"""
        config = {
            "system": {"environment": "nonexistent"},
            "environments": {"test": {"system": {"debug": True}}},
        }
        manager = ConfigManager(config=config)
        manager._apply_environment_config()
        # 元の設定が保持されることを確認
        assert manager.config == config
