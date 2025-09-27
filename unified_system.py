#!/usr/bin/env python3
"""
完全統合システム - 最高優先度問題の解決
エラーハンドリング、設定管理、ログシステムを統合した単一システム
"""

import logging
import logging.handlers
import traceback
import re
import os
import sys
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from pathlib import Path
import warnings

# 警告を抑制
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


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


class UnifiedSystem:
    """完全統合システム - エラーハンドリング、設定管理、ログシステムの統合"""

    def __init__(
        self,
        module_name: str = "UnifiedSystem",
        config_file: str = "config_unified.yaml",
    ):
        """初期化"""
        self.module_name = module_name
        self.config_file = config_file
        self.config = {}
        self.error_count = 0
        self.error_stats = {category.value: 0 for category in ErrorCategory}

        # 設定の読み込み
        self._load_config()

        # ログシステムの初期化
        self._setup_logging()

        # セキュリティ設定
        self.sensitive_keys = self.config.get("security", {}).get(
            "sensitive_keys", ["password", "token", "key", "secret", "auth", "email"]
        )

        self.logger.info(f"🚀 統合システム初期化完了: {self.module_name}")

    def _load_config(self) -> None:
        """統合設定の読み込み"""
        try:
            # 統合設定ファイルの読み込み
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                self.logger.info(f"✅ 統合設定ファイル読み込み完了: {self.config_file}")
            else:
                # デフォルト設定の作成
                self._create_default_config()

            # 環境別設定の適用
            self._apply_environment_config()

        except Exception as e:
            print(f"❌ 設定ファイル読み込みエラー: {e}")
            self._create_default_config()

    def _create_default_config(self) -> None:
        """デフォルト設定の作成"""
        self.config = {
            "system": {
                "name": "J-Quants株価予測システム",
                "version": "2.0.0",
                "environment": "production",
                "debug": False,
            },
            "logging": {"level": "INFO", "file": "jquants.log", "console_output": True},
            "security": {
                "sensitive_keys": [
                    "password",
                    "token",
                    "key",
                    "secret",
                    "auth",
                    "email",
                ],
                "mask_sensitive_data": True,
            },
            "error_handling": {"unified_handler": True, "error_statistics": True},
        }

    def _apply_environment_config(self) -> None:
        """環境別設定の適用"""
        environment = self.config.get("system", {}).get("environment", "production")

        if environment in self.config.get("environments", {}):
            env_config = self.config["environments"][environment]
            # 環境別設定をメイン設定にマージ
            self._deep_merge(self.config, env_config)

    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """深いマージ処理"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _setup_logging(self) -> None:
        """統合ログシステムの初期化"""
        # ログ設定の取得
        logging_config = self.config.get("logging", {})
        log_level = getattr(
            logging, logging_config.get("level", "INFO").upper(), logging.INFO
        )

        # ロガーの設定
        self.logger = logging.getLogger(f"UnifiedSystem.{self.module_name}")
        self.logger.setLevel(log_level)

        # 既存のハンドラーをクリア
        self.logger.handlers.clear()

        # フォーマッターの設定
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s",
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
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)

        # エラーファイルハンドラー（エラーのみ）
        error_handler = logging.FileHandler("errors.log", encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)

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

    def log_error(
        self,
        error: Exception,
        context: str = "",
        category: ErrorCategory = ErrorCategory.API_ERROR,
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
    ):
        """統合エラーログ出力"""
        self.error_count += 1
        self.error_stats[category.value] += 1

        # 機密情報をマスキング
        sanitized_context = self._sanitize_message(context)
        sanitized_error_msg = self._sanitize_message(str(error))

        # 追加情報のマスキング
        masked_info = None
        if additional_info:
            masked_info = self._mask_sensitive_data(additional_info)

        # エラーログの出力
        self.logger.error(
            f"❌ エラー #{self.error_count} [{category.value}]: {sanitized_context}"
        )
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

    def handle_api_error(
        self,
        error: Exception,
        api_name: str,
        url: str,
        status_code: int = None,
        context: Dict[str, Any] = None,
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

        if context:
            additional_info.update(context)

        self.log_error(error, error_context, ErrorCategory.API_ERROR, additional_info)

    def handle_model_error(
        self,
        error: Exception,
        model_name: str,
        operation: str,
        context: Dict[str, Any] = None,
    ):
        """モデルエラーの処理"""
        error_context = f"{model_name} モデル {operation} エラー"

        additional_info = {
            "model_name": model_name,
            "operation": operation,
            "module": self.module_name,
        }

        if context:
            additional_info.update(context)

        self.log_error(error, error_context, ErrorCategory.MODEL_ERROR, additional_info)

    def handle_file_error(
        self,
        error: Exception,
        file_path: str,
        operation: str,
        context: Dict[str, Any] = None,
    ):
        """ファイルエラーの処理"""
        error_context = f"ファイル {operation} エラー: {file_path}"

        additional_info = {
            "file_path": file_path,
            "operation": operation,
            "module": self.module_name,
        }

        if context:
            additional_info.update(context)

        self.log_error(error, error_context, ErrorCategory.FILE_ERROR, additional_info)

    def handle_data_processing_error(
        self,
        error: Exception,
        operation: str,
        data_info: Dict[str, Any] = None,
        context: Dict[str, Any] = None,
    ):
        """データ処理エラーの処理"""
        error_context = f"データ処理 {operation} エラー"

        additional_info = {
            "operation": operation,
            "module": self.module_name,
        }

        if data_info:
            additional_info.update(data_info)

        if context:
            additional_info.update(context)

        self.log_error(
            error, error_context, ErrorCategory.DATA_PROCESSING_ERROR, additional_info
        )

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

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """設定値の取得"""
        if key is None:
            return self.config

        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set_config(self, key: str, value: Any) -> None:
        """設定値の設定"""
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計の取得"""
        return {
            "total_errors": self.error_count,
            "error_by_category": self.error_stats,
            "module": self.module_name,
            "timestamp": datetime.now().isoformat(),
        }

    def reset_error_count(self) -> None:
        """エラーカウントのリセット"""
        self.error_count = 0
        self.error_stats = {category.value: 0 for category in ErrorCategory}
        self.logger.info("エラーカウントをリセットしました")

    def save_config(self, file_path: str = None) -> None:
        """設定の保存"""
        if file_path is None:
            file_path = self.config_file

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"設定を保存しました: {file_path}")
        except Exception as e:
            self.handle_file_error(e, file_path, "保存")


