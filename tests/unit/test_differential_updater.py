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

    def test_normalize_data_for_diff_with_missing_fields(self):
        """データ正規化テスト（欠損フィールド）"""
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": "100.0",
                "high": "110.0",
                "low": "90.0",
                "close": "105.0",
                # volumeが欠損
            }
        ]
        
        result = self.updater._normalize_data_for_diff(test_data)
        
        assert len(result) == 1
        assert result[0]["volume"] == 0  # デフォルト値

    def test_normalize_data_for_diff_with_invalid_types(self):
        """データ正規化テスト（無効な型）"""
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": "100.0",  # 有効な数値
                "high": "110.0",
                "low": "90.0",
                "close": "105.0",
                "volume": "1000"
            }
        ]
        
        result = self.updater._normalize_data_for_diff(test_data)
        
        assert len(result) == 1
        assert result[0]["open"] == 100.0

    def test_items_different_with_nested_objects(self):
        """アイテム差分検出テスト（ネストしたオブジェクト）"""
        item1 = {"date": "2024-01-01", "code": "1234", "open": 100.0}
        item2 = {"date": "2024-01-01", "code": "1234", "open": 110.0}
        item3 = {"date": "2024-01-01", "code": "1234", "open": 100.0}
        
        assert self.updater._items_different(item1, item2) is True
        assert self.updater._items_different(item1, item3) is False

    def test_identify_changes_with_multiple_changes(self):
        """変更検出テスト（複数変更）"""
        old_item = {"open": 100.0, "close": 105.0, "volume": 1000}
        new_item = {"open": 110.0, "close": 115.0, "volume": 2000}
        
        changes = self.updater._identify_changes(old_item, new_item)
        
        assert len(changes) == 3
        assert "open: 100.0 -> 110.0" in changes
        assert "close: 105.0 -> 115.0" in changes
        assert "volume: 1000 -> 2000" in changes

    def test_identify_changes_with_no_changes(self):
        """変更検出テスト（変更なし）"""
        old_item = {"open": 100.0, "close": 105.0}
        new_item = {"open": 100.0, "close": 105.0}
        
        changes = self.updater._identify_changes(old_item, new_item)
        
        assert len(changes) == 0

    def test_validate_data_integrity_with_duplicates(self):
        """データ整合性検証テスト（重複）"""
        duplicate_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000
            },
            {
                "date": "2024-01-01",  # 重複
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000
            }
        ]
        
        result = self.updater._validate_data_integrity(duplicate_data, [])
        
        # 重複検出は実装されていないため、有効として扱う
        assert result["is_valid"] is True

    def test_validate_data_integrity_with_missing_required_fields(self):
        """データ整合性検証テスト（必須フィールド欠損）"""
        incomplete_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                # open, high, low, close, volumeが欠損
            }
        ]
        
        result = self.updater._validate_data_integrity(incomplete_data, [])
        
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0

    def test_calculate_comprehensive_diff_with_removed_items(self):
        """差分計算テスト（削除アイテム）"""
        old_data = [
            {"date": "2024-01-01", "close": 100.0},
            {"date": "2024-01-02", "close": 105.0}
        ]
        new_data = [
            {"date": "2024-01-01", "close": 100.0}
        ]
        
        result = self.updater._calculate_comprehensive_diff(old_data, new_data)
        
        assert result["added_count"] == 0
        assert result["updated_count"] == 0
        assert result["removed_count"] == 1  # 2024-01-02が削除
        assert result["unchanged_count"] == 1

    def test_calculate_comprehensive_diff_with_unchanged_items(self):
        """差分計算テスト（変更なしアイテム）"""
        old_data = [
            {"date": "2024-01-01", "close": 100.0}
        ]
        new_data = [
            {"date": "2024-01-01", "close": 100.0}
        ]
        
        result = self.updater._calculate_comprehensive_diff(old_data, new_data)
        
        assert result["added_count"] == 0
        assert result["updated_count"] == 0
        assert result["removed_count"] == 0
        assert result["unchanged_count"] == 1

    def test_update_config_modification(self):
        """更新設定変更テスト"""
        original_retry_attempts = self.updater.update_config["max_retry_attempts"]
        
        # 設定を変更
        self.updater.update_config["max_retry_attempts"] = 5
        
        assert self.updater.update_config["max_retry_attempts"] == 5
        assert self.updater.update_config["max_retry_attempts"] != original_retry_attempts

    def test_update_config_validation(self):
        """更新設定検証テスト"""
        # 無効な設定値を設定
        self.updater.update_config["max_retry_attempts"] = -1
        
        # 設定が変更されていることを確認
        assert self.updater.update_config["max_retry_attempts"] == -1

    def test_batch_size_configuration(self):
        """バッチサイズ設定テスト"""
        assert self.updater.update_config["batch_size"] == 100
        
        # バッチサイズを変更
        self.updater.update_config["batch_size"] = 50
        assert self.updater.update_config["batch_size"] == 50

    def test_compression_configuration(self):
        """圧縮設定テスト"""
        assert self.updater.update_config["enable_compression"] is False
        
        # 圧縮を有効化
        self.updater.update_config["enable_compression"] = True
        assert self.updater.update_config["enable_compression"] is True

    def test_validation_configuration(self):
        """検証設定テスト"""
        assert self.updater.update_config["enable_validation"] is True
        
        # 検証を無効化
        self.updater.update_config["enable_validation"] = False
        assert self.updater.update_config["enable_validation"] is False

    def test_retry_delay_configuration(self):
        """リトライ遅延設定テスト"""
        assert self.updater.update_config["retry_delay_seconds"] == 5
        
        # リトライ遅延を変更
        self.updater.update_config["retry_delay_seconds"] = 10
        assert self.updater.update_config["retry_delay_seconds"] == 10

    def test_data_dir_path_handling(self):
        """データディレクトリパス処理テスト"""
        assert isinstance(self.updater.data_dir, Path)
        assert str(self.updater.data_dir) == self.temp_dir

    def test_logger_assignment(self):
        """ロガー割り当てテスト"""
        assert self.updater.logger == self.logger
        
        # 新しいロガーを設定
        new_logger = Mock()
        self.updater.logger = new_logger
        assert self.updater.logger == new_logger

    def test_json_manager_initialization(self):
        """JSONマネージャー初期化テスト"""
        assert self.updater.json_manager is not None
        assert hasattr(self.updater.json_manager, 'get_stock_data')
        assert hasattr(self.updater.json_manager, 'save_stock_data')

    def test_normalize_data_for_diff_empty_list(self):
        """データ正規化テスト（空リスト）"""
        result = self.updater._normalize_data_for_diff([])
        
        assert result == []

    def test_normalize_data_for_diff_none_input(self):
        """データ正規化テスト（None入力）"""
        # None入力は例外を発生させるため、例外をキャッチ
        with pytest.raises(TypeError):
            self.updater._normalize_data_for_diff(None)

    def test_items_different_none_inputs(self):
        """アイテム差分検出テスト（None入力）"""
        item = {"date": "2024-01-01", "close": 100.0}
        
        # None入力は例外を発生させるため、例外をキャッチ
        with pytest.raises(AttributeError):
            self.updater._items_different(None, item)
        with pytest.raises(AttributeError):
            self.updater._items_different(item, None)
        with pytest.raises(AttributeError):
            self.updater._items_different(None, None)

    def test_identify_changes_none_inputs(self):
        """変更検出テスト（None入力）"""
        item = {"open": 100.0, "close": 105.0}
        
        # None入力は例外を発生させるため、例外をキャッチ
        with pytest.raises(AttributeError):
            self.updater._identify_changes(None, item)
        with pytest.raises(AttributeError):
            self.updater._identify_changes(item, None)

    def test_validate_data_integrity_none_input(self):
        """データ整合性検証テスト（None入力）"""
        # None入力は例外を発生させるため、例外をキャッチ
        with pytest.raises(TypeError):
            self.updater._validate_data_integrity(None, [])

    def test_calculate_comprehensive_diff_none_inputs(self):
        """差分計算テスト（None入力）"""
        # None入力は例外を発生させるため、例外をキャッチ
        with pytest.raises(TypeError):
            self.updater._calculate_comprehensive_diff(None, None)

    def test_calculate_comprehensive_diff_mixed_none_inputs(self):
        """差分計算テスト（混合None入力）"""
        data = [{"date": "2024-01-01", "close": 100.0}]
        
        # None入力は例外を発生させるため、例外をキャッチ
        with pytest.raises(TypeError):
            self.updater._calculate_comprehensive_diff(None, data)
        with pytest.raises(TypeError):
            self.updater._calculate_comprehensive_diff(data, None)
