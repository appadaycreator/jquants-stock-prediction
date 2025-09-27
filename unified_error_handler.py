#!/usr/bin/env python3
"""
統合エラーハンドラー
統一されたエラーハンドリング機能を提供するモジュール
"""

import logging
import traceback
import re
from typing import Dict, Any, Optional
from datetime import datetime


class UnifiedErrorHandler:
    """統合エラーハンドラークラス"""

    def __init__(self, module_name: str):
        """初期化"""
        self.module_name = module_name
        self.logger = logging.getLogger(f"{__name__}.{module_name}")
        self.error_count = 0
        self.sensitive_keys = ["password", "token", "key", "secret", "auth", "email"]

    def log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
    ):
        """エラーログ出力"""
        self.error_count += 1

        # 機密情報をマスキング
        sanitized_context = self._sanitize_message(context)
        sanitized_error_msg = self._sanitize_message(str(error))

        # 追加情報のマスキング
        masked_info = None
        if additional_info:
            masked_info = self._mask_sensitive_data(additional_info)

        # エラーログの出力
        self.logger.error(f"❌ エラー #{self.error_count}: {sanitized_context}")
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

        self.log_error(error, error_context, additional_info)

    def handle_api_error(
        self,
        error: Exception,
        api_name: str,
        url: str,
        status_code: int = None,
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

        self.log_error(error, error_context, additional_info)

    def handle_file_error(
        self,
        error: Exception,
        file_path: str,
        operation: str,
    ):
        """ファイルエラーの処理"""
        error_context = f"ファイルエラー - {operation}"

        additional_info = {
            "file_path": file_path,
            "operation": operation,
            "module": self.module_name,
        }

        self.log_error(error, error_context, additional_info)

    def handle_data_error(
        self,
        error: Exception,
        data_info: Dict[str, Any] = None,
        operation: str = "データ処理",
    ):
        """データ処理エラーの処理"""
        error_context = f"データエラー - {operation}"

        additional_info = {
            "operation": operation,
            "module": self.module_name,
        }

        if data_info:
            additional_info.update(data_info)

        self.log_error(error, error_context, additional_info)

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


# グローバルエラーハンドラーインスタンスの管理
_error_handlers = {}


def get_unified_error_handler(module_name: str) -> UnifiedErrorHandler:
    """統合エラーハンドラーを取得"""
    if module_name not in _error_handlers:
        _error_handlers[module_name] = UnifiedErrorHandler(module_name)
    return _error_handlers[module_name]


def reset_error_handlers():
    """エラーハンドラーをリセット"""
    _error_handlers.clear()


def get_error_statistics() -> Dict[str, int]:
    """エラー統計を取得"""
    stats = {}
    for module_name, handler in _error_handlers.items():
        stats[module_name] = handler.error_count
    return stats


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)

    # テスト用エラーハンドラー
    error_handler = get_unified_error_handler("test_module")

    # テストエラー
    try:
        raise ValueError("テストエラー")
    except Exception as e:
        error_handler.log_error(e, "テストコンテキスト", {"test_param": "test_value"})

    # 統計情報の表示
    print(f"エラー統計: {get_error_statistics()}")
