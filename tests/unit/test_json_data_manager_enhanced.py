#!/usr/bin/env python3
"""
JSONデータ管理システムの拡張テスト
カバレッジ98%目標達成のための追加テスト
"""

import pytest
import json
import tempfile
from unittest.mock import patch, mock_open
from core.json_data_manager import JSONDataManager


class TestJSONDataManagerEnhanced:
    """JSONデータ管理システムの拡張テストクラス"""

    def test_normalize_stock_data_missing_required_fields(self):
        """必須フィールドが不足している場合のテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234"}]  # closeフィールドが不足
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 0

    def test_normalize_stock_data_invalid_numeric_values(self):
        """無効な数値でのテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": "invalid", "high": 110, "low": 90, "close": 100, "volume": 1000}]
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 0

    def test_normalize_stock_data_none_values(self):
        """None値でのテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": None, "high": 110, "low": 90, "close": 100, "volume": 1000}]
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 1
        assert result[0]["open"] == 0.0

    def test_normalize_stock_data_empty_string_values(self):
        """空文字列でのテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": "", "high": 110, "low": 90, "close": 100, "volume": 1000}]
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 1
        assert result[0]["open"] == 0.0

    def test_normalize_stock_data_negative_volume(self):
        """負の出来高でのテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": 100, "high": 110, "low": 90, "close": 100, "volume": -1000}]
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 1
        assert result[0]["volume"] == 0

    def test_normalize_stock_data_zero_volume(self):
        """出来高0でのテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": 100, "high": 110, "low": 90, "close": 100, "volume": 0}]
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 1
        assert result[0]["volume"] == 0

    def test_normalize_stock_data_high_low_validation(self):
        """高値・安値の検証テスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": 100, "high": 90, "low": 110, "close": 100, "volume": 1000}]  # high < low
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 0

    def test_normalize_stock_data_close_out_of_range(self):
        """終値が高値・安値の範囲外のテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": 100, "high": 110, "low": 90, "close": 120, "volume": 1000}]  # close > high
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 0

    def test_normalize_stock_data_open_out_of_range(self):
        """始値が高値・安値の範囲外のテスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "open": 120, "high": 110, "low": 90, "close": 100, "volume": 1000}]  # open > high
        
        result = manager._normalize_stock_data(data)
        
        assert len(result) == 0

    def test_normalize_stock_data_exception_handling(self):
        """正規化処理での例外ハンドリングテスト"""
        manager = JSONDataManager()
        
        with patch.object(manager, '_normalize_stock_data', side_effect=Exception("Normalization error")):
            result = manager._normalize_stock_data([])
            assert result == []

    def test_save_data_exception_handling(self):
        """データ保存での例外ハンドリングテスト"""
        manager = JSONDataManager()
        
        with patch("builtins.open", side_effect=IOError("Write error")):
            result = manager.save_data("test.json", [])
            assert result is False

    def test_load_data_exception_handling(self):
        """データ読み込みでの例外ハンドリングテスト"""
        manager = JSONDataManager()
        
        with patch("builtins.open", side_effect=IOError("Read error")):
            result = manager.load_data("test.json")
            assert result is None

    def test_load_data_invalid_json(self):
        """無効なJSONでのテスト"""
        manager = JSONDataManager()
        
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("json.load", side_effect=json.JSONDecodeError("Invalid JSON", "doc", 0)):
                result = manager.load_data("test.json")
                assert result is None

    def test_load_data_none_content(self):
        """Noneコンテンツでのテスト"""
        manager = JSONDataManager()
        
        with patch("builtins.open", mock_open(read_data="")):
            with patch("json.load", return_value=None):
                result = manager.load_data("test.json")
                assert result is None

    def test_validate_data_structure_invalid_structure(self):
        """無効な構造での検証テスト"""
        manager = JSONDataManager()
        
        data = {"invalid": "structure"}
        
        result = manager._validate_data_structure(data)
        
        assert result is False

    def test_validate_data_structure_missing_required_fields(self):
        """必須フィールドが不足している場合の検証テスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234"}]  # closeフィールドが不足
        
        result = manager._validate_data_structure(data)
        
        assert result is False

    def test_validate_data_structure_valid_data(self):
        """有効なデータでの検証テスト"""
        manager = JSONDataManager()
        
        data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        
        result = manager._validate_data_structure(data)
        
        assert result is True

    def test_validate_data_structure_empty_data(self):
        """空データでの検証テスト"""
        manager = JSONDataManager()
        
        data = []
        
        result = manager._validate_data_structure(data)
        
        assert result is True

    def test_validate_data_structure_non_list_data(self):
        """リスト以外のデータでの検証テスト"""
        manager = JSONDataManager()
        
        data = "not a list"
        
        result = manager._validate_data_structure(data)
        
        assert result is False

    def test_validate_data_structure_non_dict_items(self):
        """辞書以外のアイテムでの検証テスト"""
        manager = JSONDataManager()
        
        data = ["not a dict", "also not a dict"]
        
        result = manager._validate_data_structure(data)
        
        assert result is False

    def test_validate_data_structure_exception_handling(self):
        """構造検証での例外ハンドリングテスト"""
        manager = JSONDataManager()
        
        with patch.object(manager, '_validate_data_structure', side_effect=Exception("Validation error")):
            result = manager._validate_data_structure([])
            assert result is False

    def test_merge_data_with_duplicates(self):
        """重複データでのマージテスト"""
        manager = JSONDataManager()
        
        existing_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        new_data = [{"date": "2024-01-01", "code": "1234", "close": 110}]
        
        result = manager._merge_data(existing_data, new_data)
        
        assert len(result) == 1
        assert result[0]["close"] == 110  # 新しいデータで上書き

    def test_merge_data_without_duplicates(self):
        """重複なしでのマージテスト"""
        manager = JSONDataManager()
        
        existing_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        new_data = [{"date": "2024-01-02", "code": "1234", "close": 110}]
        
        result = manager._merge_data(existing_data, new_data)
        
        assert len(result) == 2

    def test_merge_data_empty_existing(self):
        """既存データが空でのマージテスト"""
        manager = JSONDataManager()
        
        existing_data = []
        new_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        
        result = manager._merge_data(existing_data, new_data)
        
        assert len(result) == 1

    def test_merge_data_empty_new(self):
        """新規データが空でのマージテスト"""
        manager = JSONDataManager()
        
        existing_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        new_data = []
        
        result = manager._merge_data(existing_data, new_data)
        
        assert len(result) == 1

    def test_merge_data_both_empty(self):
        """両方のデータが空でのマージテスト"""
        manager = JSONDataManager()
        
        existing_data = []
        new_data = []
        
        result = manager._merge_data(existing_data, new_data)
        
        assert len(result) == 0

    def test_merge_data_exception_handling(self):
        """マージ処理での例外ハンドリングテスト"""
        manager = JSONDataManager()
        
        with patch.object(manager, '_merge_data', side_effect=Exception("Merge error")):
            result = manager._merge_data([], [])
            assert result == []

    def test_get_data_key_exception_handling(self):
        """データキー取得での例外ハンドリングテスト"""
        manager = JSONDataManager()
        
        with patch.object(manager, 'get_data_key', side_effect=Exception("Key error")):
            result = manager.get_data_key({})
            assert result is None

    def test_get_data_key_missing_fields(self):
        """必須フィールドが不足している場合のキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01"}  # codeフィールドが不足
        
        result = manager.get_data_key(item)
        
        assert result is None

    def test_get_data_key_valid_item(self):
        """有効なアイテムでのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": "1234"}
        
        result = manager.get_data_key(item)
        
        assert result == "1234_2024-01-01"

    def test_get_data_key_none_values(self):
        """None値でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": None, "code": "1234"}
        
        result = manager.get_data_key(item)
        
        assert result == "1234_None"

    def test_get_data_key_empty_string_values(self):
        """空文字列でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "", "code": "1234"}
        
        result = manager.get_data_key(item)
        
        assert result == "1234_"

    def test_get_data_key_mixed_types(self):
        """混合型でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": 20240101, "code": 1234}  # 数値型
        
        result = manager.get_data_key(item)
        
        assert result == "1234_20240101"

    def test_get_data_key_special_characters(self):
        """特殊文字でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": "1234-T"}
        
        result = manager.get_data_key(item)
        
        assert result == "1234-T_2024-01-01"

    def test_get_data_key_unicode_values(self):
        """Unicode値でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": "1234\u3042"}  # ひらがな
        
        result = manager.get_data_key(item)
        
        assert result == "1234\u3042_2024-01-01"

    def test_get_data_key_long_values(self):
        """長い値でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": "1234" * 100}  # 長いコード
        
        result = manager.get_data_key(item)
        
        assert result is not None
        assert len(result) > 100

    def test_get_data_key_whitespace_values(self):
        """空白文字でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "  2024-01-01  ", "code": "  1234  "}  # 前後に空白
        
        result = manager.get_data_key(item)
        
        assert result == "  1234  _  2024-01-01  "

    def test_get_data_key_numeric_strings(self):
        """数値文字列でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": "1234.5"}  # 小数点付き
        
        result = manager.get_data_key(item)
        
        assert result == "1234.5_2024-01-01"

    def test_get_data_key_boolean_values(self):
        """真偽値でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": True}  # 真偽値
        
        result = manager.get_data_key(item)
        
        assert result == "True_2024-01-01"

    def test_get_data_key_list_values(self):
        """リスト値でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": ["1234", "5678"]}  # リスト
        
        result = manager.get_data_key(item)
        
        assert result == "['1234', '5678']_2024-01-01"

    def test_get_data_key_dict_values(self):
        """辞書値でのキー取得テスト"""
        manager = JSONDataManager()
        
        item = {"date": "2024-01-01", "code": {"nested": "value"}}  # 辞書
        
        result = manager.get_data_key(item)
        
        assert result == "{'nested': 'value'}_2024-01-01"

    def test_get_data_key_none_item(self):
        """Noneアイテムでのキー取得テスト"""
        manager = JSONDataManager()
        
        result = manager.get_data_key(None)
        
        assert result is None

    def test_get_data_key_non_dict_item(self):
        """辞書以外のアイテムでのキー取得テスト"""
        manager = JSONDataManager()
        
        result = manager.get_data_key("not a dict")
        
        assert result is None

    def test_get_data_key_exception_handling(self):
        """キー取得での例外ハンドリングテスト"""
        manager = JSONDataManager()
        
        with patch.object(manager, 'get_data_key', side_effect=Exception("Key error")):
            result = manager.get_data_key({})
            assert result is None
