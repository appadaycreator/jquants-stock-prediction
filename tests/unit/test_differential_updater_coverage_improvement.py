#!/usr/bin/env python3
"""
差分更新システムのカバレッジ向上テスト
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from core.differential_updater import (
    DifferentialUpdater,
    DiffResult,
    ValidationResult,
    UpdateStats,
)


class TestDifferentialUpdaterCoverageImprovement:
    """差分更新システムのカバレッジ向上テスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir()

        self.logger = Mock()
        self.error_handler = Mock()
        self.updater = DifferentialUpdater(str(self.data_dir), self.logger)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_update_statistics(self):
        """更新統計の取得テスト"""
        # 統計データの設定
        self.updater.update_stats.total_updates = 10
        self.updater.update_stats.successful_updates = 8
        self.updater.update_stats.failed_updates = 2
        self.updater.update_stats.validation_errors = 1
        self.updater.update_stats.total_processing_time = 5.5
        self.updater.update_stats.last_update_time = datetime.now()

        stats = self.updater.get_update_statistics()

        assert stats["total_updates"] == 10
        assert stats["successful_updates"] == 8
        assert stats["failed_updates"] == 2
        assert stats["validation_errors"] == 1
        assert stats["total_processing_time"] == 5.5
        assert stats["success_rate"] == 0.8
        assert stats["validation_error_rate"] == 0.1

    def test_get_update_statistics_zero_division(self):
        """更新統計のゼロ除算テスト"""
        # ゼロ除算のケース
        self.updater.update_stats.total_updates = 0
        self.updater.update_stats.successful_updates = 0
        self.updater.update_stats.validation_errors = 0

        stats = self.updater.get_update_statistics()

        assert stats["success_rate"] == 0.0
        assert stats["validation_error_rate"] == 0.0

    def test_calculate_comprehensive_diff(self):
        """包括的差分計算のテスト"""
        existing_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 105},
        ]
        new_data = [
            {"date": "2024-01-01", "code": "1234", "close": 100},
            {"date": "2024-01-02", "code": "1234", "close": 110},
            {"date": "2024-01-03", "code": "1234", "close": 115},
        ]

        with (
            patch.object(self.updater, "_calculate_data_hash") as mock_hash,
            patch.object(self.updater, "_calculate_diff_counts") as mock_counts,
            patch.object(self.updater, "_is_significant_change") as mock_significant,
        ):

            mock_hash.side_effect = ["hash1", "hash2"]
            mock_counts.return_value = {
                "added": 1,
                "updated": 1,
                "removed": 0,
                "unchanged": 1,
            }
            mock_significant.return_value = True

            result = self.updater._calculate_comprehensive_diff(existing_data, new_data)

            assert isinstance(result, DiffResult)
            assert result.added_count == 1
            assert result.updated_count == 1
            assert result.removed_count == 0
            assert result.unchanged_count == 1
            assert result.is_significant_change is True

    def test_validate_data_integrity_negative_prices(self):
        """データ整合性検証 - 負の価格テスト"""
        new_data = [
            {"Open": -100, "High": 200, "Low": 50, "Close": 150, "Volume": 1000},
            {"Open": 100, "High": -200, "Low": 50, "Close": 150, "Volume": 1000},
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert not result.is_valid
        assert len(result.issues) > 0
        assert any("負の価格" in issue for issue in result.issues)

    def test_validate_data_integrity_high_low_consistency(self):
        """データ整合性検証 - 高値・安値の整合性テスト"""
        new_data = [
            {
                "Open": 100,
                "High": 50,
                "Low": 200,
                "Close": 150,
                "Volume": 1000,
            }  # High < Low
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert not result.is_valid
        assert any("High価格がLow価格より低い" in issue for issue in result.issues)

    def test_validate_data_integrity_price_consistency(self):
        """データ整合性検証 - 価格の整合性テスト"""
        new_data = [
            {
                "Open": 100,
                "High": 50,
                "Low": 200,
                "Close": 150,
                "Volume": 1000,
            }  # High < Open/Close
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert not result.is_valid
        assert any(
            "High価格がOpen/Close価格より低い" in issue for issue in result.issues
        )

    def test_validate_data_integrity_low_price_consistency(self):
        """データ整合性検証 - 安値の整合性テスト"""
        new_data = [
            {
                "Open": 100,
                "High": 200,
                "Low": 150,
                "Close": 50,
                "Volume": 1000,
            }  # Low > Open/Close
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert not result.is_valid
        assert any(
            "Low価格がOpen/Close価格より高い" in issue for issue in result.issues
        )

    def test_validate_data_integrity_extreme_price_change(self):
        """データ整合性検証 - 極端な価格変動テスト"""
        existing_data = [
            {"Open": 100, "High": 200, "Low": 50, "Close": 100, "Volume": 1000}
        ]
        new_data = [
            {
                "Open": 100,
                "High": 200,
                "Low": 50,
                "Close": 200,
                "Volume": 1000,
            }  # 100%変動
        ]

        result = self.updater._validate_data_integrity(new_data, existing_data)

        # 警告は出るが、バリデーションは通る
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("極端な価格変動" in warning for warning in result.warnings)

    def test_validate_data_integrity_price_parsing_error(self):
        """データ整合性検証 - 価格解析エラーテスト"""
        new_data = [
            {"Open": "invalid", "High": 200, "Low": 50, "Close": 150, "Volume": 1000}
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert not result.is_valid
        assert any("価格データの解析エラー" in issue for issue in result.issues)

    def test_validate_data_integrity_date_validation(self):
        """データ整合性検証 - 日付検証テスト"""
        new_data = [
            {
                "Date": "invalid-date",
                "Open": 100,
                "High": 200,
                "Low": 50,
                "Close": 150,
                "Volume": 1000,
            }
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert not result.is_valid
        assert any("日付の解析エラー" in issue for issue in result.issues)

    def test_validate_data_integrity_volume_validation(self):
        """データ整合性検証 - ボリューム検証テスト"""
        new_data = [
            {"Open": 100, "High": 200, "Low": 50, "Close": 150, "Volume": "invalid"}
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert not result.is_valid
        assert any("Volume" in issue for issue in result.issues)

    def test_validate_data_integrity_success(self):
        """データ整合性検証 - 成功ケース"""
        new_data = [
            {"Open": 100, "High": 200, "Low": 50, "Close": 150, "Volume": 1000},
            {"Open": 150, "High": 250, "Low": 100, "Close": 200, "Volume": 2000},
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)

        assert result.is_valid
        assert len(result.issues) == 0
        assert result.data_quality_score > 0.8

    def test_has_record_changed_true(self):
        """レコード変更検出 - 変更あり"""
        old_record = {"date": "2024-01-01", "close": 100}
        new_record = {"date": "2024-01-01", "close": 105}

        with patch.object(self.updater, "_calculate_hash") as mock_hash:
            mock_hash.side_effect = ["hash1", "hash2"]

            result = self.updater._has_record_changed(old_record, new_record)

            assert result is True

    def test_has_record_changed_false(self):
        """レコード変更検出 - 変更なし"""
        old_record = {"date": "2024-01-01", "close": 100}
        new_record = {"date": "2024-01-01", "close": 100}

        with patch.object(self.updater, "_calculate_hash") as mock_hash:
            mock_hash.side_effect = ["hash1", "hash1"]

            result = self.updater._has_record_changed(old_record, new_record)

            assert result is False

    def test_has_record_changed_exception(self):
        """レコード変更検出 - 例外処理"""
        old_record = {"date": "2024-01-01", "close": 100}
        new_record = {"date": "2024-01-01", "close": 105}

        with patch.object(
            self.updater, "_calculate_hash", side_effect=Exception("Hash error")
        ):
            result = self.updater._has_record_changed(old_record, new_record)

            assert result is False

    def test_calculate_diff_counts_empty_data(self):
        """差分計算 - 空データ"""
        existing_data = []
        new_data = []

        result = self.updater._calculate_diff_counts(existing_data, new_data)

        assert result["added"] == 0
        assert result["updated"] == 0
        assert result["removed"] == 0
        assert result["unchanged"] == 0

    def test_calculate_diff_counts_new_data_only(self):
        """差分計算 - 新データのみ"""
        existing_data = []
        new_data = [
            {"date": "2024-01-01", "close": 100},
            {"date": "2024-01-02", "close": 105},
        ]

        result = self.updater._calculate_diff_counts(existing_data, new_data)

        assert result["added"] == 2
        assert result["updated"] == 0
        assert result["removed"] == 0
        assert result["unchanged"] == 0

    def test_calculate_diff_counts_removed_data_only(self):
        """差分計算 - 削除データのみ"""
        existing_data = [
            {"date": "2024-01-01", "close": 100},
            {"date": "2024-01-02", "close": 105},
        ]
        new_data = []

        result = self.updater._calculate_diff_counts(existing_data, new_data)

        assert result["added"] == 0
        assert result["updated"] == 0
        assert result["removed"] == 2
        assert result["unchanged"] == 0

    def test_calculate_diff_counts_mixed_changes(self):
        """差分計算 - 混合変更"""
        existing_data = [
            {"date": "2024-01-01", "close": 100},
            {"date": "2024-01-02", "close": 105},
        ]
        new_data = [
            {"date": "2024-01-01", "close": 100},  # unchanged
            {"date": "2024-01-02", "close": 110},  # updated
            {"date": "2024-01-03", "close": 115},  # added
        ]

        with patch.object(self.updater, "_has_record_changed") as mock_changed:
            mock_changed.side_effect = [False, True]  # 1つ目は変更なし、2つ目は変更あり

            result = self.updater._calculate_diff_counts(existing_data, new_data)

            assert result["added"] == 1
            assert result["updated"] == 1
            assert result["removed"] == 0
            assert result["unchanged"] == 1

    def test_is_significant_change_true(self):
        """重要な変更判定 - 変更あり"""
        diff_counts = {"added": 10, "updated": 5, "removed": 2, "unchanged": 1}

        result = self.updater._is_significant_change(diff_counts)

        assert result is True

    def test_is_significant_change_false(self):
        """重要な変更判定 - 変更なし"""
        diff_counts = {"added": 1, "updated": 0, "removed": 0, "unchanged": 100}

        result = self.updater._is_significant_change(diff_counts)

        assert result is False

    def test_is_significant_change_threshold(self):
        """重要な変更判定 - 閾値境界"""
        diff_counts = {"added": 5, "updated": 0, "removed": 0, "unchanged": 95}

        result = self.updater._is_significant_change(diff_counts)

        assert result is True  # 5%の変更は閾値を超える

    def test_calculate_data_hash(self):
        """データハッシュ計算テスト"""
        data = [
            {"date": "2024-01-01", "close": 100},
            {"date": "2024-01-02", "close": 105},
        ]

        hash1 = self.updater._calculate_data_hash(data)
        hash2 = self.updater._calculate_data_hash(data)

        assert hash1 == hash2  # 同じデータは同じハッシュ

        # データを変更してハッシュが変わることを確認
        data[0]["close"] = 110
        hash3 = self.updater._calculate_data_hash(data)

        assert hash1 != hash3  # 異なるデータは異なるハッシュ

    def test_calculate_data_hash_empty(self):
        """データハッシュ計算 - 空データ"""
        data = []

        hash_value = self.updater._calculate_data_hash(data)

        assert isinstance(hash_value, str)
        assert len(hash_value) > 0

    def test_calculate_data_hash_none(self):
        """データハッシュ計算 - Noneデータ"""
        data = None

        hash_value = self.updater._calculate_data_hash(data)

        assert isinstance(hash_value, str)
        assert len(hash_value) > 0

    def test_calculate_hash(self):
        """ハッシュ計算テスト"""
        data = {"date": "2024-01-01", "close": 100}

        hash1 = self.updater._calculate_hash(data)
        hash2 = self.updater._calculate_hash(data)

        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) > 0

    def test_calculate_hash_different_data(self):
        """ハッシュ計算 - 異なるデータ"""
        data1 = {"date": "2024-01-01", "close": 100}
        data2 = {"date": "2024-01-01", "close": 105}

        hash1 = self.updater._calculate_hash(data1)
        hash2 = self.updater._calculate_hash(data2)

        assert hash1 != hash2

    def test_calculate_hash_none(self):
        """ハッシュ計算 - Noneデータ"""
        data = None

        hash_value = self.updater._calculate_hash(data)

        assert isinstance(hash_value, str)
        assert len(hash_value) > 0

    def test_calculate_hash_exception(self):
        """ハッシュ計算 - 例外処理"""
        data = {"date": "2024-01-01", "close": 100}

        with patch("json.dumps", side_effect=Exception("JSON error")):
            hash_value = self.updater._calculate_hash(data)

            assert isinstance(hash_value, str)
            assert len(hash_value) > 0

    def test_backup_data_success(self):
        """データバックアップ - 成功"""
        symbol = "1234"
        data = [{"date": "2024-01-01", "close": 100}]

        with patch.object(self.updater, "_create_backup_dir") as mock_dir:
            mock_dir.return_value = self.data_dir / "backups" / "1234"

            result = self.updater._backup_data(symbol, data)

            assert result is True

    def test_backup_data_failure(self):
        """データバックアップ - 失敗"""
        symbol = "1234"
        data = [{"date": "2024-01-01", "close": 100}]

        with patch.object(
            self.updater, "_create_backup_dir", side_effect=Exception("Backup error")
        ):
            result = self.updater._backup_data(symbol, data)

            assert result is False

    def test_create_backup_dir(self):
        """バックアップディレクトリ作成テスト"""
        symbol = "1234"

        backup_dir = self.updater._create_backup_dir(symbol)

        assert backup_dir.exists()
        assert backup_dir.name == "1234"
        assert "backups" in str(backup_dir)

    def test_create_backup_dir_exception(self):
        """バックアップディレクトリ作成 - 例外処理"""
        symbol = "1234"

        with patch("pathlib.Path.mkdir", side_effect=Exception("Directory error")):
            backup_dir = self.updater._create_backup_dir(symbol)

            assert backup_dir is None

    def test_update_statistics_initialization(self):
        """更新統計の初期化テスト"""
        stats = UpdateStats()

        assert stats.total_updates == 0
        assert stats.successful_updates == 0
        assert stats.failed_updates == 0
        assert stats.validation_errors == 0
        assert stats.total_processing_time == 0.0
        assert stats.last_update_time is None

    def test_update_statistics_increment(self):
        """更新統計の増分テスト"""
        stats = UpdateStats()

        stats.increment_total_updates()
        stats.increment_successful_updates()
        stats.increment_failed_updates()
        stats.increment_validation_errors()
        stats.add_processing_time(1.5)
        stats.set_last_update_time(datetime.now())

        assert stats.total_updates == 1
        assert stats.successful_updates == 1
        assert stats.failed_updates == 1
        assert stats.validation_errors == 1
        assert stats.total_processing_time == 1.5
        assert stats.last_update_time is not None

    def test_diff_result_initialization(self):
        """差分結果の初期化テスト"""
        result = DiffResult(
            added_count=1,
            updated_count=2,
            removed_count=0,
            unchanged_count=3,
            processing_time=1.5,
            data_hash="hash123",
            is_significant_change=True,
        )

        assert result.added_count == 1
        assert result.updated_count == 2
        assert result.removed_count == 0
        assert result.unchanged_count == 3
        assert result.processing_time == 1.5
        assert result.data_hash == "hash123"
        assert result.is_significant_change is True

    def test_validation_result_initialization(self):
        """検証結果の初期化テスト"""
        result = ValidationResult(
            is_valid=True,
            issues=["issue1"],
            warnings=["warning1"],
            data_quality_score=0.8,
        )

        assert result.is_valid is True
        assert result.issues == ["issue1"]
        assert result.warnings == ["warning1"]
        assert result.data_quality_score == 0.8

    def test_validation_result_invalid(self):
        """検証結果 - 無効データ"""
        result = ValidationResult(
            is_valid=False,
            issues=["critical error"],
            warnings=[],
            data_quality_score=0.0,
        )

        assert result.is_valid is False
        assert len(result.issues) == 1
        assert len(result.warnings) == 0
        assert result.data_quality_score == 0.0
