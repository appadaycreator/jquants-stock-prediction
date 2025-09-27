#!/usr/bin/env python3
"""
統合エラーハンドリングシステム
統一されたエラーハンドリングとログ機能を提供
"""

import logging
import logging.handlers
import traceback
import re
import os
import sys
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from pathlib import Path
import warnings

# 警告を抑制
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class ErrorCategory(Enum):
    """エラーカテゴリの定義"""

    API_ERROR = "api_error"
    MODEL_ERROR = "model_error"
    FILE_ERROR = "file_error"
    DATA_PROCESSING_ERROR = "data_processing_error"
    VALIDATION_ERROR = "validation_error"
    CONFIG_ERROR = "config_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"


class LogLevel(Enum):
    """ログレベルの定義"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class UnifiedErrorHandler:
    """統合エラーハンドリングクラス"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初期化"""
        self.config = config or {}
        self.logger = self._setup_logger()
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_level": {},
        }

    def _setup_logger(self) -> logging.Logger:
        """ロガーの設定"""
        logger = logging.getLogger("unified_error_handler")
        logger.setLevel(logging.DEBUG)

        # 既存のハンドラーをクリア
        logger.handlers.clear()

        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # ファイルハンドラー
        file_handler = logging.FileHandler("unified_error.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d %(funcName)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def handle_error(
        self,
        error: Exception,
        category: ErrorCategory,
        context: Optional[Dict[str, Any]] = None,
        level: LogLevel = LogLevel.ERROR,
    ) -> None:
        """エラーの統合処理"""
        try:
            # エラー統計の更新
            self._update_error_stats(category, level)

            # コンテキスト情報の準備
            context_info = self._prepare_context(error, context)

            # ログ出力
            self._log_error(error, category, context_info, level)

            # エラー復旧の試行
            self._attempt_recovery(error, category, context_info)

        except Exception as e:
            # エラーハンドリング自体でエラーが発生した場合
            print(f"Critical error in error handler: {e}")
            sys.exit(1)

    def _update_error_stats(self, category: ErrorCategory, level: LogLevel) -> None:
        """エラー統計の更新"""
        self.error_stats["total_errors"] += 1

        # カテゴリ別統計
        if category.value not in self.error_stats["errors_by_category"]:
            self.error_stats["errors_by_category"][category.value] = 0
        self.error_stats["errors_by_category"][category.value] += 1

        # レベル別統計
        if level.value not in self.error_stats["errors_by_level"]:
            self.error_stats["errors_by_level"][level.value] = 0
        self.error_stats["errors_by_level"][level.value] += 1

    def _prepare_context(
        self, error: Exception, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """コンテキスト情報の準備"""
        context_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd(),
            },
        }

        if context:
            context_info.update(context)

        return context_info

    def _log_error(
        self,
        error: Exception,
        category: ErrorCategory,
        context_info: Dict[str, Any],
        level: LogLevel,
    ) -> None:
        """エラーのログ出力"""
        log_message = f"[{category.value}] {error.__class__.__name__}: {str(error)}"

        # コンテキスト情報を追加
        if context_info.get("function_name"):
            log_message += f" in {context_info["function_name"]}"

        # ログレベルに応じて出力
        if level == LogLevel.DEBUG:
            self.logger.debug(log_message, extra={"context": context_info})
        elif level == LogLevel.INFO:
            self.logger.info(log_message, extra={"context": context_info})
        elif level == LogLevel.WARNING:
            self.logger.warning(log_message, extra={"context": context_info})
        elif level == LogLevel.ERROR:
            self.logger.error(log_message, extra={"context": context_info})
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_message, extra={"context": context_info})

    def _attempt_recovery(
        self, error: Exception, category: ErrorCategory, context_info: Dict[str, Any]
    ) -> None:
        """エラー復旧の試行"""
        try:
            if category == ErrorCategory.API_ERROR:
                self._recover_api_error(error, context_info)
            elif category == ErrorCategory.FILE_ERROR:
                self._recover_file_error(error, context_info)
            elif category == ErrorCategory.DATA_PROCESSING_ERROR:
                self._recover_data_processing_error(error, context_info)
            else:
                self.logger.warning(
                    f"No specific recovery strategy for {category.value}"
                )

        except Exception as recovery_error:
            self.logger.error(f"Recovery attempt failed: {recovery_error}")

    def _recover_api_error(
        self, error: Exception, context_info: Dict[str, Any]
    ) -> None:
        """APIエラーの復旧"""
        self.logger.info("Attempting API error recovery...")
        # APIエラーの復旧ロジックを実装
        pass

    def _recover_file_error(
        self, error: Exception, context_info: Dict[str, Any]
    ) -> None:
        """ファイルエラーの復旧"""
        self.logger.info("Attempting file error recovery...")
        # ファイルエラーの復旧ロジックを実装
        pass

    def _recover_data_processing_error(
        self, error: Exception, context_info: Dict[str, Any]
    ) -> None:
        """データ処理エラーの復旧"""
        self.logger.info("Attempting data processing error recovery...")
        # データ処理エラーの復旧ロジックを実装
        pass

    def get_error_stats(self) -> Dict[str, Any]:
        """エラー統計の取得"""
        return self.error_stats.copy()

    def reset_error_stats(self) -> None:
        """エラー統計のリセット"""
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_level": {},
        }

    def log_error(
        self, error: Exception, message: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """エラーログの出力"""
        try:
            context_info = self._prepare_context(error, context)
            context_info["message"] = message

            self.logger.error(f"Error: {str(error)} | Context: {context_info}")

            # エラー統計の更新
            self._update_error_stats(ErrorCategory.ERROR, LogLevel.ERROR)

        except Exception as e:
            self.logger.critical(f"Failed to log error: {e}")

    def handle_file_error(
        self, error: Exception, file_path: str, operation: str
    ) -> None:
        """ファイルエラーの処理"""
        try:
            context = {
                "file_path": file_path,
                "operation": operation,
                "error_type": type(error).__name__,
            }

            self.handle_error(error, ErrorCategory.FILE_ERROR, context)

        except Exception as e:
            self.logger.critical(f"Failed to handle file error: {e}")

    def handle_data_error(
        self, error: Exception, operation: str, data_shape: tuple, column: str = None
    ) -> None:
        """データエラーの処理"""
        try:
            context = {
                "operation": operation,
                "data_shape": data_shape,
                "column": column,
                "error_type": type(error).__name__,
            }

            self.handle_error(error, ErrorCategory.DATA_PROCESSING_ERROR, context)

        except Exception as e:
            self.logger.critical(f"Failed to handle data error: {e}")


# グローバルエラーハンドラーインスタンス
_global_error_handler = None


def get_unified_error_handler(
    config: Optional[Dict[str, Any]] = None,
) -> UnifiedErrorHandler:
    """統合エラーハンドラーの取得"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = UnifiedErrorHandler(config)
    return _global_error_handler


def handle_error(
    error: Exception,
    category: ErrorCategory,
    context: Optional[Dict[str, Any]] = None,
    level: LogLevel = LogLevel.ERROR,
) -> None:
    """エラーハンドリングの簡易関数"""
    handler = get_unified_error_handler()
    handler.handle_error(error, category, context, level)


# デコレータ用のエラーハンドリング
def error_handler(category: ErrorCategory, level: LogLevel = LogLevel.ERROR):
    """エラーハンドリングデコレータ"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function_name": func.__name__,
                    "args": str(args)[:100],  # 最初の100文字のみ
                    "kwargs": str(kwargs)[:100],
                }
                handle_error(e, category, context, level)
                raise

        return wrapper

    return decorator


# カスタム例外クラス
class DataProcessingError(Exception):
    """データ処理エラー"""

    pass


class ModelError(Exception):
    """モデルエラー"""

    pass


class ConfigError(Exception):
    """設定エラー"""

    pass


class APIError(Exception):
    """APIエラー"""

    pass


class FileError(Exception):
    """ファイルエラー"""

    pass


class ValidationError(Exception):
    """検証エラー"""

    pass


class NetworkError(Exception):
    """ネットワークエラー"""

    pass


class AuthenticationError(Exception):
    """認証エラー"""

    pass
