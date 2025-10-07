#!/usr/bin/env python3
"""
ErrorHandlerのユニットテスト
"""

from unittest.mock import Mock, patch
from core.error_handler import ErrorHandler, ErrorCategory


class TestErrorHandler:
    """ErrorHandlerのテストクラス"""

    def test_init(self):
        """初期化のテスト"""
        handler = ErrorHandler()
        assert handler.error_count == 0
        assert handler.error_stats == {category.value: 0 for category in ErrorCategory}

    def test_init_with_logger(self):
        """ロガー付き初期化のテスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)
        assert handler.logger == mock_logger

    def test_init_with_config(self):
        """設定付き初期化のテスト"""
        config = {"error_handling": {"auto_recovery": True}}
        handler = ErrorHandler(config=config)
        assert handler.config == config

    def test_log_error(self):
        """エラーログのテスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ValueError("Test error")
        handler.log_error(error, "Test context", ErrorCategory.API_ERROR)

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.API_ERROR.value] == 1
        mock_logger.log_error.assert_called_once()

    def test_log_error_with_additional_info(self):
        """追加情報付きエラーログのテスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ValueError("Test error")
        additional_info = {"key": "value"}
        handler.log_error(
            error, "Test context", ErrorCategory.MODEL_ERROR, additional_info
        )

        assert handler.error_count == 1
        mock_logger.log_error.assert_called_once()

    def test_handle_model_error(self):
        """モデルエラーの処理テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ValueError("Model error")
        handler.handle_model_error(error, "test_model", "training")

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.MODEL_ERROR.value] == 1

    def test_handle_data_processing_error(self):
        """データ処理エラーの処理テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ValueError("Data processing error")
        data_info = {"rows": 100}
        handler.handle_data_processing_error(error, "processing", data_info)

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.DATA_PROCESSING_ERROR.value] == 1

    def test_handle_api_error(self):
        """APIエラーの処理テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ValueError("API error")
        handler.handle_api_error(error, "API call")

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.API_ERROR.value] == 1

    def test_handle_file_error(self):
        """ファイルエラーの処理テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = FileNotFoundError("File not found")
        handler.handle_file_error(error, "/path/to/file", "read")

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.FILE_ERROR.value] == 1

    def test_handle_validation_error(self):
        """検証エラーの処理テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ValueError("Validation error")
        handler.handle_validation_error(error)

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.VALIDATION_ERROR.value] == 1

    def test_handle_network_error(self):
        """ネットワークエラーの処理テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ConnectionError("Network error")
        handler.handle_network_error(error, "API call")

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.NETWORK_ERROR.value] == 1

    def test_handle_authentication_error(self):
        """認証エラーの処理テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        error = ValueError("Auth error")
        handler.handle_authentication_error(error, "login")

        assert handler.error_count == 1
        assert handler.error_stats[ErrorCategory.AUTHENTICATION_ERROR.value] == 1

    def test_get_error_statistics(self):
        """エラー統計の取得テスト"""
        handler = ErrorHandler()
        handler.error_count = 5
        handler.error_stats[ErrorCategory.API_ERROR.value] = 3
        handler.error_stats[ErrorCategory.MODEL_ERROR.value] = 2

        stats = handler.get_error_statistics()

        assert stats["total_errors"] == 5
        assert stats["error_by_category"][ErrorCategory.API_ERROR.value] == 3
        assert stats["errors_by_category"][ErrorCategory.MODEL_ERROR.value] == 2
        assert "timestamp" in stats

    def test_reset_error_count(self):
        """エラーカウントのリセットテスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)

        # エラーを追加
        handler.error_count = 5
        handler.error_stats[ErrorCategory.API_ERROR.value] = 3

        # リセット
        handler.reset_error_count()

        assert handler.error_count == 0
        assert handler.error_stats[ErrorCategory.API_ERROR.value] == 0
        mock_logger.log_info.assert_called_with("エラーカウントをリセットしました")

    def test_execute_error_recovery_workflow(self):
        """エラー復旧ワークフローの実行テスト"""
        mock_logger = Mock()
        handler = ErrorHandler(logger=mock_logger)
        handler.error_count = 3

        result = handler.execute_error_recovery_workflow()

        assert result["status"] == "success"
        assert result["recovered_errors"] == 3
        assert "timestamp" in result
        mock_logger.log_info.assert_called_with("エラー復旧ワークフローを実行しました")

    def test_attempt_error_recovery(self):
        """エラー復旧の試行テスト"""
        handler = ErrorHandler()
        error = ValueError("Test error")

        result = handler.attempt_error_recovery(error)
        assert result is True

    def test_attempt_error_recovery_failure(self):
        """エラー復旧失敗のテスト"""
        handler = ErrorHandler()

        # 復旧処理で例外を発生させる
        with patch.object(
            handler, "_attempt_error_recovery", side_effect=Exception("Recovery failed")
        ):
            result = handler.attempt_error_recovery(ValueError("Test error"))
            assert result is False

    def test_recovery_attempts_tracking(self):
        """復旧試行回数の追跡テスト"""
        config = {"error_handling": {"auto_recovery": True, "max_recovery_attempts": 2}}
        handler = ErrorHandler(config=config)

        error = ValueError("Test error")

        # 1回目の復旧試行
        handler._attempt_error_recovery(error, ErrorCategory.API_ERROR)
        assert handler.recovery_attempts["recovery_attempts_api_error"] == 1

        # 2回目の復旧試行
        handler._attempt_error_recovery(error, ErrorCategory.API_ERROR)
        assert handler.recovery_attempts["recovery_attempts_api_error"] == 2

        # 3回目の復旧試行（上限に達する）
        handler._attempt_error_recovery(error, ErrorCategory.API_ERROR)
        assert (
            handler.recovery_attempts["recovery_attempts_api_error"] == 2
        )  # 上限で止まる

    def test_recovery_disabled(self):
        """復旧無効時のテスト"""
        config = {"error_handling": {"auto_recovery": False}}
        mock_logger = Mock()
        handler = ErrorHandler(config=config, logger=mock_logger)

        error = ValueError("Test error")
        handler._attempt_error_recovery(error, ErrorCategory.API_ERROR)

        # 自動復旧が無効化されている場合、復旧処理は実行されない
        mock_logger.log_info.assert_called_with("自動復旧が無効化されています")

    def test_recovery_max_attempts_reached(self):
        """復旧試行上限到達のテスト"""
        config = {"error_handling": {"auto_recovery": True, "max_recovery_attempts": 1}}
        mock_logger = Mock()
        handler = ErrorHandler(config=config, logger=mock_logger)

        error = ValueError("Test error")

        # 1回目の復旧試行
        handler._attempt_error_recovery(error, ErrorCategory.API_ERROR)

        # 2回目の復旧試行（上限に達する）
        handler._attempt_error_recovery(error, ErrorCategory.API_ERROR)

        mock_logger.log_warning.assert_called_with(
            "復旧試行の上限に達しました: api_error"
        )
