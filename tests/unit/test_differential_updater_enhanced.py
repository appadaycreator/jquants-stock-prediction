#!/usr/bin/env python3
"""
差分更新システムの拡張テスト
カバレッジ98%目標達成のための追加テスト
"""

import pytest
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from core.differential_updater import (
    DifferentialUpdater, UpdateConfig, DiffResult, 
    UpdateStatus, ValidationResult, UpdateStats, UpdateResult
)


class TestDifferentialUpdaterEnhanced:
    """差分更新システムの拡張テストクラス"""

    def test_calculate_diff_counts_empty_data(self):
        """空データでの差分カウント計算テスト"""
        updater = DifferentialUpdater()
        
        result = updater._calculate_diff_counts([], [])
        
        assert result["added"] == 0
        assert result["updated"] == 0
        assert result["removed"] == 0
        assert result["unchanged"] == 0

    def test_calculate_diff_counts_new_data(self):
        """新規データでの差分カウント計算テスト"""
        updater = DifferentialUpdater()
        
        existing_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100}
        ]
        new_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 110}
        ]
        
        result = updater._calculate_diff_counts(existing_data, new_data)
        
        assert result["added"] == 1
        assert result["updated"] == 0
        assert result["removed"] == 0
        assert result["unchanged"] == 1

    def test_calculate_diff_counts_updated_data(self):
        """更新データでの差分カウント計算テスト"""
        updater = DifferentialUpdater()
        
        existing_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100}
        ]
        new_data = [
            {"date": "2024-01-01", "code": "1234", "close": 110}
        ]
        
        result = updater._calculate_diff_counts(existing_data, new_data)
        
        assert result["added"] == 0
        assert result["updated"] == 1
        assert result["removed"] == 0
        assert result["unchanged"] == 0

    def test_calculate_diff_counts_removed_data(self):
        """削除データでの差分カウント計算テスト"""
        updater = DifferentialUpdater()
        
        existing_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 110}
        ]
        new_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100}
        ]
        
        result = updater._calculate_diff_counts(existing_data, new_data)
        
        assert result["added"] == 0
        assert result["updated"] == 0
        assert result["removed"] == 1
        assert result["unchanged"] == 1

    def test_is_significant_change_true(self):
        """重要な変更の判定テスト（True）"""
        updater = DifferentialUpdater()
        
        diff_counts = {"added": 5, "updated": 3, "removed": 2, "unchanged": 5}
        
        result = updater._is_significant_change(diff_counts)
        
        assert result is True

    def test_is_significant_change_false(self):
        """重要な変更の判定テスト（False）"""
        updater = DifferentialUpdater()
        
        diff_counts = {"added": 1, "updated": 1, "removed": 1, "unchanged": 20}
        
        result = updater._is_significant_change(diff_counts)
        
        assert result is False

    def test_is_significant_change_zero_total(self):
        """総レコード数が0の場合のテスト"""
        updater = DifferentialUpdater()
        
        diff_counts = {"added": 0, "updated": 0, "removed": 0, "unchanged": 0}
        
        result = updater._is_significant_change(diff_counts)
        
        assert result is False

    def test_calculate_data_hash_empty_data(self):
        """空データでのハッシュ計算テスト"""
        updater = DifferentialUpdater()
        
        result = updater._calculate_data_hash([])
        
        assert isinstance(result, str)
        assert len(result) == 32  # MD5ハッシュの長さ

    def test_calculate_data_hash_with_data(self):
        """データ付きでのハッシュ計算テスト"""
        updater = DifferentialUpdater()
        
        data = [{"date": "2024-01-01", "close": 100}]
        result = updater._calculate_data_hash(data)
        
        assert isinstance(result, str)
        assert len(result) == 32

    def test_get_record_key_standard_format(self):
        """標準フォーマットでのレコードキー取得テスト"""
        updater = DifferentialUpdater()
        
        record = {"Date": "2024-01-01", "Code": "1234"}
        result = updater._get_record_key(record)
        
        assert result == "1234_2024-01-01"

    def test_get_record_key_lowercase_format(self):
        """小文字フォーマットでのレコードキー取得テスト"""
        updater = DifferentialUpdater()
        
        record = {"date": "2024-01-01", "code": "1234"}
        result = updater._get_record_key(record)
        
        assert result == "1234_2024-01-01"

    def test_get_record_key_missing_fields(self):
        """フィールドが不足している場合のテスト"""
        updater = DifferentialUpdater()
        
        record = {"date": "2024-01-01"}
        result = updater._get_record_key(record)
        
        assert result == "_2024-01-01"

    def test_find_record_by_key_existing(self):
        """存在するレコードの検索テスト"""
        updater = DifferentialUpdater()
        
        data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 110}
        ]
        
        result = updater._find_record_by_key(data, "1234_2024-01-01")
        
        assert result is not None
        assert result["close"] == 100

    def test_find_record_by_key_not_existing(self):
        """存在しないレコードの検索テスト"""
        updater = DifferentialUpdater()
        
        data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        
        result = updater._find_record_by_key(data, "1234_2024-01-02")
        
        assert result is None

    def test_has_record_changed_true(self):
        """レコード変更の判定テスト（True）"""
        updater = DifferentialUpdater()
        
        old_record = {"Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 1000}
        new_record = {"Open": 100, "High": 110, "Low": 90, "Close": 110, "Volume": 1000}
        
        result = updater._has_record_changed(old_record, new_record)
        
        assert result is True

    def test_has_record_changed_false(self):
        """レコード変更の判定テスト（False）"""
        updater = DifferentialUpdater()
        
        old_record = {"Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 1000}
        new_record = {"Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 1000}
        
        result = updater._has_record_changed(old_record, new_record)
        
        assert result is False

    def test_has_record_changed_volume_change(self):
        """出来高変更でのレコード変更判定テスト"""
        updater = DifferentialUpdater()
        
        old_record = {"Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 1000}
        new_record = {"Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 2000}
        
        result = updater._has_record_changed(old_record, new_record)
        
        assert result is True

    def test_validate_data_integrity_with_duplicates(self):
        """重複データでの検証テスト"""
        updater = DifferentialUpdater()
        
        data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-01", "code": "1234", "close": 100}  # 重複
        ]
        
        result = updater._validate_data_integrity(data, [])
        
        assert result.is_valid is False
        assert len(result.issues) > 0

    def test_validate_data_integrity_with_missing_required_fields(self):
        """必須フィールド不足での検証テスト"""
        updater = DifferentialUpdater()
        
        data = [
            {"date": "2024-01-01", "code": "1234"}  # closeフィールドが不足
        ]
        
        result = updater._validate_data_integrity(data, [])
        
        assert result.is_valid is False
        assert len(result.issues) > 0

    def test_validate_data_integrity_empty_data(self):
        """空データでの検証テスト"""
        updater = DifferentialUpdater()
        
        result = updater._validate_data_integrity([], [])
        
        assert result.is_valid is True

    def test_validate_data_integrity_missing_required_fields(self):
        """必須フィールド不足での検証テスト"""
        updater = DifferentialUpdater()
        
        data = [{"date": "2024-01-01"}]  # 必須フィールドが不足
        
        result = updater._validate_data_integrity(data, [])
        
        assert result.is_valid is False

    def test_validate_data_integrity_invalid_date_format(self):
        """無効な日付フォーマットでの検証テスト"""
        updater = DifferentialUpdater()
        
        data = [
            {"date": "invalid-date", "code": "1234", "close": 100}
        ]
        
        result = updater._validate_data_integrity(data, [])
        
        assert result.is_valid is False

    def test_validate_data_integrity_negative_prices(self):
        """負の価格での検証テスト"""
        updater = DifferentialUpdater()
        
        data = [
            {"date": "2024-01-01", "code": "1234", "close": -100}
        ]
        
        result = updater._validate_data_integrity(data, [])
        
        assert result.is_valid is False

    def test_validate_data_integrity_exception_handling(self):
        """検証処理での例外ハンドリングテスト"""
        updater = DifferentialUpdater()
        
        with patch.object(updater, '_validate_data_integrity', side_effect=Exception("Test error")):
            result = updater._validate_data_integrity([], [])
            assert result.is_valid is False

    def test_calculate_comprehensive_diff_same_data(self):
        """同一データでの包括的差分計算テスト"""
        updater = DifferentialUpdater()
        
        data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        
        result = updater._calculate_comprehensive_diff(data, data)
        
        assert result.added_count == 0
        assert result.updated_count == 0
        assert result.removed_count == 0
        assert result.unchanged_count == 1
        assert result.is_significant_change is False

    def test_calculate_comprehensive_diff_new_data(self):
        """新規データでの包括的差分計算テスト"""
        updater = DifferentialUpdater()
        
        existing_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        new_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 110}
        ]
        
        result = updater._calculate_comprehensive_diff(existing_data, new_data)
        
        assert result.added_count == 1
        assert result.updated_count == 0
        assert result.removed_count == 0
        assert result.unchanged_count == 1

    def test_calculate_comprehensive_diff_updated_data(self):
        """更新データでの包括的差分計算テスト"""
        updater = DifferentialUpdater()
        
        existing_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        new_data = [{"date": "2024-01-01", "code": "1234", "close": 110}]
        
        result = updater._calculate_comprehensive_diff(existing_data, new_data)
        
        assert result.added_count == 0
        assert result.updated_count == 1
        assert result.removed_count == 0
        assert result.unchanged_count == 0

    def test_calculate_comprehensive_diff_removed_data(self):
        """削除データでの包括的差分計算テスト"""
        updater = DifferentialUpdater()
        
        existing_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 110}
        ]
        new_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
        
        result = updater._calculate_comprehensive_diff(existing_data, new_data)
        
        assert result.added_count == 0
        assert result.updated_count == 0
        assert result.removed_count == 1
        assert result.unchanged_count == 1

    def test_calculate_comprehensive_diff_exception_handling(self):
        """包括的差分計算での例外ハンドリングテスト"""
        updater = DifferentialUpdater()
        
        with patch.object(updater, '_calculate_data_hash', side_effect=Exception("Hash error")):
            result = updater._calculate_comprehensive_diff([], [])
            assert result.added_count == 0
            assert result.updated_count == 0
            assert result.removed_count == 0
            assert result.unchanged_count == 0

    def test_items_different_with_different_values(self):
        """異なる値でのアイテム差分テスト"""
        updater = DifferentialUpdater()
        
        item1 = {"date": "2024-01-01", "close": 100}
        item2 = {"date": "2024-01-01", "close": 110}
        
        result = updater._items_different(item1, item2)
        
        assert result is True

    def test_items_different_with_same_values(self):
        """同一値でのアイテム差分テスト"""
        updater = DifferentialUpdater()
        
        item1 = {"date": "2024-01-01", "close": 100}
        item2 = {"date": "2024-01-01", "close": 100}
        
        result = updater._items_different(item1, item2)
        
        assert result is False

    def test_identify_changes_with_changes(self):
        """変更がある場合の変更識別テスト"""
        updater = DifferentialUpdater()
        
        old_data = [{"date": "2024-01-01", "close": 100}]
        new_data = [{"date": "2024-01-01", "close": 110}]
        
        result = updater._identify_changes(old_data, new_data)
        
        assert len(result["updated"]) > 0

    def test_identify_changes_without_changes(self):
        """変更がない場合の変更識別テスト"""
        updater = DifferentialUpdater()
        
        data = [{"date": "2024-01-01", "close": 100}]
        
        result = updater._identify_changes(data, data)
        
        assert len(result["updated"]) == 0
        assert len(result["added"]) == 0
        assert len(result["removed"]) == 0