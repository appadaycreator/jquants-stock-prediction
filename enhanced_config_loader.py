"""
強化された設定ローダー
複数の設定ファイルを統合管理し、環境変数との連携を提供
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """環境の種類"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ConfigValidation:
    """設定検証結果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class EnhancedConfigLoader:
    """強化された設定ローダー"""
    
    def __init__(self, config_dir: str = "config", environment: str = None):
        """
        初期化
        
        Args:
            config_dir: 設定ファイルのディレクトリ
            environment: 環境名（Noneの場合は環境変数から取得）
        """
        self.config_dir = Path(config_dir)
        self.environment = environment or os.getenv("ENVIRONMENT", "production")
        self.logger = logging.getLogger(__name__)
        
        # 設定ファイルのパス
        self.config_files = {
            "core": self.config_dir / "core.yaml",
            "api": self.config_dir / "api.yaml",
            "data": self.config_dir / "data.yaml",
            "models": self.config_dir / "models.yaml"
        }
        
        # 統合された設定
        self._config = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """すべての設定ファイルを読み込み"""
        try:
            for name, file_path in self.config_files.items():
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f) or {}
                        self._config[name] = config_data
                        self.logger.info(f"設定ファイル {name} を読み込みました")
                else:
                    self.logger.warning(f"設定ファイル {file_path} が見つかりません")
                    self._config[name] = {}
            
            # 環境変数でオーバーライド
            self._apply_environment_overrides()
            
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
            raise
    
    def _apply_environment_overrides(self):
        """環境変数で設定をオーバーライド"""
        # 環境変数のマッピング
        env_mappings = {
            "JQUANTS_EMAIL": ["jquants", "auth", "email"],
            "JQUANTS_PASSWORD": ["jquants", "auth", "password"],
            "LOG_LEVEL": ["logging", "level"],
            "DEBUG": ["system", "debug"],
            "MAX_WORKERS": ["performance", "max_workers"],
            "MEMORY_LIMIT": ["performance", "memory_limit"],
            "API_TIMEOUT": ["jquants", "timeout"],
            "MAX_RETRIES": ["jquants", "max_retries"],
            "RATE_LIMIT": ["jquants", "rate_limit"],
            "TARGET_DATE": ["data_fetch", "target_date"],
            "OUTPUT_FILE": ["data_fetch", "output_file"],
            "TEST_SIZE": ["prediction", "test_size"],
            "RANDOM_STATE": ["prediction", "random_state"],
            "PRIMARY_MODEL": ["prediction", "model_selection", "primary_model"],
            "COMPARE_MODELS": ["prediction", "model_selection", "compare_models"]
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(self._config, config_path, self._convert_env_value(env_value))
                self.logger.debug(f"環境変数 {env_var} で設定をオーバーライドしました")
    
    def _set_nested_value(self, config: Dict, path: List[str], value: Any):
        """ネストされた辞書に値を設定"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _convert_env_value(self, value: str) -> Any:
        """環境変数の値を適切な型に変換"""
        # ブール値
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 数値
        if value.isdigit():
            return int(value)
        
        # 浮動小数点数
        try:
            return float(value)
        except ValueError:
            pass
        
        # 文字列
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得
        
        Args:
            key: 設定キー（例: "system.name" または "jquants.base_url"）
            default: デフォルト値
            
        Returns:
            設定値
        """
        try:
            keys = key.split('.')
            
            # セクション名が指定されている場合（例: "jquants.base_url"）
            if len(keys) > 1 and keys[0] in self._config:
                section = keys[0]
                remaining_keys = keys[1:]
                value = self._config[section]
                
                for k in remaining_keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                
                return value
            
            # セクション名が指定されていない場合、すべてのセクションから検索
            for section_name, section_config in self._config.items():
                if isinstance(section_config, dict):
                    value = section_config
                    for k in keys:
                        if isinstance(value, dict) and k in value:
                            value = value[k]
                        else:
                            break
                    else:
                        return value
            
            return default
        except Exception as e:
            self.logger.warning(f"設定キー {key} の取得に失敗しました: {e}")
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        設定セクションを取得
        
        Args:
            section: セクション名（core, api, data, models）
            
        Returns:
            設定セクション
        """
        return self._config.get(section, {})
    
    def get_jquants_config(self) -> Dict[str, Any]:
        """J-Quants API設定を取得"""
        return self.get_section("api").get("jquants", {})
    
    def get_data_config(self) -> Dict[str, Any]:
        """データ処理設定を取得"""
        return self.get_section("data")
    
    def get_model_config(self) -> Dict[str, Any]:
        """モデル設定を取得"""
        return self.get_section("models")
    
    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定を取得"""
        return self.get_section("core").get("logging", {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """パフォーマンス設定を取得"""
        return self.get_section("core").get("performance", {})
    
    def validate_config(self) -> ConfigValidation:
        """設定の検証"""
        errors = []
        warnings = []
        
        # 必須設定の検証
        required_settings = [
            ("api.jquants.base_url", "J-Quants APIのベースURL"),
            ("api.jquants.timeout", "APIタイムアウト設定"),
            ("models.prediction.target", "予測の目的変数"),
            ("models.prediction.features", "予測に使用する特徴量")
        ]
        
        for setting, description in required_settings:
            if self.get(setting) is None:
                errors.append(f"必須設定が不足しています: {setting} ({description})")
        
        # 環境変数の検証
        if not os.getenv("JQUANTS_EMAIL"):
            warnings.append("JQUANTS_EMAIL環境変数が設定されていません")
        
        if not os.getenv("JQUANTS_PASSWORD"):
            warnings.append("JQUANTS_PASSWORD環境変数が設定されていません")
        
        # 数値設定の検証
        numeric_settings = [
            ("api.jquants.timeout", 1, 300),
            ("api.jquants.max_retries", 1, 10),
            ("models.prediction.test_size", 0.0, 1.0),
            ("core.performance.max_workers", 1, 16)
        ]
        
        for setting, min_val, max_val in numeric_settings:
            value = self.get(setting)
            if value is not None:
                if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
                    errors.append(f"設定値が範囲外です: {setting} = {value} (範囲: {min_val}-{max_val})")
        
        # ファイルパスの検証
        file_settings = [
            ("data.data_fetch.output_file", "データ出力ファイル"),
            ("data.preprocessing.input_file", "前処理入力ファイル"),
            ("data.preprocessing.output_file", "前処理出力ファイル")
        ]
        
        for setting, description in file_settings:
            file_path = self.get(setting)
            if file_path and not isinstance(file_path, str):
                errors.append(f"ファイルパスが無効です: {setting} = {file_path}")
        
        is_valid = len(errors) == 0
        
        return ConfigValidation(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def get_environment_info(self) -> Dict[str, Any]:
        """環境情報を取得"""
        return {
            "environment": self.environment,
            "config_dir": str(self.config_dir),
            "config_files": {name: str(path) for name, path in self.config_files.items()},
            "loaded_sections": list(self._config.keys())
        }
    
    def reload_config(self):
        """設定を再読み込み"""
        self._config = {}
        self._load_all_configs()
        self.logger.info("設定を再読み込みしました")
    
    def export_config(self, output_file: str = "exported_config.yaml"):
        """現在の設定をYAMLファイルにエクスポート"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"設定を {output_file} にエクスポートしました")
        except Exception as e:
            self.logger.error(f"設定のエクスポートに失敗しました: {e}")
            raise
    
    def get_all_config(self) -> Dict[str, Any]:
        """すべての設定を取得"""
        return self._config.copy()
    
    def update_config(self, section: str, key: str, value: Any):
        """設定を更新"""
        if section not in self._config:
            self._config[section] = {}
        
        keys = key.split('.')
        current = self._config[section]
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self.logger.info(f"設定を更新しました: {section}.{key} = {value}")
    
    def get_config_with_section(self, section: str, key: str, default: Any = None) -> Any:
        """セクション指定で設定値を取得"""
        section_config = self.get_section(section)
        if not section_config:
            return default
        
        keys = key.split('.')
        value = section_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value


# グローバル設定インスタンス
_config_loader = None


def get_config_loader() -> EnhancedConfigLoader:
    """グローバル設定ローダーを取得"""
    global _config_loader
    if _config_loader is None:
        _config_loader = EnhancedConfigLoader()
    return _config_loader


def get_config(key: str, default: Any = None) -> Any:
    """設定値を取得（簡易版）"""
    return get_config_loader().get(key, default)


def validate_environment():
    """環境設定の検証"""
    config_loader = get_config_loader()
    validation = config_loader.validate_config()
    
    if not validation.is_valid:
        raise ValueError(f"設定検証に失敗しました: {validation.errors}")
    
    if validation.warnings:
        for warning in validation.warnings:
            print(f"警告: {warning}")
    
    return True
