"""
設定検証モジュール
設定ファイルと環境変数の整合性を検証
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """検証レベル"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """検証結果"""

    level: ValidationLevel
    message: str
    section: str
    key: str
    current_value: Any
    expected_value: Any = None
    suggestion: str = ""


class ConfigValidator:
    """設定検証クラス"""

    def __init__(self, config_dir: str = "config"):
        """
        初期化

        Args:
            config_dir: 設定ファイルのディレクトリ
        """
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(__name__)
        self.results: List[ValidationResult] = []

    def validate_all(self) -> List[ValidationResult]:
        """すべての設定を検証"""
        self.results = []

        # 設定ファイルの存在確認
        self._validate_config_files()

        # 各設定ファイルの検証
        self._validate_core_config()
        self._validate_api_config()
        self._validate_data_config()
        self._validate_models_config()

        # 環境変数の検証
        self._validate_environment_variables()

        # 設定間の整合性検証
        self._validate_cross_config_consistency()

        return self.results

    def _validate_config_files(self):
        """設定ファイルの存在確認"""
        required_files = ["core.yaml", "api.yaml", "data.yaml", "models.yaml"]

        for file_name in required_files:
            file_path = self.config_dir / file_name
            if not file_path.exists():
                self.results.append(
                    ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"設定ファイルが見つかりません: {file_name}",
                        section="system",
                        key="config_files",
                        current_value=None,
                        suggestion=f"設定ファイル {file_name} を作成してください",
                    )
                )

    def _validate_core_config(self):
        """コア設定の検証"""
        try:
            with open(self.config_dir / "core.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"コア設定ファイルの読み込みに失敗: {e}",
                    section="core",
                    key="file_loading",
                    current_value=None,
                )
            )
            return

        # システム設定の検証
        system_config = config.get("system", {})
        if not system_config.get("name"):
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="システム名が設定されていません",
                    section="core",
                    key="system.name",
                    current_value=system_config.get("name"),
                    suggestion="システム名を設定してください",
                )
            )

        # ログ設定の検証
        logging_config = config.get("logging", {})
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        log_level = logging_config.get("level", "INFO")
        if log_level not in valid_levels:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"無効なログレベル: {log_level}",
                    section="core",
                    key="logging.level",
                    current_value=log_level,
                    expected_value=valid_levels,
                    suggestion=f"有効なログレベルを設定してください: {", ".join(valid_levels)}",
                )
            )

        # パフォーマンス設定の検証
        performance_config = config.get("performance", {})
        max_workers = performance_config.get("max_workers", 4)
        if not isinstance(max_workers, int) or max_workers < 1 or max_workers > 16:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"max_workersの値が不適切: {max_workers}",
                    section="core",
                    key="performance.max_workers",
                    current_value=max_workers,
                    suggestion="1-16の範囲で設定してください",
                )
            )

    def _validate_api_config(self):
        """API設定の検証"""
        try:
            with open(self.config_dir / "api.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"API設定ファイルの読み込みに失敗: {e}",
                    section="api",
                    key="file_loading",
                    current_value=None,
                )
            )
            return

        jquants_config = config.get("jquants", {})

        # ベースURLの検証
        base_url = jquants_config.get("base_url")
        if not base_url or not base_url.startswith("https://"):
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="J-Quants APIのベースURLが無効です",
                    section="api",
                    key="jquants.base_url",
                    current_value=base_url,
                    suggestion="https://で始まる有効なURLを設定してください",
                )
            )

        # タイムアウト設定の検証
        timeout = jquants_config.get("timeout", 30)
        if not isinstance(timeout, (int, float)) or timeout < 1 or timeout > 300:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"APIタイムアウトの値が不適切: {timeout}",
                    section="api",
                    key="jquants.timeout",
                    current_value=timeout,
                    suggestion="1-300秒の範囲で設定してください",
                )
            )

        # リトライ設定の検証
        max_retries = jquants_config.get("max_retries", 3)
        if not isinstance(max_retries, int) or max_retries < 0 or max_retries > 10:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"最大リトライ回数の値が不適切: {max_retries}",
                    section="api",
                    key="jquants.max_retries",
                    current_value=max_retries,
                    suggestion="0-10の範囲で設定してください",
                )
            )

    def _validate_data_config(self):
        """データ設定の検証"""
        try:
            with open(self.config_dir / "data.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"データ設定ファイルの読み込みに失敗: {e}",
                    section="data",
                    key="file_loading",
                    current_value=None,
                )
            )
            return

        # データ取得設定の検証
        data_fetch_config = config.get("data_fetch", {})
        target_date = data_fetch_config.get("target_date")
        if target_date and not self._is_valid_date_format(target_date):
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"無効な日付形式: {target_date}",
                    section="data",
                    key="data_fetch.target_date",
                    current_value=target_date,
                    suggestion="YYYYMMDD形式で設定してください",
                )
            )

        # 前処理設定の検証
        preprocessing_config = config.get("preprocessing", {})
        required_columns = preprocessing_config.get("columns", [])
        if not required_columns:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="必須カラムが設定されていません",
                    section="data",
                    key="preprocessing.columns",
                    current_value=required_columns,
                    suggestion="必要なカラムを設定してください",
                )
            )

        # 技術指標設定の検証
        technical_indicators = preprocessing_config.get("technical_indicators", {})
        sma_windows = technical_indicators.get("sma_windows", [])
        if sma_windows and not all(isinstance(w, int) and w > 0 for w in sma_windows):
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="SMAウィンドウサイズに無効な値が含まれています",
                    section="data",
                    key="preprocessing.technical_indicators.sma_windows",
                    current_value=sma_windows,
                    suggestion="正の整数を設定してください",
                )
            )

    def _validate_models_config(self):
        """モデル設定の検証"""
        try:
            with open(self.config_dir / "models.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"モデル設定ファイルの読み込みに失敗: {e}",
                    section="models",
                    key="file_loading",
                    current_value=None,
                )
            )
            return

        prediction_config = config.get("prediction", {})

        # 特徴量の検証
        features = prediction_config.get("features", [])
        if not features:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="予測に使用する特徴量が設定されていません",
                    section="models",
                    key="prediction.features",
                    current_value=features,
                    suggestion="予測に使用する特徴量を設定してください",
                )
            )

        # 目的変数の検証
        target = prediction_config.get("target")
        if not target:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="目的変数が設定されていません",
                    section="models",
                    key="prediction.target",
                    current_value=target,
                    suggestion="予測の目的変数を設定してください",
                )
            )

        # テストサイズの検証
        test_size = prediction_config.get("test_size", 0.2)
        if not isinstance(test_size, (int, float)) or test_size <= 0 or test_size >= 1:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"テストサイズの値が無効: {test_size}",
                    section="models",
                    key="prediction.test_size",
                    current_value=test_size,
                    suggestion="0より大きく1より小さい値を設定してください",
                )
            )

        # モデル設定の検証
        models_config = prediction_config.get("models", {})
        valid_model_types = [
            "random_forest",
            "xgboost",
            "linear_regression",
            "ridge",
            "lasso",
        ]
        for model_name, model_config in models_config.items():
            model_type = model_config.get("type")
            if model_type not in valid_model_types:
                self.results.append(
                    ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"無効なモデルタイプ: {model_type}",
                        section="models",
                        key=f"prediction.models.{model_name}.type",
                        current_value=model_type,
                        expected_value=valid_model_types,
                        suggestion=f"有効なモデルタイプを設定してください: {", ".join(valid_model_types)}",
                    )
                )

    def _validate_environment_variables(self):
        """環境変数の検証"""
        required_env_vars = ["JQUANTS_EMAIL", "JQUANTS_PASSWORD"]

        for env_var in required_env_vars:
            if not os.getenv(env_var):
                self.results.append(
                    ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"必須の環境変数が設定されていません: {env_var}",
                        section="environment",
                        key=env_var,
                        current_value=None,
                        suggestion=f"環境変数 {env_var} を設定してください",
                    )
                )

        # オプション環境変数の検証
        optional_env_vars = {
            "API_TIMEOUT": (1, 300),
            "MAX_RETRIES": (0, 10),
            "TEST_SIZE": (0.0, 1.0),
            "MAX_WORKERS": (1, 16),
        }

        for env_var, (min_val, max_val) in optional_env_vars.items():
            value = os.getenv(env_var)
            if value:
                try:
                    num_value = float(value)
                    if not (min_val <= num_value <= max_val):
                        self.results.append(
                            ValidationResult(
                                level=ValidationLevel.WARNING,
                                message=f"環境変数 {env_var} の値が範囲外: {value}",
                                section="environment",
                                key=env_var,
                                current_value=value,
                                suggestion=f"{min_val}-{max_val}の範囲で設定してください",
                            )
                        )
                except ValueError:
                    self.results.append(
                        ValidationResult(
                            level=ValidationLevel.WARNING,
                            message=f"環境変数 {env_var} の値が数値ではありません: {value}",
                            section="environment",
                            key=env_var,
                            current_value=value,
                            suggestion="数値を設定してください",
                        )
                    )

    def _validate_cross_config_consistency(self):
        """設定間の整合性検証"""
        # データファイルパスの整合性
        try:
            with open(self.config_dir / "data.yaml", "r", encoding="utf-8") as f:
                data_config = yaml.safe_load(f) or {}
            with open(self.config_dir / "models.yaml", "r", encoding="utf-8") as f:
                models_config = yaml.safe_load(f) or {}
        except Exception:
            return

        data_output = data_config.get("data_fetch", {}).get("output_file")
        preprocessing_input = data_config.get("preprocessing", {}).get("input_file")
        preprocessing_output = data_config.get("preprocessing", {}).get("output_file")
        model_input = models_config.get("prediction", {}).get("input_file")

        if data_output and preprocessing_input and data_output != preprocessing_input:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="データファイルパスの不整合",
                    section="consistency",
                    key="file_paths",
                    current_value=f"data_fetch.output_file={data_output}, preprocessing.input_file={preprocessing_input}",
                    suggestion="データフローの一貫性を保つため、ファイルパスを統一してください",
                )
            )

        if preprocessing_output and model_input and preprocessing_output != model_input:
            self.results.append(
                ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="前処理出力とモデル入力ファイルの不整合",
                    section="consistency",
                    key="file_paths",
                    current_value=f"preprocessing.output_file={preprocessing_output}, prediction.input_file={model_input}",
                    suggestion="データフローの一貫性を保つため、ファイルパスを統一してください",
                )
            )

    def _is_valid_date_format(self, date_str: str) -> bool:
        """日付形式の検証"""
        if not isinstance(date_str, str) or len(date_str) != 8:
            return False

        try:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])

            if not (1 <= month <= 12):
                return False

            if not (1 <= day <= 31):
                return False

            return True
        except ValueError:
            return False

    def get_summary(self) -> Dict[str, Any]:
        """検証結果のサマリーを取得"""
        error_count = sum(1 for r in self.results if r.level == ValidationLevel.ERROR)
        warning_count = sum(
            1 for r in self.results if r.level == ValidationLevel.WARNING
        )
        info_count = sum(1 for r in self.results if r.level == ValidationLevel.INFO)

        return {
            "total_issues": len(self.results),
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "is_valid": error_count == 0,
        }

    def export_report(self, output_file: str = "config_validation_report.yaml"):
        """検証レポートをエクスポート"""
        report = {
            "summary": self.get_summary(),
            "results": [
                {
                    "level": r.level.value,
                    "message": r.message,
                    "section": r.section,
                    "key": r.key,
                    "current_value": r.current_value,
                    "expected_value": r.expected_value,
                    "suggestion": r.suggestion,
                }
                for r in self.results
            ],
        }

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(report, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"検証レポートを {output_file} にエクスポートしました")
        except Exception as e:
            self.logger.error(f"レポートのエクスポートに失敗しました: {e}")
            raise
