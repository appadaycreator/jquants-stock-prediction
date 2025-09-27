#!/usr/bin/env python3
"""
統合設定ローダー
単一の設定ファイルから全設定を管理する統合システム
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class UnifiedConfigLoader:
    """統合設定ローダー - 単一責任原則に基づく設定管理"""

    def __init__(self, config_file: str = "config_unified.yaml"):
        """初期化"""
        self.config_file = config_file
        self.config = {}
        self.logger = logging.getLogger(__name__)

        # 設定ファイルの読み込み
        self._load_config()

    def _load_config(self) -> None:
        """設定ファイルの読み込み"""
        try:
            if not os.path.exists(self.config_file):
                self.logger.warning(f"設定ファイルが見つかりません: {self.config_file}")
                self.logger.info("デフォルト設定を使用します")
                self._create_default_config()
                return

            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}

            self.logger.info(f"✅ 設定ファイル読み込み完了: {self.config_file}")

            # 環境別設定の適用
            self._apply_environment_config()

        except Exception as e:
            self.logger.error(f"❌ 設定ファイル読み込みエラー: {e}")
            self._create_default_config()

    def _create_default_config(self) -> None:
        """デフォルト設定の作成"""
        self.config = {
            "system": {
                "name": "J-Quants株価予測システム",
                "version": "2.0.0",
                "environment": "production",
                "debug": False,
                "architecture": "unified",
            },
            "jquants": {
                "base_url": "https://api.jquants.com/v1",
                "timeout": 30,
                "max_retries": 3,
                "retry_interval": 5,
            },
            "data_fetch": {"target_date": "20240301", "output_file": "stock_data.csv"},
            "preprocessing": {
                "input_file": "stock_data.csv",
                "output_file": "processed_stock_data.csv",
                "sma_windows": [5, 10, 25, 50],
                "lag_days": [1, 5, 25],
            },
            "prediction": {
                "input_file": "processed_stock_data.csv",
                "features": ["SMA_5", "SMA_25", "SMA_50", "Close_lag_1", "Close_lag_5"],
                "target": "Close",
                "test_size": 0.2,
                "random_state": 42,
                "model_selection": {
                    "primary_model": "random_forest",
                    "compare_models": False,
                },
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "jquants.log",
            },
        }
        self.logger.info("✅ デフォルト設定を適用しました")

    def _apply_environment_config(self) -> None:
        """環境別設定の適用"""
        current_env = self.get_system_config().get("environment", "production")

        if "environments" in self.config and current_env in self.config["environments"]:
            env_config = self.config["environments"][current_env]

            # 環境別設定をマージ
            for key, value in env_config.items():
                if key in self.config:
                    if isinstance(self.config[key], dict) and isinstance(value, dict):
                        self.config[key].update(value)
                    else:
                        self.config[key] = value
                else:
                    self.config[key] = value

            self.logger.info(f"✅ 環境別設定を適用: {current_env}")

    def get_system_config(self) -> Dict[str, Any]:
        """システム設定の取得"""
        return self.config.get("system", {})

    def get_jquants_config(self) -> Dict[str, Any]:
        """J-Quants API設定の取得"""
        return self.config.get("jquants", {})

    def get_data_fetch_config(self) -> Dict[str, Any]:
        """データ取得設定の取得"""
        return self.config.get("data_fetch", {})

    def get_preprocessing_config(self) -> Dict[str, Any]:
        """データ前処理設定の取得"""
        return self.config.get("preprocessing", {})

    def get_prediction_config(self) -> Dict[str, Any]:
        """予測モデル設定の取得"""
        return self.config.get("prediction", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定の取得"""
        return self.config.get("logging", {})

    def get_performance_config(self) -> Dict[str, Any]:
        """パフォーマンス設定の取得"""
        return self.config.get("performance", {})

    def get_security_config(self) -> Dict[str, Any]:
        """セキュリティ設定の取得"""
        return self.config.get("security", {})

    def get_error_handling_config(self) -> Dict[str, Any]:
        """エラーハンドリング設定の取得"""
        return self.config.get("error_handling", {})

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """設定値の取得（ドット記法対応）"""
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set_config_value(self, key_path: str, value: Any) -> None:
        """設定値の設定（ドット記法対応）"""
        keys = key_path.split(".")
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def save_config(self, output_file: str = None) -> None:
        """設定の保存"""
        if output_file is None:
            output_file = self.config_file

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"✅ 設定を保存しました: {output_file}")
        except Exception as e:
            self.logger.error(f"❌ 設定保存エラー: {e}")
            raise

    def validate_config(self) -> Dict[str, Any]:
        """設定の検証"""
        validation_result = {"is_valid": True, "errors": [], "warnings": []}

        # 必須設定のチェック
        required_sections = [
            "system",
            "jquants",
            "data_fetch",
            "preprocessing",
            "prediction",
        ]
        for section in required_sections:
            if section not in self.config:
                validation_result["errors"].append(f"必須セクションが不足: {section}")
                validation_result["is_valid"] = False

        # J-Quants設定のチェック
        jquants_config = self.get_jquants_config()
        if not jquants_config.get("base_url"):
            validation_result["warnings"].append(
                "J-Quants APIのbase_urlが設定されていません"
            )

        # 予測設定のチェック
        prediction_config = self.get_prediction_config()
        if not prediction_config.get("features"):
            validation_result["warnings"].append("予測用特徴量が設定されていません")

        if not prediction_config.get("target"):
            validation_result["errors"].append("目的変数(target)が設定されていません")
            validation_result["is_valid"] = False

        return validation_result

    def get_environment_info(self) -> Dict[str, Any]:
        """環境情報の取得"""
        system_config = self.get_system_config()
        return {
            "name": system_config.get("name", "Unknown"),
            "version": system_config.get("version", "Unknown"),
            "environment": system_config.get("environment", "Unknown"),
            "debug": system_config.get("debug", False),
            "architecture": system_config.get("architecture", "Unknown"),
            "config_file": self.config_file,
            "config_loaded": bool(self.config),
        }

    def reload_config(self) -> None:
        """設定の再読み込み"""
        self.logger.info("🔄 設定を再読み込み中...")
        self._load_config()
        self.logger.info("✅ 設定の再読み込み完了")


# グローバル設定インスタンス
_unified_config_instance = None


def get_unified_config(config_file: str = "config_unified.yaml") -> UnifiedConfigLoader:
    """統合設定ローダーの取得（シングルトンパターン）"""
    global _unified_config_instance

    if _unified_config_instance is None:
        _unified_config_instance = UnifiedConfigLoader(config_file)

    return _unified_config_instance


def reload_unified_config() -> None:
    """統合設定の再読み込み"""
    global _unified_config_instance

    if _unified_config_instance is not None:
        _unified_config_instance.reload_config()


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)

    config = get_unified_config()

    print("🔧 統合設定ローダーテスト")
    print(f"システム名: {config.get_system_config().get('name')}")
    print(f"環境: {config.get_system_config().get('environment')}")
    print(f"J-Quants URL: {config.get_jquants_config().get('base_url')}")

    # 設定検証
    validation = config.validate_config()
    print(f"設定検証: {'✅ 正常' if validation['is_valid'] else '❌ エラー'}")
    if validation["errors"]:
        print(f"エラー: {validation['errors']}")
    if validation["warnings"]:
        print(f"警告: {validation['warnings']}")
