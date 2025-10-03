#!/usr/bin/env python3
"""
differential_updater.pyの正しいテスト
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from core.differential_updater import DifferentialUpdater


class TestDifferentialUpdaterCorrect:
    """差分更新システムの正しいテストクラス"""

    @pytest.fixture
    def temp_data_dir(self):
        """一時データディレクトリのフィクスチャ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def updater(self, temp_data_dir):
        """DifferentialUpdaterのフィクスチャ"""
        return DifferentialUpdater(data_dir=temp_data_dir)

    def test_initialization(self, temp_data_dir):
        """初期化テスト"""
        updater = DifferentialUpdater(data_dir=temp_data_dir)
        
        assert updater.data_dir == Path(temp_data_dir)
        assert updater.logger is not None
        assert updater.json_manager is not None
        assert updater.update_config is not None

    def test_update_config_defaults(self, updater):
        """更新設定のデフォルト値テスト"""
        config = updater.update_config
        
        assert config["max_retry_attempts"] == 3
        assert config["retry_delay_seconds"] == 5
        assert config["batch_size"] == 100
        assert config["enable_validation"] is True
        assert config["enable_compression"] is False

    def test_data_dir_creation(self, temp_data_dir):
        """データディレクトリの作成テスト"""
        updater = DifferentialUpdater(data_dir=temp_data_dir)
        
        assert updater.data_dir.exists()
        assert updater.data_dir.is_dir()

    def test_json_manager_initialization(self, updater):
        """JSONDataManagerの初期化テスト"""
        assert updater.json_manager is not None
        assert updater.json_manager.data_dir == updater.data_dir

    def test_logger_initialization(self, updater):
        """ロガーの初期化テスト"""
        assert updater.logger is not None
        assert hasattr(updater.logger, 'info')
        assert hasattr(updater.logger, 'error')
        assert hasattr(updater.logger, 'warning')

    def test_update_config_modification(self, updater):
        """更新設定の変更テスト"""
        # 設定を変更
        updater.update_config["max_retry_attempts"] = 5
        updater.update_config["batch_size"] = 50
        
        assert updater.update_config["max_retry_attempts"] == 5
        assert updater.update_config["batch_size"] == 50

    def test_data_dir_path_type(self, updater):
        """データディレクトリのパス型テスト"""
        assert isinstance(updater.data_dir, Path)
        assert str(updater.data_dir) == updater.data_dir.as_posix()

    def test_update_config_type(self, updater):
        """更新設定の型テスト"""
        assert isinstance(updater.update_config, dict)
        assert all(isinstance(v, (int, bool)) for v in updater.update_config.values())

    def test_json_manager_data_dir_match(self, updater):
        """JSONDataManagerのデータディレクトリが一致することをテスト"""
        assert updater.json_manager.data_dir == updater.data_dir
