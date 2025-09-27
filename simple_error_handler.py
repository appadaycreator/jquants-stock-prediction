#!/usr/bin/env python3
"""
シンプルなエラーハンドリングユーティリティ
必要最小限の機能に簡素化
"""

import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime


class SimpleErrorHandler:
    """シンプルなエラーハンドリングクラス"""

    def __init__(self, logger_name: str = None):
        self.logger = logging.getLogger(logger_name or __name__)

    def log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
    ):
        """シンプルなエラーログ出力"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }

        if additional_info:
            error_info.update(additional_info)

        # ログメッセージの構築
        log_message = f"❌ エラー [{context}]: {error_info['error_type']} - {error_info['error_message']}"

        # ログ出力
        self.logger.error(log_message)

        # デバッグ情報（DEBUGレベル）
        self.logger.debug(f"詳細情報: {error_info}")
        self.logger.debug(f"スタックトレース:\n{traceback.format_exc()}")

        return error_info

    def handle_api_error(
        self,
        error: Exception,
        api_name: str,
        endpoint: str = "",
        status_code: int = None,
    ):
        """API関連エラーのハンドリング"""
        context = f"API呼び出しエラー - {api_name}"
        if endpoint:
            context += f" ({endpoint})"

        additional_info = {
            "api_name": api_name,
            "endpoint": endpoint,
            "status_code": status_code,
        }

        return self.log_error(error, context, additional_info)

    def handle_file_error(self, error: Exception, file_path: str, operation: str):
        """ファイル操作エラーのハンドリング"""
        context = f"ファイル操作エラー - {operation}"
        additional_info = {
            "file_path": file_path,
            "operation": operation,
        }
        return self.log_error(error, context, additional_info)


def get_simple_error_handler(logger_name: str = None) -> SimpleErrorHandler:
    """シンプルエラーハンドラーインスタンスを取得"""
    return SimpleErrorHandler(logger_name)
