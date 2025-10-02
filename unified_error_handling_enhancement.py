#!/usr/bin/env python3
"""
統合エラーハンドリングシステムの完全適用
全モジュールでの統一されたエラー処理を実装
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import functools
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """エラーカテゴリ"""
    API_ERROR = "api_error"
    DATA_ERROR = "data_error"
    MODEL_ERROR = "model_error"
    FILE_ERROR = "file_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    SECURITY_ERROR = "security_error"
    PERFORMANCE_ERROR = "performance_error"
    SYSTEM_ERROR = "system_error"


class ErrorSeverity(Enum):
    """エラー重要度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """エラー情報"""
    timestamp: datetime
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    module: str
    function: str
    line_number: int
    stack_trace: str
    context: Dict[str, Any]
    recovery_attempted: bool = False
    recovery_successful: bool = False


class UnifiedErrorHandlingSystem:
    """統合エラーハンドリングシステム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.error_history = []
        self.error_stats = {category.value: 0 for category in ErrorCategory}
        self.recovery_strategies = {}
        self.performance_metrics = {
            "total_errors": 0,
            "critical_errors": 0,
            "recovered_errors": 0,
            "recovery_success_rate": 0.0
        }
        
        # 設定の初期化
        self.enable_recovery = self.config.get("enable_recovery", True)
        self.max_error_history = self.config.get("max_error_history", 1000)
        self.enable_performance_monitoring = self.config.get("enable_performance_monitoring", True)
        
        # 復旧戦略の初期化
        self._initialize_recovery_strategies()
        
        logger.info("🔧 統合エラーハンドリングシステムを初期化しました")

    def _initialize_recovery_strategies(self):
        """復旧戦略の初期化"""
        self.recovery_strategies = {
            ErrorCategory.API_ERROR: self._recover_api_error,
            ErrorCategory.DATA_ERROR: self._recover_data_error,
            ErrorCategory.MODEL_ERROR: self._recover_model_error,
            ErrorCategory.FILE_ERROR: self._recover_file_error,
            ErrorCategory.NETWORK_ERROR: self._recover_network_error,
            ErrorCategory.AUTHENTICATION_ERROR: self._recover_authentication_error,
            ErrorCategory.VALIDATION_ERROR: self._recover_validation_error,
            ErrorCategory.SECURITY_ERROR: self._recover_security_error,
            ErrorCategory.PERFORMANCE_ERROR: self._recover_performance_error,
            ErrorCategory.SYSTEM_ERROR: self._recover_system_error,
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
        """エラーのログ記録"""
        # スタックトレースの取得
        stack_trace = traceback.format_exc()
        
        # エラー情報の作成
        error_info = ErrorInfo(
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            error_message=str(error),
            category=category,
            severity=severity,
            module=module,
            function=function,
            line_number=sys._getframe(1).f_lineno,
            stack_trace=stack_trace,
            context=context or {},
            recovery_attempted=False,
            recovery_successful=False
        )
        
        # エラーログの出力
        self._log_error_info(error_info)
        
        # エラー履歴の記録
        self.error_history.append(error_info)
        self.error_stats[category.value] += 1
        self.performance_metrics["total_errors"] += 1
        
        if severity == ErrorSeverity.CRITICAL:
            self.performance_metrics["critical_errors"] += 1
        
        # 復旧の試行
        if self.enable_recovery:
            if self._attempt_recovery(error_info):
                error_info.recovery_attempted = True
                error_info.recovery_successful = True
                self.performance_metrics["recovered_errors"] += 1
        
        # 履歴の制限
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
        
        return error_info

    def _log_error_info(self, error_info: ErrorInfo):
        """エラー情報のログ出力"""
        log_message = (
            f"❌ エラー [{error_info.category.value.upper()}] "
            f"[{error_info.severity.value.upper()}] "
            f"{error_info.module}.{error_info.function}: "
            f"{error_info.error_message}"
        )
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # デバッグ情報の出力
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"スタックトレース: {error_info.stack_trace}")
            logger.debug(f"コンテキスト: {error_info.context}")

    def _attempt_recovery(self, error_info: ErrorInfo) -> bool:
        """エラー復旧の試行"""
        try:
            recovery_function = self.recovery_strategies.get(error_info.category)
            if recovery_function:
                return recovery_function(error_info)
            return False
        except Exception as e:
            logger.error(f"復旧処理中にエラーが発生: {e}")
            return False

    def _recover_api_error(self, error_info: ErrorInfo) -> bool:
        """APIエラーの復旧"""
        logger.info("🔄 APIエラーの復旧を試行中...")
        # リトライロジックの実装
        return False  # 実装例

    def _recover_data_error(self, error_info: ErrorInfo) -> bool:
        """データエラーの復旧"""
        logger.info("🔄 データエラーの復旧を試行中...")
        # データクリーニングの実装
        return False  # 実装例

    def _recover_model_error(self, error_info: ErrorInfo) -> bool:
        """モデルエラーの復旧"""
        logger.info("🔄 モデルエラーの復旧を試行中...")
        # モデル再初期化の実装
        return False  # 実装例

    def _recover_file_error(self, error_info: ErrorInfo) -> bool:
        """ファイルエラーの復旧"""
        logger.info("🔄 ファイルエラーの復旧を試行中...")
        # ファイル権限修正の実装
        return False  # 実装例

    def _recover_network_error(self, error_info: ErrorInfo) -> bool:
        """ネットワークエラーの復旧"""
        logger.info("🔄 ネットワークエラーの復旧を試行中...")
        # 接続再試行の実装
        return False  # 実装例

    def _recover_authentication_error(self, error_info: ErrorInfo) -> bool:
        """認証エラーの復旧"""
        logger.info("🔄 認証エラーの復旧を試行中...")
        # 認証情報更新の実装
        return False  # 実装例

    def _recover_validation_error(self, error_info: ErrorInfo) -> bool:
        """検証エラーの復旧"""
        logger.info("🔄 検証エラーの復旧を試行中...")
        # データ検証の再実行
        return False  # 実装例

    def _recover_security_error(self, error_info: ErrorInfo) -> bool:
        """セキュリティエラーの復旧"""
        logger.info("🔄 セキュリティエラーの復旧を試行中...")
        # セキュリティ設定の更新
        return False  # 実装例

    def _recover_performance_error(self, error_info: ErrorInfo) -> bool:
        """パフォーマンスエラーの復旧"""
        logger.info("🔄 パフォーマンスエラーの復旧を試行中...")
        # リソース最適化の実装
        return False  # 実装例

    def _recover_system_error(self, error_info: ErrorInfo) -> bool:
        """システムエラーの復旧"""
        logger.info("🔄 システムエラーの復旧を試行中...")
        # システム再起動の実装
        return False  # 実装例

    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計の取得"""
        total_errors = self.performance_metrics["total_errors"]
        recovered_errors = self.performance_metrics["recovered_errors"]
        
        recovery_success_rate = (
            recovered_errors / total_errors if total_errors > 0 else 0.0
        )
        
        return {
            "total_errors": total_errors,
            "critical_errors": self.performance_metrics["critical_errors"],
            "recovered_errors": recovered_errors,
            "recovery_success_rate": recovery_success_rate,
            "error_stats_by_category": self.error_stats,
            "recent_errors": len(self.error_history)
        }

    def export_error_report(self, file_path: str) -> bool:
        """エラーレポートのエクスポート"""
        try:
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "statistics": self.get_error_statistics(),
                "recent_errors": [
                    {
                        "timestamp": error.timestamp.isoformat(),
                        "error_type": error.error_type,
                        "error_message": error.error_message,
                        "category": error.category.value,
                        "severity": error.severity.value,
                        "module": error.module,
                        "function": error.function,
                        "recovery_attempted": error.recovery_attempted,
                        "recovery_successful": error.recovery_successful
                    }
                    for error in self.error_history[-100:]  # 直近100件
                ]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📊 エラーレポートをエクスポートしました: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ エラーレポートのエクスポートに失敗: {e}")
            return False

    def clear_error_history(self):
        """エラー履歴のクリア"""
        self.error_history.clear()
        self.error_stats = {category.value: 0 for category in ErrorCategory}
        self.performance_metrics = {
            "total_errors": 0,
            "critical_errors": 0,
            "recovered_errors": 0,
            "recovery_success_rate": 0.0
        }
        logger.info("🧹 エラー履歴をクリアしました")


