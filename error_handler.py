#!/usr/bin/env python3
"""
包括的なエラーハンドリングユーティリティ
詳細なエラーログ出力と適切なエラー分類を提供
"""

import logging
import traceback
import os
from typing import Any, Dict, Callable
from datetime import datetime
import functools


class ErrorHandler:
    """包括的なエラーハンドリングクラス"""

    def __init__(self, logger_name: str = None):
        self.logger = logging.getLogger(logger_name or __name__)
        self.error_context = {}
        self.error_count = 0

    def set_context(self, **kwargs):
        """エラーコンテキストを設定"""
        self.error_context.update(kwargs)

    def clear_context(self):
        """エラーコンテキストをクリア"""
        self.error_context.clear()

    def log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
        log_level: int = logging.ERROR,
    ):
        """詳細なエラーログを出力"""
        self.error_count += 1

        # エラー情報の収集
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "error_count": self.error_count,
            "traceback": traceback.format_exc(),
        }

        # 追加情報のマージ
        if additional_info:
            error_info.update(additional_info)

        # コンテキスト情報のマージ
        if self.error_context:
            error_info["context_data"] = self.error_context.copy()

        # ログメッセージの構築
        log_message = self._build_error_message(error_info)

        # ログ出力
        self.logger.log(log_level, log_message)

        # エラー詳細をファイルに保存（必要に応じて）
        if log_level >= logging.ERROR:
            self._save_error_details(error_info)

        return error_info

    def _build_error_message(self, error_info: Dict[str, Any]) -> str:
        """エラーメッセージを構築"""
        parts = [
            f"❌ エラー発生 [{error_info['error_count']}]",
            f"タイプ: {error_info['error_type']}",
            f"メッセージ: {error_info['error_message']}",
            f"コンテキスト: {error_info['context']}",
            f"時刻: {error_info['timestamp']}",
        ]

        if "context_data" in error_info:
            context_str = ", ".join(
                [f"{k}={v}" for k, v in error_info["context_data"].items()]
            )
            parts.append(f"追加情報: {context_str}")

        return " | ".join(parts)

    def _save_error_details(self, error_info: Dict[str, Any]):
        """エラー詳細をファイルに保存"""
        try:
            error_log_file = "error_details.log"
            with open(error_log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"エラー詳細 [{error_info['timestamp']}]\n")
                f.write(f"{'='*80}\n")
                for key, value in error_info.items():
                    f.write(f"{key}: {value}\n")
                f.write(f"{'='*80}\n")
        except Exception as e:
            self.logger.warning(f"エラー詳細の保存に失敗: {e}")

    def handle_api_error(
        self,
        error: Exception,
        api_name: str,
        endpoint: str = "",
        status_code: int = None,
        response_data: Any = None,
    ):
        """API関連エラーの専用ハンドリング"""
        context = f"API呼び出しエラー - {api_name}"
        if endpoint:
            context += f" ({endpoint})"

        additional_info = {
            "api_name": api_name,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_data": str(response_data) if response_data else None,
        }

        return self.log_error(error, context, additional_info)

    def handle_data_processing_error(
        self,
        error: Exception,
        operation: str,
        data_shape: tuple = None,
        column_name: str = None,
    ):
        """データ処理エラーの専用ハンドリング"""
        context = f"データ処理エラー - {operation}"

        additional_info = {
            "operation": operation,
            "data_shape": str(data_shape) if data_shape else None,
            "column_name": column_name,
        }

        return self.log_error(error, context, additional_info)

    def handle_model_error(
        self,
        error: Exception,
        model_name: str,
        operation: str,
        model_params: Dict = None,
    ):
        """機械学習モデルエラーの専用ハンドリング"""
        context = f"モデルエラー - {model_name} ({operation})"

        additional_info = {
            "model_name": model_name,
            "operation": operation,
            "model_params": str(model_params) if model_params else None,
        }

        return self.log_error(error, context, additional_info)

    def handle_file_error(self, error: Exception, file_path: str, operation: str):
        """ファイル操作エラーの専用ハンドリング"""
        context = f"ファイル操作エラー - {operation}"

        additional_info = {
            "file_path": file_path,
            "operation": operation,
            "file_exists": os.path.exists(file_path) if file_path else None,
            "file_readable": (
                os.access(file_path, os.R_OK)
                if file_path and os.path.exists(file_path)
                else None
            ),
        }

        return self.log_error(error, context, additional_info)


