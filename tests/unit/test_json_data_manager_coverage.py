#!/usr/bin/env python3
"""
JSONDataManagerのテストカバレッジ向上
不足しているテストケースを追加
"""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open
from core.json_data_manager import JSONDataManager


class TestJSONDataManagerCoverage:
    """JSONDataManagerのカバレッジ向上テスト"""

    def test_save_data_success(self):
        """データ保存成功テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            test_data = [
                {"date": "2024-01-01", "code": "1234", "close": 100},
                {"date": "2024-01-02", "code": "1234", "close": 101}
            ]
            
            result = manager.save_data("test.json", test_data)
            
            # 保存成功を確認
            assert result is True
            assert os.path.exists(os.path.join(temp_dir, "test.json"))

    def test_save_data_failure(self):
        """データ保存失敗テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            test_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
            
            # 無効なパスでの保存
            with patch.object(manager, '_save_json', side_effect=Exception("Save failed")):
                result = manager.save_data("test.json", test_data)
                
                # 保存失敗を確認
                assert result is False

    def test_get_stock_data_with_filters(self):
        """フィルタ付きデータ取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            # テストデータの作成
            test_data = [
                {"date": "2024-01-01", "code": "1234", "close": 100},
                {"date": "2024-01-02", "code": "1234", "close": 101},
                {"date": "2024-01-03", "code": "1234", "close": 102}
            ]
            
            # データの保存
            manager.save_data("1234.json", test_data)
            
            # フィルタ付きデータ取得
            filtered_data = manager.get_stock_data(
                "1234", 
                start_date="2024-01-01", 
                end_date="2024-01-02"
            )
            
            # フィルタが正しく適用されたことを確認
            assert len(filtered_data) == 2
            assert filtered_data[0]["date"] == "2024-01-01"
            assert filtered_data[1]["date"] == "2024-01-02"

    def test_get_stock_data_nonexistent_symbol(self):
        """存在しない銘柄のデータ取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            # 存在しない銘柄のデータ取得
            result = manager.get_stock_data("nonexistent")
            
            # 空のリストが返されることを確認
            assert result == []

    def test_calculate_diff_with_empty_data(self):
        """空データでの差分計算テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            # 空データでの差分計算
            result = manager._calculate_diff([], [])
            
            # 空データの結果を確認
            assert result["added_count"] == 0
            assert result["updated_count"] == 0
            assert result["removed_count"] == 0

    def test_calculate_diff_with_identical_data(self):
        """同一データでの差分計算テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            test_data = [{"date": "2024-01-01", "code": "1234", "close": 100}]
            
            # 同一データでの差分計算
            result = manager._calculate_diff(test_data, test_data)
            
            # 差分がないことを確認
            assert result["added_count"] == 0
            assert result["updated_count"] == 0
            assert result["removed_count"] == 0

    def test_update_metadata_with_new_symbol(self):
        """新しい銘柄でのメタデータ更新テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            diff_result = {
                "added_count": 1,
                "updated_count": 0,
                "removed_count": 0,
                "total_new": 1
            }
            
            # 新しい銘柄のメタデータ更新
            manager._update_metadata("1234", "test_source", diff_result)
            
            # メタデータファイルの存在確認
            assert os.path.exists(os.path.join(temp_dir, "metadata.json"))

    def test_log_diff_with_large_history(self):
        """大量履歴での差分ログテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            # 大量の差分ログを追加
            for i in range(1100):  # 1000件の制限を超える
                diff_result = {
                    "added_count": 1,
                    "updated_count": 0,
                    "removed_count": 0
                }
                manager._log_diff(f"symbol_{i}", diff_result)
            
            # ログファイルの読み込み
            diff_log = manager._load_json(manager.diff_log_file, [])
            
            # 履歴が1000件に制限されていることを確認
            assert len(diff_log) == 1000

    def test_calculate_hash_with_different_data(self):
        """異なるデータでのハッシュ計算テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            data1 = {"date": "2024-01-01", "code": "1234", "close": 100}
            data2 = {"date": "2024-01-01", "code": "1234", "close": 101}
            
            hash1 = manager._calculate_hash(data1)
            hash2 = manager._calculate_hash(data2)
            
            # 異なるデータで異なるハッシュが生成されることを確認
            assert hash1 != hash2

    def test_load_json_with_nonexistent_file(self):
        """存在しないファイルでのJSON読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            # 存在しないファイルの読み込み
            result = manager._load_json("nonexistent.json", {"default": "value"})
            
            # デフォルト値が返されることを確認
            assert result == {"default": "value"}

    def test_save_json_with_invalid_data(self):
        """無効なデータでのJSON保存テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = JSONDataManager(data_dir=temp_dir)
            
            # 無効なデータの保存
            with patch('json.dump', side_effect=Exception("JSON serialization failed")):
                with pytest.raises(Exception):
                    manager._save_json("test.json", {"invalid": object()})
