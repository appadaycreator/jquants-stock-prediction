#!/usr/bin/env python3
"""
ログ管理システム - 統合システムから分離
ログの設定、出力、フォーマット、セキュリティ管理
"""

import logging
import logging.handlers
import sys
import os
import re
from typing import Dict, Any
from enum import Enum


class LogLevel(Enum):
    """ログレベルの定義"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """ログカテゴリの定義"""

    SYSTEM = "SYSTEM"
    API = "API"
    DATA = "DATA"
    MODEL = "MODEL"
    PERFORMANCE = "PERFORMANCE"
    ERROR = "ERROR"
    SECURITY = "SECURITY"


class LoggingManager:
    """ログ管理システム"""

    def __init__(
        self, module_name: str = "LoggingManager", config: Dict[str, Any] = None
    ):
        """初期化"""
        self.module_name = module_name
        self.config = config or {}

        # セキュリティ設定
        self.sensitive_keys = self.config.get("security", {}).get(
            "sensitive_keys", ["password", "token", "key", "secret", "auth", "email"]
        )

        # ログシステムの初期化
        self._setup_logging()

    def _setup_logging(self) -> None:
        """ログシステムの初期化"""
        # ログ設定の取得
        logging_config = self.config.get("logging", {})
        log_level = getattr(
            logging, logging_config.get("level", "INFO").upper(), logging.INFO
        )

        # ロガーの設定
        self.logger = logging.getLogger(f"LoggingManager.{self.module_name}")
        self.logger.setLevel(log_level)

        # 既存のハンドラーをクリア
        self.logger.handlers.clear()

        # フォーマッターの設定
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | "
            "%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # コンソールハンドラー
        if logging_config.get("console_output", True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)

        # ファイルハンドラー（詳細ログ）
        log_file = logging_config.get("file", "jquants.log")
        try:
            # ログファイルのディレクトリを作成
            log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "."
            os.makedirs(log_dir, exist_ok=True)

            # ログファイルが存在しない場合は作成
            if not os.path.exists(log_file):
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write("")

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            # ログファイル作成に失敗した場合はコンソールのみで続行
            print(f"Warning: Failed to create log file {log_file}: {e}")

        # エラーファイルハンドラー（エラーのみ）
        error_log_file = "errors.log"
        try:
            if not os.path.exists(error_log_file):
                with open(error_log_file, "w", encoding="utf-8") as f:
                    f.write("")

            error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(error_handler)
        except Exception as e:
            # エラーログファイル作成に失敗した場合はコンソールのみで続行
            print(f"Warning: Failed to create error log file {error_log_file}: {e}")

    def _sanitize_message(self, message: str) -> str:
        """機密情報のマスキング"""
        if not self.config.get("security", {}).get("mask_sensitive_data", True):
            return message

        sanitized = message
        for key in self.sensitive_keys:
            # パターンマッチングで機密情報をマスキング
            pattern = rf"\b{key}[=:]\s*[^\s,}}]+"
            sanitized = re.sub(pattern, f"{key}=***", sanitized, flags=re.IGNORECASE)

        return sanitized

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """辞書データの機密情報マスキング"""
        if not self.config.get("security", {}).get("mask_sensitive_data", True):
            return data

        masked_data = {}
        for key, value in data.items():
            if any(
                sensitive_key in key.lower() for sensitive_key in self.sensitive_keys
            ):
                masked_data[key] = "***"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
            else:
                masked_data[key] = value

        return masked_data

    def log_info(
        self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs
    ):
        """情報ログの出力"""
        sanitized_message = self._sanitize_message(message)
        self.logger.info(f"[{category.value}] {sanitized_message}")

        if kwargs:
            masked_kwargs = self._mask_sensitive_data(kwargs)
            self.logger.info(f"追加情報: {masked_kwargs}")

    def log_warning(
        self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs
    ):
        """警告ログの出力"""
        sanitized_message = self._sanitize_message(message)
        self.logger.warning(f"[{category.value}] {sanitized_message}")

        if kwargs:
            masked_kwargs = self._mask_sensitive_data(kwargs)
            self.logger.warning(f"追加情報: {masked_kwargs}")

    def log_debug(
        self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs
    ):
        """デバッグログの出力"""
        sanitized_message = self._sanitize_message(message)
        self.logger.debug(f"[{category.value}] {sanitized_message}")

        if kwargs:
            masked_kwargs = self._mask_sensitive_data(kwargs)
            self.logger.debug(f"追加情報: {masked_kwargs}")

    def log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
        level: LogLevel = LogLevel.ERROR,
    ):
        """エラーログの出力"""
        # 機密情報をマスキング
        sanitized_context = self._sanitize_message(context)
        sanitized_error_msg = self._sanitize_message(str(error))

        # 追加情報のマスキング
        masked_info = None
        if additional_info:
            masked_info = self._mask_sensitive_data(additional_info)

        # エラーログの出力（レベル別）
        log_message = f"❌ エラー: {sanitized_context}"

        if level == LogLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == LogLevel.INFO:
            self.logger.info(log_message)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_message)
        elif level == LogLevel.ERROR:
            self.logger.error(log_message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_message)

        self.logger.error(f"エラー詳細: {sanitized_error_msg}")

        if masked_info:
            self.logger.error(f"追加情報: {masked_info}")

        if include_traceback:
            import traceback

            traceback_str = self._sanitize_message(
                "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
            )
            self.logger.error(f"トレースバック: {traceback_str}")

    def get_logger(self) -> logging.Logger:
        """ロガーの取得"""
        return self.logger

    def set_log_level(self, level: LogLevel) -> None:
        """ログレベルの設定"""
        self.logger.setLevel(getattr(logging, level.value))

    def add_handler(self, handler: logging.Handler) -> None:
        """ハンドラーの追加"""
        self.logger.addHandler(handler)

    def remove_handler(self, handler: logging.Handler) -> None:
        """ハンドラーの削除"""
        self.logger.removeHandler(handler)

    def clear_handlers(self) -> None:
        """ハンドラーのクリア"""
        self.logger.handlers.clear()
