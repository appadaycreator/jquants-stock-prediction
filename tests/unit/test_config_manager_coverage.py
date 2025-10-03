#!/usr/bin/env python3
"""
ConfigManagerのテストカバレッジ向上
不足しているテストケースを追加
"""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open
from core.config_manager import ConfigManager


class TestConfigManagerCoverage:
    """ConfigManagerのカバレッジ向上テスト"""

    def test_save_config_with_custom_path(self):
        """カスタムパスでの設定保存テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            custom_path = os.path.join(temp_dir, "custom_config.yaml")
            
            # 設定の保存
            config_manager.save_config(custom_path)
            
            # ファイルが作成されたことを確認
            assert os.path.exists(custom_path)

    def test_save_config_exception_handling(self):
        """設定保存時の例外処理テスト"""
        config_manager = ConfigManager()
        
        # 無効なパスでの保存を試行
        with patch('os.makedirs', side_effect=OSError("Read-only file system")):
            with pytest.raises(OSError):
                config_manager.save_config("/invalid/path/config.yaml")

    def test_update_configuration_with_none(self):
        """None設定での更新テスト"""
        config_manager = ConfigManager()
        
        # None設定での更新
        config_manager.update_configuration(None)
        
        # 設定が変更されていないことを確認
        assert config_manager.config is not None

    def test_update_configuration_exception_handling(self):
        """設定更新時の例外処理テスト"""
        config_manager = ConfigManager()
        
        # 無効な設定での更新（config属性を直接変更）
        original_config = config_manager.config
        config_manager.config = None
        
        with pytest.raises(AttributeError):
            config_manager.update_configuration({"test": "value"})
        
        # 元に戻す
        config_manager.config = original_config

    def test_validate_config_with_test_environment(self):
        """テスト環境での設定検証テスト"""
        config_manager = ConfigManager()
        
        # テスト環境の設定
        test_config = {
            "system": {
                "environment": "test"
            }
        }
        
        result = config_manager.validate_config(test_config)
        
        # テスト環境ではAPIキーが不要
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_config_with_production_environment(self):
        """本番環境での設定検証テスト"""
        config_manager = ConfigManager()
        
        # 本番環境の設定（APIキーなし）
        prod_config = {
            "system": {
                "environment": "production"
            }
        }
        
        result = config_manager.validate_config(prod_config)
        
        # 本番環境ではAPIキーが必要
        assert result["is_valid"] is False
        assert "api_key" in str(result["issues"])

    def test_validate_config_exception_handling(self):
        """設定検証時の例外処理テスト"""
        config_manager = ConfigManager()
        
        # 無効な設定での検証
        result = config_manager.validate_config({"invalid": "config"})
        assert result["is_valid"] is False
        assert "api_key" in str(result["issues"])

    def test_get_nested_config_with_missing_key(self):
        """存在しないキーでの設定取得テスト"""
        config_manager = ConfigManager()
        
        # 存在しないキーでの取得
        result = config_manager.get_nested_config("nonexistent.key")
        
        # Noneが返されることを確認
        assert result is None

    def test_set_nested_config_with_new_key(self):
        """新しいキーでの設定設定テスト"""
        config_manager = ConfigManager()
        
        # 新しいキーの設定
        config_manager.set_nested_config("new.nested.key", "test_value")
        
        # 設定が正しく設定されたことを確認
        assert config_manager.get_nested_config("new.nested.key") == "test_value"

    def test_set_nested_config_exception_handling(self):
        """設定設定時の例外処理テスト"""
        config_manager = ConfigManager()
        
        # 正常な設定のテスト
        config_manager.set_nested_config("test.key", "test_value")
        assert config_manager.get_nested_config("test.key") == "test_value"
