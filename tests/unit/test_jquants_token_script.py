#!/usr/bin/env python3
"""
scripts/test_jquants_token.py のテスト（リファクタリング版）
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import json
from datetime import datetime

# テスト対象のインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scripts.test_jquants_token import (
    JQuantsTestResult,
    EndpointConfig,
    JQuantsTestResultData,
    JQuantsTokenTester,
    test_jquants_token,
)


class TestJQuantsTestResult(unittest.TestCase):
    """JQuantsTestResult列挙型のテスト"""

    def test_test_result_values(self):
        """テスト結果値のテスト"""
        self.assertEqual(JQuantsTestResult.SUCCESS.value, "success")
        self.assertEqual(JQuantsTestResult.FAILURE.value, "failure")
        self.assertEqual(JQuantsTestResult.TIMEOUT.value, "timeout")
        self.assertEqual(JQuantsTestResult.ERROR.value, "error")
        self.assertEqual(JQuantsTestResult.EXCEPTION.value, "exception")


class TestEndpointConfig(unittest.TestCase):
    """EndpointConfigクラスのテスト"""

    def test_endpoint_config_initialization(self):
        """エンドポイント設定の初期化テスト"""
        config = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
            timeout=30,
        )

        self.assertEqual(config.name, "テストエンドポイント")
        self.assertEqual(config.url, "https://api.example.com/test")
        self.assertEqual(config.description, "テスト用エンドポイント")
        self.assertEqual(config.timeout, 30)

    def test_endpoint_config_default_timeout(self):
        """デフォルトタイムアウトのテスト"""
        config = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
        )

        self.assertEqual(config.timeout, 30)  # デフォルト値


class TestJQuantsTestResultData(unittest.TestCase):
    """JQuantsTestResultDataクラスのテスト"""

    def test_test_result_data_initialization(self):
        """テスト結果データの初期化テスト"""
        result = JQuantsTestResultData(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            status_code=200,
            success=True,
            response_size=1024,
            headers={"Content-Type": "application/json"},
            data_keys=["key1", "key2"],
            data_sample="sample data",
            error_message=None,
            json_error=False,
            error=None,
        )

        self.assertEqual(result.name, "テストエンドポイント")
        self.assertEqual(result.url, "https://api.example.com/test")
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.success)
        self.assertEqual(result.response_size, 1024)
        self.assertEqual(result.headers["Content-Type"], "application/json")
        self.assertEqual(result.data_keys, ["key1", "key2"])
        self.assertEqual(result.data_sample, "sample data")
        self.assertIsNone(result.error_message)
        self.assertFalse(result.json_error)
        self.assertIsNone(result.error)


class TestJQuantsTokenTester(unittest.TestCase):
    """JQuantsTokenTesterクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_token = "test_token_12345"
        self.tester = JQuantsTokenTester(self.test_token)

    def test_initialization(self):
        """初期化のテスト"""
        self.assertEqual(self.tester.id_token, self.test_token)
        self.assertEqual(
            self.tester.headers["Authorization"], f"Bearer {self.test_token}"
        )
        self.assertEqual(self.tester.headers["Content-Type"], "application/json")
        self.assertEqual(
            self.tester.headers["User-Agent"], "jQuants-Stock-Prediction/1.0"
        )
        self.assertEqual(len(self.tester.endpoints), 3)

    def test_get_default_endpoints(self):
        """デフォルトエンドポイントの取得テスト"""
        endpoints = self.tester._get_default_endpoints()

        self.assertEqual(len(endpoints), 3)
        self.assertEqual(endpoints[0].name, "上場企業情報")
        self.assertEqual(endpoints[1].name, "銘柄一覧")
        self.assertEqual(endpoints[2].name, "市場情報")

    @patch("requests.get")
    def test_test_single_endpoint_success(self, mock_get):
        """単一エンドポイント成功テスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"test": "data"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response

        endpoint = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
        )

        result = self.tester.test_single_endpoint(endpoint)

        self.assertEqual(result.name, "テストエンドポイント")
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.success)
        self.assertEqual(result.data_keys, ["test"])
        self.assertIn("data", result.data_sample)

    @patch("requests.get")
    def test_test_single_endpoint_failure(self, mock_get):
        """単一エンドポイント失敗テスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = b"Not Found"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        endpoint = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
        )

        result = self.tester.test_single_endpoint(endpoint)

        self.assertEqual(result.name, "テストエンドポイント")
        self.assertEqual(result.status_code, 404)
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Not Found")

    @patch("requests.get")
    def test_test_single_endpoint_timeout(self, mock_get):
        """単一エンドポイントタイムアウトテスト"""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        endpoint = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
        )

        result = self.tester.test_single_endpoint(endpoint)

        self.assertEqual(result.name, "テストエンドポイント")
        self.assertEqual(result.status_code, "TIMEOUT")
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Timeout")

    @patch("requests.get")
    def test_test_single_endpoint_request_exception(self, mock_get):
        """単一エンドポイントリクエスト例外テスト"""
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        endpoint = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
        )

        result = self.tester.test_single_endpoint(endpoint)

        self.assertEqual(result.name, "テストエンドポイント")
        self.assertEqual(result.status_code, "ERROR")
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Connection error")

    @patch("requests.get")
    def test_test_single_endpoint_general_exception(self, mock_get):
        """単一エンドポイント一般例外テスト"""
        mock_get.side_effect = Exception("Unexpected error")

        endpoint = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
        )

        result = self.tester.test_single_endpoint(endpoint)

        self.assertEqual(result.name, "テストエンドポイント")
        self.assertEqual(result.status_code, "EXCEPTION")
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Unexpected error")

    def test_process_successful_response(self):
        """成功レスポンス処理のテスト"""
        mock_response = Mock()
        mock_response.json.return_value = {"key1": "value1", "key2": "value2"}

        result = JQuantsTestResultData(
            name="テスト",
            url="https://api.example.com/test",
            status_code=200,
            success=True,
            response_size=100,
            headers={},
        )

        self.tester._process_successful_response(mock_response, result)

        self.assertEqual(result.data_keys, ["key1", "key2"])
        self.assertIn("value1", result.data_sample)

    def test_process_successful_response_json_error(self):
        """成功レスポンスJSON解析エラーのテスト"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.text = "Invalid JSON response"

        result = JQuantsTestResultData(
            name="テスト",
            url="https://api.example.com/test",
            status_code=200,
            success=True,
            response_size=100,
            headers={},
        )

        self.tester._process_successful_response(mock_response, result)

        self.assertTrue(result.json_error)

    def test_create_error_result(self):
        """エラー結果作成のテスト"""
        endpoint = EndpointConfig(
            name="テストエンドポイント",
            url="https://api.example.com/test",
            description="テスト用エンドポイント",
        )

        result = self.tester._create_error_result(endpoint, "ERROR", "Test error")

        self.assertEqual(result.name, "テストエンドポイント")
        self.assertEqual(result.url, "https://api.example.com/test")
        self.assertEqual(result.status_code, "ERROR")
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Test error")

    @patch("requests.get")
    def test_test_all_endpoints(self, mock_get):
        """全エンドポイントテスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"test": "data"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response

        results = self.tester.test_all_endpoints()

        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result.success)
            self.assertEqual(result.status_code, 200)

    def test_print_summary(self):
        """サマリー表示のテスト"""
        results = [
            JQuantsTestResultData(
                "成功テスト", "https://api.example.com/success", 200, True, 100, {}
            ),
            JQuantsTestResultData(
                "失敗テスト",
                "https://api.example.com/failure",
                404,
                False,
                0,
                {},
                error_message="Not Found",
            ),
        ]

        # 標準出力をキャプチャしてテスト
        with patch("builtins.print") as mock_print:
            self.tester.print_summary(results)

            # サマリーが表示されることを確認
            mock_print.assert_called()

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("json.dump")
    def test_save_results(self, mock_json_dump, mock_open):
        """結果保存のテスト"""
        results = [
            JQuantsTestResultData("テスト", "https://api.example.com/test", 200, True, 100, {})
        ]

        self.tester.save_results(results, "test_output.json")

        # ファイルが開かれることを確認
        mock_open.assert_called_once_with("test_output.json", "w", encoding="utf-8")

        # JSONが保存されることを確認
        mock_json_dump.assert_called_once()


