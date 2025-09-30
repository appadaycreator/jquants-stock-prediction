#!/usr/bin/env python3
"""
強化されたデータ検証モジュール
データ品質の向上と異常値検出の改善
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import warnings
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class ValidationLevel(Enum):
    """検証レベルの定義"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    CUSTOM = "custom"


@dataclass
class ValidationResult:
    """検証結果のデータクラス"""

    is_valid: bool
    score: float
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    detailed_report: Dict[str, Any]


class EnhancedDataValidator:
    """強化されたデータ検証クラス"""

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)

        # 検証ルールの設定
        self.validation_rules = self._setup_validation_rules()

    def _setup_validation_rules(self) -> Dict[str, Any]:
        """検証ルールの設定"""
        rules = {
            "required_columns": ["Date", "Open", "High", "Low", "Close", "Volume"],
            "numeric_columns": ["Open", "High", "Low", "Close", "Volume"],
            "date_column": "Date",
            "ohlc_validation": True,
            "volume_validation": True,
            "outlier_detection": True,
            "missing_value_threshold": 0.1,  # 10%以上欠損値がある場合は警告
            "outlier_threshold": 3.0,  # 3σルール
            "volume_min": 0,  # ボリュームの最小値
            "price_min": 0.01,  # 価格の最小値
            "price_max": 1000000,  # 価格の最大値
        }

        if self.validation_level == ValidationLevel.STRICT:
            rules.update(
                {
                    "missing_value_threshold": 0.05,  # 5%以上欠損値がある場合はエラー
                    "outlier_threshold": 2.5,  # 2.5σルール
                    "require_ohlc_consistency": True,
                    "require_volume_consistency": True,
                }
            )
        elif self.validation_level == ValidationLevel.BASIC:
            rules.update(
                {
                    "missing_value_threshold": 0.2,  # 20%以上欠損値がある場合は警告
                    "outlier_threshold": 4.0,  # 4σルール
                    "ohlc_validation": False,
                    "volume_validation": False,
                }
            )

        return rules

    def validate_data_quality(self, data: pd.DataFrame) -> ValidationResult:
        """データ品質の包括的検証"""
        self.logger.info("🔍 データ品質の検証を開始")

        issues = []
        warnings = []
        recommendations = []
        detailed_report = {}

        # 1. 基本構造の検証
        structure_issues = self._validate_data_structure(data)
        issues.extend(structure_issues)

        # 2. データ型の検証
        type_issues = self._validate_data_types(data)
        issues.extend(type_issues)

        # 3. 欠損値の検証
        missing_report = self._validate_missing_values(data)
        detailed_report["missing_values"] = missing_report
        if missing_report["total_missing"] > 0:
            warnings.append(f"欠損値が検出されました: {missing_report['total_missing']}個")

        # 4. 異常値の検証
        outlier_report = self._validate_outliers(data)
        detailed_report["outliers"] = outlier_report
        if outlier_report["total_outliers"] > 0:
            warnings.append(f"異常値が検出されました: {outlier_report['total_outliers']}個")

        # 5. OHLCデータの整合性検証
        if self.validation_rules["ohlc_validation"]:
            ohlc_issues = self._validate_ohlc_consistency(data)
            issues.extend(ohlc_issues)

        # 6. ボリュームデータの検証
        if self.validation_rules["volume_validation"]:
            volume_issues = self._validate_volume_data(data)
            issues.extend(volume_issues)

        # 7. 時系列データの検証
        timeseries_issues = self._validate_timeseries_consistency(data)
        issues.extend(timeseries_issues)

        # 8. データ分布の検証
        distribution_report = self._validate_data_distribution(data)
        detailed_report["distribution"] = distribution_report

        # 9. 推奨事項の生成
        recommendations = self._generate_recommendations(data, detailed_report)

        # 10. 総合スコアの計算
        score = self._calculate_quality_score(data, issues, warnings, detailed_report)

        is_valid = len(issues) == 0 and score >= 0.7

        result = ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
            detailed_report=detailed_report,
        )

        self.logger.info(
            f"✅ データ品質検証完了: スコア={score:.2f}, 問題={len(issues)}個, 警告={len(warnings)}個"
        )

        return result

    def _validate_data_structure(self, data: pd.DataFrame) -> List[str]:
        """データ構造の検証"""
        issues = []

        # 必須カラムの確認
        required_columns = self.validation_rules["required_columns"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            issues.append(f"必須カラムが不足しています: {missing_columns}")

        # データの行数確認
        if len(data) == 0:
            issues.append("データが空です")
        elif len(data) < 10:
            issues.append("データが少なすぎます（10行未満）")

        return issues

    def _validate_data_types(self, data: pd.DataFrame) -> List[str]:
        """データ型の検証"""
        issues = []

        # 数値カラムの型確認
        numeric_columns = self.validation_rules["numeric_columns"]
        for col in numeric_columns:
            if col in data.columns:
                if not pd.api.types.is_numeric_dtype(data[col]):
                    issues.append(f"カラム '{col}' が数値型ではありません")

        # 日付カラムの型確認
        date_column = self.validation_rules["date_column"]
        if date_column in data.columns:
            if not pd.api.types.is_datetime64_any_dtype(data[date_column]):
                issues.append(f"カラム '{date_column}' が日付型ではありません")

        return issues

    def _validate_missing_values(self, data: pd.DataFrame) -> Dict[str, Any]:
        """欠損値の検証"""
        missing_report = {
            "total_missing": 0,
            "missing_by_column": {},
            "missing_percentage": 0.0,
            "critical_missing": [],
        }

        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        missing_report["total_missing"] = missing_cells
        missing_report["missing_percentage"] = (
            missing_cells / total_cells if total_cells > 0 else 0
        )

        # カラム別の欠損値
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            missing_report["missing_by_column"][col] = missing_count

            # 重要なカラムの欠損値チェック
            if col in self.validation_rules["required_columns"] and missing_count > 0:
                missing_report["critical_missing"].append(col)

        return missing_report

    def _validate_outliers(self, data: pd.DataFrame) -> Dict[str, Any]:
        """異常値の検証"""
        outlier_report = {
            "total_outliers": 0,
            "outliers_by_column": {},
            "outlier_percentage": 0.0,
            "critical_outliers": [],
        }

        numeric_columns = [
            col
            for col in self.validation_rules["numeric_columns"]
            if col in data.columns
        ]

        for col in numeric_columns:
            if data[col].dtype in ["int64", "float64"]:
                # Z-score法による異常値検出
                z_scores = np.abs(stats.zscore(data[col].dropna()))
                outliers = z_scores > self.validation_rules["outlier_threshold"]
                outlier_count = outliers.sum()

                outlier_report["outliers_by_column"][col] = outlier_count
                outlier_report["total_outliers"] += outlier_count

                # 重要なカラムの異常値チェック
                if col in ["Close", "Volume"] and outlier_count > 0:
                    outlier_report["critical_outliers"].append(col)

        if outlier_report["total_outliers"] > 0:
            outlier_report["outlier_percentage"] = (
                outlier_report["total_outliers"] / data.size
            )

        return outlier_report

    def _validate_ohlc_consistency(self, data: pd.DataFrame) -> List[str]:
        """OHLCデータの整合性検証"""
        issues = []

        ohlc_columns = ["Open", "High", "Low", "Close"]
        if all(col in data.columns for col in ohlc_columns):
            # High >= Low の確認
            invalid_high_low = data["High"] < data["Low"]
            if invalid_high_low.any():
                issues.append(f"High < Low の行が {invalid_high_low.sum()} 行あります")

            # High >= Open, Close の確認
            invalid_high_open = data["High"] < data["Open"]
            if invalid_high_open.any():
                issues.append(f"High < Open の行が {invalid_high_open.sum()} 行あります")

            invalid_high_close = data["High"] < data["Close"]
            if invalid_high_close.any():
                issues.append(f"High < Close の行が {invalid_high_close.sum()} 行あります")

            # Low <= Open, Close の確認
            invalid_low_open = data["Low"] > data["Open"]
            if invalid_low_open.any():
                issues.append(f"Low > Open の行が {invalid_low_open.sum()} 行あります")

            invalid_low_close = data["Low"] > data["Close"]
            if invalid_low_close.any():
                issues.append(f"Low > Close の行が {invalid_low_close.sum()} 行あります")

        return issues

    def _validate_volume_data(self, data: pd.DataFrame) -> List[str]:
        """ボリュームデータの検証"""
        issues = []

        if "Volume" in data.columns:
            # 負のボリュームの確認
            negative_volume = data["Volume"] < 0
            if negative_volume.any():
                issues.append(f"負のボリュームが {negative_volume.sum()} 行あります")

            # ゼロボリュームの確認
            zero_volume = data["Volume"] == 0
            if zero_volume.any():
                issues.append(f"ゼロボリュームが {zero_volume.sum()} 行あります")

            # 異常に大きなボリュームの確認
            volume_mean = data["Volume"].mean()
            volume_std = data["Volume"].std()
            if volume_std > 0:
                extreme_volume = data["Volume"] > volume_mean + 5 * volume_std
                if extreme_volume.any():
                    issues.append(f"異常に大きなボリュームが {extreme_volume.sum()} 行あります")

        return issues

    def _validate_timeseries_consistency(self, data: pd.DataFrame) -> List[str]:
        """時系列データの整合性検証"""
        issues = []

        date_column = self.validation_rules["date_column"]
        if date_column in data.columns:
            # 日付の重複確認
            duplicate_dates = data[date_column].duplicated()
            if duplicate_dates.any():
                issues.append(f"重複した日付が {duplicate_dates.sum()} 行あります")

            # 日付の順序確認
            if not data[date_column].is_monotonic_increasing:
                issues.append("日付が時系列順になっていません")

            # 日付の間隔確認
            if len(data) > 1:
                date_diffs = data[date_column].diff().dropna()
                if not date_diffs.empty:
                    # 異常に大きな間隔の確認
                    max_expected_interval = pd.Timedelta(days=7)  # 1週間
                    large_gaps = date_diffs > max_expected_interval
                    if large_gaps.any():
                        issues.append(f"異常に大きな日付間隔が {large_gaps.sum()} 箇所あります")

        return issues

    def _validate_data_distribution(self, data: pd.DataFrame) -> Dict[str, Any]:
        """データ分布の検証"""
        distribution_report = {
            "skewness": {},
            "kurtosis": {},
            "correlation": {},
            "stationarity": {},
        }

        numeric_columns = [
            col
            for col in self.validation_rules["numeric_columns"]
            if col in data.columns
        ]

        for col in numeric_columns:
            if data[col].dtype in ["int64", "float64"] and not data[col].isna().all():
                # 歪度の計算
                distribution_report["skewness"][col] = data[col].skew()

                # 尖度の計算
                distribution_report["kurtosis"][col] = data[col].kurtosis()

        # 相関の計算
        if len(numeric_columns) > 1:
            correlation_matrix = data[numeric_columns].corr()
            distribution_report["correlation"] = correlation_matrix.to_dict()

        return distribution_report

    def _generate_recommendations(
        self, data: pd.DataFrame, detailed_report: Dict[str, Any]
    ) -> List[str]:
        """推奨事項の生成"""
        recommendations = []

        # 欠損値の推奨事項
        missing_report = detailed_report.get("missing_values", {})
        if missing_report.get("missing_percentage", 0) > 0.05:
            recommendations.append("欠損値の処理を検討してください（前値補完、線形補完など）")

        # 異常値の推奨事項
        outlier_report = detailed_report.get("outliers", {})
        if outlier_report.get("total_outliers", 0) > 0:
            recommendations.append("異常値の処理を検討してください（除外、修正、変換など）")

        # データ分布の推奨事項
        distribution_report = detailed_report.get("distribution", {})
        for col, skewness in distribution_report.get("skewness", {}).items():
            if abs(skewness) > 2:
                recommendations.append(f"カラム '{col}' の分布が偏っています（歪度: {skewness:.2f}）")

        # データ量の推奨事項
        if len(data) < 100:
            recommendations.append("データ量が少ないため、より多くのデータの取得を検討してください")

        return recommendations

    def _calculate_quality_score(
        self,
        data: pd.DataFrame,
        issues: List[str],
        warnings: List[str],
        detailed_report: Dict[str, Any],
    ) -> float:
        """データ品質スコアの計算"""
        base_score = 1.0

        # 問題による減点
        issue_penalty = len(issues) * 0.1
        warning_penalty = len(warnings) * 0.05

        # 欠損値による減点
        missing_report = detailed_report.get("missing_values", {})
        missing_penalty = missing_report.get("missing_percentage", 0) * 0.3

        # 異常値による減点
        outlier_report = detailed_report.get("outliers", {})
        outlier_penalty = outlier_report.get("outlier_percentage", 0) * 0.2

        # 最終スコアの計算
        final_score = max(
            0.0,
            base_score
            - issue_penalty
            - warning_penalty
            - missing_penalty
            - outlier_penalty,
        )

        return final_score

    def detect_anomalies(
        self, data: pd.DataFrame, method: str = "isolation_forest"
    ) -> Dict[str, Any]:
        """異常値検出の強化"""
        self.logger.info(f"🔍 異常値検出を開始: 方法={method}")

        numeric_columns = [
            col
            for col in self.validation_rules["numeric_columns"]
            if col in data.columns
        ]

        if not numeric_columns:
            return {"anomalies": [], "anomaly_scores": [], "method": method}

        # 数値データの準備
        numeric_data = data[numeric_columns].dropna()

        if len(numeric_data) == 0:
            return {"anomalies": [], "anomaly_scores": [], "method": method}

        # データの標準化
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_data)

        anomalies = []
        anomaly_scores = []

        if method == "isolation_forest":
            # Isolation Forest法
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(scaled_data)
            anomaly_scores = iso_forest.decision_function(scaled_data)

            anomalies = numeric_data[anomaly_labels == -1].index.tolist()

        elif method == "z_score":
            # Z-score法
            z_scores = np.abs(stats.zscore(scaled_data, axis=0))
            max_z_scores = np.max(z_scores, axis=1)
            anomalies = numeric_data[
                max_z_scores > self.validation_rules["outlier_threshold"]
            ].index.tolist()
            anomaly_scores = max_z_scores.tolist()

        result = {
            "anomalies": anomalies,
            "anomaly_scores": anomaly_scores,
            "method": method,
            "total_anomalies": len(anomalies),
            "anomaly_percentage": (
                len(anomalies) / len(numeric_data) if len(numeric_data) > 0 else 0
            ),
        }

        self.logger.info(f"✅ 異常値検出完了: {len(anomalies)}個の異常値を検出")

        return result

    def suggest_data_improvements(
        self, data: pd.DataFrame, validation_result: ValidationResult
    ) -> List[str]:
        """データ改善の提案"""
        improvements = []

        # 欠損値の改善提案
        missing_report = validation_result.detailed_report.get("missing_values", {})
        if missing_report.get("total_missing", 0) > 0:
            improvements.append("欠損値の処理: 前値補完、線形補完、または機械学習による補完を検討")

        # 異常値の改善提案
        outlier_report = validation_result.detailed_report.get("outliers", {})
        if outlier_report.get("total_outliers", 0) > 0:
            improvements.append("異常値の処理: 除外、修正、またはロバスト統計量の使用を検討")

        # データ分布の改善提案
        distribution_report = validation_result.detailed_report.get("distribution", {})
        for col, skewness in distribution_report.get("skewness", {}).items():
            if abs(skewness) > 1:
                improvements.append(f"カラム '{col}' の分布改善: 対数変換、Box-Cox変換、または正規化を検討")

        # データ量の改善提案
        if len(data) < 100:
            improvements.append("データ量の増加: より多くの履歴データの取得を検討")

        return improvements

    def generate_quality_report(
        self, data: pd.DataFrame, validation_result: ValidationResult
    ) -> str:
        """品質レポートの生成"""
        report = []
        report.append("=" * 50)
        report.append("データ品質レポート")
        report.append("=" * 50)

        # 基本情報
        report.append(f"データサイズ: {len(data)} 行 × {len(data.columns)} 列")
        report.append(f"品質スコア: {validation_result.score:.2f}")
        report.append(f"検証結果: {'合格' if validation_result.is_valid else '不合格'}")

        # 問題の詳細
        if validation_result.issues:
            report.append("\n【問題】")
            for i, issue in enumerate(validation_result.issues, 1):
                report.append(f"{i}. {issue}")

        # 警告の詳細
        if validation_result.warnings:
            report.append("\n【警告】")
            for i, warning in enumerate(validation_result.warnings, 1):
                report.append(f"{i}. {warning}")

        # 推奨事項
        if validation_result.recommendations:
            report.append("\n【推奨事項】")
            for i, recommendation in enumerate(validation_result.recommendations, 1):
                report.append(f"{i}. {recommendation}")

        # 詳細レポート
        report.append("\n【詳細レポート】")
        for key, value in validation_result.detailed_report.items():
            report.append(f"{key}: {value}")

        return "\n".join(report)


