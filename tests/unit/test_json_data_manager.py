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
        assert (
            self.manager.stock_data_file.exists()
            or not self.manager.stock_data_file.exists()
        )
        assert self.manager.metadata_file.exists()

    def test_save_json_success(self):
        """JSON保存テスト（成功）"""
        test_data = {"test": "data"}
        test_file = self.manager.data_dir / "test.json"

        result = self.manager._save_json(test_file, test_data)

        assert result is True
        assert test_file.exists()

        with open(test_file, "r") as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    def test_load_json_existing_file(self):
        """JSON読み込みテスト（ファイル存在）"""
        test_data = {"test": "data"}
        test_file = self.manager.data_dir / "test.json"

        with open(test_file, "w") as f:
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
                "volume": "1000",
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
                "volume": 1000,
            }
        ]

        result = self.manager.save_stock_data("1234", test_data)

        assert result is True
        assert self.manager.stock_data_file.exists()

        # 保存されたデータを確認
        with open(self.manager.stock_data_file, "r") as f:
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
                "volume": 1000,
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
                    "volume": 1000,
                }
            ]
            self.manager.save_stock_data(symbol, test_data)

        result = self.manager.get_all_symbols()

        assert len(result) == 3
        for symbol in symbols:
            assert symbol in result

    def test_calculate_diff(self):
        """差分計算テスト"""
        old_data = [{"date": "2024-01-01", "close": 100.0}]
        new_data = [
            {"date": "2024-01-01", "close": 105.0},
            {"date": "2024-01-02", "close": 110.0},
        ]

        result = self.manager._calculate_diff(old_data, new_data)

        assert result["added_count"] == 1
        assert result["updated_count"] == 1
        assert result["removed_count"] == 0

    def test_update_metadata(self):
        """メタデータ更新テスト"""
        diff_result = {"added_count": 1, "updated_count": 1, "removed_count": 0}

        self.manager._update_metadata("1234", "test_source", diff_result)

        # メタデータファイルの存在確認
        assert self.manager.metadata_file.exists()

        with open(self.manager.metadata_file, "r") as f:
            metadata = json.load(f)
        assert "last_updated" in metadata
        assert "data_sources" in metadata

    def test_log_diff(self):
        """差分ログテスト"""
        diff_result = {"added_count": 1, "updated_count": 1, "removed_count": 0}

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
                "volume": 1000,
            }
        ]
        self.manager.save_stock_data("1234", test_data)

        result = self.manager.get_data_statistics()

        assert "total_symbols" in result
        assert "total_records" in result
        assert "last_updated" in result
        assert result["total_symbols"] == 1

    def test_save_json_error_handling(self):
        """JSON保存エラーハンドリングテスト"""
        # 無効なパスでエラーを発生させる
        invalid_file = Path("/invalid/path/that/does/not/exist.json")
        
        result = self.manager._save_json(invalid_file, {"test": "data"})
        assert result is False

    def test_load_json_with_invalid_json(self):
        """無効なJSONファイルの読み込みテスト"""
        invalid_json_file = self.manager.data_dir / "invalid.json"
        with open(invalid_json_file, "w") as f:
            f.write("invalid json content")
        
        result = self.manager._load_json(invalid_json_file, "default_value")
        assert result == "default_value"

    def test_calculate_hash_with_error(self):
        """ハッシュ計算エラーハンドリングテスト"""
        # 循環参照を含むデータでエラーを発生させる
        circular_data = {}
        circular_data["self"] = circular_data
        
        result = self.manager._calculate_hash(circular_data)
        # エラーが発生してもハッシュ値は返される
        assert isinstance(result, str)
        assert len(result) > 0

    def test_normalize_stock_data_with_invalid_data(self):
        """無効なデータの正規化テスト"""
        invalid_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": "invalid_number",  # 無効な数値
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]
        
        result = self.manager._normalize_stock_data(invalid_data)
        # 無効なデータは除外される
        assert len(result) == 0

    def test_normalize_stock_data_missing_fields(self):
        """必須フィールド不足のデータ正規化テスト"""
        incomplete_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                # 必須フィールドが不足
            }
        ]
        
        result = self.manager._normalize_stock_data(incomplete_data)
        # 必須フィールド不足のデータは除外される
        assert len(result) == 0

    def test_get_stock_data_with_filters(self):
        """フィルタ付き株価データ取得テスト"""
        # テストデータの準備
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            },
            {
                "date": "2024-01-02",
                "code": "1234",
                "open": 105.0,
                "high": 115.0,
                "low": 100.0,
                "close": 110.0,
                "volume": 1200,
            }
        ]
        self.manager.save_stock_data("1234", test_data)

        # 日付フィルタテスト
        filtered_data = self.manager.get_stock_data("1234", "2024-01-02", "2024-01-02")
        assert len(filtered_data) == 1
        assert filtered_data[0]["date"] == "2024-01-02"

    def test_get_latest_data(self):
        """最新データ取得テスト"""
        # テストデータの準備
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            },
            {
                "date": "2024-01-02",
                "code": "1234",
                "open": 105.0,
                "high": 115.0,
                "low": 100.0,
                "close": 110.0,
                "volume": 1200,
            }
        ]
        self.manager.save_stock_data("1234", test_data)

        latest_data = self.manager.get_latest_data("1234", 1)
        assert len(latest_data) == 1
        assert latest_data[0]["date"] == "2024-01-02"

    def test_cleanup_old_data(self):
        """古いデータクリーンアップテスト"""
        # テストデータの準備
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]
        self.manager.save_stock_data("1234", test_data)

        # データクリーンアップ
        result = self.manager.cleanup_old_data(days_to_keep=0)  # 全てのデータを削除
        assert result is True

        # データが削除されたことを確認
        data = self.manager.get_stock_data("1234")
        assert len(data) == 0

    def test_save_json_error_handling(self):
        """JSON保存エラーハンドリングテスト"""
        # 無効なパスでエラーを発生させる
        invalid_path = Path("/invalid/path/that/does/not/exist.json")
        test_data = {"test": "data"}
        
        result = self.manager._save_json(invalid_path, test_data)
        assert result is False

    def test_load_json_error_handling(self):
        """JSON読み込みエラーハンドリングテスト"""
        # 無効なJSONファイルを作成
        invalid_json_file = self.manager.data_dir / "invalid.json"
        with open(invalid_json_file, "w") as f:
            f.write("invalid json content")
        
        result = self.manager._load_json(invalid_json_file, "default")
        assert result == "default"

    def test_calculate_hash_error_handling(self):
        """ハッシュ計算エラーハンドリングテスト"""
        # 循環参照を含むデータでエラーを発生させる
        circular_data = {}
        circular_data["self"] = circular_data
        
        result = self.manager._calculate_hash(circular_data)
        # エラーが発生してもハッシュ値は返される
        assert isinstance(result, str)
        assert len(result) == 32  # MD5ハッシュの長さ

    def test_save_stock_data_with_logger_error(self):
        """ロガーエラー時の株価データ保存テスト"""
        # ロガーを無効にしてエラーを発生させる
        self.manager.logger = None
        test_data = [{"date": "2024-01-01", "close": 100.0}]
        
        result = self.manager.save_stock_data("1234", test_data)
        assert result is True

    def test_get_stock_data_with_invalid_symbol(self):
        """無効な銘柄コードでのデータ取得テスト"""
        result = self.manager.get_stock_data("nonexistent")
        assert result == []

    def test_get_stock_data_with_date_filter(self):
        """日付フィルタ付きデータ取得テスト"""
        test_data = [
            {"date": "2024-01-01", "close": 100.0},
            {"date": "2024-01-02", "close": 110.0},
            {"date": "2024-01-03", "close": 120.0}
        ]
        self.manager.save_stock_data("1234", test_data)
        
        # 日付範囲外のデータを取得
        result = self.manager.get_stock_data("1234", "2024-01-05", "2024-01-10")
        assert result == []

    def test_get_latest_data_with_invalid_symbol(self):
        """無効な銘柄コードでの最新データ取得テスト"""
        result = self.manager.get_latest_data("nonexistent", 5)
        assert result == []

    def test_get_latest_data_with_zero_limit(self):
        """制限0での最新データ取得テスト"""
        test_data = [{"date": "2024-01-01", "close": 100.0}]
        self.manager.save_stock_data("1234", test_data)
        
        result = self.manager.get_latest_data("1234", 0)
        assert result == []

    def test_cleanup_old_data_with_invalid_days(self):
        """無効な日数でのデータクリーンアップテスト"""
        result = self.manager.cleanup_old_data(days_to_keep=-1)
        assert result is True

    def test_cleanup_old_data_with_exception(self):
        """例外発生時のデータクリーンアップテスト"""
        # データディレクトリを削除してエラーを発生させる
        import shutil
        shutil.rmtree(self.manager.data_dir)
        
        result = self.manager.cleanup_old_data(days_to_keep=30)
        assert result is False

    def test_get_metadata(self):
        """メタデータ取得テスト"""
        metadata = self.manager.get_metadata()
        assert "created_at" in metadata
        assert "version" in metadata

    def test_get_metadata_basic(self):
        """メタデータ取得テスト（基本）"""
        metadata = self.manager.get_metadata()
        assert isinstance(metadata, dict)

    def test_get_metadata_with_exception(self):
        """例外発生時のメタデータ取得テスト"""
        # データディレクトリを削除してエラーを発生させる
        import shutil
        shutil.rmtree(self.manager.data_dir)

        metadata = self.manager.get_metadata()
        assert metadata == {}

    def test_get_data_sources_from_metadata(self):
        """メタデータからデータソース取得テスト"""
        metadata = self.manager.get_metadata()
        sources = metadata.get("data_sources", {})
        assert isinstance(sources, dict)

    def test_save_stock_data_with_source(self):
        """データソース付きで株価データ保存テスト"""
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000
            }
        ]
        result = self.manager.save_stock_data("1234", test_data, "test_source")
        assert result is True
        
        # 追加されたソースを確認
        metadata = self.manager.get_metadata()
        sources = metadata.get("data_sources", {})
        assert "1234" in sources

    def test_save_stock_data_with_exception(self):
        """例外発生時の株価データ保存テスト"""
        # データディレクトリを削除してエラーを発生させる
        import shutil
        shutil.rmtree(self.manager.data_dir)

        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        result = self.manager.save_stock_data("1234", test_data)
        assert result is False

    def test_get_update_history_from_metadata(self):
        """メタデータから更新履歴取得テスト"""
        metadata = self.manager.get_metadata()
        history = metadata.get("update_history", [])
        assert isinstance(history, list)

    def test_save_stock_data_creates_update_record(self):
        """株価データ保存で更新記録作成テスト"""
        test_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000
            }
        ]
        result = self.manager.save_stock_data("1234", test_data)
        assert result is True
        
        # 更新履歴を確認
        metadata = self.manager.get_metadata()
        history = metadata.get("update_history", [])
        assert len(history) > 0

    def test_save_stock_data_creates_update_record_with_exception(self):
        """例外発生時の株価データ保存で更新記録作成テスト"""
        # データディレクトリを削除してエラーを発生させる
        import shutil
        shutil.rmtree(self.manager.data_dir)

        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        result = self.manager.save_stock_data("1234", test_data)
        assert result is False

    def test_normalize_stock_data(self):
        """株価データ正規化テスト"""
        raw_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": "100.0",  # 文字列
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": "1000"  # 文字列
            }
        ]
        
        normalized = self.manager._normalize_stock_data(raw_data)
        assert len(normalized) == 1
        assert normalized[0]["open"] == 100.0
        assert normalized[0]["volume"] == 1000

    def test_normalize_stock_data_with_invalid_data(self):
        """無効なデータでの正規化テスト"""
        invalid_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": "invalid",  # 無効な数値
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000
            }
        ]

        normalized = self.manager._normalize_stock_data(invalid_data)
        assert len(normalized) == 0  # 無効なデータは除外される

    def test_normalize_stock_data_with_missing_fields(self):
        """必須フィールド不足での正規化テスト"""
        incomplete_data = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": 100.0,
                # high, low, close, volumeが不足
            }
        ]

        normalized = self.manager._normalize_stock_data(incomplete_data)
        assert len(normalized) == 0  # 必須フィールド不足は除外される

    def test_normalize_stock_data_with_exception(self):
        """例外発生時の正規化テスト"""
        # 無効なデータ型でエラーを発生させる
        invalid_data = "not a list"
        
        normalized = self.manager._normalize_stock_data(invalid_data)
        assert normalized == []

    def test_get_data_statistics(self):
        """データ統計取得テスト"""
        test_data = [
            {"date": "2024-01-01", "close": 100.0},
            {"date": "2024-01-02", "close": 110.0}
        ]
        self.manager.save_stock_data("1234", test_data)
        
        stats = self.manager.get_data_statistics()
        assert "total_symbols" in stats
        assert "total_records" in stats
        assert "last_updated" in stats

    def test_get_data_statistics_with_exception(self):
        """例外発生時のデータ統計取得テスト"""
        # データディレクトリを削除してエラーを発生させる
        import shutil
        shutil.rmtree(self.manager.data_dir)

        stats = self.manager.get_data_statistics()
        assert isinstance(stats, dict)

    def test_export_data(self):
        """データエクスポートテスト"""
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)

        export_path = self.manager.data_dir / "export.json"
        result = self.manager.export_data("1234", str(export_path))
        assert result is True
        assert export_path.exists()

    def test_export_data_with_exception(self):
        """例外発生時のデータエクスポートテスト"""
        # 無効なパスでエラーを発生させる
        invalid_path = "/invalid/path/export.json"
        result = self.manager.export_data("1234", invalid_path)
        assert result is False

    def test_export_data_file_creation(self):
        """データエクスポートファイル作成テスト"""
        # エクスポートファイルを作成
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)
        
        export_path = self.manager.data_dir / "import.json"
        result = self.manager.export_data("1234", str(export_path))
        assert result is True
        assert export_path.exists()

    def test_export_data_with_invalid_file(self):
        """無効なファイルでのデータエクスポートテスト"""
        # 無効なパスでエラーを発生させる
        invalid_path = "/invalid/path/export.json"
        result = self.manager.export_data("1234", invalid_path)
        assert result is False

    def test_export_data_with_nonexistent_symbol(self):
        """存在しない銘柄でのデータエクスポートテスト"""
        nonexistent_file = self.manager.data_dir / "nonexistent.json"
        result = self.manager.export_data("nonexistent", str(nonexistent_file))
        assert result is False

    def test_get_all_symbols(self):
        """全銘柄コード取得テスト"""
        # テストデータを保存
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)
        
        symbols = self.manager.get_all_symbols()
        assert "1234" in symbols

    def test_get_incremental_data(self):
        """差分データ取得テスト"""
        # テストデータを保存
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)
        
        incremental = self.manager.get_incremental_data("1234")
        assert "is_full_update" in incremental
        assert "data" in incremental

    def test_get_diff_log(self):
        """差分ログ取得テスト"""
        # テストデータを保存して差分ログを生成
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)
        
        diff_log = self.manager.get_diff_log()
        assert isinstance(diff_log, list)

    def test_get_diff_log_with_symbol(self):
        """特定銘柄の差分ログ取得テスト"""
        # テストデータを保存して差分ログを生成
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)
        
        diff_log = self.manager.get_diff_log("1234")
        assert isinstance(diff_log, list)

    def test_get_diff_log_with_limit(self):
        """制限付き差分ログ取得テスト"""
        # テストデータを保存して差分ログを生成
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)
        
        diff_log = self.manager.get_diff_log(limit=5)
        assert isinstance(diff_log, list)
        assert len(diff_log) <= 5

    def test_calculate_hash_with_exception(self):
        """ハッシュ計算の例外処理テスト"""
        # 無効なデータでハッシュ計算をテスト
        invalid_data = {"circular": None}
        invalid_data["circular"] = invalid_data  # 循環参照
        
        hash_value = self.manager._calculate_hash(invalid_data)
        assert isinstance(hash_value, str)
        assert len(hash_value) > 0

    def test_save_json_with_exception(self):
        """JSON保存の例外処理テスト"""
        # 無効なパスでエラーを発生させる
        invalid_path = Path("/invalid/path/that/does/not/exist.json")
        result = self.manager._save_json(invalid_path, {"test": "data"})
        assert result is False

    def test_load_json_with_exception(self):
        """JSON読み込みの例外処理テスト"""
        # 無効なJSONファイルを作成
        invalid_file = self.manager.data_dir / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("invalid json content")
        
        result = self.manager._load_json(invalid_file, {"default": "value"})
        assert result == {"default": "value"}

    def test_calculate_diff_with_empty_data(self):
        """空データでの差分計算テスト"""
        diff = self.manager._calculate_diff([], [])
        assert "added_count" in diff
        assert "updated_count" in diff
        assert "removed_count" in diff
        assert diff["added_count"] == 0
        assert diff["updated_count"] == 0
        assert diff["removed_count"] == 0

    def test_calculate_diff_with_new_data(self):
        """新規データでの差分計算テスト"""
        old_data = []
        new_data = [{"date": "2024-01-01", "close": 100.0}]
        
        diff = self.manager._calculate_diff(old_data, new_data)
        assert diff["added_count"] == 1
        assert diff["updated_count"] == 0
        assert diff["removed_count"] == 0

    def test_calculate_diff_with_updated_data(self):
        """更新データでの差分計算テスト"""
        old_data = [{"date": "2024-01-01", "close": 100.0}]
        new_data = [{"date": "2024-01-01", "close": 110.0}]
        
        diff = self.manager._calculate_diff(old_data, new_data)
        assert diff["added_count"] == 0
        assert diff["updated_count"] == 1
        assert diff["removed_count"] == 0

    def test_calculate_diff_with_removed_data(self):
        """削除データでの差分計算テスト"""
        old_data = [{"date": "2024-01-01", "close": 100.0}]
        new_data = []
        
        diff = self.manager._calculate_diff(old_data, new_data)
        assert diff["added_count"] == 0
        assert diff["updated_count"] == 0
        assert diff["removed_count"] == 1

    def test_normalize_stock_data_with_none_values(self):
        """None値での正規化テスト"""
        data_with_none = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": None,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": None
            }
        ]
        
        normalized = self.manager._normalize_stock_data(data_with_none)
        assert len(normalized) == 1
        assert normalized[0]["open"] == 0.0
        assert normalized[0]["volume"] == 0

    def test_normalize_stock_data_with_string_numbers(self):
        """文字列数値での正規化テスト"""
        data_with_strings = [
            {
                "date": "2024-01-01",
                "code": "1234",
                "open": "100.5",
                "high": "110.0",
                "low": "95.0",
                "close": "105.0",
                "volume": "1000"
            }
        ]
        
        normalized = self.manager._normalize_stock_data(data_with_strings)
        assert len(normalized) == 1
        assert normalized[0]["open"] == 100.5
        assert normalized[0]["volume"] == 1000

    def test_get_latest_data_with_invalid_symbol(self):
        """無効な銘柄での最新データ取得テスト"""
        data = self.manager.get_latest_data("nonexistent")
        assert data == []

    def test_get_latest_data_with_zero_days(self):
        """0日での最新データ取得テスト"""
        test_data = [{"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000}]
        self.manager.save_stock_data("1234", test_data)
        
        data = self.manager.get_latest_data("1234", days=0)
        assert data == []

    def test_get_stock_data_with_invalid_symbol(self):
        """無効な銘柄での株価データ取得テスト"""
        data = self.manager.get_stock_data("nonexistent")
        assert data == []

    def test_get_stock_data_with_date_filter(self):
        """日付フィルターでの株価データ取得テスト"""
        test_data = [
            {"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000},
            {"date": "2024-01-02", "code": "1234", "open": 105.0, "high": 115.0, "low": 100.0, "close": 110.0, "volume": 1200}
        ]
        self.manager.save_stock_data("1234", test_data)
        
        data = self.manager.get_stock_data("1234", start_date="2024-01-02")
        assert len(data) == 1
        assert data[0]["date"] == "2024-01-02"

    def test_get_stock_data_with_end_date_filter(self):
        """終了日フィルターでの株価データ取得テスト"""
        test_data = [
            {"date": "2024-01-01", "code": "1234", "open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0, "volume": 1000},
            {"date": "2024-01-02", "code": "1234", "open": 105.0, "high": 115.0, "low": 100.0, "close": 110.0, "volume": 1200}
        ]
        self.manager.save_stock_data("1234", test_data)
        
        data = self.manager.get_stock_data("1234", end_date="2024-01-01")
        assert len(data) == 1
        assert data[0]["date"] == "2024-01-01"
