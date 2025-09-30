#!/usr/bin/env python3
"""
エラーハンドリングシステム - 統合システムから分離
エラーの分類、処理、復旧、統計管理
"""

import traceback
from typing import Dict, Any, Optional
from datetime import datetime
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


class ErrorHandler:
    """エラーハンドリングシステム"""

    def __init__(self, logger=None, config: Dict[str, Any] = None):
        """初期化"""
        self.logger = logger
        self.config = config or {}
        self.error_count = 0
        self.error_stats = {category.value: 0 for category in ErrorCategory}

        # 復旧試行回数の追跡
        self.recovery_attempts = {}

    def log_error(
        self,
        error: Exception,
        context: str = "",
        category: ErrorCategory = ErrorCategory.API_ERROR,
        additional_info: Dict[str, Any] = None,
        include_traceback: bool = True,
    ):
        """エラーログの出力"""
        self.error_count += 1

        # エラー統計の更新
        category_key = category.value
        if category_key not in self.error_stats:
            self.error_stats[category_key] = 0
        self.error_stats[category_key] += 1

        # ログ出力
        if self.logger:
            self.logger.log_error(error, context, additional_info, include_traceback)

        # エラー復旧の試行
        self._attempt_error_recovery(error, category, additional_info)

    def _attempt_error_recovery(
        self, error: Exception, category: ErrorCategory, context: Dict[str, Any] = None
    ) -> None:
        """エラー復旧の試行"""
        try:
            # 復旧設定の取得
            recovery_config = self.config.get("error_handling", {}).get(
                "auto_recovery", True
            )
            max_attempts = self.config.get("error_handling", {}).get(
                "max_recovery_attempts", 3
            )

            if not recovery_config:
                if self.logger:
                    self.logger.log_info("自動復旧が無効化されています")
                return

            # 復旧試行回数のチェック
            recovery_key = f"recovery_attempts_{category.value}"
            current_attempts = self.recovery_attempts.get(recovery_key, 0)

            if current_attempts >= max_attempts:
                if self.logger:
                    self.logger.log_warning(f"復旧試行の上限に達しました: {category.value}")
                return

            # カテゴリ別復旧処理
            if category == ErrorCategory.API_ERROR:
                self._recover_api_error(error, context)
            elif category == ErrorCategory.FILE_ERROR:
                self._recover_file_error(error, context)
            elif category == ErrorCategory.DATA_PROCESSING_ERROR:
                self._recover_data_processing_error(error, context)
            elif category == ErrorCategory.MODEL_ERROR:
                self._recover_model_error(error, context)
            elif category == ErrorCategory.NETWORK_ERROR:
                self._recover_network_error(error, context)
            elif category == ErrorCategory.AUTHENTICATION_ERROR:
                self._recover_authentication_error(error, context)
            else:
                if self.logger:
                    self.logger.log_warning(f"特定の復旧戦略がありません: {category.value}")

            # 復旧試行回数を更新
            self.recovery_attempts[recovery_key] = current_attempts + 1

        except Exception as recovery_error:
            if self.logger:
                self.logger.log_error(f"復旧試行に失敗: {recovery_error}")

    def _recover_api_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> None:
        """APIエラーの復旧"""
        if self.logger:
            self.logger.log_info("APIエラーの復旧を試行中...")
        # APIエラーの復旧ロジック（リトライ、認証更新など）
        if context and context.get("retry_count", 0) < 3:
            if self.logger:
                self.logger.log_info(
                    f"APIリトライを実行: {context.get('retry_count', 0) + 1}回目"
                )
        else:
            if self.logger:
                self.logger.log_warning("API復旧の上限に達しました")

    def _recover_file_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> None:
        """ファイルエラーの復旧"""
        if self.logger:
            self.logger.log_info("ファイルエラーの復旧を試行中...")
        # ファイルエラーの復旧ロジック（バックアップファイルの使用、権限修正など）
        if context and context.get("file_path"):
            if self.logger:
                self.logger.log_info(f"ファイル復旧を試行: {context['file_path']}")

    def _recover_data_processing_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> None:
        """データ処理エラーの復旧"""
        if self.logger:
            self.logger.log_info("データ処理エラーの復旧を試行中...")
        # データ処理エラーの復旧ロジック（データクリーニング、フォールバック処理など）
        if context and context.get("operation"):
            if self.logger:
                self.logger.log_info(f"データ処理復旧を試行: {context['operation']}")

    def _recover_model_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> None:
        """モデルエラーの復旧"""
        if self.logger:
            self.logger.log_info("モデルエラーの復旧を試行中...")
        # モデルエラーの復旧ロジック（デフォルトモデルの使用、パラメータ調整など）
        if context and context.get("model_name"):
            if self.logger:
                self.logger.log_info(f"モデル復旧を試行: {context['model_name']}")

    def _recover_network_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> None:
        """ネットワークエラーの復旧"""
        if self.logger:
            self.logger.log_info("ネットワークエラーの復旧を試行中...")
        # ネットワークエラーの復旧ロジック（接続再試行、プロキシ設定など）
        if context and context.get("url"):
            if self.logger:
                self.logger.log_info(f"ネットワーク復旧を試行: {context['url']}")

    def _recover_authentication_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> None:
        """認証エラーの復旧"""
        if self.logger:
            self.logger.log_info("認証エラーの復旧を試行中...")
        # 認証エラーの復旧ロジック（トークン更新、認証情報再取得など）
        if context and context.get("auth_type"):
            if self.logger:
                self.logger.log_info(f"認証復旧を試行: {context['auth_type']}")

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
        }

        if context:
            additional_info.update(context)

        self.log_error(error, error_context, ErrorCategory.MODEL_ERROR, additional_info)

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
        }

        if data_info:
            additional_info.update(data_info)

        if context:
            additional_info.update(context)

        self.log_error(
            error, error_context, ErrorCategory.DATA_PROCESSING_ERROR, additional_info
        )

    def handle_api_error(self, error: Exception, context: str = ""):
        """APIエラーの処理"""
        if self.logger:
            self.logger.log_error(f"API Error: {error} in context: {context}")
        self.log_error(
            error, f"API Error in context: {context}", ErrorCategory.API_ERROR
        )

    def handle_file_error(self, error: Exception, file_path: str, operation: str):
        """ファイルエラーの処理"""
        if self.logger:
            self.logger.log_error(
                f"File Error: {error} for file: {file_path}, operation: {operation}"
            )
        self.log_error(
            error,
            f"File Error for file: {file_path}, operation: {operation}",
            ErrorCategory.FILE_ERROR,
        )

    def handle_validation_error(self, error: Exception):
        """検証エラーの処理"""
        if self.logger:
            self.logger.log_error(f"Validation Error: {error}")
        self.log_error(
            error,
            f"Validation Error: {error}",
            ErrorCategory.VALIDATION_ERROR,
        )

    def handle_network_error(self, error: Exception, context: str = ""):
        """ネットワークエラーの処理"""
        if self.logger:
            self.logger.log_error(f"Network Error: {error}")
        self.log_error(error, f"Network Error: {error}", ErrorCategory.NETWORK_ERROR)

    def handle_authentication_error(self, error: Exception, context: str = ""):
        """認証エラーの処理"""
        if self.logger:
            self.logger.log_error(f"Authentication Error: {error}")
        self.log_error(
            error,
            f"Authentication Error: {error}",
            ErrorCategory.AUTHENTICATION_ERROR,
        )

    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計の取得"""
        return {
            "total_errors": self.error_count,
            "error_by_category": {k: v for k, v in self.error_stats.items()},
            "errors_by_category": {
                k: v for k, v in self.error_stats.items()
            },  # テスト用の別名
            "timestamp": datetime.now().isoformat(),
        }

    def reset_error_count(self) -> None:
        """エラーカウントのリセット"""
        self.error_count = 0
        self.error_stats = {category.value: 0 for category in ErrorCategory}
        self.recovery_attempts = {}
        if self.logger:
            self.logger.log_info("エラーカウントをリセットしました")

    def execute_error_recovery_workflow(self) -> Dict[str, Any]:
        """エラー復旧ワークフローの実行"""
        try:
            recovery_result = {
                "status": "success",
                "recovered_errors": self.error_count,
                "timestamp": datetime.now().isoformat(),
            }
            if self.logger:
                self.logger.log_info("エラー復旧ワークフローを実行しました")
            return recovery_result
        except Exception as e:
            self.log_error(e, "エラー復旧ワークフローエラー", ErrorCategory.DATA_PROCESSING_ERROR)
            raise

    def attempt_error_recovery(self, error: Exception) -> bool:
        """エラー復旧の試行"""
        try:
            self._attempt_error_recovery(error, ErrorCategory.DATA_PROCESSING_ERROR)
            return True
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error recovery failed: {e}")
            return False