# デコレータとコンテキストマネージャー
def error_handler(
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    operation: str = "操作"
):
    """エラーハンドリングデコレータ"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 統合エラーハンドリングシステムの取得
                error_system = get_unified_error_handler()
                error_system.log_error(
                    error=e,
                    category=category,
                    severity=severity,
                    operation=operation,
                    module=func.__module__,
                    function=func.__name__
                )
                raise
        return wrapper
    return decorator


@contextmanager
def error_context(
    operation: str,
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
):
    """エラーコンテキストマネージャー"""
    error_system = get_unified_error_handler()
    try:
        yield error_system
    except Exception as e:
        error_system.log_error(
            error=e,
            category=category,
            severity=severity,
            operation=operation
        )
        raise


# グローバルインスタンス
_error_handler_instance = None


def get_unified_error_handler() -> UnifiedErrorHandlingSystem:
    """統合エラーハンドリングシステムの取得"""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = UnifiedErrorHandlingSystem()
    return _error_handler_instance


# 便利関数
def log_api_error(error: Exception, operation: str = "API操作", **kwargs):
    """APIエラーのログ"""
    error_system = get_unified_error_handler()
    return error_system.log_error(
        error=error,
        category=ErrorCategory.API_ERROR,
        severity=ErrorSeverity.HIGH,
        operation=operation,
        **kwargs
    )


def log_data_error(error: Exception, operation: str = "データ操作", **kwargs):
    """データエラーのログ"""
    error_system = get_unified_error_handler()
    return error_system.log_error(
        error=error,
        category=ErrorCategory.DATA_ERROR,
        severity=ErrorSeverity.MEDIUM,
        operation=operation,
        **kwargs
    )


def log_model_error(error: Exception, operation: str = "モデル操作", **kwargs):
    """モデルエラーのログ"""
    error_system = get_unified_error_handler()
    return error_system.log_error(
        error=error,
        category=ErrorCategory.MODEL_ERROR,
        severity=ErrorSeverity.HIGH,
        operation=operation,
        **kwargs
    )


def log_file_error(error: Exception, operation: str = "ファイル操作", **kwargs):
    """ファイルエラーのログ"""
    error_system = get_unified_error_handler()
    return error_system.log_error(
        error=error,
        category=ErrorCategory.FILE_ERROR,
        severity=ErrorSeverity.MEDIUM,
        operation=operation,
        **kwargs
    )
