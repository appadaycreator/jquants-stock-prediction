"""
統一されたログ設定
プロジェクト全体で一貫したログフォーマットを提供
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class UnifiedLoggingConfig:
    """統一されたログ設定クラス"""

    # 統一されたログフォーマット
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

    # ログレベル設定
    DEFAULT_LEVEL = logging.INFO

    # ログディレクトリ
    LOG_DIR = Path("logs")

    @classmethod
    def setup_logging(
        cls,
        name: str,
        level: int = None,
        log_file: Optional[str] = None,
        detailed: bool = False,
    ) -> logging.Logger:
        """
        統一されたログ設定を適用

        Args:
            name: ロガー名
            level: ログレベル
            log_file: ログファイル名（オプション）
            detailed: 詳細ログフォーマットを使用するか

        Returns:
            設定済みのロガー
        """
        # ログディレクトリを作成
        cls.LOG_DIR.mkdir(exist_ok=True)

        # ロガーを作成
        logger = logging.getLogger(name)

        # 既存のハンドラーをクリア
        logger.handlers.clear()

        # ログレベルを設定
        if level is None:
            level = cls.DEFAULT_LEVEL
        logger.setLevel(level)

        # フォーマットを選択
        formatter = logging.Formatter(
            cls.DETAILED_LOG_FORMAT if detailed else cls.LOG_FORMAT
        )

        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # ファイルハンドラー（指定された場合）
        if log_file:
            file_path = cls.LOG_DIR / log_file
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @classmethod
    def get_system_logger(cls) -> logging.Logger:
        """システムログ用のロガーを取得"""
        return cls.setup_logging("system", log_file="system.log", detailed=True)

    @classmethod
    def get_data_logger(cls) -> logging.Logger:
        """データ処理ログ用のロガーを取得"""
        return cls.setup_logging("data", log_file="data_processing.log", detailed=True)

    @classmethod
    def get_model_logger(cls) -> logging.Logger:
        """モデルログ用のロガーを取得"""
        return cls.setup_logging("model", log_file="model.log", detailed=True)

    @classmethod
    def get_api_logger(cls) -> logging.Logger:
        """APIログ用のロガーを取得"""
        return cls.setup_logging("api", log_file="api.log", detailed=True)

    @classmethod
    def get_error_logger(cls) -> logging.Logger:
        """エラーログ用のロガーを取得"""
        return cls.setup_logging(
            "error", level=logging.ERROR, log_file="error.log", detailed=True
        )


# 便利な関数
def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """統一されたログ設定でロガーを取得"""
    return UnifiedLoggingConfig.setup_logging(name, log_file=log_file)


def get_system_logger() -> logging.Logger:
    """システムログ用のロガーを取得"""
    return UnifiedLoggingConfig.get_system_logger()


def get_data_logger() -> logging.Logger:
    """データ処理ログ用のロガーを取得"""
    return UnifiedLoggingConfig.get_data_logger()


def get_model_logger() -> logging.Logger:
    """モデルログ用のロガーを取得"""
    return UnifiedLoggingConfig.get_model_logger()


def get_api_logger() -> logging.Logger:
    """APIログ用のロガーを取得"""
    return UnifiedLoggingConfig.get_api_logger()


def get_error_logger() -> logging.Logger:
    """エラーログ用のロガーを取得"""
    return UnifiedLoggingConfig.get_error_logger()


def get_enhanced_logger() -> logging.Logger:
    """拡張ログ用のロガーを取得（データ情報ログ用）"""
    logger = UnifiedLoggingConfig.setup_logging(
        "enhanced", log_file="enhanced.log", detailed=True
    )

    # 拡張メソッドを追加
    def log_data_info(message: str, **kwargs):
        """データ情報をログに記録"""
        info_parts = [message]
        for key, value in kwargs.items():
            info_parts.append(f"{key}={value}")
        logger.info(" | ".join(info_parts))

    def log_operation_start(operation: str, **kwargs):
        """操作開始をログに記録"""
        info_parts = [f"🚀 {operation}開始"]
        for key, value in kwargs.items():
            info_parts.append(f"{key}={value}")
        logger.info(" | ".join(info_parts))

    def log_operation_end(operation: str, success: bool = True, **kwargs):
        """操作終了をログに記録"""
        status = "✅ 成功" if success else "❌ 失敗"
        info_parts = [f"🏁 {operation}終了", status]
        for key, value in kwargs.items():
            info_parts.append(f"{key}={value}")
        logger.info(" | ".join(info_parts))

    # メソッドをロガーに追加
    logger.log_data_info = log_data_info
    logger.log_operation_start = log_operation_start
    logger.log_operation_end = log_operation_end

    return logger
