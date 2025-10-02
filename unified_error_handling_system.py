#!/usr/bin/env python3
"""
統合エラーハンドリングシステム
すべてのエラーハンドリング機能を統合した単一システム

機能:
- 統一されたエラー分類とハンドリング
- 構造化ログ出力
- エラー復旧機能
- パフォーマンス監視
- セキュリティ監査
"""

import logging
import os
import sys
import traceback
import json
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union, Callable
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import functools


class ErrorSeverity(Enum):
    """エラー重要度"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """エラーカテゴリ"""

    API = "API"
    DATA = "DATA"
    MODEL = "MODEL"
    FILE = "FILE"
    NETWORK = "NETWORK"
    AUTHENTICATION = "AUTHENTICATION"
    VALIDATION = "VALIDATION"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    SYSTEM = "SYSTEM"


class LogLevel(Enum):
    """ログレベル"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ErrorContext:
    """エラーコンテキスト情報"""

    operation: str
    module: str
    function: str
    line_number: int
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class ErrorInfo:
    """エラー情報"""

    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: ErrorContext
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data["context"] = self.context.to_dict()
        return data


class UnifiedErrorHandlingSystem:
    """統合エラーハンドリングシステム"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初期化

        Args:
            config: 設定辞書
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        self.error_count = 0
        self.error_history: List[ErrorInfo] = []
        self.recovery_strategies: Dict[ErrorCategory, List[Callable]] = {}
        self.performance_metrics = {
            "total_errors": 0,
            "recovered_errors": 0,
            "critical_errors": 0,
            "average_recovery_time": 0.0,
        }

        # ログディレクトリの作成
        self._ensure_log_directory()

        # デフォルト復旧戦略の設定
        self._setup_default_recovery_strategies()

    def _setup_logger(self) -> logging.Logger:
        """ロガーの設定"""
        logger = logging.getLogger("UnifiedErrorHandling")
        logger.setLevel(logging.DEBUG)

        # 既存のハンドラーをクリア
        logger.handlers.clear()

        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # ログディレクトリの作成
        import os
        os.makedirs("logs", exist_ok=True)
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(
            "logs/unified_error_handling.log", encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def _ensure_log_directory(self):
        """ログディレクトリの作成"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

    def _setup_default_recovery_strategies(self):
        """デフォルト復旧戦略の設定"""
        self.recovery_strategies = {
            ErrorCategory.API: [self._retry_api_request, self._fallback_to_cached_data],
            ErrorCategory.NETWORK: [self._retry_connection, self._use_offline_mode],
            ErrorCategory.DATA: [self._clean_data, self._use_default_values],
            ErrorCategory.FILE: [self._create_backup, self._use_alternative_path],
        }

    def log_error(
        self,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        operation: str = "不明な操作",
        module: str = "不明なモジュール",
        function: str = "不明な関数",
    ) -> ErrorInfo:
        """
        エラーのログ記録

        Args:
            error: 発生したエラー
            category: エラーカテゴリ
            severity: エラー重要度
            context: 追加コンテキスト情報
            operation: 操作名
            module: モジュール名
            function: 関数名

        Returns:
            ErrorInfo: エラー情報
        """
        # スタックトレースの取得
        stack_trace = traceback.format_exc()

        # コンテキスト情報の作成
        error_context = ErrorContext(
            operation=operation,
            module=module,
            function=function,
            line_number=sys._getframe(1).f_lineno,
            timestamp=datetime.now(timezone.utc),
            additional_data=context or {},
        )

        # エラー情報の作成
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            error_message=str(error),
            category=category,
            severity=severity,
            context=error_context,
            stack_trace=stack_trace,
        )

        # ログ出力
        self._log_error_info(error_info)

        # エラー履歴の記録
        self.error_history.append(error_info)
        self.error_count += 1
        self.performance_metrics["total_errors"] += 1

        if severity == ErrorSeverity.CRITICAL:
            self.performance_metrics["critical_errors"] += 1

        # 復旧の試行
        if self._attempt_recovery(error_info):
            error_info.recovery_attempted = True
            error_info.recovery_successful = True
            self.performance_metrics["recovered_errors"] += 1

        return error_info

    def _log_error_info(self, error_info: ErrorInfo):
        """エラー情報のログ出力"""
        log_data = {
            "error_info": error_info.to_dict(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd(),
            },
        }

        # 重要度に応じたログレベル
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error_info.error_message}")
            self.logger.critical(
                f"Error Details: {json.dumps(log_data, ensure_ascii=False, indent=2, default=str)}"
            )
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY ERROR: {error_info.error_message}")
            self.logger.error(
                f"Error Details: {json.dumps(log_data, ensure_ascii=False, indent=2, default=str)}"
            )
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY ERROR: {error_info.error_message}")
            self.logger.warning(
                f"Error Details: {json.dumps(log_data, ensure_ascii=False, indent=2, default=str)}"
            )
        else:
            self.logger.info(f"LOW SEVERITY ERROR: {error_info.error_message}")
            self.logger.info(
                f"Error Details: {json.dumps(log_data, ensure_ascii=False, indent=2, default=str)}"
            )

    def _attempt_recovery(self, error_info: ErrorInfo) -> bool:
        """エラー復旧の試行"""
        recovery_strategies = self.recovery_strategies.get(error_info.category, [])

        for strategy in recovery_strategies:
            try:
                if strategy(error_info):
                    self.logger.info(f"✅ エラー復旧成功: {error_info.error_type}")
                    return True
            except Exception as recovery_error:
                self.logger.warning(f"⚠️ 復旧戦略失敗: {recovery_error}")

        return False

    def _retry_api_request(self, error_info: ErrorInfo) -> bool:
        """APIリクエストの再試行"""
        # API復旧ロジック
        return False  # 実装は呼び出し元に委ねる

    def _fallback_to_cached_data(self, error_info: ErrorInfo) -> bool:
        """キャッシュデータへのフォールバック"""
        # キャッシュ復旧ロジック
        return False  # 実装は呼び出し元に委ねる

    def _retry_connection(self, error_info: ErrorInfo) -> bool:
        """接続の再試行"""
        # 接続復旧ロジック
        return False  # 実装は呼び出し元に委ねる

    def _use_offline_mode(self, error_info: ErrorInfo) -> bool:
        """オフラインモードの使用"""
        # オフライン復旧ロジック
        return False  # 実装は呼び出し元に委ねる

    def _clean_data(self, error_info: ErrorInfo) -> bool:
        """データのクリーニング"""
        # データクリーニングロジック
        return False  # 実装は呼び出し元に委ねる

    def _use_default_values(self, error_info: ErrorInfo) -> bool:
        """デフォルト値の使用"""
        # デフォルト値復旧ロジック
        return False  # 実装は呼び出し元に委ねる

    def _create_backup(self, error_info: ErrorInfo) -> bool:
        """バックアップの作成"""
        # バックアップ作成ロジック
        return False  # 実装は呼び出し元に委ねる

    def _use_alternative_path(self, error_info: ErrorInfo) -> bool:
        """代替パスの使用"""
        # 代替パス復旧ロジック
        return False  # 実装は呼び出し元に委ねる

    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計情報の取得"""
        return {
            "total_errors": self.error_count,
            "error_history_count": len(self.error_history),
            "performance_metrics": self.performance_metrics,
            "errors_by_category": self._get_errors_by_category(),
            "errors_by_severity": self._get_errors_by_severity(),
        }

    def _get_errors_by_category(self) -> Dict[str, int]:
        """カテゴリ別エラー数"""
        category_counts = {}
        for error_info in self.error_history:
            category = error_info.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts

    def _get_errors_by_severity(self) -> Dict[str, int]:
        """重要度別エラー数"""
        severity_counts = {}
        for error_info in self.error_history:
            severity = error_info.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts

    def clear_error_history(self):
        """エラー履歴のクリア"""
        self.error_history.clear()
        self.error_count = 0
        self.performance_metrics = {
            "total_errors": 0,
            "recovered_errors": 0,
            "critical_errors": 0,
            "average_recovery_time": 0.0,
        }

    def export_error_report(self, file_path: str):
        """エラーレポートのエクスポート"""
        report_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": self.get_error_statistics(),
            "error_history": [error.to_dict() for error in self.error_history],
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)

        self.logger.info(f"📊 エラーレポートをエクスポートしました: {file_path}")


# グローバルインスタンス
_unified_error_handler = None


def get_unified_error_handler(
    config: Optional[Dict[str, Any]] = None,
) -> UnifiedErrorHandlingSystem:
    """
    統合エラーハンドリングシステムの取得

    Args:
        config: 設定辞書

    Returns:
        UnifiedErrorHandlingSystem: 統合エラーハンドリングシステム
    """
    global _unified_error_handler

    if _unified_error_handler is None:
        _unified_error_handler = UnifiedErrorHandlingSystem(config)

    return _unified_error_handler


def error_handler(
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    operation: str = "不明な操作",
):
    """
    エラーハンドリングデコレータ

    Args:
        category: エラーカテゴリ
        severity: エラー重要度
        operation: 操作名
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = get_unified_error_handler()
                error_handler.log_error(
                    error=e,
                    category=category,
                    severity=severity,
                    operation=operation,
                    module=func.__module__,
                    function=func.__name__,
                )
                raise

        return wrapper

    return decorator