class TestTestJquantsTokenFunction(unittest.TestCase):
    """test_jquants_token関数のテスト"""

    @patch.dict(os.environ, {"JQUANTS_ID_TOKEN": "test_token_12345"})
    @patch("scripts.test_jquants_token.JQuantsTokenTester")
    def test_test_jquants_token_success(self, mock_tester_class):
        """トークンテスト成功のテスト"""
        # モックテスターの設定
        mock_tester = Mock()
        mock_result = JQuantsTestResultData(
            "テスト", "https://api.example.com/test", 200, True, 100, {}
        )
        mock_tester.test_all_endpoints.return_value = [mock_result]
        mock_tester_class.return_value = mock_tester

        result = test_jquants_token()

        self.assertTrue(result)
        mock_tester.test_all_endpoints.assert_called_once()
        mock_tester.print_summary.assert_called_once()
        mock_tester.save_results.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_test_jquants_token_no_token(self):
        """トークンなしのテスト"""
        result = test_jquants_token()

        self.assertFalse(result)

    @patch.dict(os.environ, {"JQUANTS_ID_TOKEN": "test_token_12345"})
    @patch("scripts.test_jquants_token.JQuantsTokenTester")
    def test_test_jquants_token_failure(self, mock_tester_class):
        """トークンテスト失敗のテスト"""
        # モックテスターの設定
        mock_tester = Mock()
        mock_result = JQuantsTestResultData(
            "テスト", "https://api.example.com/test", 404, False, 0, {}
        )
        mock_tester.test_all_endpoints.return_value = [mock_result]
        mock_tester_class.return_value = mock_tester

        result = test_jquants_token()

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
