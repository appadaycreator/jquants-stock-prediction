#!/usr/bin/env python3
"""
型安全なデータ検証モジュール
実行時エラーを防ぎ、データ整合性を保証する
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime
import warnings

logger = logging.getLogger(__name__)


class TypeSafeValidator:
    """型安全なデータ検証クラス"""

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.validation_results = {}

    def validate_dataframe_structure(
        self, df: pd.DataFrame, required_columns: List[str]
    ) -> Dict[str, Any]:
        """DataFrameの構造検証"""
        logger.info("🔍 DataFrame構造の検証を開始")

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "missing_columns": [],
            "extra_columns": [],
        }

        # 必須カラムの存在確認
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            result["missing_columns"] = missing_columns
            result["errors"].append(f"必須カラムが不足: {missing_columns}")
            result["is_valid"] = False

        # 余分なカラムの確認
        extra_columns = [col for col in df.columns if col not in required_columns]
        if extra_columns:
            result["extra_columns"] = extra_columns
            result["warnings"].append(f"予期しないカラム: {extra_columns}")

        logger.info(f"✅ DataFrame構造検証完了: {len(df.columns)}カラム, {len(df)}行")
        return result

    def validate_numeric_columns(
        self, df: pd.DataFrame, numeric_columns: List[str]
    ) -> Dict[str, Any]:
        """数値カラムの型安全性検証"""
        logger.info("🔢 数値カラムの型安全性検証を開始")

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "conversion_issues": {},
            "nan_issues": {},
            "inf_issues": {},
        }

        for col in numeric_columns:
            if col not in df.columns:
                result["warnings"].append(f"カラム '{col}' が存在しません")
                continue

            # 型変換の検証
            try:
                original_dtype = df[col].dtype
                converted_series = pd.to_numeric(df[col], errors="coerce")

                # NaN値の確認
                nan_count = converted_series.isna().sum()
                if nan_count > 0:
                    result["nan_issues"][col] = nan_count
                    if self.strict_mode and nan_count > len(df) * 0.5:  # 50%以上
                        result["errors"].append(
                            f"カラム '{col}' に過度のNaN値: {nan_count}件"
                        )
                        result["is_valid"] = False
                    else:
                        result["warnings"].append(
                            f"カラム '{col}' にNaN値: {nan_count}件"
                        )

                # 無限値の確認
                inf_count = np.isinf(converted_series).sum()
                if inf_count > 0:
                    result["inf_issues"][col] = inf_count
                    result["errors"].append(f"カラム '{col}' に無限値: {inf_count}件")
                    result["is_valid"] = False

                # 型変換の問題
                if original_dtype != converted_series.dtype:
                    result["conversion_issues"][col] = {
                        "original": str(original_dtype),
                        "converted": str(converted_series.dtype),
                    }
                    result["warnings"].append(
                        f"カラム '{col}' の型変換: {original_dtype} -> {converted_series.dtype}"
                    )

            except Exception as e:
                result["errors"].append(f"カラム '{col}' の検証エラー: {e}")
                result["is_valid"] = False

        logger.info("✅ 数値カラムの型安全性検証完了")
        return result

    def validate_date_columns(
        self, df: pd.DataFrame, date_columns: List[str]
    ) -> Dict[str, Any]:
        """日付カラムの型安全性検証"""
        logger.info("📅 日付カラムの型安全性検証を開始")

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "conversion_issues": {},
            "range_issues": {},
        }

        for col in date_columns:
            if col not in df.columns:
                result["warnings"].append(f"カラム '{col}' が存在しません")
                continue

            try:
                # 日付変換の検証
                converted_dates = pd.to_datetime(df[col], errors="coerce")

                # NaN値の確認
                nan_count = converted_dates.isna().sum()
                if nan_count > 0:
                    result["warnings"].append(
                        f"カラム '{col}' に無効な日付: {nan_count}件"
                    )

                # 日付範囲の確認
                if not converted_dates.empty:
                    min_date = converted_dates.min()
                    max_date = converted_dates.max()

                    # 異常な日付の確認
                    current_year = datetime.now().year
                    if min_date.year < 1900 or max_date.year > current_year + 1:
                        result["range_issues"][col] = {
                            "min": str(min_date),
                            "max": str(max_date),
                        }
                        result["warnings"].append(
                            f"カラム '{col}' に異常な日付範囲: {min_date} - {max_date}"
                        )

            except Exception as e:
                result["errors"].append(f"カラム '{col}' の日付検証エラー: {e}")
                result["is_valid"] = False

        logger.info("✅ 日付カラムの型安全性検証完了")
        return result

    def safe_nan_handling(
        self, df: pd.DataFrame, strategy: str = "forward_fill"
    ) -> pd.DataFrame:
        """安全なNaN値処理"""
        logger.info(f"🧹 安全なNaN値処理を開始 (戦略: {strategy})")

        original_nan_count = df.isnull().sum().sum()
        if original_nan_count == 0:
            logger.info("✅ NaN値は存在しません")
            return df

        df_processed = df.copy()

        try:
            if strategy == "forward_fill":
                df_processed = df_processed.fillna(method="ffill")
                df_processed = df_processed.fillna(
                    method="bfill"
                )  # 前方補完で処理できない場合
            elif strategy == "backward_fill":
                df_processed = df_processed.fillna(method="bfill")
                df_processed = df_processed.fillna(
                    method="ffill"
                )  # 後方補完で処理できない場合
            elif strategy == "mean":
                numeric_columns = df_processed.select_dtypes(
                    include=[np.number]
                ).columns
                df_processed[numeric_columns] = df_processed[numeric_columns].fillna(
                    df_processed[numeric_columns].mean()
                )
            elif strategy == "median":
                numeric_columns = df_processed.select_dtypes(
                    include=[np.number]
                ).columns
                df_processed[numeric_columns] = df_processed[numeric_columns].fillna(
                    df_processed[numeric_columns].median()
                )
            elif strategy == "drop":
                df_processed = df_processed.dropna()
            else:
                raise ValueError(f"未知のNaN処理戦略: {strategy}")

            final_nan_count = df_processed.isnull().sum().sum()
            processed_count = original_nan_count - final_nan_count

            logger.info(
                f"✅ NaN値処理完了: {processed_count}件処理, 残り{final_nan_count}件"
            )

            if final_nan_count > 0:
                logger.warning(f"⚠️ {final_nan_count}件のNaN値が残っています")

        except Exception as e:
            logger.error(f"❌ NaN値処理エラー: {e}")
            raise

        return df_processed

    def validate_data_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """データ整合性の包括的検証"""
        logger.info("🔍 データ整合性の包括的検証を開始")

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "consistency_issues": {},
        }

        # 重複行の確認
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            result["warnings"].append(f"重複行: {duplicate_count}件")
            result["consistency_issues"]["duplicates"] = duplicate_count

        # 数値カラムの整合性確認
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in ["Open", "High", "Low", "Close"]:
                # OHLCの整合性確認
                invalid_ohlc = (
                    (df["High"] < df["Low"])
                    | (df["High"] < df["Open"])
                    | (df["High"] < df["Close"])
                    | (df["Low"] > df["Open"])
                    | (df["Low"] > df["Close"])
                ).sum()

                if invalid_ohlc > 0:
                    result["errors"].append(f"OHLC整合性エラー: {invalid_ohlc}件")
                    result["is_valid"] = False
                    result["consistency_issues"][f"{col}_ohlc"] = invalid_ohlc

        # 負の値の確認
        for col in ["Volume", "Open", "High", "Low", "Close"]:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    result["warnings"].append(
                        f"カラム '{col}' に負の値: {negative_count}件"
                    )
                    result["consistency_issues"][f"{col}_negative"] = negative_count

        logger.info("✅ データ整合性検証完了")
        return result

    def create_type_safe_dataframe(
        self, data: Union[Dict, List, pd.DataFrame], column_types: Dict[str, str]
    ) -> pd.DataFrame:
        """型安全なDataFrameの作成"""
        logger.info("🛡️ 型安全なDataFrameの作成を開始")

        try:
            if isinstance(data, pd.DataFrame):
                df = data.copy()
            else:
                df = pd.DataFrame(data)

            # カラム型の適用
            for col, dtype in column_types.items():
                if col in df.columns:
                    try:
                        if dtype == "numeric":
                            df[col] = pd.to_numeric(df[col], errors="coerce")
                        elif dtype == "datetime":
                            df[col] = pd.to_datetime(df[col], errors="coerce")
                        elif dtype == "category":
                            df[col] = df[col].astype("category")
                        else:
                            df[col] = df[col].astype(dtype)
                    except Exception as e:
                        logger.warning(f"カラム '{col}' の型変換に失敗: {e}")

            # NaN値の安全な処理
            df = self.safe_nan_handling(df)

            logger.info("✅ 型安全なDataFrameの作成完了")
            return df

        except Exception as e:
            logger.error(f"❌ 型安全なDataFrameの作成エラー: {e}")
            raise


def validate_stock_data_types(df: pd.DataFrame) -> Dict[str, Any]:
    """株価データの型安全性検証（専用関数）"""
    validator = TypeSafeValidator(strict_mode=True)

    # 必須カラムの定義
    required_columns = ["Date", "Code", "Open", "High", "Low", "Close", "Volume"]
    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
    date_columns = ["Date"]

    # 構造検証
    structure_result = validator.validate_dataframe_structure(df, required_columns)

    # 数値カラム検証
    numeric_result = validator.validate_numeric_columns(df, numeric_columns)

    # 日付カラム検証
    date_result = validator.validate_date_columns(df, date_columns)

    # 整合性検証
    consistency_result = validator.validate_data_consistency(df)

    # 結果の統合
    combined_result = {
        "is_valid": all(
            [
                structure_result["is_valid"],
                numeric_result["is_valid"],
                date_result["is_valid"],
                consistency_result["is_valid"],
            ]
        ),
        "errors": (
            structure_result["errors"]
            + numeric_result["errors"]
            + date_result["errors"]
            + consistency_result["errors"]
        ),
        "warnings": (
            structure_result["warnings"]
            + numeric_result["warnings"]
            + date_result["warnings"]
            + consistency_result["warnings"]
        ),
        "structure": structure_result,
        "numeric": numeric_result,
        "date": date_result,
        "consistency": consistency_result,
    }

    return combined_result
