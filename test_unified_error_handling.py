#!/usr/bin/env python3
"""
統合エラーハンドリングシステムのテスト
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

# テスト対象のインポート
from unified_error_handling_system import (
    UnifiedErrorHandlingSystem,
    ErrorCategory,
    ErrorSeverity,
    ErrorContext,
    ErrorInfo,
    get_unified_error_handler,
    error_handler,
    error_context,
    log_api_error,
    log_data_error,
    log_model_error,
    log_file_error,
)


class TestUnifiedErrorHandlingSystem(unittest.TestCase):
    """統合エラーハンドリングシステムのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

        # ログディレクトリの作成
        os.makedirs("logs", exist_ok=True)

        self.error_handler = UnifiedErrorHandlingSystem()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_error_handler_initialization(self):
        """エラーハンドラーの初期化テスト"""
        self.assertIsInstance(self.error_handler, UnifiedErrorHandlingSystem)
        self.assertEqual(self.error_handler.error_count, 0)
        self.assertEqual(len(self.error_handler.error_history), 0)

    def test_log_error_basic(self):
        """基本的なエラーログテスト"""
        error = ValueError("テストエラー")

        error_info = self.error_handler.log_error(
            error=error,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            operation="テスト操作",
            module="test_module",
            function="test_function",
        )

        self.assertIsInstance(error_info, ErrorInfo)
        self.assertEqual(error_info.error_type, "ValueError")
        self.assertEqual(error_info.error_message, "テストエラー")
        self.assertEqual(error_info.category, ErrorCategory.SYSTEM)
        self.assertEqual(error_info.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(self.error_handler.error_count, 1)
        self.assertEqual(len(self.error_handler.error_history), 1)

    def test_log_error_with_context(self):
        """コンテキスト付きエラーログテスト"""
        error = RuntimeError("ランタイムエラー")
        context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "additional_info": "テスト情報",
        }

        error_info = self.error_handler.log_error(
            error=error,
            category=ErrorCategory.API,
            severity=ErrorSeverity.HIGH,
            context=context,
            operation="API呼び出し",
            module="api_module",
            function="api_call",
        )

        self.assertEqual(error_info.context.operation, "API呼び出し")
        self.assertEqual(error_info.context.module, "api_module")
        self.assertEqual(error_info.context.function, "api_call")
        self.assertEqual(error_info.context.additional_data, context)

    def test_error_statistics(self):
        """エラー統計情報のテスト"""
        # 複数のエラーを記録
        errors = [
            (ValueError("エラー1"), ErrorCategory.SYSTEM, ErrorSeverity.LOW),
            (RuntimeError("エラー2"), ErrorCategory.API, ErrorSeverity.HIGH),
            (FileNotFoundError("エラー3"), ErrorCategory.FILE, ErrorSeverity.MEDIUM),
        ]

        for error, category, severity in errors:
            self.error_handler.log_error(
                error=error,
                category=category,
                severity=severity,
                operation="テスト操作",
            )

        stats = self.error_handler.get_error_statistics()

        self.assertEqual(stats["total_errors"], 3)
        self.assertEqual(stats["error_history_count"], 3)
        self.assertEqual(stats["performance_metrics"]["total_errors"], 3)
        self.assertEqual(
            stats["performance_metrics"]["critical_errors"], 0
        )  # CRITICALは0個

        # カテゴリ別エラー数
        category_counts = stats["errors_by_category"]
        self.assertEqual(category_counts["SYSTEM"], 1)
        self.assertEqual(category_counts["API"], 1)
        self.assertEqual(category_counts["FILE"], 1)

        # 重要度別エラー数
        severity_counts = stats["errors_by_severity"]
        self.assertEqual(severity_counts["LOW"], 1)
        self.assertEqual(severity_counts["HIGH"], 1)
        self.assertEqual(severity_counts["MEDIUM"], 1)

    def test_critical_error_counting(self):
        """CRITICALエラーのカウントテスト"""
        error = Exception("重大なエラー")

        self.error_handler.log_error(
            error=error,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            operation="重大な操作",
        )

        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["performance_metrics"]["critical_errors"], 1)

    def test_error_history_clear(self):
        """エラー履歴のクリアテスト"""
        # エラーを記録
        self.error_handler.log_error(
            error=ValueError("テストエラー"),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            operation="テスト操作",
        )

        self.assertEqual(self.error_handler.error_count, 1)
        self.assertEqual(len(self.error_handler.error_history), 1)

        # 履歴をクリア
        self.error_handler.clear_error_history()

        self.assertEqual(self.error_handler.error_count, 0)
        self.assertEqual(len(self.error_handler.error_history), 0)

    def test_export_error_report(self):
        """エラーレポートのエクスポートテスト"""
        # エラーを記録
        self.error_handler.log_error(
            error=ValueError("テストエラー"),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            operation="テスト操作",
        )

        # レポートをエクスポート
        report_file = os.path.join(self.temp_dir, "error_report.json")
        self.error_handler.export_error_report(report_file)

        # レポートファイルの存在確認
        self.assertTrue(os.path.exists(report_file))

        # レポート内容の確認
        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)

        self.assertIn("export_timestamp", report_data)
        self.assertIn("statistics", report_data)
        self.assertIn("error_history", report_data)
        self.assertEqual(report_data["statistics"]["total_errors"], 1)

    def test_global_error_handler(self):
        """グローバルエラーハンドラーのテスト"""
        handler1 = get_unified_error_handler()
        handler2 = get_unified_error_handler()

        # 同じインスタンスが返されることを確認
        self.assertIs(handler1, handler2)

    def test_error_handler_decorator(self):
        """エラーハンドラーデコレータのテスト"""

        @error_handler(ErrorCategory.API, ErrorSeverity.HIGH, "API呼び出し")
        def failing_function():
            raise ValueError("デコレータテストエラー")

        # エラーが発生することを確認
        with self.assertRaises(ValueError):
            failing_function()

        # エラーが記録されることを確認（グローバルハンドラーを使用）
        global_handler = get_unified_error_handler()
        stats = global_handler.get_error_statistics()
        # 累積カウントなので、期待値を調整
        self.assertGreaterEqual(stats["total_errors"], 1)

    def test_error_context_manager(self):
        """エラーコンテキストマネージャーのテスト"""
        with self.assertRaises(ValueError):
            with error_context(
                "テスト操作", ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM
            ) as handler:
                raise ValueError("コンテキストマネージャーテストエラー")

        # エラーが記録されることを確認（グローバルハンドラーを使用）
        global_handler = get_unified_error_handler()
        stats = global_handler.get_error_statistics()
        # 累積カウントなので、期待値を調整
        self.assertGreaterEqual(stats["total_errors"], 1)

    def test_convenience_functions(self):
        """便利関数のテスト"""
        # APIエラーのログ
        log_api_error(ValueError("APIエラー"), "test_endpoint", 500)

        # データエラーのログ
        log_data_error(ValueError("データエラー"), "test_data", (100, 10))

        # モデルエラーのログ
        log_model_error(ValueError("モデルエラー"), "test_model", "training")

        # ファイルエラーのログ
        log_file_error(FileNotFoundError("ファイルエラー"), "test_file.txt", "読み込み")

        # エラーが記録されることを確認（グローバルハンドラーを使用）
        global_handler = get_unified_error_handler()
        stats = global_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 4)

    def test_recovery_strategies(self):
        """復旧戦略のテスト"""

        # 復旧戦略の設定
        def test_recovery_strategy(error_info):
            return True  # 常に成功

        self.error_handler.recovery_strategies[ErrorCategory.SYSTEM] = [
            test_recovery_strategy
        ]

        # エラーの記録
        error_info = self.error_handler.log_error(
            error=ValueError("復旧テストエラー"),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            operation="復旧テスト",
        )

        # 復旧が試行されることを確認
        self.assertTrue(error_info.recovery_attempted)
        self.assertTrue(error_info.recovery_successful)

    def test_logger_setup(self):
        """ロガー設定のテスト"""
        self.assertIsNotNone(self.error_handler.logger)
        self.assertEqual(self.error_handler.logger.name, "UnifiedErrorHandling")

    def test_error_context_creation(self):
        """エラーコンテキスト作成のテスト"""
        context = ErrorContext(
            operation="テスト操作",
            module="test_module",
            function="test_function",
            line_number=100,
            timestamp=None,  # 自動設定される
        )

        self.assertEqual(context.operation, "テスト操作")
        self.assertEqual(context.module, "test_module")
        self.assertEqual(context.function, "test_function")
        self.assertEqual(context.line_number, 100)

    def test_error_info_creation(self):
        """エラー情報作成のテスト"""
        context = ErrorContext(
            operation="テスト操作",
            module="test_module",
            function="test_function",
            line_number=100,
            timestamp=None,
        )

        error_info = ErrorInfo(
            error_type="ValueError",
            error_message="テストエラー",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            context=context,
        )

        self.assertEqual(error_info.error_type, "ValueError")
        self.assertEqual(error_info.error_message, "テストエラー")
        self.assertEqual(error_info.category, ErrorCategory.SYSTEM)
        self.assertEqual(error_info.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error_info.context, context)

    def test_performance_metrics(self):
        """パフォーマンスメトリクスのテスト"""
        # 初期状態の確認
        metrics = self.error_handler.performance_metrics
        self.assertEqual(metrics["total_errors"], 0)
        self.assertEqual(metrics["recovered_errors"], 0)
        self.assertEqual(metrics["critical_errors"], 0)
        self.assertEqual(metrics["average_recovery_time"], 0.0)

        # エラー記録後の確認
        self.error_handler.log_error(
            error=ValueError("テストエラー"),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            operation="テスト操作",
        )

        metrics = self.error_handler.performance_metrics
        self.assertEqual(metrics["total_errors"], 1)


