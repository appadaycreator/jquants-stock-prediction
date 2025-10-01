"""
強化された設定ローダーモジュール
複数の設定ファイルを管理し、環境変数でのオーバーライドに対応
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

from config_validator import ConfigValidator, ValidationResult


class Environment(Enum):
    """環境タイプ"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ValidationSummary:
    """検証結果のサマリー"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]


class EnhancedConfigLoader:
    """強化された設定ローダークラス"""

    def __init__(self, config_dir: str = "config", environment: str = "development"):
        """
        初期化

        Args:
            config_dir: 設定ファイルのディレクトリ
            environment: 環境名
        """
        self.config_dir = Path(config_dir)
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        self._config: Dict[str, Any] = {}

        # ログ設定
        self._setup_logging()

        # 設定ファイルの読み込み
        self._load_config_files()

    def _setup_logging(self):
        """ログ設定のセットアップ"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_config_files(self):
        """設定ファイルの読み込み"""
        config_files = ["core.yaml", "api.yaml", "data.yaml", "models.yaml"]

        for config_file in config_files:
            file_path = self.config_dir / config_file
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f) or {}

                    # 環境変数でのオーバーライド
                    config_data = self._apply_environment_overrides(config_data)

                    # 設定名（ファイル名から拡張子を除く）
                    config_name = config_file.replace(".yaml", "")
                    self._config[config_name] = config_data

                    self.logger.info(f"設定ファイルを読み込みました: {file_path}")
                except Exception as e:
                    self.logger.error(
                        f"設定ファイルの読み込みに失敗しました: {file_path} - {e}"
                    )
            else:
                self.logger.warning(f"設定ファイルが見つかりません: {file_path}")

    def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """環境変数での設定オーバーライド"""

        def override_nested_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
            result = {}
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    result[key] = override_nested_dict(value, full_key)
                else:
                    # 環境変数名のマッピング
                    env_key = full_key.upper().replace(".", "_")

                    # 特別なマッピング
                    if full_key == "logging.level":
                        env_key = "LOG_LEVEL"
                    elif full_key == "system.debug":
                        env_key = "DEBUG"

                    env_value = os.getenv(env_key)
                    if env_value is not None:
                        result[key] = self._convert_env_value(env_value)
                    else:
                        result[key] = value
            return result

        return override_nested_dict(config)

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """環境変数値の型変換"""
        # ブール値の変換
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # 数値の変換
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # 文字列として返す
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値の取得（ドット記法対応）

        Args:
            key: 設定キー（例: "system.name" または "core.system.name"）
            default: デフォルト値

        Returns:
            設定値
        """
        keys = key.split(".")

        # セクション名が指定されていない場合、すべてのセクションを検索
        if len(keys) == 1:
            # 単一キーの場合、すべてのセクションから検索
            for section_name, section_data in self._config.items():
                if keys[0] in section_data:
                    return section_data[keys[0]]
            return default

        # セクション名が指定されている場合
        if len(keys) >= 2:
            section_name = keys[0]
            if section_name in self._config:
                value = self._config[section_name]
                try:
                    for k in keys[1:]:
                        value = value[k]
                    return value
                except (KeyError, TypeError):
                    pass

        # セクション名が指定されていない場合、すべてのセクションから検索
        for section_name, section_data in self._config.items():
            try:
                value = section_data
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                continue

        return default

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        設定セクションの取得

        Args:
            section: セクション名

        Returns:
            設定セクションの辞書
        """
        return self._config.get(section, {})

    def update_config(self, section: str, key: str, value: Any):
        """
        設定値の更新

        Args:
            section: セクション名
            key: キー名（ドット記法対応）
            value: 新しい値
        """
        if section not in self._config:
            self._config[section] = {}

        keys = key.split(".")
        current = self._config[section]

        # ネストした辞書の作成
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.logger.info(f"設定を更新しました: {section}.{key} = {value}")

    def get_all_config(self) -> Dict[str, Any]:
        """全設定の取得"""
        return self._config.copy()

    def reload_config(self):
        """設定の再読み込み"""
        self._config.clear()
        self._load_config_files()
        self.logger.info("設定を再読み込みしました")

    def export_config(self, output_file: str):
        """
        設定のエクスポート

        Args:
            output_file: 出力ファイルパス
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"設定をエクスポートしました: {output_file}")
        except Exception as e:
            self.logger.error(f"設定のエクスポートに失敗しました: {e}")
            raise

    def validate_config(self) -> ValidationSummary:
        """
        設定の検証

        Returns:
            検証結果のサマリー
        """
        validator = ConfigValidator(str(self.config_dir))
        results = validator.validate_all()

        errors = []
        warnings = []
        info = []

        for result in results:
            if result.level.value == "error":
                errors.append(result.message)
            elif result.level.value == "warning":
                warnings.append(result.message)
            else:
                info.append(result.message)

        return ValidationSummary(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings, info=info
        )

    def get_environment_info(self) -> Dict[str, Any]:
        """環境情報の取得"""
        return {
            "environment": self.environment,
            "config_dir": str(self.config_dir),
            "config_files": list(self._config.keys()),
            "loaded_sections": list(self._config.keys()),
        }

    def __getitem__(self, key: str) -> Any:
        """辞書風のアクセス"""
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        """辞書風の設定"""
        if "." in key:
            section, sub_key = key.split(".", 1)
            self.update_config(section, sub_key, value)
        else:
            self._config[key] = value

    def __contains__(self, key: str) -> bool:
        """キーの存在確認"""
        try:
            self.get(key)
            return True
        except (KeyError, TypeError):
            return False


# グローバル設定ローダーインスタンス
_config_loader: Optional[EnhancedConfigLoader] = None


def get_config_loader() -> EnhancedConfigLoader:
    """グローバル設定ローダーの取得"""
    global _config_loader
    if _config_loader is None:
        _config_loader = EnhancedConfigLoader()
    return _config_loader


def get_config(key: str, default: Any = None) -> Any:
    """
    設定値の取得（グローバル関数）

    Args:
        key: 設定キー
        default: デフォルト値

    Returns:
        設定値
    """
    loader = get_config_loader()
    return loader.get(key, default)


def validate_environment() -> bool:
    """
    環境の検証（グローバル関数）

    Returns:
        検証結果
    """
    loader = get_config_loader()
    validation = loader.validate_config()
    return validation.is_valid


def reload_config():
    """設定の再読み込み（グローバル関数）"""
    loader = get_config_loader()
    loader.reload_config()


def get_environment_info() -> Dict[str, Any]:
    """環境情報の取得（グローバル関数）"""
    loader = get_config_loader()
    return loader.get_environment_info()
