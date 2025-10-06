#!/usr/bin/env python3
"""
差分更新システムのカバレッジ向上テスト
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from core.differential_updater import (
    DifferentialUpdater,
    UpdateStatus,
    ValidationResult,
    UpdateStats,
    DiffResult,
)


class TestDifferentialUpdaterCoverageImprovement:
    """差分更新システムのカバレッジ向上テスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.updater = DifferentialUpdater(self.temp_dir)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validation_result_post_init(self):
        """ValidationResultのpost_initテスト"""
        # warningsがNoneの場合
        result = ValidationResult(
            is_valid=True, issues=["test issue"], warnings=None, data_quality_score=0.8
        )
        assert result.warnings == []

        # warningsが設定されている場合
        result = ValidationResult(
            is_valid=True,
            issues=["test issue"],
            warnings=["warning1", "warning2"],
            data_quality_score=0.8,
        )
        assert result.warnings == ["warning1", "warning2"]

    def test_update_stats_initialization(self):
        """UpdateStatsの初期化テスト"""
        stats = UpdateStats()
        assert stats.total_updates == 0
        assert stats.successful_updates == 0
        assert stats.failed_updates == 0
        assert stats.validation_errors == 0
        assert stats.total_processing_time == 0.0
        assert stats.last_update_time is None

    def test_diff_result_initialization(self):
        """DiffResultの初期化テスト"""
        result = DiffResult(
            added_count=2,
            updated_count=3,
            removed_count=1,
            unchanged_count=5,
            processing_time=1.5,
            data_hash="test_hash",
            is_significant_change=True,
            symbol="7203",
            status="success",
            changes_count=5,
        )
        assert result.added_count == 2
        assert result.updated_count == 3
        assert result.removed_count == 1
        assert result.unchanged_count == 5
        assert result.processing_time == 1.5
        assert result.symbol == "7203"
        assert result.status == "success"
        assert result.changes_count == 5
        assert result.data_hash == "test_hash"
        assert result.is_significant_change is True

    def test_remove_duplicates(self):
        """重複データ除去テスト"""
        data = [
            {"date": "2024-01-01", "close": 100},
            {"date": "2024-01-02", "close": 101},
            {"date": "2024-01-01", "close": 100},  # 重複
            {"date": "2024-01-03", "close": 102},
        ]

        result = self.updater._remove_duplicates(data)
        assert len(result) == 3
        assert result[0]["date"] == "2024-01-01"
        assert result[1]["date"] == "2024-01-02"
        assert result[2]["date"] == "2024-01-03"

    def test_normalize_data_for_diff(self):
        """差分用データ正規化テスト"""
        data = [
            {
                "Date": "2024-01-01",
                "Open": "100.5",
                "High": "105.0",
                "Low": "98.0",
                "Close": "102.0",
                "Volume": "1000000",
            },
            {
                "date": "2024-01-02",
                "open": "102.0",
                "high": "108.0",
                "low": "100.0",
                "close": "106.0",
                "volume": "1200000",
            },
        ]

        result = self.updater._normalize_data_for_diff(data)
        assert len(result) == 2
        assert result[0]["date"] == "2024-01-01"
        assert result[0]["open"] == 100.5
        assert result[0]["high"] == 105.0
        assert result[0]["low"] == 98.0
        assert result[0]["close"] == 102.0
        assert result[0]["volume"] == 1000000.0

    def test_normalize_data_for_diff_invalid_values(self):
        """無効な値での正規化テスト"""
        data = [
            {
                "date": "2024-01-01",
                "open": "invalid",
                "high": None,
                "low": "98.0",
                "close": "102.0",
                "volume": "1000000",
            }
        ]

        result = self.updater._normalize_data_for_diff(data)
        assert len(result) == 1
        assert result[0]["open"] == 0.0  # 無効な値は0.0に変換
        assert result[0]["high"] == 0.0  # Noneは0.0に変換

    def test_items_different(self):
        """アイテム差分判定テスト"""
        item1 = {"date": "2024-01-01", "close": 100}
        item2 = {"date": "2024-01-01", "close": 101}
        item3 = {"date": "2024-01-01", "close": 100}

        # 異なるアイテム
        assert self.updater._items_different(item1, item2) is True

        # 同じアイテム
        assert self.updater._items_different(item1, item3) is False

    def test_items_different_case_insensitive(self):
        """大文字小文字を考慮した差分判定テスト"""
        item1 = {"Date": "2024-01-01", "Close": 100}
        item2 = {"date": "2024-01-01", "close": 101}

        assert self.updater._items_different(item1, item2) is True

    def test_identify_changes(self):
        """変更識別テスト"""
        old_item = {"date": "2024-01-01", "close": 100, "volume": 1000000}
        new_item = {"date": "2024-01-01", "close": 101, "volume": 1200000}

        changes = self.updater._identify_changes(old_item, new_item)
        assert len(changes) == 2
        assert any("close: 100 -> 101" in change for change in changes)
        assert any("volume: 1000000 -> 1200000" in change for change in changes)

    def test_identify_changes_case_insensitive(self):
        """大文字小文字を考慮した変更識別テスト"""
        old_item = {"Date": "2024-01-01", "Close": 100}
        new_item = {"date": "2024-01-01", "close": 101}

        changes = self.updater._identify_changes(old_item, new_item)
        assert len(changes) == 1
        assert "close: 100 -> 101" in changes[0]

    def test_validate_data_integrity_success(self):
        """データ整合性検証成功テスト"""
        new_data = [
            {
                "date": "2024-01-01",
                "code": "7203",
                "open": 100,
                "high": 105,
                "low": 98,
                "close": 102,
                "volume": 1000000,
            },
            {
                "date": "2024-01-02",
                "code": "7203",
                "open": 102,
                "high": 108,
                "low": 100,
                "close": 106,
                "volume": 1200000,
            },
        ]
        existing_data = [
            {
                "date": "2024-01-01",
                "code": "7203",
                "open": 100,
                "high": 105,
                "low": 98,
                "close": 100,
                "volume": 1000000,
            }
        ]

        result = self.updater._validate_data_integrity(new_data, existing_data)
        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_validate_data_integrity_issues(self):
        """データ整合性検証問題テスト"""
        new_data = [
            {"date": "2024-01-01", "close": 100, "volume": 1000000},
            {"date": "2024-01-02", "close": -50, "volume": -1000},  # 異常値
        ]
        existing_data = []

        result = self.updater._validate_data_integrity(new_data, existing_data)
        assert result.is_valid is False
        assert len(result.issues) > 0

    def test_batch_update_success(self):
        """バッチ更新成功テスト"""
        updates = [
            {"symbol": "7203", "data": [{"date": "2024-01-01", "close": 100}]},
            {"symbol": "6758", "data": [{"date": "2024-01-01", "close": 200}]},
        ]

        # モックの設定
        with patch.object(
            self.updater,
            "update_stock_data",
            side_effect=[
                {"success": True, "status": "success"},
                {"success": True, "status": "success"},
            ],
        ):
            result = self.updater.batch_update(updates)
            assert result["success"] is True
            assert result["total"] == 2
            assert result["successful"] == 2
            assert result["failed"] == 0

    def test_batch_update_partial_failure(self):
        """バッチ更新部分失敗テスト"""
        updates = [
            {"symbol": "7203", "data": [{"date": "2024-01-01", "close": 100}]},
            {"symbol": "6758", "data": [{"date": "2024-01-01", "close": 200}]},
        ]

        # モックの設定
        with patch.object(
            self.updater,
            "update_stock_data",
            side_effect=[
                {"success": True, "status": "success"},
                {"success": False, "status": "failed"},
            ],
        ):
            result = self.updater.batch_update(updates)
            assert result["success"] is False
            assert result["total"] == 2
            assert result["successful"] == 1
            assert result["failed"] == 1

    def test_batch_update_exception(self):
        """バッチ更新例外テスト"""
        updates = [{"symbol": "7203", "data": []}]

        # 例外を発生させる
        with patch.object(
            self.updater, "update_stock_data", side_effect=Exception("Test error")
        ):
            result = self.updater.batch_update(updates)
            assert result["success"] is False
            assert result["status"] == "error"
            assert "Test error" in result["error"]

    def test_get_update_history(self):
        """更新履歴取得テスト"""
        mock_log = [
            {"symbol": "7203", "timestamp": "2024-01-01T10:00:00", "status": "success"},
            {"symbol": "6758", "timestamp": "2024-01-01T11:00:00", "status": "success"},
            {"symbol": "7203", "timestamp": "2024-01-01T12:00:00", "status": "failed"},
        ]

        with patch.object(
            self.updater.json_manager, "get_diff_log", return_value=mock_log
        ):
            # 全履歴取得
            result = self.updater.get_update_history()
            assert len(result) == 3

            # 特定銘柄の履歴取得
            result = self.updater.get_update_history(symbol="7203")
            assert len(result) == 2
            assert all(entry["symbol"] == "7203" for entry in result)

    def test_get_update_history_exception(self):
        """更新履歴取得例外テスト"""
        with patch.object(
            self.updater.json_manager,
            "get_diff_log",
            side_effect=Exception("Test error"),
        ):
            result = self.updater.get_update_history()
            assert result == []

    def test_get_update_statistics(self):
        """更新統計取得テスト"""
        # 統計データの設定
        self.updater.update_stats.total_updates = 100
        self.updater.update_stats.successful_updates = 80
        self.updater.update_stats.failed_updates = 15
        self.updater.update_stats.validation_errors = 5
        self.updater.update_stats.total_processing_time = 120.5
        self.updater.update_stats.last_update_time = "2024-01-01T10:00:00"
        self.updater.update_stats.data_sources = ["7203", "6758"]

        result = self.updater.get_update_statistics()

        assert result["total_updates"] == 100
        assert result["successful_updates"] == 80
        assert result["failed_updates"] == 15
        assert result["validation_errors"] == 5
        assert result["total_processing_time"] == 120.5
        assert result["last_update_time"] == "2024-01-01T10:00:00"
        assert result["success_rate"] == 0.8
        assert result["validation_error_rate"] == 0.05
        assert result["symbols_updated"] == 2

    def test_get_update_statistics_exception(self):
        """更新統計取得例外テスト"""
        self.updater.update_stats = None  # 例外を発生させる

        result = self.updater.get_update_statistics()
        assert result == {}

    def test_optimize_data_structure_no_data(self):
        """データ構造最適化（データなし）テスト"""
        with patch.object(
            self.updater.json_manager, "get_stock_data", return_value=None
        ):
            result = self.updater.optimize_data_structure("7203")
            assert result["success"] is False
            assert "データが見つかりません" in result["message"]

    def test_optimize_data_structure_success(self):
        """データ構造最適化成功テスト"""
        data = [
            {"date": "2024-01-01", "close": 100, "volume": 1000000},
            {"date": "2024-01-02", "close": 101, "volume": 1200000},
            {"date": "2024-01-03", "close": 102, "volume": 1100000},
        ]

        with patch.object(
            self.updater.json_manager, "get_stock_data", return_value=data
        ), patch.object(
            self.updater.json_manager, "save_stock_data", return_value=True
        ):
            result = self.updater.optimize_data_structure("7203")
            assert result["success"] is True
            assert "original_count" in result
            assert "optimized_count" in result

    def test_optimize_data_structure_save_failure(self):
        """データ構造最適化保存失敗テスト"""
        data = [{"date": "2024-01-01", "close": 100}]

        with patch.object(
            self.updater.json_manager, "get_stock_data", return_value=data
        ), patch.object(
            self.updater.json_manager, "save_stock_data", return_value=False
        ):
            result = self.updater.optimize_data_structure("7203")
            assert result["success"] is False
            assert "error" in result

    def test_optimize_data_structure_exception(self):
        """データ構造最適化例外テスト"""
        with patch.object(
            self.updater.json_manager,
            "get_stock_data",
            side_effect=Exception("Test error"),
        ):
            result = self.updater.optimize_data_structure("7203")
            assert result["success"] is False
            assert "Test error" in result["error"]

    def test_create_error_result(self):
        """エラー結果作成テスト"""
        result = self.updater._create_error_result(
            UpdateStatus.FAILED, "7203", "Test error message"
        )

        assert result["success"] is False
        assert result["status"] == "failed"
        assert result["symbol"] == "7203"
        assert result["error"] == "Test error message"
        assert "timestamp" in result

    def test_normalize_data_for_diff_empty_data(self):
        """空データでの正規化テスト"""
        result = self.updater._normalize_data_for_diff([])
        assert result == []

    def test_normalize_data_for_diff_exception(self):
        """正規化処理例外テスト"""
        # 例外を発生させるデータ
        data = [{"date": "2024-01-01"}]  # 必要なフィールドが不足

        with patch.object(self.updater, "logger") as mock_logger:
            result = self.updater._normalize_data_for_diff(data)
            # 正規化されたデータが返される（不足フィールドは0.0で補完される）
            assert len(result) == 1
            assert result[0]["date"] == "2024-01-01"
            assert result[0]["open"] == 0.0
            assert result[0]["high"] == 0.0
            assert result[0]["low"] == 0.0
            assert result[0]["close"] == 0.0
            assert result[0]["volume"] == 0.0

    def test_items_different_exception(self):
        """アイテム差分判定例外テスト"""
        # 例外を発生させるデータ
        item1 = {"date": "2024-01-01"}
        item2 = None  # Noneで例外を発生

        result = self.updater._items_different(item1, item2)
        assert result is True  # 例外時はTrueを返す

    def test_identify_changes_exception(self):
        """変更識別例外テスト"""
        # 例外を発生させるデータ
        old_item = {"date": "2024-01-01"}
        new_item = None  # Noneで例外を発生

        result = self.updater._identify_changes(old_item, new_item)
        assert result == []  # 例外時は空リストを返す

    def test_validate_data_integrity_exception(self):
        """データ整合性検証例外テスト"""
        # 例外を発生させるデータ
        new_data = None
        existing_data = None

        result = self.updater._validate_data_integrity(new_data, existing_data)
        assert result.is_valid is False
        assert len(result.issues) > 0
