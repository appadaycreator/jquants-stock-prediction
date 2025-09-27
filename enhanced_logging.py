#!/usr/bin/env python3
"""
強化されたログ設定モジュール
詳細なログ出力とエラーレベルの適切な使用を提供
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import json


class EnhancedLogger:
    """強化されたログ設定クラス"""

    def __init__(self, name: str = None, log_level: str = "INFO"):
        self.name = name or "enhanced_logger"
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger(self.name)
        self._setup_logger()

    def _setup_logger(self):
        """ログ設定を初期化"""
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()

        # ログレベルを設定
        self.logger.setLevel(self.log_level)

        # フォーマッターの設定
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # コンソールハンドラー（簡潔な形式）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # ファイルハンドラー（詳細な形式）
        file_handler = logging.FileHandler("enhanced.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)

        # エラーファイルハンドラー（エラーのみ）
        error_handler = logging.FileHandler("errors.log", encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)

        # ローテーティングハンドラー（大容量ログ対応）
        rotating_handler = logging.handlers.RotatingFileHandler(
            "application.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        rotating_handler.setLevel(logging.DEBUG)
        rotating_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(rotating_handler)

    def get_logger(self) -> logging.Logger:
        """ロガーインスタンスを取得"""
        return self.logger

    def log_operation_start(self, operation: str, **kwargs):
        """操作開始ログ"""
        self.logger.info(f"🚀 {operation} を開始")
        if kwargs:
            self.logger.debug(f"操作パラメータ: {kwargs}")

    def log_operation_end(self, operation: str, success: bool = True, **kwargs):
        """操作終了ログ"""
        if success:
            self.logger.info(f"✅ {operation} が正常に完了")
        else:
            self.logger.error(f"❌ {operation} が失敗")

        if kwargs:
            self.logger.debug(f"操作結果: {kwargs}")

    def log_data_info(
        self, data_name: str, shape: tuple = None, dtype: str = None, **kwargs
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

    def log_performance(self, operation: str, duration: float, **kwargs):
        """パフォーマンスログ"""
        self.logger.info(f"⏱️ {operation} 実行時間: {duration:.2f}秒")
        if kwargs:
            self.logger.debug(f"パフォーマンス詳細: {kwargs}")

    def log_warning_with_context(self, message: str, context: Dict[str, Any] = None):
        """コンテキスト付き警告ログ"""
        self.logger.warning(f"⚠️ {message}")
        if context:
            self.logger.debug(f"警告コンテキスト: {context}")

    def log_error_with_context(
        self, message: str, error: Exception = None, context: Dict[str, Any] = None
    ):
        """コンテキスト付きエラーログ"""
        self.logger.error(f"❌ {message}")
        if error:
            self.logger.error(f"エラー詳細: {str(error)}")
        if context:
            self.logger.debug(f"エラーコンテキスト: {context}")


class StructuredLogger:
    """構造化ログ出力クラス"""

    def __init__(self, name: str = None):
        self.name = name or "structured_logger"
        self.logger = logging.getLogger(self.name)
        self._setup_structured_logger()

    def _setup_structured_logger(self):
        """構造化ログ設定を初期化"""
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()

        # ログレベルを設定
        self.logger.setLevel(logging.INFO)

        # JSONフォーマッター
        json_formatter = JSONFormatter()

        # ファイルハンドラー（JSON形式）
        json_handler = logging.FileHandler("structured.log", encoding="utf-8")
        json_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_handler)

    def log_structured(self, level: str, message: str, **kwargs):
        """構造化ログ出力"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "logger": self.name,
            **kwargs,
        }

        if level.upper() == "ERROR":
            self.logger.error(json.dumps(log_data, ensure_ascii=False))
        elif level.upper() == "WARNING":
            self.logger.warning(json.dumps(log_data, ensure_ascii=False))
        elif level.upper() == "INFO":
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.debug(json.dumps(log_data, ensure_ascii=False))


class JSONFormatter(logging.Formatter):
    """JSON形式のログフォーマッター"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 例外情報がある場合は追加
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_enhanced_logging(
    logger_name: str = None, log_level: str = "INFO"
) -> EnhancedLogger:
    """強化されたログ設定を初期化"""
    return EnhancedLogger(logger_name, log_level)


def setup_structured_logging(logger_name: str = None) -> StructuredLogger:
    """構造化ログ設定を初期化"""
    return StructuredLogger(logger_name)


def get_enhanced_logger(
    logger_name: str = None, log_level: str = "INFO"
) -> logging.Logger:
    """強化されたロガーを取得"""
    enhanced_logger = setup_enhanced_logging(logger_name, log_level)
    return enhanced_logger.get_logger()


# グローバルログ設定
def configure_global_logging():
    """グローバルログ設定を適用"""
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

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
    file_handler = logging.FileHandler("application.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


# ログレベル定数
class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ログカテゴリ定数
class LogCategory:
    API = "API"
    DATA_PROCESSING = "DATA_PROCESSING"
    MODEL_TRAINING = "MODEL_TRAINING"
    FILE_OPERATION = "FILE_OPERATION"
    VALIDATION = "VALIDATION"
    PERFORMANCE = "PERFORMANCE"
    ERROR = "ERROR"


if __name__ == "__main__":
    # テスト実行
    enhanced_logger = setup_enhanced_logging("test_logger")
    logger = enhanced_logger.get_logger()

    logger.info("テストログメッセージ")
    logger.warning("テスト警告メッセージ")
    logger.error("テストエラーメッセージ")

    # 構造化ログのテスト
    structured_logger = setup_structured_logging("test_structured")
    structured_logger.log_structured(
        "INFO", "構造化ログテスト", user_id=123, operation="test"
    )
