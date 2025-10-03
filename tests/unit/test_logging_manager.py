#!/usr/bin/env python3
"""
LoggingManagerのユニットテスト
"""

import pytest
import tempfile
import os
import sys
import logging
from unittest.mock import Mock, patch, MagicMock
from core.logging_manager import LoggingManager, LogLevel, LogCategory


class TestLoggingManager:
    """LoggingManagerのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "logging": {
                "level": "INFO",
                "console_output": True,
                "file": os.path.join(self.temp_dir, "test.log"),
            },
            "security": {
                "mask_sensitive_data": True,
                "sensitive_keys": ["password", "token", "key"],
            },
        }
        self.logging_manager = LoggingManager("TestModule", self.config)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """初期化テスト"""
        assert self.logging_manager.module_name == "TestModule"
        assert self.logging_manager.config == self.config
        assert self.logging_manager.logger is not None
        assert len(self.logging_manager.sensitive_keys) > 0

    def test_log_info(self):
        """情報ログのテスト"""
        with patch.object(self.logging_manager.logger, "info") as mock_info:
            self.logging_manager.log_info("テストメッセージ")
            mock_info.assert_called()

    def test_log_warning(self):
        """警告ログのテスト"""
        with patch.object(self.logging_manager.logger, "warning") as mock_warning:
            self.logging_manager.log_warning("警告メッセージ")
            mock_warning.assert_called()

    def test_log_debug(self):
        """デバッグログのテスト"""
        with patch.object(self.logging_manager.logger, "debug") as mock_debug:
            self.logging_manager.log_debug("デバッグメッセージ")
            mock_debug.assert_called()

    def test_log_error(self):
        """エラーログのテスト"""
        with patch.object(self.logging_manager.logger, "error") as mock_error:
            error = ValueError("テストエラー")
            self.logging_manager.log_error(error, "テストコンテキスト")
            mock_error.assert_called()

    def test_sanitize_message(self):
        """メッセージのサニタイズテスト"""
        message = "password=secret123 token=abc456"
        sanitized = self.logging_manager._sanitize_message(message)
        assert "password=***" in sanitized
        assert "token=***" in sanitized
        assert "secret123" not in sanitized
        assert "abc456" not in sanitized

    def test_mask_sensitive_data(self):
        """機密データのマスキングテスト"""
        data = {
            "username": "user123",
            "password": "secret123",
            "token": "abc456",
            "normal_data": "value",
        }
        masked = self.logging_manager._mask_sensitive_data(data)
        assert masked["username"] == "user123"
        assert masked["password"] == "***"
        assert masked["token"] == "***"
        assert masked["normal_data"] == "value"

    def test_log_with_category(self):
        """カテゴリ付きログのテスト"""
        with patch.object(self.logging_manager.logger, "info") as mock_info:
            self.logging_manager.log_info("APIログ", LogCategory.API)
            mock_info.assert_called()
            # カテゴリが含まれていることを確認
            call_args = mock_info.call_args[0][0]
            assert "[API]" in call_args

    def test_log_with_kwargs(self):
        """追加情報付きログのテスト"""
        with patch.object(self.logging_manager.logger, "info") as mock_info:
            self.logging_manager.log_info("テスト", additional_info="value")
            mock_info.assert_called()

    def test_set_log_level(self):
        """ログレベルの設定テスト"""
        with patch.object(self.logging_manager.logger, "setLevel") as mock_set_level:
            self.logging_manager.set_log_level(LogLevel.DEBUG)
            mock_set_level.assert_called()

    def test_get_logger(self):
        """ロガーの取得テスト"""
        logger = self.logging_manager.get_logger()
        assert isinstance(logger, logging.Logger)

    def test_add_handler(self):
        """ハンドラーの追加テスト"""
        handler = logging.StreamHandler()
        with patch.object(self.logging_manager.logger, "addHandler") as mock_add:
            self.logging_manager.add_handler(handler)
            mock_add.assert_called_with(handler)

    def test_remove_handler(self):
        """ハンドラーの削除テスト"""
        handler = logging.StreamHandler()
        with patch.object(self.logging_manager.logger, "removeHandler") as mock_remove:
            self.logging_manager.remove_handler(handler)
            mock_remove.assert_called_with(handler)

    def test_clear_handlers(self):
        """ハンドラーのクリアテスト"""
        with patch.object(self.logging_manager.logger, "handlers") as mock_handlers:
            mock_handlers.clear = Mock()
            self.logging_manager.clear_handlers()
            mock_handlers.clear.assert_called()

    def test_log_error_with_traceback(self):
        """トレースバック付きエラーログのテスト"""
        with patch.object(self.logging_manager.logger, "error") as mock_error:
            error = ValueError("テストエラー")
            self.logging_manager.log_error(
                error, "テストコンテキスト", include_traceback=True
            )
            # エラーメッセージとトレースバックの両方が呼ばれることを確認
            assert mock_error.call_count >= 2

    def test_log_error_without_traceback(self):
        """トレースバックなしエラーログのテスト"""
        with patch.object(self.logging_manager.logger, "error") as mock_error:
            error = ValueError("テストエラー")
            self.logging_manager.log_error(
                error, "テストコンテキスト", include_traceback=False
            )
            mock_error.assert_called()

    def test_log_error_with_additional_info(self):
        """追加情報付きエラーログのテスト"""
        with patch.object(self.logging_manager.logger, "error") as mock_error:
            error = ValueError("テストエラー")
            additional_info = {"key": "value", "password": "secret"}
            self.logging_manager.log_error(
                error, "テストコンテキスト", additional_info=additional_info
            )
            mock_error.assert_called()

    def test_log_error_different_levels(self):
        """異なるレベルのエラーログのテスト"""
        error = ValueError("テストエラー")

        with patch.object(self.logging_manager.logger, "debug") as mock_debug:
            self.logging_manager.log_error(error, "テスト", level=LogLevel.DEBUG)
            mock_debug.assert_called()

        with patch.object(self.logging_manager.logger, "critical") as mock_critical:
            self.logging_manager.log_error(error, "テスト", level=LogLevel.CRITICAL)
            mock_critical.assert_called()

    def test_sensitive_keys_configuration(self):
        """機密キーの設定テスト"""
        custom_config = {"security": {"sensitive_keys": ["custom_key", "secret"]}}
        manager = LoggingManager("Test", custom_config)
        assert "custom_key" in manager.sensitive_keys
        assert "secret" in manager.sensitive_keys

    def test_nested_dict_masking(self):
        """ネストした辞書のマスキングテスト"""
        data = {
            "user": {
                "name": "test",
                "password": "secret",
                "nested": {"token": "abc123"},
            }
        }
        masked = self.logging_manager._mask_sensitive_data(data)
        assert masked["user"]["name"] == "test"
        assert masked["user"]["password"] == "***"
        assert masked["user"]["nested"]["token"] == "***"

    def test_log_file_creation(self):
        """ログファイルの作成テスト"""
        # 新しいログファイルパスでテスト
        log_file = os.path.join(self.temp_dir, "new_test.log")
        config = {"logging": {"level": "INFO", "file": log_file}}
        manager = LoggingManager("Test", config)
        assert os.path.exists(log_file)

    def test_error_log_file_creation(self):
        """エラーログファイルの作成テスト"""
        error_log_file = os.path.join(self.temp_dir, "test_errors.log")
        config = {
            "logging": {
                "level": "INFO",
                "file": os.path.join(self.temp_dir, "test.log"),
            }
        }
        manager = LoggingManager("Test", config)
        # エラーログファイルは固定名で作成される
        assert os.path.exists("errors.log")

    def test_console_output_disabled(self):
        """コンソール出力無効化のテスト"""
        config = {
            "logging": {
                "console_output": False,
                "file": os.path.join(self.temp_dir, "test.log"),
            }
        }
        manager = LoggingManager("Test", config)
        # コンソールハンドラー（stdout/stderr）が追加されていないことを確認
        console_handlers = [
            h
            for h in manager.logger.handlers
            if isinstance(h, logging.StreamHandler)
            and h.stream in [sys.stdout, sys.stderr]
        ]
        assert len(console_handlers) == 0
