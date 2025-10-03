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

    def validate_stock_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """株価データの検証"""
        try:
            if data is None or len(data) == 0:
                return {
                    "is_valid": False,
                    "errors": ["データが空です"],
                    "warnings": [],
                    "data_quality_score": 0,
                    "validation_timestamp": datetime.now().isoformat()
                }

            errors = []
            warnings = []
            quality_score = 100

            # 必須カラムのチェック
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                errors.append(f"必須カラムが不足: {missing_columns}")
                quality_score -= 20

            # データ型のチェック
            for col in required_columns:
                if col in data.columns:
                    if col == 'date':
                        # 日付列のチェック
                        try:
                            pd.to_datetime(data[col])
                        except:
                            errors.append(f"日付形式が無効: {col}")
                            quality_score -= 10
                    else:
                        # 数値列のチェック
                        if not pd.api.types.is_numeric_dtype(data[col]):
                            errors.append(f"数値型でない: {col}")
                            quality_score -= 10

            # 負の価格のチェック
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in data.columns:
                    if (data[col] < 0).any():
                        errors.append(f"負の価格が含まれています: {col}")
                        quality_score -= 15
                    if (data[col] == 0).any():
                        errors.append(f"ゼロ価格が含まれています: {col}")
                        quality_score -= 10

            # 高値・安値の整合性チェック
            if 'high' in data.columns and 'low' in data.columns:
                if (data['high'] < data['low']).any():
                    errors.append("高値・安値の整合性がありません（high < low）")
                    quality_score -= 15

            # ボリュームのチェック
            if 'volume' in data.columns:
                if (data['volume'] < 0).any():
                    errors.append("負のボリュームが含まれています")
                    quality_score -= 10
                if (data['volume'] == 0).any():
                    warnings.append("ゼロボリュームが含まれています")
                    quality_score -= 5

            # 欠損値のチェック
            for col in data.columns:
                if data[col].isnull().any():
                    errors.append(f"欠損値が含まれています: {col}")
                    quality_score -= 10

            # 無限値のチェック
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if np.isinf(data[col]).any():
                    errors.append(f"無限値が含まれています: {col}")
                    quality_score -= 15

            # 重複日付のチェック
            if 'date' in data.columns:
                if data['date'].duplicated().any():
                    errors.append("重複日付が含まれています")
                    quality_score -= 10

            # 外れ値のチェック（簡易版）
            for col in price_columns:
                if col in data.columns and len(data) > 3:  # データが少なすぎる場合はスキップ
                    Q1 = data[col].quantile(0.25)
                    Q3 = data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    if IQR > 0:  # IQRが0でない場合のみ
                        outliers = data[(data[col] < Q1 - 1.5 * IQR) | (data[col] > Q3 + 1.5 * IQR)]
                        if len(outliers) > 0:
                            warnings.append(f"外れ値が検出されました: {col} ({len(outliers)}件)")
                            quality_score -= 5

            # データ数が少ない場合の警告
            if len(data) < 5:
                warnings.append("データ数が少ないです（5行未満）")
                quality_score -= 10

            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "data_quality_score": max(0, quality_score),
                "validation_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_validation_error(e)
            return {
                "is_valid": False,
                "errors": [f"検証エラー: {str(e)}"],
                "warnings": [],
                "data_quality_score": 0,
                "validation_timestamp": datetime.now().isoformat()
            }

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