def validate_stock_data(
    data: pd.DataFrame, validation_level: ValidationLevel = ValidationLevel.STANDARD
) -> ValidationResult:
    """株価データの検証（便利関数）"""
    validator = EnhancedDataValidator(validation_level)
    return validator.validate_data_quality(data)


def detect_stock_anomalies(
    data: pd.DataFrame, method: str = "isolation_forest"
) -> Dict[str, Any]:
    """株価データの異常値検出（便利関数）"""
    validator = EnhancedDataValidator()
    return validator.detect_anomalies(data, method)


if __name__ == "__main__":
    # テスト用のサンプルデータ
    sample_data = pd.DataFrame(
        {
            "Date": pd.date_range("2023-01-01", periods=100, freq="D"),
            "Open": np.random.uniform(50, 200, 100),
            "High": np.random.uniform(50, 200, 100),
            "Low": np.random.uniform(50, 200, 100),
            "Close": np.random.uniform(50, 200, 100),
            "Volume": np.random.randint(1000, 10000, 100),
        }
    )

    # 検証の実行
    validator = EnhancedDataValidator(ValidationLevel.STANDARD)
    result = validator.validate_data_quality(sample_data)

    print(f"検証結果: {result.is_valid}")
    print(f"品質スコア: {result.score:.2f}")
    print(f"問題数: {len(result.issues)}")
    print(f"警告数: {len(result.warnings)}")
