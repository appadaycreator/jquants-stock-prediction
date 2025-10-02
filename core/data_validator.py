#!/usr/bin/env python3
"""
データ検証システム
データの品質チェック、検証、前処理を管理
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime


class DataValidator:
    """データ検証クラス"""

    def __init__(self, logger=None, error_handler=None):
        """初期化"""
        self.logger = logger
        self.error_handler = error_handler

    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """データの検証"""
        try:
            if data is None or len(data) == 0:
                return {"is_valid": False, "issues": ["データが空です"]}

            issues = []
            warnings = []

            # 基本チェック
            basic_validation = self._validate_basic_structure(data)
            issues.extend(basic_validation["issues"])
            warnings.extend(basic_validation["warnings"])

            # 数値データのチェック
            numeric_validation = self._validate_numeric_data(data)
            issues.extend(numeric_validation["issues"])
            warnings.extend(numeric_validation["warnings"])

            # 時系列データのチェック
            time_series_validation = self._validate_time_series_data(data)
            issues.extend(time_series_validation["issues"])
            warnings.extend(time_series_validation["warnings"])

            return {
                "is_valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "data_shape": data.shape,
                "validation_timestamp": datetime.now().isoformat(),
                "message": (
                    "データ検証成功" if len(issues) == 0 else "データ検証で問題を発見"
                )
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_validation_error(e)
            return {"is_valid": False, "issues": [f"データ検証エラー: {str(e)}"]}

    def _validate_basic_structure(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """基本構造の検証"""
        issues = []
        warnings = []

        # データサイズのチェック
        if len(data) < 10:
            issues.append("データが少なすぎます（最低10行必要）")
        elif len(data) < 50:
            warnings.append("データが少ないです（50行以上推奨）")

        # 列数のチェック
        if len(data.columns) < 2:
            issues.append("列数が少なすぎます（最低2列必要）")

        return {"issues": issues, "warnings": warnings}

    def _validate_numeric_data(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """数値データの検証"""
        issues = []
        warnings = []

        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            # 欠損値のチェック
            missing_ratio = data[col].isnull().sum() / len(data)
            if missing_ratio > 0.5:
                issues.append(f"列 '{col}' に欠損値が多すぎます（{missing_ratio:.1%}）")
            elif missing_ratio > 0.1:
                warnings.append(f"列 '{col}' に欠損値があります（{missing_ratio:.1%}）")

            # 無限値のチェック
            if np.isinf(data[col]).any():
                issues.append(f"列 '{col}' に無限値が含まれています")

            # 分散のチェック
            if data[col].var() == 0:
                warnings.append(f"列 '{col}' の分散が0です（定数値）")

        return {"issues": issues, "warnings": warnings}

    def _validate_time_series_data(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """時系列データの検証"""
        issues = []
        warnings = []

        # 日付列のチェック
        date_columns = data.select_dtypes(include=['datetime64']).columns
        if len(date_columns) == 0:
            warnings.append("日付列が見つかりません")

        # 重複のチェック
        if data.duplicated().any():
            duplicate_count = data.duplicated().sum()
            warnings.append(f"重複行が {duplicate_count} 行あります")

        return {"issues": issues, "warnings": warnings}

    def validate_features(self, data: pd.DataFrame, features: List[str]) -> Dict[str, Any]:
        """特徴量の検証"""
        try:
            missing_features = [f for f in features if f not in data.columns]
            
            if missing_features:
                return {
                    "is_valid": False,
                    "missing_features": missing_features,
                    "message": f"不足している特徴量: {missing_features}"
                }

            # 特徴量の品質チェック
            quality_issues = []
            for feature in features:
                if data[feature].dtype not in ['int64', 'float64']:
                    quality_issues.append(f"特徴量 '{feature}' が数値型ではありません")
                elif data[feature].isnull().any():
                    quality_issues.append(f"特徴量 '{feature}' に欠損値があります")

            return {
                "is_valid": len(quality_issues) == 0,
                "quality_issues": quality_issues,
                "feature_count": len(features),
                "message": "特徴量検証成功" if len(quality_issues) == 0 else "特徴量に問題があります"
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_validation_error(e)
            return {"is_valid": False, "issues": [f"特徴量検証エラー: {str(e)}"]}

    def validate_target(self, data: pd.DataFrame, target: str) -> Dict[str, Any]:
        """ターゲット変数の検証"""
        try:
            if target not in data.columns:
                return {
                    "is_valid": False,
                    "message": f"ターゲット変数 '{target}' が見つかりません"
                }

            target_data = data[target]
            
            # 基本チェック
            if target_data.isnull().any():
                return {
                    "is_valid": False,
                    "message": "ターゲット変数に欠損値があります"
                }

            if np.isinf(target_data).any():
                return {
                    "is_valid": False,
                    "message": "ターゲット変数に無限値があります"
                }

            return {
                "is_valid": True,
                "target_type": str(target_data.dtype),
                "target_range": [float(target_data.min()), float(target_data.max())],
                "message": "ターゲット変数検証成功"
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_validation_error(e)
            return {"is_valid": False, "issues": [f"ターゲット変数検証エラー: {str(e)}"]}

    def get_validation_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """検証サマリーの取得"""
        try:
            return {
                "data_shape": data.shape,
                "columns": list(data.columns),
                "dtypes": data.dtypes.to_dict(),
                "missing_values": data.isnull().sum().to_dict(),
                "numeric_columns": list(data.select_dtypes(include=[np.number]).columns),
                "datetime_columns": list(data.select_dtypes(include=['datetime64']).columns),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_validation_error(e)
            return {"error": str(e)}
