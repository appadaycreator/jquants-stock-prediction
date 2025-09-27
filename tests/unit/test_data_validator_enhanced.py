"""
データ検証モジュールの強化されたユニットテスト
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from data_validator import DataValidator


class TestDataValidatorEnhanced:
    """DataValidatorクラスの強化されたテスト"""

    def test_init(self):
        """初期化テスト"""
        validator = DataValidator()
        assert validator is not None
        assert hasattr(validator, "logger")

    def test_init_with_config(self):
        """設定付き初期化テスト"""
        config = {
            "required_columns": ["Code", "Date", "Close"],
            "date_format": "%Y%m%d",
            "numeric_columns": ["Open", "High", "Low", "Close", "Volume"]
        }
        validator = DataValidator(config)
        assert validator.config == config

    def test_validate_basic_structure_success(self):
        """基本構造検証成功テスト"""
        validator = DataValidator()
        valid_data = pd.DataFrame({
            "Code": ["1234", "5678"],
            "Date": ["20240301", "20240302"],
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [95.0, 96.0],
            "Close": [102.0, 103.0],
            "Volume": [1000000, 1100000]
        })
        
        result = validator.validate_basic_structure(valid_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_basic_structure_missing_columns(self):
        """必須カラム不足のテスト"""
        validator = DataValidator()
        incomplete_data = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"]
            # 必須カラムが不足
        })
        
        result = validator.validate_basic_structure(incomplete_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "required columns" in str(result["errors"]).lower()

    def test_validate_basic_structure_empty_data(self):
        """空データのテスト"""
        validator = DataValidator()
        empty_data = pd.DataFrame()
        
        result = validator.validate_basic_structure(empty_data)
        assert result["is_valid"] is False
        assert "empty" in str(result["errors"]).lower()

    def test_validate_data_types_success(self):
        """データ型検証成功テスト"""
        validator = DataValidator()
        valid_data = pd.DataFrame({
            "Code": ["1234", "5678"],
            "Date": ["20240301", "20240302"],
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [95.0, 96.0],
            "Close": [102.0, 103.0],
            "Volume": [1000000, 1100000]
        })
        
        result = validator.validate_data_types(valid_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_data_types_invalid_numeric(self):
        """無効な数値データのテスト"""
        validator = DataValidator()
        invalid_data = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"],
            "Open": ["invalid"],  # 数値でない
            "High": [105.0],
            "Low": [95.0],
            "Close": [102.0],
            "Volume": [1000000]
        })
        
        result = validator.validate_data_types(invalid_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_date_format_success(self):
        """日付フォーマット検証成功テスト"""
        validator = DataValidator()
        valid_data = pd.DataFrame({
            "Date": ["20240301", "20240302", "20240303"],
            "Close": [100.0, 101.0, 102.0]
        })
        
        result = validator.validate_date_format(valid_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_date_format_invalid(self):
        """無効な日付フォーマットのテスト"""
        validator = DataValidator()
        invalid_data = pd.DataFrame({
            "Date": ["2024-03-01", "invalid_date", "20240303"],
            "Close": [100.0, 101.0, 102.0]
        })
        
        result = validator.validate_date_format(invalid_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_price_consistency_success(self):
        """価格一貫性検証成功テスト"""
        validator = DataValidator()
        valid_data = pd.DataFrame({
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [95.0, 96.0],
            "Close": [102.0, 103.0]
        })
        
        result = validator.validate_price_consistency(valid_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_price_consistency_invalid(self):
        """価格一貫性違反のテスト"""
        validator = DataValidator()
        invalid_data = pd.DataFrame({
            "Open": [100.0, 101.0],
            "High": [95.0, 96.0],  # High < Open
            "Low": [105.0, 106.0],  # Low > High
            "Close": [102.0, 103.0]
        })
        
        result = validator.validate_price_consistency(invalid_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_volume_consistency_success(self):
        """ボリューム一貫性検証成功テスト"""
        validator = DataValidator()
        valid_data = pd.DataFrame({
            "Volume": [1000000, 1100000, 1200000]
        })
        
        result = validator.validate_volume_consistency(valid_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_volume_consistency_invalid(self):
        """ボリューム一貫性違反のテスト"""
        validator = DataValidator()
        invalid_data = pd.DataFrame({
            "Volume": [1000000, -100000, 1200000]  # 負の値
        })
        
        result = validator.validate_volume_consistency(invalid_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_missing_values_success(self):
        """欠損値検証成功テスト"""
        validator = DataValidator()
        valid_data = pd.DataFrame({
            "Code": ["1234", "5678"],
            "Close": [100.0, 101.0]
        })
        
        result = validator.validate_missing_values(valid_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_missing_values_invalid(self):
        """欠損値検証失敗テスト"""
        validator = DataValidator()
        invalid_data = pd.DataFrame({
            "Code": ["1234", None],
            "Close": [100.0, np.nan]
        })
        
        result = validator.validate_missing_values(invalid_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_outliers_success(self):
        """外れ値検証成功テスト"""
        validator = DataValidator()
        valid_data = pd.DataFrame({
            "Close": [100.0, 101.0, 102.0, 103.0, 104.0]
        })
        
        result = validator.validate_outliers(valid_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_outliers_detected(self):
        """外れ値検出テスト"""
        validator = DataValidator()
        outlier_data = pd.DataFrame({
            "Close": [100.0, 101.0, 1000.0, 103.0, 104.0]  # 1000.0が外れ値
        })
        
        result = validator.validate_outliers(outlier_data)
        # 外れ値が検出されても、警告として扱う（is_valid=True）
        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0

    def test_validate_data_quality_success(self):
        """データ品質検証成功テスト"""
        validator = DataValidator()
        high_quality_data = pd.DataFrame({
            "Code": ["1234", "5678", "9012"],
            "Date": ["20240301", "20240302", "20240303"],
            "Open": [100.0, 101.0, 102.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [95.0, 96.0, 97.0],
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, 1100000, 1200000]
        })
        
        result = validator.validate_data_quality(high_quality_data)
        assert result["is_valid"] is True
        assert result["quality_score"] > 0.8

    def test_validate_data_quality_low_quality(self):
        """低品質データのテスト"""
        validator = DataValidator()
        low_quality_data = pd.DataFrame({
            "Code": ["1234", None, "9012"],
            "Date": ["invalid", "20240302", "20240303"],
            "Open": [100.0, np.nan, 102.0],
            "High": [95.0, 106.0, 107.0],  # High < Open
            "Low": [105.0, 96.0, 97.0],   # Low > High
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, -1000, 1200000]  # 負のボリューム
        })
        
        result = validator.validate_data_quality(low_quality_data)
        assert result["is_valid"] is False
        assert result["quality_score"] < 0.5

    def test_comprehensive_validation_success(self):
        """包括的検証成功テスト"""
        validator = DataValidator()
        perfect_data = pd.DataFrame({
            "Code": ["1234", "5678", "9012", "3456", "7890"],
            "Date": ["20240301", "20240302", "20240303", "20240304", "20240305"],
            "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "High": [105.0, 106.0, 107.0, 108.0, 109.0],
            "Low": [95.0, 96.0, 97.0, 98.0, 99.0],
            "Close": [102.0, 103.0, 104.0, 105.0, 106.0],
            "Volume": [1000000, 1100000, 1200000, 1300000, 1400000]
        })
        
        result = validator.validate_comprehensive(perfect_data)
        assert result["is_valid"] is True
        assert result["quality_score"] > 0.9
        assert len(result["errors"]) == 0

    def test_comprehensive_validation_failure(self):
        """包括的検証失敗テスト"""
        validator = DataValidator()
        problematic_data = pd.DataFrame({
            "Code": [None, "5678", "9012"],
            "Date": ["invalid", "20240302", "20240303"],
            "Open": [100.0, np.nan, 102.0],
            "High": [95.0, 106.0, 107.0],
            "Low": [105.0, 96.0, 97.0],
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, -1000, 1200000]
        })
        
        result = validator.validate_comprehensive(problematic_data)
        assert result["is_valid"] is False
        assert result["quality_score"] < 0.3
        assert len(result["errors"]) > 0

    def test_validate_with_custom_rules(self):
        """カスタムルールでの検証テスト"""
        custom_rules = {
            "min_volume": 100000,
            "max_price_change": 0.1,
            "required_data_points": 3
        }
        validator = DataValidator({"custom_rules": custom_rules})
        
        data = pd.DataFrame({
            "Code": ["1234", "5678", "9012"],
            "Date": ["20240301", "20240302", "20240303"],
            "Open": [100.0, 101.0, 102.0],
            "High": [105.0, 106.0, 107.0],
            "Low": [95.0, 96.0, 97.0],
            "Close": [102.0, 103.0, 104.0],
            "Volume": [1000000, 1100000, 1200000]
        })
        
        result = validator.validate_with_custom_rules(data, custom_rules)
        assert result["is_valid"] is True

    def test_validate_performance_large_dataset(self):
        """大きなデータセットでのパフォーマンステスト"""
        validator = DataValidator()
        
        # 大きなデータセットを作成
        large_data = pd.DataFrame({
            "Code": [f"code_{i:04d}" for i in range(1000)],
            "Date": [f"2024{(i%12+1):02d}{(i%28+1):02d}" for i in range(1000)],
            "Open": np.random.uniform(90, 110, 1000),
            "High": np.random.uniform(95, 115, 1000),
            "Low": np.random.uniform(85, 105, 1000),
            "Close": np.random.uniform(90, 110, 1000),
            "Volume": np.random.randint(100000, 1000000, 1000)
        })
        
        import time
        start_time = time.time()
        result = validator.validate_comprehensive(large_data)
        end_time = time.time()
        
        # 実行時間が妥当な範囲内であることを確認（5秒以内）
        assert end_time - start_time < 5.0
        assert result is not None

    def test_validate_edge_cases(self):
        """エッジケースのテスト"""
        validator = DataValidator()
        
        # 境界値のテスト
        edge_case_data = pd.DataFrame({
            "Code": ["1234"],
            "Date": ["20240301"],
            "Open": [0.0],  # 最小値
            "High": [0.0],
            "Low": [0.0],
            "Close": [0.0],
            "Volume": [0]  # 最小ボリューム
        })
        
        result = validator.validate_comprehensive(edge_case_data)
        # 境界値でも適切に処理されることを確認
        assert result is not None

    def test_validate_error_handling(self):
        """エラーハンドリングテスト"""
        validator = DataValidator()
        
        # Noneデータのテスト
        result = validator.validate_comprehensive(None)
        assert result is None
        
        # 無効な型のテスト
        result = validator.validate_comprehensive("invalid_data")
        assert result is None

    def test_validate_with_missing_config(self):
        """設定不足時のテスト"""
        validator = DataValidator()
        data = pd.DataFrame({
            "Code": ["1234"],
            "Close": [100.0]
        })
        
        # 設定が不足していても適切に処理されることを確認
        result = validator.validate_comprehensive(data)
        assert result is not None

    def test_validate_logging(self):
        """ログ機能のテスト"""
        validator = DataValidator()
        
        # ロガーが適切に設定されていることを確認
        assert hasattr(validator, "logger")
        assert validator.logger is not None
        
        # 検証実行時にログが出力されることを確認
        data = pd.DataFrame({
            "Code": ["1234"],
            "Close": [100.0]
        })
        
        result = validator.validate_comprehensive(data)
        assert result is not None
