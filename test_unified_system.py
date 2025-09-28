#!/usr/bin/env python3
"""
テスト用の簡易UnifiedSystem
重い初期化処理をスキップしてテストを高速化
"""

import logging
import os
from typing import Dict, Any, Optional
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


class FileError(Exception):
    """ファイルエラー"""
    pass


class ValidationError(Exception):
    """検証エラー"""
    pass


class NetworkError(Exception):
    """ネットワークエラー"""
    pass


class AuthenticationError(Exception):
    """認証エラー"""
    pass


class ModelError(Exception):
    """モデルエラー"""
    pass


class TestUnifiedSystem:
    """テスト用の簡易統合システム"""
    
    def __init__(self, module_name: str = "TestUnifiedSystem"):
        """簡易初期化"""
        self.module_name = module_name
        self.config = {}
        self.error_count = 0
        self.error_stats = {category.value: 0 for category in ErrorCategory}
        
        # 簡易ログ設定
        self.logger = logging.getLogger(f"test_{module_name}")
        self.logger.setLevel(logging.WARNING)
        
        # エラーハンドラーを簡易化
        self.ErrorCategory = ErrorCategory
        
    def handle_file_error(self, error: Exception, file_path: str, operation: str):
        """ファイルエラーハンドリング"""
        self.error_count += 1
        self.error_stats[ErrorCategory.FILE_ERROR.value] += 1
        raise FileError(f"ファイルエラー: {error}")
    
    def handle_validation_error(self, error: Exception):
        """検証エラーハンドリング"""
        self.error_count += 1
        self.error_stats[ErrorCategory.VALIDATION_ERROR.value] += 1
        raise ValidationError(f"検証エラー: {error}")
    
    def handle_network_error(self, error: Exception, operation: str):
        """ネットワークエラーハンドリング"""
        self.error_count += 1
        self.error_stats[ErrorCategory.NETWORK_ERROR.value] += 1
        raise NetworkError(f"ネットワークエラー: {error}")
    
    def handle_authentication_error(self, error: Exception, operation: str):
        """認証エラーハンドリング"""
        self.error_count += 1
        self.error_stats[ErrorCategory.AUTHENTICATION_ERROR.value] += 1
        raise AuthenticationError(f"認証エラー: {error}")
    
    def log_error(self, error: Exception, context: str = "", **kwargs):
        """エラーログ"""
        self.error_count += 1
        self.logger.error(f"{context}: {error}")
    
    def log_info(self, message: str, **kwargs):
        """情報ログ"""
        self.logger.info(message)
    
    def log_warning(self, message: str, **kwargs):
        """警告ログ"""
        self.logger.warning(message)
    
    def log_debug(self, message: str, **kwargs):
        """デバッグログ"""
        self.logger.debug(message)
    
    def get_config(self, key: str = None, default: Any = None) -> Any:
        """設定取得"""
        if key is None:
            return self.config
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """設定設定"""
        self.config[key] = value


# グローバル変数
_test_unified_system = None


def get_test_unified_system(module_name: str = "TestGlobal") -> TestUnifiedSystem:
    """テスト用統合システムの取得"""
    global _test_unified_system
    if _test_unified_system is None:
        _test_unified_system = TestUnifiedSystem(module_name)
    return _test_unified_system


def reset_test_unified_system() -> None:
    """テスト用統合システムのリセット"""
    global _test_unified_system
    _test_unified_system = None
