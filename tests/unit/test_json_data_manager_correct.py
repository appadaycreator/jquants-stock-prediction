#!/usr/bin/env python3
"""
json_data_manager.pyの正しいテスト
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from core.json_data_manager import JSONDataManager


class TestJSONDataManagerCorrect:
    """JSONデータ管理の正しいテストクラス"""

    @pytest.fixture
    def temp_data_dir(self):
        """一時データディレクトリのフィクスチャ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def json_manager(self, temp_data_dir):
        """JSONDataManagerのフィクスチャ"""
        return JSONDataManager(data_dir=temp_data_dir)

    def test_initialization(self, temp_data_dir):
        """初期化テスト"""
        manager = JSONDataManager(data_dir=temp_data_dir)
        
        assert manager.data_dir == Path(temp_data_dir)
        assert manager.logger is not None
        assert manager.stock_data_file == manager.data_dir / "stock_data.json"
        assert manager.metadata_file == manager.data_dir / "metadata.json"
        assert manager.diff_log_file == manager.data_dir / "diff_log.json"

    def test_data_dir_creation(self, temp_data_dir):
        """データディレクトリの作成テスト"""
        manager = JSONDataManager(data_dir=temp_data_dir)
        
        assert manager.data_dir.exists()
        assert manager.data_dir.is_dir()

    def test_file_paths(self, json_manager):
        """ファイルパスのテスト"""
        assert json_manager.stock_data_file.name == "stock_data.json"
        assert json_manager.metadata_file.name == "metadata.json"
        assert json_manager.diff_log_file.name == "diff_log.json"

    def test_logger_initialization(self, json_manager):
        """ロガーの初期化テスト"""
        assert json_manager.logger is not None
        assert hasattr(json_manager.logger, 'info')
        assert hasattr(json_manager.logger, 'error')
        assert hasattr(json_manager.logger, 'warning')

    def test_data_dir_path_type(self, json_manager):
        """データディレクトリのパス型テスト"""
        assert isinstance(json_manager.data_dir, Path)
        assert str(json_manager.data_dir) == json_manager.data_dir.as_posix()

    def test_file_path_types(self, json_manager):
        """ファイルパスの型テスト"""
        assert isinstance(json_manager.stock_data_file, Path)
        assert isinstance(json_manager.metadata_file, Path)
        assert isinstance(json_manager.diff_log_file, Path)

    def test_file_path_relationships(self, json_manager):
        """ファイルパスの関係性テスト"""
        assert json_manager.stock_data_file.parent == json_manager.data_dir
        assert json_manager.metadata_file.parent == json_manager.data_dir
        assert json_manager.diff_log_file.parent == json_manager.data_dir

    def test_metadata_initialization(self, json_manager):
        """メタデータの初期化テスト"""
        # メタデータファイルが存在することを確認
        assert json_manager.metadata_file.exists()
        
        # メタデータの内容を確認
        with open(json_manager.metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        assert isinstance(metadata, dict)
        assert "created_at" in metadata
        assert "last_updated" in metadata

    def test_logger_with_custom_logger(self, temp_data_dir):
        """カスタムロガーでの初期化テスト"""
        import logging
        custom_logger = logging.getLogger("custom_test_logger")
        
        manager = JSONDataManager(data_dir=temp_data_dir, logger=custom_logger)
        
        assert manager.logger == custom_logger

    def test_data_dir_absolute_path(self, json_manager):
        """データディレクトリの絶対パステスト"""
        assert json_manager.data_dir.is_absolute() or json_manager.data_dir.resolve().is_absolute()
