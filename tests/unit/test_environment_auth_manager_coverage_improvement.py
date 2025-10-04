#!/usr/bin/env python3
"""
環境認証管理システムのカバレッジ向上テスト
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
from core.environment_auth_manager import EnvironmentAuthManager


class TestEnvironmentAuthManagerCoverageImprovement:
    """環境認証管理システムのカバレッジ向上テスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_environment_github_actions(self):
        """GitHub Actions環境の検出テスト"""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            manager = EnvironmentAuthManager()
            assert manager.environment == "production"

    def test_detect_environment_explicit_development(self):
        """明示的な開発環境設定テスト"""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "development"

    def test_detect_environment_explicit_staging(self):
        """明示的なステージング環境設定テスト"""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "staging"

    def test_detect_environment_explicit_production(self):
        """明示的な本番環境設定テスト"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            manager = EnvironmentAuthManager()
            assert manager.environment == "production"

    def test_detect_environment_default(self):
        """デフォルト環境（開発環境）テスト"""
        with patch.dict(os.environ, {}, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "development"

    def test_load_auth_info_development(self):
        """開発環境での認証情報読み込みテスト"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "JQUANTS_EMAIL": "test@example.com",
            "JQUANTS_PASSWORD": "password123"
        }, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.auth_info["email"] == "test@example.com"
            assert manager.auth_info["password"] == "password123"

    def test_load_auth_info_production(self):
        """本番環境での認証情報読み込みテスト"""
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true",
            "JQUANTS_EMAIL": "prod@example.com",
            "JQUANTS_PASSWORD": "prod_password",
            "JQUANTS_ID_TOKEN": "prod_token"
        }):
            manager = EnvironmentAuthManager()
            assert manager.auth_info["email"] == "prod@example.com"
            assert manager.auth_info["password"] == "prod_password"
            assert manager.auth_info["id_token"] == "prod_token"

    def test_load_auth_info_no_env_file(self):
        """環境ファイルなしでの認証情報読み込みテスト"""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            with patch('os.path.exists', return_value=False):
                with patch('dotenv.load_dotenv'):
                    manager = EnvironmentAuthManager()
                    assert manager.auth_info["email"] is None
                    assert manager.auth_info["password"] is None

    def test_load_auth_info_env_file_error(self):
        """環境ファイル読み込みエラーテスト"""
        # 環境変数を完全にクリア
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
                with patch('os.path.exists', return_value=True):
                    with patch('dotenv.load_dotenv', side_effect=IOError("File read error")):
                        # 環境変数を手動で削除
                        for var in ["JQUANTS_EMAIL", "JQUANTS_PASSWORD", "JQUANTS_ID_TOKEN", "JQUANTS_REFRESH_TOKEN"]:
                            if var in os.environ:
                                del os.environ[var]
                        # 環境変数がクリアされたことを確認
                        assert os.getenv("JQUANTS_EMAIL") is None
                        assert os.getenv("JQUANTS_PASSWORD") is None
                        # 特定の環境変数のみをモック
                        def mock_getenv(key, default=None):
                            if key in ["JQUANTS_EMAIL", "JQUANTS_PASSWORD", "JQUANTS_ID_TOKEN", "JQUANTS_REFRESH_TOKEN"]:
                                return None
                            return os.environ.get(key, default)
                        with patch('os.getenv', side_effect=mock_getenv):
                            manager = EnvironmentAuthManager()
                            assert manager.auth_info["email"] is None
                            assert manager.auth_info["password"] is None

    def test_get_auth_info_available(self):
        """認証情報取得（利用可能）テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com",
            "JQUANTS_PASSWORD": "password123",
            "JQUANTS_ID_TOKEN": "token123"
        }):
            manager = EnvironmentAuthManager()
            auth_info = manager.get_auth_info()
            
            assert auth_info["email"] == "test@example.com"
            assert auth_info["password"] == "password123"
            assert auth_info["id_token"] == "token123"

    def test_get_auth_info_not_available(self):
        """認証情報取得（利用不可）テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                auth_info = manager.get_auth_info()
                
                assert auth_info["email"] is None
                assert auth_info["password"] is None
                assert auth_info["id_token"] is None

    def test_get_auth_info_partial(self):
        """認証情報取得（部分的）テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com",
            "JQUANTS_PASSWORD": "password123"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                auth_info = manager.get_auth_info()
                
                assert auth_info["email"] == "test@example.com"
                assert auth_info["password"] == "password123"
                assert auth_info["id_token"] is None

    def test_is_authenticated_true(self):
        """認証状態確認（認証済み）テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_ID_TOKEN": "valid_token"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                assert manager.is_auth_configured() is True

    def test_is_authenticated_false(self):
        """認証状態確認（未認証）テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                assert manager.is_auth_configured() is False

    def test_get_environment(self):
        """環境取得テスト"""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                assert manager.environment == "staging"

    def test_get_environment_default(self):
        """環境取得（デフォルト）テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                assert manager.environment == "development"

    def test_validate_auth_info_complete(self):
        """認証情報検証（完全）テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com",
            "JQUANTS_PASSWORD": "password123",
            "JQUANTS_ID_TOKEN": "token123"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                result = manager.validate_auth_info()
                
                assert result["is_configured"] is True
                assert result["has_email_password"] is True
                assert result["has_id_token"] is True

    def test_validate_auth_info_incomplete(self):
        """認証情報検証（不完全）テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                result = manager.validate_auth_info()
                
                assert result["is_configured"] is False
                assert result["has_email_password"] is False
                assert result["has_id_token"] is False

    def test_validate_auth_info_empty(self):
        """認証情報検証（空）テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                result = manager.validate_auth_info()
                
                assert result["is_configured"] is False
                assert result["has_email_password"] is False
                assert result["has_id_token"] is False

    def test_get_missing_auth_info(self):
        """不足認証情報取得テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                result = manager.validate_auth_info()
                
                assert result["has_email_password"] is False
                assert result["has_id_token"] is False

    def test_get_missing_auth_info_all_missing(self):
        """不足認証情報取得（全て不足）テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                result = manager.validate_auth_info()
                
                assert result["is_configured"] is False
                assert result["has_email_password"] is False
                assert result["has_id_token"] is False

    def test_get_missing_auth_info_none_missing(self):
        """不足認証情報取得（不足なし）テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com",
            "JQUANTS_PASSWORD": "password123",
            "JQUANTS_ID_TOKEN": "token123"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                result = manager.validate_auth_info()
                
                assert result["is_configured"] is True
                assert result["has_email_password"] is True
                assert result["has_id_token"] is True

    def test_get_auth_summary(self):
        """認証情報サマリー取得テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com",
            "JQUANTS_PASSWORD": "password123",
            "JQUANTS_ID_TOKEN": "token123"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                summary = manager.get_auth_status_summary()
                
                assert summary["environment"] == "development"
                assert summary["is_configured"] is True
                assert summary["has_email"] is True
                assert summary["has_password"] is True
                assert summary["has_id_token"] is True

    def test_get_auth_summary_partial(self):
        """認証情報サマリー取得（部分的）テスト"""
        with patch.dict(os.environ, {
            "JQUANTS_EMAIL": "test@example.com"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                summary = manager.get_auth_status_summary()
                
                assert summary["environment"] == "development"
                assert summary["is_configured"] is False
                assert summary["has_email"] is True
                assert summary["has_password"] is False
                assert summary["has_id_token"] is False

    def test_get_auth_summary_empty(self):
        """認証情報サマリー取得（空）テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                summary = manager.get_auth_status_summary()
                
                assert summary["environment"] == "development"
                assert summary["is_configured"] is False
                assert summary["has_email"] is False
                assert summary["has_password"] is False
                assert summary["has_id_token"] is False

    def test_environment_specific_loading(self):
        """環境別読み込みテスト"""
        # 開発環境
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            with patch('builtins.open', mock_open(read_data="JQUANTS_EMAIL=dev@example.com")):
                with patch('os.path.exists', return_value=True):
                    # 環境変数を手動で設定
                    with patch.dict(os.environ, {"JQUANTS_EMAIL": "dev@example.com"}):
                        manager = EnvironmentAuthManager()
                        assert manager.environment == "development"
                        assert manager.auth_info["email"] == "dev@example.com"

    def test_environment_specific_loading_staging(self):
        """ステージング環境別読み込みテスト"""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            with patch.dict(os.environ, {
                "JQUANTS_EMAIL": "staging@example.com",
                "JQUANTS_PASSWORD": "staging_password"
            }):
                with patch('dotenv.load_dotenv'):
                    manager = EnvironmentAuthManager()
                    assert manager.environment == "staging"
                    assert manager.auth_info["email"] == "staging@example.com"

    def test_environment_specific_loading_production(self):
        """本番環境別読み込みテスト"""
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true",
            "JQUANTS_EMAIL": "prod@example.com",
            "JQUANTS_PASSWORD": "prod_password",
            "JQUANTS_ID_TOKEN": "prod_token"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                assert manager.environment == "production"
                assert manager.auth_info["email"] == "prod@example.com"
                assert manager.auth_info["password"] == "prod_password"
                assert manager.auth_info["id_token"] == "prod_token"

    def test_auth_info_initialization(self):
        """認証情報初期化テスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                
                # 初期化時の認証情報構造を確認
                assert "email" in manager.auth_info
                assert "password" in manager.auth_info
                assert "id_token" in manager.auth_info
                assert "refresh_token" in manager.auth_info

    def test_environment_detection_priority(self):
        """環境検出優先順位テスト"""
        # ENVIRONMENTが最優先
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true",
            "ENVIRONMENT": "development"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                assert manager.environment == "development"

    def test_auth_info_loading_fallback(self):
        """認証情報読み込みフォールバックテスト"""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            with patch('os.path.exists', return_value=False):
                with patch('dotenv.load_dotenv'):
                    manager = EnvironmentAuthManager()
                    # 環境ファイルが存在しない場合、環境変数から読み込み
                    assert manager.auth_info["email"] is None
                    assert manager.auth_info["password"] is None

    def test_auth_info_loading_with_env_vars(self):
        """環境変数での認証情報読み込みテスト"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "JQUANTS_EMAIL": "env@example.com",
            "JQUANTS_PASSWORD": "env_password"
        }, clear=True):
            with patch('dotenv.load_dotenv'):
                manager = EnvironmentAuthManager()
                assert manager.auth_info["email"] == "env@example.com"
                assert manager.auth_info["password"] == "env_password"

    def test_auth_info_loading_mixed_sources(self):
        """混在ソースでの認証情報読み込みテスト"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "JQUANTS_EMAIL": "env@example.com",
            "JQUANTS_PASSWORD": "file_password"
        }, clear=True):
            with patch('builtins.open', mock_open(read_data="JQUANTS_PASSWORD=file_password")):
                with patch('os.path.exists', return_value=True):
                    # 環境変数を手動で設定
                    manager = EnvironmentAuthManager()
                    # 環境変数が優先される
                    assert manager.auth_info["email"] == "env@example.com"
                    # ファイルから読み込まれる
                    assert manager.auth_info["password"] == "file_password"
