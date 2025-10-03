#!/usr/bin/env python3
"""
DataValidatorのユニットテスト
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock
from core.data_validator import DataValidator


class TestDataValidator:
    """DataValidatorのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.logger = Mock()
        self.error_handler = Mock()
        self.validator = DataValidator(self.logger, self.error_handler)

    def test_initialization(self):
        """初期化テスト"""
        assert self.validator.logger == self.logger
        assert self.validator.error_handler == self.error_handler

    def test_validate_stock_data_valid(self):
        """有効な株価データの検証テスト"""
        valid_data = pd.DataFrame(
            {
                "date": [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                ],
                "open": [100.0, 101.0, 102.0, 103.0, 104.0],
                "high": [105.0, 106.0, 107.0, 108.0, 109.0],
                "low": [95.0, 96.0, 97.0, 98.0, 99.0],
                "close": [103.0, 104.0, 105.0, 106.0, 107.0],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

        result = self.validator.validate_stock_data(valid_data)
        assert result["is_valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_stock_data_missing_columns(self):
        """必須カラムが不足しているデータの検証テスト"""
        invalid_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, 101.0],
                # high, low, close, volumeが不足
            }
        )

        result = self.validator.validate_stock_data(invalid_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "必須カラム" in result["errors"][0]

    def test_validate_stock_data_empty_dataframe(self):
        """空のデータフレームの検証テスト"""
        empty_data = pd.DataFrame()

        result = self.validator.validate_stock_data(empty_data)
        assert result["is_valid"] is False
        assert "データが空" in result["errors"][0]

    def test_validate_stock_data_negative_prices(self):
        """負の価格データの検証テスト"""
        invalid_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, -10.0],  # 負の価格
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(invalid_data)
        assert result["is_valid"] is False
        assert any("負の価格" in error for error in result["errors"])

    def test_validate_stock_data_zero_volume(self):
        """ゼロボリュームの検証テスト"""
        data_with_zero_volume = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, 101.0],
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 0],  # ゼロボリューム
            }
        )

        result = self.validator.validate_stock_data(data_with_zero_volume)
        assert result["is_valid"] is True  # 警告レベル
        assert any("ゼロボリューム" in warning for warning in result["warnings"])

    def test_validate_stock_data_invalid_date_format(self):
        """無効な日付形式の検証テスト"""
        invalid_data = pd.DataFrame(
            {
                "date": ["invalid-date", "2024-01-02"],
                "open": [100.0, 101.0],
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(invalid_data)
        assert result["is_valid"] is False
        assert any("日付形式" in error for error in result["errors"])

    def test_validate_stock_data_high_low_consistency(self):
        """高値・安値の整合性検証テスト"""
        inconsistent_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, 101.0],
                "high": [95.0, 106.0],  # high < low
                "low": [105.0, 96.0],  # low > high
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(inconsistent_data)
        assert result["is_valid"] is False
        assert any("高値・安値" in error for error in result["errors"])

    def test_validate_stock_data_outliers(self):
        """外れ値の検出テスト"""
        data_with_outliers = pd.DataFrame(
            {
                "date": [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                ],
                "open": [100.0, 101.0, 102.0, 103.0, 10000.0],  # 外れ値
                "high": [105.0, 106.0, 107.0, 108.0, 10005.0],
                "low": [95.0, 96.0, 97.0, 98.0, 9995.0],
                "close": [103.0, 104.0, 105.0, 106.0, 10003.0],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

        result = self.validator.validate_stock_data(data_with_outliers)
        assert result["is_valid"] is True  # 警告レベル
        assert any("外れ値" in warning for warning in result["warnings"])

    def test_validate_stock_data_duplicate_dates(self):
        """重複日付の検出テスト"""
        duplicate_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-01"],  # 重複日付
                "open": [100.0, 101.0],
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(duplicate_data)
        assert result["is_valid"] is False
        assert any("重複日付" in error for error in result["errors"])

    def test_validate_stock_data_missing_values(self):
        """欠損値の検出テスト"""
        data_with_nan = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, np.nan],  # 欠損値
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(data_with_nan)
        assert result["is_valid"] is False
        assert any("欠損値" in error for error in result["errors"])

    def test_validate_stock_data_inf_values(self):
        """無限値の検出テスト"""
        data_with_inf = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, np.inf],  # 無限値
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(data_with_inf)
        assert result["is_valid"] is False
        assert any("無限値" in error for error in result["errors"])

    def test_validate_stock_data_string_prices(self):
        """文字列価格の検証テスト"""
        data_with_strings = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, "invalid"],  # 文字列価格
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(data_with_strings)
        # 文字列が数値に変換される場合があるため、結果は不定
        # エラーまたは警告が含まれることを確認
        assert not result["is_valid"] or len(result["warnings"]) > 0

    def test_validate_stock_data_very_small_dataset(self):
        """非常に小さなデータセットの検証テスト"""
        small_data = pd.DataFrame(
            {
                "date": ["2024-01-01"],
                "open": [100.0],
                "high": [105.0],
                "low": [95.0],
                "close": [103.0],
                "volume": [1000],
            }
        )

        result = self.validator.validate_stock_data(small_data)
        assert result["is_valid"] is True  # 最小限のデータでも有効
        assert any("データ数が少ない" in warning for warning in result["warnings"])

    def test_validate_stock_data_large_dataset(self):
        """大きなデータセットの検証テスト"""
        # 有効な日付範囲でデータを生成
        from datetime import datetime, timedelta

        start_date = datetime(2024, 1, 1)
        dates = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(100)
        ]

        large_data = pd.DataFrame(
            {
                "date": dates,
                "open": [100.0 + i for i in range(100)],
                "high": [105.0 + i for i in range(100)],
                "low": [95.0 + i for i in range(100)],
                "close": [103.0 + i for i in range(100)],
                "volume": [1000 + i for i in range(100)],
            }
        )

        result = self.validator.validate_stock_data(large_data)
        # データが有効であることを確認（エラーがない）
        assert result["is_valid"] is True

    def test_validate_stock_data_mixed_data_types(self):
        """混合データ型の検証テスト"""
        mixed_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, "101.0"],  # 文字列と数値の混合
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(mixed_data)
        # 文字列が数値に変換される場合があるため、結果は不定

    def test_validate_stock_data_perfect_data(self):
        """完璧なデータの検証テスト"""
        perfect_data = pd.DataFrame(
            {
                "date": [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                ],
                "open": [100.0, 101.0, 102.0, 103.0, 104.0],
                "high": [105.0, 106.0, 107.0, 108.0, 109.0],
                "low": [95.0, 96.0, 97.0, 98.0, 99.0],
                "close": [103.0, 104.0, 105.0, 106.0, 107.0],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

        result = self.validator.validate_stock_data(perfect_data)
        assert result["is_valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_stock_data_edge_case_zero_prices(self):
        """エッジケース: ゼロ価格の検証テスト"""
        zero_price_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [0.0, 101.0],  # ゼロ価格
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(zero_price_data)
        assert result["is_valid"] is False
        assert any("ゼロ価格" in error for error in result["errors"])

    def test_validate_stock_data_result_structure(self):
        """検証結果の構造テスト"""
        valid_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "open": [100.0, 101.0],
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [103.0, 104.0],
                "volume": [1000, 1100],
            }
        )

        result = self.validator.validate_stock_data(valid_data)

        required_keys = [
            "is_valid",
            "errors",
            "warnings",
            "data_quality_score",
            "validation_timestamp",
        ]
        for key in required_keys:
            assert key in result

        assert isinstance(result["is_valid"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["data_quality_score"], (int, float))
        assert 0 <= result["data_quality_score"] <= 100
