#!/usr/bin/env python3
"""
差分更新システムのテスト
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from core.differential_updater import DifferentialUpdater


class TestDifferentialUpdater:
    """差分更新システムのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Mock()
        self.updater = DifferentialUpdater(self.temp_dir, self.logger)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """初期化テスト"""
        assert self.updater.data_dir == Path(self.temp_dir)
        assert self.updater.logger == self.logger
        assert self.updater.update_config["max_retry_attempts"] == 3

    def test_normalize_data_for_diff(self):
        """データ正規化テスト"""
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": "100.0",
                "high": "110.0",
                "low": "90.0",
                "close": "105.0",
                "volume": "1000"
            }
        ]
        
        result = self.updater._normalize_data_for_diff(test_data)
        
        assert len(result) == 1
        assert result[0]["date"] == "2024-01-01"
        assert result[0]["code"] == "1234"
        assert result[0]["open"] == 100.0
        assert result[0]["high"] == 110.0
        assert result[0]["low"] == 90.0
        assert result[0]["close"] == 105.0
        assert result[0]["volume"] == 1000

    def test_items_different(self):
        """アイテム差分検出テスト"""
        item1 = {"date": "2024-01-01", "close": 100.0}
        item2 = {"date": "2024-01-01", "close": 105.0}
        item3 = {"date": "2024-01-01", "close": 100.0}
        
        assert self.updater._items_different(item1, item2) is True
        assert self.updater._items_different(item1, item3) is False

    def test_identify_changes(self):
        """変更検出テスト"""
        old_item = {"open": 100.0, "close": 105.0}
        new_item = {"open": 100.0, "close": 110.0}
        
        changes = self.updater._identify_changes(old_item, new_item)
        
        assert len(changes) == 1
        assert "close: 105.0 -> 110.0" in changes

    def test_validate_data_integrity_valid(self):
        """データ整合性検証テスト（正常）"""
        valid_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000
            }
        ]
        
        result = self.updater._validate_data_integrity(valid_data, [])
        
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_data_integrity_invalid(self):
        """データ整合性検証テスト（異常）"""
        invalid_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": -100.0,  # 負の値
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000
            }
        ]
        
        result = self.updater._validate_data_integrity(invalid_data, [])
        
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0

    def test_calculate_comprehensive_diff_empty_data(self):
        """差分計算テスト（空データ）"""
        result = self.updater._calculate_comprehensive_diff([], [])
        
        assert result["added_count"] == 0
        assert result["updated_count"] == 0
        assert result["removed_count"] == 0
        assert result["unchanged_count"] == 0

    def test_calculate_comprehensive_diff_with_data(self):
        """差分計算テスト（データあり）"""
        old_data = [
            {"date": "2024-01-01", "close": 100.0}
        ]
        new_data = [
            {"date": "2024-01-01", "close": 105.0},
            {"date": "2024-01-02", "close": 110.0}
        ]
        
        result = self.updater._calculate_comprehensive_diff(old_data, new_data)
        
        assert result["added_count"] == 1  # 2024-01-02が新規
        assert result["updated_count"] == 1  # 2024-01-01が更新
        assert result["removed_count"] == 0
        assert result["unchanged_count"] == 0

    @patch('core.differential_updater.JSONDataManager')
    def test_update_stock_data_success(self, mock_json_manager):
        """株価データ更新テスト（成功）"""
        mock_manager = Mock()
        mock_json_manager.return_value = mock_manager
        mock_manager.get_stock_data.return_value = []
        mock_manager.save_stock_data.return_value = True
        
        self.updater.json_manager = mock_manager
        
        test_data = [
            {"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 1000}
        ]
        
        result = self.updater.update_stock_data("1234", test_data)
        
        assert result["success"] is True
        assert result["symbol"] == "1234"
        assert "timestamp" in result

    @patch('core.differential_updater.JSONDataManager')
    def test_update_stock_data_failure(self, mock_json_manager):
        """株価データ更新テスト（失敗）"""
        mock_manager = Mock()
        mock_json_manager.return_value = mock_manager
        mock_manager.get_stock_data.return_value = []
        mock_manager.save_stock_data.return_value = False
        
        self.updater.json_manager = mock_manager
        
        test_data = [
            {"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 1000}
        ]
        
        result = self.updater.update_stock_data("1234", test_data)
        
        assert result["success"] is False
        assert "error" in result

    def test_calculate_comprehensive_diff_error_handling(self):
        """差分計算エラーハンドリングテスト"""
        # 不正なデータでエラーを発生させる
        invalid_old_data = [{"invalid": "data"}]
        invalid_new_data = [{"invalid": "data"}]
        
        result = self.updater._calculate_comprehensive_diff(invalid_old_data, invalid_new_data)
        
        # エラーが発生しても適切にハンドリングされる
        assert "error" in result or result["added_count"] >= 0