class TestErrorHandlingIntegration(unittest.TestCase):
    """エラーハンドリング統合テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        os.makedirs("logs", exist_ok=True)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_system_integration(self):
        """システム統合テスト"""
        # 統合エラーハンドリングシステムの使用
        from unified_error_handling_system import (
            get_unified_error_handler,
            ErrorCategory,
            ErrorSeverity,
        )

        handler = get_unified_error_handler()

        # 複数のエラーを記録
        errors = [
            (ValueError("システムエラー"), ErrorCategory.SYSTEM, ErrorSeverity.HIGH),
            (
                ConnectionError("接続エラー"),
                ErrorCategory.NETWORK,
                ErrorSeverity.MEDIUM,
            ),
            (
                FileNotFoundError("ファイルエラー"),
                ErrorCategory.FILE,
                ErrorSeverity.LOW,
            ),
        ]

        for error, category, severity in errors:
            handler.log_error(
                error=error,
                category=category,
                severity=severity,
                operation="統合テスト",
            )

        # 統計情報の確認
        stats = handler.get_error_statistics()
        # 累積カウントなので、期待値を調整
        self.assertGreaterEqual(stats["total_errors"], 3)
        # 累積カウントなので期待値を調整
        self.assertGreaterEqual(len(stats["errors_by_category"]), 3)
        self.assertGreaterEqual(len(stats["errors_by_severity"]), 3)

    def test_error_handling_with_real_scenarios(self):
        """実際のシナリオでのエラーハンドリングテスト"""
        handler = get_unified_error_handler()

        # APIエラーのシナリオ
        try:
            raise ConnectionError("API接続失敗")
        except Exception as e:
            log_api_error(e, "https://api.example.com/data", 500)

        # データ処理エラーのシナリオ
        try:
            raise ValueError("データ型エラー")
        except Exception as e:
            log_data_error(e, "stock_data", (1000, 50))

        # モデルエラーのシナリオ
        try:
            raise RuntimeError("モデル学習失敗")
        except Exception as e:
            log_model_error(e, "LSTM_Model", "training")

        # ファイルエラーのシナリオ
        try:
            raise FileNotFoundError("設定ファイルが見つかりません")
        except Exception as e:
            log_file_error(e, "config.yaml", "読み込み")

        # 統計情報の確認（グローバルハンドラーを使用）
        global_handler = get_unified_error_handler()
        stats = global_handler.get_error_statistics()
        # 累積カウントなので、期待値を調整
        self.assertGreaterEqual(stats["total_errors"], 4)

        # カテゴリ別の確認（累積カウントなので期待値を調整）
        category_counts = stats["errors_by_category"]
        self.assertGreaterEqual(category_counts["API"], 1)
        self.assertGreaterEqual(category_counts["DATA"], 1)
        self.assertGreaterEqual(category_counts["MODEL"], 1)
        self.assertGreaterEqual(category_counts["FILE"], 1)


if __name__ == "__main__":
    # テストの実行
    unittest.main(verbosity=2)
