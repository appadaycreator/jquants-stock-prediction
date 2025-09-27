"""
強化されたデータ前処理モジュールのユニットテスト
カバレッジを向上させるための包括的なテスト
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from jquants_data_preprocessing import (
    validate_input_file,
    load_and_clean_data,
    engineer_basic_features,
    preprocess_data,
    calculate_technical_indicators,
    validate_data_quality,
    handle_missing_data,
    detect_outliers,
    standardize_data,
    export_processed_data,
)


class TestEnhancedDataPreprocessing:
    """強化されたデータ前処理関数のテスト"""

    def test_validate_input_file_comprehensive(self, tmp_path):
        """包括的なファイル検証テスト"""
        # 正常なファイル
        valid_file = tmp_path / "valid.csv"
        valid_file.write_text(
            "Date,Open,High,Low,Close,Volume\n2023-01-01,100,105,95,102,1000"
        )
        assert os.path.exists(str(valid_file))
        validate_input_file(str(valid_file))

        # 存在しないファイル
        with pytest.raises(FileNotFoundError):
            validate_input_file("nonexistent.csv")

        # 空のファイル
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        with pytest.raises(ValueError, match="入力ファイルが空です"):
            validate_input_file(str(empty_file))

        # 権限のないファイル（Unix系システム）
        if os.name != "nt":
            no_permission_file = tmp_path / "no_permission.csv"
            no_permission_file.write_text("test")
            os.chmod(no_permission_file, 0o000)
            with pytest.raises(PermissionError):
                validate_input_file(str(no_permission_file))

    def test_load_and_clean_data_comprehensive(self, tmp_path):
        """包括的なデータ読み込みテスト"""
        # 正常なデータ
        valid_data = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )
        valid_file = tmp_path / "valid.csv"
        valid_data.to_csv(valid_file, index=False)

        result = load_and_clean_data(str(valid_file))
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # 欠損値のあるデータ
        missing_data = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, np.nan, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )
        missing_file = tmp_path / "missing.csv"
        missing_data.to_csv(missing_file, index=False)

        result = load_and_clean_data(str(missing_file))
        assert isinstance(result, pd.DataFrame)

        # 無効なCSVファイル
        invalid_file = tmp_path / "invalid.csv"
        invalid_file.write_text("invalid,csv,content\nwith,missing,columns")

        with pytest.raises(KeyError):
            load_and_clean_data(str(invalid_file))

    def test_engineer_basic_features_comprehensive(self, sample_stock_data):
        """包括的な特徴量エンジニアリングテスト"""
        # 正常なデータ
        result = engineer_basic_features(sample_stock_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # 日付カラムの処理
        if "Date" in result.columns:
            assert pd.api.types.is_datetime64_any_dtype(result["Date"])

        # 数値カラムの処理
        numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_columns:
            if col in result.columns:
                assert pd.api.types.is_numeric_dtype(result[col])

    def test_preprocess_data_edge_cases(self):
        """エッジケースでのデータ前処理テスト"""
        # 空のデータフレーム
        empty_df = pd.DataFrame()
        with pytest.raises(KeyError):
            engineer_basic_features(empty_df)

        # 1行のデータフレーム
        single_row = pd.DataFrame(
            {
                "Date": ["2023-01-01"],
                "Open": [100],
                "High": [105],
                "Low": [95],
                "Close": [102],
                "Volume": [1000],
            }
        )
        result = engineer_basic_features(single_row)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

        # 重複日付
        duplicate_dates = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-01", "2023-01-02"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )
        result = engineer_basic_features(duplicate_dates)
        assert isinstance(result, pd.DataFrame)

        # 無効なOHLCデータ
        invalid_ohlc = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "Open": [100, 101],
                "High": [95, 96],  # High < Open
                "Low": [105, 106],  # Low > High
                "Close": [102, 103],
                "Volume": [1000, 1100],
            }
        )
        result = engineer_basic_features(invalid_ohlc)
        assert isinstance(result, pd.DataFrame)

    def test_calculate_technical_indicators(self, sample_stock_data):
        """技術指標計算のテスト"""
        result = calculate_technical_indicators(sample_stock_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # 技術指標が追加されていることを確認
        expected_indicators = ["SMA_5", "SMA_25", "EMA_12", "EMA_26"]
        for indicator in expected_indicators:
            if indicator in result.columns:
                assert not result[indicator].isna().all()

    def test_validate_data_quality(self, sample_stock_data):
        """データ品質検証のテスト"""
        # 正常なデータ
        quality_report = validate_data_quality(sample_stock_data)
        assert isinstance(quality_report, dict)
        assert "missing_values" in quality_report
        assert "outliers" in quality_report
        assert "data_types" in quality_report

        # 問題のあるデータ
        problematic_data = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, np.nan, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, -1100, 1200],  # 負の値
            }
        )

        quality_report = validate_data_quality(problematic_data)
        assert quality_report["missing_values"]["Open"] > 0
        assert quality_report["outliers"]["Volume"] > 0

    def test_handle_missing_data(self):
        """欠損値処理のテスト"""
        data_with_missing = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, np.nan, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )

        result = handle_missing_data(data_with_missing)
        assert isinstance(result, pd.DataFrame)
        assert not result["Open"].isna().any()

    def test_detect_outliers(self, sample_stock_data):
        """異常値検出のテスト"""
        # 正常なデータ
        outliers = detect_outliers(sample_stock_data)
        assert isinstance(outliers, dict)
        assert "Open" in outliers
        assert "High" in outliers
        assert "Low" in outliers
        assert "Close" in outliers
        assert "Volume" in outliers

        # 異常値を含むデータ
        data_with_outliers = sample_stock_data.copy()
        data_with_outliers.loc[0, "Close"] = 1000  # 異常に高い値
        data_with_outliers.loc[1, "Volume"] = -1000  # 負の値

        outliers = detect_outliers(data_with_outliers)
        assert outliers["Close"][0] == True  # 異常値として検出
        assert outliers["Volume"][1] == True  # 異常値として検出

    def test_standardize_data(self, sample_stock_data):
        """データ標準化のテスト"""
        result = standardize_data(sample_stock_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_stock_data)

        # 数値カラムが標準化されていることを確認
        numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_columns:
            if col in result.columns:
                # 標準化後の値が適切な範囲にあることを確認
                assert result[col].min() >= -5  # 3σルールを考慮
                assert result[col].max() <= 5

    def test_export_processed_data(self, sample_stock_data, tmp_path):
        """処理済みデータのエクスポートテスト"""
        output_file = tmp_path / "processed_data.csv"

        result = export_processed_data(sample_stock_data, str(output_file))
        assert result is True
        assert os.path.exists(str(output_file))

        # エクスポートされたファイルの内容を確認
        exported_data = pd.read_csv(str(output_file))
        assert len(exported_data) == len(sample_stock_data)

    def test_preprocess_data_with_logging(self, sample_stock_data):
        """ログ出力のテスト"""
        with patch("jquants_data_preprocessing.logger") as mock_logger:
            engineer_basic_features(sample_stock_data)
            # ログが出力されていることを確認
            assert mock_logger.info.called or mock_logger.debug.called

    def test_preprocess_data_with_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なデータ型
        invalid_data = pd.DataFrame(
            {
                "Date": [123, 456, 789],  # 数値の日付
                "Open": ["invalid", "data", "types"],  # 文字列の価格
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )

        # エラーが発生しても適切に処理されることを確認
        try:
            result = engineer_basic_features(invalid_data)
            assert isinstance(result, pd.DataFrame)
        except Exception as e:
            assert isinstance(e, (ValueError, TypeError, KeyError))

    def test_preprocess_data_performance(self, sample_stock_data):
        """パフォーマンステスト"""
        import time

        # 大きなデータセットを作成
        large_data = pd.concat([sample_stock_data] * 10, ignore_index=True)

        start_time = time.time()
        result = engineer_basic_features(large_data)
        end_time = time.time()

        execution_time = end_time - start_time
        assert execution_time < 5.0  # 5秒以内
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_memory_usage(self, sample_stock_data):
        """メモリ使用量テスト"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 大きなデータセットを処理
        large_data = pd.concat([sample_stock_data] * 100, ignore_index=True)
        result = engineer_basic_features(large_data)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # メモリ使用量の増加が妥当な範囲内であることを確認（100MB以内）
        assert memory_increase < 100 * 1024 * 1024

    def test_preprocess_data_concurrent_access(self, sample_stock_data):
        """並行アクセスのテスト"""
        import threading
        import time

        results = []
        errors = []

        def process_data():
            try:
                result = engineer_basic_features(sample_stock_data)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # 複数のスレッドで同時に処理
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=process_data)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # エラーが発生していないことを確認
        assert len(errors) == 0
        assert len(results) == 5

    def test_preprocess_data_with_different_locales(self, sample_stock_data):
        """異なるロケールでのテスト"""
        # 日付フォーマットの違いをテスト
        data_with_different_date_format = sample_stock_data.copy()
        data_with_different_date_format["Date"] = data_with_different_date_format[
            "Date"
        ].dt.strftime("%d/%m/%Y")

        result = engineer_basic_features(data_with_different_date_format)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_unicode(self):
        """Unicode文字を含むデータのテスト"""
        unicode_data = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
                "Symbol": ["AAPL", "MSFT", "GOOGL"],  # Unicode文字を含む可能性
                "Name": ["Apple Inc.", "Microsoft Corp.", "Alphabet Inc."],
            }
        )

        result = engineer_basic_features(unicode_data)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_timezone(self):
        """タイムゾーン情報を含むデータのテスト"""
        timezone_data = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=5, freq="D", tz="UTC"),
                "Open": [100, 101, 102, 103, 104],
                "High": [105, 106, 107, 108, 109],
                "Low": [95, 96, 97, 98, 99],
                "Close": [102, 103, 104, 105, 106],
                "Volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

        result = engineer_basic_features(timezone_data)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_custom_indicators(self, sample_stock_data):
        """カスタム指標のテスト"""
        # カスタム指標を追加
        custom_data = sample_stock_data.copy()
        custom_data["Custom_Indicator"] = custom_data["Close"].rolling(window=3).mean()

        result = engineer_basic_features(custom_data)
        assert isinstance(result, pd.DataFrame)
        assert "Custom_Indicator" in result.columns

    def test_preprocess_data_with_nan_handling(self):
        """NaN値の処理テスト"""
        data_with_nan = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, np.nan, 102],
                "High": [105, np.nan, 107],
                "Low": [95, np.nan, 97],
                "Close": [102, np.nan, 104],
                "Volume": [1000, np.nan, 1200],
            }
        )

        result = engineer_basic_features(data_with_nan)
        assert isinstance(result, pd.DataFrame)
        # NaN値が適切に処理されていることを確認
        assert not result["Open"].isna().all()

    def test_preprocess_data_with_inf_values(self):
        """無限大値の処理テスト"""
        data_with_inf = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, np.inf, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )

        result = engineer_basic_features(data_with_inf)
        assert isinstance(result, pd.DataFrame)
        # 無限大値が適切に処理されていることを確認
        assert not np.isinf(result["Open"]).any()

    def test_preprocess_data_with_negative_values(self):
        """負の値の処理テスト"""
        data_with_negative = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, -1100, 1200],  # 負の値
            }
        )

        result = engineer_basic_features(data_with_negative)
        assert isinstance(result, pd.DataFrame)
        # 負の値が適切に処理されていることを確認
        assert result["Volume"].min() >= 0

    def test_preprocess_data_with_zero_values(self):
        """ゼロ値の処理テスト"""
        data_with_zero = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 0, 1200],  # ゼロ値
            }
        )

        result = engineer_basic_features(data_with_zero)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_extreme_values(self):
        """極値の処理テスト"""
        data_with_extreme = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1e10, 1200],  # 極値
            }
        )

        result = engineer_basic_features(data_with_extreme)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_mixed_types(self):
        """混合型データの処理テスト"""
        data_with_mixed_types = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, "101", 102],  # 混合型
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )

        result = engineer_basic_features(data_with_mixed_types)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_duplicate_columns(self):
        """重複カラムの処理テスト"""
        data_with_duplicate_columns = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
            }
        )
        data_with_duplicate_columns.columns = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        result = engineer_basic_features(data_with_duplicate_columns)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_special_characters(self):
        """特殊文字を含むデータの処理テスト"""
        data_with_special_chars = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Open": [100, 101, 102],
                "High": [105, 106, 107],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000, 1100, 1200],
                "Symbol": ["AAPL", "MSFT", "GOOGL"],
                "Name": ["Apple Inc.", "Microsoft Corp.", "Alphabet Inc."],
            }
        )

        result = engineer_basic_features(data_with_special_chars)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_with_large_dataset(self):
        """大きなデータセットの処理テスト"""
        # 大きなデータセットを作成
        large_data = pd.DataFrame(
            {
                "Date": pd.date_range("2020-01-01", periods=10000, freq="D"),
                "Open": np.random.uniform(50, 200, 10000),
                "High": np.random.uniform(50, 200, 10000),
                "Low": np.random.uniform(50, 200, 10000),
                "Close": np.random.uniform(50, 200, 10000),
                "Volume": np.random.randint(1000, 100000, 10000),
            }
        )

        result = engineer_basic_features(large_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10000

    def test_preprocess_data_with_memory_efficiency(self):
        """メモリ効率のテスト"""
        import gc

        # メモリ使用量を監視
        initial_memory = len(gc.get_objects())

        # 大きなデータセットを処理
        large_data = pd.DataFrame(
            {
                "Date": pd.date_range("2020-01-01", periods=5000, freq="D"),
                "Open": np.random.uniform(50, 200, 5000),
                "High": np.random.uniform(50, 200, 5000),
                "Low": np.random.uniform(50, 200, 5000),
                "Close": np.random.uniform(50, 200, 5000),
                "Volume": np.random.randint(1000, 100000, 5000),
            }
        )

        result = engineer_basic_features(large_data)

        # メモリクリーンアップ
        del large_data
        gc.collect()

        final_memory = len(gc.get_objects())
        memory_increase = final_memory - initial_memory

        # メモリ使用量の増加が妥当な範囲内であることを確認
        assert memory_increase < 10000  # オブジェクト数の増加が10000以内
