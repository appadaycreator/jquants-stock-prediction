#!/usr/bin/env python3
"""
統合エラーハンドリングシステムの包括的テスト
全機能のテストと検証を実行
"""

import asyncio
import unittest
import logging
import json
import time
from typing import Dict, Any, List, Tuple
from datetime import datetime
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 統合エラーハンドリングシステムのインポート
from unified_error_handling_system import (
    get_unified_error_handler,
    ErrorCategory,
    ErrorSeverity,
    error_handler,
    error_context,
    log_api_error,
    log_data_error,
    log_model_error,
    log_file_error
)

# ユーザーフレンドリーなエラーメッセージシステムのインポート
from user_friendly_error_messages import (
    get_user_friendly_error_messages,
    ErrorType,
    format_error_for_user,
    get_error_guidance_for_user
)

# 強化自動復旧システムのインポート
from enhanced_auto_recovery_system import (
    get_enhanced_auto_recovery_system,
    attempt_auto_recovery
)

# エラーガイダンスシステムのインポート
from error_guidance_system import (
    get_error_guidance_system,
    generate_error_guidance
)


class UnifiedErrorHandlingTestSuite(unittest.TestCase):
    """統合エラーハンドリングシステムのテストスイート"""
    
    def setUp(self):
        """テストの初期化"""
        self.error_handler = get_unified_error_handler()
        self.user_friendly_messages = get_user_friendly_error_messages()
        self.auto_recovery_system = get_enhanced_auto_recovery_system()
        self.guidance_system = get_error_guidance_system()
        
        # テスト用の一時ディレクトリ
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        
        # ログ設定
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("UnifiedErrorHandlingTest")
    
    def tearDown(self):
        """テストのクリーンアップ"""
        # 一時ディレクトリの削除
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # エラー履歴のクリア
        self.error_handler.clear_error_history()
    
    def test_basic_error_logging(self):
        """基本エラーログ機能のテスト"""
        # テストエラーの生成
        test_error = ValueError("テストエラー")
        
        # エラーログの記録
        error_info = self.error_handler.log_error(
            error=test_error,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            operation="テスト操作"
        )
        
        # 検証
        self.assertIsNotNone(error_info)
        self.assertEqual(error_info.error_type, "ValueError")
        self.assertEqual(error_info.category, ErrorCategory.SYSTEM)
        self.assertEqual(error_info.severity, ErrorSeverity.MEDIUM)
        
        # エラー統計の確認
        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 1)
        self.assertEqual(stats["errors_by_category"]["SYSTEM"], 1)
    
    def test_error_categories(self):
        """エラーカテゴリのテスト"""
        test_cases = [
            (ConnectionError("接続エラー"), ErrorCategory.NETWORK),
            (FileNotFoundError("ファイルエラー"), ErrorCategory.FILE),
            (ValueError("データエラー"), ErrorCategory.DATA),
            (RuntimeError("モデルエラー"), ErrorCategory.MODEL),
            (PermissionError("認証エラー"), ErrorCategory.AUTHENTICATION)
        ]
        
        for error, category in test_cases:
            with self.subTest(error=type(error).__name__, category=category.value):
                error_info = self.error_handler.log_error(
                    error=error,
                    category=category,
                    severity=ErrorSeverity.MEDIUM,
                    operation="テスト操作"
                )
                
                self.assertEqual(error_info.category, category)
    
    def test_error_severity(self):
        """エラー重要度のテスト"""
        test_cases = [
            (ValueError("軽微なエラー"), ErrorSeverity.LOW),
            (RuntimeError("中程度のエラー"), ErrorSeverity.MEDIUM),
            (ConnectionError("重要なエラー"), ErrorSeverity.HIGH),
            (SystemError("致命的なエラー"), ErrorSeverity.CRITICAL)
        ]
        
        for error, severity in test_cases:
            with self.subTest(error=type(error).__name__, severity=severity.value):
                error_info = self.error_handler.log_error(
                    error=error,
                    category=ErrorCategory.SYSTEM,
                    severity=severity,
                    operation="テスト操作"
                )
                
                self.assertEqual(error_info.severity, severity)
    
    def test_error_decorator(self):
        """エラーハンドラーデコレータのテスト"""
        @error_handler(ErrorCategory.API, ErrorSeverity.HIGH, "API呼び出し")
        def test_api_function():
            raise ConnectionError("API接続エラー")
        
        # デコレータがエラーをキャッチすることを確認
        with self.assertRaises(ConnectionError):
            test_api_function()
        
        # エラーがログに記録されることを確認
        stats = self.error_handler.get_error_statistics()
        self.assertGreater(stats["total_errors"], 0)
    
    def test_error_context_manager(self):
        """エラーコンテキストマネージャーのテスト"""
        with error_context("データ処理", ErrorCategory.DATA, ErrorSeverity.MEDIUM) as handler:
            # コンテキスト内でエラーが発生
            raise ValueError("データ処理エラー")
    
    def test_convenience_functions(self):
        """便利関数のテスト"""
        # APIエラーのログ
        log_api_error(ConnectionError("API接続エラー"), "https://api.example.com", 500)
        
        # データエラーのログ
        log_data_error(ValueError("データ型エラー"), "stock_data", (1000, 50))
        
        # モデルエラーのログ
        log_model_error(RuntimeError("モデル実行エラー"), "LSTM_Model", "prediction")
        
        # ファイルエラーのログ
        log_file_error(FileNotFoundError("ファイルが見つかりません"), "/path/to/file.txt", "read")
        
        # エラーがログに記録されることを確認
        stats = self.error_handler.get_error_statistics()
        self.assertGreater(stats["total_errors"], 0)
    
    def test_user_friendly_messages(self):
        """ユーザーフレンドリーなメッセージのテスト"""
        test_errors = [
            "ConnectionError: Failed to establish connection",
            "FileNotFoundError: No such file or directory",
            "ValueError: Invalid data format",
            "AuthenticationError: Invalid API key",
            "ModelError: Failed to load model"
        ]
        
        for error_message in test_errors:
            with self.subTest(error=error_message):
                # ユーザーフレンドリーなメッセージの取得
                formatted_message = format_error_for_user(error_message)
                
                # メッセージがフォーマットされていることを確認
                self.assertIsInstance(formatted_message, str)
                self.assertGreater(len(formatted_message), 0)
                
                # 日本語が含まれていることを確認
                self.assertTrue(any(char in formatted_message for char in "エラー解決方法予防"))
    
    def test_error_guidance(self):
        """エラーガイダンスのテスト"""
        test_errors = [
            (ConnectionError("接続エラー"), ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            (FileNotFoundError("ファイルエラー"), ErrorCategory.FILE, ErrorSeverity.MEDIUM),
            (ValueError("データエラー"), ErrorCategory.DATA, ErrorSeverity.LOW)
        ]
        
        for error, category, severity in test_errors:
            with self.subTest(error=type(error).__name__, category=category.value):
                # ガイダンスの生成
                guidance = asyncio.run(
                    self.guidance_system.generate_error_guidance(error, category, severity)
                )
                
                # ガイダンスが生成されることを確認
                self.assertIsNotNone(guidance)
                self.assertIsNotNone(guidance.title)
                self.assertIsNotNone(guidance.description)
                self.assertGreater(len(guidance.immediate_actions), 0)
                self.assertGreater(len(guidance.step_by_step_guide), 0)
    
    def test_auto_recovery(self):
        """自動復旧機能のテスト"""
        test_errors = [
            (ConnectionError("接続エラー"), ErrorCategory.NETWORK),
            (FileNotFoundError("ファイルエラー"), ErrorCategory.FILE),
            (ValueError("データエラー"), ErrorCategory.DATA)
        ]
        
        for error, category in test_errors:
            with self.subTest(error=type(error).__name__, category=category.value):
                # 自動復旧の試行
                success, result = asyncio.run(
                    self.auto_recovery_system.attempt_recovery(error, category)
                )
                
                # 復旧試行が実行されることを確認
                self.assertIsInstance(success, bool)
                self.assertIsNotNone(result)
    
    def test_error_statistics(self):
        """エラー統計のテスト"""
        # 複数のエラーを生成
        errors = [
            (ValueError("エラー1"), ErrorCategory.SYSTEM, ErrorSeverity.LOW),
            (ConnectionError("エラー2"), ErrorCategory.NETWORK, ErrorSeverity.MEDIUM),
            (FileNotFoundError("エラー3"), ErrorCategory.FILE, ErrorSeverity.HIGH),
            (RuntimeError("エラー4"), ErrorCategory.MODEL, ErrorSeverity.CRITICAL)
        ]
        
        for error, category, severity in errors:
            self.error_handler.log_error(
                error=error,
                category=category,
                severity=severity,
                operation="テスト操作"
            )
        
        # 統計情報の取得
        stats = self.error_handler.get_error_statistics()
        
        # 検証
        self.assertEqual(stats["total_errors"], 4)
        self.assertEqual(stats["errors_by_category"]["SYSTEM"], 1)
        self.assertEqual(stats["errors_by_category"]["NETWORK"], 1)
        self.assertEqual(stats["errors_by_category"]["FILE"], 1)
        self.assertEqual(stats["errors_by_category"]["MODEL"], 1)
        self.assertEqual(stats["errors_by_severity"]["LOW"], 1)
        self.assertEqual(stats["errors_by_severity"]["MEDIUM"], 1)
        self.assertEqual(stats["errors_by_severity"]["HIGH"], 1)
        self.assertEqual(stats["errors_by_severity"]["CRITICAL"], 1)
    
    def test_error_export(self):
        """エラーレポートのエクスポートテスト"""
        # テストエラーの生成
        self.error_handler.log_error(
            error=ValueError("テストエラー"),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            operation="テスト操作"
        )
        
        # レポートのエクスポート
        report_file = os.path.join(self.temp_dir, "error_report.json")
        self.error_handler.export_error_report(report_file)
        
        # ファイルが作成されることを確認
        self.assertTrue(os.path.exists(report_file))
        
        # レポートの内容を確認
        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        
        self.assertIn("export_timestamp", report_data)
        self.assertIn("statistics", report_data)
        self.assertIn("error_history", report_data)
    
    def test_performance_metrics(self):
        """パフォーマンスメトリクスのテスト"""
        # 大量のエラーを生成
        start_time = time.time()
        
        for i in range(100):
            self.error_handler.log_error(
                error=ValueError(f"エラー{i}"),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.LOW,
                operation="パフォーマンステスト"
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 処理時間が合理的であることを確認
        self.assertLess(processing_time, 10.0)  # 10秒以内
        
        # 統計情報の確認
        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 100)
    
    def test_error_recovery_rate(self):
        """エラー復旧率のテスト"""
        # 復旧システムの統計を取得
        recovery_stats = self.auto_recovery_system.get_recovery_statistics()
        
        # 復旧率が計算されることを確認
        self.assertIn("recovery_stats", recovery_stats)
        self.assertIn("recovery_rate", recovery_stats["recovery_stats"])
        
        # 復旧率が0-1の範囲内であることを確認
        recovery_rate = recovery_stats["recovery_stats"]["recovery_rate"]
        self.assertGreaterEqual(recovery_rate, 0.0)
        self.assertLessEqual(recovery_rate, 1.0)
    
    def test_guidance_statistics(self):
        """ガイダンス統計のテスト"""
        # ガイダンス統計を取得
        guidance_stats = self.guidance_system.get_guidance_statistics()
        
        # 統計情報が含まれることを確認
        self.assertIn("guidance_stats", guidance_stats)
        self.assertIn("recent_guidances", guidance_stats)
        self.assertIn("category_guidance_count", guidance_stats)
        self.assertIn("success_rate", guidance_stats)
    
    def test_integration(self):
        """統合テスト"""
        # 統合エラーハンドリングのテスト
        test_error = ConnectionError("統合テストエラー")
        
        # 1. エラーログの記録
        error_info = self.error_handler.log_error(
            error=test_error,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            operation="統合テスト"
        )
        
        # 2. ユーザーフレンドリーなメッセージの生成
        user_message = format_error_for_user(str(test_error))
        
        # 3. 自動復旧の試行
        recovery_success, recovery_result = asyncio.run(
            self.auto_recovery_system.attempt_recovery(test_error, ErrorCategory.NETWORK)
        )
        
        # 4. エラーガイダンスの生成
        guidance = asyncio.run(
            self.guidance_system.generate_error_guidance(
                test_error, ErrorCategory.NETWORK, ErrorSeverity.HIGH
            )
        )
        
        # 検証
        self.assertIsNotNone(error_info)
        self.assertIsNotNone(user_message)
        self.assertIsNotNone(recovery_result)
        self.assertIsNotNone(guidance)
        
        # 統合統計の確認
        error_stats = self.error_handler.get_error_statistics()
        recovery_stats = self.auto_recovery_system.get_recovery_statistics()
        guidance_stats = self.guidance_system.get_guidance_statistics()
        
        self.assertGreater(error_stats["total_errors"], 0)
        self.assertGreater(recovery_stats["recovery_stats"]["total_attempts"], 0)
        self.assertGreater(guidance_stats["guidance_stats"]["total_guidances"], 0)


class ErrorHandlingPerformanceTest(unittest.TestCase):
    """エラーハンドリングのパフォーマンステスト"""
    
    def setUp(self):
        """テストの初期化"""
        self.error_handler = get_unified_error_handler()
        self.auto_recovery_system = get_enhanced_auto_recovery_system()
        self.guidance_system = get_error_guidance_system()
    
    def tearDown(self):
        """テストのクリーンアップ"""
        self.error_handler.clear_error_history()
    
    def test_high_volume_error_handling(self):
        """大量エラーハンドリングのパフォーマンステスト"""
        start_time = time.time()
        
        # 1000個のエラーを生成
        for i in range(1000):
            self.error_handler.log_error(
                error=ValueError(f"パフォーマンステストエラー{i}"),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.LOW,
                operation="パフォーマンステスト"
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 処理時間が合理的であることを確認
        self.assertLess(processing_time, 30.0)  # 30秒以内
        
        # 統計情報の確認
        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 1000)
    
    def test_concurrent_error_handling(self):
        """並行エラーハンドリングのテスト"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def error_worker(worker_id):
            """エラーワーカー"""
            try:
                for i in range(100):
                    self.error_handler.log_error(
                        error=ValueError(f"並行テストエラー{worker_id}-{i}"),
                        category=ErrorCategory.SYSTEM,
                        severity=ErrorSeverity.LOW,
                        operation="並行テスト"
                    )
                results.put(f"ワーカー{worker_id}完了")
            except Exception as e:
                results.put(f"ワーカー{worker_id}エラー: {e}")
        
        # 5つのスレッドで並行実行
        threads = []
        for i in range(5):
            thread = threading.Thread(target=error_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待機
        for thread in threads:
            thread.join()
        
        # 結果の確認
        self.assertEqual(results.qsize(), 5)
        
        # 統計情報の確認
        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 500)  # 5ワーカー × 100エラー


def run_comprehensive_tests():
    """包括的テストの実行"""
    print("🧪 統合エラーハンドリングシステム包括的テスト")
    print("=" * 60)
    
    # テストスイートの作成
    test_suite = unittest.TestSuite()
    
    # 基本機能テスト
    test_suite.addTest(unittest.makeSuite(UnifiedErrorHandlingTestSuite))
    
    # パフォーマンステスト
    test_suite.addTest(unittest.makeSuite(ErrorHandlingPerformanceTest))
    
    # テストランナーの実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果の表示
    print(f"\n📊 テスト結果:")
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ 失敗したテスト:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 エラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


def run_integration_test():
    """統合テストの実行"""
    print("\n🔗 統合テストの実行")
    print("-" * 40)
    
    try:
        # 統合エラーハンドリングシステムのテスト
        error_handler = get_unified_error_handler()
        auto_recovery_system = get_enhanced_auto_recovery_system()
        guidance_system = get_error_guidance_system()
        
        # テストエラーの生成
        test_error = ConnectionError("統合テストエラー")
        
        # エラーハンドリングの実行
        error_info = error_handler.log_error(
            error=test_error,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            operation="統合テスト"
        )
        
        # 自動復旧の試行
        recovery_success, recovery_result = asyncio.run(
            auto_recovery_system.attempt_recovery(test_error, ErrorCategory.NETWORK)
        )
        
        # エラーガイダンスの生成
        guidance = asyncio.run(
            guidance_system.generate_error_guidance(
                test_error, ErrorCategory.NETWORK, ErrorSeverity.HIGH
            )
        )
        
        print("✅ 統合テスト成功")
        print(f"エラー情報: {error_info.error_type}")
        print(f"復旧成功: {recovery_success}")
        print(f"ガイダンス: {guidance.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ 統合テスト失敗: {e}")
        return False


def run_performance_test():
    """パフォーマンステストの実行"""
    print("\n⚡ パフォーマンステストの実行")
    print("-" * 40)
    
    try:
        error_handler = get_unified_error_handler()
        
        # 大量エラーハンドリングのテスト
        start_time = time.time()
        
        for i in range(1000):
            error_handler.log_error(
                error=ValueError(f"パフォーマンステストエラー{i}"),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.LOW,
                operation="パフォーマンステスト"
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ パフォーマンステスト成功")
        print(f"処理時間: {processing_time:.2f}秒")
        print(f"処理速度: {1000/processing_time:.2f}エラー/秒")
        
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンステスト失敗: {e}")
        return False


if __name__ == "__main__":
    # 包括的テストの実行
    test_success = run_comprehensive_tests()
    
    # 統合テストの実行
    integration_success = run_integration_test()
    
    # パフォーマンステストの実行
    performance_success = run_performance_test()
    
    # 最終結果の表示
    print("\n🎯 最終テスト結果")
    print("=" * 60)
    print(f"包括的テスト: {'✅ 成功' if test_success else '❌ 失敗'}")
    print(f"統合テスト: {'✅ 成功' if integration_success else '❌ 失敗'}")
    print(f"パフォーマンステスト: {'✅ 成功' if performance_success else '❌ 失敗'}")
    
    overall_success = test_success and integration_success and performance_success
    print(f"\n🏆 全体結果: {'✅ 成功' if overall_success else '❌ 失敗'}")
    
    if overall_success:
        print("\n🎉 統合エラーハンドリングシステムのテストが完了しました！")
        print("すべての機能が正常に動作しています。")
    else:
        print("\n⚠️ 一部のテストが失敗しました。")
        print("詳細なログを確認して問題を特定してください。")
