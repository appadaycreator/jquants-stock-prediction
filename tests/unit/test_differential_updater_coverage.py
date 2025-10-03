#!/usr/bin/env python3
"""
DifferentialUpdaterのテストカバレッジ向上
不足しているテストケースを追加
"""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open
from core.differential_updater import DifferentialUpdater, UpdateStatus, UpdateConfig, DiffResult


class TestDifferentialUpdaterCoverage:
    """DifferentialUpdaterのカバレッジ向上テスト"""

    def test_update_config_initialization(self):
        """更新設定の初期化テスト"""
        config = UpdateConfig(
            max_retry_attempts=5,
            retry_delay_seconds=10,
            batch_size=50,
            enable_validation=True,
            enable_compression=True,
            enable_backup=True,
            max_data_age_days=60
        )
        
        # 設定値の確認
        assert config.max_retry_attempts == 5
        assert config.retry_delay_seconds == 10
        assert config.batch_size == 50
        assert config.enable_validation is True
        assert config.enable_compression is True
        assert config.enable_backup is True
        assert config.max_data_age_days == 60

    def test_diff_result_initialization(self):
        """差分結果の初期化テスト"""
        result = DiffResult(
            added_count=10,
            updated_count=5,
            removed_count=2,
            unchanged_count=100,
            processing_time=1.5,
            data_hash="test_hash",
            is_significant_change=True
        )
        
        # 結果値の確認
        assert result.added_count == 10
        assert result.updated_count == 5
        assert result.removed_count == 2
        assert result.unchanged_count == 100
        assert result.processing_time == 1.5
        assert result.data_hash == "test_hash"
        assert result.is_significant_change is True

    def test_update_status_enum(self):
        """更新ステータス列挙型テスト"""
        # 各ステータスの確認
        assert UpdateStatus.SUCCESS.value == "success"
        assert UpdateStatus.FAILED.value == "failed"
        assert UpdateStatus.PARTIAL.value == "partial"
        assert UpdateStatus.VALIDATION_ERROR.value == "validation_error"
        assert UpdateStatus.RETRY_EXHAUSTED.value == "retry_exhausted"

    def test_calculate_comprehensive_diff_with_empty_data(self):
        """空データでの包括的差分計算テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            # 空データでの差分計算
            result = updater._calculate_comprehensive_diff([], [])
            
            # 空データの結果を確認
            assert result.added_count == 0
            assert result.updated_count == 0
            assert result.removed_count == 0
            assert result.unchanged_count == 0
            assert result.is_significant_change is False

    def test_calculate_comprehensive_diff_with_identical_data(self):
        """同一データでの包括的差分計算テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            test_data = [
                {"date": "2024-01-01", "code": "1234", "close": 100},
                {"date": "2024-01-02", "code": "1234", "close": 101}
            ]
            
            # 同一データでの差分計算
            result = updater._calculate_comprehensive_diff(test_data, test_data)
            
            # 差分がないことを確認
            assert result.added_count == 0
            assert result.updated_count == 0
            assert result.removed_count == 0
            assert result.unchanged_count == 2
            assert result.is_significant_change is False

    def test_is_significant_change_with_high_ratio(self):
        """高い変更率での重要変更判定テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            # 高い変更率の差分カウント
            diff_counts = {
                "added": 20,
                "updated": 10,
                "removed": 5,
                "unchanged": 15
            }
            
            result = updater._is_significant_change(diff_counts)
            
            # 重要変更と判定されることを確認
            assert result is True

    def test_is_significant_change_with_low_ratio(self):
        """低い変更率での重要変更判定テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            # 低い変更率の差分カウント
            diff_counts = {
                "added": 2,
                "updated": 1,
                "removed": 1,
                "unchanged": 96
            }
            
            result = updater._is_significant_change(diff_counts)
            
            # 重要変更と判定されないことを確認
            assert result is False

    def test_is_significant_change_with_zero_total(self):
        """ゼロ総数での重要変更判定テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            # ゼロ総数の差分カウント
            diff_counts = {
                "added": 0,
                "updated": 0,
                "removed": 0,
                "unchanged": 0
            }
            
            result = updater._is_significant_change(diff_counts)
            
            # 重要変更と判定されないことを確認
            assert result is False

    def test_calculate_data_hash_with_different_data(self):
        """異なるデータでのハッシュ計算テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            data1 = [{"date": "2024-01-01", "code": "1234", "close": 100}]
            data2 = [{"date": "2024-01-01", "code": "1234", "close": 101}]
            
            hash1 = updater._calculate_data_hash(data1)
            hash2 = updater._calculate_data_hash(data2)
            
            # 異なるデータで異なるハッシュが生成されることを確認
            assert hash1 != hash2

    def test_calculate_data_hash_with_identical_data(self):
        """同一データでのハッシュ計算テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
            
            hash1 = updater._calculate_data_hash(data)
            hash2 = updater._calculate_data_hash(data)
            
            # 同一データで同一ハッシュが生成されることを確認
            assert hash1 == hash2

    def test_get_record_key_with_different_field_names(self):
        """異なるフィールド名でのレコードキー取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            # 大文字フィールド名
            record1 = {"Date": "2024-01-01", "Code": "1234", "close": 100}
            key1 = updater._get_record_key(record1)
            
            # 小文字フィールド名
            record2 = {"date": "2024-01-01", "code": "1234", "close": 100}
            key2 = updater._get_record_key(record2)
            
            # 同じキーが生成されることを確認
            assert key1 == key2
            assert key1 == "1234_2024-01-01"

    def test_has_record_changed_with_different_values(self):
        """異なる値でのレコード変更判定テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            old_record = {"date": "2024-01-01", "code": "1234", "Close": 100, "Volume": 1000}
            new_record = {"date": "2024-01-01", "code": "1234", "Close": 101, "Volume": 1000}
            
            result = updater._has_record_changed(old_record, new_record)
            
            # 変更が検出されることを確認
            assert result is True

    def test_has_record_changed_with_identical_values(self):
        """同一値でのレコード変更判定テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            old_record = {"date": "2024-01-01", "code": "1234", "Close": 100, "Volume": 1000}
            new_record = {"date": "2024-01-01", "code": "1234", "Close": 100, "Volume": 1000}
            
            result = updater._has_record_changed(old_record, new_record)
            
            # 変更が検出されないことを確認
            assert result is False

    def test_has_record_changed_with_missing_fields(self):
        """欠損フィールドでのレコード変更判定テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            old_record = {"date": "2024-01-01", "code": "1234", "Close": 100}
            new_record = {"date": "2024-01-01", "code": "1234", "Close": 100, "Volume": 1000}
            
            result = updater._has_record_changed(old_record, new_record)
            
            # 新しいフィールドが追加された場合は変更と判定されることを確認
            assert result is True

    def test_create_error_result(self):
        """エラー結果作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            result = updater._create_error_result(
                "1234", 
                UpdateStatus.FAILED, 
                "Test error message"
            )
            
            # エラー結果の確認
            assert result["success"] is False
            assert result["status"] == "failed"
            assert result["symbol"] == "1234"
            assert result["error"] == "Test error message"
            assert "timestamp" in result

    def test_create_backup_success(self):
        """バックアップ作成成功テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            test_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
            
            # バックアップの作成
            updater._create_backup("1234", test_data)
            
            # バックアップディレクトリの存在確認
            backup_dir = updater.data_dir / "backups" / "1234"
            assert backup_dir.exists()
            
            # バックアップファイルの存在確認
            backup_files = list(backup_dir.glob("backup_*.json"))
            assert len(backup_files) == 1

    def test_create_backup_failure(self):
        """バックアップ作成失敗テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            test_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
            
            # 無効なパスでのバックアップ作成
            with patch.object(updater, 'data_dir', "/invalid/path"):
                # 例外が発生しても処理が継続されることを確認
                updater._create_backup("1234", test_data)

    def test_get_update_statistics(self):
        """更新統計取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            updater = DifferentialUpdater(data_dir=temp_dir)
            
            # 統計の取得
            stats = updater.get_update_statistics()
            
            # 統計項目の確認
            assert "total_updates" in stats
            assert "data_sources" in stats
            assert "symbols_updated" in stats
            assert "recent_updates_7days" in stats
            assert "symbol_statistics" in stats
            assert "last_updated" in stats
