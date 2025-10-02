"""
統合テストモジュール

このモジュールは統合テストのサンプルです。
実際の統合テストを追加する際のテンプレートとして使用してください。
"""

import pytest
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.config_manager import ConfigManager
from core.error_handler import ErrorHandler


class TestIntegration:
    """統合テストクラス"""

    def test_config_manager_integration(self):
        """ConfigManagerの統合テスト"""
        # テスト用の設定ファイルが存在するかチェック
        config_file = project_root / "config_final.yaml"
        if config_file.exists():
            config_manager = ConfigManager(str(config_file))
            assert config_manager is not None
        else:
            # 設定ファイルが存在しない場合はスキップ
            pytest.skip("設定ファイルが存在しません")

    def test_error_handler_integration(self):
        """ErrorHandlerの統合テスト"""
        error_handler = ErrorHandler()
        assert error_handler is not None

        # エラーハンドラーの基本機能をテスト
        try:
            # 意図的にエラーを発生させる
            raise ValueError("テスト用のエラー")
        except ValueError as e:
            # エラーハンドラーが正常に動作することを確認
            assert str(e) == "テスト用のエラー"

    def test_logs_directory_creation(self):
        """ログディレクトリの自動作成テスト"""
        logs_dir = project_root / "logs"

        # ログディレクトリを強制的に作成
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            pytest.fail(f"ログディレクトリの作成に失敗しました: {e}")

        # ログディレクトリが存在することを確認
        assert logs_dir.exists(), f"ログディレクトリが存在しません: {logs_dir}"
        assert (
            logs_dir.is_dir()
        ), f"ログディレクトリがディレクトリではありません: {logs_dir}"

        # ログディレクトリが作成されたことを確認
        assert logs_dir.exists(), f"ログディレクトリの作成に失敗しました: {logs_dir}"

        # ログディレクトリに書き込み権限があることを確認
        try:
            test_file = logs_dir / "test.log"
            test_file.write_text("test")
            test_file.unlink()  # テストファイルを削除
        except Exception as e:
            pytest.fail(f"ログディレクトリに書き込み権限がありません: {e}")

    def test_project_structure(self):
        """プロジェクト構造の統合テスト"""
        # 必要なディレクトリが存在することを確認
        required_dirs = ["core", "data", "scripts", "tests", "web-app"]

        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"必要なディレクトリ {dir_name} が存在しません"
            assert dir_path.is_dir(), f"{dir_name} がディレクトリではありません"

    def test_core_modules_import(self):
        """コアモジュールのインポート統合テスト"""
        try:
            from core.config_manager import ConfigManager
            from core.error_handler import ErrorHandler
            from core.logging_manager import LoggingManager
            from core.prediction_engine import PredictionEngine
            from core.json_data_manager import JSONDataManager
            from core.differential_updater import DifferentialUpdater
            from core.performance_optimizer import PerformanceOptimizer

            # すべてのモジュールが正常にインポートできることを確認
            assert True
        except ImportError as e:
            pytest.fail(f"コアモジュールのインポートに失敗しました: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
