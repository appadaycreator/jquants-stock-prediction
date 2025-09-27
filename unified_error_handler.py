#!/usr/bin/env python3
"""
統合エラーハンドリングモジュール
シンプルでセキュアなエラーハンドリングを提供
"""

import logging
import traceback
import os
import re
from typing import Any, Dict, Optional
from datetime import datetime


class UnifiedErrorHandler:
    """統合エラーハンドリングクラス"""

    def __init__(self, logger_name: str = None):
        self.logger = logging.getLogger(logger_name or __name__)
        self.error_count = 0
        self.sensitive_keys = ["password", "token", "key", "secret", "auth"]

    def _sanitize_message(self, message: str) -> str:
        """機密情報をマスキング"""
        # パスワード、トークン、キーなどの機密情報をマスキング
        sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'auth["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        ]

        sanitized = message
        for pattern in sensitive_patterns:
            sanitized = re.sub(
                pattern, r"\1***MASKED***", sanitized, flags=re.IGNORECASE
            )
        return sanitized

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """機密データのマスキング"""
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive_key in key.lower() for sensitive_key in self.sensitive_keys):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    masked_data[key] = "***"
        
        return masked_data

    def log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
    ):
        """統合エラーログ出力"""
        self.error_count += 1

        # エラー情報の収集
        error_info = {
            "error_type": type(error).__name__,
            "error_message": self._sanitize_message(str(error)),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "error_count": self.error_count,
        }

        # トレースバックの処理（機密情報を除去）
        if include_traceback:
            tb_lines = traceback.format_exc().split("\n")
            sanitized_tb = []
            for line in tb_lines:
                sanitized_tb.append(self._sanitize_message(line))
            error_info["traceback"] = "\n".join(sanitized_tb)

        # 追加情報のマージ（機密情報を除去）
        if additional_info:
            error_info.update(self._mask_sensitive_data(additional_info))

        # ログメッセージの構築
        log_message = f"❌ エラー [{context}]: {error_info['error_type']} - {error_info['error_message']}"

        # ログ出力
        self.logger.error(log_message)

        # デバッグ情報（DEBUGレベル）
        self.logger.debug(f"詳細情報: {error_info}")
        if include_traceback:
            self.logger.debug(f"スタックトレース:\n{error_info.get('traceback', '')}")

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
            "file_exists": os.path.exists(file_path) if file_path else None,
        }
        return self.log_error(error, context, additional_info)

    def handle_data_error(
        self,
        error: Exception,
        operation: str,
        data_shape: tuple = None,
        column_name: str = None,
    ):
        """データ処理エラーのハンドリング"""
        context = f"データ処理エラー - {operation}"
        additional_info = {
            "operation": operation,
            "data_shape": str(data_shape) if data_shape else None,
            "column_name": column_name,
        }
        return self.log_error(error, context, additional_info)


def get_unified_error_handler(logger_name: str = None) -> UnifiedErrorHandler:
    """統合エラーハンドラーインスタンスを取得"""
    return UnifiedErrorHandler(logger_name)
