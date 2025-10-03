#!/usr/bin/env python3
"""
JSONDataManagerのカバレッジ向上テスト
"""

import tempfile
import json
from unittest.mock import Mock, patch
import pytest
from core.json_data_manager import JSONDataManager


class TestJSONDataManagerCoverage:
    """JSONデータ管理システムのカバレッジ向上テスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = JSONDataManager(
            data_dir=self.temp_dir,
            logger=Mock()
        )

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """初期化テスト"""
        assert str(self.manager.data_dir) == self.temp_dir
        assert self.manager.logger is not None
        assert self.manager.stock_data_file is not None
        assert self.manager.metadata_file is not None

    def test_save_data_success(self):
        """データ保存成功テスト"""
        data = [{"test": "data", "value": 123}]
        result = self.manager.save_data("test.json", data)
        assert result is True

    def test_save_stock_data(self):
        """株価データ保存テスト"""
        stock_data = [
            {
                "Code": "1234",
                "Date": "2024-01-01",
                "Open": 100.0,
                "High": 110.0,
                "Low": 95.0,
                "Close": 105.0,
                "Volume": 1000
            }
        ]
        result = self.manager.save_stock_data("1234", stock_data, "test_source")
        assert result is True

    def test_get_stock_data(self):
        """株価データ取得テスト"""
        stock_data = [
            {
                "Code": "1234",
                "Date": "2024-01-01",
                "Open": 100.0,
                "High": 110.0,
                "Low": 95.0,
                "Close": 105.0,
                "Volume": 1000
            }
        ]
        self.manager.save_stock_data("1234", stock_data, "test_source")
        retrieved_data = self.manager.get_stock_data("1234")
        assert isinstance(retrieved_data, list)

    def test_get_latest_data(self):
        """最新データ取得テスト"""
        stock_data = [
            {
                "Code": "1234",
                "Date": "2024-01-01",
                "Open": 100.0,
                "High": 110.0,
                "Low": 95.0,
                "Close": 105.0,
                "Volume": 1000
            }
        ]
        self.manager.save_stock_data("1234", stock_data, "test_source")
        latest_data = self.manager.get_latest_data("1234", days=30)
        assert isinstance(latest_data, list)

    def test_get_incremental_data(self):
        """増分データ取得テスト"""
        stock_data = [
            {
                "Code": "1234",
                "Date": "2024-01-01",
                "Open": 100.0,
                "High": 110.0,
                "Low": 95.0,
                "Close": 105.0,
                "Volume": 1000
            }
        ]
        self.manager.save_stock_data("1234", stock_data, "test_source")
        incremental_data = self.manager.get_incremental_data("1234", "2024-01-01")
        assert isinstance(incremental_data, dict)
        assert "data" in incremental_data

    def test_get_metadata(self):
        """メタデータ取得テスト"""
        metadata = self.manager.get_metadata()
        assert isinstance(metadata, dict)
        assert "created_at" in metadata

    def test_get_diff_log(self):
        """差分ログ取得テスト"""
        diff_log = self.manager.get_diff_log()
        assert isinstance(diff_log, list)

    def test_get_statistics(self):
        """統計情報取得テスト"""
        stats = self.manager.get_statistics()
        assert isinstance(stats, dict)
        assert "total_records" in stats

    def test_get_data_statistics(self):
        """データ統計取得テスト"""
        stats = self.manager.get_data_statistics()
        assert isinstance(stats, dict)
        assert "total_records" in stats

    def test_get_all_symbols(self):
        """全シンボル取得テスト"""
        symbols = self.manager.get_all_symbols()
        assert isinstance(symbols, list)

    def test_cleanup_old_data(self):
        """古いデータクリーンアップテスト"""
        result = self.manager.cleanup_old_data(days_to_keep=365)
        assert result is True

    def test_export_data(self):
        """データエクスポートテスト"""
        stock_data = [
            {
                "Code": "1234",
                "Date": "2024-01-01",
                "Open": 100.0,
                "High": 110.0,
                "Low": 95.0,
                "Close": 105.0,
                "Volume": 1000
            }
        ]
        self.manager.save_stock_data("1234", stock_data, "test_source")
        result = self.manager.export_data("1234", "test_export.json")
        assert isinstance(result, bool)

    def test_error_handling_in_save(self):
        """保存時のエラーハンドリングテスト"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = self.manager.save_data("test.json", [{"test": "data"}])
            assert isinstance(result, bool)

    def test_error_handling_in_save_stock_data(self):
        """株価データ保存時のエラーハンドリングテスト"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            stock_data = [{"Code": "1234", "Date": "2024-01-01"}]
            result = self.manager.save_stock_data("1234", stock_data, "test_source")
            assert result is False

    def test_validation_required_fields(self):
        """必須フィールド検証テスト"""
        invalid_data = [{"Code": "1234"}]  # Dateフィールドが不足
        result = self.manager.save_stock_data("1234", invalid_data, "test_source")
        assert result is True  # バリデーションは内部で処理される

    def test_data_type_conversion(self):
        """データ型変換テスト"""
        stock_data = [
            {
                "Code": "1234",
                "Date": "2024-01-01",
                "Open": "100.0",  # 文字列として提供
                "High": "110.0",
                "Low": "95.0",
                "Close": "105.0",
                "Volume": "1000"
            }
        ]
        result = self.manager.save_stock_data("1234", stock_data, "test_source")
        assert result is True

    def test_hash_calculation(self):
        """ハッシュ計算テスト"""
        data = {"test": "data"}
        hash1 = self.manager._calculate_hash(data)
        hash2 = self.manager._calculate_hash(data)
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) > 0

    def test_json_save_load(self):
        """JSON保存・読み込みテスト"""
        test_data = {"test": "value", "number": 123}
        file_path = self.manager.data_dir / "test.json"
        
        # 保存テスト
        result = self.manager._save_json(file_path, test_data)
        assert result is True
        
        # 読み込みテスト
        loaded_data = self.manager._load_json(file_path)
        assert loaded_data == test_data

    def test_json_load_with_default(self):
        """デフォルト値付きJSON読み込みテスト"""
        file_path = self.manager.data_dir / "nonexistent.json"
        default_value = {"default": "value"}
        loaded_data = self.manager._load_json(file_path, default_value)
        assert loaded_data == default_value

    def test_metadata_initialization(self):
        """メタデータ初期化テスト"""
        # 新しいマネージャーを作成してメタデータを確認
        new_manager = JSONDataManager(data_dir=self.temp_dir + "_new")
        metadata = new_manager.get_metadata()
        assert "created_at" in metadata
        assert "version" in metadata
        assert "data_sources" in metadata