# グローバルインスタンス
_unified_system = None


def get_unified_system(module_name: str = "Global") -> UnifiedSystem:
    """統合システムの取得（シングルトンパターン）"""
    global _unified_system
    if _unified_system is None:
        _unified_system = UnifiedSystem(module_name)
    return _unified_system


def reset_unified_system() -> None:
    """統合システムのリセット（テスト用）"""
    global _unified_system
    _unified_system = None


# 便利な関数
def log_error(error: Exception, context: str = "", **kwargs):
    """エラーログの簡易出力"""
    system = get_unified_system()
    system.log_error(error, context, **kwargs)


def log_info(message: str, **kwargs):
    """情報ログの簡易出力"""
    system = get_unified_system()
    system.log_info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """警告ログの簡易出力"""
    system = get_unified_system()
    system.log_warning(message, **kwargs)


def log_debug(message: str, **kwargs):
    """デバッグログの簡易出力"""
    system = get_unified_system()
    system.log_debug(message, **kwargs)


def get_config(key: str = None, default: Any = None) -> Any:
    """設定値の簡易取得"""
    system = get_unified_system()
    return system.get_config(key, default)


def set_config(key: str, value: Any) -> None:
    """設定値の簡易設定"""
    system = get_unified_system()
    system.set_config(key, value)


if __name__ == "__main__":
    # テスト実行
    system = UnifiedSystem("TestModule")

    # テストログ出力
    system.log_info("統合システムのテスト開始")
    system.log_warning("これは警告メッセージです")
    system.log_debug("これはデバッグメッセージです")

    # テストエラー処理
    try:
        raise ValueError("テストエラー")
    except Exception as e:
        system.log_error(e, "テストエラーの処理")

    # エラー統計の表示
    stats = system.get_error_statistics()
    print(f"エラー統計: {stats}")

    system.log_info("統合システムのテスト完了")
