#!/usr/bin/env python3
"""
EnvironmentAuthManagerのテスト
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from core.environment_auth_manager import EnvironmentAuthManager


class TestEnvironmentAuthManager:
    """EnvironmentAuthManagerのテストクラス"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.auth_manager = EnvironmentAuthManager()
    
    def test_initialization(self):
        """初期化テスト"""
        assert self.auth_manager is not None
        assert hasattr(self.auth_manager, 'environment')
        assert hasattr(self.auth_manager, 'auth_info')
    
    def test_detect_environment_development(self):
        """開発環境の検出テスト"""
        with patch.dict(os.environ, {}, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "development"
    
    def test_detect_environment_production(self):
        """本番環境の検出テスト"""
        with patch.dict(os.environ, {'GITHUB_ACTIONS': 'true'}, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "production"
    
    def test_detect_environment_staging(self):
        """ステージング環境の検出テスト"""
        with patch.dict(os.environ, {'ENVIRONMENT': 'staging'}, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "staging"
    
    def test_load_auth_info_development(self):
        """開発環境での認証情報読み込みテスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('builtins.open', mock_open(read_data='JQUANTS_EMAIL=test@example.com\nJQUANTS_PASSWORD=password')):
                manager = EnvironmentAuthManager()
                assert manager.auth_info is not None
    
    def test_load_auth_info_production(self):
        """本番環境での認証情報読み込みテスト"""
        with patch.dict(os.environ, {
            'GITHUB_ACTIONS': 'true',
            'JQUANTS_EMAIL': 'prod@example.com',
            'JQUANTS_PASSWORD': 'prod_password'
        }, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.auth_info is not None
    
    def test_get_auth_info(self):
        """認証情報取得テスト"""
        auth_info = self.auth_manager.get_auth_info()
        assert isinstance(auth_info, dict)
        assert 'email' in auth_info
        assert 'password' in auth_info
        assert 'id_token' in auth_info
        assert 'refresh_token' in auth_info
    
    def test_is_authenticated_false(self):
        """未認証状態のテスト"""
        with patch.object(self.auth_manager, 'auth_info', {
            'email': None,
            'password': None,
            'id_token': None,
            'refresh_token': None
        }):
            assert not self.auth_manager.is_auth_configured()
    
    def test_is_authenticated_true_with_token(self):
        """IDトークンでの認証状態テスト"""
        with patch.object(self.auth_manager, 'auth_info', {
            'email': 'test@example.com',
            'password': 'password',
            'id_token': 'valid_token',
            'refresh_token': 'refresh_token'
        }):
            assert self.auth_manager.is_auth_configured()
    
    def test_is_authenticated_true_with_credentials(self):
        """認証情報での認証状態テスト"""
        with patch.object(self.auth_manager, 'auth_info', {
            'email': 'test@example.com',
            'password': 'password',
            'id_token': None,
            'refresh_token': None
        }):
            assert self.auth_manager.is_auth_configured()
    
    def test_get_environment(self):
        """環境取得テスト"""
        environment = self.auth_manager.environment
        assert environment in ['development', 'staging', 'production']
    
    def test_get_credentials(self):
        """認証情報取得テスト"""
        credentials = {
            'email': self.auth_manager.get_email(),
            'password': self.auth_manager.get_password()
        }
        assert isinstance(credentials, dict)
        assert 'email' in credentials
        assert 'password' in credentials
    
    def test_get_tokens(self):
        """トークン取得テスト"""
        tokens = {
            'id_token': self.auth_manager.get_id_token(),
            'refresh_token': self.auth_manager.get_refresh_token()
        }
        assert isinstance(tokens, dict)
        assert 'id_token' in tokens
        assert 'refresh_token' in tokens
    
    def test_validate_auth_info_valid(self):
        """有効な認証情報の検証テスト"""
        valid_auth = {
            'email': 'test@example.com',
            'password': 'password',
            'id_token': 'valid_token',
            'refresh_token': 'refresh_token'
        }
        with patch.object(self.auth_manager, 'auth_info', valid_auth):
            assert self.auth_manager.validate_auth_info()
    
    def test_validate_auth_info_invalid(self):
        """無効な認証情報の検証テスト"""
        invalid_auth = {
            'email': None,
            'password': None,
            'id_token': None,
            'refresh_token': None
        }
        with patch.object(self.auth_manager, 'auth_info', invalid_auth):
            result = self.auth_manager.validate_auth_info()
            assert not result['is_configured']
    
    def test_get_auth_summary(self):
        """認証情報サマリー取得テスト"""
        summary = self.auth_manager.validate_auth_info()
        assert isinstance(summary, dict)
        assert 'environment' in summary
        assert 'has_email_password' in summary
        assert 'has_id_token' in summary
        assert 'has_refresh_token' in summary
    
    def test_error_handling_missing_env_file(self):
        """環境ファイル不在時のエラーハンドリングテスト"""
        with patch.dict(os.environ, {}, clear=True):
            # 環境変数が設定されていない場合のテスト
            with patch.object(EnvironmentAuthManager, '_load_auth_info', return_value={
                'email': None,
                'password': None,
                'id_token': None,
                'refresh_token': None
            }):
                manager = EnvironmentAuthManager()
                assert manager.auth_info is not None
                assert not manager.is_auth_configured()
    
    def test_error_handling_invalid_env_file(self):
        """無効な環境ファイルのエラーハンドリングテスト"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('builtins.open', mock_open(read_data='invalid content')):
                manager = EnvironmentAuthManager()
                assert manager.auth_info is not None
    
    def test_environment_specific_loading(self):
        """環境固有の読み込みテスト"""
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}, clear=True):
            with patch('builtins.open', mock_open(read_data='JQUANTS_EMAIL=dev@example.com')):
                manager = EnvironmentAuthManager()
                assert manager.environment == "development"
    
    def test_production_environment_detection(self):
        """本番環境の検出テスト"""
        with patch.dict(os.environ, {
            'GITHUB_ACTIONS': 'true',
            'JQUANTS_EMAIL': 'prod@example.com'
        }, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "production"
            assert manager.auth_info['email'] == 'prod@example.com'
    
    def test_staging_environment_detection(self):
        """ステージング環境の検出テスト"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'staging',
            'JQUANTS_EMAIL': 'staging@example.com'
        }, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "staging"
    
    def test_auth_info_structure(self):
        """認証情報構造のテスト"""
        auth_info = self.auth_manager.get_auth_info()
        required_keys = ['email', 'password', 'id_token', 'refresh_token']
        for key in required_keys:
            assert key in auth_info
            assert auth_info[key] is None or isinstance(auth_info[key], str)
    
    def test_environment_detection_priority(self):
        """環境検出の優先順位テスト"""
        # ENVIRONMENTが最優先
        with patch.dict(os.environ, {
            'GITHUB_ACTIONS': 'true',
            'ENVIRONMENT': 'development'
        }, clear=True):
            manager = EnvironmentAuthManager()
            assert manager.environment == "development"
    
    def test_credentials_validation(self):
        """認証情報の検証テスト"""
        # 有効な認証情報
        with patch.object(self.auth_manager, 'auth_info', {
            'email': 'test@example.com',
            'password': 'password'
        }):
            assert self.auth_manager.is_auth_configured()
        
        # 無効な認証情報
        with patch.object(self.auth_manager, 'auth_info', {
            'email': '',
            'password': ''
        }):
            assert not self.auth_manager.is_auth_configured()
    
    def test_token_validation(self):
        """トークンの検証テスト"""
        # 有効なトークン
        with patch.object(self.auth_manager, 'auth_info', {
            'id_token': 'valid_token',
            'refresh_token': 'valid_refresh'
        }):
            assert self.auth_manager.is_auth_configured()
        
        # 無効なトークン
        with patch.object(self.auth_manager, 'auth_info', {
            'id_token': '',
            'refresh_token': ''
        }):
            assert not self.auth_manager.is_auth_configured()
    
    def test_auth_summary_completeness(self):
        """認証情報サマリーの完全性テスト"""
        summary = self.auth_manager.validate_auth_info()
        assert 'environment' in summary
        assert 'has_email_password' in summary
        assert 'has_id_token' in summary
        assert 'has_refresh_token' in summary
    
    def test_load_env_manually(self):
        """手動環境ファイル読み込みテスト"""
        with patch('builtins.open', mock_open(read_data='JQUANTS_EMAIL=test@example.com\nJQUANTS_PASSWORD=testpass')):
            with patch.dict(os.environ, {}, clear=True):
                # 手動読み込みをテスト
                self.auth_manager._load_env_manually(Path('.env'))
                assert os.getenv('JQUANTS_EMAIL') == 'test@example.com'
                assert os.getenv('JQUANTS_PASSWORD') == 'testpass'
    
    def test_load_env_manually_with_error(self):
        """手動環境ファイル読み込みエラーテスト"""
        with patch('builtins.open', side_effect=IOError("File not found")):
            # エラーが発生しても例外が発生しないことを確認
            self.auth_manager._load_env_manually(Path('.env'))
    
    def test_dotenv_import_error(self):
        """dotenvインポートエラーのテスト"""
        import builtins
        real_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'dotenv':
                raise ImportError("No module named 'dotenv'")
            return real_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            with patch.object(self.auth_manager, '_load_env_manually') as mock_load:
                with patch('pathlib.Path.exists', return_value=True):
                    self.auth_manager._load_from_env_file()
                    mock_load.assert_called_once()
    
    def test_get_auth_status_message(self):
        """認証状態メッセージ取得テスト"""
        message = self.auth_manager.get_auth_status_message()
        assert isinstance(message, str)
        assert len(message) > 0
    
    def test_get_auth_status_message_with_tokens(self):
        """トークンありの認証状態メッセージテスト"""
        with patch.object(self.auth_manager, 'auth_info', {
            'email': 'test@example.com',
            'password': 'password',
            'id_token': 'token123',
            'refresh_token': 'refresh123'
        }):
            message = self.auth_manager.get_auth_status_message()
            assert isinstance(message, str)
            assert len(message) > 0