def error_handler_decorator(
    error_handler: ErrorHandler = None,
    context: str = "",
    reraise: bool = True,
    return_on_error: Any = None,
):
    """エラーハンドリングデコレータ"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = error_handler or ErrorHandler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler.log_error(e, context or f"関数 {func.__name__}")
                if reraise:
                    raise
                return return_on_error

        return wrapper

    return decorator


class SpecificErrorHandler:
    """特定のエラータイプに特化したハンドラー"""

    def __init__(self, logger_name: str = None):
        self.logger = logging.getLogger(logger_name or __name__)
        self.error_handler = ErrorHandler(logger_name)

    def handle_connection_error(
        self, error: Exception, retry_count: int = 0, max_retries: int = 3
    ) -> bool:
        """接続エラーのハンドリング（リトライ可能）"""
        self.error_handler.log_error(
            error,
            f"接続エラー (試行 {retry_count + 1}/{max_retries + 1})",
            {"retry_count": retry_count, "max_retries": max_retries},
        )

        if retry_count < max_retries:
            self.logger.info(
                f"⏳ 接続を再試行します " f"({retry_count + 1}/{max_retries + 1})"
            )
            return True  # リトライ可能
        else:
            self.logger.error("❌ 最大リトライ回数に達しました")
            return False  # リトライ不可

    def handle_data_validation_error(
        self, error: Exception, validation_type: str, data_info: Dict[str, Any] = None
    ) -> bool:
        """データ検証エラーのハンドリング"""
        context = f"データ検証エラー - {validation_type}"
        additional_info = {
            "validation_type": validation_type,
            "data_info": data_info or {},
        }

        self.error_handler.log_error(error, context, additional_info)

        # データ検証エラーの場合は処理を停止
        self.logger.error("❌ データ検証に失敗したため処理を停止します")
        return False

    def handle_model_training_error(
        self,
        error: Exception,
        model_name: str,
        training_data_info: Dict[str, Any] = None,
    ) -> bool:
        """モデル学習エラーのハンドリング"""
        context = f"モデル学習エラー - {model_name}"
        additional_info = {
            "model_name": model_name,
            "training_data_info": training_data_info or {},
        }

        self.error_handler.log_error(error, context, additional_info)

        # モデル学習エラーの場合は代替モデルを試行
        self.logger.warning("⚠️ 代替モデルでの学習を試行します")
        return True  # 代替処理を試行

    def handle_file_io_error(
        self, error: Exception, file_path: str, operation: str
    ) -> bool:
        """ファイルI/Oエラーのハンドリング"""
        context = f"ファイルI/Oエラー - {operation}"
        additional_info = {
            "file_path": file_path,
            "operation": operation,
            "file_exists": os.path.exists(file_path),
            "file_readable": (
                os.access(file_path, os.R_OK) if os.path.exists(file_path) else False
            ),
        }

        self.error_handler.log_error(error, context, additional_info)

        # ファイルエラーの場合は代替パスを試行
        if operation in ["read", "load"]:
            self.logger.warning("⚠️ 代替ファイルパスを試行します")
            return True  # 代替処理を試行
        else:
            self.logger.error("❌ ファイル操作に失敗したため処理を停止します")
            return False


# グローバルエラーハンドラーインスタンス
global_error_handler = ErrorHandler("global_error_handler")
specific_error_handler = SpecificErrorHandler("specific_error_handler")


def get_error_handler(logger_name: str = None) -> ErrorHandler:
    """エラーハンドラーインスタンスを取得"""
    return ErrorHandler(logger_name)


def get_specific_error_handler(logger_name: str = None) -> SpecificErrorHandler:
    """特定エラーハンドラーインスタンスを取得"""
    return SpecificErrorHandler(logger_name)
