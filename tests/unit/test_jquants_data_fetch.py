"""
J-Quantsデータ取得モジュールのユニットテスト
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
from jquants_data_fetch import JQuantsDataFetcher


class TestJQuantsDataFetcher:
    """JQuantsDataFetcherクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        fetcher = JQuantsDataFetcher()
        assert fetcher is not None
        assert hasattr(fetcher, "base_url")
        assert hasattr(fetcher, "logger")

    def test_init_with_config(self):
        """設定付き初期化テスト"""
        config = {
            "base_url": "https://test.api.com",
            "max_retries": 5,
            "retry_interval": 10
        }
        fetcher = JQuantsDataFetcher(config)
        assert fetcher.base_url == "https://test.api.com"
        assert fetcher.max_retries == 5
        assert fetcher.retry_interval == 10

    @patch('jquants_data_fetch.requests.get')
    def test_authenticate_success(self, mock_get):
        """認証成功テスト"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh_token"
        }
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        result = fetcher.authenticate("test@example.com", "password")

        assert result is True
        assert fetcher.access_token == "test_token"
        assert fetcher.refresh_token == "refresh_token"

    @patch('jquants_data_fetch.requests.get')
    def test_authenticate_failure(self, mock_get):
        """認証失敗テスト"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid credentials"}
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        result = fetcher.authenticate("invalid@example.com", "wrong_password")

        assert result is False
        assert fetcher.access_token is None

    @patch('jquants_data_fetch.requests.get')
    def test_authenticate_network_error(self, mock_get):
        """ネットワークエラーテスト"""
        mock_get.side_effect = Exception("Network error")

        fetcher = JQuantsDataFetcher()
        result = fetcher.authenticate("test@example.com", "password")

        assert result is False

    @patch('jquants_data_fetch.requests.get')
    def test_refresh_token_success(self, mock_get):
        """トークンリフレッシュ成功テスト"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "refresh_token": "new_refresh_token"
        }
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        fetcher.refresh_token = "old_refresh_token"
        result = fetcher.refresh_access_token()

        assert result is True
        assert fetcher.access_token == "new_token"
        assert fetcher.refresh_token == "new_refresh_token"

    @patch('jquants_data_fetch.requests.get')
    def test_refresh_token_failure(self, mock_get):
        """トークンリフレッシュ失敗テスト"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        fetcher.refresh_token = "invalid_refresh_token"
        result = fetcher.refresh_access_token()

        assert result is False

    @patch('jquants_data_fetch.requests.get')
    def test_fetch_stock_data_success(self, mock_get):
        """株価データ取得成功テスト"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "Code": "1234",
                    "Date": "20240301",
                    "Open": 100.0,
                    "High": 105.0,
                    "Low": 95.0,
                    "Close": 102.0,
                    "Volume": 1000000
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        fetcher.access_token = "test_token"
        
        result = fetcher.fetch_stock_data("20240301")

        assert result is not None
        assert len(result) == 1
        assert result.iloc[0]["Code"] == "1234"
        assert result.iloc[0]["Close"] == 102.0

    @patch('jquants_data_fetch.requests.get')
    def test_fetch_stock_data_unauthorized(self, mock_get):
        """認証エラー時のテスト"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        fetcher.access_token = "invalid_token"
        
        result = fetcher.fetch_stock_data("20240301")

        assert result is None

    @patch('jquants_data_fetch.requests.get')
    def test_fetch_stock_data_empty(self, mock_get):
        """空のデータレスポンスのテスト"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        fetcher.access_token = "test_token"
        
        result = fetcher.fetch_stock_data("20240301")

        assert result is not None
        assert len(result) == 0

    def test_save_data_to_csv(self, tmp_path):
        """CSV保存テスト"""
        fetcher = JQuantsDataFetcher()
        
        # テストデータの作成
        test_data = pd.DataFrame({
            "Code": ["1234", "5678"],
            "Date": ["20240301", "20240302"],
            "Close": [100.0, 101.0]
        })
        
        file_path = tmp_path / "test_data.csv"
        result = fetcher.save_data_to_csv(test_data, str(file_path))
        
        assert result is True
        assert file_path.exists()
        
        # 保存されたデータの確認
        loaded_data = pd.read_csv(file_path)
        assert len(loaded_data) == 2
        assert loaded_data.iloc[0]["Code"] == "1234"

    def test_save_data_to_csv_error(self):
        """CSV保存エラーテスト"""
        fetcher = JQuantsDataFetcher()
        
        # 無効なパスでの保存
        test_data = pd.DataFrame({"test": [1, 2, 3]})
        result = fetcher.save_data_to_csv(test_data, "/invalid/path/test.csv")
        
        assert result is False

    @patch('jquants_data_fetch.requests.get')
    def test_fetch_with_retry_success(self, mock_get):
        """リトライ成功テスト"""
        # 最初のリクエストは失敗、2回目は成功
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": []}
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]

        fetcher = JQuantsDataFetcher()
        fetcher.access_token = "test_token"
        fetcher.max_retries = 3
        fetcher.retry_interval = 0.1  # テスト用に短縮
        
        result = fetcher.fetch_stock_data("20240301")

        assert result is not None
        assert mock_get.call_count == 2

    @patch('jquants_data_fetch.requests.get')
    def test_fetch_with_retry_failure(self, mock_get):
        """リトライ失敗テスト"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        fetcher = JQuantsDataFetcher()
        fetcher.access_token = "test_token"
        fetcher.max_retries = 2
        fetcher.retry_interval = 0.1
        
        result = fetcher.fetch_stock_data("20240301")

        assert result is None
        assert mock_get.call_count == 3  # 初回 + 2回のリトライ

    def test_validate_date_format(self):
        """日付フォーマット検証テスト"""
        fetcher = JQuantsDataFetcher()
        
        # 有効な日付
        assert fetcher._validate_date_format("20240301") is True
        assert fetcher._validate_date_format("20241231") is True
        
        # 無効な日付
        assert fetcher._validate_date_format("2024-03-01") is False
        assert fetcher._validate_date_format("240301") is False
        assert fetcher._validate_date_format("invalid") is False
        assert fetcher._validate_date_format("") is False

    def test_validate_data_structure(self):
        """データ構造検証テスト"""
        fetcher = JQuantsDataFetcher()
        
        # 有効なデータ
        valid_data = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"],
            "Open": [100.0],
            "High": [105.0],
            "Low": [95.0],
            "Close": [102.0],
            "Volume": [1000000]
        })
        assert fetcher._validate_data_structure(valid_data) is True
        
        # 必須カラムが不足
        invalid_data = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"]
        })
        assert fetcher._validate_data_structure(invalid_data) is False
        
        # 空のデータフレーム
        empty_data = pd.DataFrame()
        assert fetcher._validate_data_structure(empty_data) is False

    @patch('jquants_data_fetch.requests.get')
    def test_complete_workflow(self, mock_get):
        """完全なワークフローテスト"""
        # 認証レスポンス
        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh_token"
        }
        
        # データ取得レスポンス
        data_response = MagicMock()
        data_response.status_code = 200
        data_response.json.return_value = {
            "data": [
                {
                    "Code": "1234",
                    "Date": "20240301",
                    "Open": 100.0,
                    "High": 105.0,
                    "Low": 95.0,
                    "Close": 102.0,
                    "Volume": 1000000
                }
            ]
        }
        
        mock_get.side_effect = [auth_response, data_response]

        fetcher = JQuantsDataFetcher()
        
        # 認証
        auth_result = fetcher.authenticate("test@example.com", "password")
        assert auth_result is True
        
        # データ取得
        data_result = fetcher.fetch_stock_data("20240301")
        assert data_result is not None
        assert len(data_result) == 1

    def test_error_handling_invalid_input(self):
        """無効な入力のエラーハンドリングテスト"""
        fetcher = JQuantsDataFetcher()
        
        # 無効な日付形式
        result = fetcher.fetch_stock_data("invalid_date")
        assert result is None
        
        # 空の文字列
        result = fetcher.fetch_stock_data("")
        assert result is None
        
        # None
        result = fetcher.fetch_stock_data(None)
        assert result is None

    @patch('jquants_data_fetch.requests.get')
    def test_network_timeout(self, mock_get):
        """ネットワークタイムアウトテスト"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        fetcher = JQuantsDataFetcher()
        fetcher.access_token = "test_token"
        
        result = fetcher.fetch_stock_data("20240301")
        assert result is None

    @patch('jquants_data_fetch.requests.get')
    def test_connection_error(self, mock_get):
        """接続エラーテスト"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        fetcher = JQuantsDataFetcher()
        fetcher.access_token = "test_token"
        
        result = fetcher.fetch_stock_data("20240301")
        assert result is None
