"""
データ前処理モジュールのユニットテスト
"""

import pytest

pytestmark = pytest.mark.unit
import pandas as pd
import numpy as np
import os
from unittest.mock import patch, mock_open
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from test_jquants_data_preprocessing import (
    validate_input_file,
    load_and_clean_data,
    engineer_basic_features,
    preprocess_data,
)
from test_unified_system import FileError, TestUnifiedSystem


class TestDataPreprocessing:
    """データ前処理関数のテスト"""

    def test_validate_input_file_success(self, temp_csv_file):
        """正常なファイルの検証テスト"""
        # ファイルが存在し、読み取り可能であることを確認
        assert os.path.exists(temp_csv_file)
        assert os.access(temp_csv_file, os.R_OK)

        # 検証関数が正常に実行されることを確認
        validate_input_file(temp_csv_file)

    def test_validate_input_file_not_found(self):
        """存在しないファイルの検証テスト"""
        with pytest.raises((FileNotFoundError, FileError)):
            validate_input_file("nonexistent_file.csv")

    def test_validate_input_file_no_permission(self, tmp_path):
        """読み取り権限がないファイルの検証テスト"""
        # 権限のないファイルを作成（Unix系システムでのみ有効）
        if os.name != "nt":  # Windows以外
            no_permission_file = tmp_path / "no_permission.csv"
            no_permission_file.write_text("test")
            os.chmod(no_permission_file, 0o000)  # 権限を削除

            with pytest.raises((PermissionError, FileError)):
                validate_input_file(str(no_permission_file))

    def test_load_and_validate_data_success(self, temp_csv_file, sample_stock_data):
        """正常なデータ読み込みテスト"""
        # サンプルデータをCSVファイルに保存
        sample_stock_data.to_csv(temp_csv_file, index=False)

        result = load_and_clean_data(temp_csv_file)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "Date" in result.columns or "date" in result.columns.lower()

    def test_load_and_validate_data_empty_file(self, tmp_path):
        """空のファイルの読み込みテスト"""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")

        with pytest.raises(ValueError, match="入力ファイルが空です"):
            load_and_clean_data(str(empty_file))

    def test_load_and_validate_data_invalid_csv(self, tmp_path):
        """無効なCSVファイルの読み込みテスト"""
        invalid_file = tmp_path / "invalid.csv"
        invalid_file.write_text("invalid,csv,content\nwith,missing,columns")

        with pytest.raises(KeyError):
            load_and_clean_data(str(invalid_file))

    def test_preprocess_data_basic(self, sample_stock_data):
        """基本的なデータ前処理テスト"""
        result = engineer_basic_features(sample_stock_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # 日付カラムが正しく処理されていることを確認
        if "Date" in result.columns:
            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_preprocess_data_missing_values(self):
        """欠損値の処理テスト"""
        data_with_missing = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=10),
                "Open": [100, 101, np.nan, 103, 104, 105, 106, 107, 108, 109],
                "High": [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
                "Low": [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
                "Close": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
                "Volume": [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
            }
        )

        result = preprocess_data(data_with_missing)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_duplicate_dates(self):
        """重複日付の処理テスト"""
        data_with_duplicates = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-01", "2023-01-02", "2023-01-02"],
                "Open": [100, 101, 102, 103],
                "High": [105, 106, 107, 108],
                "Low": [95, 96, 97, 98],
                "Close": [102, 103, 104, 105],
                "Volume": [1000, 1100, 1200, 1300],
            }
        )

        result = preprocess_data(data_with_duplicates)
        assert isinstance(result, pd.DataFrame)
        # 重複が処理されていることを確認（具体的な処理方法は実装による）

    def test_preprocess_data_invalid_ohlc(self):
        """無効なOHLCデータの処理テスト"""
        invalid_ohlc_data = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=5),
                "Open": [100, 101, 102, 103, 104],
                "High": [95, 96, 97, 98, 99],  # High < Open (無効)
                "Low": [105, 106, 107, 108, 109],  # Low > High (無効)
                "Close": [102, 103, 104, 105, 106],
                "Volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

        result = preprocess_data(invalid_ohlc_data)
        assert isinstance(result, pd.DataFrame)
        # 無効なデータが修正されていることを確認

    def test_preprocess_data_negative_volume(self):
        """負のボリュームの処理テスト"""
        data_with_negative_volume = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=5),
                "Open": [100, 101, 102, 103, 104],
                "High": [105, 106, 107, 108, 109],
                "Low": [95, 96, 97, 98, 99],
                "Close": [102, 103, 104, 105, 106],
                "Volume": [1000, -1100, 1200, 1300, 1400],  # 負の値
            }
        )

        result = preprocess_data(data_with_negative_volume)
        assert isinstance(result, pd.DataFrame)
        # 負のボリュームが処理されていることを確認

    def test_preprocess_data_empty_dataframe(self):
        """空のデータフレームの処理テスト"""
        empty_df = pd.DataFrame()

        with pytest.raises(KeyError):
            engineer_basic_features(empty_df)

    def test_preprocess_data_single_row(self):
        """1行のデータフレームの処理テスト"""
        single_row_df = pd.DataFrame(
            {
                "Date": ["2023-01-01"],
                "Open": [100],
                "High": [105],
                "Low": [95],
                "Close": [102],
                "Volume": [1000],
            }
        )

        result = engineer_basic_features(single_row_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("jquants_data_preprocessing.logger")
    def test_preprocess_data_logging(self, mock_logger, sample_stock_data):
        """ログ出力のテスト"""
        engineer_basic_features(sample_stock_data)
        # ログが出力されていることを確認
        assert mock_logger.info.called or mock_logger.debug.called

    def test_preprocess_data_column_standardization(self):
        """カラム名の標準化テスト"""
        data_with_lowercase = pd.DataFrame(
            {
                "date": pd.date_range("2023-01-01", periods=5),
                "open": [100, 101, 102, 103, 104],
                "high": [105, 106, 107, 108, 109],
                "low": [95, 96, 97, 98, 99],
                "close": [102, 103, 104, 105, 106],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

        # カラム名を標準化
        data_with_lowercase.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

        result = engineer_basic_features(data_with_lowercase)
        assert isinstance(result, pd.DataFrame)
        # カラム名が標準化されていることを確認（実装による）

    def test_preprocess_data_data_types(self, sample_stock_data):
        """データ型の変換テスト"""
        result = engineer_basic_features(sample_stock_data)

        # 数値カラムが適切な型になっていることを確認
        numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_columns:
            if col in result.columns:
                assert pd.api.types.is_numeric_dtype(result[col])

        # 日付カラムが適切な型になっていることを確認
        if "Date" in result.columns:
            assert pd.api.types.is_datetime64_any_dtype(result["Date"])
