#!/usr/bin/env python3
"""
統合エラーハンドリング・ログシステム
統一されたエラーハンドリングとログ機能を提供する完全統合システム
"""

import logging
import logging.handlers
import traceback
import re
import os
import sys
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


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


class LogCategory(Enum):
    """ログカテゴリの定義"""

    API = "API"
    DATA_PROCESSING = "DATA_PROCESSING"
    MODEL_TRAINING = "MODEL_TRAINING"
    FILE_OPERATION = "FILE_OPERATION"
    VALIDATION = "VALIDATION"
    PERFORMANCE = "PERFORMANCE"
    ERROR = "ERROR"
    SECURITY = "SECURITY"


class UnifiedErrorLoggingSystem:
    """統合エラーハンドリング・ログシステム"""

    def __init__(self, module_name: str, config: Dict[str, Any] = None):
        """初期化"""
        self.module_name = module_name
        self.config = config or {}
        self.error_count = 0
        self.sensitive_keys = self.config.get("security", {}).get(
            "sensitive_keys", ["password", "token", "key", "secret", "auth", "email"]
        )

        # ログ設定の初期化
        self._setup_logging()

        # エラー統計
        self.error_stats = {category.value: 0 for category in ErrorCategory}

    def _setup_logging(self):
        """ログ設定の初期化"""
        # ログ設定の取得
        logging_config = self.config.get("logging", {})
        log_level = getattr(
            logging, logging_config.get("level", "INFO").upper(), logging.INFO
        )

        # ロガーの設定
        self.logger = logging.getLogger(f"UnifiedSystem.{self.module_name}")
        self.logger.setLevel(log_level)

        # 既存のハンドラーをクリア
        self.logger.handlers.clear()

        # フォーマッターの設定
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # ファイルハンドラー（詳細ログ）
        log_file = logging_config.get("file", "jquants.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)

        # エラーファイルハンドラー
        error_handler = logging.FileHandler("errors.log", encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)

        # ローテーティングハンドラー
        max_size = logging_config.get("max_size", "10MB")
        max_bytes = self._parse_size(max_size)
        backup_count = logging_config.get("backup_count", 5)

        rotating_handler = logging.handlers.RotatingFileHandler(
            "application.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        rotating_handler.setLevel(logging.DEBUG)
        rotating_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(rotating_handler)

    def _parse_size(self, size_str: str) -> int:
        """サイズ文字列をバイト数に変換"""
        size_str = size_str.upper()
        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)

    def _sanitize_message(self, message: str) -> str:
        """機密情報をマスキング"""
        if not message:
            return message

        sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'auth["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'email["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        ]

        sanitized = message
        for pattern in sensitive_patterns:
            sanitized = re.sub(
                pattern, r"\1***MASKED***", sanitized, flags=re.IGNORECASE
            )
        return sanitized

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """機密データをマスキング"""
        if not data:
            return data

        masked_data = {}
        for key, value in data.items():
            if any(
                sensitive_key in key.lower() for sensitive_key in self.sensitive_keys
            ):
                masked_data[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
            else:
                masked_data[key] = value

        return masked_data

    def log_error(
        self,
        error: Exception,
        context: str = "",
        category: ErrorCategory = ErrorCategory.ERROR,
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
    ):
        """統合エラーログ出力"""
        self.error_count += 1
        self.error_stats[category.value] += 1

        # 機密情報をマスキング
        sanitized_context = self._sanitize_message(context)
        sanitized_error_msg = self._sanitize_message(str(error))

        # 追加情報のマスキング
        masked_info = None
        if additional_info:
            masked_info = self._mask_sensitive_data(additional_info)

        # エラーログの出力
        self.logger.error(
            f"❌ エラー #{self.error_count} [{category.value}]: {sanitized_context}"
        )
        self.logger.error(f"エラー詳細: {sanitized_error_msg}")

        if masked_info:
            self.logger.error(f"追加情報: {masked_info}")

        if include_traceback:
            traceback_str = self._sanitize_message(
                "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
            )
            self.logger.error(f"トレースバック: {traceback_str}")

    def handle_api_error(
        self,
        error: Exception,
        api_name: str,
        url: str,
        status_code: int = None,
        context: Dict[str, Any] = None,
    ):
        """APIエラーの処理"""
        error_context = f"{api_name} API エラー"
        if status_code:
            error_context += f" (HTTP {status_code})"

        additional_info = {
            "api_name": api_name,
            "url": url,
            "status_code": status_code,
            "module": self.module_name,
        }

        if context:
            additional_info.update(context)

        self.log_error(error, error_context, ErrorCategory.API_ERROR, additional_info)

    def handle_model_error(
        self,
        error: Exception,
        model_name: str,
        operation: str,
        context: Dict[str, Any] = None,
    ):
        """モデル関連エラーの処理"""
        error_context = f"モデルエラー ({model_name}) - {operation}"
        additional_info = {
            "model_name": model_name,
            "operation": operation,
            "module": self.module_name,
        }

        if context:
            additional_info.update(context)

        self.log_error(error, error_context, ErrorCategory.MODEL_ERROR, additional_info)

    def handle_file_error(
        self,
        error: Exception,
        file_path: str,
        operation: str,
        context: Dict[str, Any] = None,
    ):
        """ファイルエラーの処理"""
        error_context = f"ファイルエラー - {operation}"

        additional_info = {
            "file_path": file_path,
            "operation": operation,
            "module": self.module_name,
        }

        if context:
            additional_info.update(context)

        self.log_error(error, error_context, ErrorCategory.FILE_ERROR, additional_info)

    def handle_data_error(
        self,
        error: Exception,
        data_info: Dict[str, Any] = None,
        operation: str = "データ処理",
        context: Dict[str, Any] = None,
    ):
        """データ処理エラーの処理"""
        error_context = f"データエラー - {operation}"

        additional_info = {
            "operation": operation,
            "module": self.module_name,
        }

        if data_info:
            additional_info.update(data_info)

        if context:
            additional_info.update(context)

        self.log_error(
            error, error_context, ErrorCategory.DATA_PROCESSING_ERROR, additional_info
        )

    def log_operation_start(
        self, operation: str, category: LogCategory = LogCategory.API, **kwargs
    ):
        """操作開始ログ"""
        self.logger.info(f"🚀 {operation} を開始 [{category.value}]")
        if kwargs:
            self.logger.debug(f"操作パラメータ: {kwargs}")

    def log_operation_end(
        self,
        operation: str,
        success: bool = True,
        category: LogCategory = LogCategory.API,
        **kwargs,
    ):
        """操作終了ログ"""
        if success:
            self.logger.info(f"✅ {operation} が正常に完了 [{category.value}]")
        else:
            self.logger.error(f"❌ {operation} が失敗 [{category.value}]")

        if kwargs:
            self.logger.debug(f"操作結果: {kwargs}")

    def log_data_info(
        self,
        data_name: str,
        shape: tuple = None,
        dtype: str = None,
        category: LogCategory = LogCategory.DATA_PROCESSING,
        **kwargs,
    ):
        """データ情報ログ"""
        info_parts = [f"📊 {data_name}"]
        if shape:
            info_parts.append(f"形状: {shape}")
        if dtype:
            info_parts.append(f"型: {dtype}")

        self.logger.info(" | ".join(info_parts))

        if kwargs:
            self.logger.debug(f"データ詳細: {kwargs}")

    def log_performance(
        self,
        operation: str,
        duration: float,
        category: LogCategory = LogCategory.PERFORMANCE,
        **kwargs,
    ):
        """パフォーマンスログ"""
        self.logger.info(f"⏱️ {operation} 実行時間: {duration:.2f}秒 [{category.value}]")
        if kwargs:
            self.logger.debug(f"パフォーマンス詳細: {kwargs}")

    def log_warning_with_context(
        self,
        message: str,
        context: Dict[str, Any] = None,
        category: LogCategory = LogCategory.ERROR,
    ):
        """コンテキスト付き警告ログ"""
        self.logger.warning(f"⚠️ {message} [{category.value}]")
        if context:
            self.logger.debug(f"警告コンテキスト: {context}")

    def log_security_event(self, event: str, context: Dict[str, Any] = None):
        """セキュリティイベントログ"""
        self.logger.warning(f"🔒 セキュリティイベント: {event}")
        if context:
            masked_context = self._mask_sensitive_data(context)
            self.logger.debug(f"セキュリティコンテキスト: {masked_context}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計の取得"""
        return {
            "total_errors": self.error_count,
            "error_categories": self.error_stats,
            "module": self.module_name,
            "timestamp": datetime.now().isoformat(),
        }

    def get_logger(self) -> logging.Logger:
        """ロガーインスタンスを取得"""
        return self.logger


# グローバルエラーハンドラーインスタンスの管理
_error_handlers = {}


def get_unified_error_logging_system(
    module_name: str, config: Dict[str, Any] = None
) -> UnifiedErrorLoggingSystem:
    """統合エラーハンドリング・ログシステムを取得"""
    if module_name not in _error_handlers:
        _error_handlers[module_name] = UnifiedErrorLoggingSystem(module_name, config)
    return _error_handlers[module_name]


def reset_error_handlers():
    """エラーハンドラーをリセット"""
    _error_handlers.clear()


def get_global_error_statistics() -> Dict[str, Any]:
    """グローバルエラー統計を取得"""
    stats = {}
    for module_name, handler in _error_handlers.items():
        stats[module_name] = handler.get_error_statistics()
    return stats


def configure_global_logging(config: Dict[str, Any] = None):
    """グローバルログ設定を適用"""
    if config is None:
        config = {}

    # ルートロガーの設定
    root_logger = logging.getLogger()
    log_level = getattr(
        logging, config.get("logging", {}).get("level", "INFO").upper(), logging.INFO
    )
    root_logger.setLevel(log_level)

    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 基本フォーマッター
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ファイルハンドラー
    log_file = config.get("logging", {}).get("file", "application.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


if __name__ == "__main__":
    # テスト実行
    test_config = {
        "logging": {"level": "INFO", "file": "test.log"},
        "security": {"sensitive_keys": ["password", "token"]},
    }

    # グローバルログ設定
    configure_global_logging(test_config)

    # テスト用エラーハンドラー
    error_handler = get_unified_error_logging_system("test_module", test_config)

    # テストエラー
    try:
        raise ValueError("テストエラー")
    except Exception as e:
        error_handler.log_error(
            e,
            "テストコンテキスト",
            ErrorCategory.VALIDATION_ERROR,
            {"test_param": "test_value"},
        )

    # 統計情報の表示
    print(f"エラー統計: {get_global_error_statistics()}")
