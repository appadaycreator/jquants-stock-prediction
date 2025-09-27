#!/usr/bin/env python3
"""
セキュアなエラーハンドリングモジュール
機密情報の漏洩を防ぎ、適切な例外処理を提供
"""

import logging
import traceback
import os
import re
from typing import Any, Dict, Callable, Optional, Union
from datetime import datetime
import functools
from security_config import SecurityConfig


class SecureErrorHandler:
    """セキュアなエラーハンドリングクラス"""
    
    def __init__(self, logger_name: str = None):
        self.logger = logging.getLogger(logger_name or __name__)
        self.error_context = {}
        self.error_count = 0
        self.security_config = SecurityConfig()
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def set_context(self, **kwargs):
        """エラーコンテキストを設定"""
        self.error_context.update(kwargs)
    
    def clear_context(self):
        """エラーコンテキストをクリア"""
        self.error_context.clear()
    
    def _sanitize_error_message(self, error_message: str) -> str:
        """エラーメッセージから機密情報を除去"""
        # パスワード、トークン、キーなどの機密情報をマスキング
        sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            r'auth["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        ]
        
        sanitized_message = error_message
        for pattern in sensitive_patterns:
            sanitized_message = re.sub(pattern, r'\1***MASKED***', sanitized_message, flags=re.IGNORECASE)
        
        return sanitized_message
    
    def _sanitize_context_data(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """コンテキストデータから機密情報を除去"""
        return self.security_config.mask_sensitive_data(context_data)
    
    def log_error(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
        log_level: int = logging.ERROR,
        include_traceback: bool = True
    ):
        """セキュアなエラーログを出力"""
        self.error_count += 1
        
        # エラー情報の収集
        error_info = {
            "error_type": type(error).__name__,
            "error_message": self._sanitize_error_message(str(error)),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "error_count": self.error_count,
        }
        
        # トレースバックの処理（機密情報を除去）
        if include_traceback:
            tb_lines = traceback.format_exc().split('\n')
            sanitized_tb = []
            for line in tb_lines:
                sanitized_tb.append(self._sanitize_error_message(line))
            error_info["traceback"] = '\n'.join(sanitized_tb)
        
        # 追加情報のマージ（機密情報を除去）
        if additional_info:
            error_info.update(self._sanitize_context_data(additional_info))
        
        # コンテキスト情報のマージ（機密情報を除去）
        if self.error_context:
            error_info["context_data"] = self._sanitize_context_data(self.error_context.copy())
        
        # ログメッセージの構築
        log_message = self._build_error_message(error_info)
        
        # ログ出力
        self.logger.log(log_level, log_message)
        
        # エラー詳細をファイルに保存（必要に応じて）
        if log_level >= logging.ERROR:
            self._save_error_details(error_info)
        
        return error_info
    
    def _build_error_message(self, error_info: Dict[str, Any]) -> str:
        """エラーメッセージの構築"""
        message_parts = [
            f"エラー発生: {error_info['error_type']}",
            f"メッセージ: {error_info['error_message']}",
            f"コンテキスト: {error_info['context']}",
            f"発生時刻: {error_info['timestamp']}",
        ]
        
        if error_info.get('context_data'):
            context_str = ", ".join([f"{k}: {v}" for k, v in error_info['context_data'].items()])
            message_parts.append(f"コンテキストデータ: {context_str}")
        
        return " | ".join(message_parts)
    
    def _save_error_details(self, error_info: Dict[str, Any]) -> None:
        """エラー詳細をファイルに保存"""
        try:
            error_file = f"error_details_{datetime.now().strftime('%Y%m%d')}.log"
            with open(error_file, "a", encoding="utf-8") as f:
                f.write(f"{'='*80}\n")
                f.write(f"エラー発生時刻: {error_info['timestamp']}\n")
                f.write(f"エラータイプ: {error_info['error_type']}\n")
                f.write(f"エラーメッセージ: {error_info['error_message']}\n")
                f.write(f"コンテキスト: {error_info['context']}\n")
                if error_info.get('traceback'):
                    f.write(f"トレースバック:\n{error_info['traceback']}\n")
                f.write(f"{'='*80}\n")
        except Exception as e:
            self.logger.warning(f"エラー詳細の保存に失敗: {e}")
    
    def handle_api_error(
        self, 
        error: Exception, 
        api_endpoint: str, 
        request_data: Dict[str, Any] = None,
        retry_count: int = 0
    ) -> bool:
        """APIエラーの安全な処理"""
        # リクエストデータから機密情報を除去
        safe_request_data = self._sanitize_context_data(request_data or {})
        
        context = f"APIエラー - {api_endpoint}"
        additional_info = {
            "api_endpoint": api_endpoint,
            "request_data": safe_request_data,
            "retry_count": retry_count,
        }
        
        self.log_error(error, context, additional_info)
        
        # リトライ可能なエラーかどうかを判定
        if retry_count < self.max_retries:
            self.logger.info(f"⏳ {self.retry_delay}秒後にリトライします (試行 {retry_count + 1}/{self.max_retries})")
            return True  # リトライ可能
        
        return False  # リトライ不可
    
    def handle_data_processing_error(
        self, 
        error: Exception, 
        operation: str, 
        data_shape: tuple = None,
        column_name: str = None
    ) -> bool:
        """データ処理エラーの安全な処理"""
        context = f"データ処理エラー - {operation}"
        additional_info = {
            "operation": operation,
            "data_shape": data_shape,
            "column_name": column_name,
        }
        
        self.log_error(error, context, additional_info)
        
        # データ処理エラーの場合は代替処理を試行
        self.logger.warning("⚠️ 代替処理を試行します")
        return True
    
    def handle_file_error(self, error: Exception, file_path: str, operation: str) -> bool:
        """ファイルエラーの安全な処理"""
        context = f"ファイルエラー - {operation}"
        additional_info = {
            "file_path": file_path,
            "operation": operation,
            "file_exists": os.path.exists(file_path),
            "file_readable": (
                os.access(file_path, os.R_OK) if os.path.exists(file_path) else False
            ),
        }
        
        self.log_error(error, context, additional_info)
        
        # ファイルエラーの場合は代替パスを試行
        if operation in ["read", "load"]:
            self.logger.warning("⚠️ 代替ファイルパスを試行します")
            return True
        else:
            self.logger.error("❌ ファイル操作に失敗したため処理を停止します")
            return False


def secure_error_handler_decorator(
    error_handler: SecureErrorHandler = None,
    context: str = "",
    reraise: bool = True,
    return_on_error: Any = None,
    max_retries: int = 3
):
    """セキュアなエラーハンドリングデコレータ"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = error_handler or SecureErrorHandler()
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 特定の例外タイプに応じた処理
                    if isinstance(e, (ValueError, TypeError, KeyError)):
                        # データ関連エラーは即座に再発生
                        handler.log_error(e, context or f"関数 {func.__name__}")
                        if reraise:
                            raise
                        return return_on_error
                    elif isinstance(e, (ConnectionError, TimeoutError)):
                        # ネットワークエラーはリトライ
                        if retry_count < max_retries:
                            handler.log_error(e, f"{context or func.__name__} - リトライ {retry_count + 1}")
                            retry_count += 1
                            continue
                        else:
                            handler.log_error(e, f"{context or func.__name__} - 最大リトライ回数に達しました")
                            if reraise:
                                raise
                            return return_on_error
                    else:
                        # その他のエラー
                        handler.log_error(e, context or f"関数 {func.__name__}")
                        if reraise:
                            raise
                        return return_on_error
            
            # 全てのリトライが失敗した場合
            final_error = Exception(f"関数 {func.__name__} が {max_retries} 回失敗しました")
            handler.log_error(final_error, context or f"関数 {func.__name__}")
            if reraise:
                raise final_error
            return return_on_error
        
        return wrapper
    
    return decorator


# グローバルセキュアエラーハンドラーインスタンス
global_secure_error_handler = SecureErrorHandler("global_secure_error_handler")
