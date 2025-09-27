"""
強化されたログシステム
高度なログ機能とカテゴリ別ログ管理を提供
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pathlib import Path


class LogLevel(Enum):
    """ログレベル"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """ログカテゴリ"""

    SYSTEM = "SYSTEM"
    DATA = "DATA"
    MODEL = "MODEL"
    API = "API"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    ERROR = "ERROR"


class EnhancedLogger:
    """強化されたログクラス"""

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        """
        初期化

        Args:
            name: ロガー名
            level: ログレベル
        """
        self.name = name
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))

        # ハンドラーの設定
        self._setup_handlers()

    def _setup_handlers(self):
        """ハンドラーの設定"""
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)

        # ファイルハンドラー
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / f"{self.name.lower()}.log", encoding="utf-8"
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # ハンドラーの追加
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """ロガーの取得"""
        return self.logger

    def log_with_category(
        self, level: LogLevel, category: LogCategory, message: str, **kwargs
    ):
        """
        カテゴリ付きログ

        Args:
            level: ログレベル
            category: ログカテゴリ
            message: メッセージ
            **kwargs: 追加情報
        """
        formatted_message = f"[{category.value}] {message}"
        if kwargs:
            formatted_message += f" | {kwargs}"

        getattr(self.logger, level.value.lower())(formatted_message)

    def log_performance(self, operation: str, duration: float, **kwargs):
        """
        パフォーマンスログ

        Args:
            operation: 操作名
            duration: 実行時間（秒）
            **kwargs: 追加情報
        """
        self.log_with_category(
            LogLevel.INFO,
            LogCategory.PERFORMANCE,
            f"Operation: {operation}, Duration: {duration:.3f}s",
            **kwargs,
        )

    def log_data_operation(self, operation: str, data_info: Dict[str, Any]):
        """
        データ操作ログ

        Args:
            operation: 操作名
            data_info: データ情報
        """
        self.log_with_category(
            LogLevel.INFO, LogCategory.DATA, f"Data operation: {operation}", **data_info
        )

    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """
        コンテキスト付きエラーログ

        Args:
            error: エラーオブジェクト
            context: コンテキスト情報
        """
        self.log_with_category(
            LogLevel.ERROR, LogCategory.ERROR, f"Error: {str(error)}", **context
        )

    def log_operation_start(self, operation: str, **kwargs):
        """
        操作開始ログ

        Args:
            operation: 操作名
            **kwargs: 追加情報
        """
        self.log_with_category(
            LogLevel.INFO,
            LogCategory.SYSTEM,
            f"Operation started: {operation}",
            **kwargs,
        )

    def log_operation_end(self, operation: str, success: bool = True, **kwargs):
        """
        操作終了ログ

        Args:
            operation: 操作名
            success: 成功フラグ
            **kwargs: 追加情報
        """
        status = "completed successfully" if success else "failed"
        self.log_with_category(
            LogLevel.INFO,
            LogCategory.SYSTEM,
            f"Operation {status}: {operation}",
            **kwargs,
        )

    def log_data_info(self, message: str, **kwargs):
        """
        データ情報ログ

        Args:
            message: メッセージ
            **kwargs: 追加情報
        """
        self.log_with_category(LogLevel.INFO, LogCategory.DATA, message, **kwargs)


def setup_enhanced_logging(
    name: str, level: LogLevel = LogLevel.INFO
) -> EnhancedLogger:
    """
    強化されたログシステムのセットアップ

    Args:
        name: ロガー名
        level: ログレベル

    Returns:
        強化されたロガーインスタンス
    """
    return EnhancedLogger(name, level)


def get_enhanced_logger(name: str, level: LogLevel = LogLevel.INFO) -> EnhancedLogger:
    """
    強化されたロガーの取得

    Args:
        name: ロガー名
        level: ログレベル

    Returns:
        強化されたロガーインスタンス
    """
    return setup_enhanced_logging(name, level)


# グローバルログ設定
def configure_global_logging(level: LogLevel = LogLevel.INFO):
    """
    グローバルログ設定

    Args:
        level: ログレベル
    """
    logging.basicConfig(
        level=getattr(logging, level.value),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/global.log", encoding="utf-8"),
        ],
    )


# ログディレクトリの作成
def ensure_log_directory():
    """ログディレクトリの作成"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir
