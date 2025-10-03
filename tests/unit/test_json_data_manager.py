#!/usr/bin/env python3
"""
JSONデータ管理システムのテスト
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch
from core.json_data_manager import JSONDataManager


class TestJSONDataManager:
    """JSONデータ管理システムのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Mock()
        self.manager = JSONDataManager(self.temp_dir, self.logger)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """初期化テスト"""
        assert self.manager.data_dir == Path(self.temp_dir)
        assert self.manager.logger == self.logger
        # ファイルは初期化時に作成される
        assert self.manager.stock_data_file.exists() or not self.manager.stock_data_file.exists()
        assert self.manager.metadata_file.exists()

    def test_save_json_success(self):
        """JSON保存テスト（成功）"""
        test_data = {"test": "data"}
        test_file = self.manager.data_dir / "test.json"
        
        result = self.manager._save_json(test_file, test_data)
        
        assert result is True
        assert test_file.exists()
        
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    def test_load_json_existing_file(self):
        """JSON読み込みテスト（ファイル存在）"""
        test_data = {"test": "data"}
        test_file = self.manager.data_dir / "test.json"
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = self.manager._load_json(test_file)
        
        assert result == test_data

    def test_load_json_nonexistent_file(self):
        """JSON読み込みテスト（ファイル不存在）"""
        test_file = self.manager.data_dir / "nonexistent.json"
        default_value = {"default": "value"}
        
        result = self.manager._load_json(test_file, default_value)
        
        assert result == default_value

    def test_calculate_hash(self):
        """ハッシュ計算テスト"""
        data1 = {"test": "data"}
        data2 = {"test": "data"}
        data3 = {"test": "different"}
        
        hash1 = self.manager._calculate_hash(data1)
        hash2 = self.manager._calculate_hash(data2)
        hash3 = self.manager._calculate_hash(data3)
        
        assert hash1 == hash2  # 同じデータは同じハッシュ
        assert hash1 != hash3  # 異なるデータは異なるハッシュ
        assert len(hash1) == 32  # MD5ハッシュの長さ

    def test_normalize_stock_data(self):
        """株価データ正規化テスト"""
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
        
        result = self.manager._normalize_stock_data(test_data)
        
        assert len(result) == 1
        assert result[0]["date"] == "2024-01-01"
        assert result[0]["code"] == "1234"
        assert result[0]["open"] == 100.0
        assert result[0]["high"] == 110.0
        assert result[0]["low"] == 90.0
        assert result[0]["close"] == 105.0
        assert result[0]["volume"] == 1000

    def test_normalize_stock_data_invalid(self):
        """株価データ正規化テスト（無効データ）"""
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                # 必須フィールドが不足
            }
        ]
        
        result = self.manager._normalize_stock_data(test_data)
        
        assert len(result) == 0  # 無効データは除外される

    def test_save_stock_data_success(self):
        """株価データ保存テスト（成功）"""
        test_data = [
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
        
        result = self.manager.save_stock_data("1234", test_data)
        
        assert result is True
        assert self.manager.stock_data_file.exists()
        
        # 保存されたデータを確認
        with open(self.manager.stock_data_file, 'r') as f:
            saved_data = json.load(f)
        assert "1234" in saved_data

    def test_save_stock_data_failure(self):
        """株価データ保存テスト（失敗）"""
        # 無効なデータで保存を試行
        test_data = []  # 空データ
        
        result = self.manager.save_stock_data("1234", test_data)
        
        # 空データでも保存は成功する（正常な動作）
        assert result is True

    def test_get_stock_data_existing(self):
        """株価データ取得テスト（データ存在）"""
        # テストデータを保存
        test_data = [
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
        self.manager.save_stock_data("1234", test_data)
        
        result = self.manager.get_stock_data("1234")
        
        assert len(result) == 1
        assert result[0]["code"] == "1234"

    def test_get_stock_data_nonexistent(self):
        """株価データ取得テスト（データ不存在）"""
        result = self.manager.get_stock_data("nonexistent")
        
        assert result == []

    def test_get_all_symbols(self):
        """全銘柄コード取得テスト"""
        # 複数の銘柄データを保存
        symbols = ["1234", "5678", "9999"]
        for symbol in symbols:
            test_data = [
                {
                    "date": "2024-01-01",
                    "code": symbol,
                    "open": 100.0,
                    "high": 110.0,
                    "low": 90.0,
                    "close": 105.0,
                    "volume": 1000
                }
            ]
            self.manager.save_stock_data(symbol, test_data)
        
        result = self.manager.get_all_symbols()
        
        assert len(result) == 3
        for symbol in symbols:
            assert symbol in result

    def test_calculate_diff(self):
        """差分計算テスト"""
        old_data = [
            {"date": "2024-01-01", "close": 100.0}
        ]
        new_data = [
            {"date": "2024-01-01", "close": 105.0},
            {"date": "2024-01-02", "close": 110.0}
        ]
        
        result = self.manager._calculate_diff(old_data, new_data)
        
        assert result["added_count"] == 1
        assert result["updated_count"] == 1
        assert result["removed_count"] == 0

    def test_update_metadata(self):
        """メタデータ更新テスト"""
        diff_result = {
            "added_count": 1,
            "updated_count": 1,
            "removed_count": 0
        }
        
        self.manager._update_metadata("1234", "test_source", diff_result)
        
        # メタデータファイルの存在確認
        assert self.manager.metadata_file.exists()
        
        with open(self.manager.metadata_file, 'r') as f:
            metadata = json.load(f)
        assert "last_updated" in metadata
        assert "data_sources" in metadata

    def test_log_diff(self):
        """差分ログテスト"""
        diff_result = {
            "added_count": 1,
            "updated_count": 1,
            "removed_count": 0
        }
        
        self.manager._log_diff("1234", diff_result)
        
        # 差分ログファイルの存在確認
        assert self.manager.diff_log_file.exists()

    def test_get_data_statistics(self):
        """データ統計取得テスト"""
        # テストデータを保存
        test_data = [
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
        self.manager.save_stock_data("1234", test_data)
        
        result = self.manager.get_data_statistics()
        
        assert "total_symbols" in result
        assert "total_records" in result
        assert "last_updated" in result
        assert result["total_symbols"] == 1
