#!/usr/bin/env python3
"""
差分更新システムの拡張テスト
テストカバレッジ向上のための追加テストケース
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch
from core.differential_updater import DifferentialUpdater


class TestDifferentialUpdaterEnhanced:
    """差分更新システムの拡張テストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Mock()
        self.updater = DifferentialUpdater(self.temp_dir, self.logger)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)

    def test_batch_update_success(self):
        """バッチ更新テスト（成功）"""
        updates = [
            {
                "symbol": "7203",
                "data": [{"date": "2024-01-01", "close": 100.0}],
                "source": "jquants_api",
            },
            {
                "symbol": "6758",
                "data": [{"date": "2024-01-01", "close": 200.0}],
                "source": "jquants_api",
            },
        ]

        with patch.object(self.updater, "update_stock_data") as mock_update:
            mock_update.return_value = {"success": True, "symbol": "test"}
            result = self.updater.batch_update(updates)

            assert result["success"] is True
            assert result["total_updates"] == 2
            assert result["success_count"] == 2
            assert result["error_count"] == 0

    def test_batch_update_partial_failure(self):
        """バッチ更新テスト（部分失敗）"""
        updates = [
            {
                "symbol": "7203",
                "data": [{"date": "2024-01-01", "close": 100.0}],
                "source": "jquants_api",
            },
            {
                "symbol": "6758",
                "data": [{"date": "2024-01-01", "close": 200.0}],
                "source": "jquants_api",
            },
        ]

        with patch.object(self.updater, "update_stock_data") as mock_update:
            mock_update.side_effect = [
                {"success": True, "symbol": "7203"},
                {"success": False, "error": "Test error", "symbol": "6758"},
            ]
            result = self.updater.batch_update(updates)

            assert result["success"] is False  # エラーがある場合はFalse
            assert result["total_updates"] == 2
            assert result["success_count"] == 1
            assert result["error_count"] == 1

    def test_batch_update_all_failure(self):
        """バッチ更新テスト（全失敗）"""
        updates = [
            {
                "symbol": "7203",
                "data": [{"date": "2024-01-01", "close": 100.0}],
                "source": "jquants_api",
            }
        ]

        with patch.object(self.updater, "update_stock_data") as mock_update:
            mock_update.return_value = {"success": False, "error": "Test error"}
            result = self.updater.batch_update(updates)

            assert result["success"] is False
            assert result["total_updates"] == 1
            assert result["success_count"] == 0
            assert result["error_count"] == 1

    def test_batch_update_empty_list(self):
        """バッチ更新テスト（空リスト）"""
        result = self.updater.batch_update([])

        assert result["success"] is True
        assert result["total_updates"] == 0
        assert result["success_count"] == 0
        assert result["error_count"] == 0

    def test_validate_data_integrity_comprehensive(self):
        """データ整合性検証テスト（包括的）"""
        # 正常データ
        valid_data = [
            {
                "date": "2024-01-01",
                "code": "7203",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]

        result = self.updater._validate_data_integrity(valid_data, [])
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

        # 異常データ（負の値）
        invalid_data = [
            {
                "date": "2024-01-01",
                "code": "7203",
                "open": -100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]

        result = self.updater._validate_data_integrity(invalid_data, [])
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0

        # 異常データ（無効な日付）
        invalid_date_data = [
            {
                "date": "invalid-date",
                "code": "7203",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]

        result = self.updater._validate_data_integrity(invalid_date_data, [])
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0

        # 異常データ（価格の論理的整合性）
        invalid_price_data = [
            {
                "date": "2024-01-01",
                "code": "7203",
                "open": 100.0,
                "high": 90.0,  # 高値が始値より低い
                "low": 110.0,  # 安値が始値より高い
                "close": 105.0,
                "volume": 1000,
            }
        ]

        result = self.updater._validate_data_integrity(invalid_price_data, [])
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0

    def test_remove_duplicates(self):
        """重複削除テスト"""
        duplicate_data = [
            {"date": "2024-01-01", "close": 100.0},
            {"date": "2024-01-01", "close": 100.0},  # 重複
            {"date": "2024-01-02", "close": 105.0},
        ]

        result = self.updater._remove_duplicates(duplicate_data)

        assert len(result) == 2
        assert result[0]["date"] == "2024-01-01"
        assert result[1]["date"] == "2024-01-02"

    def test_remove_duplicates_empty_list(self):
        """重複削除テスト（空リスト）"""
        result = self.updater._remove_duplicates([])
        assert result == []

    def test_remove_duplicates_no_duplicates(self):
        """重複削除テスト（重複なし）"""
        unique_data = [
            {"date": "2024-01-01", "close": 100.0},
            {"date": "2024-01-02", "close": 105.0},
        ]

        result = self.updater._remove_duplicates(unique_data)
        assert len(result) == 2
        assert result == unique_data

    def test_update_stock_data_integration(self):
        """株価データ更新統合テスト"""
        symbol = "7203"
        data = [{"date": "2024-01-01", "close": 100.0}]
        source = "jquants_api"

        # 統合テストとしてupdate_stock_dataをテスト
        with patch.object(
            self.updater.json_manager, "save_stock_data", return_value=True
        ):
            with patch.object(
                self.updater.json_manager, "get_stock_data", return_value=[]
            ):
                result = self.updater.update_stock_data(symbol, data, source)
                # 成功することを確認（実際の実装に依存）
                assert isinstance(result, dict)
                assert "success" in result

    def test_get_update_statistics_empty(self):
        """更新統計取得テスト（空データ）"""
        result = self.updater.get_update_statistics()

        assert result["total_updates"] == 0
        assert result["symbols_updated"] == 0
        assert result["recent_updates_7days"] == 0
        assert result["symbol_statistics"] == {}

    def test_get_update_statistics_with_data(self):
        """更新統計取得テスト（データあり）"""
        # 差分ログデータの作成
        diff_log = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "symbol": "7203",
                "diff": {"added_count": 1, "updated_count": 0, "removed_count": 0},
            },
            {
                "timestamp": "2024-01-02T10:00:00",
                "symbol": "6758",
                "diff": {"added_count": 2, "updated_count": 1, "removed_count": 0},
            },
        ]

        diff_log_file = self.updater.data_dir / "diff_log.json"
        with open(diff_log_file, "w", encoding="utf-8") as f:
            json.dump(diff_log, f, ensure_ascii=False, indent=2)

        result = self.updater.get_update_statistics()

        assert result["total_updates"] == 2
        assert result["symbols_updated"] == 2
        assert "7203" in result["symbol_statistics"]
        assert "6758" in result["symbol_statistics"]

    def test_calculate_comprehensive_diff_edge_cases(self):
        """差分計算テスト（エッジケース）"""
        # 空データ同士
        result = self.updater._calculate_comprehensive_diff([], [])
        assert result["added_count"] == 0
        assert result["updated_count"] == 0
        assert result["removed_count"] == 0
        assert result["unchanged_count"] == 0

        # 新規データのみ
        new_data = [{"date": "2024-01-01", "close": 100.0}]
        result = self.updater._calculate_comprehensive_diff([], new_data)
        assert result["added_count"] == 1
        assert result["updated_count"] == 0
        assert result["removed_count"] == 0
        assert result["unchanged_count"] == 0

        # 削除データのみ
        old_data = [{"date": "2024-01-01", "close": 100.0}]
        result = self.updater._calculate_comprehensive_diff(old_data, [])
        assert result["added_count"] == 0
        assert result["updated_count"] == 0
        assert result["removed_count"] == 1
        assert result["unchanged_count"] == 0

    def test_normalize_data_for_diff_edge_cases(self):
        """データ正規化テスト（エッジケース）"""
        # 空リスト
        result = self.updater._normalize_data_for_diff([])
        assert result == []

        # None値の処理
        data_with_none = [
            {
                "date": "2024-01-01",
                "code": "7203",
                "open": None,
                "high": "110.0",
                "low": "90.0",
                "close": "105.0",
                "volume": "1000",
            }
        ]

        result = self.updater._normalize_data_for_diff(data_with_none)
        assert len(result) == 1
        assert result[0]["open"] == 0.0  # Noneは0.0に変換

    def test_items_different_edge_cases(self):
        """アイテム差分検出テスト（エッジケース）"""
        # 完全に同じアイテム
        item1 = {"date": "2024-01-01", "close": 100.0}
        item2 = {"date": "2024-01-01", "close": 100.0}
        assert self.updater._items_different(item1, item2) is False

        # 完全に異なるアイテム
        item3 = {"date": "2024-01-02", "close": 105.0}
        assert self.updater._items_different(item1, item3) is True

        # 一部フィールドが異なる
        item4 = {"date": "2024-01-01", "close": 105.0}
        assert self.updater._items_different(item1, item4) is True

    def test_identify_changes_edge_cases(self):
        """変更検出テスト（エッジケース）"""
        # 変更なし
        old_item = {"open": 100.0, "close": 105.0}
        new_item = {"open": 100.0, "close": 105.0}
        changes = self.updater._identify_changes(old_item, new_item)
        assert len(changes) == 0

        # 全フィールド変更
        old_item2 = {"open": 100.0, "close": 105.0}
        new_item2 = {"open": 110.0, "close": 115.0}
        changes = self.updater._identify_changes(old_item2, new_item2)
        assert len(changes) == 2
        assert "open: 100.0 -> 110.0" in changes
        assert "close: 105.0 -> 115.0" in changes

    def test_update_config_modification(self):
        """更新設定変更テスト"""
        # デフォルト設定の確認
        assert self.updater.update_config["max_retry_attempts"] == 3
        assert self.updater.update_config["batch_size"] == 100
        assert self.updater.update_config["enable_validation"] is True
        assert self.updater.update_config["enable_compression"] is False

        # 設定の変更
        self.updater.update_config["max_retry_attempts"] = 5
        self.updater.update_config["batch_size"] = 50
        self.updater.update_config["enable_validation"] = False
        self.updater.update_config["enable_compression"] = True

        assert self.updater.update_config["max_retry_attempts"] == 5
        assert self.updater.update_config["batch_size"] == 50
        assert self.updater.update_config["enable_validation"] is False
        assert self.updater.update_config["enable_compression"] is True

    def test_error_handling_in_update_stock_data(self):
        """update_stock_dataのエラーハンドリングテスト"""
        # 無効なデータでのテスト
        invalid_data = None

        result = self.updater.update_stock_data("7203", invalid_data)
        assert result["success"] is False
        assert "error" in result

    def test_error_handling_in_batch_update(self):
        """batch_updateのエラーハンドリングテスト"""
        # 無効な更新データ
        invalid_updates = None

        with pytest.raises(TypeError):
            self.updater.batch_update(invalid_updates)

    def test_error_handling_in_get_update_statistics(self):
        """get_update_statisticsのエラーハンドリングテスト"""
        # 破損した差分ログファイルの作成
        diff_log_file = self.updater.data_dir / "diff_log.json"
        with open(diff_log_file, "w", encoding="utf-8") as f:
            f.write("invalid json")

        result = self.updater.get_update_statistics()
        # エラー時はデフォルト値を持つ辞書を返す
        assert isinstance(result, dict)
        assert "total_updates" in result
        assert "symbols_updated" in result