@contextmanager
def error_context(
    operation: str,
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
):
    """
    エラーコンテキストマネージャー

    Args:
        operation: 操作名
        category: エラーカテゴリ
        severity: エラー重要度
    """
    error_handler = get_unified_error_handler()
    try:
        yield error_handler
    except Exception as e:
        error_handler.log_error(
            error=e, category=category, severity=severity, operation=operation
        )
        raise


# 便利な関数
def log_api_error(error: Exception, endpoint: str, status_code: Optional[int] = None):
    """APIエラーのログ記録"""
    error_handler = get_unified_error_handler()
    context = {"endpoint": endpoint}
    if status_code:
        context["status_code"] = status_code

    error_handler.log_error(
        error=error,
        category=ErrorCategory.API,
        severity=ErrorSeverity.HIGH,
        context=context,
        operation=f"API呼び出し: {endpoint}",
    )


def log_data_error(
    error: Exception, data_type: str, data_shape: Optional[tuple] = None
):
    """データエラーのログ記録"""
    error_handler = get_unified_error_handler()
    context = {"data_type": data_type}
    if data_shape:
        context["data_shape"] = data_shape

    error_handler.log_error(
        error=error,
        category=ErrorCategory.DATA,
        severity=ErrorSeverity.MEDIUM,
        context=context,
        operation=f"データ処理: {data_type}",
    )


def log_model_error(error: Exception, model_name: str, operation_type: str):
    """モデルエラーのログ記録"""
    error_handler = get_unified_error_handler()
    context = {"model_name": model_name, "operation_type": operation_type}

    error_handler.log_error(
        error=error,
        category=ErrorCategory.MODEL,
        severity=ErrorSeverity.HIGH,
        context=context,
        operation=f"モデル{operation_type}: {model_name}",
    )


def log_file_error(error: Exception, file_path: str, operation: str):
    """ファイルエラーのログ記録"""
    error_handler = get_unified_error_handler()
    context = {"file_path": file_path, "file_exists": os.path.exists(file_path)}

    error_handler.log_error(
        error=error,
        category=ErrorCategory.FILE,
        severity=ErrorSeverity.MEDIUM,
        context=context,
        operation=f"ファイル{operation}: {file_path}",
    )


if __name__ == "__main__":
    # テスト実行
    error_handler = get_unified_error_handler()

    # テストエラーの生成
    try:
        raise ValueError("テストエラー")
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.LOW,
            operation="テスト実行",
        )

    # 統計情報の表示
    stats = error_handler.get_error_statistics()
    print("エラー統計情報:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
